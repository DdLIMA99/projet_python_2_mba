"""Pydantic schemas for request and response models."""

from typing import List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Transaction schemas
# ---------------------------------------------------------------------------

class TransactionItem(BaseModel):
    """Single transaction item.

    Attributes
    ----------
    id : str
        Unique transaction identifier.
    date : str
        Date of the transaction.
    client_id : str
        Client identifier (originator).
    card_id : str
        Card identifier used.
    amount : float
        Transaction amount.
    use_chip : str
        Transaction method (Swipe, Chip, Online).
    merchant_id : str
        Merchant identifier.
    merchant_city : str
        Merchant city.
    merchant_state : str
        Merchant state.
    zip : str
        Merchant zip code.
    mcc : str
        Merchant category code.
    errors : str
        Error or fraud indicator (empty = clean).
    isFraud : int
        Derived fraud flag (1 if errors non-empty, 0 otherwise).
    """

    id: str
    date: str
    client_id: str
    card_id: str
    amount: float
    use_chip: str
    merchant_id: str
    merchant_city: str
    merchant_state: str
    zip: str
    mcc: str
    errors: str
    isFraud: int


class TransactionListResponse(BaseModel):
    """Paginated list of transactions.

    Attributes
    ----------
    page : int
        Current page number.
    limit : int
        Number of items per page.
    total : int
        Total number of matching transactions.
    transactions : List[TransactionItem]
        List of transactions for current page.
    """

    page: int
    limit: int
    total: int
    transactions: List[TransactionItem]


class TransactionSearchRequest(BaseModel):
    """Search criteria for transactions.

    Attributes
    ----------
    use_chip : Optional[str]
        Filter by transaction method.
    isFraud : Optional[int]
        Filter by fraud flag.
    amount_range : Optional[List[float]]
        Min and max amount range [min, max].
    client_id : Optional[str]
        Filter by client identifier.
    merchant_id : Optional[str]
        Filter by merchant identifier.
    """

    use_chip: Optional[str] = None
    isFraud: Optional[int] = None
    amount_range: Optional[List[float]] = None
    client_id: Optional[str] = None
    merchant_id: Optional[str] = None


class TransactionTypesResponse(BaseModel):
    """List of unique transaction types.

    Attributes
    ----------
    types : List[str]
        List of unique use_chip values.
    """

    types: List[str]


class DeleteResponse(BaseModel):
    """Response for delete operation.

    Attributes
    ----------
    message : str
        Confirmation message.
    id : str
        Deleted transaction identifier.
    """

    message: str
    id: str


# ---------------------------------------------------------------------------
# Statistics schemas
# ---------------------------------------------------------------------------

class StatsOverview(BaseModel):
    """Global dataset statistics.

    Attributes
    ----------
    total_transactions : int
        Total number of transactions.
    fraud_rate : float
        Overall fraud rate.
    avg_amount : float
        Average transaction amount.
    most_common_type : str
        Most frequent transaction method.
    """

    total_transactions: int
    fraud_rate: float
    avg_amount: float
    most_common_type: str


class AmountDistribution(BaseModel):
    """Histogram of transaction amounts.

    Attributes
    ----------
    bins : List[str]
        Label for each amount bin.
    counts : List[int]
        Number of transactions per bin.
    """

    bins: List[str]
    counts: List[int]


class TypeStats(BaseModel):
    """Statistics per transaction type.

    Attributes
    ----------
    type : str
        Transaction method (use_chip value).
    count : int
        Number of transactions.
    avg_amount : float
        Average transaction amount.
    total_amount : float
        Total transaction amount.
    """

    type: str
    count: int
    avg_amount: float
    total_amount: float


class DailyStats(BaseModel):
    """Daily transaction statistics.

    Attributes
    ----------
    date : str
        Date identifier.
    count : int
        Number of transactions.
    avg_amount : float
        Average transaction amount.
    total_amount : float
        Total transaction amount.
    """

    date: str
    count: int
    avg_amount: float
    total_amount: float


# ---------------------------------------------------------------------------
# Fraud schemas
# ---------------------------------------------------------------------------

class FraudSummary(BaseModel):
    """Fraud overview statistics.

    Attributes
    ----------
    total_frauds : int
        Total number of fraudulent transactions.
    flagged : int
        Number of flagged transactions.
    precision : float
        Precision metric.
    recall : float
        Recall metric.
    """

    total_frauds: int
    flagged: int
    precision: float
    recall: float


class FraudByType(BaseModel):
    """Fraud rate by transaction type.

    Attributes
    ----------
    type : str
        Transaction method.
    total : int
        Total transactions of this type.
    frauds : int
        Number of fraudulent transactions.
    fraud_rate : float
        Fraud rate for this type.
    """

    type: str
    total: int
    frauds: int
    fraud_rate: float


class FraudPredictRequest(BaseModel):
    """Input for fraud prediction.

    Attributes
    ----------
    use_chip : str
        Transaction method.
    amount : float
        Transaction amount.
    merchant_city : str
        Merchant city.
    merchant_state : str
        Merchant state.
    """

    use_chip: str
    amount: float = Field(..., gt=0)
    merchant_city: str = ""
    merchant_state: str = ""


class FraudPredictResponse(BaseModel):
    """Fraud prediction result.

    Attributes
    ----------
    isFraud : bool
        Whether the transaction is predicted as fraud.
    probability : float
        Probability score of fraud.
    """

    isFraud: bool
    probability: float


# ---------------------------------------------------------------------------
# Customer schemas
# ---------------------------------------------------------------------------

class CustomerListResponse(BaseModel):
    """Paginated list of customers.

    Attributes
    ----------
    page : int
        Current page number.
    limit : int
        Number of items per page.
    total : int
        Total number of customers.
    customers : List[str]
        List of customer identifiers.
    """

    page: int
    limit: int
    total: int
    customers: List[str]


class CustomerProfile(BaseModel):
    """Synthetic customer profile.

    Attributes
    ----------
    id : str
        Customer identifier.
    transactions_count : int
        Total number of transactions.
    avg_amount : float
        Average transaction amount.
    total_amount : float
        Total transaction volume.
    fraudulent : bool
        Whether any fraud is associated.
    """

    id: str
    transactions_count: int
    avg_amount: float
    total_amount: float
    fraudulent: bool


class TopCustomer(BaseModel):
    """Customer ranked by transaction volume.

    Attributes
    ----------
    id : str
        Customer identifier.
    total_amount : float
        Total transaction volume.
    transactions_count : int
        Number of transactions.
    """

    id: str
    total_amount: float
    transactions_count: int


# ---------------------------------------------------------------------------
# System schemas
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    """API health check response.

    Attributes
    ----------
    status : str
        Current status of the API.
    uptime : str
        Human-readable uptime string.
    dataset_loaded : bool
        Whether the dataset is loaded.
    """

    status: str
    uptime: str
    dataset_loaded: bool


class MetadataResponse(BaseModel):
    """API metadata response.

    Attributes
    ----------
    version : str
        API version string.
    last_update : str
        ISO 8601 timestamp of last update.
    total_records : int
        Total number of records in dataset.
    """

    version: str
    last_update: str
    total_records: int
