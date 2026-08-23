# GitHub Actions Unity CI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add GitHub Actions workflows that run Unity tests and export an unsigned iOS Xcode project without Unity Cloud or Apple Developer membership.

**Architecture:** GameCI v4 runs Unity 6000.0.44f1 in GitHub-hosted Linux jobs using a Personal license stored in repository secrets. A small Editor-only C# command owns deterministic iOS export behavior, while workflows own triggers, caching, artifacts, concurrency, and secret validation. Apple signing remains a separate deferred macOS stage.

**Tech Stack:** Unity 6000.0.44f1, C#, Unity Test Framework 1.6.0, GitHub Actions, GameCI v4, actions/cache v4, actions/upload-artifact v4.

**Spec:** `docs/superpowers/specs/2026-08-23-github-actions-unity-ci-design.md`

## Global Constraints

- Repository: `bolmaxim/kolo-greece`, private, default branch `main`.
- Unity version is read from `ProjectSettings/ProjectVersion.txt` and must remain `6000.0.44f1`.
- Unity Cloud is not used.
- Phase one exports an unsigned Xcode project; it does not create an IPA or contact Apple.
- `UNITY_LICENSE`, `UNITY_EMAIL`, and `UNITY_PASSWORD` exist only as GitHub Actions secrets.
- Workflows never print secrets or upload them as artifacts.
- Routine tests use Linux; macOS and Apple signing stay deferred.
- A workflow is not considered operational until a real run passes.

---

### Task 1: Add a tested Editor command for iOS export

**Files:**
- Create: `Assets/Scripts/Editor.meta`
- Create: `Assets/Scripts/Editor/Kolo.Editor.asmdef`
- Create: `Assets/Scripts/Editor/Kolo.Editor.asmdef.meta`
- Create: `Assets/Scripts/Editor/AssemblyInfo.cs`
- Create: `Assets/Scripts/Editor/AssemblyInfo.cs.meta`
- Create: `Assets/Scripts/Editor/BuildCommand.cs`
- Create: `Assets/Scripts/Editor/BuildCommand.cs.meta`
- Create: `Assets/Tests/Editor.meta`
- Create: `Assets/Tests/Editor/Kolo.Tests.Editor.asmdef`
- Create: `Assets/Tests/Editor/Kolo.Tests.Editor.asmdef.meta`
- Create: `Assets/Tests/Editor/BuildCommandTests.cs`
- Create: `Assets/Tests/Editor/BuildCommandTests.cs.meta`

**Interfaces:**
- Produces: `Kolo.Editor.BuildCommand.ExportIos(): void`
- Produces: `BuildCommand.ResolveOutputPath(string[] args): string`
- Produces: `BuildCommand.ResolveEnabledScenes(EditorBuildSettingsScene[] scenes): string[]`
- Consumes: enabled scenes from `EditorBuildSettings.scenes`
- Consumes: optional CLI pair `-customBuildPath <path>`
- Throws: `BuildFailedException` when there are no enabled scenes or Unity reports a failed build

- [ ] **Step 1: Create Editor assembly definitions**

Create `Assets/Scripts/Editor/Kolo.Editor.asmdef`:

```json
{
  "name": "Kolo.Editor",
  "rootNamespace": "Kolo.Editor",
  "references": [],
  "includePlatforms": ["Editor"],
  "excludePlatforms": [],
  "allowUnsafeCode": false,
  "overrideReferences": false,
  "precompiledReferences": [],
  "autoReferenced": true,
  "defineConstraints": [],
  "versionDefines": [],
  "noEngineReferences": false
}
```

Create `Assets/Tests/Editor/Kolo.Tests.Editor.asmdef`:

```json
{
  "name": "Kolo.Tests.Editor",
  "rootNamespace": "Kolo.Tests.Editor",
  "references": ["Kolo.Editor"],
  "includePlatforms": ["Editor"],
  "excludePlatforms": [],
  "allowUnsafeCode": false,
  "overrideReferences": false,
  "precompiledReferences": [],
  "autoReferenced": false,
  "defineConstraints": ["UNITY_INCLUDE_TESTS"],
  "versionDefines": [],
  "noEngineReferences": false,
  "optionalUnityReferences": ["TestAssemblies"]
}
```

