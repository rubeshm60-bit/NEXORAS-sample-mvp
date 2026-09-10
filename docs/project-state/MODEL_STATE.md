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
COMPLETE (Module 4B, Checkpoint: v0.5-autoencoder)

### Purpose
Neural compression-reconstruction architecture trained to detect non-linear multi-feature irregularities via reconstruction Mean Squared Error (MSE).

### Architecture (Implemented in PyTorch)
```
Input(9 features) -> Linear(9, 32) -> ReLU -> Linear(32, 16) -> ReLU -> Linear(16, 8) [Bottleneck]
                  -> Linear(8, 16) -> ReLU -> Linear(16, 32) -> ReLU -> Linear(32, 9) [Reconstruction]
Optimization: Adam (lr=0.005, weight_decay=1e-5), Criterion: MSELoss
```

### Input Features (9 normalized via StandardScaler)
`utilization_rate`, `unspent_ratio`, `completion_rate`, `vendor_hhi`, `top_vendor_share`, `pending_payment_ratio`, `avg_transaction_size`, `image_compliance_rate`, `avg_spend_per_vendor`

### Threshold & Calibration
- Threshold: 92nd percentile of training reconstruction error (0.3743 for PyTorch model)
- Contamination target: 8.0% (flags 62 anomalous MPs)
- Normalized continuous anomaly score: $[0.0, 1.0]$ based on min/max training MSE

### Training Performance
- Initial Loss: 1.0050
- Final Loss: 0.1437 (verified monotonic convergence)
- Backend: PyTorch 2.14.0+cpu with scikit-learn MLPRegressor fallback

### Evaluation & Test Results
- Unit tests: 26/26 PASS in `tests/test_autoencoder.py`
- Exact reproducibility: $\Delta < 10^{-5}$ across save/load cycles
- Explainability: `explain_mp()` produces feature-by-feature scaled reconstruction errors

### Next Action
Module 5 — Anomaly Ensemble (combining Isolation Forest and Autoencoder)


---

## Model 3 — Anomaly Ensemble

### Status
COMPLETE (Module 5, Checkpoint: v0.6-anomaly-ensemble)

### Purpose
Dual-engine consensus synthesizer that blends Isolation Forest ($w=0.5$) and PyTorch Autoencoder ($w=0.5$) continuous anomaly scores into calibrated consensus tiers.

### Models Synthesized
1. `MPIsolationForest` (Tree-based orthogonal recursive partitioning)
2. `MPAutoencoder` (Deep bottleneck neural reconstruction MSE)

### Output Schema
- `ensemble_score`: float in $[0.0, 1.0]$
- `ensemble_tier`: `CRITICAL_CONSENSUS` (28 MPs), `TREE_ISOLATED` (34 MPs), `NEURAL_IRREGULARITY` (34 MPs), `NORMAL` (678 MPs)
- `model_disagreement`: $|S_{\text{IF}} - S_{\text{AE}}|$
- `audit_priority_rank`: 1 to 774

### Test Results
- Unit tests: 29/29 PASS in `tests/test_ensemble.py`

### Next Action
Module 6 & 7 — Vendor Network Intelligence & Graph Analysis

---

## Model 4 — XGBoost


### Status
NOT STARTED

### Purpose
Supervised risk classifier IF valid labeled data exists.

### Feasibility
Supervised ground-truth fraud labels do not exist in the open portal dataset. Per DECISION-002, NEXORAS relies on unsupervised ensemble + vendor graph intelligence rather than synthetic labels.

### Next Action
Bypassed / merged into unsupervised risk scoring pipeline.

---

## Model 4 — Vendor Network Intelligence

### Status
COMPLETE (Module 7, Checkpoint: v0.7-vendor-intelligence)

### Purpose
Entity-relationship modeling, contractor profiling, cartel/syndicate identification, and risk signal generation across 28,206 vendors.

### Patterns Detected
1. `MULTI_MP_SYNDICATE`: 134 vendors active across $\ge 3$ MPs and $\ge 2$ states ($\ge ₹5\text{ Lakh}$)
2. `MONOPOLY_CONTRACTOR`: 116 instances where single vendor captures $\ge 50\%$ of an MP's spending
3. `IDA_EXCLUSIVE_CONDUIT`: 88 instances where single vendor captures $\ge 60\%$ of an agency's disbursements
4. `HIGH_IN_PROGRESS_RISK`: Vendors with high ratio & volume of incomplete payments
5. `HIGH_VALUE_OUTLIER`: Top 1% national payout contractors

### Output & Metrics
- Composite Vendor Risk Score ($0.0 \text{ to } 100.0$)
- 4 Risk Tiers: `HIGH_RISK` (8), `MEDIUM_RISK` (213), `LOW_RISK` (71), `BENIGN` (27,914)
- Total audit candidates: 292 vendors requiring audit review

### Next Action
Module 8 — NetworkX Graph Engine

---

## Model 5 — NetworkX Graph Engine

### Status
COMPLETE (Module 8, Checkpoint: v0.8-network-graph)

### Purpose
Heterogeneous tripartite (MP ↔ Vendor ↔ IDA) and bipartite (MP ↔ Vendor) topological network modeling. Computes PageRank, betweenness centrality, Louvain modularity communities, and bipartite cartel cliques.

### Network Topology & Scale
- Nodes: 29,745 (774 MPs, 28,206 Vendors, 765 IDAs)
- Edges: 64,375 (31,585 direct MP-Vendor disbursements)
- Giant Connected Component: 29,103 nodes (97.8% of entire network)
- Modular Communities: 310 Louvain communities

### Key Algorithms & Metrics
1. `PageRank`: Weighted stationary transition probability distribution ($\sum PR = 1.0$)
2. `Betweenness Centrality`: Core subgraph bridge detection
3. `Louvain Community Detection`: Modularity-optimized clustering
4. `Bipartite Cartel Mining`: Co-vendor partnership rings
5. `Ego Subgraph API`: Cytoscape / UI-ready graph data

### Next Action
Module 10 — NLP / Text Matching & Module 11 — Unified Risk Engine

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
