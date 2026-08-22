using UnityEngine;

namespace Kolo.Level
{
    [DisallowMultipleComponent]
    [RequireComponent(typeof(Collider2D))]
    public sealed class FinishTrigger : MonoBehaviour
    {
        [SerializeField] private LevelFlowController flow;

        public void Configure(LevelFlowController controller)
        {
            flow = controller;
        }

        private void OnTriggerEnter2D(Collider2D other)
        {
            if (other.GetComponent<Kolo.Player.KoloController>() != null)
            {
                flow?.CompleteLevel();
            }
        }
    }
}
