# Meteora Level 01 starter art pack

This directory contains the repaired starter runtime art pack for the first Meteora level. The approved Meteora contact sheet remains the visual authority: realistic limestone and monastery scenery, warm upper-left sunlight with cool sky fill, and a highly readable golden sesame-bread Kolo. These images are starter production assets for Unity integration, not final in-engine validation.

Review references saved outside runtime imports:

- [Repaired atlas contact sheet](../../../docs/concept-art/asset-previews/meteora-level-01-repaired-atlases.png)
- [Parallax safe-crop comparison](../../../docs/concept-art/asset-previews/meteora-level-01-parallax-safe-crops.png)

## Permanent PNG integrity gate

Run both permanent checks from the repository root:

```bash
python3 -m unittest discover -s Tools/Art/tests -v
python3 Tools/Art/validate_meteora_art.py --root . --manifest Assets/Art/Meteora/meteora-level-01-art-manifest.json
```

A PNG signature or valid IHDR header alone is insufficient. The validator checks the complete chunk stream and CRCs, requires consecutive IDAT chunks, inflates the full IDAT payload to the exact expected scanline length, validates scanline filter bytes, and requires a valid terminal IEND chunk. It also verifies the manifest inventory, order, SHA-256 values, dimensions, and RGB/RGBA alpha contracts.

## Parallax composition and tested crop envelope

Compose the background in this back-to-front order:

1. `Backgrounds/Level01/sky-base.png`
2. `Backgrounds/Level01/clouds-far.png`
3. `Backgrounds/Level01/meteora-far.png`
4. `Backgrounds/Level01/meteora-mid.png`
5. `Backgrounds/Level01/cliffs-near.png`
6. Gameplay sprites over the existing greybox collision geometry

Provisional movement factors, relative to camera movement, are `0.00` for sky, `0.05` for clouds, `0.10` for far Meteora, `0.20` for mid Meteora, and `0.35` for near cliffs.

The reviewed 80% source-pixel crop envelope is:

| Source layer | Center crop | Left crop | Right crop |
|---|---|---|---|
| `sky-base.png` (1774×887) | `(177,44)–(1596,842)` | `x=0–1419, y=44–842` | `x=355–1774, y=44–842` |
| Other parallax layers (1672×941) | `(167,94)–(1505,847)` | `x=0–1338, y=94–847` | `x=334–1672, y=94–847` |

Keep provisional camera movement inside this tested source-pixel envelope. Final world-space camera bounds, common display bounds, seams, crop, route readability, and parallax factors must be tuned in Unity.

## Deterministic sprite slicing maps

Manual SpriteRects and their `.meta` import data will be created in Unity. Until the Unity Editor is available and those imports are tested, slicing remains unvalidated and `unityValidated` must remain `false`.

### Characters and controls

- `Characters/Kolo/kolo-normal-sheet.png`: 5 separated character states; choose pivots per action.
- `Characters/Kolo/kolo-heavy-sheet.png`: 4 separated Heavy states; choose pivots per action.
- `../UI/Controls/touch-controls-atlas.png`: 3×2 order: left, right, jump; roll/flatten, interact/tap, pause.

### Rock surfaces

`Environment/rock-surfaces-atlas.png` uses four 627×627 quadrants:

| Row | Left | Right |
|---|---|---|
| Top | natural cliff face | hand-cut monastery stone |
| Bottom | cracked bridge stone | flat walkable limestone |

Inside every quadrant, the Unity-visible/core SpriteRect starts at local `(+12,+12)` and is exactly `603×603`. The surrounding 12px wrapped extrusion is texture bleed protection and must be excluded from each SpriteRect.

### Wood, rope, bronze, and interactables

Both `Environment/wood-rope-bronze-atlas.png` and `Environment/interactables-atlas.png` use:

- x starts `1, 314, 627, 940`, width `313`;
- y starts `0, 627`, height `627`;
- a 12px transparent inner gutter inside every cell boundary.

Wood/rope/bronze order:

| Row | Cell 1 | Cell 2 | Cell 3 | Cell 4 |
|---|---|---|---|---|
| Top | plank platform | beam end | straight rope | coiled rope/connector |
| Bottom | pulley | hook | pressure plate | hinge/axle |

Interactables order:

| Row | Cell 1 | Cell 2 | Cell 3 | Cell 4 |
|---|---|---|---|---|
| Top | raised plate | pressed plate | pushable stone | hanging platform |
| Bottom | cracked platform with grouped debris | Heavy water source | finish bell | sesame with grouped sparkles |

### Water and honey effects

`Environment/water-honey-effects.png` uses a 3×3 map with x/y starts `0, 418, 836` and exact cell size `418×418`:

| Row | Cell 1 | Cell 2 | Cell 3 |
|---|---|---|---|
| Top | pool edge | splash with grouped droplets | small droplet |
| Middle | medium droplet | large droplet | subtle water-ring Heavy sheen |
| Bottom | honey coating | honey drip | grouped landing dust |

## Alpha and collision authority

`Backgrounds/Level01/sky-base.png` and `Environment/rock-surfaces-atlas.png` are opaque RGB images. The other ten deliverables are transparent RGBA images. Preserve their intended import alpha mode and do not flatten transparent files onto a matte.

The existing greybox colliders remain authoritative. Visual sprites, painted rock edges, atlas SpriteRects, and preview crops must not reshape, resize, or derive gameplay collision.

## Deferred Unity and device checks

Unity import and device performance validation have not been run. Before shipping, verify:

- Texture import mode, alpha handling, manual SpriteRect names, pivots, PPU, and generated `.meta` files.
- Character and object scale against the authoritative greybox colliders.
- Final background crop, common display bounds, camera coverage, seams, route readability, and tuned parallax speeds.
- `meteora-far.png` residual-alpha trimming; faint pixels may expand bounds or increase transparent overdraw.
- Platform compression quality, texture memory, batching, draw calls, and transparent overdraw.
- Touch-control safe-area placement, small-size readability, hit regions, and contrast over gameplay.
- Visual readability on a target iPhone, plus sustained target-iPhone frame rate and memory behavior.

Record Unity-tested import settings after these checks; until then the manifest intentionally keeps `unityValidated` set to `false`.
