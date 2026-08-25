# Meteora Level 01 Art Assets Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Generate, validate, and store the complete 2.5D starter texture and sprite pack for the first Meteora level.

**Architecture:** The approved screenshot is the visual authority. Runtime-ready source PNGs are grouped by character, parallax background, environment, effects, and UI under `Assets/Art/`; concept sheets remain under `docs/`. Asset generation is independent from gameplay code, and the existing greybox remains the collision authority.

**Tech Stack:** Built-in image generation, PNG with alpha where specified, Unity 6 `6000.0.44f1`, SpriteRenderer, URP-compatible 2.5D presentation, GitHub blobs/trees/commits.

**Spec:** `docs/superpowers/specs/2026-08-24-meteora-level-01-art-assets-design.md`

## Global Constraints

- Match `docs/concept-art/level-screenshots/meteora-levels-01-07.png`, especially panel 1 and the Heavy-state appearance.
- Preserve one consistent Kolo identity: golden Greek sesame bread ring, central hole, large friendly eyes, no arms or legs, no frosting.
- Warm sunlight comes from upper left; cool sky fill supplies shadows.
- Background scenery is realistic; Kolo and interactables have stronger silhouette and contrast for mobile readability.
- No humans, weapons, text, logos, watermarks, HUD baked into backgrounds, or protagonist baked into backgrounds.
- Files named by this plan are intended for runtime and live under `Assets/Art/`; concept-only sheets remain under `docs/`.
- Generated images are starter production assets; in-engine quality and performance remain unverified until Unity is available.

---

### Task 1: Generate Normal and Heavy Kolo sheets

**Files:**
- Create: `Assets/Art/Meteora/Characters/Kolo/kolo-normal-sheet.png`
- Create: `Assets/Art/Meteora/Characters/Kolo/kolo-heavy-sheet.png`

**Interfaces:**
- Consumes: approved Meteora contact sheet as a visual reference.
- Produces: two transparent character sheets used by later Unity sprite slicing.

- [x] **Step 1: Generate the Normal sheet**

Use the built-in image generator with the approved Meteora sheet as the reference and this exact intent:

```text
Transparent production sprite sheet for Kolo, the same living Greek sesame bread ring from the reference. Five evenly separated full-body states: friendly idle, rolling side view, airborne jump, soft landing squash, surprised expression. Identical golden baked crust, sesame distribution, central hole, eye shape, body proportions, material and upper-left lighting in every cell. Premium family mobile game rendering. No environment, floor, shadow plate, labels, text, arms, legs, frosting, watermark, or overlapping sprites. Genuine transparent background.
```

- [x] **Step 2: Inspect Normal sheet**

Open the output at original detail. Reject and regenerate if the number of states is not five, sprites overlap, the hole closes, identity changes, or transparency is absent.

- [x] **Step 3: Generate the Heavy sheet**

```text
Transparent production sprite sheet for the exact same Kolo identity. Four evenly separated full-body Heavy-state poses: heavy idle, heavy rolling side view, short heavy jump, heavy landing squash. Preserve crust, sesame, hole, eyes and proportions; show a physically readable clear-blue water-filled lower portion inside the bread ring and stronger lower-body squash. Same upper-left lighting. No environment, labels, text, arms, legs, frosting, watermark, or overlapping sprites. Genuine transparent background.
```

- [x] **Step 4: Validate files**

Run `file` and an alpha-channel inspection tool on both PNGs. Expected: readable PNG, nonzero dimensions, alpha channel present. Visually confirm both sheets show the same character.

- [x] **Step 5: Commit character sheets**

Commit only the two validated PNGs with message `art: add Kolo Meteora character sheets`.

---

### Task 2: Generate five parallax background layers

**Files:**
- Create: `Assets/Art/Meteora/Backgrounds/Level01/sky-base.png`
- Create: `Assets/Art/Meteora/Backgrounds/Level01/clouds-far.png`
- Create: `Assets/Art/Meteora/Backgrounds/Level01/meteora-far.png`
- Create: `Assets/Art/Meteora/Backgrounds/Level01/meteora-mid.png`
- Create: `Assets/Art/Meteora/Backgrounds/Level01/cliffs-near.png`

