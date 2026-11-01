import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))





"""
dashboard.py
------------
Interactive Streamlit dashboard for Audit Analytics.

Run with:
    streamlit run dashboard.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.data_loader import load_data
from src.anomaly_detector import AnomalyDetector
from src.risk_scorer import RiskScorer

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Audit Analytics Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Internal Audit Analytics Dashboard")
st.caption("Automated anomaly detection and risk scoring for financial transactions")

# ── Sidebar controls ──────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuration")
    method    = st.selectbox("Detection Method", ["zscore", "iqr", "both"], index=0)
    threshold = st.slider("Z-Score Threshold", 1.5, 5.0, 3.0, 0.5)
    group_col = st.selectbox("Group By", ["department", "vendor", "category"])
    st.divider()
    st.info("Adjust settings above and the dashboard will update automatically.")

# ── Load & analyse ────────────────────────────────────────────
@st.cache_data(show_spinner="Loading data…")
def get_data():
    return load_data()

@st.cache_data(show_spinner="Running analysis…")
def get_analysis(method, threshold, group_col):
    txns, _ = get_data()
    detector = AnomalyDetector(threshold=threshold)
    outliers = detector.detect(txns, method=method, group_by=group_col)
    dupes    = detector.detect_duplicates(txns)
    rounds   = detector.detect_round_amounts(txns)
    scorer   = RiskScorer(group_col=group_col)
    risk_df  = scorer.compute(txns, outliers.flagged_df, dupes, rounds)
    return txns, outliers, dupes, rounds, risk_df

transactions, outliers, dupes, rounds, risk_df = get_analysis(method, threshold, group_col)

# ── KPI row ───────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Transactions",  f"{len(transactions):,}")
k2.metric("Total Amount (₹)",    f"₹{transactions['amount'].sum()/1e6:.1f}M")
k3.metric("Anomalies Flagged",   outliers.flagged_count, delta=f"{outliers.flag_rate}%")
k4.metric("Duplicate TXNs",      len(dupes))
k5.metric("Round Amounts",       len(rounds))

st.divider()

# ── Charts row ────────────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader(f"Risk Score by {group_col.title()}")
    color_map = {"Low": "#22c55e", "Medium": "#eab308", "High": "#f97316", "Critical": "#ef4444"}
    fig = px.bar(
        risk_df, x="entity", y="risk_score", color="risk_level",
        color_discrete_map=color_map,
        labels={"entity": group_col.title(), "risk_score": "Risk Score"},
    )
    fig.update_layout(showlegend=True, plot_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("Transaction Amount Distribution")
    fig2 = px.histogram(
        transactions, x="amount", nbins=50,
        color_discrete_sequence=["#3b82f6"],
        labels={"amount": "Transaction Amount (₹)"},
    )
    fig2.update_layout(plot_bgcolor="white")
    st.plotly_chart(fig2, use_container_width=True)

# ── Risk matrix table ─────────────────────────────────────────
st.subheader("📋 Risk Matrix")
display_risk = risk_df[["entity", "transaction_count", "avg_amount",
                          "anomaly_rate_%", "duplicate_rate_%", "risk_score", "risk_level"]].copy()
display_risk.columns = [group_col.title(), "Transactions", "Avg Amount (₹)",
                         "Anomaly %", "Duplicate %", "Risk Score", "Level"]
st.dataframe(display_risk, use_container_width=True, hide_index=True)

# ── Flagged transactions ──────────────────────────────────────
st.subheader("🚨 Flagged Transactions")
if len(outliers.flagged_df):
    st.dataframe(outliers.flagged_df.head(50), use_container_width=True, hide_index=True)
else:
    st.success("No anomalies detected with current settings.")

# ── Monthly trend ─────────────────────────────────────────────
st.subheader("📈 Monthly Transaction Trend")
monthly = transactions.copy()
monthly["month"] = monthly["date"].dt.to_period("M").astype(str)
monthly_grp = monthly.groupby("month").agg(
    total_amount=("amount", "sum"),
    count=("amount", "count")
).reset_index()
fig3 = px.line(monthly_grp, x="month", y="total_amount",
               markers=True, labels={"total_amount": "Total Amount (₹)", "month": "Month"})
fig3.update_layout(plot_bgcolor="white")
st.plotly_chart(fig3, use_container_width=True)
