import struct
import hashlib
import json
import tempfile
import unittest
import zlib
from pathlib import Path

from Tools.Art.validate_meteora_art import (
    PngValidationError,
    validate_manifest,
    validate_png_bytes,
)


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _chunk(kind: bytes, payload: bytes) -> bytes:
    checksum = zlib.crc32(kind)
    checksum = zlib.crc32(payload, checksum) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", checksum)


def make_png(width: int, height: int, channels: int) -> bytes:
    color_type = 2 if channels == 3 else 6
    ihdr = struct.pack(">IIBBBBB", width, height, 8, color_type, 0, 0, 0)
    scanlines = b"".join(b"\x00" + bytes(width * channels) for _ in range(height))
    return (
        PNG_SIGNATURE
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(scanlines))
        + _chunk(b"IEND", b"")
    )


class ValidatePngBytesTests(unittest.TestCase):
    def test_rejects_png_with_valid_ihdr_but_truncated_idat(self):
        data = make_png(width=2, height=2, channels=3)
        corrupt = data[:-20]

        with self.assertRaisesRegex(PngValidationError, "IDAT|IEND|truncated"):
            validate_png_bytes(corrupt)

    def test_rejects_chunk_with_bad_crc(self):
        data = bytearray(make_png(width=2, height=2, channels=4))
        data[-1] ^= 1

        with self.assertRaisesRegex(PngValidationError, "CRC"):
            validate_png_bytes(bytes(data))

    def test_rejects_incomplete_decoded_scanlines(self):
        color_type = 2
        ihdr = struct.pack(">IIBBBBB", 2, 2, 8, color_type, 0, 0, 0)
        one_scanline = b"\x00" + bytes(2 * 3)
        data = (
            PNG_SIGNATURE
            + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(one_scanline))
            + _chunk(b"IEND", b"")
        )

        with self.assertRaisesRegex(PngValidationError, "decoded scanlines"):
            validate_png_bytes(data)

    def test_rejects_unknown_critical_chunk(self):
        width = height = 1
        ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
        scanline = b"\x00" + bytes(width * 3)
        data = (
            PNG_SIGNATURE
            + _chunk(b"IHDR", ihdr)
            + _chunk(b"ABCD", b"")
            + _chunk(b"IDAT", zlib.compress(scanline))
            + _chunk(b"IEND", b"")
        )

        with self.assertRaisesRegex(PngValidationError, "critical chunk"):
            validate_png_bytes(data)

    def test_rejects_nonconsecutive_idat_chunks(self):
        width = height = 1
        ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
        compressed = zlib.compress(b"\x00" + bytes(width * 3))
        split = len(compressed) // 2
        data = (
            PNG_SIGNATURE
            + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", compressed[:split])
            + _chunk(b"tEXt", b"note\x00value")
            + _chunk(b"IDAT", compressed[split:])
            + _chunk(b"IEND", b"")
        )

        with self.assertRaisesRegex(PngValidationError, "IDAT.*consecutive"):
            validate_png_bytes(data)

    def test_rejects_invalid_scanline_filter_byte(self):
        width = height = 1
        ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
        data = (
            PNG_SIGNATURE
            + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(b"\x05" + bytes(width * 3)))
            + _chunk(b"IEND", b"")
        )

        with self.assertRaisesRegex(PngValidationError, "filter byte"):
            validate_png_bytes(data)


class ValidateManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def make_pack(
        self,
        *,
        sha256: str | None = None,
        alpha: str = "opaque",
        png_channels: int = 3,
        width: int = 2,
        height: int = 2,
    ) -> Path:
        data = make_png(width=width, height=height, channels=png_channels)
        asset_path = Path("Assets/Art/Meteora/test.png")
        target = self.root / asset_path
        target.parent.mkdir(parents=True)
        target.write_bytes(data)
        manifest_path = Path("Assets/Art/Meteora/manifest.json")
        manifest = {
            "assets": [
                {
                    "path": asset_path.as_posix(),
                    "width": width,
                    "height": height,
                    "sha256": sha256 or hashlib.sha256(data).hexdigest(),
                    "alphaExpectation": alpha,
                }
            ]
        }
        (self.root / manifest_path).write_text(json.dumps(manifest), encoding="utf-8")
        return manifest_path

    def test_manifest_rejects_hash_mismatch(self):
        manifest = self.make_pack(sha256="0" * 64)

        self.assertIn("sha256 mismatch", validate_manifest(self.root, manifest)[0])

    def test_manifest_rejects_wrong_alpha_contract(self):
        manifest = self.make_pack(alpha="transparent", png_channels=3)

        self.assertIn("alpha mismatch", validate_manifest(self.root, manifest)[0])

    def test_manifest_accepts_complete_valid_png(self):
        manifest = self.make_pack(alpha="opaque", png_channels=3)

        self.assertEqual([], validate_manifest(self.root, manifest))


if __name__ == "__main__":
    unittest.main()
