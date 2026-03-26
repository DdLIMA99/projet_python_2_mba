"""Pytest unit tests for service layer functions."""

import pandas as pd
import pytest

from banking_api.services import data_loader
from banking_api.services import transactions_service
from banking_api.services import stats_service
from banking_api.services import fraud_detection_service
from banking_api.services import customer_service
from banking_api.services import system_service
from banking_api.models.schemas import (
    FraudPredictRequest,
    TransactionSearchRequest,
)


class TestTransactionsService:
    """Unit tests for transactions_service module."""

    def test_get_transactions_default(self) -> None:
        """Default pagination returns page 1 with 10 results."""
        result = transactions_service.get_transactions()
        assert result.page == 1
        assert len(result.transactions) == 10

    def test_get_transactions_filter_type(self) -> None:
        """Filtering by type returns only matching records."""
        result = transactions_service.get_transactions(
            type="Online Transaction"
        )
        for tx in result.transactions:
            assert tx.use_chip == "Online Transaction"

    def test_get_transactions_filter_fraud(self) -> None:
        """Filtering by isFraud=1 returns fraudulent records."""
        result = transactions_service.get_transactions(isFraud=1)
        for tx in result.transactions:
            assert tx.isFraud == 1

    def test_get_transaction_by_id_found(self) -> None:
        """Known ID returns a TransactionItem."""
        tx = transactions_service.get_transaction_by_id("tx_001")
        assert tx is not None
        assert tx.id == "tx_001"

    def test_get_transaction_by_id_not_found(self) -> None:
        """Unknown ID returns None."""
        assert transactions_service.get_transaction_by_id(
            "tx_BADID"
        ) is None

    def test_search_by_client_id(self) -> None:
        """Search by client_id filters correctly."""
        criteria = TransactionSearchRequest(client_id="C200")
        results = transactions_service.search_transactions(criteria)
        for tx in results:
            assert tx.client_id == "C200"

    def test_search_empty_criteria(self) -> None:
        """Empty search returns all transactions."""
        results = transactions_service.search_transactions(
            TransactionSearchRequest()
        )
        assert len(results) == 10

    def test_get_transaction_types(self) -> None:
        """Types list is non-empty and sorted."""
        types = transactions_service.get_transaction_types()
        assert len(types) > 0
        assert types == sorted(types)

    def test_get_recent_transactions(self) -> None:
        """Recent transactions returns at most n items."""
        results = transactions_service.get_recent_transactions(n=5)
        assert len(results) == 5

    def test_delete_transaction_exists(self) -> None:
        """Deleting an existing transaction returns True."""
        assert transactions_service.delete_transaction(
            "tx_001"
        ) is True

    def test_delete_transaction_not_found(self) -> None:
        """Deleting a missing transaction returns False."""
        assert transactions_service.delete_transaction(
            "tx_BADID"
        ) is False

    def test_delete_already_deleted(self) -> None:
        """Deleting the same transaction twice returns False."""
        transactions_service.delete_transaction("tx_003")
        assert transactions_service.delete_transaction(
            "tx_003"
        ) is False

    def test_get_transactions_by_customer(self) -> None:
        """Customer transactions filtered by client_id."""
        result = transactions_service.get_transactions_by_customer(
            "C100"
        )
        assert result.total > 0
        for tx in result.transactions:
            assert tx.client_id == "C100"

    def test_get_transactions_to_customer(self) -> None:
        """Transactions to merchant filtered by merchant_id."""
        result = transactions_service.get_transactions_to_customer(
            "M001"
        )
        assert result.total > 0
        for tx in result.transactions:
            assert tx.merchant_id == "M001"


class TestStatsService:
    """Unit tests for stats_service module."""

    def test_overview_total(self) -> None:
        """Total transactions matches sample size."""
        assert stats_service.get_overview().total_transactions == 10

    def test_overview_fraud_rate(self) -> None:
        """Fraud rate is between 0 and 1."""
        rate = stats_service.get_overview().fraud_rate
        assert 0.0 <= rate <= 1.0

    def test_overview_avg_amount_positive(self) -> None:
        """Average amount is positive."""
        assert stats_service.get_overview().avg_amount > 0

    def test_overview_most_common_type(self) -> None:
        """Most common type is a non-empty string."""
        t = stats_service.get_overview().most_common_type
        assert isinstance(t, str) and len(t) > 0

    def test_amount_distribution_length(self) -> None:
        """bins and counts have equal length."""
        dist = stats_service.get_amount_distribution(num_bins=4)
        assert len(dist.bins) == 4
        assert len(dist.counts) == 4

    def test_amount_distribution_sum(self) -> None:
        """Sum of counts equals total transactions."""
        dist = stats_service.get_amount_distribution(num_bins=8)
        assert sum(dist.counts) == 10

    def test_stats_by_type_non_empty(self) -> None:
        """Stats by type returns non-empty list."""
        assert len(stats_service.get_stats_by_type()) > 0

    def test_stats_by_type_counts_positive(self) -> None:
        """All type counts should be positive."""
        for item in stats_service.get_stats_by_type():
            assert item.count > 0

    def test_daily_stats_non_empty(self) -> None:
        """Daily stats returns non-empty list."""
        assert len(stats_service.get_daily_stats()) > 0

    def test_daily_stats_sorted(self) -> None:
        """Daily stats should be ordered by date."""
        result = stats_service.get_daily_stats()
        dates = [s.date for s in result]
        assert dates == sorted(dates)


