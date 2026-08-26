# Meteora Level 02 art handoff

This pack is production-starter art for **Basket Above the Clouds**. The Level 02 manifest records `unityValidated: false`; all Unity-specific settings and checks listed below remain pending until the assets are imported and exercised on the target device.

The concept and QA images under `docs/concept-art/asset-previews/` are documentation previews only. They are not runtime assets, are not included in either runtime manifest, and are not proof of final in-engine quality.

## Runtime inventory

| Runtime asset | Geometry | Alpha | Role |
|---|---:|---|---|
| `Backgrounds/Level02/sky-base.png` | 1672×941 | opaque | base sky |
| `Backgrounds/Level02/clouds-depth.png` | 1672×941 | transparent | cloud depth |
| `Backgrounds/Level02/meteora-far.png` | 1672×941 | transparent | distant geology |
| `Backgrounds/Level02/meteora-mid-gorge.png` | 1672×941 | transparent | mid gorge and destination monastery |
| `Backgrounds/Level02/cliffs-near-station.png` | 1672×941 | transparent | near route framing |
| `Environment/Level02/cargo-crane-atlas.png` | 1448×1086 | transparent | modular cargo-crane sprites |
| `Environment/Level02/cliff-route-atlas.png` | 1254×1254 | transparent | route and landing sprites |

Level 02 reuses these Level 01 dependencies rather than duplicating them:

| Shared dependency | Runtime source | Use in Level 02 |
|---|---|---|
| Kolo normal/heavy sheets | `Characters/Kolo/kolo-normal-sheet.png`, `Characters/Kolo/kolo-heavy-sheet.png` | player character states |
| pushable stone and bell | `Environment/interactables-atlas.png` | shared interactables |
| touch UI | `Assets/Art/UI/Controls/touch-controls-atlas.png` | shared mobile controls |

The shared paths and their dimensions/hashes remain owned by `meteora-level-01-art-manifest.json`; the Level 02 manifest intentionally contains only the seven Level 02 files above.

## Parallax order and provisional factors

Create the layers back-to-front in this exact order. Factors are provisional implementation starting points, not Unity-validated values.

| Order | Layer | Provisional factor |
|---:|---|---:|
| 1 | `sky-base.png` | `0.00` |
| 2 | `clouds-depth.png` | `0.06` |
| 3 | `meteora-far.png` | `0.11` |
| 4 | `meteora-mid-gorge.png` | `0.22` |
| 5 | `cliffs-near-station.png` | `0.36` |

## Safe-crop QA preview

`meteora-level-02-parallax-safe-crops.png` first composites all five exact runtime layers in the order above, then takes three equal 1280×720 crops. Coordinates are half-open top-left source coordinates, `[x0,x1)×[y0,y1)`, on the common 1672×941 source canvas.

| Panel | Source rectangle | Size |
|---|---|---:|
| LEFT | `[0,1280)×[110,830)` | 1280×720 |
| CENTER | `[196,1476)×[110,830)` | 1280×720 |
| RIGHT | `[392,1672)×[110,830)` | 1280×720 |

The panel labels and separators exist only in the documentation preview. The opaque sky is the base of every panel, so no crop depends on black or uncovered pixels.

## Atlas slicing

All atlas source coordinates below are half-open top-left coordinates. Convert any source rectangle `[x0,x1)×[y0,y1)` from an atlas of height `H` to a Unity bottom-left rectangle with:

```text
SpriteRect(x0, H-y1, x1-x0, y1-y0)
```

Use deterministic manual SpriteRects. Do not allow automatic tight slicing to absorb reserved cells or generator fringe.

### Cargo crane atlas

Geometry is **1448×1086**, arranged as a **4×3** map of 362×362 cells in row-major order (`H = 1086`).

