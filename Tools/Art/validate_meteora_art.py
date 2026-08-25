#!/usr/bin/env python3
"""Validate complete Meteora PNG streams and their manifest metadata."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
import zlib
from dataclasses import dataclass
from pathlib import Path


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
SUPPORTED_COLOR_TYPES = {2: 3, 6: 4}


class PngValidationError(ValueError):
    """Raised when bytes do not form a complete supported PNG."""


@dataclass(frozen=True)
class PngInfo:
    width: int
    height: int
    color_type: int

    @property
    def has_alpha(self) -> bool:
        return self.color_type == 6


@dataclass(frozen=True)
class _Chunk:
    kind: bytes
    data: bytes


def _parse_chunks(data: bytes) -> list[_Chunk]:
    if not data.startswith(PNG_SIGNATURE):
        raise PngValidationError("invalid PNG signature")

    chunks: list[_Chunk] = []
    offset = len(PNG_SIGNATURE)
    while offset < len(data):
        if len(data) - offset < 12:
            raise PngValidationError("truncated PNG chunk")
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        chunk_end = offset + 12 + length
        if chunk_end > len(data):
            raise PngValidationError("truncated PNG chunk data")
        kind = data[offset + 4 : offset + 8]
        payload = data[offset + 8 : offset + 8 + length]
        declared_crc = struct.unpack(">I", data[offset + 8 + length : chunk_end])[0]
        actual_crc = zlib.crc32(kind)
        actual_crc = zlib.crc32(payload, actual_crc) & 0xFFFFFFFF
        if actual_crc != declared_crc:
            label = kind.decode("ascii", errors="replace")
            raise PngValidationError(f"CRC mismatch in {label} chunk")
        chunks.append(_Chunk(kind, payload))
        offset = chunk_end
        if kind == b"IEND":
            if offset != len(data):
                raise PngValidationError("data found after IEND chunk")
            break

    return chunks


def _read_ihdr(chunks: list[_Chunk]) -> tuple[int, int, int]:
    if not chunks or chunks[0].kind != b"IHDR":
        raise PngValidationError("IHDR must be the first PNG chunk")
    if sum(chunk.kind == b"IHDR" for chunk in chunks) != 1:
        raise PngValidationError("PNG must contain exactly one IHDR chunk")
    payload = chunks[0].data
    if len(payload) != 13:
        raise PngValidationError("IHDR must contain 13 bytes")
    width, height, bit_depth, color_type, compression, filtering, interlace = struct.unpack(
        ">IIBBBBB", payload
    )
    if width == 0 or height == 0:
        raise PngValidationError("PNG dimensions must be positive")
    if bit_depth != 8 or color_type not in SUPPORTED_COLOR_TYPES:
        raise PngValidationError("only 8-bit RGB/RGBA PNGs are supported")
    if compression != 0 or filtering != 0 or interlace != 0:
        raise PngValidationError("only standard, non-interlaced PNGs are supported")
    return width, height, color_type


def _inflate_idat(chunks: list[_Chunk]) -> bytes:
    idat_parts = [chunk.data for chunk in chunks if chunk.kind == b"IDAT"]
    if not idat_parts:
        raise PngValidationError("PNG has no IDAT chunk")
    compressed = b"".join(idat_parts)
    inflater = zlib.decompressobj()
    try:
        decoded = inflater.decompress(compressed)
        decoded += inflater.flush()
    except zlib.error as error:
        raise PngValidationError(f"IDAT zlib decode failed: {error}") from error
    if not inflater.eof or inflater.unconsumed_tail or inflater.unused_data:
        raise PngValidationError("IDAT stream is truncated or contains trailing data")
    return decoded


def validate_png_bytes(data: bytes) -> PngInfo:
    chunks = _parse_chunks(data)
    width, height, color_type = _read_ihdr(chunks)
    iend_chunks = [chunk for chunk in chunks if chunk.kind == b"IEND"]
    if len(iend_chunks) != 1 or iend_chunks[0].data:
        raise PngValidationError("PNG must end with one empty IEND chunk")
    decoded = _inflate_idat(chunks)
    expected_size = height * (1 + width * SUPPORTED_COLOR_TYPES[color_type])
    if len(decoded) != expected_size:
        raise PngValidationError(
            f"decoded scanlines: {len(decoded)} != {expected_size} bytes"
        )
    return PngInfo(width=width, height=height, color_type=color_type)


def validate_manifest(repo_root: Path, manifest_path: Path) -> list[str]:
    root = repo_root.resolve()
    manifest_file = manifest_path if manifest_path.is_absolute() else root / manifest_path
    try:
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        return [f"{manifest_path}: cannot read manifest: {error}"]

    errors: list[str] = []
    assets = manifest.get("assets")
    if not isinstance(assets, list):
        return [f"{manifest_path}: manifest assets must be a list"]

    for index, entry in enumerate(assets):
        if not isinstance(entry, dict):
            errors.append(f"asset[{index}]: manifest entry must be an object")
            continue
        label = str(entry.get("path", f"asset[{index}]"))
        asset_path = Path(label)
        if asset_path.is_absolute() or ".." in asset_path.parts:
            errors.append(f"{label}: asset path must stay inside repository root")
            continue
        try:
            data = (root / asset_path).read_bytes()
        except OSError as error:
            errors.append(f"{label}: cannot read asset: {error}")
            continue
        try:
            info = validate_png_bytes(data)
        except PngValidationError as error:
            errors.append(f"{label}: {error}")
            continue

        actual_hash = hashlib.sha256(data).hexdigest()
        if actual_hash != entry.get("sha256"):
            errors.append(
                f"{label}: sha256 mismatch: {actual_hash} != {entry.get('sha256')}"
            )
        if (info.width, info.height) != (entry.get("width"), entry.get("height")):
            errors.append(
                f"{label}: dimensions mismatch: {info.width}x{info.height} != "
                f"{entry.get('width')}x{entry.get('height')}"
            )
        expected_alpha = entry.get("alphaExpectation")
        actual_alpha = "transparent" if info.has_alpha else "opaque"
        if actual_alpha != expected_alpha:
            errors.append(
                f"{label}: alpha mismatch: {actual_alpha} != {expected_alpha}"
            )

    return errors


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="repository root")
    parser.add_argument("--manifest", type=Path, required=True, help="manifest path")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    errors = validate_manifest(args.root, args.manifest)
    if errors:
        print(f"Meteora art validation failed ({len(errors)} error(s)):", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Meteora art validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
