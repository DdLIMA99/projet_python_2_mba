"""Feature tests using unittest for Banking Transactions API."""

import unittest

import pandas as pd
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


def _build_df() -> pd.DataFrame:
    """Build the sample DataFrame.

    Returns
    -------
    pd.DataFrame
        Sample transactions.
    """
    return pd.DataFrame(SAMPLE_DATA)


class FeatureTransactionBrowsing(unittest.TestCase):
    """Feature: analyst browses and retrieves transactions."""

    def setUp(self) -> None:
        """Set up test client and inject sample data."""
        data_loader.set_data(_build_df())
        self.client = TestClient(app)

    def tearDown(self) -> None:
        """Reset data loader after each test."""
        data_loader.reset_data()

    def test_browse_first_page(self) -> None:
        """Analyst can browse the first page of transactions."""
        resp = self.client.get("/api/transactions?page=1&limit=5")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["page"], 1)
        self.assertLessEqual(len(data["transactions"]), 5)
        self.assertEqual(data["total"], 10)

    def test_retrieve_by_id(self) -> None:
        """Analyst retrieves full details of a known transaction."""
        resp = self.client.get("/api/transactions/tx_001")
        self.assertEqual(resp.status_code, 200)
        tx = resp.json()
        self.assertEqual(tx["id"], "tx_001")
        self.assertIn("amount", tx)
        self.assertIn("use_chip", tx)

    def test_retrieve_unknown_id(self) -> None:
        """Retrieving an unknown transaction returns 404."""
        resp = self.client.get("/api/transactions/tx_BADID")
        self.assertEqual(resp.status_code, 404)

    def test_browse_available_types(self) -> None:
        """Analyst can discover available transaction types."""
        resp = self.client.get("/api/transactions/types")
        self.assertEqual(resp.status_code, 200)
        types = resp.json()["types"]
        self.assertIn("Online Transaction", types)
        self.assertIn("Chip Transaction", types)


class FeatureTransactionSearch(unittest.TestCase):
    """Feature: analyst searches transactions using filters."""

    def setUp(self) -> None:
        """Set up test client and inject sample data."""
        data_loader.set_data(_build_df())
        self.client = TestClient(app)

    def tearDown(self) -> None:
        """Reset data loader after each test."""
        data_loader.reset_data()

    def test_search_fraudulent_online(self) -> None:
        """Analyst finds fraudulent Online transactions."""
        resp = self.client.post(
            "/api/transactions/search",
            json={"use_chip": "Online Transaction", "isFraud": 1},
        )
        self.assertEqual(resp.status_code, 200)
        for tx in resp.json():
            self.assertEqual(tx["use_chip"], "Online Transaction")
            self.assertEqual(tx["isFraud"], 1)

    def test_search_large_amounts(self) -> None:
        """Analyst finds large transactions."""
        resp = self.client.post(
            "/api/transactions/search",
            json={"amount_range": [5000.0, 99999.0]},
        )
        self.assertEqual(resp.status_code, 200)
        for tx in resp.json():
            self.assertGreaterEqual(tx["amount"], 5000.0)

    def test_filter_by_url_params(self) -> None:
        """Analyst uses URL params for quick filtering."""
        resp = self.client.get(
            "/api/transactions?type=Swipe+Transaction"
        )
        self.assertEqual(resp.status_code, 200)
        for tx in resp.json()["transactions"]:
            self.assertEqual(tx["use_chip"], "Swipe Transaction")