**Interfaces:**
- Consumes: the approved landscape, lighting direction, and side-camera framing.
- Produces: five single-sprite layers ordered from sky to foreground.

- [x] **Step 1: Generate opaque sky**

```text
Wide seamless-feeling mobile game sky backdrop for a Meteora level, warm early-morning sun from upper left, natural blue-to-gold gradient and subtle atmospheric haze. No land, rocks, buildings, clouds, characters, UI, text, logo, or watermark. Opaque full-frame background.
```

- [x] **Step 2: Generate transparent clouds**

```text
Wide sparse layer of realistic soft Mediterranean clouds and mist wisps matching warm upper-left sunrise lighting. Clouds occupy varied heights with large transparent gaps for parallax. No sky color fill, landscape, buildings, characters, UI, text, logo, or watermark. Genuine transparent background.
```

- [x] **Step 3: Generate transparent far Meteora**

```text
Wide distant Meteora panorama layer: realistic pale rock pillars softened by atmospheric perspective, two tiny Greek Orthodox monastery silhouettes, remote mountain haze, low contrast and cool values, warm rim light from upper left. Keep the bottom contour usable behind a gameplay plane. No sky fill, foreground objects, character, HUD, text, logo, or watermark. Genuine transparent background.
```

- [x] **Step 4: Generate transparent middle distance**

```text
Wide mid-distance Meteora layer: realistic limestone pillars, sparse pine and scrub vegetation, a small monastery, medium contrast, natural depth and warm upper-left sunlight. Leave the central gameplay band readable and avoid large foreground occlusion. No sky fill, Kolo, mechanisms, HUD, text, logo, or watermark. Genuine transparent background.
```

- [x] **Step 5: Generate transparent near cliffs**

```text
Wide foreground framing layer for a side-view Meteora mobile platformer: detailed cliff ledges, small grasses and pine branches concentrated at far left, far right and lower edge, with the central route mostly open. Stronger contrast and warm upper-left light. No sky fill, player, puzzle objects, HUD, text, logo, or watermark. Genuine transparent background.
```

- [x] **Step 6: Validate the layer set**

Open all five images in order. Confirm consistent horizon, lighting and color; no Kolo/HUD; alpha on layers 2–5; sky opaque. Record dimensions and SHA-256 values in the asset manifest created by Task 5.

- [x] **Step 7: Commit parallax layers**

Commit with message `art: add Meteora level 01 parallax layers`.

---

### Task 3: Generate surfaces, mechanisms, interactables, and effects

**Files:**
- Create: `Assets/Art/Meteora/Environment/rock-surfaces-atlas.png`
- Create: `Assets/Art/Meteora/Environment/wood-rope-bronze-atlas.png`
- Create: `Assets/Art/Meteora/Environment/interactables-atlas.png`
- Create: `Assets/Art/Meteora/Environment/water-honey-effects.png`

**Interfaces:**
- Consumes: the first-level object list from `MeteoraSliceBuilder`.
- Produces: four separated atlases to be sliced without changing colliders.

- [x] **Step 1: Generate rock atlas**

```text
Square production texture atlas with four equal non-overlapping material swatches: natural Meteora cliff face, cut monastery stone blocks, cracked bridge stone, and flat walkable limestone. Realistic detail, coherent scale, near-neutral lighting with subtle upper-left direction, edge-to-edge swatches, no perspective objects, labels, text, logo, watermark, vegetation, or baked deep shadows.
```

- [x] **Step 2: Generate wood, rope, and bronze atlas**

```text
Square transparent production atlas with clearly separated game-art pieces: weathered wooden plank surface, wooden beam end, straight rope segment, curved rope segment, pulley wheel, iron hook, bronze pressure-plate surface, and bronze bell surface. Realistic materials with consistent warm upper-left light, generous separation, no labels, text, characters, logo, watermark, or overlaps. Genuine transparent background outside pieces.
```

- [x] **Step 3: Generate interactables atlas**

