using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;

namespace Kolo.Editor
{
    public static class BuildCommand
    {
        private const string OutputArgument = "-customBuildPath";
        private const string DefaultOutputPath = "build/iOS/Kolo";

        public static void ExportIos()
        {
            BuildPlayerOptions options = CreateBuildPlayerOptions(
                EditorBuildSettings.scenes,
                Environment.GetCommandLineArgs());

            Directory.CreateDirectory(options.locationPathName);
            BuildReport report = BuildPipeline.BuildPlayer(options);
            EnsureBuildSucceeded(report.summary.result, report.summary.totalErrors);
        }

        internal static BuildPlayerOptions CreateBuildPlayerOptions(
            EditorBuildSettingsScene[] configuredScenes,
            string[] args)
        {
            string[] scenes = ResolveEnabledScenes(configuredScenes);
            if (scenes.Length == 0)
            {
                throw new BuildFailedException("No enabled scenes are configured.");
            }

            return new BuildPlayerOptions
            {
                scenes = scenes,
                locationPathName = ResolveOutputPath(args),
                target = BuildTarget.iOS,
                options = BuildOptions.None
            };
        }

        internal static void EnsureBuildSucceeded(BuildResult result, uint totalErrors)
        {
            if (result != BuildResult.Succeeded)
            {
                throw new BuildFailedException(
                    $"iOS export failed: {result}, {totalErrors} errors.");
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
