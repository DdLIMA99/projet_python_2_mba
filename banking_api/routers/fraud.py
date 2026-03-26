"""Router for fraud detection endpoints (routes 13-15)."""

from typing import List

from fastapi import APIRouter

from banking_api.models.schemas import (
    FraudByType,
    FraudPredictRequest,
    FraudPredictResponse,
    FraudSummary,
)
from banking_api.services import fraud_detection_service

router: APIRouter = APIRouter(
    prefix="/api/fraud",
    tags=["Fraud"],
)


# Route 13
@router.get(
    "/summary",
    response_model=FraudSummary,
    summary="Overview of fraud in the dataset",
)
def get_fraud_summary() -> FraudSummary:
    """Return high-level fraud statistics.

    Returns
    -------
    FraudSummary
        Total frauds, flagged count, precision, and recall.
    """
    return fraud_detection_service.get_fraud_summary()


# Route 14
@router.get(
    "/by-type",
    response_model=List[FraudByType],
    summary="Fraud rate by transaction method",
)
def get_fraud_by_type() -> List[FraudByType]:
    """Return the fraud rate broken down by transaction method.

    Returns
    -------
    List[FraudByType]
        Fraud statistics per transaction method.
    """
    return fraud_detection_service.get_fraud_by_type()


# Route 15
@router.post(
    "/predict",
    response_model=FraudPredictResponse,
    summary="Predict if a transaction is fraudulent",
)
def predict_fraud(
    request: FraudPredictRequest,
) -> FraudPredictResponse:
    """Score a transaction and predict fraud probability.

    Parameters
    ----------
    request : FraudPredictRequest
        Transaction features for scoring.

    Returns
    -------
    FraudPredictResponse
        Fraud label and probability score.
    """
    return fraud_detection_service.predict_fraud(request)
