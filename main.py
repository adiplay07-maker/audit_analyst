"""
main.py
-------
CLI entry point for the Audit Analytics Pipeline.

Usage:
    python main.py
    python main.py --method iqr --threshold 2.5 --group vendor
"""

import argparse
import sys
from pathlib import Path

# Allow running from project root
sys.path.insert(0, str(Path(__file__).parent))

from src.data_loader import load_data
from src.anomaly_detector import AnomalyDetector
from src.risk_scorer import RiskScorer
from src.report_generator import ReportGenerator


def parse_args():
    p = argparse.ArgumentParser(description="Audit Analytics Pipeline")
    p.add_argument("--method",    default="zscore", choices=["zscore", "iqr", "both"],
                   help="Anomaly detection method (default: zscore)")
    p.add_argument("--threshold", default=3.0, type=float,
                   help="Z-score threshold (default: 3.0)")
    p.add_argument("--group",     default="department",
                   help="Column to group by for risk scoring (default: department)")
    p.add_argument("--data-dir",  default="data",
                   help="Directory containing input CSVs (default: data/)")
    p.add_argument("--no-report", action="store_true",
                   help="Skip HTML report generation")
    return p.parse_args()


def run_pipeline(method="zscore", threshold=3.0, group="department",
                 data_dir="data", generate_report=True):

    print("\n🔄 Starting Audit Analytics Pipeline...\n")

    # 1. Load data
    transactions, gl_entries = load_data(data_dir)

    # 2. Detect anomalies
    detector = AnomalyDetector(threshold=threshold)

    outlier_result   = detector.detect(transactions, method=method, group_by=group)
    duplicate_result = detector.detect_duplicates(transactions)
    round_result     = detector.detect_round_amounts(transactions)

    print(f"\n{outlier_result.summary()}")
    print(f"[Duplicates]  Found {len(duplicate_result)} duplicate transactions")
    print(f"[Round Amts]  Found {len(round_result)} suspiciously round amounts")

    # 3. Score risk
    scorer = RiskScorer(group_col=group)
    risk_df = scorer.compute(
        transactions=transactions,
        flagged_df=outlier_result.flagged_df,
        duplicate_df=duplicate_result,
        round_df=round_result,
    )

    # 4. Print text summary
    reporter = ReportGenerator()
    reporter.generate_text_summary(risk_df, outlier_result.flagged_count, outlier_result.total_count)

    # 5. Generate HTML report
    if generate_report:
        report_path = reporter.generate_html(
            risk_df=risk_df,
            anomaly_df=outlier_result.flagged_df,
            transactions=transactions,
        )
        print(f"\n📄 Open your report: {report_path}\n")

    return {
        "transactions": transactions,
        "outliers": outlier_result.flagged_df,
        "risk_matrix": risk_df,
    }


if __name__ == "__main__":
    args = parse_args()
    run_pipeline(
        method=args.method,
        threshold=args.threshold,
        group=args.group,
        data_dir=args.data_dir,
        generate_report=not args.no_report,
    )
