using System;
using UnityEngine;

namespace Kolo.Player
{
    [DisallowMultipleComponent]
    [RequireComponent(typeof(Rigidbody2D), typeof(KoloController))]
    public sealed class KoloStateController : MonoBehaviour
    {
        private Rigidbody2D body;
        private KoloController movement;
        private float normalMass;

        public KoloState CurrentState { get; private set; } = KoloState.Normal;
        public KoloStateModifiers CurrentModifiers { get; private set; } = KoloStateModifiers.Normal;

        public event Action<KoloState> StateChanged;

        private void Awake()
        {
            CacheComponents();
            normalMass = body.mass;
            Apply(KoloState.Normal, notify: false);
        }

        public void SetState(KoloState state)
        {
            Apply(state, notify: state != CurrentState);
        }

        public void ResetState()
        {
            SetState(KoloState.Normal);
        }

        private void Apply(KoloState state, bool notify)
        {
            CacheComponents();
            CurrentState = state;
            CurrentModifiers = ResolveModifiers(state);
            body.mass = normalMass * CurrentModifiers.MassMultiplier;
            movement.SetStateModifiers(CurrentModifiers);

            if (notify)
            {
                StateChanged?.Invoke(state);
            }
        }

        private static KoloStateModifiers ResolveModifiers(KoloState state)
        {
            return state switch
            {
                KoloState.Heavy => KoloStateModifiers.Heavy,
                KoloState.Normal => KoloStateModifiers.Normal,
                KoloState.Sticky => KoloStateModifiers.Normal,
                KoloState.Solid => KoloStateModifiers.Normal,
                _ => KoloStateModifiers.Normal
            };
        }

        private void CacheComponents()
        {
            if (body == null)
            {
                body = GetComponent<Rigidbody2D>();
            }

            if (movement == null)
            {
                movement = GetComponent<KoloController>();
            }

            if (normalMass <= 0f && body != null)
            {
                normalMass = body.mass;
            }
        }
    }
}
