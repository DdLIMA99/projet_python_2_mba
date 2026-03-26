"""Service layer for statistics and analytics operations."""

from typing import List

import numpy as np
import pandas as pd

from banking_api.services import data_loader
from banking_api.models.schemas import (
    AmountDistribution,
    DailyStats,
    StatsOverview,
    TypeStats,
)


def get_overview() -> StatsOverview:
    """Compute global statistics for the full dataset.

    Returns
    -------
    StatsOverview
        Object containing total count, fraud rate,
        average amount, and most common transaction method.
    """
    df: pd.DataFrame = data_loader.get_data()

    total: int = len(df)
    fraud_rate: float = float(df["isFraud"].mean())
    avg_amount: float = float(df["amount"].mean())
    most_common: str = str(df["use_chip"].mode().iloc[0])

    return StatsOverview(
        total_transactions=total,
        fraud_rate=round(fraud_rate, 6),
        avg_amount=round(avg_amount, 2),
        most_common_type=most_common,
    )


def get_amount_distribution(
    num_bins: int = 8,
) -> AmountDistribution:
    """Build a histogram of transaction amounts.

    Parameters
    ----------
    num_bins : int
        Number of bins for the histogram.

    Returns
    -------
    AmountDistribution
        Object containing bin labels and counts.
    """
    df: pd.DataFrame = data_loader.get_data()
    amounts: pd.Series = df["amount"]

    counts_arr, edges = np.histogram(amounts, bins=num_bins)

    bins: List[str] = []
    for i in range(len(edges) - 1):
        lo: float = round(float(edges[i]), 2)
        hi: float = round(float(edges[i + 1]), 2)
        bins.append(f"{lo}-{hi}")

    counts: List[int] = [int(c) for c in counts_arr]

    return AmountDistribution(bins=bins, counts=counts)


def get_stats_by_type() -> List[TypeStats]:
    """Compute count, average, and total amount by use_chip.

    Returns
    -------
    List[TypeStats]
        One entry per transaction method with aggregated stats.
    """
    df: pd.DataFrame = data_loader.get_data()
    grouped = df.groupby("use_chip")["amount"].agg(
        ["count", "mean", "sum"]
    ).reset_index()

    result: List[TypeStats] = []
    for _, row in grouped.iterrows():
        result.append(
            TypeStats(
                type=str(row["use_chip"]),
                count=int(row["count"]),
                avg_amount=round(float(row["mean"]), 2),
                total_amount=round(float(row["sum"]), 2),
            )
        )

    return sorted(result, key=lambda x: x.count, reverse=True)


def get_daily_stats() -> List[DailyStats]:
    """Compute transaction volume and average per date.

    Returns
    -------
    List[DailyStats]
        One entry per date with count and average amount.
    """
    df: pd.DataFrame = data_loader.get_data()
    grouped = df.groupby("date")["amount"].agg(
        ["count", "mean", "sum"]
    ).reset_index().sort_values("date")

    result: List[DailyStats] = []
    for _, row in grouped.iterrows():
        result.append(
            DailyStats(
                date=str(row["date"]),
                count=int(row["count"]),
                avg_amount=round(float(row["mean"]), 2),
                total_amount=round(float(row["sum"]), 2),
            )
        )

    return result
