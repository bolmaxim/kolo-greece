# Meteora Level 02 Art Assets Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce and validate the complete starter art pack for Meteora Level 02, “Basket Above the Clouds,” while preserving Level 01 and its integrity guarantees.

**Architecture:** Level 02 reuses the shared Kolo, UI, and material atlases from Level 01 and adds five independent parallax layers plus two transparent mechanism atlases. A filename-keyed validator contract keeps each manifest inventory deterministic; permanent CI validates both packs. Concept and QA previews remain under `docs/`, while Unity runtime inputs remain under `Assets/Art/`.

**Tech Stack:** AI raster generation, PNG RGB/RGBA assets, Python 3.11+ standard library validator and `unittest`, GitHub Actions, Unity 6000.0.44f1 SpriteRenderer/2D physics.

**Spec:** `docs/superpowers/specs/2026-08-25-meteora-level-02-art-assets-design.md`

## Global Constraints

- Work only on `art/meteora-level-02-assets`, based on `main` commit `754c5e43ad95537ae26d6f12b463c4e26d65fe15`.
- Keep warm upper-left sunlight, cool atmospheric fill, realistic Meteora geology, and a readable stylized Kolo/mechanism language.
- Do not bake Kolo, HUD, labels, ropes of fixed gameplay length, or interactive objects into parallax backgrounds.
- `sky-base.png` is opaque RGB; every other new runtime PNG is RGBA and must contain at least one genuinely transparent pixel.
- Preserve all Level 01 runtime files and require both Level 01 and Level 02 manifests to pass permanent CI.
- Collision, joints, winch motion, and mass thresholds remain Unity data, not painted pixels.
- Unity/device validation is deferred until the repository is opened on a Mac with a Unity license.

## File Map

- `Tools/Art/meteora_contracts.py` — ordered per-manifest runtime inventories.
- `Tools/Art/validate_meteora_art.py` — validates one or more named manifests against those inventories.
- `Tools/Art/tests/test_validate_meteora_art.py` — parser, manifest-contract, CLI, and workflow regression tests.
- `.github/workflows/validate-meteora-art.yml` — runs tests and validates both packs.
- `Assets/Art/Meteora/Backgrounds/Level02/*.png` — five new parallax layers.
- `Assets/Art/Meteora/Environment/Level02/*.png` — crane and route atlases.
- `Assets/Art/Meteora/meteora-level-02-art-manifest.json` — exact inventory, metadata, and hashes for seven new runtime PNGs.
- `Assets/Art/Meteora/Level02-README.md` — composition order, crop envelope, atlas cell map, and Unity caveats.
- `docs/concept-art/asset-previews/meteora-level-02-*.png` — gameplay, parallax, and atlas QA previews.

---

### Task 1: Add a deterministic Level 02 manifest contract

**Files:**
- Create: `Tools/Art/meteora_contracts.py`
- Modify: `Tools/Art/validate_meteora_art.py`
- Modify: `Tools/Art/tests/test_validate_meteora_art.py`

**Interfaces:**
- Produces: `required_paths_for(manifest_path: Path) -> tuple[str, ...]`
- Changes: `validate_manifest(repo_root: Path, manifest_path: Path) -> list[str]` selects the inventory by manifest filename.
- Preserves: `validate_png_bytes(data: bytes) -> PngInfo` and all PNG stream rules.

- [ ] **Step 1: Write failing contract-selection tests**

Add tests that assert Level 01 returns the existing 12 paths, Level 02 returns exactly the seven paths below, and an unknown filename returns a clear `unknown manifest contract` error:

```python
LEVEL02_PATHS = [
    "Assets/Art/Meteora/Backgrounds/Level02/sky-base.png",
    "Assets/Art/Meteora/Backgrounds/Level02/clouds-depth.png",
    "Assets/Art/Meteora/Backgrounds/Level02/meteora-far.png",
    "Assets/Art/Meteora/Backgrounds/Level02/meteora-mid-gorge.png",
    "Assets/Art/Meteora/Backgrounds/Level02/cliffs-near-station.png",
    "Assets/Art/Meteora/Environment/Level02/cargo-crane-atlas.png",
    "Assets/Art/Meteora/Environment/Level02/cliff-route-atlas.png",
]
```

- [ ] **Step 2: Run the focused tests and confirm RED**

Run: `python3 -m unittest Tools.Art.tests.test_validate_meteora_art.ValidateManifestTests -v`

