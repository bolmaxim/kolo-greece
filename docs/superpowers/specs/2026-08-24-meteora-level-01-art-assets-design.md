# Kolo: Greece — Meteora Level 01 Art Assets Design

**Date:** 2026-08-24  
**Status:** proposed production asset specification  
**Visual authority:** `docs/concept-art/level-screenshots/meteora-levels-01-07.png`, especially panel 1 and the approved Heavy-state direction

## Goal

Replace the first Meteora level's plain-color visual placeholders with a cohesive 2.5D starter art pack that matches the approved concept: realistic Meteora scenery, warm natural light, readable stylized Kolo, and clear mobile puzzle objects.

This pack is intended for the existing SpriteRenderer/2D-physics architecture. It does not convert gameplay to full 3D.

## Art direction

- Realistic geology, monastery silhouettes, vegetation, clouds, haze, wood, rope, stone, bronze, water, and honey.
- Kolo remains more stylized than the environment: golden baked bread ring, visible central hole, sesame crust, large friendly eyes, and a clean silhouette.
- Interactive objects use controlled saturation and edge contrast so they remain legible over realistic scenery.
- No text, logos, watermarks, humans, weapons, frosting, or photorealistic human facial features.
- Lighting direction stays consistent: warm sun from upper left, cool atmospheric fill from the sky.

## Deliverables

### Character

Directory: `Assets/Art/Meteora/Characters/Kolo/`

1. `kolo-normal-sheet.png`
   - transparent background;
   - idle, roll, airborne, landing, and surprised expressions;
   - consistent body size, hole, eyes, crust, and sesame placement.
2. `kolo-heavy-sheet.png`
   - transparent background;
   - idle, roll, airborne, and landing poses;
   - visibly water-filled lower body, heavier squash, but the same identity.

### Parallax background

Directory: `Assets/Art/Meteora/Backgrounds/Level01/`

3. `sky-base.png` — opaque blue-to-warm sky gradient with distant haze.
4. `clouds-far.png` — transparent soft cloud layer with no landscape.
5. `meteora-far.png` — transparent distant rock pillars and tiny monastery silhouettes.
6. `meteora-mid.png` — transparent mid-distance pillars, pine and scrub vegetation.
7. `cliffs-near.png` — transparent foreground cliff edges and vegetation framing the playable lane without covering it.

The layers must overlap beyond the camera edges and avoid embedded Kolo, gameplay objects, HUD, or baked labels.

### Surfaces and mechanisms

Directory: `Assets/Art/Meteora/Environment/`

8. `rock-surfaces-atlas.png`
   - cliff face, cut stone, cracked bridge stone, and flat walkable stone variants;
   - lighting-neutral enough for tinting, with seamless-looking interior regions.
9. `wood-rope-bronze-atlas.png`
   - weathered planks, beam ends, rope sections, pulley, hook, and bronze plate surfaces.
10. `interactables-atlas.png`
    - pressure plate up/down, pushable stone, hanging platform, cracked platform, Heavy water source, monastery bell, and sesame collectible;
    - transparent background and generous separation between objects.
11. `water-honey-effects.png`
    - transparent water pool edge, splash, droplets, honey coating, honey drip, and small impact effects.

### Mobile UI

Directory: `Assets/Art/UI/Controls/`

12. `touch-controls-atlas.png`
    - transparent icons for left, right, jump, roll/flatten, interaction, and pause;
    - simple high-contrast shapes readable at small iPhone sizes;
    - no words or letters.

## Unity import and runtime use

- Character, interactable, effect, and UI files import as Sprite assets with transparency preserved.
- Parallax layers import as single sprites; only `sky-base.png` is opaque.
- Environment atlases are sliced later in Unity using a documented cell map; gameplay colliders remain independent from visible sprites.
- Source images stay in `Assets/Art/` because they are intended for runtime use, unlike concept sheets under `docs/`.
- The existing greybox remains the collision authority. Art may not change puzzle distances, mass thresholds, or completion logic.

## Mobile constraints

- Prefer a small number of atlases to reduce draw calls.
- Avoid tiny high-frequency detail that shimmers when scaled on an iPhone.
- Keep transparent empty space reasonable.
- Unity import profiles will cap texture size and choose platform compression after the first Editor inspection.
- The first pack targets visual validation, not final App Store memory optimization.

## Verification

Before integration:

- every PNG opens successfully and has the intended alpha behavior;
- Kolo identity is consistent across both sheets;
- parallax layers contain no HUD or protagonist;
- object atlases contain every named item with no overlaps;
- UI icons remain recognizable when previewed small;
- filenames and directories match this specification exactly.

After Unity becomes available:

- inspect sprite slicing and pixels-per-unit;
- verify no visible seams during camera movement;
- verify layer ordering, parallax speed, and safe-area UI placement;
- profile memory, draw calls, compression artifacts, and frame rate on the target iPhone;
- replace any generated source that fails gameplay readability or device performance.

## Scope boundary

These generated images are production starter assets and a coherent visual baseline. They are not proof of final in-engine quality until lighting, import settings, slicing, scaling, and performance are inspected in Unity.
