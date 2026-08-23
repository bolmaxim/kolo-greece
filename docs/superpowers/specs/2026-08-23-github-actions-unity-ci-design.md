# GitHub Actions Unity CI Design

**Date:** 2026-08-23  
**Status:** approved direction, pending user review  
**Repository:** `bolmaxim/kolo-greece`

## 1. Goal

Add a GitHub Actions pipeline that validates the Unity project without Unity Cloud Build Automation. Phase one must work without Apple Developer membership and prepare a later signed iOS/TestFlight pipeline.

## 2. Constraints

- Private repository using Unity `6000.0.44f1`.
- The owner currently works from an iPhone and cannot run Unity Editor locally.
- Unity Cloud is not required.
- A Unity ID and activated Unity license are still required by the Unity Editor used in CI.
- Apple signing, IPA creation, TestFlight, and App Store submission are outside phase one.
- Credentials and license files must never be committed.

## 3. Architecture

Use GitHub Actions with maintained GameCI actions.

### Validation workflow

Run on pushes to `main`, pull requests targeting `main`, and manual `workflow_dispatch`.

1. Checkout.
2. Restore the Unity Library cache.
3. Activate Unity from GitHub Secrets.
4. Run EditMode tests.
5. Run PlayMode tests.
6. Upload reports and Editor logs even when tests fail.

Routine validation uses a Linux GitHub-hosted runner.

### iOS project workflow

A separate manually triggered job:

1. checks out the selected source revision;
2. restores the Unity cache;
3. activates Unity;
4. exports for the iOS target in batch mode;
5. uploads the unsigned Xcode project as an artifact.

It proves that Unity can export the game for iOS. It does not create an installable IPA or communicate with Apple.

### Future signed build

After Apple Developer enrollment and access to a Mac, a separate protected stage will import signing credentials, build with Xcode, sign the app, and upload it to App Store Connect/TestFlight. Unsigned export and Apple signing remain separate.

## 4. Repository Files

Implementation adds:

- `.github/workflows/unity-tests.yml`;
- `.github/workflows/ios-xcode-export.yml`;
- `Assets/Scripts/Editor/BuildCommand.cs`;
- `docs/ci/github-actions-setup.md`;
- small editor tests or utilities only when required.

Generated builds, `Library`, licenses, certificates, provisioning profiles, and passwords never enter Git.

## 5. GitHub Secrets

The workflows reference but never create or expose:

- `UNITY_LICENSE`;
- `UNITY_EMAIL`;
- `UNITY_PASSWORD`.

Missing secrets must cause a concise actionable setup failure. No Apple secrets exist in phase one.

## 6. Security

- Secrets are available only to jobs requiring Unity activation.
- Pull requests from untrusted forks receive no repository secrets.
- Secrets are never printed, included in artifacts, or written to committed files.
- Artifacts contain test results, Editor logs, or the unsigned Xcode project.
- Future Apple credentials use a separate protected environment.

## 7. Failure Behavior

- Compilation failure stops tests and uploads the available Editor log.
- Test failure marks the workflow failed but still uploads XML reports.
- Missing Unity secrets explains which repository settings require configuration.
- iOS export failure uploads the Editor log when possible.
- Artifact retention remains short to control storage.

## 8. Verification

Before enabling required checks:

1. validate workflow YAML;
2. verify the workflow Unity version matches `ProjectSettings/ProjectVersion.txt`;
3. manually run CI after Unity secrets are configured;
4. confirm EditMode and PlayMode reports upload;
5. confirm the iOS artifact contains an `.xcodeproj`;
6. intentionally omit one secret and verify the error is understandable.

The pipeline is not operational until a real GitHub Actions run passes. YAML files alone are not proof.

## 9. Cost Control

- Linux runners handle routine tests.
- iOS export stays manual until the project stabilizes.
- Cache keys include Unity version, platform, and dependency files.
- Superseded runs on the same branch are cancelled.
- Artifacts use short retention.
- macOS runners remain deferred until Xcode signing is required.

Private repositories consume the GitHub account's Actions allowance; usage is reviewed after initial runs.

## 10. Completion Criteria

Phase one is complete when:

- both workflows exist and pass static review;
- Unity secrets are documented but absent from source;
- a real test run compiles the project and uploads reports;
- a real manual iOS run exports an unsigned Xcode project;
- no Unity Cloud connection or Apple Developer membership is required;
- CI documentation explains failures and artifact downloads.

## 11. Deferred Work

- signed IPA generation;
- TestFlight and App Store Connect automation;
- Apple certificates and provisioning profiles;
- Android signing and Google Play deployment;
- mandatory merge checks.