Expected: failure because contract selection does not exist and the validator still requires only Level 01 paths.

- [ ] **Step 3: Create the contract module**

Implement two immutable ordered tuples keyed by basename:

```python
MANIFEST_CONTRACTS = {
    "meteora-level-01-art-manifest.json": LEVEL01_REQUIRED_ASSET_PATHS,
    "meteora-level-02-art-manifest.json": LEVEL02_REQUIRED_ASSET_PATHS,
}

def required_paths_for(manifest_path: Path) -> tuple[str, ...]:
    try:
        return MANIFEST_CONTRACTS[manifest_path.name]
    except KeyError as error:
        raise ValueError(f"unknown manifest contract: {manifest_path.name}") from error
```

Update `validate_manifest` to call this before inventory comparison and return the error without reading assets when the basename is unknown.

- [ ] **Step 4: Run the focused tests and confirm GREEN**

Run: `python3 -m unittest Tools.Art.tests.test_validate_meteora_art.ValidateManifestTests -v`

Expected: all manifest tests pass, including both ordered contracts and unknown-contract rejection.

- [ ] **Step 5: Run the complete existing suite**

Run: `python3 -m unittest discover -s Tools/Art/tests -v`

Expected: all existing 30 tests plus the new contract tests pass.

- [ ] **Step 6: Commit**

```bash
git add Tools/Art/meteora_contracts.py Tools/Art/validate_meteora_art.py Tools/Art/tests/test_validate_meteora_art.py
git commit -m "feat: add Meteora level 02 art contract"
```

---

### Task 2: Make the CLI and permanent workflow validate both packs

**Files:**
- Modify: `Tools/Art/validate_meteora_art.py`
- Modify: `Tools/Art/tests/test_validate_meteora_art.py`
- Modify: `.github/workflows/validate-meteora-art.yml`

**Interfaces:**
- Changes: `--manifest` becomes repeatable with `action="append"` and remains required.
- Produces: one nonzero exit when any selected manifest fails, with errors grouped by manifest.

- [ ] **Step 1: Write failing CLI/workflow tests**

Add a temporary Level 01 and Level 02 pack, invoke:

```python
result = main([
    "--root", str(self.root),
    "--manifest", str(level01_manifest),
    "--manifest", str(level02_manifest),
])
self.assertEqual(0, result)
```

Also assert the workflow contains both exact manifest paths and only one test-suite command.

- [ ] **Step 2: Run tests and confirm RED**

Run: `python3 -m unittest Tools.Art.tests.test_validate_meteora_art -v`

Expected: the second `--manifest` is rejected or ignored, and the workflow lacks Level 02.

- [ ] **Step 3: Implement repeatable manifest validation**

Use:

```python
parser.add_argument(
    "--manifest", type=Path, action="append", required=True,
    help="manifest path; repeat to validate multiple packs",
)
```

Aggregate all errors as `f"{manifest}: {error}"`; print `Meteora art validation passed (N manifests)` only when every manifest succeeds.

- [ ] **Step 4: Update the workflow command**

Use one invocation:

```yaml
python3 Tools/Art/validate_meteora_art.py \
  --root . \
  --manifest Assets/Art/Meteora/meteora-level-01-art-manifest.json \
  --manifest Assets/Art/Meteora/meteora-level-02-art-manifest.json
```

- [ ] **Step 5: Run tests and confirm GREEN**

