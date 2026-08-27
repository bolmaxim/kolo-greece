# Meteora Level 03 Art Assets Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Создать production starter art pack уровня «Ветер над пропастью»: пять реалистичных слоёв Метеор, два модульных атласа, два игровых концепта, два QA-превью, manifest Level 03 и постоянную проверку трёх art packs в CI.

**Architecture:** Runtime-графика остаётся независимой от логики Unity: фон состоит из пяти параллакс-слоёв на общем холсте, а мельница, парус, мост и погоня собираются из двух прозрачных атласов. Filename-keyed Python contract задаёт точный inventory Level 03; hardened PNG validator проверяет порядок, размеры, SHA-256, `colorType`, прозрачность и resource bounds, а GitHub Actions запускает unit tests один раз и валидирует три manifest одной CLI-командой.

**Tech Stack:** Unity-compatible PNG, built-in ImageGen, ImageMagick 6 для детерминированных QA-композитов, Python 3 standard library (`unittest`, `json`, `zlib`, `hashlib`), GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-08-27-meteora-level-03-art-assets-design.md`

## Global Constraints

- Основной режим уровня — 2.5D side view; камера за спиной используется только в 15–25-секундной погоне.
- Новое состояние Kolo не добавляется; ветер комбинируется с уже существующим тяжёлым состоянием.
- Геология и освещение Метеор максимально реалистичны; Kolo и интерактивные механизмы сохраняют чистые мобильные силуэты.
- Свет тёплый позднеутренний слева сверху, ущелье получает холодное голубое заполнение.
- Runtime art не является collision authority и не содержит запечённых траекторий, разрушающихся последовательностей или фиксированной длины канатов.
- Runtime inventory содержит ровно семь новых PNG: пять parallax и два atlas.
- Все parallax PNG имеют общий холст `1672×941`; `sky-wind-base.png` — PNG color type `2`, остальные runtime PNG — color type `6` с настоящей прозрачностью.
- Атласы имеют геометрию `1448×1086`, карту `4×3` и ячейки `362×362`; двенадцатая ячейка зарезервирована, а не используется автоматически.
- Для runtime-границ значимая альфа определяется как `alpha >= 2/255`; `1/255` допускается только как документированный неотрисовываемый generator fringe внутри ручных SpriteRect.
- QA-превью и концепты не входят в runtime manifest и не считаются доказательством готовой Unity-сцены.
- Unity import, slicing, pivots, фильтрация, mip bleed, compression, частицы, производительность, safe area и iPhone readability остаются pending до проверки на Mac/iPhone.
- Ни один этап не изменяет `main`; работа выполняется в `art/meteora-level-03-assets` обычными non-force коммитами.

---

### Task 1: Добавить filename-keyed контракт Level 03

**Files:**
- Modify: `Tools/Art/meteora_contracts.py`
- Modify: `Tools/Art/validate_meteora_art.py`
- Modify: `Tools/Art/tests/test_validate_meteora_art.py`

**Interfaces:**
- Consumes: `required_paths_for(manifest_path: Path) -> tuple[str, ...]`, `COLOR_TYPE_REQUIRED_MANIFESTS`.
- Produces: `LEVEL03_REQUIRED_ASSET_PATHS`, contract name `meteora-level-03-art-manifest.json`, обязательный `colorType` для Level 03.

- [ ] **Step 1: Написать failing contract tests**

Добавить тесты, требующие точный tuple и неизменность Level 01/02:

```python
def test_level03_contract_has_exact_order(self):
    self.assertEqual(
        (
            "Assets/Art/Meteora/Backgrounds/Level03/sky-wind-base.png",
            "Assets/Art/Meteora/Backgrounds/Level03/cloud-streams.png",
            "Assets/Art/Meteora/Backgrounds/Level03/meteora-wind-far.png",
            "Assets/Art/Meteora/Backgrounds/Level03/meteora-wind-mid.png",
            "Assets/Art/Meteora/Backgrounds/Level03/cliffs-wind-near.png",
            "Assets/Art/Meteora/Environment/Level03/windmill-sail-atlas.png",
            "Assets/Art/Meteora/Environment/Level03/wind-bridge-chase-atlas.png",
        ),
        required_paths_for(Path("meteora-level-03-art-manifest.json")),
    )

