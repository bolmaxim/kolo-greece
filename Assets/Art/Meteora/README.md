# Meteora Level 01 starter art pack

This directory contains the starter runtime art pack for the first Meteora level. The approved Meteora contact sheet remains the visual authority: realistic limestone and monastery scenery, warm upper-left sunlight with cool sky fill, and a highly readable golden sesame-bread Kolo. The images are starter production assets for Unity integration, not final in-engine validation.

## Parallax composition

Compose the background in this back-to-front order:

1. `Backgrounds/Level01/sky-base.png`
2. `Backgrounds/Level01/clouds-far.png`
3. `Backgrounds/Level01/meteora-far.png`
4. `Backgrounds/Level01/meteora-mid.png`
5. `Backgrounds/Level01/cliffs-near.png`
6. Gameplay sprites and the existing greybox collision geometry

Provisional movement factors, relative to camera movement, are `0.00` for sky, `0.05` for clouds, `0.10` for far Meteora, `0.20` for mid Meteora, and `0.35` for near cliffs. These values are untested starting points; tune them in Unity while checking seams, crop, route readability, and camera bounds. The source layers have different native aspect ratios, so establish common display bounds deliberately rather than assuming identical crops.

## Sprite slicing intent

- `Characters/Kolo/kolo-normal-sheet.png`: 5 separated character states.
- `Characters/Kolo/kolo-heavy-sheet.png`: 4 separated Heavy states.
- `Environment/rock-surfaces-atlas.png`: 2 × 2 material swatches.
- `Environment/wood-rope-bronze-atlas.png`: 8 separated pieces.
- `Environment/interactables-atlas.png`: 8 separated regions: pressure plate raised, pressure plate pressed, pushable stone, hanging platform, cracked platform, Heavy water source, finish bell, and sesame collectible. Both plate states must remain independently sliceable.
- `Environment/water-honey-effects.png`: 9 separated regions: pool edge, splash, three separately sliceable droplets, Heavy shimmer, honey coating, honey drip, and landing dust.
- `../UI/Controls/touch-controls-atlas.png`: 6 controls in 3 × 2 order: left, right, jump; roll/flatten, interact/tap, pause.

Choose pivots per gameplay use rather than relying on an automatic grid alone. Confirm that transparent padding does not make rendered or collision alignment drift.

## Alpha and collision rules

`Backgrounds/Level01/sky-base.png` and `Environment/rock-surfaces-atlas.png` are opaque RGB images. The other ten deliverables are transparent RGBA images. Preserve their intended import alpha mode and do not flatten transparent files onto a matte.

The existing greybox colliders remain authoritative. Replacing visual sprites must not reshape, resize, or otherwise derive gameplay collision from painted edges.

## Deferred Unity and device checks

Unity import and device performance validation have not been run. Before shipping, verify:

- Texture import mode, alpha handling, sprite slicing, slice names, pivots, and pixels per unit (PPU).
- Character and object scale against the authoritative greybox colliders.
- Background crop, common display bounds, camera coverage, and route readability.
- `meteora-far.png` residual-alpha trimming; very faint residual pixels may expand sprite bounds or add transparent overdraw.
- Platform compression quality, texture memory, batching, draw calls, and transparent overdraw.
- Layer seams, edge coverage, and tuned parallax speeds across the full camera route.
- Touch-control safe-area placement, small-size readability, hit regions, and contrast over gameplay.
- Visual readability of Kolo, mechanisms, collectibles, and the finish bell on a target iPhone.
- Sustained target-iPhone frame rate and memory behavior during representative play.

Record Unity-tested import settings separately once these checks are complete; the manifest intentionally keeps `unityValidated` set to `false`.

