using Kolo.Interactables;
using NUnit.Framework;
using UnityEngine;

namespace Kolo.Tests.Interactables
{
    public sealed class MeteoraInteractableTests
    {
        [Test]
        public void PressurePlateUsesWeightThresholdAndDeactivates()
        {
            GameObject plateObject = new("Pressure plate");
            plateObject.AddComponent<BoxCollider2D>();
            PressurePlate plate = plateObject.AddComponent<PressurePlate>();
            plate.Configure(2f);

            plate.EvaluateWeight(1f);
            Assert.That(plate.IsActive, Is.False);

            plate.EvaluateWeight(3f);
            Assert.That(plate.IsActive, Is.True);

            plate.EvaluateWeight(0f);
            Assert.That(plate.IsActive, Is.False);
            Object.DestroyImmediate(plateObject);
        }

        [Test]
        public void BreakablePlatformBreaksOnlyOnceAndDisablesCollision()
        {
            GameObject platformObject = new("Breakable platform");
            BoxCollider2D collider = platformObject.AddComponent<BoxCollider2D>();
            BreakablePlatform platform = platformObject.AddComponent<BreakablePlatform>();

            platform.Break();
            platform.Break();

            Assert.That(platform.IsBroken, Is.True);
            Assert.That(collider.enabled, Is.False);
            Object.DestroyImmediate(platformObject);
        }

        [Test]
        public void HangingPlatformMovesDeterministicallyToTarget()
        {
            GameObject platformObject = new("Hanging platform");
            HangingPlatform platform = platformObject.AddComponent<HangingPlatform>();
            platform.Configure(new Vector3(2f, 0f, 0f), 2f);

            platform.MoveToTarget();
            platform.Tick(0.5f);

            Assert.That(platform.IsActive, Is.True);
            Assert.That(platformObject.transform.position.x, Is.EqualTo(1f).Within(0.001f));

            platform.Tick(0.5f);
            Assert.That(platform.HasReachedDestination, Is.True);
            Assert.That(platformObject.transform.position.x, Is.EqualTo(2f).Within(0.001f));
            Object.DestroyImmediate(platformObject);
        }
    }
}