Run: `python3 -m unittest discover -s Tools/Art/tests -v`

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add Tools/Art/validate_meteora_art.py Tools/Art/tests/test_validate_meteora_art.py .github/workflows/validate-meteora-art.yml
git commit -m "ci: validate both Meteora art packs"
```

---

### Task 3: Generate the five Level 02 parallax layers

**Files:**
- Create: `Assets/Art/Meteora/Backgrounds/Level02/sky-base.png`
- Create: `Assets/Art/Meteora/Backgrounds/Level02/clouds-depth.png`
- Create: `Assets/Art/Meteora/Backgrounds/Level02/meteora-far.png`
- Create: `Assets/Art/Meteora/Backgrounds/Level02/meteora-mid-gorge.png`
- Create: `Assets/Art/Meteora/Backgrounds/Level02/cliffs-near-station.png`

**Interfaces:**
- Produces: back-to-front layers at consistent aspect ratio, lighting, horizon, and camera-safe composition.
- Consumes: the approved Level 01 previews as visual-style references, not as pixels to overwrite.

- [ ] **Step 1: Generate a gameplay-composition reference**

Generate a 16:9 realistic Meteora gorge at warm morning light: starting cliff left, open crane space center, separate monastery pillar right, clouds below the playable lane, no character, crane, HUD, text, or watermark.

- [ ] **Step 2: Review the reference at full resolution**

Reject it if the monastery is unreadable, the gorge lacks depth, the middle is visually noisy, lighting comes from the wrong side, or any prohibited baked object appears.

- [ ] **Step 3: Generate the opaque sky and transparent cloud layer**

Keep their horizon and sun direction aligned. The sky contains no terrain. Clouds concentrate below the play lane and leave the central rope corridor open.

- [ ] **Step 4: Generate far, mid, and near transparent terrain layers**

Far: pale low-contrast pillars. Mid: distinct gorge walls and right monastery pillar. Near: only left/right framing cliffs and vegetation, with an open central gap.

- [ ] **Step 5: Validate every output before commit**

Run the PNG stream validator directly on each file, inspect alpha presence for the four overlays, and create left/center/right 16:9 composites. Reject any image with black/truncated regions, opaque overlay backgrounds, uncovered crop edges, seams, or baked gameplay objects.

- [ ] **Step 6: Commit**

```bash
git add Assets/Art/Meteora/Backgrounds/Level02
git commit -m "art: add Meteora level 02 parallax layers"
```

---

### Task 4: Generate the crane and cliff-route atlases

**Files:**
- Create: `Assets/Art/Meteora/Environment/Level02/cargo-crane-atlas.png`
- Create: `Assets/Art/Meteora/Environment/Level02/cliff-route-atlas.png`

**Interfaces:**
- Produces: transparent, non-overlapping sprite cells documented for later Unity slicing.
- Consumes: Level 01 wood, rope, bronze, stone, bell, and pushable-stone material language.

- [ ] **Step 1: Generate `cargo-crane-atlas.png`**

Use a transparent 4×3 presentation grid with consistent orthographic side view and warm upper-left light. Include exactly: crane frame, boom, winch, axle/brake, Kolo-sized hook, empty basket, loaded basket, counterweight, passenger platform, straight rope, rope connector, and one empty reserved cell.

- [ ] **Step 2: Inspect isolation and silhouettes**

At original resolution verify that no alpha bounds touch adjacent cells, the hook opening remains visible at mobile scale, empty/loaded baskets share the same proportions, and the rope cells tile without baked knots at both ends.

- [ ] **Step 3: Generate `cliff-route-atlas.png`**

Use a transparent 4×2 grid containing exactly: start ledge edge, destination ledge edge, crane footing, monastery landing stones, broken railing, hook-route anchor, sesame cluster effect, and one empty reserved cell.

- [ ] **Step 4: Inspect atlas integrity**

Reject overlaps, shadows crossing cell boundaries, inconsistent light, opaque backgrounds, text, or high-frequency edge noise.

- [ ] **Step 5: Commit**

```bash
git add Assets/Art/Meteora/Environment/Level02
git commit -m "art: add level 02 crane and route atlases"
```

---

### Task 5: Create the manifest and prove corruption is rejected

**Files:**
- Create: `Assets/Art/Meteora/meteora-level-02-art-manifest.json`
- Modify: `Tools/Art/tests/test_validate_meteora_art.py`

**Interfaces:**
- Produces: exact ordered seven-entry manifest matching `LEVEL02_REQUIRED_ASSET_PATHS`.

- [ ] **Step 1: Write a failing real-pack integration test**

Add a test that resolves the repository root and expects:

```python
errors = validate_manifest(
    repo_root,
    Path("Assets/Art/Meteora/meteora-level-02-art-manifest.json"),
)
self.assertEqual([], errors)
```

Before the manifest exists, expected result is a manifest-read failure.

- [ ] **Step 2: Record deterministic metadata**

For each required path, calculate the actual width, height, SHA-256, and alpha expectation from bytes. Record `role` and `unityValidated: false`; do not copy values from prompts or visual estimates.

- [ ] **Step 3: Run the focused integration test**

Run: `python3 -m unittest Tools.Art.tests.test_validate_meteora_art.ValidateRepositoryPacksTests -v`

Expected: PASS for Level 01 and Level 02.

- [ ] **Step 4: Prove the lower-half corruption gate**

In a temporary copy, truncate one Level 02 IDAT payload while preserving the original header. Run validation and require a nonzero result mentioning `IDAT`, `scanlines`, `CRC`, or `truncated`; restore nothing because the mutation exists only in a temporary directory.

- [ ] **Step 5: Run the full suite and validator**

```bash
python3 -m unittest discover -s Tools/Art/tests -v
python3 Tools/Art/validate_meteora_art.py --root . \
  --manifest Assets/Art/Meteora/meteora-level-01-art-manifest.json \
  --manifest Assets/Art/Meteora/meteora-level-02-art-manifest.json
