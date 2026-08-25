# Meteora Art PNG Repair Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace every structurally corrupted Meteora Level 01 PNG and prevent incomplete/corrupt image streams from being accepted again.

**Architecture:** Add a dependency-free Python validator that parses PNG chunks, verifies CRCs, inflates the complete IDAT stream, checks the exact decoded scanline length, and cross-checks the art manifest. Run it in a permanent GitHub Actions workflow. Use the approved visual brief to regenerate only invalid assets, then update manifest hashes atomically.

**Tech Stack:** Python 3 standard library, `unittest`, GitHub Actions, built-in image generation, Git data API.

**Spec:** `docs/superpowers/specs/2026-08-24-meteora-level-01-art-assets-design.md`

## Global Constraints

- Work only on `art/meteora-level-01-assets`; do not update `main`.
- Preserve the exact 12 runtime asset paths and manifest entry order.
- Preserve alpha contracts: sky and rock atlas opaque RGB; all other assets RGBA.
- Preserve approved visual direction: realistic, polished 2.5D Meteora environment with readable mobile silhouettes.
- Do not claim Unity import or iPhone performance validation until those checks actually run.

---

### Task 1: Full PNG integrity gate

**Files:**
- Create: `Tools/Art/validate_meteora_art.py`
- Create: `Tools/Art/tests/test_validate_meteora_art.py`
- Create: `.github/workflows/validate-meteora-art.yml`

**Interfaces:**
- Produces: `validate_png_bytes(data: bytes) -> PngInfo`; `validate_manifest(repo_root: Path, manifest_path: Path) -> list[str]`; process exit code `0` only when every manifest asset fully decodes and matches its declared SHA-256/dimensions/alpha.

- [x] **Step 1: Write the failing corruption regression test**

```python
def test_rejects_png_with_valid_ihdr_but_truncated_idat():
    data = make_png(width=2, height=2, channels=3)
    corrupt = data[:-20]
    with self.assertRaisesRegex(PngValidationError, "IDAT|IEND|truncated"):
        validate_png_bytes(corrupt)
```

- [x] **Step 2: Run the test before implementation**

Run: `python3 -m unittest discover -s Tools/Art/tests -v`

Expected: FAIL because `Tools.Art.validate_meteora_art` does not exist.

- [x] **Step 3: Implement the minimal validator**

```python
def validate_png_bytes(data: bytes) -> PngInfo:
    require_png_signature(data)
    chunks = parse_chunks_with_crc(data)
    ihdr = require_supported_ihdr(chunks)  # 8-bit, non-interlaced RGB/RGBA
    compressed = b"".join(c.data for c in chunks if c.kind == b"IDAT")
    decoded = zlib.decompress(compressed)
    channels = 3 if ihdr.color_type == 2 else 4
    expected = ihdr.height * (1 + ihdr.width * channels)
    if len(decoded) != expected:
        raise PngValidationError(f"decoded scanlines: {len(decoded)} != {expected}")
    require_iend(chunks)
    return PngInfo(ihdr.width, ihdr.height, ihdr.color_type)
```

- [x] **Step 4: Add manifest behavior tests**

```python
def test_manifest_rejects_hash_mismatch(self):
    root, manifest = self.make_pack(sha256="0" * 64)
    self.assertIn("sha256 mismatch", validate_manifest(root, manifest)[0])

def test_manifest_rejects_wrong_alpha_contract(self):
    root, manifest = self.make_pack(alpha="transparent", png_channels=3)
    self.assertIn("alpha mismatch", validate_manifest(root, manifest)[0])

def test_manifest_accepts_complete_valid_png(self):
    root, manifest = self.make_pack(alpha="opaque", png_channels=3)
    self.assertEqual([], validate_manifest(root, manifest))
```

- [x] **Step 5: Verify GREEN locally and in GitHub Actions**

Run: `python3 -m unittest discover -s Tools/Art/tests -v`

Run: `python3 Tools/Art/validate_meteora_art.py --root . --manifest Assets/Art/Meteora/meteora-level-01-art-manifest.json`

Expected before asset repair: unit tests PASS; repository validation FAIL and names every corrupt PNG.

