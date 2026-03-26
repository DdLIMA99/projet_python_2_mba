"""Router for customer-related endpoints (routes 16-18)."""

from typing import List

from fastapi import APIRouter, HTTPException, Query, status

from banking_api.models.schemas import (
    CustomerListResponse,
    CustomerProfile,
    TopCustomer,
)
from banking_api.services import customer_service

router: APIRouter = APIRouter(
    prefix="/api/customers",
    tags=["Customers"],
)


# Route 18 — must be declared BEFORE /{customer_id}
@router.get(
    "/top",
    response_model=List[TopCustomer],
    summary="Top customers by transaction volume",
)
def get_top_customers(
    n: int = Query(default=10, ge=1, le=100),
) -> List[TopCustomer]:
    """Return the N customers with the highest transaction volume.

    Parameters
    ----------
    n : int
        Number of top customers to return (default: 10).

    Returns
    -------
    List[TopCustomer]
        Ranked list of customers with total volumes.
    """
    return customer_service.get_top_customers(n=n)


# Route 16
@router.get(
    "",
    response_model=CustomerListResponse,
    summary="Paginated list of customers",
)
def list_customers(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
) -> CustomerListResponse:
    """Return a paginated list of unique customer IDs.

    Parameters
    ----------
    page : int
        Page number (1-indexed).
    limit : int
        Number of customers per page.

    Returns
    -------
    CustomerListResponse
        Paginated list of customer identifiers.
    """
    return customer_service.get_customers(page=page, limit=limit)


# Route 17 — parameterized, must come AFTER /top
@router.get(
    "/{customer_id}",
    response_model=CustomerProfile,
    summary="Customer synthetic profile",
)
def get_customer_profile(customer_id: str) -> CustomerProfile:
    """Return a synthetic profile for a specific customer.

    Parameters
    ----------
    customer_id : str
        Unique customer identifier.

    Returns
    -------
    CustomerProfile
        Aggregated profile data.

    Raises
    ------
    HTTPException
        404 if the customer is not found.
    """
    profile = customer_service.get_customer_profile(customer_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer '{customer_id}' not found.",
        )
    return profile
