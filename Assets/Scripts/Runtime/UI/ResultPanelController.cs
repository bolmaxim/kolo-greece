using Kolo.Level;
using UnityEngine;
using UnityEngine.UI;

namespace Kolo.UI
{
    [DisallowMultipleComponent]
    public sealed class ResultPanelController : MonoBehaviour
    {
        [SerializeField] private GameObject panelRoot;
        [SerializeField] private Text title;
        [SerializeField] private Text seeds;
        [SerializeField] private Text goals;

        public void Configure(GameObject root, Text titleText, Text seedsText, Text goalsText)
        {
            panelRoot = root;
            title = titleText;
            seeds = seedsText;
            goals = goalsText;
        }

        public void ShowResult(LevelResult result)
        {
            if (panelRoot != null)
            {
                panelRoot.SetActive(true);
            }

            if (title != null)
            {
                title.text = result.Completed ? "Level complete" : "Try again";
            }

            if (seeds != null)
            {
                seeds.text = $"{result.CollectedSeeds}/{result.TotalSeeds}";
            }

            if (goals != null)
            {
                goals.text = $"{result.OptionalGoalsCompleted}/3";
            }
        }

        public void Hide()
        {
            if (panelRoot != null)
            {
                panelRoot.SetActive(false);
            }
        }
    }
}
