using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;

namespace Kolo.Interactables
{
    [DisallowMultipleComponent]
    [RequireComponent(typeof(Collider2D))]
    public sealed class PressurePlate : MonoBehaviour, IActivatable
    {
        [SerializeField, Min(0.01f)] private float weightThreshold = 2f;
        [SerializeField] private MonoBehaviour[] activationTargets;
        [SerializeField] private UnityEvent onActivated;
        [SerializeField] private UnityEvent onDeactivated;

        private readonly HashSet<Rigidbody2D> bodies = new();

        public float WeightThreshold => weightThreshold;
        public bool IsActive { get; private set; }
        public float CurrentWeight { get; private set; }

        public void Configure(float threshold)
        {
            weightThreshold = Mathf.Max(0.01f, threshold);
            Recalculate();
        }

        public void EvaluateWeight(float weight)
        {
            CurrentWeight = Mathf.Max(0f, weight);
            SetActive(CurrentWeight >= weightThreshold);
        }

        public void SetActive(bool active)
        {
            if (IsActive == active)
            {
                return;
            }

            IsActive = active;

            if (activationTargets != null)
            {
                foreach (MonoBehaviour target in activationTargets)
                {
                    if (target is IActivatable activatable)
                    {
                        activatable.SetActive(active);
                    }
                }
            }

            if (active)
            {
                onActivated?.Invoke();
            }
            else
            {
                onDeactivated?.Invoke();
            }
        }

        private void OnCollisionEnter2D(Collision2D collision)
        {
            if (collision.rigidbody != null)
            {
                bodies.Add(collision.rigidbody);
                Recalculate();
            }
        }

        private void OnCollisionExit2D(Collision2D collision)
        {
            if (collision.rigidbody != null)
            {
                bodies.Remove(collision.rigidbody);
                Recalculate();
            }
        }

        private void OnDisable()
        {
            bodies.Clear();
            EvaluateWeight(0f);
        }

        private void Recalculate()
        {
            float weight = 0f;
            bodies.RemoveWhere(body => body == null);

            foreach (Rigidbody2D body in bodies)
            {
                weight += body.mass;
            }

            EvaluateWeight(weight);
        }
    }
}