class TestFraudDetectionService:
    """Unit tests for fraud_detection_service module."""

    def test_fraud_summary_fields(self) -> None:
        """Fraud summary contains all expected fields."""
        summary = fraud_detection_service.get_fraud_summary()
        assert summary.total_frauds == 3
        assert summary.flagged >= 0
        assert 0.0 <= summary.precision <= 1.0
        assert 0.0 <= summary.recall <= 1.0

    def test_fraud_by_type_non_empty(self) -> None:
        """Fraud by type returns entries for each method."""
        assert len(fraud_detection_service.get_fraud_by_type()) > 0

    def test_fraud_by_type_rate_range(self) -> None:
        """All fraud rates are between 0 and 1."""
        for item in fraud_detection_service.get_fraud_by_type():
            assert 0.0 <= item.fraud_rate <= 1.0

    def test_predict_returns_response(self) -> None:
        """Predict returns a valid FraudPredictResponse."""
        req = FraudPredictRequest(
            use_chip="Online Transaction",
            amount=15000.0,
        )
        result = fraud_detection_service.predict_fraud(req)
        assert isinstance(result.isFraud, bool)
        assert 0.0 <= result.probability <= 1.0

    def test_predict_probability_range(self) -> None:
        """Probability score is always between 0 and 1."""
        req = FraudPredictRequest(
            use_chip="Chip Transaction",
            amount=100.0,
        )
        result = fraud_detection_service.predict_fraud(req)
        assert 0.0 <= result.probability <= 1.0


class TestCustomerService:
    """Unit tests for customer_service module."""

    def test_get_customers_pagination(self) -> None:
        """Pagination metadata is correct."""
        result = customer_service.get_customers(page=1, limit=5)
        assert result.page == 1
        assert len(result.customers) <= 5

    def test_get_customers_total(self) -> None:
        """Total unique customers matches sample data."""
        result = customer_service.get_customers()
        assert result.total == 7

    def test_get_customer_profile_found(self) -> None:
        """Profile for existing customer is returned."""
        profile = customer_service.get_customer_profile("C100")
        assert profile is not None
        assert profile.id == "C100"
        assert profile.transactions_count > 0

    def test_get_customer_profile_not_found(self) -> None:
        """Unknown customer returns None."""
        assert customer_service.get_customer_profile(
            "UNKNOWN"
        ) is None

    def test_get_top_customers_length(self) -> None:
        """Top customers list respects n parameter."""
        assert len(customer_service.get_top_customers(n=3)) <= 3

    def test_get_top_customers_sorted(self) -> None:
        """Top customers are sorted by total_amount descending."""
        result = customer_service.get_top_customers()
        amounts = [c.total_amount for c in result]
        assert amounts == sorted(amounts, reverse=True)


class TestSystemService:
    """Unit tests for system_service module."""

    def test_health_ok_when_loaded(self) -> None:
        """Health returns ok when data is loaded."""
        health = system_service.get_health()
        assert health.status == "ok"
        assert health.dataset_loaded is True

    def test_health_uptime_string(self) -> None:
        """Uptime is a non-empty string."""
        health = system_service.get_health()
        assert isinstance(health.uptime, str)
        assert len(health.uptime) > 0

    def test_metadata_version(self) -> None:
        """Version matches configured value."""
        assert system_service.get_metadata().version == "1.0.0"

    def test_metadata_last_update_iso(self) -> None:
        """Last update ends with Z."""
        assert system_service.get_metadata().last_update.endswith("Z")

    def test_metadata_total_records(self) -> None:
        """Total records matches sample size."""
        assert system_service.get_metadata().total_records == 10


class TestDataLoader:
    """Unit tests for data_loader module."""

    def test_get_data_returns_dataframe(self) -> None:
        """get_data returns a non-empty DataFrame."""
        df = data_loader.get_data()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 10

    def test_isfraud_column_derived(self) -> None:
        """isFraud column is derived from errors column."""
        df = data_loader.get_data()
        assert "isFraud" in df.columns

    def test_mark_deleted_excluded(self) -> None:
        """Marked IDs are excluded from get_data."""
        data_loader.mark_deleted("tx_001")
        df = data_loader.get_data()
        assert "tx_001" not in df["id"].values

    def test_is_deleted_true(self) -> None:
        """is_deleted returns True after marking."""
        data_loader.mark_deleted("tx_002")
        assert data_loader.is_deleted("tx_002") is True

    def test_is_deleted_false(self) -> None:
        """is_deleted returns False for unmarked ID."""
        assert data_loader.is_deleted("tx_003") is False

    def test_load_data_missing_file(self) -> None:
        """load_data raises FileNotFoundError for missing file."""
        data_loader.reset_data()
        with pytest.raises(FileNotFoundError):
            data_loader.load_data("/tmp/nonexistent_file.csv")
