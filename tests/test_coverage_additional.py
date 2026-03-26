"""
Tests supplémentaires pour améliorer la couverture globale.
Couvre les chemins de code manquants et les cas d'utilisation avancés.
"""

from fastapi.testclient import TestClient


class TestMainRoutesAdditional:
    """Tests supplémentaires pour les routes main.py non couvertes."""

    def test_get_transactions_with_all_filters(
        self, client: TestClient
    ) -> None:
        """Test avec tous les filtres à la fois."""
        response = client.get(
            "/api/transactions?page=1&limit=10"
            "&type=Chip+Transaction&isFraud=0"
            "&min_amount=100&max_amount=5000"
        )
        assert response.status_code == 200
        data = response.json()
        for tx in data["transactions"]:
            assert tx["use_chip"] == "Chip Transaction"
            assert tx["isFraud"] == 0
            assert 100 <= tx["amount"] <= 5000

    def test_search_transactions_with_type_only(
        self, client: TestClient
    ) -> None:
        """Recherche avec seulement le type."""
        response = client.post(
            "/api/transactions/search",
            json={"use_chip": "Chip Transaction"},
        )
        assert response.status_code == 200
        for tx in response.json():
            assert tx["use_chip"] == "Chip Transaction"

    def test_search_transactions_with_fraud_flag(
        self, client: TestClient
    ) -> None:
        """Recherche avec flag fraude."""
        response = client.post(
            "/api/transactions/search",
            json={"isFraud": 1},
        )
        assert response.status_code == 200

    def test_search_transactions_with_all_params(
        self, client: TestClient
    ) -> None:
        """Recherche avec tous les paramètres."""
        response = client.post(
            "/api/transactions/search",
            json={
                "use_chip": "Online Transaction",
                "isFraud": 1,
                "amount_range": [100.0, 50000.0],
            },
        )
        assert response.status_code == 200
        for tx in response.json():
            assert tx["use_chip"] == "Online Transaction"
            assert 100.0 <= tx["amount"] <= 50000.0

    def test_get_transactions_min_amount_only(
        self, client: TestClient
    ) -> None:
        """Test avec seulement min_amount."""
        response = client.get("/api/transactions?min_amount=200")
        assert response.status_code == 200
        for tx in response.json()["transactions"]:
            assert tx["amount"] >= 200

    def test_get_transactions_max_amount_only(
        self, client: TestClient
    ) -> None:
        """Test avec seulement max_amount."""
        response = client.get("/api/transactions?max_amount=5000")
        assert response.status_code == 200
        for tx in response.json()["transactions"]:
            assert tx["amount"] <= 5000

    def test_get_top_customers_various_n_values(
        self, client: TestClient
    ) -> None:
        """Test top customers avec différentes valeurs de N."""
        for n in [1, 3, 5]:
            response = client.get(f"/api/customers/top?n={n}")
            assert response.status_code == 200
            assert len(response.json()) <= n

    def test_health_check_multiple_times(
        self, client: TestClient
    ) -> None:
        """Test le health check plusieurs fois de suite."""
        for _ in range(3):
            response = client.get("/api/system/health")
            assert response.status_code == 200
            assert response.json()["status"] == "ok"

    def test_metadata_consistent(self, client: TestClient) -> None:
        """Test que les métadonnées sont cohérentes."""
        r1 = client.get("/api/system/metadata")
        r2 = client.get("/api/system/metadata")
        assert r1.status_code == 200
        assert r1.json() == r2.json()


class TestStatsRoutesAdditional:
    """Tests supplémentaires pour les routes statistiques."""

    def test_stats_overview_all_keys_present(
        self, client: TestClient
    ) -> None:
        """Test que toutes les clés sont présentes dans overview."""
        data = client.get("/api/stats/overview").json()
        for key in [
            "total_transactions", "fraud_rate",
            "avg_amount", "most_common_type",
        ]:
            assert key in data

    def test_amount_distribution_sums_correctly(
        self, client: TestClient
    ) -> None:
        """Test que la distribution des montants est cohérente."""
        data = client.get("/api/stats/amount-distribution").json()
        assert len(data["bins"]) == len(data["counts"])
        assert sum(data["counts"]) > 0

    def test_stats_by_type_contains_all_types(
        self, client: TestClient
    ) -> None:
        """Test que tous les types de transactions sont inclus."""
        all_types = set(
            client.get("/api/transactions/types").json()["types"]
        )
        stats_types = {
            item["type"]
            for item in client.get("/api/stats/by-type").json()
        }
        assert all_types == stats_types

    def test_daily_stats_non_zero_counts(
        self, client: TestClient
    ) -> None:
        """Test que tous les jours ont au moins une transaction."""
        data = client.get("/api/stats/daily").json()
        for item in data:
            assert item["count"] > 0


