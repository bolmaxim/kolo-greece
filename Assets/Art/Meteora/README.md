# Meteora Level 01 starter art pack

This directory contains the repaired starter runtime art pack for the first Meteora level. The approved Meteora contact sheet remains the visual authority: realistic limestone and monastery scenery, warm upper-left sunlight with cool sky fill, and a highly readable golden sesame-bread Kolo. These images are starter production assets for Unity integration, not final in-engine validation.

Review references saved outside runtime imports:

- [Repaired atlas contact sheet](../../../docs/concept-art/asset-previews/meteora-level-01-repaired-atlases.png)
- [Five-layer parallax safe-crop comparison](../../../docs/concept-art/asset-previews/meteora-level-01-parallax-safe-crops.png)

## Permanent PNG integrity gate

Run both permanent checks from the repository root:

```bash
python3 -m unittest discover -s Tools/Art/tests -v
python3 Tools/Art/validate_meteora_art.py --root . --manifest Assets/Art/Meteora/meteora-level-01-art-manifest.json
```

A PNG signature or valid IHDR header alone is insufficient. The validator checks the complete chunk stream and CRCs, requires consecutive IDAT chunks, inflates the full IDAT payload to the exact expected scanline length, validates scanline filter bytes, and requires a valid terminal IEND chunk. It also verifies the manifest inventory, order, SHA-256 values, dimensions, and RGB/RGBA alpha contracts.

## Coordinate conventions

All source packing and crop bounds below are half-open `(x0,y0)-(x1,y1)`: `x1` and `y1` are excluded. Source-image origin is top-left and source `y` increases downward.

Unity Sprite Editor uses bottom-left origin and `y` increases upward. Every `SpriteRect(x,y,w,h)` below is computed from a source rect in an image of height `H` as:

`SpriteRect(x0, H-y1, x1-x0, y1-y0)`.

Use the exact deterministic names below when creating manual SpriteRects and the corresponding `.meta` import data in Unity. Unity import has not run, so all rectangles and pivots remain unvalidated in the Editor and `unityValidated` remains `false`.

## Parallax composition and tested crop envelope

Compose all five background layers in this back-to-front order:

1. `Backgrounds/Level01/sky-base.png`
2. `Backgrounds/Level01/clouds-far.png`
3. `Backgrounds/Level01/meteora-far.png`
4. `Backgrounds/Level01/meteora-mid.png`
5. `Backgrounds/Level01/cliffs-near.png`
6. Gameplay sprites over the existing greybox collision geometry

The committed LEFT / CENTER / RIGHT preview composites all five layers. Provisional movement factors, relative to camera movement, are `0.00` for sky, `0.05` for clouds, `0.10` for far Meteora, `0.20` for mid Meteora, and `0.35` for near cliffs.

Here “80%” means the horizontal overscan envelope: the visible crop is approximately 80% of source width, leaving approximately 10% horizontal travel on each side. Source width determines a 16:9 crop height, rounded to whole pixels and vertically centered. It does not mean every source uses 80% of its height.

| Source layer | LEFT source crop | CENTER source crop | RIGHT source crop | Exact crop size |
|---|---|---|---|---|
| `sky-base.png` (1774×887) | `(0,44)-(1419,842)` | `(177,44)-(1596,842)` | `(355,44)-(1774,842)` | `1419×798` (~80% width, ~90% height) |
| Each 1672×941 overlay: clouds, far, mid, near | `(0,94)-(1338,847)` | `(167,94)-(1505,847)` | `(334,94)-(1672,847)` | `1338×753` (~80% width and height) |

These crop coordinates use the half-open top-left/y-down source convention. Keep provisional camera movement inside this tested source-pixel envelope. Final world-space camera bounds, common display bounds, seams, crop, route readability, and parallax factors must be tuned in Unity.

## Deterministic SpriteRects

### Rock surfaces — 1254×1254 RGB

Each source quadrant is 627×627. The Unity-visible core is offset `(+12,+12)` inside its source quadrant and is 603×603. The surrounding 12px wrapped extrusion is bleed protection and is excluded from SpriteRects.

