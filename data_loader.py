"""
data_loader.py
--------------
Loads and validates input datasets for audit analysis.
"""

import pandas as pd
import numpy as np
from pathlib import Path


def generate_sample_transactions(n: int = 500, seed: int = 42) -> pd.DataFrame:
    """Generate synthetic transaction data for demonstration."""
    rng = np.random.default_rng(seed)

    departments = ["Finance", "Procurement", "HR", "IT", "Operations", "Marketing"]
    vendors = [f"Vendor_{chr(65+i)}" for i in range(12)]
    categories = ["Capex", "Opex", "Travel", "Utilities", "Consulting", "Maintenance"]

    df = pd.DataFrame({
        "transaction_id": [f"TXN{str(i).zfill(5)}" for i in range(1, n + 1)],
        "date": pd.date_range("2024-01-01", periods=n, freq="D").to_list()[:n],
        "department": rng.choice(departments, n),
        "vendor": rng.choice(vendors, n),
        "category": rng.choice(categories, n),
        "amount": np.concatenate([
            rng.normal(50_000, 15_000, int(n * 0.95)),  # normal transactions
            rng.normal(500_000, 100_000, int(n * 0.05))  # outlier injections
        ])[:n],
        "approved_by": rng.choice(["MGR001", "MGR002", "MGR003", "MGR004"], n),
        "payment_mode": rng.choice(["NEFT", "RTGS", "Cheque", "Card"], n),
    })

    # Ensure non-negative amounts
    df["amount"] = df["amount"].abs().round(2)
    df["date"] = pd.to_datetime(df["date"])
    return df


def generate_gl_entries(n: int = 300, seed: int = 7) -> pd.DataFrame:
    """Generate synthetic General Ledger entries."""
    rng = np.random.default_rng(seed)

    accounts = {
        "1001": "Cash & Equivalents",
        "1200": "Accounts Receivable",
        "2001": "Accounts Payable",
        "4001": "Revenue",
        "5001": "Operating Expenses",
        "5200": "Capital Expenditure",
    }

    account_codes = list(accounts.keys())
    df = pd.DataFrame({
        "entry_id": [f"GL{str(i).zfill(5)}" for i in range(1, n + 1)],
        "date": pd.date_range("2024-01-01", periods=n, freq="D").to_list()[:n],
        "account_code": rng.choice(account_codes, n),
        "debit": rng.choice([True, False], n),
        "amount": np.abs(rng.normal(30_000, 12_000, n)).round(2),
        "narration": rng.choice(
            ["Monthly salary", "Vendor payment", "Asset purchase",
             "Utility bill", "Consulting fee", "Revenue receipt"], n
        ),
        "posted_by": rng.choice(["ACC001", "ACC002", "ACC003"], n),
    })

    df["account_name"] = df["account_code"].map(accounts)
    df["date"] = pd.to_datetime(df["date"])
    return df


def load_data(data_dir: str = "data") -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load transactions and GL entries from CSV files.
    Falls back to synthetic data if files are not found.
    """
    txn_path = Path(data_dir) / "transactions.csv"
    gl_path = Path(data_dir) / "gl_entries.csv"

    if txn_path.exists():
        transactions = pd.read_csv(txn_path, parse_dates=["date"])
        print(f"[✓] Loaded {len(transactions)} transactions from {txn_path}")
    else:
        transactions = generate_sample_transactions()
        print("[!] transactions.csv not found — using generated sample data.")

    if gl_path.exists():
        gl_entries = pd.read_csv(gl_path, parse_dates=["date"])
        print(f"[✓] Loaded {len(gl_entries)} GL entries from {gl_path}")
    else:
        gl_entries = generate_gl_entries()
        print("[!] gl_entries.csv not found — using generated sample data.")

    return transactions, gl_entries