Add the normal Unity folder and importer `.meta` files with unique 32-character lowercase hexadecimal GUIDs. Add `Assets/Scripts/Editor/AssemblyInfo.cs`:

```csharp
using System.Runtime.CompilerServices;

[assembly: InternalsVisibleTo("Kolo.Tests.Editor")]
```

- [ ] **Step 2: Write failing Editor tests**

Create `Assets/Tests/Editor/BuildCommandTests.cs`:

```csharp
using NUnit.Framework;
using UnityEditor;

namespace Kolo.Tests.Editor
{
    public sealed class BuildCommandTests
    {
        [Test]
        public void ResolveOutputPathUsesCustomBuildPath()
        {
            string path = BuildCommand.ResolveOutputPath(
                new[] { "Unity", "-batchmode", "-customBuildPath", "artifacts/iOS/Kolo" });

            Assert.That(path, Is.EqualTo("artifacts/iOS/Kolo"));
        }

        [Test]
        public void ResolveOutputPathUsesSafeDefault()
        {
            Assert.That(
                BuildCommand.ResolveOutputPath(new[] { "Unity", "-batchmode" }),
                Is.EqualTo("build/iOS/Kolo"));
        }

        [Test]
        public void ResolveEnabledScenesFiltersDisabledScenes()
        {
            EditorBuildSettingsScene[] scenes =
            {
                new("Assets/Scenes/Bootstrap.unity", true),
                new("Assets/Scenes/MeteoraSlice.unity", false)
            };

            Assert.That(
                BuildCommand.ResolveEnabledScenes(scenes),
                Is.EqualTo(new[] { "Assets/Scenes/Bootstrap.unity" }));
        }
    }
}
```

- [ ] **Step 3: Run the focused EditMode test and verify failure**

Run in Unity batch mode:

```bash
Unity -batchmode -nographics -projectPath .   -runTests -testPlatform EditMode   -testFilter Kolo.Tests.Editor.BuildCommandTests   -testResults artifacts/editmode-before.xml -quit
```

Expected: compilation fails because `BuildCommand` does not exist.

- [ ] **Step 4: Implement the minimal export command**

Create `Assets/Scripts/Editor/BuildCommand.cs`:

```csharp
using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Build.Reporting;

namespace Kolo.Editor
{
    public static class BuildCommand
    {
        private const string OutputArgument = "-customBuildPath";
        private const string DefaultOutputPath = "build/iOS/Kolo";

        public static void ExportIos()
        {
            string[] scenes = ResolveEnabledScenes(EditorBuildSettings.scenes);
            if (scenes.Length == 0)
            {
                throw new BuildFailedException("No enabled scenes are configured.");
            }

            string outputPath = ResolveOutputPath(Environment.GetCommandLineArgs());
            Directory.CreateDirectory(outputPath);

            BuildReport report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
            {
                scenes = scenes,
                locationPathName = outputPath,
                target = BuildTarget.iOS,
                options = BuildOptions.None
            });

            if (report.summary.result != BuildResult.Succeeded)
            {
                throw new BuildFailedException(
                    $"iOS export failed: {report.summary.result}, " +
                    $"{report.summary.totalErrors} errors.");
            }
        }

        internal static string ResolveOutputPath(string[] args)
        {
            for (int index = 0; index < args.Length - 1; index++)
            {
                if (args[index] == OutputArgument
                    && !string.IsNullOrWhiteSpace(args[index + 1]))
                {
                    return args[index + 1];
                }
            }

            return DefaultOutputPath;
        }

        internal static string[] ResolveEnabledScenes(EditorBuildSettingsScene[] scenes)
        {
            return scenes
                .Where(scene => scene.enabled && !string.IsNullOrWhiteSpace(scene.path))
                .Select(scene => scene.path)
                .ToArray();
        }
    }
}
```

