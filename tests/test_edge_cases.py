"""Tests des cas limites et cas exceptionnels pour l'API Banking."""

from fastapi.testclient import TestClient


class TestTransactionEdgeCases:
    """Tests des cas limites pour les transactions."""

    def test_get_transactions_invalid_page_negative(
        self, client: TestClient
    ) -> None:
        """Test avec un numéro de page négatif."""
        response = client.get("/api/transactions?page=-1")
        assert response.status_code == 422

    def test_get_transactions_invalid_limit_zero(
        self, client: TestClient
    ) -> None:
        """Test avec une limite de 0."""
        response = client.get("/api/transactions?limit=0")
        assert response.status_code == 422

    def test_get_transactions_limit_exceeds_max(
        self, client: TestClient
    ) -> None:
        """Test avec une limite supérieure à 100."""
        response = client.get("/api/transactions?limit=200")
        assert response.status_code == 422

    def test_get_transactions_with_invalid_type(
        self, client: TestClient
    ) -> None:
        """Test avec un type inexistant."""
        response = client.get("/api/transactions?type=INVALID_TYPE")
        assert response.status_code == 200
        assert response.json()["transactions"] == []

    def test_search_with_empty_criteria(
        self, client: TestClient
    ) -> None:
        """Test de recherche avec aucun critère."""
        response = client.post("/api/transactions/search", json={})
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_search_with_invalid_amount_range_size(
        self, client: TestClient
    ) -> None:
        """Test avec une plage de montants à un seul élément."""
        response = client.post(
            "/api/transactions/search",
            json={"amount_range": [1000.0]},
        )
        assert response.status_code in [200, 422]

    def test_get_recent_transactions_n_exceeds_limit(
        self, client: TestClient
    ) -> None:
        """Test avec N supérieur à 1000."""
        response = client.get("/api/transactions/recent?n=2000")
        assert response.status_code == 422

    def test_get_recent_transactions_n_zero(
        self, client: TestClient
    ) -> None:
        """Test avec N = 0."""
        response = client.get("/api/transactions/recent?n=0")
        assert response.status_code == 422

    def test_get_transaction_unknown_id(
        self, client: TestClient
    ) -> None:
        """Test avec un ID inexistant."""
        response = client.get("/api/transactions/tx_BADID")
        assert response.status_code == 404

    def test_delete_multiple_times_same_transaction(
        self, client: TestClient
    ) -> None:
        """Test la suppression répétée de la même transaction."""
        response1 = client.delete("/api/transactions/tx_001")
        response2 = client.delete("/api/transactions/tx_001")
        assert response1.status_code == 200
        assert response2.status_code == 404

    def test_transaction_after_deletion_not_visible(
        self, client: TestClient
    ) -> None:
        """Transaction supprimée n'apparaît plus dans la pagination."""
        before = client.get(
            "/api/transactions?page=1&limit=10"
        ).json()["total"]
        client.delete("/api/transactions/tx_002")
        after = client.get(
            "/api/transactions?page=1&limit=10"
        ).json()["total"]
        assert after < before


class TestTransactionsByCustomerEdgeCases:
    """Tests des cas limites pour les transactions par client."""

    def test_get_transactions_nonexistent_customer(
        self, client: TestClient
    ) -> None:
        """Test avec un client inexistant."""
        response = client.get(
            "/api/transactions/by-customer/NONEXISTENT"
        )
        assert response.status_code == 200
        assert response.json()["total"] == 0

    def test_get_transactions_nonexistent_merchant(
        self, client: TestClient
    ) -> None:
        """Test avec un marchand inexistant."""
        response = client.get(
            "/api/transactions/to-customer/NONEXISTENT"
        )
        assert response.status_code == 200
        assert response.json()["total"] == 0


class TestStatsEdgeCases:
    """Tests des cas limites pour les statistiques."""

    def test_stats_overview_values_validity(
        self, client: TestClient
    ) -> None:
        """Test la validité des valeurs statistiques."""
        data = client.get("/api/stats/overview").json()
        assert data["total_transactions"] > 0
        assert 0 <= data["fraud_rate"] <= 1
        assert data["avg_amount"] >= 0

    def test_amount_distribution_consistency(
        self, client: TestClient
    ) -> None:
        """Test la cohérence entre bins et counts."""
        data = client.get("/api/stats/amount-distribution").json()
        assert len(data["bins"]) == len(data["counts"])
        assert len(data["bins"]) > 0

    def test_amount_distribution_counts_non_negative(
        self, client: TestClient
    ) -> None:
        """Test que tous les counts sont non négatifs."""
        data = client.get("/api/stats/amount-distribution").json()
        for count in data["counts"]:
            assert count >= 0

    def test_stats_by_type_all_types_have_data(
        self, client: TestClient
    ) -> None:
        """Test que chaque type a au moins une transaction."""
        data = client.get("/api/stats/by-type").json()
        for item in data:
            assert item["count"] > 0
            assert item["avg_amount"] >= 0

    def test_daily_stats_dates_ordered(
        self, client: TestClient
    ) -> None:
        """Test que les dates sont correctement ordonnées."""
        data = client.get("/api/stats/daily").json()
        if len(data) > 1:
            dates = [item["date"] for item in data]
            assert dates == sorted(dates)

    def test_daily_stats_counts_positive(
        self, client: TestClient
    ) -> None:
        """Test que les counts journaliers sont positifs."""
        data = client.get("/api/stats/daily").json()
        for item in data:
            assert item["count"] > 0


