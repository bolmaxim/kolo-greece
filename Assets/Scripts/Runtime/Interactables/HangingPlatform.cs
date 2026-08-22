using UnityEngine;

namespace Kolo.Interactables
{
    [DisallowMultipleComponent]
    public sealed class HangingPlatform : MonoBehaviour, IActivatable
    {
        [SerializeField] private Transform target;
        [SerializeField, Min(0.01f)] private float moveSpeed = 2f;

        private Vector3 homePosition;
        private Vector3 targetPosition;
        private bool initialized;

        public bool IsActive { get; private set; }
        public bool HasReachedDestination { get; private set; }

        private void Awake()
        {
            Initialize();
        }

        private void FixedUpdate()
        {
            Tick(Time.fixedDeltaTime);
        }

        public void Configure(Vector3 destination, float speed)
        {
            Initialize();
            targetPosition = destination;
            moveSpeed = Mathf.Max(0.01f, speed);
        }

        public void MoveToTarget()
        {
            SetActive(true);
        }

        public void SetActive(bool active)
        {
            Initialize();
            IsActive = active;
            HasReachedDestination = false;
        }

        internal void Tick(float deltaTime)
        {
            Initialize();
            Vector3 destination = IsActive ? targetPosition : homePosition;
            transform.position = Vector3.MoveTowards(
                transform.position,
                destination,
                moveSpeed * deltaTime);
            HasReachedDestination = Vector3.SqrMagnitude(transform.position - destination) < 0.0001f;
        }

        private void Initialize()
        {
            if (initialized)
            {
                return;
            }

            homePosition = transform.position;
            targetPosition = target != null ? target.position : transform.position;
            initialized = true;
        }
    }
}