- [ ] **Step 5: Run focused tests and verify pass**

Run the same batch command from Step 3.

Expected: all three `BuildCommandTests` pass and `artifacts/editmode-before.xml` is created.

- [ ] **Step 6: Commit the Editor command**

```bash
git add Assets/Scripts/Editor.meta Assets/Scripts/Editor   Assets/Tests/Editor.meta Assets/Tests/Editor
git commit -m "feat: add deterministic iOS export command"
```

---

### Task 2: Add the Unity test workflow

**Files:**
- Create: `.github/workflows/unity-tests.yml`

**Interfaces:**
- Consumes secrets: `UNITY_LICENSE`, `UNITY_EMAIL`, `UNITY_PASSWORD`
- Produces check: `Unity tests / test`
- Produces artifact: `unity-test-results`
- Triggered by: push to `main`, pull request to `main`, manual dispatch

- [ ] **Step 1: Create the test workflow**

Create `.github/workflows/unity-tests.yml`:

```yaml
name: Unity tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  checks: write

concurrency:
  group: unity-tests-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  test:
    name: EditMode and PlayMode
    runs-on: ubuntu-latest
    timeout-minutes: 45
    env:
      UNITY_LICENSE: ${{ secrets.UNITY_LICENSE }}
      UNITY_EMAIL: ${{ secrets.UNITY_EMAIL }}
      UNITY_PASSWORD: ${{ secrets.UNITY_PASSWORD }}

    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          lfs: true

      - name: Verify Unity secrets
        shell: bash
        run: |
          missing=0
          for name in UNITY_LICENSE UNITY_EMAIL UNITY_PASSWORD; do
            if [ -z "${!name}" ]; then
              echo "::error::Missing GitHub Actions secret: ${name}"
              missing=1
            fi
          done
          exit "${missing}"

      - name: Cache Unity Library
        uses: actions/cache@v4
        with:
          path: Library
          key: unity-library-6000.0.44f1-tests-${{ hashFiles('Packages/manifest.json', 'Packages/packages-lock.json', 'ProjectSettings/ProjectVersion.txt') }}
          restore-keys: |
            unity-library-6000.0.44f1-tests-
            unity-library-6000.0.44f1-

      - name: Run Unity tests
        id: tests
        uses: game-ci/unity-test-runner@v4
        env:
          UNITY_LICENSE: ${{ env.UNITY_LICENSE }}
          UNITY_EMAIL: ${{ env.UNITY_EMAIL }}
          UNITY_PASSWORD: ${{ env.UNITY_PASSWORD }}
        with:
          projectPath: .
          unityVersion: 6000.0.44f1
          testMode: All
          artifactsPath: artifacts
          coverageEnabled: false
          githubToken: ${{ secrets.GITHUB_TOKEN }}
          checkName: Kolo Unity tests

      - name: Upload test reports and logs
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: unity-test-results
          path: |
            artifacts
            **/Editor.log
          if-no-files-found: warn
          retention-days: 7
```

- [ ] **Step 2: Validate YAML and secret references locally**

Run:

```bash
ruby -e "require 'yaml'; YAML.load_file('.github/workflows/unity-tests.yml'); puts 'valid yaml'"
rg -n "UNITY_(LICENSE|EMAIL|PASSWORD)" .github/workflows/unity-tests.yml
rg -n "(license|password).*:" .github/workflows/unity-tests.yml
```

Expected: YAML prints `valid yaml`; only secret references and variable names appear; no credential values appear.

- [ ] **Step 3: Verify trigger and artifact behavior by inspection**

Confirm:

```bash
rg -n "push:|pull_request:|workflow_dispatch:|if: always|retention-days: 7"   .github/workflows/unity-tests.yml
```

Expected: all five patterns are present.

- [ ] **Step 4: Commit the test workflow**

```bash
git add .github/workflows/unity-tests.yml
git commit -m "ci: add Unity test workflow"
```