| Name | Source core `(x0,y0)-(x1,y1)` | Unity rect |
|---|---|---|
| `rock_natural_cliff` | `(12,12)-(615,615)` | `SpriteRect(12,639,603,603)` |
| `rock_monastery_stone` | `(639,12)-(1242,615)` | `SpriteRect(639,639,603,603)` |
| `rock_cracked_bridge` | `(12,639)-(615,1242)` | `SpriteRect(12,12,603,603)` |
| `rock_walkable_limestone` | `(639,639)-(1242,1242)` | `SpriteRect(639,12,603,603)` |

The conversion is exact: for the top row, `1254-615=639`; for the bottom row, `1254-1242=12`.

### Wood, rope, and bronze — 1254×1254 RGBA

Source cells use x starts `1,314,627,940`, width `313`; source y starts `0,627`, height `627`. Each cell contains a 12px transparent inner gutter.

| Name | Source cell | Unity rect |
|---|---|---|
| `wood_plank_platform` | `(1,0)-(314,627)` | `SpriteRect(1,627,313,627)` |
| `wood_beam_end` | `(314,0)-(627,627)` | `SpriteRect(314,627,313,627)` |
| `rope_straight` | `(627,0)-(940,627)` | `SpriteRect(627,627,313,627)` |
| `rope_coiled_connector` | `(940,0)-(1253,627)` | `SpriteRect(940,627,313,627)` |
| `wood_pulley` | `(1,627)-(314,1254)` | `SpriteRect(1,0,313,627)` |
| `bronze_hook` | `(314,627)-(627,1254)` | `SpriteRect(314,0,313,627)` |
| `bronze_pressure_plate` | `(627,627)-(940,1254)` | `SpriteRect(627,0,313,627)` |
| `bronze_hinge_axle` | `(940,627)-(1253,1254)` | `SpriteRect(940,0,313,627)` |

### Interactables — 1254×1254 RGBA

Interactables use the same x/y cell map and 12px transparent inner gutter as the wood atlas.

| Name | Source cell | Unity rect |
|---|---|---|
| `plate_raised` | `(1,0)-(314,627)` | `SpriteRect(1,627,313,627)` |
| `plate_pressed` | `(314,0)-(627,627)` | `SpriteRect(314,627,313,627)` |
| `stone_pushable` | `(627,0)-(940,627)` | `SpriteRect(627,627,313,627)` |
| `platform_hanging` | `(940,0)-(1253,627)` | `SpriteRect(940,627,313,627)` |
| `platform_cracked` | `(1,627)-(314,1254)` | `SpriteRect(1,0,313,627)` |
| `heavy_water_source` | `(314,627)-(627,1254)` | `SpriteRect(314,0,313,627)` |
| `finish_bell` | `(627,627)-(940,1254)` | `SpriteRect(627,0,313,627)` |
| `sesame_collectible` | `(940,627)-(1253,1254)` | `SpriteRect(940,0,313,627)` |

Cracked debris, sesame sparkles, and other grouped marks remain inside their named cell.

### Water and honey effects — 1254×1254 RGBA

Source x/y starts are `0,418,836`; every cell is 418×418. Source rows y `0,418,836` convert to Unity y `836,418,0`.

| Name | Source cell | Unity rect |
|---|---|---|
| `water_pool_edge` | `(0,0)-(418,418)` | `SpriteRect(0,836,418,418)` |
| `water_splash_group` | `(418,0)-(836,418)` | `SpriteRect(418,836,418,418)` |
| `water_droplet_small` | `(836,0)-(1254,418)` | `SpriteRect(836,836,418,418)` |
| `water_droplet_medium` | `(0,418)-(418,836)` | `SpriteRect(0,418,418,418)` |
| `water_droplet_large` | `(418,418)-(836,836)` | `SpriteRect(418,418,418,418)` |
| `heavy_water_sheen` | `(836,418)-(1254,836)` | `SpriteRect(836,418,418,418)` |
| `honey_coating` | `(0,836)-(418,1254)` | `SpriteRect(0,0,418,418)` |
| `honey_drip` | `(418,836)-(836,1254)` | `SpriteRect(418,0,418,418)` |
| `landing_dust` | `(836,836)-(1254,1254)` | `SpriteRect(836,0,418,418)` |

### Touch controls — 1254×1254 RGBA

The UI uses a 3×2 map: source x starts `0,418,836`, width `418`; source top y `0` converts to Unity y `627`, and source bottom y `627` converts to Unity y `0`; height is `627`.

