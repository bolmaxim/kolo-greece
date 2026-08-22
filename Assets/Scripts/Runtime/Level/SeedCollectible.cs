using UnityEngine;

namespace Kolo.Level
{
    [DisallowMultipleComponent]
    [RequireComponent(typeof(Collider2D))]
    public sealed class SeedCollectible : MonoBehaviour
    {
        [SerializeField] private LevelFlowController flow;
        public bool IsCollected { get; private set; }

        public void Configure(LevelFlowController controller)
        {
            flow = controller;
        }

        private void OnTriggerEnter2D(Collider2D other)
        {
            if (IsCollected || other.GetComponent<Kolo.Player.KoloController>() == null)
            {
                return;
            }

            IsCollected = true;
            flow?.CollectSeed();
            gameObject.SetActive(false);
        }
    }
}
