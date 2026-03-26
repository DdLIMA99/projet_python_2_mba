"""Service layer for fraud detection and analysis."""

from typing import List

import pandas as pd

from banking_api.services import data_loader
from banking_api.models.schemas import (
    FraudByType,
    FraudPredictRequest,
    FraudPredictResponse,
    FraudSummary,
)

# Transaction methods known to carry higher fraud risk
_HIGH_RISK_TYPES: List[str] = ["Online Transaction"]


def get_fraud_summary() -> FraudSummary:
    """Return a high-level overview of fraud in the dataset.

    Returns
    -------
    FraudSummary
        Total frauds, flagged count, precision, and recall.
    """
    df: pd.DataFrame = data_loader.get_data()

    total_frauds: int = int(df["isFraud"].sum())
    # flagged = transactions with non-empty errors field
    flagged: int = int(
        df["errors"].str.strip().ne("").sum()
    )

    true_pos: int = total_frauds
    precision: float = (
        round(true_pos / flagged, 4) if flagged > 0 else 0.0
    )
    recall: float = (
        round(true_pos / total_frauds, 4)
        if total_frauds > 0
        else 0.0
    )

    return FraudSummary(
        total_frauds=total_frauds,
        flagged=flagged,
        precision=precision,
        recall=recall,
    )


def get_fraud_by_type() -> List[FraudByType]:
    """Return the fraud rate broken down by transaction method.

    Returns
    -------
    List[FraudByType]
        One entry per method with fraud count and rate.
    """
    df: pd.DataFrame = data_loader.get_data()
    grouped = df.groupby("use_chip").agg(
        total=("isFraud", "count"),
        frauds=("isFraud", "sum"),
    ).reset_index()

    result: List[FraudByType] = []
    for _, row in grouped.iterrows():
        total: int = int(row["total"])
        frauds: int = int(row["frauds"])
        rate: float = (
            round(frauds / total, 6) if total > 0 else 0.0
        )
        result.append(
            FraudByType(
                type=str(row["use_chip"]),
                total=total,
                frauds=frauds,
                fraud_rate=rate,
            )
        )

    return sorted(result, key=lambda x: x.fraud_rate, reverse=True)


def predict_fraud(
    request: FraudPredictRequest,
) -> FraudPredictResponse:
    """Predict whether a transaction is fraudulent.

    Uses a rule-based heuristic:
    - Online transactions carry higher fraud risk.
    - Large amounts increase risk.
    - Unknown methods carry moderate risk.

    Parameters
    ----------
    request : FraudPredictRequest
        Transaction features to score.

    Returns
    -------
    FraudPredictResponse
        Predicted fraud label and probability score.
    """
    df: pd.DataFrame = data_loader.get_data()
    total: int = len(df)
    fraud_count: int = int(df["isFraud"].sum())
    base_rate: float = fraud_count / total if total > 0 else 0.05

    probability: float = base_rate

    if request.use_chip in _HIGH_RISK_TYPES:
        probability = min(0.95, base_rate * 3)
    elif request.use_chip == "Swipe Transaction":
        probability = min(0.80, base_rate * 2)

    # Large amounts increase risk
    if request.amount > 10000:
        probability = min(0.95, probability * 1.5)
    elif request.amount > 1000:
        probability = min(0.80, probability * 1.2)

    probability = round(probability, 4)
    is_fraud: bool = probability >= 0.5

    return FraudPredictResponse(
        isFraud=is_fraud,
        probability=probability,
    )
