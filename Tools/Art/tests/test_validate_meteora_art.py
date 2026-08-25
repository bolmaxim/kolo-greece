import struct
import unittest
import zlib

from Tools.Art.validate_meteora_art import PngValidationError, validate_png_bytes


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


if __name__ == "__main__":
    unittest.main()
