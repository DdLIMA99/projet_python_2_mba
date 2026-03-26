"""Router for transaction-related endpoints (routes 1-8)."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status

from banking_api.models.schemas import (
    DeleteResponse,
    TransactionItem,
    TransactionListResponse,
    TransactionSearchRequest,
    TransactionTypesResponse,
)
from banking_api.services import transactions_service

router: APIRouter = APIRouter(
    prefix="/api/transactions",
    tags=["Transactions"],
)


# Route 4 — declared BEFORE /{id} to avoid conflict
@router.get(
    "/types",
    response_model=TransactionTypesResponse,
    summary="List unique transaction types",
)
def list_transaction_types() -> TransactionTypesResponse:
    """Return all unique transaction method values.

    Returns
    -------
    TransactionTypesResponse
        Object containing the sorted list of types.
    """
    types: List[str] = transactions_service.get_transaction_types()
    return TransactionTypesResponse(types=types)


# Route 5 — declared BEFORE /{id} to avoid conflict
@router.get(
    "/recent",
    response_model=List[TransactionItem],
    summary="Get N most recent transactions",
)
def get_recent(
    n: int = Query(default=10, ge=1, le=1000),
) -> List[TransactionItem]:
    """Return the N most recent transactions (by date).

    Parameters
    ----------
    n : int
        Number of transactions to return (default: 10).

    Returns
    -------
    List[TransactionItem]
        The N most recent transactions.
    """
    return transactions_service.get_recent_transactions(n=n)


# Route 7 — declared BEFORE /{id} to avoid conflict
@router.get(
    "/by-customer/{customer_id}",
    response_model=TransactionListResponse,
    summary="Get transactions by client",
)
def get_by_customer(
    customer_id: str,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
) -> TransactionListResponse:
    """Return paginated transactions sent by a client.

    Parameters
    ----------
    customer_id : str
        The client identifier.
    page : int
        Page number.
    limit : int
        Items per page.

    Returns
    -------
    TransactionListResponse
        Paginated list of client transactions.
    """
    return transactions_service.get_transactions_by_customer(
        customer_id=customer_id,
        page=page,
        limit=limit,
    )


# Route 8 — declared BEFORE /{id} to avoid conflict
@router.get(
    "/to-customer/{merchant_id}",
    response_model=TransactionListResponse,
    summary="Get transactions received by a merchant",
)
def get_to_customer(
    merchant_id: str,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
) -> TransactionListResponse:
    """Return paginated transactions received by a merchant.

    Parameters
    ----------
    merchant_id : str
        The merchant identifier.
    page : int
        Page number.
    limit : int
        Items per page.

    Returns
    -------
    TransactionListResponse
        Paginated list of incoming transactions.
    """
    return transactions_service.get_transactions_to_customer(
        customer_id=merchant_id,
        page=page,
        limit=limit,
    )


# Route 1
@router.get(
    "",
    response_model=TransactionListResponse,
    summary="List transactions (paginated, filterable)",
)
def list_transactions(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    type: Optional[str] = Query(default=None),
    isFraud: Optional[int] = Query(default=None, ge=0, le=1),
    min_amount: Optional[float] = Query(default=None, ge=0),
    max_amount: Optional[float] = Query(default=None, ge=0),
) -> TransactionListResponse:
    """Return a paginated, filtered list of transactions.

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
        Paginated list of transactions.
    """
    return transactions_service.get_transactions(
        page=page,
        limit=limit,
        type=type,
        isFraud=isFraud,
        min_amount=min_amount,
        max_amount=max_amount,
    )


# Route 3
@router.post(
    "/search",
    response_model=List[TransactionItem],
    summary="Multi-criteria transaction search",
)
def search_transactions(
    criteria: TransactionSearchRequest,
) -> List[TransactionItem]:
    """Search transactions using a JSON body with multiple filters.

    Parameters
    ----------
    criteria : TransactionSearchRequest
        JSON body with optional filters.

    Returns
    -------
    List[TransactionItem]
        All matching transactions.
    """
    return transactions_service.search_transactions(criteria)


# Route 2
@router.get(
    "/{transaction_id}",
    response_model=TransactionItem,
    summary="Get a transaction by ID",
)
def get_transaction(transaction_id: str) -> TransactionItem:
    """Return the details of a specific transaction.

    Parameters
    ----------
    transaction_id : str
        Unique transaction identifier.

    Returns
    -------
    TransactionItem
        Transaction details.

    Raises
    ------
    HTTPException
        404 if the transaction is not found or deleted.
    """
    item = transactions_service.get_transaction_by_id(
        transaction_id
    )
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction '{transaction_id}' not found.",
        )
    return item


# Route 6
@router.delete(
    "/{transaction_id}",
    response_model=DeleteResponse,
    summary="Delete a transaction (test mode only)",
)
def delete_transaction(transaction_id: str) -> DeleteResponse:
    """Logically delete a transaction (test mode only).

    Parameters
    ----------
    transaction_id : str
        Unique transaction identifier.

    Returns
    -------
    DeleteResponse
        Confirmation message with the deleted ID.

    Raises
    ------
    HTTPException
        404 if the transaction is not found.
    """
    deleted: bool = transactions_service.delete_transaction(
        transaction_id
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction '{transaction_id}' not found.",
        )
    return DeleteResponse(
        message="Transaction deleted successfully.",
        id=transaction_id,
    )
