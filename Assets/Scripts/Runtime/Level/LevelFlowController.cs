using System;
using UnityEngine;

namespace Kolo.Level
{
    [DisallowMultipleComponent]
    public sealed class LevelFlowController : MonoBehaviour
    {
        [SerializeField, Min(0)] private int totalSeeds = 3;

        private float startedAt;
        private int collectedSeeds;
        private int optionalGoalsCompleted;

        public bool IsRunning { get; private set; }
        public bool IsComplete { get; private set; }
        public LevelResult LastResult { get; private set; }

        public event Action LevelStarted;
        public event Action<LevelResult> LevelCompleted;

        public void BeginLevel()
        {
            startedAt = Time.realtimeSinceStartup;
            collectedSeeds = 0;
            optionalGoalsCompleted = 0;
            IsComplete = false;
            IsRunning = true;
            LastResult = default;
            LevelStarted?.Invoke();
        }

        public void CollectSeed()
        {
            if (IsRunning && !IsComplete)
            {
                collectedSeeds = Mathf.Min(totalSeeds, collectedSeeds + 1);
            }
        }

        public void CompleteOptionalGoal()
        {
            if (IsRunning && !IsComplete)
            {
                optionalGoalsCompleted++;
            }
        }

        public void CompleteLevel()
        {
            if (!IsRunning || IsComplete)
            {
                return;
            }

            IsComplete = true;
            IsRunning = false;
            LastResult = new LevelResult(
                true,
                collectedSeeds,
                totalSeeds,
                optionalGoalsCompleted,
                Mathf.Max(0f, Time.realtimeSinceStartup - startedAt));
            LevelCompleted?.Invoke(LastResult);
        }

        public void ConfigureTotalSeeds(int count)
        {
            totalSeeds = Mathf.Max(0, count);
        }
    }
}
