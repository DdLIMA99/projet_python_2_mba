"""Service layer for transaction-related operations."""

from typing import List, Optional

import pandas as pd

from banking_api.services import data_loader
from banking_api.models.schemas import (
    TransactionItem,
    TransactionListResponse,
    TransactionSearchRequest,
)


def _row_to_item(row: pd.Series) -> TransactionItem:
    """Convert a DataFrame row to a TransactionItem.

    Parameters
    ----------
    row : pd.Series
        A row from the transactions DataFrame.

    Returns
    -------
    TransactionItem
        Pydantic model populated from the row.
    """
    return TransactionItem(
        id=str(row["id"]),
        date=str(row["date"]),
        client_id=str(row["client_id"]),
        card_id=str(row["card_id"]),
        amount=float(row["amount"]),
        use_chip=str(row["use_chip"]),
        merchant_id=str(row["merchant_id"]),
        merchant_city=str(row["merchant_city"]),
        merchant_state=str(row["merchant_state"]),
        zip=str(row["zip"]),
        mcc=str(row["mcc"]),
        errors=str(row["errors"]),
        isFraud=int(row["isFraud"]),
    )


def get_transactions(
    page: int = 1,
    limit: int = 10,
    type: Optional[str] = None,
    isFraud: Optional[int] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
) -> TransactionListResponse:
    """Return a paginated, optionally filtered list of transactions.

    Parameters
    ----------
    page : int
        Page number (1-indexed).
    limit : int
        Number of results per page.
    type : Optional[str]
        Filter by use_chip value.
    isFraud : Optional[int]
        Filter by fraud flag (0 or 1).
    min_amount : Optional[float]
        Minimum transaction amount.
    max_amount : Optional[float]
        Maximum transaction amount.

    Returns
    -------
    TransactionListResponse
        Paginated list of matching transactions.
    """
    df: pd.DataFrame = data_loader.get_data()

    if type is not None:
        df = df[df["use_chip"] == type]
    if isFraud is not None:
        df = df[df["isFraud"] == isFraud]
    if min_amount is not None:
        df = df[df["amount"] >= min_amount]
    if max_amount is not None:
        df = df[df["amount"] <= max_amount]

    total: int = len(df)
    start: int = (page - 1) * limit
    end: int = start + limit
    page_df: pd.DataFrame = df.iloc[start:end]

    transactions: List[TransactionItem] = [
        _row_to_item(row) for _, row in page_df.iterrows()
    ]

    return TransactionListResponse(
        page=page,
        limit=limit,
        total=total,
        transactions=transactions,
    )


def get_transaction_by_id(
    transaction_id: str,
) -> Optional[TransactionItem]:
    """Retrieve a single transaction by its ID.

    Parameters
    ----------
    transaction_id : str
        The unique transaction identifier.

    Returns
    -------
    Optional[TransactionItem]
        The transaction if found, None otherwise.
    """
    if data_loader.is_deleted(transaction_id):
        return None

    df: pd.DataFrame = data_loader.get_data()
    matches: pd.DataFrame = df[df["id"] == transaction_id]

    if matches.empty:
        return None

    return _row_to_item(matches.iloc[0])


def search_transactions(
    criteria: TransactionSearchRequest,
) -> List[TransactionItem]:
    """Search transactions using multiple criteria.

    Parameters
    ----------
    criteria : TransactionSearchRequest
        Search filters to apply.

    Returns
    -------
    List[TransactionItem]
        List of matching transactions.
    """
    df: pd.DataFrame = data_loader.get_data()

    if criteria.use_chip is not None:
        df = df[df["use_chip"] == criteria.use_chip]
    if criteria.isFraud is not None:
        df = df[df["isFraud"] == criteria.isFraud]
    if criteria.amount_range is not None and len(criteria.amount_range) == 2:
        lo: float = criteria.amount_range[0]
        hi: float = criteria.amount_range[1]
        df = df[(df["amount"] >= lo) & (df["amount"] <= hi)]
    if criteria.client_id is not None:
        df = df[df["client_id"] == criteria.client_id]
    if criteria.merchant_id is not None:
        df = df[df["merchant_id"] == criteria.merchant_id]

    return [_row_to_item(row) for _, row in df.iterrows()]


def get_transaction_types() -> List[str]:
    """Return the list of unique transaction methods.

    Returns
    -------
    List[str]
        Sorted list of unique use_chip values.
    """
    df: pd.DataFrame = data_loader.get_data()
    return sorted(df["use_chip"].unique().tolist())


def get_recent_transactions(n: int = 10) -> List[TransactionItem]:
    """Return the N most recent transactions (by date).

    Parameters
    ----------
    n : int
        Number of recent transactions to return.

    Returns
    -------
    List[TransactionItem]
        List of the N most recent transactions.
    """
    df: pd.DataFrame = data_loader.get_data()
    recent: pd.DataFrame = df.sort_values(
        "date", ascending=False
    ).head(n)
    return [_row_to_item(row) for _, row in recent.iterrows()]


def delete_transaction(transaction_id: str) -> bool:
    """Logically delete a transaction (test mode only).

    Parameters
    ----------
    transaction_id : str
        The ID of the transaction to delete.

    Returns
    -------
    bool
        True if the transaction existed and was deleted,
        False if it was not found or already deleted.
    """
    if data_loader.is_deleted(transaction_id):
        return False

    df: pd.DataFrame = data_loader.get_data()
    exists: bool = not df[df["id"] == transaction_id].empty

    if exists:
        data_loader.mark_deleted(transaction_id)
        return True

    return False


def get_transactions_by_customer(
    customer_id: str,
    page: int = 1,
    limit: int = 10,
) -> TransactionListResponse:
    """Return transactions originated by a given customer.

    Parameters
    ----------
    customer_id : str
        The client identifier.
    page : int
        Page number (1-indexed).
    limit : int
        Number of results per page.

    Returns
    -------
    TransactionListResponse
        Paginated transactions from the customer.
    """
    df: pd.DataFrame = data_loader.get_data()
    df = df[df["client_id"] == customer_id]

    total: int = len(df)
    start: int = (page - 1) * limit
    end: int = start + limit
    page_df: pd.DataFrame = df.iloc[start:end]

    transactions: List[TransactionItem] = [
        _row_to_item(row) for _, row in page_df.iterrows()
    ]

    return TransactionListResponse(
        page=page,
        limit=limit,
        total=total,
        transactions=transactions,
    )


def get_transactions_to_customer(
    customer_id: str,
    page: int = 1,
    limit: int = 10,
) -> TransactionListResponse:
    """Return transactions received by a given merchant.

    Parameters
    ----------
    customer_id : str
        The merchant identifier.
    page : int
        Page number (1-indexed).
    limit : int
        Number of results per page.

    Returns
    -------
    TransactionListResponse
        Paginated transactions to the merchant.
    """
    df: pd.DataFrame = data_loader.get_data()
    df = df[df["merchant_id"] == customer_id]

    total: int = len(df)
    start: int = (page - 1) * limit
    end: int = start + limit
    page_df: pd.DataFrame = df.iloc[start:end]

    transactions: List[TransactionItem] = [
        _row_to_item(row) for _, row in page_df.iterrows()
    ]

    return TransactionListResponse(
        page=page,
        limit=limit,
        total=total,
        transactions=transactions,
    )
