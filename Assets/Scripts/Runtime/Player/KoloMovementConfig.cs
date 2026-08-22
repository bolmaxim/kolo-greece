using System;
using UnityEngine;

namespace Kolo.Player
{
    [Serializable]
    public sealed class KoloMovementConfig
    {
        [field: SerializeField, Min(0.1f)]
        public float MaxSpeed { get; private set; } = 7f;

        [field: SerializeField, Min(0.1f)]
        public float Acceleration { get; private set; } = 35f;

        [field: SerializeField, Min(0.1f)]
        public float Deceleration { get; private set; } = 45f;

        [field: SerializeField, Min(0.1f)]
        public float JumpSpeed { get; private set; } = 11f;

        [field: SerializeField, Min(0f)]
        public float JumpBufferTime { get; private set; } = 0.12f;

        [field: SerializeField, Min(0.001f)]
        public float GroundProbeDistance { get; private set; } = 0.08f;

        [field: SerializeField, Range(0.25f, 0.95f)]
        public float RollHeightMultiplier { get; private set; } = 0.55f;

        [field: SerializeField, Range(1f, 1.5f)]
        public float RollWidthMultiplier { get; private set; } = 1.15f;
    }
}
