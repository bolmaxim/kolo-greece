# Meteora Vertical Slice — Playtest Checklist

**Build identifier:** pending first Unity run  
**Unity version:** `6000.0.44f1`  
**Scene:** `Assets/Scenes/Bootstrap.unity` → `MeteoraSlice`  
**Status:** not run — Unity Personal is not activated yet

## Purpose

Validate that the first Meteora level is playable from start to finish and that a new player understands the Heavy state without spoken instructions.

## Prerequisites

- A Mac, Windows, or Linux computer with Unity Hub.
- Unity Editor `6000.0.44f1` with iOS Build Support when testing an iPhone export.
- A free activated Unity Personal license.
- Repository opened at the commit being tested.
- Input System package restored successfully.

## Automated checks

- [ ] Run EditMode tests.
- [ ] Run PlayMode tests.
- [ ] Confirm movement tests pass: acceleration, grounded jump buffer, roll collider profile.
- [ ] Confirm Heavy-state tests pass: state application, replacement, reset, and modifiers.
- [ ] Confirm interactable tests pass: pressure threshold, breakable platform, hanging platform.
- [ ] Confirm level-flow tests pass: start, one-time completion, seeds, and optional goals.

Record results:

| Check | Result | Notes |
|---|---|---|
| EditMode | Not run | Unity unavailable |
| PlayMode | Not run | Unity unavailable |

## Clean-launch route

1. Open `Assets/Scenes/Bootstrap.unity`.
2. Enter Play Mode and confirm `MeteoraSlice` loads automatically.
3. Move Kolo left and right; check acceleration and stopping.
4. Jump across the opening route and confirm jumping is blocked while airborne.
5. Hold Roll and confirm Kolo flattens, then restores the standing profile when released.
6. Enter the blue Heavy water source and confirm Kolo visibly changes state and moves/jumps more slowly.
7. Put Heavy Kolo or the pushable stone on the pressure plate.
8. Confirm the hanging platform moves to its target and returns when the plate deactivates.
9. Cross the cracked bridge and verify its break behavior is deterministic.
10. Collect the three sesame seeds.
11. Reach the monastery bell finish trigger.
12. Confirm the result panel appears exactly once and reports the correct seed count.

## Input coverage

- [ ] Keyboard: horizontal movement, jump, roll, interaction.
- [ ] Gamepad: horizontal movement, jump, roll, interaction.
- [ ] Touch UI: left, right, jump, and roll buttons respond and release correctly.
- [ ] iPhone safe area: controls do not overlap the notch, Dynamic Island, or home indicator.

## Player-understanding questions

Ask the tester without explaining the solution:

1. What changed when Kolo entered the water source?
2. Why could Kolo activate the pressure plate afterward?
3. What do you expect the three sesame icons to represent?
4. Did you understand where the level ended?

Pass condition: the tester explains that Heavy Kolo has more weight and independently uses that property to progress.

## Acceptance criteria

- [ ] Clean launch reaches the playable level without errors.
- [ ] The complete route can be finished without restarting the Editor.
- [ ] No required jump depends on a frame-perfect input.
- [ ] Heavy state is understandable without spoken instructions.
- [ ] Pressure plate and hanging platform cannot enter a stuck state.
- [ ] Result UI appears once and does not accept movement input underneath.
- [ ] Average first completion takes 2–4 minutes.
- [ ] Frame rate and touch response are acceptable on the target iPhone.

## Issues and decisions

| ID | Severity | Observation | Reproduction | Decision |
|---|---|---|---|---|
| — | — | No live playtest has been run | — | Await Unity activation |

## Next decision

Do not expand production to the remaining levels until the movement feel, Heavy-state readability, and complete route pass this checklist.
