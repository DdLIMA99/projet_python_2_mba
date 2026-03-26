"""Pytest unit tests for all 20 API routes."""

from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Routes 1-8 : Transactions
# ---------------------------------------------------------------------------

class TestListTransactions:
    """Tests for GET /api/transactions (Route 1)."""

    def test_default_pagination(self, client: TestClient) -> None:
        """Should return page 1 with default limit."""
        resp = client.get("/api/transactions")
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"] == 1
        assert "transactions" in data
        assert isinstance(data["transactions"], list)

    def test_pagination_page_2(self, client: TestClient) -> None:
        """Page 2 with limit 3 should return correct slice."""
        resp = client.get("/api/transactions?page=2&limit=3")
        assert resp.status_code == 200
        assert resp.json()["page"] == 2

    def test_filter_by_type(self, client: TestClient) -> None:
        """Filtering by type should return only matching records."""
        resp = client.get(
            "/api/transactions?type=Online+Transaction"
        )
        assert resp.status_code == 200
        for tx in resp.json()["transactions"]:
            assert tx["use_chip"] == "Online Transaction"

    def test_filter_by_is_fraud(self, client: TestClient) -> None:
        """Filtering isFraud=1 should return only fraudulent."""
        resp = client.get("/api/transactions?isFraud=1")
        assert resp.status_code == 200
        for tx in resp.json()["transactions"]:
            assert tx["isFraud"] == 1

    def test_filter_by_min_amount(self, client: TestClient) -> None:
        """min_amount filter should exclude small transactions."""
        resp = client.get("/api/transactions?min_amount=5000")
        assert resp.status_code == 200
        for tx in resp.json()["transactions"]:
            assert tx["amount"] >= 5000

    def test_filter_by_max_amount(self, client: TestClient) -> None:
        """max_amount filter should exclude large transactions."""
        resp = client.get("/api/transactions?max_amount=200")
        assert resp.status_code == 200
        for tx in resp.json()["transactions"]:
            assert tx["amount"] <= 200


class TestGetTransactionById:
    """Tests for GET /api/transactions/{id} (Route 2)."""

    def test_existing_id(self, client: TestClient) -> None:
        """Should return 200 and correct ID for existing tx."""
        resp = client.get("/api/transactions/tx_001")
        assert resp.status_code == 200
        assert resp.json()["id"] == "tx_001"

    def test_nonexistent_id(self, client: TestClient) -> None:
        """Should return 404 for unknown transaction ID."""
        resp = client.get("/api/transactions/tx_BADID")
        assert resp.status_code == 404

    def test_response_fields(self, client: TestClient) -> None:
        """Response should contain all required fields."""
        resp = client.get("/api/transactions/tx_001")
        data = resp.json()
        required = {
            "id", "date", "client_id", "card_id", "amount",
            "use_chip", "merchant_id", "isFraud",
        }
        assert required.issubset(data.keys())


class TestSearchTransactions:
    """Tests for POST /api/transactions/search (Route 3)."""

    def test_search_by_type(self, client: TestClient) -> None:
        """Should filter by use_chip correctly."""
        resp = client.post(
            "/api/transactions/search",
            json={"use_chip": "Chip Transaction"},
        )
        assert resp.status_code == 200
        for tx in resp.json():
            assert tx["use_chip"] == "Chip Transaction"

    def test_search_by_fraud(self, client: TestClient) -> None:
        """Should filter fraudulent transactions."""
        resp = client.post(
            "/api/transactions/search",
            json={"isFraud": 1},
        )
        assert resp.status_code == 200
        for tx in resp.json():
            assert tx["isFraud"] == 1

    def test_search_by_amount_range(self, client: TestClient) -> None:
        """Should filter by amount range."""
        resp = client.post(
            "/api/transactions/search",
            json={"amount_range": [1000.0, 3000.0]},
        )
        assert resp.status_code == 200
        for tx in resp.json():
            assert 1000.0 <= tx["amount"] <= 3000.0

    def test_search_by_client(self, client: TestClient) -> None:
        """Should filter by client_id."""
        resp = client.post(
            "/api/transactions/search",
            json={"client_id": "C200"},
        )
        assert resp.status_code == 200
        for tx in resp.json():
            assert tx["client_id"] == "C200"

    def test_search_empty_body(self, client: TestClient) -> None:
        """Empty body should return all transactions."""
        resp = client.post("/api/transactions/search", json={})
        assert resp.status_code == 200
        assert len(resp.json()) == 10


