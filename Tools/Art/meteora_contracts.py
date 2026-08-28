"""Filename-keyed Meteora art manifest contracts."""

from __future__ import annotations

from pathlib import Path


LEVEL01_REQUIRED_ASSET_PATHS = (
    "Assets/Art/Meteora/Characters/Kolo/kolo-normal-sheet.png",
    "Assets/Art/Meteora/Characters/Kolo/kolo-heavy-sheet.png",
    "Assets/Art/Meteora/Backgrounds/Level01/sky-base.png",
    "Assets/Art/Meteora/Backgrounds/Level01/clouds-far.png",
    "Assets/Art/Meteora/Backgrounds/Level01/meteora-far.png",
    "Assets/Art/Meteora/Backgrounds/Level01/meteora-mid.png",
    "Assets/Art/Meteora/Backgrounds/Level01/cliffs-near.png",
    "Assets/Art/Meteora/Environment/rock-surfaces-atlas.png",
    "Assets/Art/Meteora/Environment/wood-rope-bronze-atlas.png",
    "Assets/Art/Meteora/Environment/interactables-atlas.png",
    "Assets/Art/Meteora/Environment/water-honey-effects.png",
    "Assets/Art/UI/Controls/touch-controls-atlas.png",
)
LEVEL02_REQUIRED_ASSET_PATHS = (
    "Assets/Art/Meteora/Backgrounds/Level02/sky-base.png",
    "Assets/Art/Meteora/Backgrounds/Level02/clouds-depth.png",
    "Assets/Art/Meteora/Backgrounds/Level02/meteora-far.png",
    "Assets/Art/Meteora/Backgrounds/Level02/meteora-mid-gorge.png",
    "Assets/Art/Meteora/Backgrounds/Level02/cliffs-near-station.png",
    "Assets/Art/Meteora/Environment/Level02/cargo-crane-atlas.png",
    "Assets/Art/Meteora/Environment/Level02/cliff-route-atlas.png",
)
LEVEL03_REQUIRED_ASSET_PATHS = (
    "Assets/Art/Meteora/Backgrounds/Level03/sky-wind-base.png",
    "Assets/Art/Meteora/Backgrounds/Level03/cloud-streams.png",
    "Assets/Art/Meteora/Backgrounds/Level03/meteora-wind-far.png",
    "Assets/Art/Meteora/Backgrounds/Level03/meteora-wind-mid.png",
    "Assets/Art/Meteora/Backgrounds/Level03/cliffs-wind-near.png",
    "Assets/Art/Meteora/Environment/Level03/windmill-sail-atlas.png",
    "Assets/Art/Meteora/Environment/Level03/wind-bridge-chase-atlas.png",
)

MANIFEST_CONTRACTS = {
    "meteora-level-01-art-manifest.json": LEVEL01_REQUIRED_ASSET_PATHS,
    "meteora-level-02-art-manifest.json": LEVEL02_REQUIRED_ASSET_PATHS,
    "meteora-level-03-art-manifest.json": LEVEL03_REQUIRED_ASSET_PATHS,
}


def required_paths_for(manifest_path: Path) -> tuple[str, ...]:
    """Return the required asset path contract for a manifest filename."""
    try:
        return MANIFEST_CONTRACTS[manifest_path.name]
    except KeyError as error:
        raise ValueError(f"unknown manifest contract: {manifest_path.name}") from error
