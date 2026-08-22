using System;
using UnityEngine;

namespace Kolo.Player
{
    [Serializable]
    public readonly struct KoloStateModifiers
    {
        public static KoloStateModifiers Normal => new(1f, 1f, 1f, 1f);
        public static KoloStateModifiers Heavy => new(3f, 0.72f, 0.68f, 0.78f);

        public float MassMultiplier { get; }
        public float SpeedMultiplier { get; }
        public float AccelerationMultiplier { get; }
        public float JumpMultiplier { get; }

        public KoloStateModifiers(
            float massMultiplier,
            float speedMultiplier,
            float accelerationMultiplier,
            float jumpMultiplier)
        {
            MassMultiplier = Mathf.Max(0.01f, massMultiplier);
            SpeedMultiplier = Mathf.Max(0.01f, speedMultiplier);
            AccelerationMultiplier = Mathf.Max(0.01f, accelerationMultiplier);
            JumpMultiplier = Mathf.Max(0.01f, jumpMultiplier);
        }
    }
}