```

Expected: all tests pass and output reports two validated manifests.

- [ ] **Step 6: Commit**

```bash
git add Assets/Art/Meteora/meteora-level-02-art-manifest.json Tools/Art/tests/test_validate_meteora_art.py
git commit -m "test: validate Meteora level 02 runtime art"
```

---

### Task 6: Produce previews and deterministic Unity import guidance

**Files:**
- Create: `docs/concept-art/asset-previews/meteora-level-02-gameplay-concept.png`
- Create: `docs/concept-art/asset-previews/meteora-level-02-parallax-safe-crops.png`
- Create: `docs/concept-art/asset-previews/meteora-level-02-atlases.png`
- Create: `Assets/Art/Meteora/Level02-README.md`

**Interfaces:**
- Produces: human-readable QA evidence and exact source-to-Unity rectangle conversions.

- [ ] **Step 1: Create the gameplay preview**

Composite the five new background layers, shared Kolo/stone/bell, and new crane components into a representative 16:9 scene. Label nothing inside the runtime scene; any explanatory captions belong outside its frame.

- [ ] **Step 2: Create crop and atlas previews**

The crop preview shows labeled LEFT/CENTER/RIGHT composites using every parallax layer. The atlas preview shows both atlases at useful scale with gutters visible.

- [ ] **Step 3: Measure source rectangles**

Record half-open top-left source rectangles `(x0,y0)-(x1,y1)` for each atlas cell. Convert each to Unity bottom-left coordinates with `SpriteRect(x0, H-y1, x1-x0, y1-y0)`; never infer rectangles from grid intent if alpha crosses a boundary.

- [ ] **Step 4: Document composition and caveats**

Write exact layer order, provisional parallax factors, tested crop envelope, atlas names/rectangles, shared Level 01 dependencies, validation commands, and the explicit statement that Unity/device checks remain pending.

- [ ] **Step 5: Inspect all three previews at original resolution**

Require full-height rendering, no black lower halves, no missing layer, no clipped atlas cell, readable hook/basket/platform silhouettes, and visual continuity with Level 01.

- [ ] **Step 6: Commit**

```bash
git add docs/concept-art/asset-previews/meteora-level-02-*.png Assets/Art/Meteora/Level02-README.md
git commit -m "docs: add Meteora level 02 art previews"
```

---

### Task 7: Run exact-head CI and final review

**Files:**
- Verify only; modify files only to address a reproduced failure.

**Interfaces:**
- Produces: exact commit SHA, successful permanent art workflow, and a merge-readiness verdict.

- [ ] **Step 1: Run fresh local verification**

Run the complete unit suite and both-manifest validator from a clean exact-head checkout. Record test count, validator output, and exit codes.

- [ ] **Step 2: Push the exact branch head**

Push `art/meteora-level-02-assets` without force and record its 40-character SHA.

- [ ] **Step 3: Verify GitHub Actions**

Locate the `Validate Meteora art` push run whose `head_sha` exactly equals the recorded SHA. Require successful test and runtime-validation steps. Do not treat the Unity workflow’s missing-license gate as an art failure.

- [ ] **Step 4: Request a final whole-branch review**

Compare base `754c5e43ad95537ae26d6f12b463c4e26d65fe15` to the exact branch head. Review asset inventory, visual contracts, validator security/resource bounds, test coverage, workflow, documentation, and absence of temporary workflows.

- [ ] **Step 5: Resolve findings with TDD**

For every Critical or Important finding: reproduce it, add a failing test when code behavior is involved, apply the smallest correction, rerun the full suite, and obtain fresh exact-head CI evidence.

- [ ] **Step 6: Present integration options**

Only after all checks pass, offer merge to `main`, Pull Request creation, or keeping the branch separate. Do not merge without the user’s selection.
