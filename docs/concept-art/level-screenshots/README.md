# Kolo: Greece — Level Concept Screenshots

These images define the approved visual target for the first 21 levels of the mobile game. They are concept references, not final runtime textures and not screenshots from a working Unity build.

## Chapter sheets

- `meteora-levels-01-07.png` — realistic Meteora cliffs and monasteries; wind, honey, ropes, counterweights, bridge chase, and monastery bell.
- `corfu-levels-08-14.png` — realistic Ionian coast and Venetian architecture; tides, docks, sailboat, waterwheel, storm chase, and fortress beacon.
- `santorini-levels-15-21.png` — realistic whitewashed villages and caldera; rooftops, windmills, updrafts, volcanic mechanisms, sunset chase, and clockwork bull puzzle.

## Unity usage

Use these sheets as references for:

- scene composition and side-view camera framing;
- environment modeling and material direction;
- lighting, fog, clouds, water, and atmospheric perspective;
- placement and readability of puzzle mechanisms;
- Kolo's scale, silhouette, and contrast against the environment;
- mobile HUD placement and safe areas.

Do not ship these sheets inside the application. Recreate each level with optimized 3D models, materials, textures, lighting, cameras, and UI prefabs under `Assets/`. Keeping the concept sheets under `docs/` prevents Unity from importing them into the player build.

## Visual rules

- Realistic Greek backgrounds with a polished 2.5D gameplay plane.
- Kolo remains a stylized living sesame bread ring with a consistent appearance.
- Interactive objects must be easier to read than distant scenery.
- Most levels use a side camera; chase levels 6, 13, and 20 temporarily use a camera behind Kolo.
- The final game should preserve the mood and composition while adapting geometry for gameplay, performance, and accessibility.

## Source and status

Generated as approved visual-development material on 2026-08-23. The images may guide production but require separate art, gameplay, and performance validation in Unity.