class TestFraudEdgeCases:
    """Tests des cas limites pour la détection de fraude."""

    def test_fraud_summary_values_validity(
        self, client: TestClient
    ) -> None:
        """Test la validité des valeurs de fraude."""
        data = client.get("/api/fraud/summary").json()
        assert data["total_frauds"] >= 0
        assert 0 <= data["precision"] <= 1
        assert 0 <= data["recall"] <= 1

    def test_predict_fraud_all_chip_types(
        self, client: TestClient
    ) -> None:
        """Test la prédiction avec tous les types réels."""
        for chip in [
            "Swipe Transaction",
            "Chip Transaction",
            "Online Transaction",
        ]:
            resp = client.post(
                "/api/fraud/predict",
                json={"use_chip": chip, "amount": 1000.0},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert "isFraud" in data
            assert 0 <= data["probability"] <= 1

    def test_predict_fraud_invalid_amount(
        self, client: TestClient
    ) -> None:
        """Test la prédiction avec montant négatif."""
        resp = client.post(
            "/api/fraud/predict",
            json={"use_chip": "Online Transaction", "amount": -10.0},
        )
        assert resp.status_code == 422

    def test_fraud_by_type_structure(
        self, client: TestClient
    ) -> None:
        """Test la structure des données de fraude par type."""
        for item in client.get("/api/fraud/by-type").json():
            assert "type" in item
            assert "fraud_rate" in item
            assert 0 <= item["fraud_rate"] <= 1


class TestCustomerEdgeCases:
    """Tests des cas limites pour les clients."""

    def test_get_customers_page_beyond_available(
        self, client: TestClient
    ) -> None:
        """Test pagination avec une page bien au-delà des disponibles."""
        response = client.get("/api/customers?page=99999&limit=10")
        assert response.status_code == 200
        assert response.json()["customers"] == []

    def test_get_customer_profile_not_found(
        self, client: TestClient
    ) -> None:
        """Test que les clients inexistants retournent 404."""
        assert (
            client.get(
                "/api/customers/DOESNOTEXIST"
            ).status_code == 404
        )

    def test_get_top_customers_n_zero(
        self, client: TestClient
    ) -> None:
        """Test top customers avec N = 0."""
        assert (
            client.get("/api/customers/top?n=0").status_code == 422
        )

    def test_get_top_customers_n_negative(
        self, client: TestClient
    ) -> None:
        """Test top customers avec N négatif."""
        assert (
            client.get("/api/customers/top?n=-5").status_code == 422
        )


class TestSystemEdgeCases:
    """Tests des cas limites pour les routes système."""

    def test_health_check_response_structure(
        self, client: TestClient
    ) -> None:
        """Test la structure du health check."""
        data = client.get("/api/system/health").json()
        assert "status" in data
        assert data["status"] == "ok"

    def test_metadata_response_structure(
        self, client: TestClient
    ) -> None:
        """Test la structure des métadonnées."""
        data = client.get("/api/system/metadata").json()
        assert "version" in data

    def test_multiple_health_checks(
        self, client: TestClient
    ) -> None:
        """Test plusieurs health checks consécutifs."""
        for _ in range(5):
            resp = client.get("/api/system/health")
            assert resp.status_code == 200
            assert resp.json()["status"] == "ok"


class TestRobustness:
    """Tests de robustesse."""

    def test_concurrent_deletes_same_transaction(
        self, client: TestClient
    ) -> None:
        """Test que les suppressions multiples sont gérées."""
        r1 = client.delete("/api/transactions/tx_003")
        r2 = client.delete("/api/transactions/tx_003")
        assert r1.status_code == 200
        assert r2.status_code == 404

    def test_filter_type_case_sensitive(
        self, client: TestClient
    ) -> None:
        """Test que le type est sensible à la casse."""
        data = client.get(
            "/api/transactions?type=swipe+transaction"
        ).json()
        assert data["transactions"] == []

    def test_filter_returns_zero_results(
        self, client: TestClient
    ) -> None:
        """Test un filtre qui ne retourne aucun résultat."""
        data = client.get(
            "/api/transactions?type=NONEXISTENT_TYPE"
        ).json()
        assert data["transactions"] == []
        assert data["total"] == 0

    def test_pagination_no_overlap(
        self, client: TestClient
    ) -> None:
        """Les deux pages ne doivent pas avoir d'intersection."""
        ids1 = [
            tx["id"] for tx in client.get(
                "/api/transactions?page=1&limit=3"
            ).json()["transactions"]
        ]
        ids2 = [
            tx["id"] for tx in client.get(
                "/api/transactions?page=2&limit=3"
            ).json()["transactions"]
        ]
        assert len(set(ids1).intersection(set(ids2))) == 0

    def test_single_transaction_limit(
        self, client: TestClient
    ) -> None:
        """Test la pagination avec limit=1."""
        data = client.get("/api/transactions?limit=1").json()
        assert len(data["transactions"]) <= 1

    def test_max_page_number_empty(
        self, client: TestClient
    ) -> None:
        """Test avec un numéro de page très élevé."""
        data = client.get(
            "/api/transactions?page=10000&limit=10"
        ).json()
        assert data["page"] == 10000
        assert data["transactions"] == []

    def test_404_detail_present(
        self, client: TestClient
    ) -> None:
        """Test que les erreurs 404 contiennent un champ detail."""
        data = client.get("/api/transactions/tx_BADID").json()
        assert "detail" in data

    def test_422_for_invalid_query_param(
        self, client: TestClient
    ) -> None:
        """Test que 422 est retourné pour des paramètres invalides."""
        assert (
            client.get(
                "/api/transactions?limit=abc"
            ).status_code == 422
        )