class TestFraudRoutesAdditional:
    """Tests supplémentaires pour les routes fraude."""

    def test_predict_fraud_all_chip_types(
        self, client: TestClient
    ) -> None:
        """Test la prédiction avec les vrais types du dataset."""
        for chip_type in [
            "Swipe Transaction",
            "Chip Transaction",
            "Online Transaction",
        ]:
            response = client.post(
                "/api/fraud/predict",
                json={
                    "use_chip": chip_type,
                    "amount": 1000.0,
                },
            )
            assert response.status_code == 200
            data = response.json()
            assert "isFraud" in data
            assert "probability" in data
            assert 0.0 <= data["probability"] <= 1.0

    def test_fraud_summary_complete(
        self, client: TestClient
    ) -> None:
        """Test que le résumé fraude contient tous les éléments."""
        data = client.get("/api/fraud/summary").json()
        for key in ["total_frauds", "flagged", "precision", "recall"]:
            assert key in data
            assert isinstance(data[key], (int, float))

    def test_fraud_by_type_includes_fraud_rates(
        self, client: TestClient
    ) -> None:
        """Test que les taux de fraude sont inclus."""
        for item in client.get("/api/fraud/by-type").json():
            assert "fraud_rate" in item
            assert 0 <= item["fraud_rate"] <= 1


class TestCustomerRoutesAdditional:
    """Tests supplémentaires pour les routes clients."""

    def test_get_customers_page_1_not_empty(
        self, client: TestClient
    ) -> None:
        """Test que la première page a des clients."""
        data = client.get("/api/customers?page=1&limit=10").json()
        assert len(data["customers"]) > 0

    def test_get_customers_pagination_total_accurate(
        self, client: TestClient
    ) -> None:
        """Test que le total est précis."""
        data = client.get("/api/customers?page=1&limit=1").json()
        assert data["total"] > 0
        assert data["page"] == 1
        assert data["limit"] == 1

    def test_get_customer_profile_structure(
        self, client: TestClient
    ) -> None:
        """Test la structure du profil client."""
        customers = client.get(
            "/api/customers?limit=1"
        ).json()["customers"]
        if customers:
            data = client.get(
                f"/api/customers/{customers[0]}"
            ).json()
            for key in [
                "id", "transactions_count", "avg_amount", "fraudulent"
            ]:
                assert key in data


class TestTransactionDetailsAdditional:
    """Tests supplémentaires pour les détails des transactions."""

    def test_get_transaction_by_id_structure(
        self, client: TestClient
    ) -> None:
        """Test la structure complète d'une transaction."""
        resp = client.get("/api/transactions/tx_001")
        assert resp.status_code == 200
        data = resp.json()
        assert "amount" in data
        assert "use_chip" in data
        assert "isFraud" in data
        assert isinstance(data["amount"], (int, float))
        assert isinstance(data["use_chip"], str)
        assert isinstance(data["isFraud"], int)

    def test_delete_returns_message(
        self, client: TestClient
    ) -> None:
        """Test que la suppression retourne un message."""
        response = client.delete("/api/transactions/tx_005")
        assert response.status_code == 200
        assert "message" in response.json()

    def test_transactions_by_customer_returns_paginated(
        self, client: TestClient
    ) -> None:
        """Test que les transactions par client retournent une réponse paginée."""
        customers = client.get(
            "/api/customers?limit=1"
        ).json()["customers"]
        if customers:
            data = client.get(
                f"/api/transactions/by-customer/{customers[0]}"
            ).json()
            for k in ["page", "total", "transactions"]:
                assert k in data


class TestPaginationAdvanced:
    """Tests avancés pour la pagination."""

    def test_pagination_no_overlap(
        self, client: TestClient
    ) -> None:
        """Les deux pages ne doivent pas avoir d'intersection."""
        ids1 = [
            tx["id"]
            for tx in client.get(
                "/api/transactions?page=1&limit=5"
            ).json()["transactions"]
        ]
        ids2 = [
            tx["id"]
            for tx in client.get(
                "/api/transactions?page=2&limit=5"
            ).json()["transactions"]
        ]
        assert len(set(ids1).intersection(set(ids2))) == 0