class TestGetTransactionTypes:
    """Tests for GET /api/transactions/types (Route 4)."""

    def test_returns_types(self, client: TestClient) -> None:
        """Should return a list of unique types."""
        resp = client.get("/api/transactions/types")
        assert resp.status_code == 200
        data = resp.json()
        assert "types" in data
        assert isinstance(data["types"], list)
        assert len(data["types"]) > 0

    def test_types_are_unique(self, client: TestClient) -> None:
        """All returned types should be unique."""
        types = client.get("/api/transactions/types").json()["types"]
        assert len(types) == len(set(types))

    def test_known_types_present(self, client: TestClient) -> None:
        """Expected types from sample data should be present."""
        types = client.get("/api/transactions/types").json()["types"]
        assert "Online Transaction" in types
        assert "Chip Transaction" in types


class TestGetRecentTransactions:
    """Tests for GET /api/transactions/recent (Route 5)."""

    def test_default_n(self, client: TestClient) -> None:
        """Default should return at most 10 transactions."""
        resp = client.get("/api/transactions/recent")
        assert resp.status_code == 200
        assert len(resp.json()) <= 10

    def test_custom_n(self, client: TestClient) -> None:
        """Should return exactly n transactions when n <= total."""
        resp = client.get("/api/transactions/recent?n=3")
        assert resp.status_code == 200
        assert len(resp.json()) == 3

    def test_invalid_n(self, client: TestClient) -> None:
        """n=0 should return 422 validation error."""
        resp = client.get("/api/transactions/recent?n=0")
        assert resp.status_code == 422


class TestDeleteTransaction:
    """Tests for DELETE /api/transactions/{id} (Route 6)."""

    def test_delete_existing(self, client: TestClient) -> None:
        """Deleting an existing transaction should return 200."""
        resp = client.delete("/api/transactions/tx_001")
        assert resp.status_code == 200
        assert resp.json()["id"] == "tx_001"

    def test_deleted_not_found(self, client: TestClient) -> None:
        """After deletion, GET should return 404."""
        client.delete("/api/transactions/tx_002")
        resp = client.get("/api/transactions/tx_002")
        assert resp.status_code == 404

    def test_delete_nonexistent(self, client: TestClient) -> None:
        """Deleting a non-existent ID should return 404."""
        resp = client.delete("/api/transactions/tx_BADID")
        assert resp.status_code == 404


class TestGetByCustomer:
    """Tests for GET /api/transactions/by-customer/{id} (Route 7)."""

    def test_existing_customer(self, client: TestClient) -> None:
        """Should return transactions for client."""
        resp = client.get("/api/transactions/by-customer/C100")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] > 0
        for tx in data["transactions"]:
            assert tx["client_id"] == "C100"

    def test_unknown_customer(self, client: TestClient) -> None:
        """Should return empty list for unknown customer."""
        resp = client.get("/api/transactions/by-customer/UNKNOWN")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0


class TestGetToCustomer:
    """Tests for GET /api/transactions/to-customer/{id} (Route 8)."""

    def test_existing_merchant(self, client: TestClient) -> None:
        """Should return transactions for merchant."""
        resp = client.get("/api/transactions/to-customer/M001")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] > 0
        for tx in data["transactions"]:
            assert tx["merchant_id"] == "M001"

    def test_unknown_merchant(self, client: TestClient) -> None:
        """Unknown merchant should return empty list."""
        resp = client.get("/api/transactions/to-customer/UNKNOWN")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0


# ---------------------------------------------------------------------------
# Routes 9-12 : Statistics
# ---------------------------------------------------------------------------

class TestStatsOverview:
    """Tests for GET /api/stats/overview (Route 9)."""

    def test_returns_200(self, client: TestClient) -> None:
        """Should return 200."""
        resp = client.get("/api/stats/overview")
        assert resp.status_code == 200

    def test_fields_present(self, client: TestClient) -> None:
        """Response should contain all required fields."""
        data = client.get("/api/stats/overview").json()
        assert "total_transactions" in data
        assert "fraud_rate" in data
        assert "avg_amount" in data
        assert "most_common_type" in data

    def test_total_matches_sample(self, client: TestClient) -> None:
        """Total transactions should equal sample size."""
        data = client.get("/api/stats/overview").json()
        assert data["total_transactions"] == 10

    def test_fraud_rate_range(self, client: TestClient) -> None:
        """Fraud rate should be between 0 and 1."""
        data = client.get("/api/stats/overview").json()
        assert 0.0 <= data["fraud_rate"] <= 1.0


