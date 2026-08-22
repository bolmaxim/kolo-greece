# Kolo: Greece — Vertical Slice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a playable Unity vertical slice of one Meteora level with Kolo movement, the heavy state, a pressure plate puzzle, a hanging platform section, and a result screen.

**Architecture:** Use a small Unity project with gameplay code separated into input, player movement, player states, interactables, camera, level flow, and UI. Level-specific values live in serializable data objects or scene components; core behaviours do not contain Meteora-specific branching.

**Tech Stack:** Unity 6.x, C#, Unity Input System, 2D physics, Unity Test Framework, URP-compatible 2.5D presentation.

**Spec:** `docs/superpowers/specs/2026-08-23-kolo-greece-mvp-design.md`

## Global Constraints

- Primary gameplay camera is side-on; the player moves in a constrained 2.5D lane.
- Approved visual target: the second Heavy-state concept. Meteora backgrounds use realistic geology, monasteries, dramatic cool-to-warm natural lighting, cloud layers, and atmospheric perspective; Kolo and interactables remain more stylized and contrast-separated for mobile readability.
- The vertical slice uses touch-friendly input abstraction and supports keyboard/gamepad in the editor.
- Kolo has four player actions: horizontal movement, jump, roll/flatten, and contextual interaction.
- The first slice implements the Heavy state only; Sticky and Solid remain documented extensions.
- State changes come from level objects, not a state-selection menu.
- The level must be completable without advertising or monetization SDKs.
- All gameplay rules must be testable without requiring rendered art assets.

---

### Task 1: Create the Unity project scaffold

**Files:**
- Create: `ProjectSettings/ProjectVersion.txt`
- Create: `Packages/manifest.json`
- Create: `Packages/packages-lock.json`
- Create: `Assets/Scenes/Bootstrap.unity`
- Create: `Assets/Scenes/MeteoraSlice.unity`
- Create: `Assets/Scripts/Runtime/` folder structure
- Create: `Assets/Tests/Runtime/` folder structure
- Modify: `README.md` with Unity setup and editor play instructions

**Interfaces:**
- Produces a project that opens in Unity and runs the Bootstrap scene.
- Runtime assemblies must be usable by Unity Test Framework tests.

- [x] Add Unity project metadata and package manifests for Unity 6.x, Input System, Test Framework, and URP.
- [x] Create the minimum scene files with a Bootstrap scene loading the Meteora slice.
- [x] Add assembly definition files separating runtime and tests.
- [x] Add a README section explaining the Unity version, opening the project, and entering Play Mode.
- [x] Verify the repository contains the expected Unity folders and no generated Library/Temp folders.

---

### Task 2: Add input and Kolo movement

**Files:**
- Create: `Assets/Scripts/Runtime/Input/PlayerInputReader.cs`
- Create: `Assets/Scripts/Runtime/Player/KoloController.cs`
- Create: `Assets/Scripts/Runtime/Player/KoloMovementConfig.cs`
- Create: `Assets/Tests/Runtime/Player/KoloMovementTests.cs`

**Interfaces:**
- `PlayerInputReader.MoveAxis`: `float`
- `PlayerInputReader.JumpPressedThisFrame`: `bool`
- `PlayerInputReader.RollHeld`: `bool`
- `PlayerInputReader.InteractPressedThisFrame`: `bool`
- `KoloController.SetInput(float moveAxis, bool jumpPressed, bool rollHeld, bool interactPressed)`
- `KoloController.IsGrounded`: `bool`

- [x] Write tests for acceleration toward the target horizontal speed, jump only while grounded, and roll changing the collider profile.
- [ ] Run the focused tests and confirm the new tests fail before implementation.
- [x] Implement input as an adapter so touch UI, keyboard, and gamepad can feed the same controller.
- [x] Implement Kolo movement with Rigidbody2D, ground detection, jump buffering, and a roll/flatten state.
- [ ] Run the focused tests and confirm they pass.
- [x] Commit with message `feat: add Kolo movement and input abstraction`.

---

### Task 3: Add player state system and heavy-state source

**Files:**
- Create: `Assets/Scripts/Runtime/Player/KoloState.cs`
- Create: `Assets/Scripts/Runtime/Player/KoloStateController.cs`
- Create: `Assets/Scripts/Runtime/Interactables/HeavyStateSource.cs`
- Create: `Assets/Tests/Runtime/Player/KoloStateTests.cs`

**Interfaces:**
- `KoloState`: `Normal`, `Heavy`, `Sticky`, `Solid`
- `KoloStateController.CurrentState`: `KoloState`
- `KoloStateController.SetState(KoloState state)`
- `KoloStateController.ResetState()`
- `HeavyStateSource.ApplyTo(KoloStateController target)`

- [x] Write tests for applying Heavy, replacing a previous state, resetting to Normal, and Heavy’s gameplay modifiers.
- [ ] Run the focused tests and confirm failure before implementation.
- [x] Implement state changes as explicit commands from environment objects.
- [x] Apply Heavy modifiers through configuration rather than hard-coded checks in unrelated interactables.
- [ ] Run the focused tests and confirm they pass.
- [x] Commit with message `feat: add Kolo state system`.

