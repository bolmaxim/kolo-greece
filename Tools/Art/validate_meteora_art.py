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

try:
    from Tools.Art.meteora_contracts import (
        LEVEL01_REQUIRED_ASSET_PATHS,
        required_paths_for,
    )
except ModuleNotFoundError:
    from meteora_contracts import LEVEL01_REQUIRED_ASSET_PATHS, required_paths_for


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
SUPPORTED_COLOR_TYPES = {2: 3, 6: 4}
KNOWN_CRITICAL_CHUNKS = {b"IHDR", b"PLTE", b"IDAT", b"IEND"}
MANIFEST_CONTRACT_VERSION = 1
REQUIRED_ASSET_PATHS = LEVEL01_REQUIRED_ASSET_PATHS
MAX_DIMENSION = 8192
MAX_PIXELS = 32_000_000
MAX_PNG_BYTES = 64 * 1024 * 1024
MAX_DECODED_BYTES = 256 * 1024 * 1024
# Generated PNGs normally use only a handful of chunks; this leaves ample
# headroom while bounding per-chunk object amplification.
MAX_PNG_CHUNKS = 4_096
COLOR_TYPE_REQUIRED_MANIFESTS = {
    "meteora-level-02-art-manifest.json",
    "meteora-level-03-art-manifest.json",
}


class PngValidationError(ValueError):
    """Raised when bytes do not form a complete supported PNG."""


@dataclass(frozen=True)
class PngInfo:
    width: int
    height: int
    color_type: int
    has_transparency_key: bool
    has_transparent_pixels: bool

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
        if len(chunks) >= MAX_PNG_CHUNKS:
            raise PngValidationError(
                f"PNG chunk count exceeds resource limit ({MAX_PNG_CHUNKS})"
            )
        if len(data) - offset < 12:
            raise PngValidationError("truncated PNG chunk")
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        chunk_end = offset + 12 + length
        if chunk_end > len(data):
            raise PngValidationError("truncated PNG chunk data")
        kind = data[offset + 4 : offset + 8]
        if not all(65 <= byte <= 90 or 97 <= byte <= 122 for byte in kind):
            raise PngValidationError("PNG chunk type must contain only ASCII letters")
        if kind[2] & 0x20:
            raise PngValidationError(
                "PNG chunk type reserved byte must be uppercase"
            )
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


def _validate_plte(chunks: list[_Chunk]) -> None:
    plte_indexes = [index for index, chunk in enumerate(chunks) if chunk.kind == b"PLTE"]
    if len(plte_indexes) > 1:
        raise PngValidationError("PNG may contain at most one PLTE chunk")
    if not plte_indexes:
        return
    idat_indexes = [index for index, chunk in enumerate(chunks) if chunk.kind == b"IDAT"]
    if idat_indexes and plte_indexes[0] > idat_indexes[0]:
        raise PngValidationError("PLTE must appear before the first IDAT chunk")
    length = len(chunks[plte_indexes[0]].data)
    if length < 3 or length > 768 or length % 3:
        raise PngValidationError(
            "PLTE length must be a positive multiple of 3 and at most 768 bytes"
        )


def _read_trns(chunks: list[_Chunk], color_type: int) -> tuple[int, int, int] | None:
    trns_indexes = [index for index, chunk in enumerate(chunks) if chunk.kind == b"tRNS"]
    if len(trns_indexes) > 1:
        raise PngValidationError("PNG may contain at most one tRNS chunk")
    if not trns_indexes:
        return None

    trns_index = trns_indexes[0]
    idat_indexes = [index for index, chunk in enumerate(chunks) if chunk.kind == b"IDAT"]
    if idat_indexes and trns_index > idat_indexes[0]:
        raise PngValidationError("tRNS must appear before the first IDAT chunk")
    plte_indexes = [index for index, chunk in enumerate(chunks) if chunk.kind == b"PLTE"]
    if plte_indexes and trns_index < plte_indexes[0]:
        raise PngValidationError("tRNS must appear after PLTE")
    if color_type == 6:
        raise PngValidationError("tRNS is not allowed for color type 6")

    payload = chunks[trns_index].data
    if len(payload) != 6:
        raise PngValidationError("tRNS for RGB must contain exactly 6 bytes")
    transparent_rgb = struct.unpack(">HHH", payload)
    if any(sample > 255 for sample in transparent_rgb):
        raise PngValidationError("tRNS sample exceeds 8-bit color depth")
    return transparent_rgb


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


def _paeth_predictor(left: int, up: int, upper_left: int) -> int:
    estimate = left + up - upper_left
    left_distance = abs(estimate - left)
    up_distance = abs(estimate - up)
    upper_left_distance = abs(estimate - upper_left)
    if left_distance <= up_distance and left_distance <= upper_left_distance:
        return left
    if up_distance <= upper_left_distance:
        return up
    return upper_left


