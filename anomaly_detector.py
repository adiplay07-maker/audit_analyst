"""
anomaly_detector.py
-------------------
Detects financial anomalies in transaction data using statistical methods.
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import Literal


@dataclass
class AnomalyResult:
    method: str
    flagged_count: int
    total_count: int
    flagged_df: pd.DataFrame = field(repr=False)

    @property
    def flag_rate(self) -> float:
        return round(self.flagged_count / self.total_count * 100, 2)

    def summary(self) -> str:
        return (
            f"[{self.method}] Flagged {self.flagged_count} / {self.total_count} "
            f"transactions ({self.flag_rate}%)"
        )


class AnomalyDetector:
    """
    Detects outlier transactions using configurable statistical methods.

    Supported methods:
        - 'zscore'  : flags transactions beyond `threshold` standard deviations
        - 'iqr'     : flags transactions beyond IQR fence
        - 'both'    : applies both and takes the union
    """

    def __init__(self, threshold: float = 3.0):
        self.threshold = threshold

    def detect(
        self,
        df: pd.DataFrame,
        amount_col: str = "amount",
        method: Literal["zscore", "iqr", "both"] = "zscore",
        group_by: str | None = "department",
    ) -> AnomalyResult:
        """
        Detect anomalies in transaction amounts.

        Args:
            df:          DataFrame containing transactions
            amount_col:  Column name for transaction amounts
            method:      Detection algorithm to use
            group_by:    If set, anomaly detection is applied per group

        Returns:
            AnomalyResult with flagged transactions
        """
        df = df.copy()
        df["_anomaly"] = False

        if group_by and group_by in df.columns:
            for _, group in df.groupby(group_by):
                idx = group.index
                flags = self._apply_method(group[amount_col], method)
                df.loc[idx, "_anomaly"] = flags
        else:
            df["_anomaly"] = self._apply_method(df[amount_col], method)

        flagged = df[df["_anomaly"]].drop(columns=["_anomaly"])
        return AnomalyResult(
            method=method,
            flagged_count=len(flagged),
            total_count=len(df),
            flagged_df=flagged,
        )

    def _apply_method(self, series: pd.Series, method: str) -> pd.Series:
        flags = pd.Series(False, index=series.index)

        if method in ("zscore", "both"):
            mean, std = series.mean(), series.std()
            if std > 0:
                z = (series - mean).abs() / std
                flags |= z > self.threshold

        if method in ("iqr", "both"):
            q1, q3 = series.quantile(0.25), series.quantile(0.75)
            iqr = q3 - q1
            lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            flags |= (series < lower) | (series > upper)

        return flags

    def detect_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Flag duplicate transactions (same vendor, amount, date)."""
        key_cols = [c for c in ["date", "vendor", "amount"] if c in df.columns]
        dupes = df[df.duplicated(subset=key_cols, keep=False)].copy()
        dupes["_duplicate_flag"] = True
        return dupes

    def detect_round_amounts(
        self, df: pd.DataFrame, amount_col: str = "amount", threshold: float = 1000.0
    ) -> pd.DataFrame:
        """Flag suspiciously round amounts (potential fictitious transactions)."""
        mask = (df[amount_col] % threshold == 0) & (df[amount_col] >= threshold)
        return df[mask].copy()
