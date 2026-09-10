# CHANGELOG

## 2026-09-10

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