---

### Task 3: Add manual unsigned iOS export workflow

**Files:**
- Create: `.github/workflows/ios-xcode-export.yml`

**Interfaces:**
- Consumes secrets: `UNITY_LICENSE`, `UNITY_EMAIL`, `UNITY_PASSWORD`
- Calls: `Kolo.Editor.BuildCommand.ExportIos(): void`
- Produces artifact: `kolo-ios-xcode-project`
- Triggered only by: `workflow_dispatch`

- [ ] **Step 1: Create the manual iOS workflow**

Create `.github/workflows/ios-xcode-export.yml`:

```yaml
name: Export iOS Xcode project

on:
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: ios-xcode-export-${{ github.ref }}
  cancel-in-progress: true

jobs:
  export:
    name: Unsigned Xcode project
    runs-on: ubuntu-latest
    timeout-minutes: 60
    env:
      UNITY_LICENSE: ${{ secrets.UNITY_LICENSE }}
      UNITY_EMAIL: ${{ secrets.UNITY_EMAIL }}
      UNITY_PASSWORD: ${{ secrets.UNITY_PASSWORD }}

    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          lfs: true

      - name: Verify Unity secrets
        shell: bash
        run: |
          missing=0
          for name in UNITY_LICENSE UNITY_EMAIL UNITY_PASSWORD; do
            if [ -z "${!name}" ]; then
              echo "::error::Missing GitHub Actions secret: ${name}"
              missing=1
            fi
          done
          exit "${missing}"

      - name: Cache Unity Library
        uses: actions/cache@v4
        with:
          path: Library
          key: unity-library-6000.0.44f1-ios-${{ hashFiles('Packages/manifest.json', 'Packages/packages-lock.json', 'ProjectSettings/ProjectVersion.txt') }}
          restore-keys: |
            unity-library-6000.0.44f1-ios-
            unity-library-6000.0.44f1-

      - name: Export unsigned Xcode project
        uses: game-ci/unity-builder@v4
        env:
          UNITY_LICENSE: ${{ env.UNITY_LICENSE }}
          UNITY_EMAIL: ${{ env.UNITY_EMAIL }}
          UNITY_PASSWORD: ${{ env.UNITY_PASSWORD }}
        with:
          projectPath: .
          unityVersion: 6000.0.44f1
          targetPlatform: iOS
          buildMethod: Kolo.Editor.BuildCommand.ExportIos
          customParameters: -customBuildPath build/iOS/Kolo
          buildsPath: build
          versioning: Semantic

      - name: Verify Xcode project
        shell: bash
        run: |
          if ! find build/iOS/Kolo -maxdepth 2 -name '*.xcodeproj' -print -quit | grep -q .; then
            echo "::error::Unity completed without producing an .xcodeproj"
            exit 1
          fi

      - name: Upload Xcode project
        uses: actions/upload-artifact@v4
        with:
          name: kolo-ios-xcode-project
          path: build/iOS/Kolo
          if-no-files-found: error
          retention-days: 7
```

- [ ] **Step 2: Validate YAML and manual-only trigger**

Run:

```bash
ruby -e "require 'yaml'; YAML.load_file('.github/workflows/ios-xcode-export.yml'); puts 'valid yaml'"
rg -n "workflow_dispatch:|buildMethod: Kolo.Editor.BuildCommand.ExportIos|targetPlatform: iOS"   .github/workflows/ios-xcode-export.yml
! rg -n "push:|pull_request:" .github/workflows/ios-xcode-export.yml
```

Expected: YAML is valid; dispatch/build method/platform patterns exist; the final command exits zero because automatic triggers are absent.

- [ ] **Step 3: Verify that Apple signing is absent**

Run:

```bash
! rg -ni "APPLE_|MATCH_|PROVISION|CERTIFICATE|APP_STORE|TESTFLIGHT"   .github/workflows/ios-xcode-export.yml
```

Expected: exit zero with no matches.

- [ ] **Step 4: Commit the export workflow**

