#!/usr/bin/env python3
"""Validate complete Meteora PNG streams and their manifest metadata."""

from __future__ import annotations

import argparse
import hashlib
import json
import stat
import struct
import sys
import zlib
from dataclasses import dataclass
from pathlib import Path


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
SUPPORTED_COLOR_TYPES = {2: 3, 6: 4}
KNOWN_CRITICAL_CHUNKS = {b"IHDR", b"PLTE", b"IDAT", b"IEND"}
MANIFEST_CONTRACT_VERSION = 1
REQUIRED_ASSET_PATHS = (
    "Assets/Art/Meteora/Characters/Kolo/kolo-normal-sheet.png",
    "Assets/Art/Meteora/Characters/Kolo/kolo-heavy-sheet.png",
    "Assets/Art/Meteora/Backgrounds/Level01/sky-base.png",
    "Assets/Art/Meteora/Backgrounds/Level01/clouds-far.png",
    "Assets/Art/Meteora/Backgrounds/Level01/meteora-far.png",
    "Assets/Art/Meteora/Backgrounds/Level01/meteora-mid.png",
    "Assets/Art/Meteora/Backgrounds/Level01/cliffs-near.png",
    "Assets/Art/Meteora/Environment/rock-surfaces-atlas.png",
    "Assets/Art/Meteora/Environment/wood-rope-bronze-atlas.png",
    "Assets/Art/Meteora/Environment/interactables-atlas.png",
    "Assets/Art/Meteora/Environment/water-honey-effects.png",
    "Assets/Art/UI/Controls/touch-controls-atlas.png",
)
MAX_DIMENSION = 8192
MAX_PIXELS = 32_000_000
MAX_PNG_BYTES = 64 * 1024 * 1024
MAX_DECODED_BYTES = 256 * 1024 * 1024


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
        if kind[0] & 0x20 == 0 and kind not in KNOWN_CRITICAL_CHUNKS:
            label = kind.decode("ascii", errors="replace")
            raise PngValidationError(f"unknown critical chunk: {label}")
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
    if width > MAX_DIMENSION or height > MAX_DIMENSION or width * height > MAX_PIXELS:
        raise PngValidationError("PNG dimensions exceed resource limit")
    if bit_depth != 8 or color_type not in SUPPORTED_COLOR_TYPES:
        raise PngValidationError("only 8-bit RGB/RGBA PNGs are supported")
    if compression != 0 or filtering != 0 or interlace != 0:
        raise PngValidationError("only standard, non-interlaced PNGs are supported")
    return width, height, color_type


def _inflate_idat(chunks: list[_Chunk], expected_size: int) -> bytes:
    idat_indexes = [index for index, chunk in enumerate(chunks) if chunk.kind == b"IDAT"]
    idat_parts = [chunks[index].data for index in idat_indexes]
    if not idat_parts:
        raise PngValidationError("PNG has no IDAT chunk")
    if idat_indexes != list(range(idat_indexes[0], idat_indexes[-1] + 1)):
        raise PngValidationError("IDAT chunks must be consecutive")
    compressed = b"".join(idat_parts)
    inflater = zlib.decompressobj()
    try:
        decoded = inflater.decompress(compressed, expected_size + 1)
    except zlib.error as error:
        raise PngValidationError(f"IDAT zlib decode failed: {error}") from error
    if len(decoded) > expected_size:
        raise PngValidationError("decoded scanlines exceed resource limit")
    if not inflater.eof or inflater.unconsumed_tail or inflater.unused_data:
        raise PngValidationError("IDAT stream is truncated or contains trailing data")
    return decoded


