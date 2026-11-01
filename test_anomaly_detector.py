"""
test_anomaly_detector.py
------------------------
Unit tests for the AnomalyDetector module.

Run with:
    pytest tests/ -v
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import pandas as pd
import numpy as np

from src.anomaly_detector import AnomalyDetector
from src.data_loader import generate_sample_transactions


@pytest.fixture
def sample_df():
    return generate_sample_transactions(n=200, seed=0)


@pytest.fixture
def simple_df():
    """Small, deterministic dataset for precise assertions."""
    amounts = [100, 110, 95, 105, 99, 108, 102, 10_000]  # last is clear outlier
    return pd.DataFrame({
        "transaction_id": [f"T{i}" for i in range(len(amounts))],
        "date": pd.date_range("2024-01-01", periods=len(amounts)),
        "department": ["Finance"] * len(amounts),
        "vendor": ["VendorA"] * len(amounts),
        "amount": amounts,
    })


class TestAnomalyDetector:

    def test_zscore_flags_outlier(self, simple_df):
        detector = AnomalyDetector(threshold=2.0)
        result = detector.detect(simple_df, method="zscore", group_by=None)
        assert result.flagged_count >= 1
        # The ₹10,000 outlier should be caught
        assert 10_000 in result.flagged_df["amount"].values

    def test_iqr_flags_outlier(self, simple_df):
        detector = AnomalyDetector()
        result = detector.detect(simple_df, method="iqr", group_by=None)
        assert result.flagged_count >= 1

    def test_both_method(self, simple_df):
        detector = AnomalyDetector()
        result = detector.detect(simple_df, method="both", group_by=None)
        assert result.flagged_count >= 1

    def test_flag_rate_within_bounds(self, sample_df):
        detector = AnomalyDetector(threshold=3.0)
        result = detector.detect(sample_df, method="zscore", group_by="department")
        assert 0 <= result.flag_rate <= 100

    def test_flagged_df_subset_of_original(self, sample_df):
        detector = AnomalyDetector()
        result = detector.detect(sample_df, method="zscore")
        assert set(result.flagged_df.index).issubset(set(sample_df.index))

    def test_no_group_by(self, sample_df):
        detector = AnomalyDetector()
        result = detector.detect(sample_df, method="zscore", group_by=None)
        assert result.flagged_count >= 0

    def test_duplicate_detection(self):
        df = pd.DataFrame({
            "date": ["2024-01-01", "2024-01-01", "2024-01-02"],
            "vendor": ["A", "A", "B"],
            "amount": [100.0, 100.0, 200.0],
            "department": ["Finance", "Finance", "IT"],
        })
        detector = AnomalyDetector()
        dupes = detector.detect_duplicates(df)
        assert len(dupes) == 2

    def test_round_amount_detection(self):
        df = pd.DataFrame({
            "amount": [1000.0, 5000.0, 1234.56, 250.0, 10_000.0],
            "department": ["Finance"] * 5,
        })
        detector = AnomalyDetector()
        rounds = detector.detect_round_amounts(df, threshold=1000.0)
        assert 1000.0 in rounds["amount"].values
        assert 5000.0 in rounds["amount"].values
        assert 1234.56 not in rounds["amount"].values

    def test_anomaly_result_summary_string(self, simple_df):
        detector = AnomalyDetector()
        result = detector.detect(simple_df, method="zscore", group_by=None)
        summary = result.summary()
        assert "zscore" in summary
        assert "%" in summary