```bash
git add .github/workflows/ios-xcode-export.yml
git commit -m "ci: add unsigned iOS Xcode export"
```

---

### Task 4: Document setup, failures, and first real runs

**Files:**
- Create: `docs/ci/github-actions-setup.md`
- Modify: `README.md`

**Interfaces:**
- Documents secrets without their values
- Documents workflow names: `Unity tests`, `Export iOS Xcode project`
- Documents artifact names: `unity-test-results`, `kolo-ios-xcode-project`
- Records that Apple Developer and TestFlight are deferred

- [ ] **Step 1: Write setup documentation**

Create `docs/ci/github-actions-setup.md` with these exact sections:

```markdown
# GitHub Actions setup

## What works without Apple Developer

- Unity compilation and EditMode/PlayMode tests.
- Manual export of an unsigned Xcode project.
- Downloading test reports and Xcode artifacts from GitHub Actions.

An unsigned Xcode project cannot be installed on an iPhone.

## Required Unity secrets

Add these under **GitHub → Settings → Secrets and variables → Actions**:

- `UNITY_LICENSE`: the activated Unity Personal license text;
- `UNITY_EMAIL`: the Unity account email;
- `UNITY_PASSWORD`: the Unity account password.

Never paste these values into an issue, commit, chat message, build log, or artifact.

## First validation run

1. Open **Actions → Unity tests**.
2. Select **Run workflow** on `main`.
3. Wait for **EditMode and PlayMode**.
4. Download `unity-test-results` when diagnosis is needed.

A green run proves that the project compiles and its Unity tests pass in CI.

## First iOS export

1. Open **Actions → Export iOS Xcode project**.
2. Select **Run workflow** on `main`.
3. Download `kolo-ios-xcode-project`.

This artifact is an unsigned Xcode project, not an IPA.

## Common failures

- **Missing GitHub Actions secret**: add the named secret and rerun.
- **Unity activation failure**: renew the Unity Personal license and replace `UNITY_LICENSE`.
- **Compilation failure**: download `unity-test-results` and inspect `Editor.log`.
- **No .xcodeproj produced**: inspect the export job log and verify enabled scenes.
- **Minutes exhausted**: wait for allowance renewal or add GitHub Actions billing.

## Deferred Apple stage

After joining Apple Developer and obtaining access to a Mac, add signing, IPA generation, App Store Connect upload, and TestFlight distribution as a separate protected workflow.
```

- [ ] **Step 2: Link CI documentation from README**

Add under the README documentation section:

```markdown
- [GitHub Actions setup](docs/ci/github-actions-setup.md)
- [GitHub Actions Unity CI design](docs/superpowers/specs/2026-08-23-github-actions-unity-ci-design.md)
```

- [ ] **Step 3: Run repository safety checks**

Run:

```bash
rg -n "UNITY_LICENSE|UNITY_EMAIL|UNITY_PASSWORD" .github docs/ci
! rg -n "BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY|-----BEGIN CERTIFICATE-----" .
! git ls-files | rg '(^|/)(Library|Temp|Obj|Build|Builds|Logs)/'
git status --short
```

Expected: only secret names and workflow references are shown; no key/certificate material or generated Unity directories are tracked; status contains only intended Task 4 files.

- [ ] **Step 4: Commit documentation**

```bash
git add docs/ci/github-actions-setup.md README.md
git commit -m "docs: explain GitHub Actions Unity setup"
```

- [ ] **Step 5: Configure secrets and run workflows**

From GitHub on the owner's account:

1. Add `UNITY_LICENSE`, `UNITY_EMAIL`, and `UNITY_PASSWORD` under repository Actions secrets.
2. Manually run `Unity tests`.
3. Confirm `unity-test-results` is available.
4. Manually run `Export iOS Xcode project`.
5. Confirm `kolo-ios-xcode-project` contains an `.xcodeproj`.

Expected: both workflow runs are green. If Unity secrets cannot yet be created, record the workflows as **configured but not operational**; do not mark this step complete.
