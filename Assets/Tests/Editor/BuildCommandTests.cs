using Kolo.Editor;
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
