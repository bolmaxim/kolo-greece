using Kolo.Level;
using NUnit.Framework;
using UnityEngine;

namespace Kolo.Tests.Level
{
    public sealed class LevelFlowTests
    {
        private GameObject gameObject;
        private LevelFlowController flow;

        [SetUp]
        public void SetUp()
        {
            gameObject = new GameObject("Level flow");
            flow = gameObject.AddComponent<LevelFlowController>();
            flow.ConfigureTotalSeeds(3);
        }

        [TearDown]
        public void TearDown()
        {
            Object.DestroyImmediate(gameObject);
        }

        [Test]
        public void BeginLevelResetsCompletion()
        {
            flow.BeginLevel();

            Assert.That(flow.IsRunning, Is.True);
            Assert.That(flow.IsComplete, Is.False);
        }

        [Test]
        public void CompleteLevelFiresOnlyOnce()
        {
            int completionCount = 0;
            flow.LevelCompleted += _ => completionCount++;
            flow.BeginLevel();

            flow.CompleteLevel();
            flow.CompleteLevel();

            Assert.That(completionCount, Is.EqualTo(1));
            Assert.That(flow.IsComplete, Is.True);
        }

        [Test]
        public void ResultContainsCollectedSeedsAndGoals()
        {
            flow.BeginLevel();
            flow.CollectSeed();
            flow.CollectSeed();
            flow.CompleteOptionalGoal();

            flow.CompleteLevel();

            Assert.That(flow.LastResult.Completed, Is.True);
            Assert.That(flow.LastResult.CollectedSeeds, Is.EqualTo(2));
            Assert.That(flow.LastResult.TotalSeeds, Is.EqualTo(3));
            Assert.That(flow.LastResult.OptionalGoalsCompleted, Is.EqualTo(1));
        }

        [Test]
        public void CatalogContainsTwentyTwoLevels()
        {
            Assert.That(LevelCatalog.All.Count, Is.EqualTo(22));
            Assert.That(LevelCatalog.Find("meteora-03").PrimaryMechanic, Is.EqualTo("heavy state"));
            Assert.That(LevelCatalog.Find("santorini-08").Difficulty, Is.EqualTo(5));
        }
    }
}
