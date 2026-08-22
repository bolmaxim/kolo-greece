using UnityEngine;
using UnityEngine.Events;

namespace Kolo.Interactables
{
    [DisallowMultipleComponent]
    [RequireComponent(typeof(Collider2D))]
    public sealed class BreakablePlatform : MonoBehaviour, IActivatable
    {
        [SerializeField, Min(0.01f)] private float minimumBreakMass = 2f;
        [SerializeField] private UnityEvent onBroken;

        private Collider2D platformCollider;

        public bool IsBroken { get; private set; }
        public bool IsActive => IsBroken;

        private void Awake()
        {
            platformCollider = GetComponent<Collider2D>();
        }

        public void Break()
        {
            if (IsBroken)
            {
                return;
            }

            IsBroken = true;
            EnsureCollider();
            platformCollider.enabled = false;
            onBroken?.Invoke();
        }

        public void SetActive(bool active)
        {
            if (active)
            {
                Break();
            }
        }

        private void OnCollisionEnter2D(Collision2D collision)
        {
            if (collision.rigidbody != null && collision.rigidbody.mass >= minimumBreakMass)
            {
                Break();
            }
        }

        private void EnsureCollider()
        {
            if (platformCollider == null)
            {
                platformCollider = GetComponent<Collider2D>();
            }
        }
    }
}