def test_level03_manifest_requires_color_type(self):
    errors = validate_manifest(self.root, Path("meteora-level-03-art-manifest.json"))
    self.assertTrue(any("colorType is required" in error for error in errors))
```

- [ ] **Step 2: Запустить focused tests и подтвердить RED**

Run:

```bash
python3 -m unittest Tools.Art.tests.test_validate_meteora_art.ValidateManifestTests -v
```

Expected: новые Level 03 tests падают из-за `unknown manifest contract` и отсутствующего обязательного `colorType`.

- [ ] **Step 3: Реализовать минимальный контракт**

Добавить в `meteora_contracts.py` точный tuple из Step 1 и запись:

```python
MANIFEST_CONTRACTS = {
    "meteora-level-01-art-manifest.json": LEVEL01_REQUIRED_ASSET_PATHS,
    "meteora-level-02-art-manifest.json": LEVEL02_REQUIRED_ASSET_PATHS,
    "meteora-level-03-art-manifest.json": LEVEL03_REQUIRED_ASSET_PATHS,
}
```

Расширить validator:

```python
COLOR_TYPE_REQUIRED_MANIFESTS = {
    "meteora-level-02-art-manifest.json",
    "meteora-level-03-art-manifest.json",
}
```

- [ ] **Step 4: Запустить полный suite**

Run:

```bash
python3 -m unittest discover -s Tools/Art/tests -v
python3 -m py_compile Tools/Art/meteora_contracts.py Tools/Art/validate_meteora_art.py Tools/Art/tests/test_validate_meteora_art.py
```

Expected: exit `0`; прежние 54 tests и новые contract tests проходят.

- [ ] **Step 5: Commit**

```bash
git add Tools/Art/meteora_contracts.py Tools/Art/validate_meteora_art.py Tools/Art/tests/test_validate_meteora_art.py
git commit -m "feat: add Meteora level 03 art contract"
```

---

### Task 2: Создать пять parallax-слоёв Level 03

**Files:**
- Create: `Assets/Art/Meteora/Backgrounds/Level03/sky-wind-base.png`
- Create: `Assets/Art/Meteora/Backgrounds/Level03/cloud-streams.png`
- Create: `Assets/Art/Meteora/Backgrounds/Level03/meteora-wind-far.png`
- Create: `Assets/Art/Meteora/Backgrounds/Level03/meteora-wind-mid.png`
- Create: `Assets/Art/Meteora/Backgrounds/Level03/cliffs-wind-near.png`

**Interfaces:**
- Consumes: approved Level 01/02 visual language and Level 03 spec.
- Produces: five exact `1672×941` layers composable back-to-front in listed order.

- [ ] **Step 1: Подготовить точный ImageGen brief**

Использовать built-in ImageGen и references из утверждённых Level 02 composite/concept. Общий prompt должен фиксировать:

```text
Realistic Meteora late-morning gorge for a polished 2.5D mobile puzzle platformer;
warm upper-left sunlight, cool blue atmospheric fill, dramatic cloud motion,
open playable center corridor, destination chapel on a right middle-distance pillar,
no Kolo, no UI, no windmill, no bridge, no text, no black or blank lower half.
All five deliverables share one 1672x941 camera canvas and geometry registration.
```

- [ ] **Step 2: Создать непрозрачный sky base**

Сгенерировать/нормализовать `sky-wind-base.png` как 8-bit RGB type `2`, без alpha/tRNS и без запечённых скал переднего плана.

- [ ] **Step 3: Создать четыре прозрачных зарегистрированных слоя**

Для каждого слоя использовать один и тот же canvas:

```text
cloud-streams: soft cloud ribbons and haze only;
meteora-wind-far: pale low-contrast distant pillars only;
meteora-wind-mid: mid-distance pillars plus small right-side chapel destination;
cliffs-wind-near: near cliff edges, grass, shrubs and wind-reactive foliage only.
Transparent RGBA background; no checkerboard, black fill or baked sky.
```

- [ ] **Step 4: Проверить stream, geometry и alpha**

Run:

```bash
identify -format '%f %wx%h %[channels]\n' Assets/Art/Meteora/Backgrounds/Level03/*.png
python3 - <<'PY'
from pathlib import Path
from Tools.Art.validate_meteora_art import validate_png_bytes
for path in sorted(Path('Assets/Art/Meteora/Backgrounds/Level03').glob('*.png')):
    info = validate_png_bytes(path.read_bytes())
    print(path.name, info.width, info.height, info.color_type, info.has_transparent_pixels)
PY
```

Expected: all `1672×941`; sky type `2` opaque; four overlays type `6` with transparent pixels.

- [ ] **Step 5: Создать три временных safe crops и визуально проверить**

Composite order:

```bash
convert sky-wind-base.png cloud-streams.png -compose over -composite \
  meteora-wind-far.png -compose over -composite \
  meteora-wind-mid.png -compose over -composite \
  cliffs-wind-near.png -compose over -composite level03-composite.png
convert level03-composite.png -crop 1280x720+0+110 +repage left.png
convert level03-composite.png -crop 1280x720+196+110 +repage center.png
convert level03-composite.png -crop 1280x720+392+110 +repage right.png
```

Inspect all five layers and the three crops with `view_image(detail="original")`. Reject black/truncated areas, high-contrast far pillars, unreadable chapel, hard cloud seams, floating edge fragments at alpha `>=2/255`, or missing open corridor.

- [ ] **Step 6: Commit**

```bash
git add Assets/Art/Meteora/Backgrounds/Level03
git commit -m "art: add Meteora level 03 parallax layers"
```

---

### Task 3: Создать атлас мельницы и парусной платформы

**Files:**
- Create: `Assets/Art/Meteora/Environment/Level03/windmill-sail-atlas.png`

**Interfaces:**
- Consumes: Level 02 timber/bronze/rope material language.
- Produces: `1448×1086` RGBA atlas, `4×3`, cells `362×362`.

- [ ] **Step 1: Зафиксировать row-major cell map**

```text
1 stone-and-timber windmill base
2 detachable four-blade assembly
3 rotating wind-direction head
4 three-position lever
5 closed sail
6 open sail
7 small passenger sail platform
8 repeatable rope segment
9 fabric direction ribbons
10 bronze hinge and axle
11 wind vane
12 reserved transparent cell
```

- [ ] **Step 2: Сгенерировать atlas built-in ImageGen**

Prompt:

```text
Transparent 4x3 production atlas for the same realistic 2.5D Meteora mobile game.
Orthographic three-quarter side-readable props, consistent warm upper-left light,
weathered Greek timber, pale sandstone, aged bronze, linen sail and fibrous rope.
Exactly the eleven row-major objects from the supplied cell map; cell 12 empty.
No text, labels, Kolo, background, scenery, UI, checkerboard or cast shadow crossing cells.
Every object centered with generous transparent gutters and no alpha>=2/255 on boundaries.
```

- [ ] **Step 3: Нормализовать без перерисовки объектов**

Нормализовать только canvas/bit depth/color type при необходимости. Запрещено использовать raster cleanup для дорисовки отсутствующих деталей или перемещения объектов между ячейками.

- [ ] **Step 4: Проверить atlas contract**

Run:

```bash
identify -format '%wx%h %[channels]\n' Assets/Art/Meteora/Environment/Level03/windmill-sail-atlas.png
python3 Tools/Art/validate_meteora_art.py --help >/dev/null
```

Дополнительный measurement script должен подтвердить: `1448×1086`, type `6`, настоящая transparency, `alpha>=2/255` не пересекает `x=362,724,1086` или `y=362,724`, cell 12 не содержит `alpha>=2/255`.

- [ ] **Step 5: Inspect original resolution**

Проверить `view_image(detail="original")`: три положения механики читаются через отдельные детали, открытый/закрытый парус различаются, passenger platform не похожа на cargo basket, канат tileable, reserved cell пуст визуально.

- [ ] **Step 6: Commit**

```bash
git add Assets/Art/Meteora/Environment/Level03/windmill-sail-atlas.png
git commit -m "art: add Meteora level 03 windmill atlas"
```

---

### Task 4: Создать атлас моста и модулей погони

**Files:**
- Create: `Assets/Art/Meteora/Environment/Level03/wind-bridge-chase-atlas.png`

**Interfaces:**
- Consumes: bridge/rope language from prior levels and chase warning rules from spec.
- Produces: `1448×1086` RGBA atlas, `4×3`, cells `362×362`.

- [ ] **Step 1: Зафиксировать row-major cell map**

```text
1 intact suspension-bridge segment
2 taut bridge edge
3 sagging bridge edge
4 cracked plank
5 fallen beam with duck-under clearance
6 stone road gap
7 small warning debris
8 large falling rock
9 safe finish platform
10 bell trigger mechanism
11 wind/leaves particle cluster
12 reserved transparent cell
```

- [ ] **Step 2: Сгенерировать atlas built-in ImageGen**

Prompt:

```text
Transparent 4x3 modular chase atlas matching the approved realistic Meteora game.
Exactly eleven separate row-major objects; cell 12 empty. Side-readable and usable in
both 2.5D and behind-camera chase assembly. Warm upper-left light, pale sandstone,
weathered timber, old rope and aged bronze. Warning debris visibly smaller than the
falling rock. No full route, baked motion, character, text, UI, background or shadows
crossing cells; generous transparent gutters; no alpha>=2/255 on cell boundaries.
```

- [ ] **Step 3: Проверить geometry, boundaries и semantics**

Require: `1448×1086`, type `6`, real transparency, no significant alpha across grid, reserved cell empty at `alpha>=2/255`. Visually verify intact/taut/sagging variants are distinct, duck beam clearance is obvious, gap does not contain a baked collider shape, and warning debris reads one second before the large hazard at target scale.

- [ ] **Step 4: Commit**

```bash
git add Assets/Art/Meteora/Environment/Level03/wind-bridge-chase-atlas.png
git commit -m "art: add Meteora level 03 chase atlas"
```

---

### Task 5: Создать manifest Level 03 и постоянную three-pack CI-проверку

**Files:**
- Create: `Assets/Art/Meteora/meteora-level-03-art-manifest.json`
- Modify: `Tools/Art/tests/test_validate_meteora_art.py`
- Modify: `.github/workflows/validate-meteora-art.yml`

**Interfaces:**
- Consumes: exact seven runtime PNG bytes, `LEVEL03_REQUIRED_ASSET_PATHS`, repeatable `--manifest` CLI.
- Produces: schema-v1 Level 03 manifest and one permanent three-manifest validator invocation.

- [ ] **Step 1: Написать failing repository-pack и workflow tests**

```python
def test_level03_repository_pack_is_valid(self):
    repo_root = Path(__file__).resolve().parents[3]
    self.assertEqual(
        [],
        validate_manifest(
            repo_root,
            Path("Assets/Art/Meteora/meteora-level-03-art-manifest.json"),
        ),
    )

def test_workflow_validates_three_packs_in_one_invocation(self):
    workflow = self._workflow_text()
    self.assertEqual(1, workflow.count("python3 Tools/Art/validate_meteora_art.py"))
    self.assertIn("--manifest Assets/Art/Meteora/meteora-level-03-art-manifest.json", workflow)
    self.assertIn("      - art/meteora-level-03-assets", workflow)
```

- [ ] **Step 2: Запустить focused tests и подтвердить RED**

```bash
python3 -m unittest Tools.Art.tests.test_validate_meteora_art.WorkflowTests Tools.Art.tests.test_validate_meteora_art.ValidateRepositoryPacksTests -v
```

Expected: Level 03 manifest отсутствует; workflow не содержит третью ветку/manifest.

- [ ] **Step 3: Создать exact manifest**

Top-level:

```json
{
  "schemaVersion": 1,
  "level": "Meteora/Level03",
  "generatedAt": "2026-08-27",
  "unityValidated": false,
  "assets": []
}
```

Заполнить `assets` в exact contract order. Для каждого файла вычислить реальные `width`, `height`, `sha256`, `colorType`, `alphaExpectation` и `role`; запрещено копировать hash из временного generation output.

- [ ] **Step 4: Расширить workflow без дублирования команд**

Добавить push branch `art/meteora-level-03-assets` и третий аргумент после Level 02:

```yaml
          --manifest Assets/Art/Meteora/meteora-level-03-art-manifest.json
```

Сохранить `contents: read`, `pull_request`, `workflow_dispatch`, timeout `10`, один unittest discovery и один validator process.

- [ ] **Step 5: Запустить полный GREEN и corruption proof**

```bash
python3 -m unittest discover -s Tools/Art/tests -v
python3 Tools/Art/validate_meteora_art.py --root . \
  --manifest Assets/Art/Meteora/meteora-level-01-art-manifest.json \
  --manifest Assets/Art/Meteora/meteora-level-02-art-manifest.json \
  --manifest Assets/Art/Meteora/meteora-level-03-art-manifest.json
```

На временной копии обрезать один Level 03 PNG после IHDR и подтвердить nonzero exit с `truncated PNG chunk data`. Не изменять repository PNG.

- [ ] **Step 6: Commit и exact-head CI**

```bash
git add Assets/Art/Meteora/meteora-level-03-art-manifest.json \
  Tools/Art/tests/test_validate_meteora_art.py \
  .github/workflows/validate-meteora-art.yml
git commit -m "test: validate Meteora level 03 runtime art"
```

Require `Validate Meteora art` push run with exact commit SHA and successful unit-test/runtime-art steps.

---

### Task 6: Создать concepts, QA previews и Unity handoff

**Files:**
- Create: `docs/concept-art/asset-previews/meteora-level-03-gameplay-concept.png`
- Create: `docs/concept-art/asset-previews/meteora-level-03-chase-concept.png`
- Create: `docs/concept-art/asset-previews/meteora-level-03-parallax-safe-crops.png`
- Create: `docs/concept-art/asset-previews/meteora-level-03-atlases.png`
- Create: `Assets/Art/Meteora/Level03-README.md`

**Interfaces:**
- Consumes: exact five layers, exact two atlases, approved Kolo/heavy-state references.
- Produces: two visual targets, two deterministic QA boards and exact Unity import guidance.

- [ ] **Step 1: Сгенерировать gameplay concept**

Built-in ImageGen, output normalized to `1664×936` RGB:

```text
Polished realistic 2.5D side-view Meteora mobile gameplay screenshot. Kolo in heavy
state on the left, central old windmill with readable three-position lever, visible
wind ribbons, raised sail platform, stretched suspension bridge, right chapel goal.
Warm upper-left late-morning sun and cool gorge depth. No HUD, text, humans, black
bands or cropped lower half. Wind readable without covering the playable lane.
```

- [ ] **Step 2: Сгенерировать chase concept**

Built-in ImageGen, output normalized to `1664×936` RGB:

```text
Same Meteora materials and lighting, camera behind rolling Kolo during a 3-lane
15-25 second chase. Broken path ahead, advance warning debris, one jump gap, one
duck-under beam, large falling rock shown at safe distance, chapel destination visible.
Clear central route, no HUD, text, speed lines hiding hazards, black or blank lower half.
```

- [ ] **Step 3: Создать deterministic parallax board**

Composite exact runtime layers, затем LEFT `[0,1280)×[110,830)`, CENTER `[196,1476)×[110,830)`, RIGHT `[392,1672)×[110,830)`. Создать `3904×808` RGB board: панели `1280×720` в `(16,72)`, `(1312,72)`, `(2608,72)`; labels находятся вне изображений. Fresh `compare -metric AE` должен вернуть `0` для всех трёх панелей.

- [ ] **Step 4: Создать deterministic atlas board**

Создать `2956×1246` RGB board на solid `#343b3f`. Поместить `windmill-sail-atlas.png` native-size `1448×1086` в `(20,140)` и `wind-bridge-chase-atlas.png` в `(1488,140)`. Labels находятся выше content. Fresh AE comparison против independently flattened originals возвращает `0` для обоих.

- [ ] **Step 5: Написать Level03 README**

Документировать:

- exact inventory и reused Level 01/02 dependencies;
- back-to-front factors `0.00`, `0.06`, `0.11`, `0.22`, `0.36`;
- half-open source crop rectangles;
- обе `4×3` cell maps и conversion `SpriteRect(x0, H-y1, x1-x0, y1-y0)`;
- manual SpriteRect и `alpha 1/255` fringe ruling;
- команды unit tests и three-manifest validation;
- wind direction remains Unity state, art is not collision authority;
- pending slicing, pivots, PPU, filtering/mips, rope tiling, particles, sorting, seams, compression, memory, frame rate, safe area, chase camera and target-iPhone readability;
- concepts/QA previews are not runtime assets or proof of final in-engine quality.

- [ ] **Step 6: Inspect original resolution и integrity**

Проверить четыре previews через `view_image(detail="original")`. Require complete lower halves, all required gameplay objects, readable chase warning order, exact three crop panels and both full atlases. Прогнать `validate_png_bytes` для каждого preview; previews не добавлять в manifest.

- [ ] **Step 7: Commit**

```bash
git add docs/concept-art/asset-previews/meteora-level-03-*.png Assets/Art/Meteora/Level03-README.md
git commit -m "docs: add Meteora level 03 art previews"
```

---

### Task 7: Exact-head verification и final whole-branch review

**Files:**
- Verify only; modify only through one reviewed fix wave for reproduced Critical/Important findings.

**Interfaces:**
- Consumes: complete feature branch and permanent three-pack workflow.
- Produces: exact SHA, successful CI evidence, whole-branch review and integration choice.

- [ ] **Step 1: Fresh verification**

```bash
python3 -m unittest discover -s Tools/Art/tests -v
python3 Tools/Art/validate_meteora_art.py --root . \
  --manifest Assets/Art/Meteora/meteora-level-01-art-manifest.json \
  --manifest Assets/Art/Meteora/meteora-level-02-art-manifest.json \
  --manifest Assets/Art/Meteora/meteora-level-03-art-manifest.json
```

Record exit codes, test count, validator output, exact 40-character feature SHA and file inventory.

- [ ] **Step 2: Verify exact-head GitHub Actions**

Require `Validate Meteora art` push run whose `head_sha` equals the feature SHA, with successful unit-test and runtime-art steps. `Unity tests` missing-license gate is documented separately and is not treated as an art-validator failure.

- [ ] **Step 3: Request final whole-branch review**

Review `17caa50b5511c5f81d026b02e21a7cde9b87e063..HEAD` against the spec. Cover runtime inventory, parallax visual depth, atlas isolation, chase readability, PNG resource/security bounds, manifest metadata, three-manifest aggregation, workflow scope, README and preview integrity.

- [ ] **Step 4: Resolve findings once**

For every Critical/Important: reproduce, add a failing test for code behavior, make the smallest fix, rerun full suite and exact-head CI, then obtain one scoped re-review. Record deferred Minor findings for Unity/device validation.

- [ ] **Step 5: Present integration options**

Only after no Critical/Important remain, offer:

1. merge `art/meteora-level-03-assets` to `main`;
2. create a Pull Request to `main`;
3. keep the feature branch.

Do not update `main` without the user's selection.

