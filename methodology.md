# Audit Analytics — Methodology

## 1. Anomaly Detection

### Z-Score Method
Flags transactions where the normalised deviation from the mean exceeds the configured threshold (default: 3σ). Applied per-group (department/vendor) to account for natural differences in spending scale.

```
z = |x - μ| / σ
flag if z > threshold
```

### IQR (Interquartile Range) Method
Flags transactions outside the IQR fence:

```
lower = Q1 − 1.5 × IQR
upper = Q3 + 1.5 × IQR
```

Non-parametric; more robust to heavy-tailed distributions.

### Combined ("Both")
Union of Z-Score and IQR flags — catches outliers that only one method may miss.

---

## 2. Risk Scoring Framework

Each department/business unit receives a composite risk score (0–100) based on four weighted dimensions:

| Dimension | Weight | Description |
|---|---|---|
| Anomaly Rate | 40% | % of transactions flagged as outliers |
| Average Amount | 25% | Normalised avg transaction size vs portfolio max |
| Duplicate Rate | 20% | % of duplicate transactions (same vendor/amount/date) |
| Round Amount Rate | 15% | % of suspiciously round-number transactions |

### Risk Bands
| Score Range | Level | Recommended Action |
|---|---|---|
| 0–25 | 🟢 Low | Routine monitoring |
| 25–50 | 🟡 Medium | Quarterly review |
| 50–75 | 🟠 High | Immediate review recommended |
| 75–100 | 🔴 Critical | Escalate to senior audit management |

---

## 3. Duplicate Transaction Detection

Transactions sharing the same **date + vendor + amount** triplet are flagged as potential duplicates. These may indicate:
- Double payments to vendors
- System-level processing errors
- Fraudulent re-submissions

---

## 4. Round Amount Detection

Transactions at exact multiples of ₹1,000 (configurable) above a minimum threshold are flagged. Round amounts are a well-documented indicator of fictitious or estimated invoices in internal audit literature.

---

## 5. Sampling Considerations

The pipeline analyses the full transaction population rather than a statistical sample, enabling 100% coverage audit testing — consistent with data analytics best practices for automated controls testing.
