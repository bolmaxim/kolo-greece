import struct
import contextlib
import hashlib
import io
import json
import tempfile
import unittest
import zlib
from pathlib import Path

from Tools.Art.validate_meteora_art import (
    PngValidationError,
    main,
    validate_manifest,
    validate_png_bytes,
)

try:
    from Tools.Art.meteora_contracts import required_paths_for
except ModuleNotFoundError:
    required_paths_for = None


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
REQUIRED_PATHS = [
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
]
LEVEL02_REQUIRED_PATHS = [
    "Assets/Art/Meteora/Backgrounds/Level02/sky-base.png",
    "Assets/Art/Meteora/Backgrounds/Level02/clouds-depth.png",
    "Assets/Art/Meteora/Backgrounds/Level02/meteora-far.png",
    "Assets/Art/Meteora/Backgrounds/Level02/meteora-mid-gorge.png",
    "Assets/Art/Meteora/Backgrounds/Level02/cliffs-near-station.png",
    "Assets/Art/Meteora/Environment/Level02/cargo-crane-atlas.png",
    "Assets/Art/Meteora/Environment/Level02/cliff-route-atlas.png",
]
OPAQUE_PATHS = {
    "Assets/Art/Meteora/Backgrounds/Level01/sky-base.png",
    "Assets/Art/Meteora/Environment/rock-surfaces-atlas.png",
}


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