class TestAmountDistribution:
    """Tests for GET /api/stats/amount-distribution (Route 10)."""

    def test_returns_200(self, client: TestClient) -> None:
        """Should return 200."""
        assert client.get(
            "/api/stats/amount-distribution"
        ).status_code == 200

    def test_bins_and_counts(self, client: TestClient) -> None:
        """bins and counts lists must be of equal length."""
        data = client.get("/api/stats/amount-distribution").json()
        assert len(data["bins"]) == len(data["counts"])

    def test_custom_bins(self, client: TestClient) -> None:
        """Custom bin count should produce matching output length."""
        data = client.get(
            "/api/stats/amount-distribution?bins=4"
        ).json()
        assert len(data["bins"]) == 4


class TestStatsByType:
    """Tests for GET /api/stats/by-type (Route 11)."""

    def test_returns_list(self, client: TestClient) -> None:
        """Should return a non-empty list."""
        resp = client.get("/api/stats/by-type")
        assert resp.status_code == 200
        assert len(resp.json()) > 0

    def test_entry_fields(self, client: TestClient) -> None:
        """Each entry should have type, count, avg_amount."""
        for item in client.get("/api/stats/by-type").json():
            assert "type" in item
            assert "count" in item
            assert "avg_amount" in item


class TestDailyStats:
    """Tests for GET /api/stats/daily (Route 12)."""

    def test_returns_list(self, client: TestClient) -> None:
        """Should return a list."""
        resp = client.get("/api/stats/daily")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_entry_fields(self, client: TestClient) -> None:
        """Each entry should contain date, count, avg_amount."""
        for item in client.get("/api/stats/daily").json():
            assert "date" in item
            assert "count" in item
            assert "avg_amount" in item


# ---------------------------------------------------------------------------
# Routes 13-15 : Fraud
# ---------------------------------------------------------------------------

class TestFraudSummary:
    """Tests for GET /api/fraud/summary (Route 13)."""

    def test_returns_200(self, client: TestClient) -> None:
        """Should return 200."""
        assert client.get("/api/fraud/summary").status_code == 200

    def test_fields(self, client: TestClient) -> None:
        """Should contain all fraud summary fields."""
        data = client.get("/api/fraud/summary").json()
        assert "total_frauds" in data
        assert "flagged" in data
        assert "precision" in data
        assert "recall" in data

    def test_fraud_count_matches(self, client: TestClient) -> None:
        """total_frauds should equal 3 (from sample data)."""
        data = client.get("/api/fraud/summary").json()
        assert data["total_frauds"] == 3


class TestFraudByType:
    """Tests for GET /api/fraud/by-type (Route 14)."""

    def test_returns_list(self, client: TestClient) -> None:
        """Should return a non-empty list."""
        resp = client.get("/api/fraud/by-type")
        assert resp.status_code == 200
        assert len(resp.json()) > 0

    def test_entry_structure(self, client: TestClient) -> None:
        """Each entry should have required fields."""
        for item in client.get("/api/fraud/by-type").json():
            assert "type" in item
            assert "total" in item
            assert "frauds" in item
            assert 0.0 <= item["fraud_rate"] <= 1.0


class TestFraudPredict:
    """Tests for POST /api/fraud/predict (Route 15)."""

    def test_prediction_returns_200(self, client: TestClient) -> None:
        """Valid request should return 200."""
        resp = client.post(
            "/api/fraud/predict",
            json={
                "use_chip": "Online Transaction",
                "amount": 15000.0,
            },
        )
        assert resp.status_code == 200

    def test_prediction_fields(self, client: TestClient) -> None:
        """Response should contain isFraud and probability."""
        resp = client.post(
            "/api/fraud/predict",
            json={"use_chip": "Chip Transaction", "amount": 100.0},
        )
        data = resp.json()
        assert "isFraud" in data
        assert "probability" in data
        assert 0.0 <= data["probability"] <= 1.0

    def test_invalid_amount(self, client: TestClient) -> None:
        """Negative amount should return 422."""
        resp = client.post(
            "/api/fraud/predict",
            json={"use_chip": "Online Transaction", "amount": -10.0},
        )
        assert resp.status_code == 422

    def test_missing_field(self, client: TestClient) -> None:
        """Missing use_chip should return 422."""
        resp = client.post(
            "/api/fraud/predict",
            json={"amount": 500.0},
        )
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Routes 16-18 : Customers
# ---------------------------------------------------------------------------

