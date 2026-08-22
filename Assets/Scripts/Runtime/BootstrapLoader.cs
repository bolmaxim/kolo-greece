using UnityEngine;
using UnityEngine.SceneManagement;

namespace Kolo.Level
{
    internal static class BootstrapLoader
    {
        private const string BootstrapScene = "Bootstrap";
        private const string GameplayScene = "MeteoraSlice";

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void LoadGameplayScene()
        {
            if (SceneManager.GetActiveScene().name == BootstrapScene)
            {
                SceneManager.LoadScene(GameplayScene, LoadSceneMode.Single);
            }
        }
    }
}