def _validate_and_unfilter_scanlines(
    decoded: bytes,
    width: int,
    height: int,
    channels: int,
    transparent_rgb: tuple[int, int, int] | None,
) -> bool:
    row_size = width * channels
    scanline_size = 1 + row_size
    previous = bytearray(row_size)
    has_transparent_pixels = False
    for row_index in range(height):
        start = row_index * scanline_size
        filter_byte = decoded[start]
        if filter_byte > 4:
            raise PngValidationError(
                f"invalid filter byte {filter_byte} on scanline {row_index}"
            )
        raw = decoded[start + 1 : start + scanline_size]
        current = bytearray(row_size)
        for index, value in enumerate(raw):
            left = current[index - channels] if index >= channels else 0
            up = previous[index]
            upper_left = previous[index - channels] if index >= channels else 0
            if filter_byte == 0:
                predictor = 0
            elif filter_byte == 1:
                predictor = left
            elif filter_byte == 2:
                predictor = up
            elif filter_byte == 3:
                predictor = (left + up) // 2
            else:
                predictor = _paeth_predictor(left, up, upper_left)
            current[index] = (value + predictor) & 0xFF
        if channels == 4 and any(alpha < 255 for alpha in current[3::4]):
            has_transparent_pixels = True
        elif transparent_rgb is not None and any(
            tuple(current[index : index + 3]) == transparent_rgb
            for index in range(0, len(current), 3)
        ):
            has_transparent_pixels = True
        previous = current
    return has_transparent_pixels


def validate_png_bytes(data: bytes) -> PngInfo:
    if len(data) > MAX_PNG_BYTES:
        raise PngValidationError("PNG file size exceeds resource limit")
    chunks = _parse_chunks(data)
    width, height, color_type = _read_ihdr(chunks)
    _validate_plte(chunks)
    transparent_rgb = _read_trns(chunks, color_type)
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
    has_transparent_pixels = _validate_and_unfilter_scanlines(
        decoded,
        width,
        height,
        SUPPORTED_COLOR_TYPES[color_type],
        transparent_rgb,
    )
    return PngInfo(
        width=width,
        height=height,
        color_type=color_type,
        has_transparency_key=transparent_rgb is not None,
        has_transparent_pixels=has_transparent_pixels,
    )


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

    try:
        required_asset_paths = required_paths_for(manifest_path)
    except ValueError as error:
        return [str(error)]

    if not isinstance(manifest, dict):
        return [f"{manifest_path}: manifest top-level value must be an object"]

    errors: list[str] = []
    requires_color_type = manifest_path.name in COLOR_TYPE_REQUIRED_MANIFESTS
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
    missing_paths = [path for path in required_asset_paths if path not in paths]
    if missing_paths:
        errors.append(f"missing required asset(s): {', '.join(missing_paths)}")
    extra_paths = [
        path for path in paths
        if isinstance(path, str) and path not in required_asset_paths
    ]
    if extra_paths:
        errors.append(f"unexpected asset path(s): {', '.join(extra_paths)}")
    if paths != list(required_asset_paths):
        errors.append(
            f"asset paths must match contract v{MANIFEST_CONTRACT_VERSION} in exact order"
        )

    for index, entry in enumerate(assets):
        if not isinstance(entry, dict):
            errors.append(f"asset[{index}]: manifest entry must be an object")
            continue
        label = str(entry.get("path", f"asset[{index}]"))
        declared_color_type = entry.get("colorType")
        valid_declared_color_type = True
        if requires_color_type:
            if "colorType" not in entry:
                errors.append(f"{label}: colorType is required")
                valid_declared_color_type = False
            elif type(declared_color_type) is not int:
                errors.append(f"{label}: colorType must be an integer")
                valid_declared_color_type = False
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
        if (
            requires_color_type
            and valid_declared_color_type
            and info.color_type != declared_color_type
        ):
            errors.append(
                f"{label}: colorType mismatch: {info.color_type} != {declared_color_type}"
            )
        expected_alpha = entry.get("alphaExpectation")
        actual_alpha = "transparent" if info.has_transparent_pixels else "opaque"
        if actual_alpha != expected_alpha:
            detail = (
                " (image contains no transparent pixels)"
                if expected_alpha == "transparent"
                else ""
            )
            errors.append(
                f"{label}: alpha mismatch: {actual_alpha} != {expected_alpha}{detail}"
            )

    return errors


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="repository root")
    parser.add_argument(
        "--manifest",
        action="append",
        type=Path,
        required=True,
        help="manifest path",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    errors = [
        (manifest_path, error)
        for manifest_path in args.manifest
        for error in validate_manifest(args.root, manifest_path)
    ]
    if errors:
        print(f"Meteora art validation failed ({len(errors)} error(s)):", file=sys.stderr)
        for manifest_path, error in errors:
            print(f"- {manifest_path}: {error}", file=sys.stderr)
        return 1
    print(f"Meteora art validation passed ({len(args.manifest)} manifests)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
