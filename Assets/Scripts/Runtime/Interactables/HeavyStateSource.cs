using Kolo.Player;
using UnityEngine;

namespace Kolo.Interactables
{
    [DisallowMultipleComponent]
    public sealed class HeavyStateSource : MonoBehaviour
    {
        [SerializeField] private bool consumeOnUse;

        public bool IsConsumed { get; private set; }

        public void ApplyTo(KoloStateController target)
        {
            if (target == null || IsConsumed)
            {
                return;
            }

            target.SetState(KoloState.Heavy);

            if (consumeOnUse)
            {
                IsConsumed = true;
                gameObject.SetActive(false);
            }
        }

        private void OnTriggerEnter2D(Collider2D other)
        {
            if (other.TryGetComponent(out KoloStateController target))
            {
                ApplyTo(target);
            }
        }
    }
}
