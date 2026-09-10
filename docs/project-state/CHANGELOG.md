# CHANGELOG

## 2026-09-10

### v1.3-frontend (2026-09-10)
- Implemented Module 16 (React Frontend).
- Initialized Vite + React.
- Created Dashboard, ProjectExplorer, ProjectInvestigation, VendorIntelligence, and NetworkVisualization views.
- Integrated eact-cytoscapejs for bipartite network graphing.


### v1.2-fastapi (2026-09-10)
- Implemented Module 15 (FastAPI Backend).
- Defined Pydantic schemas in schemas.py.
- Added endpoints for dashboard, projects, anomalies, vendors, and network in main.py.
- Added 100% passing API tests using TestClient.


### v1.1-database (2026-09-10)
- Implemented Module 14 (Database) with SQLAlchemy.
- Created normalized relational schema (MP, Project, Vendor, Agency, Payments).
- Created intelligence tables (RiskScores, Explanations).
- Added 100% passing tests for ORM relationships.


### v1.0-explainability (2026-09-10)
- Implemented Module 12 (Explainability / SHAP) with shap.TreeExplainer.
- Implemented Module 13 (Why Flagged Engine) for human-readable evidence.
- Added 100% passing tests for both.


### v0.9-risk-scoring (2026-09-10)
- Implemented Module 10 (NLP Project Intelligence Engine).
- Implemented Module 11 (Unified Risk Scoring Engine).
- Added tests for modules 10 & 11 (100% pass).
- Updated all project state files.


