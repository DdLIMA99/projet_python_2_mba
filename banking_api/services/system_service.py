"""Service layer for system health and metadata endpoints."""

import time

import pandas as pd

from banking_api import config
from banking_api.services import data_loader
from banking_api.models.schemas import HealthResponse, MetadataResponse


def _format_uptime(seconds: float) -> str:
    """Format a duration in seconds as a human-readable string.

    Parameters
    ----------
    seconds : float
        Duration in seconds.

    Returns
    -------
    str
        Formatted string like '2h 15min' or '45min 30s'.
    """
    total: int = int(seconds)
    hours: int = total // 3600
    minutes: int = (total % 3600) // 60
    secs: int = total % 60

    if hours > 0:
        return f"{hours}h {minutes}min"
    if minutes > 0:
        return f"{minutes}min {secs}s"
    return f"{secs}s"


def get_health() -> HealthResponse:
    """Return the health status of the API.

    Returns
    -------
    HealthResponse
        Status, uptime, and dataset loading state.
    """
    dataset_loaded: bool = True
    status: str = "ok"

    try:
        df: pd.DataFrame = data_loader.get_data()
        dataset_loaded = df is not None and not df.empty
    except RuntimeError:
        dataset_loaded = False
        status = "degraded"

    elapsed: float = time.time() - config.START_TIME
    uptime: str = _format_uptime(elapsed)

    return HealthResponse(
        status=status,
        uptime=uptime,
        dataset_loaded=dataset_loaded,
    )


def get_metadata() -> MetadataResponse:
    """Return version and update metadata for the API.

    Returns
    -------
    MetadataResponse
        Version string, last update timestamp, and record count.
    """
    total_records: int = 0

    try:
        df: pd.DataFrame = data_loader.get_data()
        total_records = len(df)
    except RuntimeError:
        total_records = 0

    return MetadataResponse(
        version=config.APP_VERSION,
        last_update=config.LAST_UPDATE,
        total_records=total_records,
    )
