# NEXORAS MODEL STATE

## Overview
No models implemented yet. All statuses are NOT STARTED.

---

## Model 1 — Isolation Forest

### Status
COMPLETE (Module 4A, Checkpoint: v0.4-isolation-forest)

### Purpose
Unsupervised multi-tree recursive partitioning to isolate multi-dimensional statistical outliers across parliamentarians (MP level) and individual works.

### Models Implemented
1. `MPIsolationForest`:
   - Input Features (9): `utilization_rate`, `unspent_ratio`, `completion_rate`, `vendor_hhi`, `top_vendor_share`, `pending_payment_ratio`, `avg_transaction_size`, `image_compliance_rate`, `avg_spend_per_vendor`
   - Preprocessing: `StandardScaler`
   - Training Data: 774 MP feature vectors
   - Parameters: `n_estimators=200`, `contamination=0.08`, `random_state=42`
   - Output: `if_anomaly_score` [0.0, 1.0], `if_is_anomaly` (bool, 62 MPs flagged, 8.0%)
   - Serialization: `joblib` compatible

2. `WorkIsolationForest`:
   - Input Features (3): `final_amount`, `cost_deviation_z`, `cost_to_median_ratio`
   - Preprocessing: `StandardScaler`
   - Training Data: 44,028 completed works
   - Parameters: `n_estimators=150`, `contamination=0.03`, `random_state=42`
   - Output: `work_if_score` [0.0, 1.0], `work_is_anomaly` (bool, 1,310 works flagged, 3.0%)

### Evaluation & Test Results
- Unit tests: 25/25 PASS in `tests/test_isolation_forest.py`
- Exact reproducibility: $\Delta < 10^{-6}$ across save/load cycles
- Explainability: `explain_mp()` produces rank-ordered feature percentage deviations relative to inlier medians

### Known Limitations
- Does not model entity network topologies (addressed in Module 8 NetworkX)
- Score represents statistical outlier status, not definitive legal guilt

### Next Action
Module 4B — Autoencoder (Neural Reconstruction Error Engine)

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
