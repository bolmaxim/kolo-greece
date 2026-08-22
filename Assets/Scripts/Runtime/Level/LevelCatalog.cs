using System.Collections.Generic;

namespace Kolo.Level
{
    public static class LevelCatalog
    {
        private static readonly LevelDefinition[] Levels =
        {
            new("meteora-01", ChapterId.Meteora, "First Roll", 1, "movement"),
            new("meteora-02", ChapterId.Meteora, "Sesame Trail", 1, "jump"),
            new("meteora-03", ChapterId.Meteora, "Weight of Water", 2, "heavy state"),
            new("meteora-04", ChapterId.Meteora, "Bronze Plate", 2, "pressure plate"),
            new("meteora-05", ChapterId.Meteora, "Rope Above the Valley", 3, "hanging platform"),
            new("meteora-06", ChapterId.Meteora, "Cracked Bridge", 3, "breakable floor"),
            new("meteora-07", ChapterId.Meteora, "Monastery Ascent", 4, "combined heavy puzzle", true),
            new("corfu-01", ChapterId.Corfu, "Old Port", 1, "water movement"),
            new("corfu-02", ChapterId.Corfu, "Olive Grove", 2, "slopes"),
            new("corfu-03", ChapterId.Corfu, "Honey Wall", 2, "sticky state"),
            new("corfu-04", ChapterId.Corfu, "Canal Crossing", 3, "boats"),
            new("corfu-05", ChapterId.Corfu, "Wind in the Sails", 3, "wind and sail"),
            new("corfu-06", ChapterId.Corfu, "Fortress Drain", 4, "water level"),
            new("corfu-07", ChapterId.Corfu, "Storm over Kerkyra", 4, "combined sticky puzzle", true),
            new("santorini-01", ChapterId.Santorini, "White Roofs", 2, "roof routes"),
            new("santorini-02", ChapterId.Santorini, "Blue Dome", 2, "vertical jump"),
            new("santorini-03", ChapterId.Santorini, "Baker's Oven", 3, "solid state"),
            new("santorini-04", ChapterId.Santorini, "Mill Blades", 3, "timed mechanisms"),
            new("santorini-05", ChapterId.Santorini, "Caldera Wind", 4, "air currents"),
            new("santorini-06", ChapterId.Santorini, "Roof Collapse", 4, "solid impacts"),
            new("santorini-07", ChapterId.Santorini, "Sunset Run", 5, "state combination", true),
            new("santorini-08", ChapterId.Santorini, "The Great Mill", 5, "puzzle boss")
        };

        public static IReadOnlyList<LevelDefinition> All => Levels;

        public static IEnumerable<LevelDefinition> ForChapter(ChapterId chapter)
        {
            foreach (LevelDefinition level in Levels)
            {
                if (level.Chapter == chapter)
                {
                    yield return level;
                }
            }
        }

        public static LevelDefinition Find(string id)
        {
            foreach (LevelDefinition level in Levels)
            {
                if (level.Id == id)
                {
                    return level;
                }
            }

            return null;
        }
    }
}
