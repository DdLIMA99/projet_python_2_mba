"""Service layer for customer-related operations."""

from typing import List, Optional

import pandas as pd

from banking_api.services import data_loader
from banking_api.models.schemas import (
    CustomerListResponse,
    CustomerProfile,
    TopCustomer,
)


def get_customers(
    page: int = 1,
    limit: int = 10,
) -> CustomerListResponse:
    """Return a paginated list of unique client IDs.

    Parameters
    ----------
    page : int
        Page number (1-indexed).
    limit : int
        Number of customers per page.

    Returns
    -------
    CustomerListResponse
        Paginated list of unique customer identifiers.
    """
    df: pd.DataFrame = data_loader.get_data()
    all_customers: List[str] = sorted(
        df["client_id"].unique().tolist()
    )

    total: int = len(all_customers)
    start: int = (page - 1) * limit
    end: int = start + limit
    page_customers: List[str] = all_customers[start:end]

    return CustomerListResponse(
        page=page,
        limit=limit,
        total=total,
        customers=page_customers,
    )


def get_customer_profile(
    customer_id: str,
) -> Optional[CustomerProfile]:
    """Build a synthetic profile for a given customer.

    Parameters
    ----------
    customer_id : str
        The customer identifier to look up.

    Returns
    -------
    Optional[CustomerProfile]
        Customer profile if found, None otherwise.
    """
    df: pd.DataFrame = data_loader.get_data()
    subset: pd.DataFrame = df[df["client_id"] == customer_id]

    if subset.empty:
        return None

    count: int = len(subset)
    avg_amount: float = round(float(subset["amount"].mean()), 2)
    total_amount: float = round(float(subset["amount"].sum()), 2)
    fraudulent: bool = bool(subset["isFraud"].any())

    return CustomerProfile(
        id=customer_id,
        transactions_count=count,
        avg_amount=avg_amount,
        total_amount=total_amount,
        fraudulent=fraudulent,
    )


def get_top_customers(n: int = 10) -> List[TopCustomer]:
    """Return the top N customers by total transaction volume.

    Parameters
    ----------
    n : int
        Number of top customers to return.

    Returns
    -------
    List[TopCustomer]
        Ranked list of customers with their volumes.
    """
    df: pd.DataFrame = data_loader.get_data()
    grouped = (
        df.groupby("client_id")["amount"]
        .agg(["sum", "count"])
        .reset_index()
        .rename(
            columns={"sum": "total_amount", "count": "tx_count"}
        )
        .nlargest(n, "total_amount")
    )

    result: List[TopCustomer] = []
    for _, row in grouped.iterrows():
        result.append(
            TopCustomer(
                id=str(row["client_id"]),
                total_amount=round(float(row["total_amount"]), 2),
                transactions_count=int(row["tx_count"]),
            )
        )

    return result
