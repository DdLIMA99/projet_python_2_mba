"""Router for system/administration endpoints (routes 19-20)."""

from fastapi import APIRouter

from banking_api.models.schemas import HealthResponse, MetadataResponse
from banking_api.services import system_service

router: APIRouter = APIRouter(
    prefix="/api/system",
    tags=["System"],
)


# Route 19
@router.get(
    "/health",
    response_model=HealthResponse,
    summary="API health check",
)
def get_health() -> HealthResponse:
    """Check the health of the API service.

    Returns
    -------
    HealthResponse
        Status, uptime, and dataset loading state.
    """
    return system_service.get_health()


# Route 20
@router.get(
    "/metadata",
    response_model=MetadataResponse,
    summary="API version and metadata",
)
def get_metadata() -> MetadataResponse:
    """Return version and metadata for the API.

    Returns
    -------
    MetadataResponse
        Version, last update timestamp, and record count.
    """
    return system_service.get_metadata()
