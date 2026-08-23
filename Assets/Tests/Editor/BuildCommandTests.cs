using System;
using Kolo.Editor;
using NUnit.Framework;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;

namespace Kolo.Tests.Editor
{
    public sealed class BuildCommandTests
    {
        [Test]
        public void ResolveOutputPathUsesGameCiGeneratedIosPath()
        {
            string path = BuildCommand.ResolveOutputPath(new[]
            {
                "/opt/unity/Editor/Unity",
                "-batchmode",
                "-nographics",
                "-projectPath",
                "/github/workspace",
                "-buildTarget",
                "iOS",
                "-customBuildPath",
                "build/iOS/Kolo",
                "-executeMethod",
                "Kolo.Editor.BuildCommand.ExportIos"
            });

            Assert.That(path, Is.EqualTo("build/iOS/Kolo"));
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

        [Test]
        public void CreateBuildPlayerOptionsRejectsNoConfiguredScenes()
        {
            Assert.Throws<BuildFailedException>(() =>
                BuildCommand.CreateBuildPlayerOptions(
                    Array.Empty<EditorBuildSettingsScene>(),
                    new[] { "Unity", "-customBuildPath", "build/iOS/Kolo" }));
        }

        [Test]
        public void CreateBuildPlayerOptionsUsesIosExportContract()
        {
            EditorBuildSettingsScene[] scenes =
            {
                new("Assets/Scenes/Bootstrap.unity", true),
                new("Assets/Scenes/MeteoraSlice.unity", true)
            };

            BuildPlayerOptions options = BuildCommand.CreateBuildPlayerOptions(
                scenes,
                new[] { "Unity", "-customBuildPath", "build/iOS/Kolo" });

            Assert.That(options.target, Is.EqualTo(BuildTarget.iOS));
            Assert.That(options.locationPathName, Is.EqualTo("build/iOS/Kolo"));
            Assert.That(
                options.scenes,
                Is.EqualTo(new[]
                {
                    "Assets/Scenes/Bootstrap.unity",
                    "Assets/Scenes/MeteoraSlice.unity"
                }));
            Assert.That(options.options, Is.EqualTo(BuildOptions.None));
        }

        [Test]
        public void EnsureBuildSucceededConvertsFailureToBuildFailedException()
        {
            BuildFailedException exception = Assert.Throws<BuildFailedException>(() =>
                BuildCommand.EnsureBuildSucceeded(BuildResult.Failed, 2));

            Assert.That(exception.Message, Does.Contain("Failed"));
            Assert.That(exception.Message, Does.Contain("2 errors"));
        }
    }
}
