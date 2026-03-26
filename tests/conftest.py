"""Shared pytest fixtures for Banking Transactions API tests."""

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from banking_api.main import app
from banking_api.services import data_loader


SAMPLE_DATA = {
    "id": [
        "tx_001", "tx_002", "tx_003", "tx_004", "tx_005",
        "tx_006", "tx_007", "tx_008", "tx_009", "tx_010",
    ],
    "date": [
        "2020-01-01", "2020-01-01", "2020-01-02",
        "2020-01-02", "2020-01-03", "2020-01-03",
        "2020-01-04", "2020-01-05", "2020-01-06",
        "2020-01-07",
    ],
    "client_id": [
        "C100", "C200", "C300", "C400", "C200",
        "C300", "C100", "C500", "C600", "C700",
    ],
    "card_id": [
        "CARD1", "CARD2", "CARD3", "CARD4", "CARD2",
        "CARD3", "CARD1", "CARD5", "CARD6", "CARD7",
    ],
    "amount": [
        100.0, 5000.0, 2500.0, 300.0, 8000.0,
        1500.0, 200.0, 50.0, 12000.0, 3000.0,
    ],
    "use_chip": [
        "Swipe Transaction", "Online Transaction",
        "Chip Transaction", "Swipe Transaction",
        "Online Transaction", "Chip Transaction",
        "Swipe Transaction", "Online Transaction",
        "Online Transaction", "Chip Transaction",
    ],
    "merchant_id": [
        "M001", "M002", "M003", "M004", "M001",
        "M002", "M005", "M006", "M003", "M004",
    ],
    "merchant_city": [
        "Paris", "Lyon", "Marseille", "Toulouse",
        "Paris", "Lyon", "Nice", "Bordeaux",
        "Marseille", "Toulouse",
    ],
    "merchant_state": [
        "IDF", "ARA", "PAC", "OCC", "IDF",
        "ARA", "PAC", "NAQ", "PAC", "OCC",
    ],
    "zip": [
        "75001", "69001", "13001", "31000", "75001",
        "69001", "06000", "33000", "13001", "31000",
    ],
    "mcc": [
        "5411", "5812", "5999", "5411", "5812",
        "5999", "5411", "5812", "5999", "5411",
    ],
    "errors": [
        "", "", "Insufficient Balance", "", "Bad CVV",
        "", "", "", "Insufficient Balance", "",
    ],
}


@pytest.fixture(autouse=True)
def inject_test_data() -> None:
    """Inject sample DataFrame before each test and reset after.

    This fixture is applied automatically to all tests.
    """
    df = pd.DataFrame(SAMPLE_DATA)
    data_loader.set_data(df)
    yield
    data_loader.reset_data()


@pytest.fixture
def client() -> TestClient:
    """Return a FastAPI TestClient for the application.

    Returns
    -------
    TestClient
        Configured test client.
    """
    return TestClient(app)


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Return a fresh copy of the sample DataFrame.

    Returns
    -------
    pd.DataFrame
        Sample transactions DataFrame.
    """
    return pd.DataFrame(SAMPLE_DATA)