def validate_png_bytes(data: bytes) -> PngInfo:
    if len(data) > MAX_PNG_BYTES:
        raise PngValidationError("PNG file size exceeds resource limit")
    chunks = _parse_chunks(data)
    width, height, color_type = _read_ihdr(chunks)
    iend_chunks = [chunk for chunk in chunks if chunk.kind == b"IEND"]
    if len(iend_chunks) != 1 or iend_chunks[0].data:
        raise PngValidationError("PNG must end with one empty IEND chunk")
    expected_size = height * (1 + width * SUPPORTED_COLOR_TYPES[color_type])
    if expected_size > MAX_DECODED_BYTES:
        raise PngValidationError("decoded image size exceeds resource limit")
    decoded = _inflate_idat(chunks, expected_size)
    if len(decoded) != expected_size:
        raise PngValidationError(
            f"decoded scanlines: {len(decoded)} != {expected_size} bytes"
        )
    scanline_size = 1 + width * SUPPORTED_COLOR_TYPES[color_type]
    for row in range(height):
        filter_byte = decoded[row * scanline_size]
        if filter_byte > 4:
            raise PngValidationError(
                f"invalid filter byte {filter_byte} on scanline {row}"
            )
    return PngInfo(width=width, height=height, color_type=color_type)


def validate_manifest(repo_root: Path, manifest_path: Path) -> list[str]:
    try:
        root = repo_root.resolve(strict=True)
    except OSError as error:
        return [f"{repo_root}: cannot resolve repository root: {error}"]
    manifest_file = manifest_path if manifest_path.is_absolute() else root / manifest_path
    try:
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        return [f"{manifest_path}: cannot read manifest: {error}"]

    if not isinstance(manifest, dict):
        return [f"{manifest_path}: manifest top-level value must be an object"]

    errors: list[str] = []
    assets = manifest.get("assets")
    if not isinstance(assets, list):
        return [f"{manifest_path}: manifest assets must be a list"]

    paths = [entry.get("path") if isinstance(entry, dict) else None for entry in assets]
    if not assets:
        errors.append("asset inventory must not be empty")
    duplicate_paths = sorted(
        {path for path in paths if isinstance(path, str) and paths.count(path) > 1}
    )
    if duplicate_paths:
        errors.append(f"duplicate asset path(s): {', '.join(duplicate_paths)}")
    missing_paths = [path for path in REQUIRED_ASSET_PATHS if path not in paths]
    if missing_paths:
        errors.append(f"missing required asset(s): {', '.join(missing_paths)}")
    extra_paths = [
        path for path in paths
        if isinstance(path, str) and path not in REQUIRED_ASSET_PATHS
    ]
    if extra_paths:
        errors.append(f"unexpected asset path(s): {', '.join(extra_paths)}")
    if paths != list(REQUIRED_ASSET_PATHS):
        errors.append(
            f"asset paths must match contract v{MANIFEST_CONTRACT_VERSION} in exact order"
        )

    for index, entry in enumerate(assets):
        if not isinstance(entry, dict):
            errors.append(f"asset[{index}]: manifest entry must be an object")
            continue
        label = str(entry.get("path", f"asset[{index}]"))
        asset_path = Path(label)
        if asset_path.is_absolute() or ".." in asset_path.parts:
            errors.append(f"{label}: asset path must stay inside repository root")
            continue
        candidate = root / asset_path
        current = root
        symlink_found = False
        for part in asset_path.parts:
            current /= part
            if current.is_symlink():
                symlink_found = True
                break
        if symlink_found:
            errors.append(f"{label}: symlinked assets are not allowed")
            continue
        try:
            resolved_asset = candidate.resolve(strict=True)
            resolved_asset.relative_to(root)
        except OSError as error:
            errors.append(f"{label}: cannot read asset: {error}")
            continue
        except ValueError:
            errors.append(f"{label}: asset path must stay inside repository root")
            continue
        try:
            asset_stat = resolved_asset.stat()
            if not stat.S_ISREG(asset_stat.st_mode):
                errors.append(f"{label}: asset must be a regular file")
                continue
            if asset_stat.st_size > MAX_PNG_BYTES:
                errors.append(f"{label}: PNG file size exceeds resource limit")
                continue
            with resolved_asset.open("rb") as asset_file:
                data = asset_file.read(MAX_PNG_BYTES + 1)
        except OSError as error:
            errors.append(f"{label}: cannot read asset: {error}")
            continue
        if len(data) > MAX_PNG_BYTES:
            errors.append(f"{label}: PNG file size exceeds resource limit")
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
