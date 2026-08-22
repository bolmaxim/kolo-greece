using UnityEngine;

namespace Kolo.CameraSystem
{
    [DisallowMultipleComponent]
    [RequireComponent(typeof(Camera))]
    public sealed class SideCameraFollow : MonoBehaviour
    {
        [SerializeField] private Transform target;
        [SerializeField] private Vector3 offset = new(0f, 1f, -10f);
        [SerializeField, Min(0.01f)] private float smoothTime = 0.2f;
        [SerializeField] private Vector2 horizontalBounds = new(-5f, 50f);
        [SerializeField] private Vector2 verticalBounds = new(-2f, 12f);

        private Vector3 velocity;

        public void Configure(Transform followTarget, Vector2 xBounds, Vector2 yBounds)
        {
            target = followTarget;
            horizontalBounds = xBounds;
            verticalBounds = yBounds;
        }

        private void LateUpdate()
        {
            if (target == null)
            {
                return;
            }

            Vector3 desired = target.position + offset;
            desired.x = Mathf.Clamp(desired.x, horizontalBounds.x, horizontalBounds.y);
            desired.y = Mathf.Clamp(desired.y, verticalBounds.x, verticalBounds.y);
            desired.z = offset.z;
            transform.position = Vector3.SmoothDamp(
                transform.position,
                desired,
                ref velocity,
                smoothTime);
        }
    }
}
