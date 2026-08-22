using UnityEngine;

namespace Kolo.Player
{
    [DisallowMultipleComponent]
    [RequireComponent(typeof(Rigidbody2D), typeof(CapsuleCollider2D))]
    public sealed class KoloController : MonoBehaviour
    {
        [SerializeField] private KoloMovementConfig movement = new();
        [SerializeField] private LayerMask groundLayers = ~0;

        private readonly RaycastHit2D[] groundHits = new RaycastHit2D[4];

        private Rigidbody2D body;
        private CapsuleCollider2D capsule;
        private Vector2 standingSize;
        private Vector2 standingOffset;
        private float moveAxis;
        private float jumpBufferRemaining;
        private bool rollHeld;
        private bool interactPressed;
        private bool isRolling;

        public bool IsGrounded { get; private set; }
        public bool InteractPressedThisFrame => interactPressed;
        public KoloMovementConfig Movement => movement;

        private void Awake()
        {
            CacheComponents();
            standingSize = capsule.size;
            standingOffset = capsule.offset;
        }

        private void FixedUpdate()
        {
            Simulate(Time.fixedDeltaTime);
        }

        public void Configure(KoloMovementConfig config)
        {
            movement = config ?? throw new System.ArgumentNullException(nameof(config));
        }

        public void SetInput(float horizontalMove, bool jumpPressed, bool shouldRoll, bool shouldInteract)
        {
            moveAxis = Mathf.Clamp(horizontalMove, -1f, 1f);
            rollHeld = shouldRoll;
            interactPressed = shouldInteract;

            if (jumpPressed)
            {
                jumpBufferRemaining = movement.JumpBufferTime;
            }
        }

        internal void Simulate(float deltaTime, bool? groundedOverride = null)
        {
            CacheComponents();
            ApplyRollProfile();

            IsGrounded = groundedOverride ?? DetectGround();
            Vector2 velocity = body.linearVelocity;
            float targetSpeed = moveAxis * movement.MaxSpeed;
            float rate = Mathf.Approximately(moveAxis, 0f)
                ? movement.Deceleration
                : movement.Acceleration;

            velocity.x = Mathf.MoveTowards(velocity.x, targetSpeed, rate * deltaTime);

            if (jumpBufferRemaining > 0f && IsGrounded && !isRolling)
            {
                velocity.y = movement.JumpSpeed;
                jumpBufferRemaining = 0f;
                IsGrounded = false;
            }
            else
            {
                jumpBufferRemaining = Mathf.Max(0f, jumpBufferRemaining - deltaTime);
            }

            body.linearVelocity = velocity;
            interactPressed = false;
        }

        private bool DetectGround()
        {
            if (body.linearVelocity.y > 0.1f)
            {
                return false;
            }

            ContactFilter2D filter = new()
            {
                useLayerMask = true,
                layerMask = groundLayers,
                useTriggers = false
            };

            return capsule.Cast(
                Vector2.down,
                filter,
                groundHits,
                movement.GroundProbeDistance) > 0;
        }

        private void ApplyRollProfile()
        {
            if (rollHeld == isRolling)
            {
                return;
            }

            isRolling = rollHeld;

            if (!isRolling)
            {
                capsule.size = standingSize;
                capsule.offset = standingOffset;
                return;
            }

            Vector2 rollSize = new(
                standingSize.x * movement.RollWidthMultiplier,
                standingSize.y * movement.RollHeightMultiplier);

            capsule.size = rollSize;
            capsule.offset = standingOffset + Vector2.down * ((standingSize.y - rollSize.y) * 0.5f);
        }

        private void CacheComponents()
        {
            if (body == null)
            {
                body = GetComponent<Rigidbody2D>();
            }

            if (capsule == null)
            {
                capsule = GetComponent<CapsuleCollider2D>();
            }
        }
    }
}