class FeatureCustomerPortfolio(unittest.TestCase):
    """Feature: banker reviews a customer portfolio."""

    def setUp(self) -> None:
        """Set up test client and inject sample data."""
        data_loader.set_data(_build_df())
        self.client = TestClient(app)

    def tearDown(self) -> None:
        """Reset data loader after each test."""
        data_loader.reset_data()

    def test_view_customer_profile(self) -> None:
        """Banker views synthetic profile for a customer."""
        resp = self.client.get("/api/customers/C200")
        self.assertEqual(resp.status_code, 200)
        profile = resp.json()
        self.assertEqual(profile["id"], "C200")
        self.assertGreater(profile["transactions_count"], 0)
        self.assertIsInstance(profile["fraudulent"], bool)

    def test_view_customer_outgoing_transactions(self) -> None:
        """Banker views transactions sent by a customer."""
        resp = self.client.get(
            "/api/transactions/by-customer/C200"
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertGreater(data["total"], 0)
        for tx in data["transactions"]:
            self.assertEqual(tx["client_id"], "C200")

    def test_view_merchant_incoming_transactions(self) -> None:
        """Banker views transactions received by a merchant."""
        resp = self.client.get(
            "/api/transactions/to-customer/M001"
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertGreater(data["total"], 0)
        for tx in data["transactions"]:
            self.assertEqual(tx["merchant_id"], "M001")

    def test_top_customers_ranking(self) -> None:
        """Banker views top customers by volume."""
        resp = self.client.get("/api/customers/top?n=5")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertLessEqual(len(data), 5)
        amounts = [c["total_amount"] for c in data]
        self.assertEqual(amounts, sorted(amounts, reverse=True))

    def test_customer_not_found(self) -> None:
        """Accessing unknown customer returns 404."""
        resp = self.client.get("/api/customers/GHOST_CUSTOMER")
        self.assertEqual(resp.status_code, 404)


class FeatureFraudAnalysis(unittest.TestCase):
    """Feature: compliance team performs fraud analysis."""

    def setUp(self) -> None:
        """Set up test client and inject sample data."""
        data_loader.set_data(_build_df())
        self.client = TestClient(app)

    def tearDown(self) -> None:
        """Reset data loader after each test."""
        data_loader.reset_data()

    def test_view_fraud_summary(self) -> None:
        """Compliance sees global fraud overview."""
        resp = self.client.get("/api/fraud/summary")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["total_frauds"], 3)
        self.assertGreaterEqual(data["flagged"], 0)

    def test_fraud_breakdown_by_type(self) -> None:
        """Compliance sees fraud rate for each type."""
        resp = self.client.get("/api/fraud/by-type")
        self.assertEqual(resp.status_code, 200)
        for item in resp.json():
            self.assertIn("type", item)
            self.assertGreaterEqual(item["fraud_rate"], 0.0)
            self.assertLessEqual(item["fraud_rate"], 1.0)

    def test_predict_fraud(self) -> None:
        """Compliance scores a transaction."""
        resp = self.client.post(
            "/api/fraud/predict",
            json={
                "use_chip": "Online Transaction",
                "amount": 15000.0,
            },
        )
        self.assertEqual(resp.status_code, 200)
        result = resp.json()
        self.assertIn("isFraud", result)
        self.assertGreaterEqual(result["probability"], 0.0)
        self.assertLessEqual(result["probability"], 1.0)


class FeatureStatisticsReporting(unittest.TestCase):
    """Feature: reporting team generates statistics."""

    def setUp(self) -> None:
        """Set up test client and inject sample data."""
        data_loader.set_data(_build_df())
        self.client = TestClient(app)

    def tearDown(self) -> None:
        """Reset data loader after each test."""
        data_loader.reset_data()

    def test_global_overview(self) -> None:
        """Reporting team views global dataset overview."""
        resp = self.client.get("/api/stats/overview")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["total_transactions"], 10)
        self.assertGreater(data["avg_amount"], 0)

    def test_amount_histogram(self) -> None:
        """Reporting team generates amount histogram."""
        resp = self.client.get(
            "/api/stats/amount-distribution?bins=5"
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data["bins"]), 5)
        self.assertEqual(sum(data["counts"]), 10)

    def test_stats_by_type(self) -> None:
        """Reporting team views breakdown by type."""
        resp = self.client.get("/api/stats/by-type")
        self.assertEqual(resp.status_code, 200)
        self.assertGreater(len(resp.json()), 0)

    def test_daily_volume(self) -> None:
        """Reporting team views daily transaction volume."""
        resp = self.client.get("/api/stats/daily")
        self.assertEqual(resp.status_code, 200)
        for item in resp.json():
            self.assertIn("date", item)
            self.assertIn("count", item)


class FeatureSystemAdministration(unittest.TestCase):
    """Feature: ops team monitors system health."""

    def setUp(self) -> None:
        """Set up test client and inject sample data."""
        data_loader.set_data(_build_df())
        self.client = TestClient(app)

    def tearDown(self) -> None:
        """Reset data loader after each test."""
        data_loader.reset_data()

    def test_health_check(self) -> None:
        """Ops verifies that the API is healthy."""
        resp = self.client.get("/api/system/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "ok")
        self.assertTrue(data["dataset_loaded"])

    def test_metadata_check(self) -> None:
        """Ops reviews API version metadata."""
        resp = self.client.get("/api/system/metadata")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["version"], "1.0.0")
        self.assertTrue(data["last_update"].endswith("Z"))

    def test_delete_test_mode(self) -> None:
        """Ops deletes a transaction in test mode."""
        resp = self.client.delete("/api/transactions/tx_004")
        self.assertEqual(resp.status_code, 200)
        get_resp = self.client.get("/api/transactions/tx_004")
        self.assertEqual(get_resp.status_code, 404)

    def test_recent_transactions(self) -> None:
        """Ops checks most recent activity."""
        resp = self.client.get("/api/transactions/recent?n=5")
        self.assertEqual(resp.status_code, 200)
        self.assertLessEqual(len(resp.json()), 5)


if __name__ == "__main__":
    unittest.main()
