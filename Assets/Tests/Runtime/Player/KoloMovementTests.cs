using Kolo.Player;
using NUnit.Framework;
using UnityEngine;

namespace Kolo.Tests.Player
{
    public sealed class KoloMovementTests
    {
        private GameObject player;
        private Rigidbody2D body;
        private CapsuleCollider2D capsule;
        private KoloController controller;

        [SetUp]
        public void SetUp()
        {
            player = new GameObject("Kolo test player");
            body = player.AddComponent<Rigidbody2D>();
            body.gravityScale = 0f;
            capsule = player.AddComponent<CapsuleCollider2D>();
            capsule.size = new Vector2(1f, 1.2f);
            controller = player.AddComponent<KoloController>();
            controller.Configure(new KoloMovementConfig());
        }

        [TearDown]
        public void TearDown()
        {
            Object.DestroyImmediate(player);
        }

        [Test]
        public void AccelerationMovesTowardTargetSpeed()
        {
            controller.SetInput(1f, false, false, false);

            controller.Simulate(0.1f, true);

            Assert.That(body.linearVelocity.x, Is.GreaterThan(0f));
            Assert.That(body.linearVelocity.x, Is.LessThanOrEqualTo(controller.Movement.MaxSpeed));
        }

        [Test]
        public void JumpIsBufferedUntilKoloIsGrounded()
        {
            controller.SetInput(0f, true, false, false);

            controller.Simulate(0.02f, false);
            Assert.That(body.linearVelocity.y, Is.EqualTo(0f));

            controller.Simulate(0.02f, true);
            Assert.That(body.linearVelocity.y, Is.EqualTo(controller.Movement.JumpSpeed));
            Assert.That(controller.IsGrounded, Is.False);
        }

        [Test]
        public void RollChangesAndRestoresColliderProfile()
        {
            Vector2 standingSize = capsule.size;

            controller.SetInput(0f, false, true, false);
            controller.Simulate(0.02f, true);
            Assert.That(capsule.size.y, Is.LessThan(standingSize.y));
            Assert.That(capsule.size.x, Is.GreaterThan(standingSize.x));

            controller.SetInput(0f, false, false, false);
            controller.Simulate(0.02f, true);
            Assert.That(capsule.size, Is.EqualTo(standingSize));
        }
    }
}
