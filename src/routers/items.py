from fastapi import APIRouter, Query

from services.data_service import get_items_summary, get_player_items, get_tiers_summary
from core.logger_config import get_logger
logger = get_logger(__name__)

router = APIRouter(prefix="/api")

DEFAULT_RESPONSES = ["Tier Set", "Bis", "Catalyst"]
DEFAULT_DIFFICULTIES = ["Normal", "Heroic", "Mythic"]


@router.get("/items/summary")
def items_summary(
    responses: list[str] = Query(default=DEFAULT_RESPONSES),
    difficulties: list[str] = Query(default=DEFAULT_DIFFICULTIES),
    min_date: str = "2026-03-18",
):
    logger.info(f"Fetching items summary with responses={responses}, difficulties={difficulties}, min_date={min_date}")
    return get_items_summary(responses, difficulties, min_date)


@router.get("/items/player/{player_name}")
def player_items(
    player_name: str,
    responses: list[str] = Query(default=DEFAULT_RESPONSES),
    difficulties: list[str] = Query(default=DEFAULT_DIFFICULTIES),
    min_date: str = "2026-03-18",
):
    logger.info(f"Fetching player items for player_name={player_name} with responses={responses}, difficulties={difficulties}, min_date={min_date}")
    return get_player_items(player_name, responses, difficulties, min_date)


@router.get("/tiers/summary")
def tiers_summary(min_date: str = "2026-03-18"):
    logger.info(f"Fetching tiers summary with min_date={min_date}")
    return get_tiers_summary(min_date)
