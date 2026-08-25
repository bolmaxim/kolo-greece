# Kolo: Greece — Meteora Level 02 Art Assets Design

**Date:** 2026-08-25  
**Status:** approved design awaiting implementation planning  
**Working title:** Basket Above the Clouds  
**Visual continuity:** Meteora Level 01 starter art pack on `main`

## Goal

Create the production starter art pack for the second Meteora level. The level teaches Kolo to use the hole in his body with a bronze hook, then combines that action with a crane, cargo basket, stone weight, and passenger platform. The image must preserve the approved hybrid style: realistic Meteora scenery and materials with a friendly, clearly readable Kolo and puzzle mechanisms.

## Player experience

The player begins on a narrow sunlit cliff path and can immediately see an unreachable monastery on a separate rock pillar. A large wooden cargo crane spans the central gorge. Clouds move far below the playable lane, establishing height without covering platforms or hazards.

The puzzle sequence is:

1. Reach the old crane.
2. Jump and catch the bronze hook through Kolo's central hole.
3. Use Kolo's weight to rotate the winch and lower the empty cargo basket.
4. Detach and roll a stone weight into the basket.
5. Let the loaded basket raise a small passenger platform.
6. Ride the platform across the gorge and ring the monastery finish bell.

A short optional hook-swing route contains sesame collectibles. Level 02 has no chase sequence; the crane puzzle is its climax.

## Visual composition

- Main view remains side-on 2.5D and compatible with the existing SpriteRenderer and 2D-physics architecture.
- Warm morning sun enters from the upper left, matching Level 01. Cool blue atmospheric fill separates distant rocks.
- The left third contains the starting path, the center contains the crane and open gorge, and the right third contains the arrival ledge and monastery.
- The playable lane, hook, basket, stone, platform, and finish bell use controlled contrast and clean silhouettes for an iPhone-sized display.
- The deepest part of the gorge remains visually calm so moving ropes and the suspended basket are easy to track.
- No text, labels, HUD, protagonist, or gameplay objects are baked into background layers.

## Reuse from Level 01

Reuse without visual regeneration:

- Kolo normal and heavy sprite sheets;
- touch-control atlas;
- pushable stone and finish bell sprites;
- water and landing effects;
- reusable limestone, cut-stone, wood, rope, and bronze surface regions.

Reused source files keep their existing paths and are referenced by Level 02 rather than copied.

## New runtime assets

### Parallax background

Directory: `Assets/Art/Meteora/Backgrounds/Level02/`

1. `sky-base.png` — opaque morning sky with a warm left horizon and cooler upper-right blue.
2. `clouds-depth.png` — transparent cloud banks concentrated below the playable lane, with open space around ropes.
3. `meteora-far.png` — transparent distant pillars and tiny monastery silhouettes with strong atmospheric perspective.
4. `meteora-mid-gorge.png` — transparent mid-distance gorge walls, scrub, pine, and a separate monastery pillar on the right.
5. `cliffs-near-station.png` — transparent near cliff edges framing the start and destination without obscuring the crane.

All five layers must support left, center, and right 16:9 camera crops with horizontal overscan. Their provisional movement factors are `0.00`, `0.06`, `0.11`, `0.22`, and `0.36` respectively; final values remain subject to Unity inspection.

### Crane mechanism atlas

Directory: `Assets/Art/Meteora/Environment/Level02/`

6. `cargo-crane-atlas.png` — transparent, generously separated components:
   - tall wooden crane frame;
   - horizontal boom;
   - winch drum;
   - bronze axle and brake;
   - large bronze hook sized for Kolo's hole;
   - cargo basket, empty;
   - cargo basket, stone-loaded;
   - stone counterweight;
   - small passenger platform;
   - rope end and rope connector pieces.

7. `cliff-route-atlas.png` — transparent route dressing and silhouettes:
   - start ledge edge;
   - destination ledge edge;
   - timber crane footing;
   - monastery landing stones;
   - short broken railing;
   - hook-route anchor;
   - optional sesame cluster effect.

Ropes that change length are assembled in Unity from repeatable rope segments. They are not painted as fixed-length ropes into the background or crane frame.

### Preview sheets

Directory: `docs/concept-art/asset-previews/`

8. `meteora-level-02-gameplay-concept.png` — 16:9 representative gameplay composition showing the crane puzzle and final lighting target.
9. `meteora-level-02-parallax-safe-crops.png` — labeled left, center, and right composites using all five background layers.
10. `meteora-level-02-atlases.png` — readable contact sheet of the two new atlases.

## Technical contracts

- Background `sky-base.png` is RGB and opaque; the other four parallax layers are RGBA and contain genuine transparency.
- Both atlases are RGBA with genuine transparent separation between components.
- Runtime PNGs use valid PNG chunk order, CRCs, complete IDAT streams, and bounded dimensions suitable for the existing validator.
- A Level 02 manifest records path, dimensions, color type, alpha expectation, SHA-256, role, and deterministic inventory order.
- The Level 01 integrity validator and tests are extended only where necessary to support a second manifest; Level 01 remains validated.
- Gameplay colliders, rope joints, mass thresholds, winch motion, and interaction logic remain Unity objects. Art never becomes collision authority.

## Mobile readability and performance

- Important moving objects must remain recognizable at the smallest intended iPhone viewport.
- Avoid high-frequency detail on ropes, basket slats, and distant vegetation that would shimmer under scaling.
- Keep cloud edges soft but keep the hook, basket, and platform edges sharp enough for play.
- Prefer shared Level 01 materials and two new atlases over many individual textures.
- Texture compression, maximum sizes, pivots, slicing, safe-area UI, seams, memory, and frame rate remain unvalidated until the project is opened in Unity on a Mac and tested on an iPhone.

## Verification

Before repository integration:

- all new PNGs open fully with no black or truncated lower regions;
- automated integrity checks pass for both Level 01 and Level 02 manifests;
- transparent files contain at least one genuinely transparent pixel;
- the three 16:9 composites show no uncovered edges or baked gameplay elements;
- crane components do not overlap in their atlas cells;
- the hook opening is visually large enough to read as compatible with Kolo's hole;
- lighting direction and material language match Level 01.

After Unity becomes available:

- verify slicing, pivots, pixels-per-unit, rope tiling, and sorting layers;
- verify the full route and mechanism at Play Mode scale;
- tune parallax bounds and confirm the crane remains readable throughout camera travel;
- profile compression artifacts, memory, draw calls, and frame rate on the target iPhone.

## Scope boundary

This task creates the visual starter pack, manifest, previews, documentation, and automated PNG verification for Meteora Level 02. It does not implement crane gameplay logic, rebuild the Unity scene, validate the assets inside Unity, or produce an iOS binary.