### Added
- Repository created and cloned to `D:\sih 2026\sample mvp\NEXORAS-sample-mvp\`
- AGENTS.md — project context and agent rules
- docs/project-state/ directory with all 12 required state files:
  - MASTER_STATE.md
  - CURRENT_SESSION.md
  - MODULE_STATUS.md
  - ARCHITECTURE_STATE.md
  - DATA_STATE.md
  - MODEL_STATE.md
  - API_STATE.md
  - UI_STATE.md
  - BUGS_AND_ISSUES.md
  - DECISIONS.md
  - TEST_RESULTS.md
  - HANDOFF.md
  - CHANGELOG.md
- docs/modules/ directory (empty — populated as each module is built)
- Full folder scaffold: backend/, frontend/, notebooks/, tests/

### Decisions Made
- DECISION-001: SQLite for MVP
- DECISION-002: Unsupervised ML first (no labeled data)
- DECISION-003: GNN deferred
- DECISION-004: Airflow/Redis removed from MVP scope

### Checkpoint
v0.0-workspace-init

---

## 2026-09-10 (Module 1)

### Added
- `backend/ingestion/loader.py`: Automated multi-dataset loader for 4 MPLADS CSV files
- `backend/ingestion/validator.py`: Comprehensive data integrity validator
- `tests/test_ingestion.py`: 21-test validation suite (21/21 PASS)
- `notebooks/01_inspect_data.py`: Multi-dataset statistical profiler
- `docs/modules/module-01-data-ingestion.md`: Full documentation of Module 1
- `.gitignore`: Ignore temporary test artifacts, bytecode, and virtualenvs

### Changed
- Standardized all DataFrame columns to snake_case and stripped special symbols (`₹`, parentheses, `%`)
- Normalized date attributes into UTC-stripped datetime objects

### Fixed
- Fixed console output encoding crash by enforcing UTF-8 wrapper on Windows cp1252 environment

### Decisions Made
- DECISION-005: Drop `average_rating` column (>99% null)
- DECISION-006: Treat duplicate records in raw expenditures as WARNING for cleaning

### Checkpoint
v0.1-data-ingestion

---

## 2026-09-10 (Module 2)

### Added
- `backend/cleaning/cleaner.py`: Automated cleaning engine for all 4 MPLADS datasets
- `tests/test_cleaning.py`: 25-test comprehensive cleaning test suite (25/25 PASS)
- `notebooks/02_cleaning_analysis.py`: Pre-cleaning diagnostic analyzer
- `docs/modules/module-02-data-cleaning.md`: Full documentation of Module 2

### Changed
- Deduplicated `expenditures` table, reducing row count from 108,695 to 76,313 (pruned 32,382 duplicate rows)
- Imputed missing `work_description` values across completed and recommended tables with `"[No description]"`
- Standardized NaN categories to `"Uncategorized"`

### Decisions Made
- DECISION-007: Preserve zero-allocation MPs with audit warning
- DECISION-008: Impute missing descriptions rather than dropping rows
- DECISION-009: Standardize missing categories to `"Uncategorized"`

### Checkpoint
v0.2-data-cleaning

---

## 2026-09-10 (Module 3)

### Added
- `backend/features/__init__.py`: Features package initializer
- `backend/features/builder.py`: Multi-grain feature extraction engine:
  - `build_mp_features()`: 774 rows × 33 cols (financial ratios, vendor HHI, top vendor share, execution compliance)
  - `build_work_features()`: 44,028 rows × 19 cols (cost deviation Z-score, category median ratio, extreme cost outlier flag, missing image indicator)
  - `build_vendor_features()`: 28,206 rows × 13 cols (total payout, transaction volume, multi-MP presence, in-progress payment ratio)
  - `build_all_features()`: Unified feature extraction pipeline
- `tests/test_features.py`: 27-test feature engineering validation suite (27/27 PASS)
- `docs/modules/module-03-feature-engineering.md`: Full documentation of Module 3

### Verified
- Zero NaNs or Infinite values across all engineered feature series
- Complete mathematical boundary compliance for ratios, HHI, and compliance percentages

### Checkpoint
v0.3-feature-engineering

---

## 2026-09-10 (Module 4A)

### Added
- `backend/engine/__init__.py`: Engine package initializer
- `backend/engine/isolation_forest.py`: Unsupervised Isolation Forest anomaly detection engine:
  - `MPIsolationForest`: 200 trees, 9 financial/contractor features, contamination=0.08 (flagged 62 anomalous MPs)
  - `WorkIsolationForest`: 150 trees, 3 project cost features, contamination=0.03 (flagged 1,310 anomalous works)
  - `explain_mp()`: Local feature attribution breakdown comparing observed metrics against inlier medians
  - Serialization engine (`save`/`load`) using `joblib`
- `tests/test_isolation_forest.py`: 25-test unit validation suite (25/25 PASS)
- `docs/modules/module-04a-isolation-forest.md`: Full documentation of Module 4A

### Verified
- Exact score reproducibility ($\Delta < 10^{-6}$) after serialization
- Anomaly score strictly bounded in $[0.0, 1.0]$ with 0 NaNs or Infs
- High contractor monopoly sensitivity ($HHI \approx 1.0$ yields above-average anomaly scores)

### Checkpoint
v0.4-isolation-forest

---

## 2026-09-10 (Module 4B)

### Added
- `backend/engine/autoencoder.py`: Deep neural reconstruction Autoencoder anomaly engine:
  - Implemented `PyTorchAutoencoderNet` (9 -> 32 -> 16 -> 8 bottleneck -> 16 -> 32 -> 9) in PyTorch 2.14.0+cpu with scikit-learn MLPRegressor fallback
  - `MPAutoencoder`: Automated training, loss convergence tracking (1.0050 -> 0.1437), threshold calibration (92nd percentile = 0.3743), and $[0.0, 1.0]$ score normalization
  - `explain_mp()`: Feature-by-feature scaled reconstruction attribution
  - Serialization: full model state and network state dictionary serialization with `joblib`
- Installed `torch` (2.14.0+cpu) and `networkx` (3.6.1)
- `tests/test_autoencoder.py`: 26-test comprehensive validation suite (26/26 PASS)
- `docs/modules/module-04b-autoencoder.md`: Full documentation of Module 4B

### Verified
- Monotonic loss reduction and convergence
- Exact score reproducibility ($\Delta < 10^{-5}$) across serialization cycles
- Anomaly scores strictly bounded in $[0.0, 1.0]$ with 0 NaNs or Infs
- Top-decile anomaly separation (> 2x median reconstruction MSE)

### Checkpoint
v0.5-autoencoder

---

## 2026-09-10 (Module 5)

### Added
- `backend/engine/ensemble.py`: Multi-model Anomaly Ensemble Engine:
  - Synthesizes tree partitioning (`MPIsolationForest`) and neural reconstruction (`MPAutoencoder`)
  - Calculates calibrated consensus risk scores $S_{\text{ensemble}} \in [0.0, 1.0]$
  - Classifies constituencies into 4 mutual exclusive confidence tiers: `CRITICAL_CONSENSUS` (28 MPs), `TREE_ISOLATED` (34 MPs), `NEURAL_IRREGULARITY` (34 MPs), `NORMAL` (678 MPs)
  - Computes model divergence $D = |S_{\text{IF}} - S_{\text{AE}}|$ to surface ambiguous boundary cases
  - Assigns deterministic national audit priority rank (1 to 774)
  - Full pipeline runner `run_ensemble_pipeline()` combining all 4 datasets and 3 ML models
- `tests/test_ensemble.py`: 29-test comprehensive validation suite (29/29 PASS)
- `docs/modules/module-05-anomaly-ensemble.md`: Full documentation of Module 5

### Verified
- Zero NaNs or Infs across consensus scores and disagreement metrics
- Complete mutually exclusive tier assignment for all 774 MPs
- Risk separation: Critical consensus anomalies score $> 2\times$ higher than normal MPs

### Checkpoint
v0.6-anomaly-ensemble

---

## 2026-09-10 (Module 7)

### Added
- `backend/engine/vendor_intelligence.py`: Vendor Network Intelligence Engine:
  - Built entity relationship mappings across MP, Vendor, IDA, and Payments
  - Profiled full population of 28,206 vendors (total payouts, transaction volume, MP breadth, IDA breadth, in-progress ratio)
  - Algorithmic pattern detection:
    - `MULTI_MP_SYNDICATE`: 134 cross-constituency contractors operating across $\ge 3$ MPs and $\ge 2$ states
    - `MONOPOLY_CONTRACTOR`: 116 instances of single vendors capturing $\ge 50\%$ of an MP's fund
    - `IDA_EXCLUSIVE_CONDUIT`: 88 instances of vendors dominating $\ge 60\%$ of an agency's disbursements
    - `HIGH_IN_PROGRESS_RISK`: Vendors with high pending disbursement ratios
    - `HIGH_VALUE_OUTLIER`: Top 1% national payout contractors
  - Continuous Vendor Risk Score ($0.0 \text{ to } 100.0$) with 4 risk tiers (`HIGH_RISK`, `MEDIUM_RISK`, `LOW_RISK`, `BENIGN`)
  - Query APIs: `get_vendor_profile()`, `get_mp_vendor_breakdown()`, `get_top_risk_vendors()`, `get_summary_stats()`
  - Convenient pipeline runner: `run_vendor_intelligence_pipeline()`
- `tests/test_vendor_intelligence.py`: 14-test comprehensive validation suite (14/14 PASS)
- `docs/modules/module-07-vendor-intelligence.md`: Full documentation of Module 7

### Verified
- Zero NaNs or Infs across all 28,206 vendor risk scores
- Complete financial conservation across relational matrices and raw expenditures
- Neutral audit terminology compliance across all generated flags

### Checkpoint
v0.7-vendor-intelligence

---

## 2026-09-10 (Module 8)

### Added
- `backend/engine/network_graph.py`: NetworkX Graph Engine:
  - Heterogeneous tripartite graph (MP ↔ Vendor ↔ IDA) with 29,745 nodes and 64,375 edges
  - Bipartite MP-Vendor projection with 31,585 disbursement edges
  - Weighted PageRank centrality calculation ($\alpha = 0.85$, exact conservation to $1.0$)
  - Core betweenness centrality identifying structural bottlenecks
  - Connected component partitioning (89 components, giant component contains 97.8% of nodes)
  - Louvain modularity community detection discovering 310 community clusters
  - Bipartite clique mining identifying 50 regional contractor consortiums
  - Ego-subgraph extraction API formatting Cytoscape/UI JSON structures for frontend rendering
  - Pipeline runner `run_network_graph_pipeline()`
- `tests/test_network_graph.py`: 12-test comprehensive validation suite (12/12 PASS)
- `docs/modules/module-08-networkx-graph.md`: Full documentation of Module 8

### Verified
- Bipartite structure strictly preserved between MP and Vendor partitions
- Zero non-finite values in PageRank and Betweenness metrics
- Full ego-graph schema compliance for UI integration

### Checkpoint
v0.8-network-graph











