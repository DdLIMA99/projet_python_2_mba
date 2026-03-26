"""Main FastAPI application entry point."""

import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from banking_api import config
from banking_api.routers import (
    customers,
    fraud,
    stats,
    system,
    transactions,
)
from banking_api.services import data_loader


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Manage application startup and shutdown events.

    Parameters
    ----------
    app : FastAPI
        The FastAPI application instance.

    Yields
    ------
    None
        Control is yielded to the application.
    """
    # Startup
    config.START_TIME = time.time()
    try:
        data_loader.load_data()
    except FileNotFoundError as exc:
        # Warn but do not crash — tests inject their own data
        import warnings

        warnings.warn(
            f"Dataset not found at startup: {exc}. "
            "Use TRANSACTIONS_CSV_PATH env var to set path.",
            stacklevel=2,
        )
    yield
    # Shutdown (nothing to clean up)


app: FastAPI = FastAPI(
    title=config.APP_TITLE,
    description=config.APP_DESCRIPTION,
    version=config.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Include all routers
app.include_router(transactions.router)
app.include_router(stats.router)
app.include_router(fraud.router)
app.include_router(customers.router)
app.include_router(system.router)


@app.get("/", tags=["Root"], summary="API root")
def root() -> dict:
    """Return a welcome message and API information.

    Returns
    -------
    dict
        Welcome message and documentation links.
    """
    return {
        "message": "Banking Transactions API",
        "version": config.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
    }


def main() -> None:
    """CLI entry point to run the API server."""
    import uvicorn
    uvicorn.run("banking_api.main:app", host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()