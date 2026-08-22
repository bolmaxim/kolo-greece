using Kolo.Interactables;
using Kolo.Player;
using NUnit.Framework;
using UnityEngine;

namespace Kolo.Tests.Player
{
    public sealed class KoloStateTests
    {
        private GameObject player;
        private Rigidbody2D body;
        private KoloController movement;
        private KoloStateController states;

        [SetUp]
        public void SetUp()
        {
            player = new GameObject("Kolo state test player");
            body = player.AddComponent<Rigidbody2D>();
            body.mass = 1f;
            player.AddComponent<CapsuleCollider2D>();
            movement = player.AddComponent<KoloController>();
            states = player.AddComponent<KoloStateController>();
        }

        [TearDown]
        public void TearDown()
        {
            Object.DestroyImmediate(player);
        }

        [Test]
        public void HeavySourceAppliesHeavyState()
        {
            GameObject sourceObject = new("Heavy source");
            HeavyStateSource source = sourceObject.AddComponent<HeavyStateSource>();

            source.ApplyTo(states);

            Assert.That(states.CurrentState, Is.EqualTo(KoloState.Heavy));
            Object.DestroyImmediate(sourceObject);
        }

        [Test]
        public void NewStateReplacesPreviousState()
        {
            states.SetState(KoloState.Sticky);
            states.SetState(KoloState.Heavy);

            Assert.That(states.CurrentState, Is.EqualTo(KoloState.Heavy));
        }

        [Test]
        public void ResetReturnsToNormal()
        {
            states.SetState(KoloState.Heavy);
            states.ResetState();

            Assert.That(states.CurrentState, Is.EqualTo(KoloState.Normal));
            Assert.That(body.mass, Is.EqualTo(1f));
        }

        [Test]
        public void HeavyChangesMassAndMovementModifiers()
        {
            states.SetState(KoloState.Heavy);

            Assert.That(body.mass, Is.GreaterThan(1f));
            Assert.That(movement.StateModifiers.SpeedMultiplier, Is.LessThan(1f));
            Assert.That(movement.StateModifiers.JumpMultiplier, Is.LessThan(1f));
        }
    }
}
