namespace Kolo.Level
{
    public readonly struct LevelResult
    {
        public bool Completed { get; }
        public int CollectedSeeds { get; }
        public int TotalSeeds { get; }
        public int OptionalGoalsCompleted { get; }
        public float CompletionTimeSeconds { get; }

        public LevelResult(
            bool completed,
            int collectedSeeds,
            int totalSeeds,
            int optionalGoalsCompleted,
            float completionTimeSeconds)
        {
            Completed = completed;
            CollectedSeeds = collectedSeeds;
            TotalSeeds = totalSeeds;
            OptionalGoalsCompleted = optionalGoalsCompleted;
            CompletionTimeSeconds = completionTimeSeconds;
        }
    }
}
