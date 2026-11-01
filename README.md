# 📊 Audit & Analytics Dashboard

> An end-to-end internal audit analytics system that automates risk detection, anomaly identification, and financial controls monitoring — built with Python, Pandas, and Plotly.

---

## 🎯 Overview

This project simulates a real-world **internal audit analytics pipeline** applicable to large conglomerates. It covers:

- **Financial anomaly detection** using statistical methods (Z-score, IQR)
- **Risk scoring** across business units
- **Automated audit reports** in PDF/HTML format
- **Interactive dashboards** for audit managers

---

## 🗂️ Project Structure

```
audit-analytics-project/
│
├── data/                   # Sample datasets (transactions, GL entries)
│   ├── transactions.csv
│   └── gl_entries.csv
│
├── src/                    # Core Python modules
│   ├── anomaly_detector.py
│   ├── risk_scorer.py
│   ├── report_generator.py
│   └── data_loader.py
│
├── notebooks/              # Jupyter notebooks for EDA & analysis
│   └── audit_eda.ipynb
│
├── reports/                # Auto-generated audit reports
│
├── tests/                  # Unit tests
│   └── test_anomaly_detector.py
│
├── docs/                   # Documentation
│   └── methodology.md
│
├── dashboard.py            # Streamlit dashboard entry point
├── main.py                 # CLI entry point
├── requirements.txt
└── README.md
```

---

## ⚙️ Features

| Feature | Description |
|---|---|
| 🔍 Anomaly Detection | Flags unusual transactions using Z-score & IQR methods |
| 📈 Risk Scoring | Assigns risk levels (Low/Medium/High/Critical) per BU |
| 📑 Automated Reports | Generates formatted audit summaries |
| 📊 Interactive Dashboard | Streamlit UI for drill-down analysis |
| 🧪 Unit Tests | Pytest coverage for core modules |

---

## 🚀 Getting Started

### Prerequisites

```bash
Python 3.9+
pip
```

### Installation

```bash
git clone https://github.com/your-username/audit-analytics-project.git
cd audit-analytics-project
pip install -r requirements.txt
```

### Run the Pipeline

```bash
# Run full audit pipeline
python main.py

# Launch interactive dashboard
streamlit run dashboard.py
```

---

## 📊 Sample Output

Running `main.py` produces:

- **Anomaly Report**: Transactions flagged as outliers with confidence scores
- **Risk Matrix**: Business unit risk heatmap
- **Audit Summary**: Executive-level summary with key findings

---

## 🛠️ Tech Stack

- **Python 3.9+**
- **Pandas / NumPy** — data wrangling
- **Scikit-learn** — anomaly detection models
- **Plotly / Matplotlib** — visualizations
- **Streamlit** — dashboard
- **Pytest** — testing
- **FPDF2** — PDF report generation

---

## 📖 Methodology

See [docs/methodology.md](docs/methodology.md) for detailed explanation of:
- Audit sampling techniques
- Risk scoring framework
- Statistical thresholds used

---

## 🤝 Contributing

Pull requests are welcome. Please open an issue first to discuss proposed changes.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