class TestListCustomers:
    """Tests for GET /api/customers (Route 16)."""

    def test_returns_200(self, client: TestClient) -> None:
        """Should return 200."""
        assert client.get("/api/customers").status_code == 200

    def test_pagination_fields(self, client: TestClient) -> None:
        """Response should contain pagination metadata."""
        data = client.get("/api/customers").json()
        assert "page" in data
        assert "total" in data
        assert "customers" in data

    def test_limit_respected(self, client: TestClient) -> None:
        """Limit parameter should cap the number of customers."""
        data = client.get("/api/customers?limit=2").json()
        assert len(data["customers"]) <= 2


class TestGetCustomerProfile:
    """Tests for GET /api/customers/{id} (Route 17)."""

    def test_existing_customer(self, client: TestClient) -> None:
        """Should return profile for a known customer."""
        resp = client.get("/api/customers/C100")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "C100"
        assert data["transactions_count"] > 0

    def test_unknown_customer(self, client: TestClient) -> None:
        """Should return 404 for unknown customer."""
        resp = client.get("/api/customers/UNKNOWN_CUSTOMER")
        assert resp.status_code == 404

    def test_fraudulent_flag(self, client: TestClient) -> None:
        """Fraudulent flag should be bool."""
        data = client.get("/api/customers/C100").json()
        assert isinstance(data["fraudulent"], bool)


class TestTopCustomers:
    """Tests for GET /api/customers/top (Route 18)."""

    def test_returns_list(self, client: TestClient) -> None:
        """Should return a non-empty list."""
        resp = client.get("/api/customers/top")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_custom_n(self, client: TestClient) -> None:
        """n parameter should limit the number of results."""
        assert len(client.get("/api/customers/top?n=3").json()) <= 3

    def test_sorted_descending(self, client: TestClient) -> None:
        """Results should be sorted by total_amount descending."""
        data = client.get("/api/customers/top").json()
        amounts = [c["total_amount"] for c in data]
        assert amounts == sorted(amounts, reverse=True)


# ---------------------------------------------------------------------------
# Routes 19-20 : System
# ---------------------------------------------------------------------------

class TestHealth:
    """Tests for GET /api/system/health (Route 19)."""

    def test_returns_200(self, client: TestClient) -> None:
        """Should return 200."""
        assert client.get("/api/system/health").status_code == 200

    def test_status_field(self, client: TestClient) -> None:
        """status should be ok when dataset is loaded."""
        data = client.get("/api/system/health").json()
        assert data["status"] == "ok"

    def test_dataset_loaded(self, client: TestClient) -> None:
        """dataset_loaded should be True with injected data."""
        data = client.get("/api/system/health").json()
        assert data["dataset_loaded"] is True

    def test_uptime_format(self, client: TestClient) -> None:
        """uptime should be a non-empty string."""
        data = client.get("/api/system/health").json()
        assert isinstance(data["uptime"], str)
        assert len(data["uptime"]) > 0


class TestMetadata:
    """Tests for GET /api/system/metadata (Route 20)."""

    def test_returns_200(self, client: TestClient) -> None:
        """Should return 200."""
        assert client.get("/api/system/metadata").status_code == 200

    def test_version_present(self, client: TestClient) -> None:
        """version field should be present."""
        data = client.get("/api/system/metadata").json()
        assert data["version"] == "1.0.0"

    def test_last_update_format(self, client: TestClient) -> None:
        """last_update should end with Z."""
        data = client.get("/api/system/metadata").json()
        assert data["last_update"].endswith("Z")

    def test_total_records(self, client: TestClient) -> None:
        """total_records should equal sample size."""
        data = client.get("/api/system/metadata").json()
        assert data["total_records"] == 10