---

### Task 4: Add Meteora puzzle interactables

**Files:**
- Create: `Assets/Scripts/Runtime/Interactables/PressurePlate.cs`
- Create: `Assets/Scripts/Runtime/Interactables/BreakablePlatform.cs`
- Create: `Assets/Scripts/Runtime/Interactables/HangingPlatform.cs`
- Create: `Assets/Scripts/Runtime/Interactables/IActivatable.cs`
- Create: `Assets/Tests/Runtime/Interactables/MeteoraInteractableTests.cs`

**Interfaces:**
- `IActivatable.IsActive`: `bool`
- `IActivatable.SetActive(bool active)`
- `PressurePlate.WeightThreshold`: `float`
- `PressurePlate.IsActive`: `bool`
- `BreakablePlatform.Break()`
- `HangingPlatform.MoveToTarget()`

- [x] Write tests for the pressure plate threshold, activation/deactivation, breakable platform state, and hanging platform target movement.
- [ ] Run the focused tests and confirm failure before implementation.
- [x] Implement the pressure plate using Rigidbody2D mass and collision filtering so only sufficient weight activates it.
- [x] Implement the breakable platform with a deterministic broken state and disabled collision after breaking.
- [x] Implement the hanging platform as a simple deterministic movement state that can be triggered by the plate.
- [ ] Run the focused tests and confirm they pass.
- [x] Commit with message `feat: add Meteora puzzle interactables`.

---

### Task 5: Build the playable Meteora scene

**Files:**
- Modify: `Assets/Scenes/MeteoraSlice.unity`
- Create: `Assets/Prefabs/Player/Kolo.prefab`
- Create: `Assets/Prefabs/Interactables/HeavySource.prefab`
- Create: `Assets/Prefabs/Interactables/PressurePlate.prefab`
- Create: `Assets/Prefabs/Interactables/HangingPlatform.prefab`
- Create: `Assets/Prefabs/Interactables/BreakablePlatform.prefab`
- Create: `Assets/Scripts/Runtime/Level/MeteoraSliceBuilder.cs`

**Interfaces:**
- `MeteoraSliceBuilder.Build()`: creates or validates the test layout.
- Scene entry point: `MeteoraSliceBuilder` or serialized scene references.

- [x] Create a greybox side-on level with start point, Heavy source, pressure plate, breakable section, hanging platform, and finish point.
- [x] Add camera bounds and a camera follow target.
- [x] Keep gameplay collision geometry primitive and readable while the visible background uses realistic PBR rocks, monastery silhouettes, clouds, and atmospheric depth.
- [x] Add a finish trigger that reports successful completion to level flow.
- [ ] Open the scene in Unity and verify the player can traverse the full route in Play Mode.
- [x] Commit with message `feat: build Meteora vertical slice level`.

---

### Task 6: Add camera, level flow, and result UI

**Files:**
- Create: `Assets/Scripts/Runtime/Camera/SideCameraFollow.cs`
- Create: `Assets/Scripts/Runtime/Level/LevelFlowController.cs`
- Create: `Assets/Scripts/Runtime/UI/ResultPanelController.cs`
- Create: `Assets/Scripts/Runtime/UI/TouchInputView.cs`
- Create: `Assets/Tests/Runtime/Level/LevelFlowTests.cs`

**Interfaces:**
- `LevelFlowController.BeginLevel()`
- `LevelFlowController.CompleteLevel()`
- `LevelFlowController.IsComplete`: `bool`
- `ResultPanelController.ShowResult(LevelResult result)`
- `TouchInputView` feeds the same `PlayerInputReader` used by editor input.

- [x] Write tests for level start, one-time completion, and result data.
- [ ] Run the focused tests and confirm failure before implementation.
- [x] Implement side camera follow with clamped horizontal bounds.
- [x] Implement level completion and a result panel showing completion, collected seeds, and optional goals.
- [x] Add touch-friendly controls as a thin view layer; keep gameplay independent from UI.
- [ ] Run focused tests and the complete Unity test suite.
- [x] Commit with message `feat: add level flow and touch-ready UI`.

---

### Task 7: Validate the vertical slice and document playtest

**Files:**
- Create: `docs/playtests/2026-08-23-meteora-slice-playtest.md`
- Modify: `README.md`

**Interfaces:**
- The playtest document records build identifier, test steps, observations, and pass/fail decisions.
- README links to the playtest checklist.

- [ ] Run EditMode and PlayMode tests.
- [ ] Run the project in the Unity Editor and complete the level from a clean launch.
- [ ] Verify the Heavy state is understandable without a spoken explanation.
- [ ] Verify the level can be completed with keyboard/gamepad and the touch input view is wired.
- [ ] Record observed issues and next changes in the playtest document.
- [ ] Commit with message `docs: add vertical slice validation checklist`.
