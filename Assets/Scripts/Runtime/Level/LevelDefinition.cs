using System;

namespace Kolo.Level
{
    public enum ChapterId
    {
        Meteora,
        Corfu,
        Santorini
    }

    [Serializable]
    public sealed class LevelDefinition
    {
        public string Id { get; }
        public ChapterId Chapter { get; }
        public string Name { get; }
        public int Difficulty { get; }
        public string PrimaryMechanic { get; }
        public bool HasChase { get; }

        public LevelDefinition(
            string id,
            ChapterId chapter,
            string name,
            int difficulty,
            string primaryMechanic,
            bool hasChase = false)
        {
            Id = id;
            Chapter = chapter;
            Name = name;
            Difficulty = difficulty;
            PrimaryMechanic = primaryMechanic;
            HasChase = hasChase;
        }
    }
}
