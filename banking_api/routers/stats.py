"""Router for statistics endpoints (routes 9-12)."""

from typing import List

from fastapi import APIRouter, Query

from banking_api.models.schemas import (
    AmountDistribution,
    DailyStats,
    StatsOverview,
    TypeStats,
)
from banking_api.services import stats_service

router: APIRouter = APIRouter(
    prefix="/api/stats",
    tags=["Statistics"],
)


# Route 9
@router.get(
    "/overview",
    response_model=StatsOverview,
    summary="Global dataset statistics",
)
def get_overview() -> StatsOverview:
    """Return global statistics for the full dataset.

    Returns
    -------
    StatsOverview
        Total transactions, fraud rate, average amount,
        and most common type.
    """
    return stats_service.get_overview()


# Route 10
@router.get(
    "/amount-distribution",
    response_model=AmountDistribution,
    summary="Histogram of transaction amounts",
)
def get_amount_distribution(
    bins: int = Query(default=8, ge=2, le=50),
) -> AmountDistribution:
    """Return a histogram of transaction amount distribution.

    Parameters
    ----------
    bins : int
        Number of histogram bins (default: 8).

    Returns
    -------
    AmountDistribution
        Bin labels and counts.
    """
    return stats_service.get_amount_distribution(num_bins=bins)


# Route 11
@router.get(
    "/by-type",
    response_model=List[TypeStats],
    summary="Statistics grouped by transaction type",
)
def get_stats_by_type() -> List[TypeStats]:
    """Return count, average, and total amount per type.

    Returns
    -------
    List[TypeStats]
        Aggregated statistics per transaction type.
    """
    return stats_service.get_stats_by_type()


# Route 12
@router.get(
    "/daily",
    response_model=List[DailyStats],
    summary="Transaction volume and average per time step",
)
def get_daily_stats() -> List[DailyStats]:
    """Return transaction volume and average per time step.

    Returns
    -------
    List[DailyStats]
        Statistics grouped by step (time unit).
    """
    return stats_service.get_daily_stats()