```text
Square transparent side-view sprite atlas for one Meteora puzzle level. Exactly seven separated objects: pressure plate raised, pressure plate pressed, round pushable stone, hanging wooden platform with rope attachment, cracked breakable stone platform, glowing blue Heavy water source, bronze monastery finish bell, plus a small sesame collectible placed separately. Consistent scale language, realistic materials, readable mobile silhouettes, warm upper-left lighting. No labels, text, character, environment, logo, watermark, or overlaps. Genuine transparent background.
```

- [x] **Step 4: Generate water and honey effects atlas**

```text
Square transparent effects atlas with separated mobile-game elements: shallow blue water pool edge, upward splash, three water droplets, translucent blue Heavy-state shimmer, amber honey coating patch, hanging honey drip, and small landing dust puff. Polished semi-realistic 2.5D rendering, no labels, text, objects, character, logo, watermark, or overlaps. Genuine transparent background.
```

- [x] **Step 5: Validate atlas completeness**

At original detail, count every requested region, check separation, transparency, consistent light direction, and mobile readability. Reject any atlas with missing, merged, labeled, or unintentionally duplicated regions.

- [x] **Step 6: Commit environment assets**

Commit with message `art: add Meteora environment and effects atlases`.

---

### Task 4: Generate mobile control icons

**Files:**
- Create: `Assets/Art/UI/Controls/touch-controls-atlas.png`

**Interfaces:**
- Consumes: existing `TouchInputView` actions.
- Produces: six transparent icons for later Unity slicing.

- [x] **Step 1: Generate icon atlas**

```text
Transparent square mobile game UI icon atlas with exactly six evenly spaced symbols: left arrow, right arrow, upward jump arrow with a small bounce arc, roll/flatten symbol showing a ring squashing, interaction hand/tap symbol, and pause symbol. Soft rounded white shapes with subtle charcoal shadow, coherent line weight, readable at small iPhone size. No circular button backgrounds, words, letters, labels, character art, logo, watermark, or overlaps. Genuine transparent background.
```

- [x] **Step 2: Validate at small size**

Preview the atlas reduced to approximately phone-control scale. Confirm all six actions remain distinguishable and left/right arrows are not duplicated or reversed incorrectly.

- [x] **Step 3: Commit UI atlas**

Commit with message `art: add touch control icon atlas`.

---

### Task 5: Add manifest, verify repository assets, and document Unity handoff

**Files:**
- Create: `Assets/Art/Meteora/meteora-level-01-art-manifest.json`
- Create: `Assets/Art/Meteora/README.md`
- Modify: `docs/superpowers/plans/2026-08-24-meteora-level-01-art-assets.md`

**Interfaces:**
- Consumes: the 12 final PNGs from Tasks 1–4.
- Produces: exact asset inventory, integrity metadata, intended alpha mode, and Unity integration instructions.

- [x] **Step 1: Build manifest**

For every PNG, record relative path, pixel width, pixel height, SHA-256, alpha expectation (`opaque` or `transparent`), and usage (`character-sheet`, `parallax`, `atlas`, or `ui-atlas`). Reject duplicate hashes unless duplication is intentional and documented.

- [x] **Step 2: Write Unity handoff README**

Document layer order, intended sprite slicing, the rule that greybox colliders remain authoritative, and the deferred checks: pixels-per-unit, compression, memory, draw calls, seams, safe area, and target-iPhone frame rate.

- [x] **Step 3: Run repository validation**

Verify exactly 12 named PNG deliverables exist, all parse as PNG, expected transparent assets expose alpha, manifest hashes match, and no file lives under `docs/` by mistake.

- [x] **Step 4: Visual review against authority**

Compare the complete pack with the Meteora screenshot: Kolo identity, geology, monastery silhouettes, warm/cool lighting, material family, and mobile readability must align. Regenerate only the failing asset rather than changing the approved direction.

- [x] **Step 5: Mark completed plan checkboxes and commit**

Commit manifest, README, and completed plan with message `docs: finalize Meteora level 01 art pack`.

- [x] **Step 6: Final branch review**

Compare the feature branch to its base and confirm changes contain only the spec, plan, 12 PNGs, manifest, and art README. State explicitly that Unity import and device performance have not been run.
