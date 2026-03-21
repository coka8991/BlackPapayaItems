import pandas as pd
from pathlib import Path

from core.logger_config import get_logger
logger = get_logger(__name__)

_CSV_PATH = "https://raw.githubusercontent.com/coka8991/BlackPapayaItems/refs/heads/main/RCLootCouncil_History.csv"
_CRAFTING_PREFIXES = ("Pattern:", "Design: ", "Recipe:", "Plans:")
RAID_PREFIXES = ["Aguja del Vacío-", "Falla Onírica-"]

_cache: pd.DataFrame | None = None


def _load_raw() -> pd.DataFrame:
    global _cache
    if _cache is not None:
        return _cache
    logger.info(f"Loading data from {_CSV_PATH}")
    df = pd.read_csv(_CSV_PATH)
    df["response"] = df["response"].replace({"Tierset": "Tier Set"})
    df["date"] = pd.to_datetime(df["date"])
    df = df[df["votes"] != "nil"]
    df["note"] = df["note"].fillna("")
    for prefix in _CRAFTING_PREFIXES:
        df = df[~df["item"].str.contains(prefix, na=False)]
    _cache = df
    return _cache


def reload() -> None:
    """Force reload the CSV from disk on the next call."""
    global _cache
    _cache = None


def get_cleaned(min_date: str) -> pd.DataFrame:
    df = _load_raw()
    return df[df["date"] >= min_date].copy()


def get_items_summary(
    responses: list[str],
    difficulties: list[str],
    min_date: str = "2026-03-18",
) -> list[dict]:
    df = get_cleaned(min_date)
    logger.info(f"Computing items summary with {len(df)} records after filtering by date")
    logger.info(df.head())
    instances = [f"{RAID_PREFIX}{d}" for d in difficulties for RAID_PREFIX in RAID_PREFIXES]
    filtered = df[df["response"].isin(responses) & df["instance"].isin(instances)]

    if filtered.empty:
        logger.info("No items found for the given filters")
        return []

    pivot = (
        filtered.pivot_table(
            index="player", columns="response", aggfunc="size", fill_value=0
        )
        .reset_index()
    )
    # Ensure all requested response columns exist
    for r in responses:
        if r not in pivot.columns:
            pivot[r] = 0
    pivot["Total"] = pivot[responses].sum(axis=1)
    logger.info(f"Items summary computed with {len(pivot)} players")
    return pivot.sort_values("Total", ascending=False).to_dict(orient="records")


def get_player_items(
    player: str,
    responses: list[str],
    difficulties: list[str],
    min_date: str = "2026-03-18",
) -> list[dict]:
    df = get_cleaned(min_date)
    instances = [f"{RAID_PREFIX}{d}" for d in difficulties for RAID_PREFIX in RAID_PREFIXES]
    filtered = df[
        (df["player"] == player)
        & df["response"].isin(responses)
        & df["instance"].isin(instances)
    ]
    logger.info(f"Player items computed for player={player} with {len(filtered)} items")
    cols = ["item", "response", "date", "votes", "instance", "note"]
    result = filtered[cols].copy()
    result["date"] = result["date"].dt.strftime("%Y-%m-%d")
    return result.to_dict(orient="records")


def get_tiers_summary(min_date: str = "2026-03-18") -> list[dict]:
    df = get_cleaned(min_date)
    tiers = df[(df["response"] == "Tier Set")]
    counts = (
        tiers.groupby("player")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    logger.info(f"Tiers summary computed with {len(counts)} players")
    return counts.to_dict(orient="records")
