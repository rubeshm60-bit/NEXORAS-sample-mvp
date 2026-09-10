# NEXORAS MODEL STATE

## Overview
No models implemented yet. All statuses are NOT STARTED.

---

## Model 1 — Isolation Forest

### Status
NOT STARTED

### Purpose
Unsupervised anomaly detection on financial/expenditure features. Isolates outliers by random partitioning — anomalies need fewer splits.

### Input Features (Planned)
- expenditure_ratio, cost_deviation, unspent_ratio, admin_ratio, vendor_concentration

### Preprocessing
StandardScaler normalization (planned)

### Training Data
mplads_mp_summary + mplads_expenditures CSVs (after cleaning + feature engineering)

### Parameters (TBD)
- n_estimators, contamination, max_features

### Threshold
TBD after training

### Output
anomaly_score (float), anomaly_label (0/1)

### Model File
Not saved yet — `backend/engine/isolation_forest.pkl` (planned)

### Version
Not trained

### Known Limitations
- No labeled data — unsupervised only
- Sensitive to feature scaling

### Next Action
Build after Module 3 (Feature Engineering) is complete

---

## Model 2 — Autoencoder

### Status
NOT STARTED

### Purpose
Neural network trained on normal data. High reconstruction error = anomaly. Detects unusual feature combinations.

### Architecture (Planned)
```
Input(N features) → Dense(64) → Dense(32) → Dense(16) [bottleneck]
→ Dense(32) → Dense(64) → Output(N features)
Loss = MSE(reconstructed, actual)
```

### Input Features (Planned)
Same as Isolation Forest (normalized)

### Threshold
Percentile of reconstruction error on training set (TBD)

### Model File
`backend/engine/autoencoder.pt` (planned)

### Version
Not trained

### ⚠️ IMPORTANT
Do NOT silently remove the Autoencoder. It is a required component.
If blocked: Record STATUS: BLOCKED with reason and fallback plan.

### Next Action
Build after Module 3 (Feature Engineering) is complete

---

## Model 3 — XGBoost

### Status
NOT STARTED

### Purpose
Supervised risk classifier IF valid labeled data exists.

### Feasibility
UNKNOWN — depends on whether proxy labels can be generated from the dataset.
Rule: If no reliable labels exist, do NOT pretend XGBoost is a fraud classifier.

### Next Action
Evaluate after dataset inspection (Module 1)

---

## Model 4 — NetworkX Graph Engine

### Status
NOT STARTED

### Purpose
Build entity relationship graph (MP → Project → Vendor/IA). Detect vendor concentration, unusual relationships.

### Next Action
Build after Module 3

---

## Model 5 — GNN

### Status
DEFERRED

### Reason
Requires sufficient graph data + labels. NetworkX must prove feasibility first.

### Future Plan
If NetworkX shows clear cartel/collusion patterns that tabular ML misses, implement GNN as Module 9.

---

## Model 6 — NLP / spaCy

### Status
NOT STARTED

### Feasibility
UNKNOWN — depends on whether text fields exist in the dataset (project descriptions, work descriptions).

### Next Action
Inspect dataset columns during Module 1

---

## Model 7 — SHAP

### Status
NOT STARTED

### Purpose
Explain WHY a project was flagged — which features contributed most to the risk score.

### Next Action
Implement after ML models are working (Module 12)
