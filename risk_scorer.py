"""
risk_scorer.py
--------------
Assigns risk scores and levels to business units / departments
based on transaction patterns and anomaly rates.
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass


RISK_BANDS = [
    (0,  25,  "Low",      "🟢"),
    (25, 50,  "Medium",   "🟡"),
    (50, 75,  "High",     "🟠"),
    (75, 100, "Critical", "🔴"),
]


@dataclass
class RiskScore:
    entity: str
    score: float          # 0-100
    level: str            # Low / Medium / High / Critical
    icon: str
    drivers: dict         # contributing factors


def classify_risk(score: float) -> tuple[str, str]:
    for low, high, level, icon in RISK_BANDS:
        if low <= score < high:
            return level, icon
    return "Critical", "🔴"


class RiskScorer:
    """
    Computes a composite risk score per department/entity.

    Scoring dimensions (weights configurable):
        - anomaly_rate      : % of flagged transactions          (40%)
        - avg_amount        : normalised average transaction size (25%)
        - duplicate_rate    : % duplicate transactions           (20%)
        - round_amount_rate : % suspiciously round amounts       (15%)
    """

    WEIGHTS = {
        "anomaly_rate":      0.40,
        "avg_amount":        0.25,
        "duplicate_rate":    0.20,
        "round_amount_rate": 0.15,
    }

    def __init__(self, group_col: str = "department"):
        self.group_col = group_col

    def compute(
        self,
        transactions: pd.DataFrame,
        flagged_df: pd.DataFrame,
        duplicate_df: pd.DataFrame,
        round_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Compute risk scores for each group (department/BU).

        Returns a DataFrame with columns:
            entity, transaction_count, anomaly_rate, avg_amount,
            duplicate_rate, round_amount_rate, raw_score, score, level, icon
        """
        groups = transactions[self.group_col].unique()
        records = []

        global_max_avg = transactions.groupby(self.group_col)["amount"].mean().max()

        for grp in groups:
            txns = transactions[transactions[self.group_col] == grp]
            n = len(txns)

            anomaly_count = len(flagged_df[flagged_df[self.group_col] == grp]) if self.group_col in flagged_df.columns else 0
            dup_count = len(duplicate_df[duplicate_df[self.group_col] == grp]) if self.group_col in duplicate_df.columns else 0
            round_count = len(round_df[round_df[self.group_col] == grp]) if self.group_col in round_df.columns else 0

            anomaly_rate = anomaly_count / n if n else 0
            avg_amount_norm = txns["amount"].mean() / global_max_avg if global_max_avg else 0
            duplicate_rate = dup_count / n if n else 0
            round_rate = round_count / n if n else 0

            raw_score = (
                self.WEIGHTS["anomaly_rate"]      * anomaly_rate      * 100 +
                self.WEIGHTS["avg_amount"]         * avg_amount_norm   * 100 +
                self.WEIGHTS["duplicate_rate"]     * duplicate_rate    * 100 +
                self.WEIGHTS["round_amount_rate"]  * round_rate        * 100
            )
            score = min(round(raw_score, 2), 100)
            level, icon = classify_risk(score)

            records.append({
                "entity":            grp,
                "transaction_count": n,
                "anomaly_count":     anomaly_count,
                "anomaly_rate_%":    round(anomaly_rate * 100, 2),
                "avg_amount":        round(txns["amount"].mean(), 2),
                "duplicate_count":   dup_count,
                "duplicate_rate_%":  round(duplicate_rate * 100, 2),
                "round_amt_count":   round_count,
                "round_rate_%":      round(round_rate * 100, 2),
                "risk_score":        score,
                "risk_level":        level,
                "risk_icon":         icon,
            })

        result = pd.DataFrame(records).sort_values("risk_score", ascending=False).reset_index(drop=True)
        return result

    def top_risks(self, risk_df: pd.DataFrame, n: int = 3) -> pd.DataFrame:
        """Return the top-n highest risk entities."""
        return risk_df.head(n)