| Cell | Name | Top-left source rectangle | Unity `SpriteRect(x,y,w,h)` |
|---:|---|---|---|
| 1 | crane support frame | `[0,362)×[0,362)` | `(0,724,362,362)` |
| 2 | detached boom | `[362,724)×[0,362)` | `(362,724,362,362)` |
| 3 | winch drum | `[724,1086)×[0,362)` | `(724,724,362,362)` |
| 4 | axle and brake | `[1086,1448)×[0,362)` | `(1086,724,362,362)` |
| 5 | open bronze hook | `[0,362)×[362,724)` | `(0,362,362,362)` |
| 6 | empty basket | `[362,724)×[362,724)` | `(362,362,362,362)` |
| 7 | loaded basket | `[724,1086)×[362,724)` | `(724,362,362,362)` |
| 8 | limestone counterweight | `[1086,1448)×[362,724)` | `(1086,362,362,362)` |
| 9 | passenger platform | `[0,362)×[724,1086)` | `(0,0,362,362)` |
| 10 | repeatable rope segment | `[362,724)×[724,1086)` | `(362,0,362,362)` |
| 11 | rope connector/knot | `[724,1086)×[724,1086)` | `(724,0,362,362)` |
| 12 | reserved | `[1086,1448)×[724,1086)` | do not create |

### Cliff route atlas

Geometry is **1254×1254**, arranged as a **4×2** map in row-major order (`H = 1254`). Because 1254 is not divisible by four, use the exact column boundaries shown below.

| Cell | Name | Top-left source rectangle | Unity `SpriteRect(x,y,w,h)` |
|---:|---|---|---|
| 1 | left/start ledge edge | `[0,313)×[0,627)` | `(0,627,313,627)` |
| 2 | right/destination ledge edge | `[313,627)×[0,627)` | `(313,627,314,627)` |
| 3 | crane footing | `[627,940)×[0,627)` | `(627,627,313,627)` |
| 4 | monastery landing stones | `[940,1254)×[0,627)` | `(940,627,314,627)` |
| 5 | broken railing | `[0,313)×[627,1254)` | `(0,0,313,627)` |
| 6 | bronze-and-rope anchor | `[313,627)×[627,1254)` | `(313,0,314,627)` |
| 7 | three-seed sparkle cluster | `[627,940)×[627,1254)` | `(627,0,313,627)` |
| 8 | reserved | `[940,1254)×[627,1254)` | do not create |

### Alpha and gutter ruling

- Alpha exactly `1/255` is treated as non-rendering generator fringe.
- Every pixel with alpha `>= 2/255` stays within its assigned cell.
- Manual SpriteRects ignore reserved cells and noise-only regions; do not threshold or rewrite the runtime PNGs.
- The broken railing has a **4 px significant-alpha right gutter**. The next object begins **81 px** after the railing's significant-alpha bound (`x=309` to `x=390`). Unity filtering and mip-bleed behavior at this separation is pending verification.

## Validation

Run from the repository root:

```bash
python3 -m unittest discover -s Tools/Art/tests -v
python3 Tools/Art/validate_meteora_art.py --root . --manifest Assets/Art/Meteora/meteora-level-01-art-manifest.json
python3 Tools/Art/validate_meteora_art.py --root . --manifest Assets/Art/Meteora/meteora-level-02-art-manifest.json
python3 Tools/Art/validate_meteora_art.py --root . --manifest Assets/Art/Meteora/meteora-level-01-art-manifest.json --manifest Assets/Art/Meteora/meteora-level-02-art-manifest.json
```

## Pending Unity checks

Before accepting in-engine quality, verify manual slicing; sprite names; pivots; pixels-per-unit; filtering and mip bleed; rope-segment tiling; layer sorting; parallax seams; camera crop bounds; platform and basket attachment points; texture compression; memory footprint; frame rate; safe-area behavior; and target-iPhone readability. Confirm both empty and loaded basket states, the open hook clearance, and Kolo scale in the final scene. None of these checks is claimed complete by this document.
