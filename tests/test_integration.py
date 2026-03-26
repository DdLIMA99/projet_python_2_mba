"""Tests de performance, integration et validation des donnees."""

import time

from fastapi.testclient import TestClient


class TestPerformance:
    """Tests de performance de l API."""

    def test_large_pagination_limit_performance(
        self, client: TestClient
    ) -> None:
        """Test la performance avec un grand nombre de resultats."""
        start = time.time()
        response = client.get("/api/transactions?limit=100")
        elapsed = time.time() - start
        assert response.status_code == 200
        assert elapsed < 5.0

    def test_search_performance(
        self, client: TestClient
    ) -> None:
        """Test la performance d une recherche."""
        start = time.time()
        response = client.post(
            "/api/transactions/search",
            json={
                "use_chip": "Online Transaction",
                "isFraud": 1,
                "amount_range": [100.0, 50000.0],
            },
        )
        elapsed = time.time() - start
        assert response.status_code == 200
        assert elapsed < 5.0

    def test_stats_overview_performance(
        self, client: TestClient
    ) -> None:
        """Test la performance du calcul des statistiques."""
        start = time.time()
        response = client.get("/api/stats/overview")
        elapsed = time.time() - start
        assert response.status_code == 200
        assert elapsed < 5.0

    def test_multiple_requests_sequential(
        self, client: TestClient
    ) -> None:
        """Test que plusieurs requetes sequentielles fonctionnent."""
        for i in range(5):
            resp = client.get(
                f"/api/transactions?page={i + 1}&limit=2"
            )
            assert resp.status_code == 200


class TestIntegration:
    """Tests d integration cross-endpoints."""

    def test_transaction_consistency_between_endpoints(
        self, client: TestClient
    ) -> None:
        """Test la coherence entre pagination et detail."""
        paginated = client.get("/api/transactions?limit=10").json()
        if paginated["transactions"]:
            tx_id = paginated["transactions"][0]["id"]
            resp = client.get(f"/api/transactions/{tx_id}")
            assert resp.status_code == 200
            assert resp.json()["id"] == tx_id

    def test_customer_profile_from_list(
        self, client: TestClient
    ) -> None:
        """Coherence entre liste clients et profil client."""
        customers = client.get(
            "/api/customers?limit=1"
        ).json()["customers"]
        if customers:
            resp = client.get(f"/api/customers/{customers[0]}")
            assert resp.status_code in [200, 404]

    def test_stats_consistency_across_calls(
        self, client: TestClient
    ) -> None:
        """Test que les statistiques restent coherentes."""
        r1 = client.get("/api/stats/overview").json()
        r2 = client.get("/api/stats/overview").json()
        assert (
            r1["total_transactions"] == r2["total_transactions"]
        )
        assert r1["fraud_rate"] == r2["fraud_rate"]

    def test_fraud_predictions_valid(
        self, client: TestClient
    ) -> None:
        """Test que les predictions de fraude sont valides."""
        for chip in [
            "Swipe Transaction",
            "Chip Transaction",
            "Online Transaction",
        ]:
            resp = client.post(
                "/api/fraud/predict",
                json={"use_chip": chip, "amount": 500.0},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert isinstance(data["isFraud"], bool)
            assert 0 <= data["probability"] <= 1

    def test_delete_then_not_in_list(
        self, client: TestClient
    ) -> None:
        """Transaction supprimee ne doit plus apparaitre."""
        client.delete("/api/transactions/tx_005")
        resp = client.get("/api/transactions/tx_005")
        assert resp.status_code == 404


class TestDataValidation:
    """Tests de validation des donnees retournees."""

    def test_transaction_data_types(
        self, client: TestClient
    ) -> None:
        """Test que les types de donnees sont corrects."""
        data = client.get("/api/transactions?limit=5").json()
        assert isinstance(data["page"], int)
        assert isinstance(data["limit"], int)
        assert isinstance(data["total"], int)
        assert isinstance(data["transactions"], list)
        for tx in data["transactions"]:
            assert isinstance(tx["id"], str)
            assert isinstance(tx["amount"], (int, float))
            assert isinstance(tx["use_chip"], str)
            assert isinstance(tx["isFraud"], int)

    def test_stats_data_types(
        self, client: TestClient
    ) -> None:
        """Test les types pour les stats."""
        data = client.get("/api/stats/overview").json()
        assert isinstance(data["total_transactions"], int)
        assert isinstance(data["fraud_rate"], float)
        assert isinstance(data["avg_amount"], (int, float))
        assert isinstance(data["most_common_type"], str)

    def test_fraud_prediction_data_types(
        self, client: TestClient
    ) -> None:
        """Test les types des predictions."""
        data = client.post(
            "/api/fraud/predict",
            json={
                "use_chip": "Chip Transaction",
                "amount": 100.0,
            },
        ).json()
        assert isinstance(data["isFraud"], bool)
        assert isinstance(data["probability"], float)
        assert 0 <= data["probability"] <= 1

    def test_customer_data_types(
        self, client: TestClient
    ) -> None:
        """Test les types pour les clients."""
        data = client.get("/api/customers?limit=5").json()
        assert isinstance(data["page"], int)
        assert isinstance(data["total"], int)
        assert isinstance(data["customers"], list)
        for c in data["customers"]:
            assert isinstance(c, str)

    def test_amount_distribution_data_types(
        self, client: TestClient
    ) -> None:
        """Test les types de la distribution."""
        data = client.get(
            "/api/stats/amount-distribution"
        ).json()
        assert isinstance(data["bins"], list)
        assert isinstance(data["counts"], list)
        assert len(data["bins"]) == len(data["counts"])
        for count in data["counts"]:
            assert isinstance(count, int)


class TestErrorHandling:
    """Tests de gestion des erreurs."""

    def test_404_for_nonexistent_transaction(
        self, client: TestClient
    ) -> None:
        """Test 404 pour transaction inexistante."""
        assert (
            client.get(
                "/api/transactions/tx_BADID"
            ).status_code == 404
        )

    def test_404_for_nonexistent_customer(
        self, client: TestClient
    ) -> None:
        """Test 404 pour client inexistant."""
        assert (
            client.get(
                "/api/customers/NONEXISTENT_CUSTOMER"
            ).status_code == 404
        )

    def test_422_for_invalid_query_parameters(
        self, client: TestClient
    ) -> None:
        """Test 422 pour parametres invalides."""
        assert (
            client.get(
                "/api/transactions?limit=abc"
            ).status_code == 422
        )

    def test_404_for_delete_nonexistent(
        self, client: TestClient
    ) -> None:
        """Test 404 pour suppression inexistante."""
        assert (
            client.delete(
                "/api/transactions/tx_BADID"
            ).status_code == 404
        )

    def test_unknown_fields_ignored(
        self, client: TestClient
    ) -> None:
        """Test que les champs inconnus sont ignores."""
        resp = client.post(
            "/api/transactions/search",
            json={"unknown_field": "value"},
        )
        assert resp.status_code == 200