- [x] **Step 6: Commit the validator and workflow**

```bash
git add Tools/Art .github/workflows/validate-meteora-art.yml
git commit -m "test: validate complete Meteora PNG streams"
```

### Task 2: Replace invalid runtime assets

**Files:**
- Modify: only PNG paths reported invalid by Task 1.

**Interfaces:**
- Consumes: exact invalid-path report from `validate_meteora_art.py`.
- Produces: fully decodable 8-bit RGB/RGBA PNGs at the existing paths.

- [x] **Step 1: Record the failing validator output**

Run the permanent workflow at the exact Task 1 commit and save the job/run IDs in the execution report.

- [x] **Step 2: Regenerate each invalid image independently**

Use one built-in image-generation call per asset. Match the approved Meteora art brief, keep backgrounds compatible with the 2.5D side-view route, use no text/logos/watermarks, and preserve the required opaque/transparent contract.

- [x] **Step 3: Normalize generated output without visual redesign**

Use a lossless PNG re-encode only when required to set exact RGB/RGBA mode and remove unsafe ancillary chunks. Do not crop away required content or synthesize missing pixels.

- [x] **Step 4: Upload replacements without renaming paths**

Create new Git blobs, create one tree based on the current feature tree, create a single non-forced child commit, then fast-forward only `art/meteora-level-01-assets`.

- [x] **Step 5: Run the integrity gate**

Run: `python3 Tools/Art/validate_meteora_art.py --root . --manifest Assets/Art/Meteora/meteora-level-01-art-manifest.json`

Expected: FAIL only because the manifest still contains old SHA-256 values.

- [x] **Step 6: Commit the repaired PNGs**

```bash
git add Assets/Art
git commit -m "fix: replace corrupted Meteora art PNGs"
```

### Task 3: Manifest, documentation, and final verification

**Files:**
- Modify: `Assets/Art/Meteora/meteora-level-01-art-manifest.json`
- Modify: `Assets/Art/Meteora/README.md`
- Modify: `docs/superpowers/plans/2026-08-25-meteora-art-png-repair.md`
- Create: `docs/concept-art/asset-previews/meteora-level-01-repaired-atlases.png`
- Create: `docs/concept-art/asset-previews/meteora-level-01-parallax-safe-crops.png`

**Interfaces:**
- Consumes: SHA-256, decoded dimensions, and color type reported by the validator.
- Produces: a self-consistent art pack whose permanent CI gate passes.

- [x] **Step 1: Update only changed manifest hashes and confirmed metadata**

Keep the schema, exact path order, usage values, and alpha values unchanged.

- [x] **Step 2: Document the integrity gate**

Add the exact local validation command and explain that a valid header alone is insufficient; the complete IDAT stream must decode and end with a valid IEND chunk.

- [x] **Step 3: Run unit, repository, and CI verification**

```bash
python3 -m unittest discover -s Tools/Art/tests -v
python3 Tools/Art/validate_meteora_art.py --root . --manifest Assets/Art/Meteora/meteora-level-01-art-manifest.json
```

Expected: all unit tests PASS; 12/12 runtime PNGs PASS; GitHub Actions workflow PASS.

- [x] **Step 4: Visually inspect every repaired image**

Confirm there are no black/truncated regions, corrupt scanlines, accidental text, watermarks, or mismatched alpha backgrounds. Create a contact sheet for review without adding it under runtime `Assets/`.

- [x] **Step 5: Commit final metadata and plan state**

```bash
git add Assets/Art/Meteora/meteora-level-01-art-manifest.json Assets/Art/Meteora/README.md docs/superpowers/plans/2026-08-25-meteora-art-png-repair.md
git commit -m "docs: finalize repaired Meteora art pack"
```

## Execution note — 2026-08-25

Task 2 exact-head CI run `32844503500`, job `97791071817`, confirmed 24/24 unit tests and only the eight expected pre-manifest SHA-256 mismatches. Task 3 updates those hashes, documents deterministic slicing and reviewed crop envelopes, and saves the two non-runtime QA previews above. Unity Editor import, manual SpriteRects/`.meta` creation, and device checks remain deferred.
