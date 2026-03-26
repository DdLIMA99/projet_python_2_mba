"""Configuration module for Banking Transactions API."""

import os
from datetime import datetime, timezone

# Path to the CSV dataset (injected via environment variable)
DATA_PATH: str = os.getenv(
    "TRANSACTIONS_CSV_PATH",
    "data/transactions_data.csv",
)

# Application metadata
APP_VERSION: str = "1.0.0"
APP_TITLE: str = "Banking Transactions API"
APP_DESCRIPTION: str = (
    "API REST pour exposer et manipuler les données "
    "de transactions bancaires fictives."
)

# API last update (set at import time)
LAST_UPDATE: str = datetime.now(timezone.utc).isoformat().replace(
    "+00:00", "Z"
)

# Startup time (used for uptime calculation)
START_TIME: float = 0.0