def make_rgba_png(width: int, height: int, alpha: int) -> bytes:
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    pixel = bytes((10, 20, 30, alpha))
    scanlines = b"".join(b"\x00" + pixel * width for _ in range(height))
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

    def test_rejects_dimensions_above_resource_limit(self):
        ihdr = struct.pack(">IIBBBBB", 100_000, 1, 8, 2, 0, 0, 0)
        data = (
            PNG_SIGNATURE
            + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(b"\x00\x00\x00\x00"))
            + _chunk(b"IEND", b"")
        )

        with self.assertRaisesRegex(PngValidationError, "limit"):
            validate_png_bytes(data)

    def test_rejects_decompressed_data_above_expected_size(self):
        ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
        data = (
            PNG_SIGNATURE
            + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(b"\x00" + bytes(200_000)))
            + _chunk(b"IEND", b"")
        )

        with self.assertRaisesRegex(PngValidationError, "decoded scanlines|limit"):
            validate_png_bytes(data)

    def test_rejects_plte_after_idat(self):
        data = make_png(width=1, height=1, channels=3)
        insertion = data.rfind(_chunk(b"IEND", b""))
        malformed = data[:insertion] + _chunk(b"PLTE", b"\x00\x00\x00") + data[insertion:]

        with self.assertRaisesRegex(PngValidationError, "PLTE.*before.*IDAT"):
            validate_png_bytes(malformed)

    def test_rejects_duplicate_plte(self):
        data = make_png(width=1, height=1, channels=3)
        ihdr_end = len(PNG_SIGNATURE) + 12 + 13
        palette = _chunk(b"PLTE", b"\x00\x00\x00")
        malformed = data[:ihdr_end] + palette + palette + data[ihdr_end:]

        with self.assertRaisesRegex(PngValidationError, "at most one PLTE"):
            validate_png_bytes(malformed)

    def test_rejects_malformed_plte_length(self):
        data = make_png(width=1, height=1, channels=3)
        ihdr_end = len(PNG_SIGNATURE) + 12 + 13
        malformed = data[:ihdr_end] + _chunk(b"PLTE", b"\x00\x00") + data[ihdr_end:]

        with self.assertRaisesRegex(PngValidationError, "PLTE.*length"):
            validate_png_bytes(malformed)

    def test_rejects_non_letter_chunk_type_byte(self):
        data = make_png(width=1, height=1, channels=3)
        ihdr_end = len(PNG_SIGNATURE) + 12 + 13
        malformed = data[:ihdr_end] + _chunk(b"tE1t", b"") + data[ihdr_end:]

        with self.assertRaisesRegex(PngValidationError, "chunk type.*letters"):
            validate_png_bytes(malformed)

    def test_rejects_lowercase_reserved_chunk_type_byte(self):
        data = make_png(width=1, height=1, channels=3)
        ihdr_end = len(PNG_SIGNATURE) + 12 + 13
        malformed = data[:ihdr_end] + _chunk(b"tExt", b"") + data[ihdr_end:]

        with self.assertRaisesRegex(PngValidationError, "reserved.*uppercase"):
            validate_png_bytes(malformed)


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
        alpha: str | None = None,
        png_channels: int | None = None,
        width: int = 2,
        height: int = 2,
    ) -> Path:
        manifest_path = Path("Assets/Art/Meteora/meteora-level-01-art-manifest.json")
        assets = []
        for index, path_string in enumerate(REQUIRED_PATHS):
            expected_alpha = "opaque" if path_string in OPAQUE_PATHS else "transparent"
            channels = 3 if expected_alpha == "opaque" else 4
            if index == 0 and png_channels is not None:
                channels = png_channels
            data = make_png(width=width, height=height, channels=channels)
            target = self.root / path_string
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            assets.append(
                {
                    "path": path_string,
                    "width": width,
                    "height": height,
                    "sha256": (
                        sha256 if index == 0 and sha256 is not None
                        else hashlib.sha256(data).hexdigest()
                    ),
                    "alphaExpectation": (
                        alpha if index == 0 and alpha is not None else expected_alpha
                    ),
                }
            )
        manifest = {"assets": assets}
        (self.root / manifest_path).write_text(json.dumps(manifest), encoding="utf-8")
        return manifest_path

    def make_level02_pack(self) -> Path:
        manifest_path = Path("Assets/Art/Meteora/meteora-level-02-art-manifest.json")
        assets = []
        for index, path_string in enumerate(LEVEL02_REQUIRED_PATHS):
            channels = 3 if index == 0 else 4
            data = make_png(width=2, height=2, channels=channels)
            target = self.root / path_string
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            assets.append(
                {
                    "path": path_string,
                    "width": 2,
                    "height": 2,
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "alphaExpectation": "opaque" if index == 0 else "transparent",
                }
            )
        (self.root / manifest_path).write_text(
            json.dumps({"assets": assets}), encoding="utf-8"
        )
        return manifest_path

    def read_manifest(self, manifest_path: Path) -> dict:
        return json.loads((self.root / manifest_path).read_text(encoding="utf-8"))

    def write_manifest(self, manifest_path: Path, manifest: object) -> None:
        (self.root / manifest_path).write_text(json.dumps(manifest), encoding="utf-8")

    def test_level01_filename_selects_original_ordered_paths(self):
        self.assertIsNotNone(required_paths_for)
        if required_paths_for is None:
            return

        self.assertEqual(
            tuple(REQUIRED_PATHS),
            required_paths_for(Path("meteora-level-01-art-manifest.json")),
        )

    def test_level02_filename_selects_exact_ordered_paths(self):
        self.assertIsNotNone(required_paths_for)
        if required_paths_for is None:
            return

        self.assertEqual(
            tuple(LEVEL02_REQUIRED_PATHS),
            required_paths_for(Path("meteora-level-02-art-manifest.json")),
        )

    def test_unknown_manifest_contract_is_only_error(self):
        manifest_path = Path("Assets/Art/Meteora/unknown.json")
        (self.root / manifest_path).parent.mkdir(parents=True, exist_ok=True)
        self.write_manifest(manifest_path, {"assets": []})

        self.assertEqual(
            ["unknown manifest contract: unknown.json"],
            validate_manifest(self.root, manifest_path),
        )

    def test_level02_manifest_accepts_valid_seven_file_pack(self):
        manifest_path = self.make_level02_pack()

        self.assertEqual([], validate_manifest(self.root, manifest_path))

    def test_level02_manifest_rejects_valid_pack_when_paths_are_reordered(self):
        manifest_path = self.make_level02_pack()
        manifest = self.read_manifest(manifest_path)
        manifest["assets"][0], manifest["assets"][1] = manifest["assets"][1], manifest["assets"][0]
        self.write_manifest(manifest_path, manifest)

        self.assertEqual(
            ["asset paths must match contract v1 in exact order"],
            validate_manifest(self.root, manifest_path),
        )

    def test_manifest_rejects_hash_mismatch(self):
        manifest = self.make_pack(sha256="0" * 64)

        self.assertIn("sha256 mismatch", validate_manifest(self.root, manifest)[0])

    def test_manifest_rejects_wrong_alpha_contract(self):
        manifest = self.make_pack(alpha="transparent", png_channels=3)

        self.assertIn("alpha mismatch", validate_manifest(self.root, manifest)[0])

    def test_manifest_rejects_all_opaque_rgba_when_transparency_expected(self):
        manifest_path = self.make_pack()
        manifest = self.read_manifest(manifest_path)
        opaque_rgba = make_rgba_png(width=2, height=2, alpha=255)
        target = self.root / REQUIRED_PATHS[0]
        target.write_bytes(opaque_rgba)
        manifest["assets"][0]["sha256"] = hashlib.sha256(opaque_rgba).hexdigest()
        self.write_manifest(manifest_path, manifest)

        errors = validate_manifest(self.root, manifest_path)
        self.assertTrue(any("transparent pixels" in error for error in errors))

    def test_manifest_accepts_complete_valid_png(self):
        manifest = self.make_pack()

        self.assertEqual([], validate_manifest(self.root, manifest))

    def test_manifest_rejects_wrong_dimensions(self):
        manifest_path = self.make_pack()
        manifest = self.read_manifest(manifest_path)
        manifest["assets"][0]["width"] += 1
        self.write_manifest(manifest_path, manifest)

        self.assertTrue(any("dimensions mismatch" in error for error in validate_manifest(self.root, manifest_path)))

    def test_manifest_rejects_missing_asset_file(self):
        manifest_path = self.make_pack()
        (self.root / REQUIRED_PATHS[0]).unlink()

        self.assertTrue(any("cannot read asset" in error for error in validate_manifest(self.root, manifest_path)))

    def test_manifest_rejects_empty_inventory(self):
        manifest_path = self.make_pack()
        self.write_manifest(manifest_path, {"assets": []})

        self.assertTrue(any("inventory" in error for error in validate_manifest(self.root, manifest_path)))

    def test_manifest_rejects_duplicate_asset_path(self):
        manifest_path = self.make_pack()
        manifest = self.read_manifest(manifest_path)
        manifest["assets"][1]["path"] = manifest["assets"][0]["path"]
        self.write_manifest(manifest_path, manifest)

        self.assertTrue(any("duplicate" in error for error in validate_manifest(self.root, manifest_path)))

    def test_manifest_rejects_omitted_asset(self):
        manifest_path = self.make_pack()
        manifest = self.read_manifest(manifest_path)
        manifest["assets"].pop()
        self.write_manifest(manifest_path, manifest)

        self.assertTrue(any("missing required" in error for error in validate_manifest(self.root, manifest_path)))

    def test_manifest_rejects_extra_asset(self):
        manifest_path = self.make_pack()
        manifest = self.read_manifest(manifest_path)
        extra_path = "Assets/Art/Meteora/extra.png"
        data = make_png(2, 2, 4)
        (self.root / extra_path).write_bytes(data)
        manifest["assets"].append(
            {
                "path": extra_path,
                "width": 2,
                "height": 2,
                "sha256": hashlib.sha256(data).hexdigest(),
                "alphaExpectation": "transparent",
            }
        )
        self.write_manifest(manifest_path, manifest)

        self.assertTrue(any("unexpected asset" in error for error in validate_manifest(self.root, manifest_path)))

    def test_manifest_rejects_wrong_asset_order(self):
        manifest_path = self.make_pack()
        manifest = self.read_manifest(manifest_path)
        manifest["assets"][0], manifest["assets"][1] = manifest["assets"][1], manifest["assets"][0]
        self.write_manifest(manifest_path, manifest)

        self.assertTrue(any("exact order" in error for error in validate_manifest(self.root, manifest_path)))

    def test_manifest_rejects_symlinked_asset(self):
        manifest_path = self.make_pack()
        target = self.root / REQUIRED_PATHS[0]
        data = target.read_bytes()
        outside = self.root.parent / f"{self.root.name}-outside.png"
        outside.write_bytes(data)
        self.addCleanup(outside.unlink, missing_ok=True)
        target.unlink()
        target.symlink_to(outside)

        self.assertTrue(any("symlink" in error for error in validate_manifest(self.root, manifest_path)))

    def test_manifest_rejects_traversal_path(self):
        manifest_path = self.make_pack()
        manifest = self.read_manifest(manifest_path)
        manifest["assets"][0]["path"] = "../outside.png"
        self.write_manifest(manifest_path, manifest)

        self.assertTrue(any("inside repository root" in error for error in validate_manifest(self.root, manifest_path)))

    def test_manifest_rejects_non_object_top_level_json(self):
        manifest_path = self.make_pack()
        self.write_manifest(manifest_path, [])

        errors = validate_manifest(self.root, manifest_path)
        self.assertTrue(any("top-level" in error for error in errors))

    def test_cli_returns_zero_for_valid_pack(self):
        manifest_path = self.make_pack()
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            result = main(["--root", str(self.root), "--manifest", str(manifest_path)])

        self.assertEqual(0, result)
        self.assertIn("validation passed", output.getvalue())

    def test_cli_returns_zero_for_two_valid_manifests(self):
        level01_manifest = self.make_pack()
        level02_manifest = self.make_level02_pack()
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            result = main(
                [
                    "--root",
                    str(self.root),
                    "--manifest",
                    str(level01_manifest),
                    "--manifest",
                    str(level02_manifest),
                ]
            )

        self.assertEqual(0, result)
        self.assertIn("(2 manifests)", output.getvalue())

    def test_cli_identifies_invalid_level02_manifest(self):
        level01_manifest = self.make_pack()
        level02_manifest = self.make_level02_pack()
        manifest = self.read_manifest(level02_manifest)
        manifest["assets"][0]["sha256"] = "0" * 64
        self.write_manifest(level02_manifest, manifest)
        error_output = io.StringIO()

        with contextlib.redirect_stderr(error_output):
            result = main(
                [
                    "--root",
                    str(self.root),
                    "--manifest",
                    str(level01_manifest),
                    "--manifest",
                    str(level02_manifest),
                ]
            )

        self.assertEqual(1, result)
        self.assertIn(str(level02_manifest), error_output.getvalue())
        self.assertIn(LEVEL02_REQUIRED_PATHS[0], error_output.getvalue())

    def test_cli_reports_single_manifest_count(self):
        manifest_path = self.make_pack()
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            result = main(["--root", str(self.root), "--manifest", str(manifest_path)])

        self.assertEqual(0, result)
        self.assertIn("(1 manifests)", output.getvalue())

    def test_cli_requires_manifest_argument(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                main(["--root", str(self.root)])

    def test_cli_returns_one_and_lists_invalid_asset(self):
        manifest_path = self.make_pack(sha256="0" * 64)
        error_output = io.StringIO()

        with contextlib.redirect_stderr(error_output):
            result = main(["--root", str(self.root), "--manifest", str(manifest_path)])

        self.assertEqual(1, result)
        self.assertIn(REQUIRED_PATHS[0], error_output.getvalue())


class WorkflowTests(unittest.TestCase):
    def test_workflow_validates_both_packs_once_and_keeps_ci_scope(self):
        repo_root = Path(__file__).resolve().parents[3]
        workflow = (repo_root / ".github/workflows/validate-meteora-art.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn("      - art/meteora-level-02-assets", workflow)
        self.assertIn("      - main", workflow)
        self.assertIn("  pull_request:", workflow)
        self.assertIn("  workflow_dispatch:", workflow)
        self.assertRegex(workflow, r"timeout-minutes:\s*\d+")
        self.assertEqual(
            1,
            workflow.count("python3 -m unittest discover -s Tools/Art/tests -v"),
        )
        self.assertIn(
            "python3 Tools/Art/validate_meteora_art.py\n"
            "          --root .\n"
            "          --manifest Assets/Art/Meteora/meteora-level-01-art-manifest.json\n"
            "          --manifest Assets/Art/Meteora/meteora-level-02-art-manifest.json",
            workflow,
        )


class ValidateRepositoryPacksTests(unittest.TestCase):
    def test_level02_repository_pack_is_valid(self):
        repo_root = Path(__file__).resolve().parents[3]

        self.assertEqual(
            [],
            validate_manifest(
                repo_root,
                Path("Assets/Art/Meteora/meteora-level-02-art-manifest.json"),
            ),
        )


if __name__ == "__main__":
    unittest.main()