| Name | Source cell | Unity rect |
|---|---|---|
| `ui_left` | `(0,0)-(418,627)` | `SpriteRect(0,627,418,627)` |
| `ui_right` | `(418,0)-(836,627)` | `SpriteRect(418,627,418,627)` |
| `ui_jump` | `(836,0)-(1254,627)` | `SpriteRect(836,627,418,627)` |
| `ui_roll_flatten` | `(0,627)-(418,1254)` | `SpriteRect(0,0,418,627)` |
| `ui_interact` | `(418,627)-(836,1254)` | `SpriteRect(418,0,418,627)` |
| `ui_pause` | `(836,627)-(1254,1254)` | `SpriteRect(836,0,418,627)` |

### Kolo character sheets — CI alpha evidence

A temporary exact-head CI measurement used Pillow to inspect every pixel with alpha > 0. State order is fixed by the approved generation brief.

Normal order is `kolo_idle`, `kolo_rolling`, `kolo_jump`, `kolo_landing_squash`, `kolo_surprised`. The measured half-open alpha bboxes were:

| Name | Alpha bbox |
|---|---|
| `kolo_idle` | `(24,311)-(334,627)` |
| `kolo_rolling` | `(431,313)-(646,626)` |
| `kolo_jump` | `(729,259)-(1064,580)` |
| `kolo_landing_squash` | `(1064,445)-(1389,631)` |
| `kolo_surprised` | `(1458,311)-(1751,627)` |

The Normal jump occupies alpha through column `1063`, while landing begins at `1064`. There is no transparent separator column, so a non-overlapping five-rect layout with padding cannot be derived without cutting a pose or guessing ownership. Do not auto-slice this sheet and do not commit Normal SpriteRects yet. Inspect it at original resolution in Unity, repair/repack the source into separated cells if necessary, then record five manual rectangles. Normal slicing is explicitly deferred rather than presenting unsafe coordinates.

Heavy order and 12px evidence-derived padded rectangles are unambiguous:

| Name | Alpha bbox | Padded source rect | Unity rect |
|---|---|---|---|
| `kolo_heavy_idle` | `(83,280)-(404,622)` | `(71,268)-(416,634)` | `SpriteRect(71,253,345,366)` |
| `kolo_heavy_rolling` | `(490,302)-(861,625)` | `(478,290)-(873,637)` | `SpriteRect(478,250,395,347)` |
| `kolo_heavy_jump` | `(953,217)-(1262,539)` | `(941,205)-(1274,551)` | `SpriteRect(941,336,333,346)` |
| `kolo_heavy_landing_squash` | `(1334,402)-(1691,629)` | `(1322,390)-(1703,641)` | `SpriteRect(1322,246,381,251)` |

These Heavy rectangles cover all measured alpha, retain 12px padding, and do not overlap. Pivots still require Unity visual verification.

## Alpha and collision authority

`Backgrounds/Level01/sky-base.png` and `Environment/rock-surfaces-atlas.png` are opaque RGB images. The other ten deliverables are transparent RGBA images. Preserve their intended import alpha mode and do not flatten transparent files onto a matte.

The existing greybox colliders remain authoritative. Visual sprites, painted rock edges, atlas SpriteRects, and preview crops must not reshape, resize, or derive gameplay collision.

## Deferred Unity and device checks

Unity import and device performance validation have not been run. Before shipping, verify:

- Texture import mode, alpha handling, manual SpriteRect names, pivots, PPU, and generated `.meta` files.
- Repair/repack and manually slice the ambiguous Normal Kolo sheet before gameplay use.
- Character and object scale against the authoritative greybox colliders.
- Final background crop, common display bounds, camera coverage, seams, route readability, and tuned parallax speeds.
- `meteora-far.png` residual-alpha trimming; faint pixels may expand bounds or increase transparent overdraw.
- Platform compression quality, texture memory, batching, draw calls, and transparent overdraw.
- Touch-control safe-area placement, small-size readability, hit regions, and contrast over gameplay.
- Visual readability on a target iPhone, plus sustained target-iPhone frame rate and memory behavior.

Record Unity-tested import settings after these checks; until then the manifest intentionally keeps `unityValidated` set to `false`.
