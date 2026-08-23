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
