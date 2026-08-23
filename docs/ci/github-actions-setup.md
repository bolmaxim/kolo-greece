# GitHub Actions setup

## What works without Apple Developer

- Unity compilation and EditMode/PlayMode tests.
- Manual export of an unsigned Xcode project.
- Downloading test reports and Xcode artifacts from GitHub Actions.

The exported Xcode project is not directly installable. With a Mac, Xcode, and a free Apple Account, you can locally sign and install it on a personal iPhone for development. Paid Apple Developer Program membership is required for TestFlight or App Store distribution.

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

After joining the paid Apple Developer Program and obtaining access to a Mac, add signing, IPA generation, App Store Connect upload, and TestFlight distribution as a separate protected workflow.
