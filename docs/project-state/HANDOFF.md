# NEXORAS HANDOFF

## READ THIS FIRST
This document allows a new AI session to immediately continue NEXORAS development.

---

## PROJECT
NEXORAS

## PROBLEM
SIH26102 — AI-powered anomaly, fraud and inefficiency detection in MPLAD Scheme

## CURRENT STATUS
**Module 5 — Anomaly Ensemble: COMPLETE** (29/29 tests pass)
Ready to begin Module 7 — Vendor Network Intelligence.

## CURRENT MODULE
Module 5 (COMPLETE) → Starting Module 7 — Vendor Network Intelligence

## CURRENT TASK
Implement Vendor Network Intelligence (`backend/engine/vendor_intelligence.py`) to analyze contractor concentration, detect cross-constituency cartel patterns, and compute vendor risk scores.

## WHAT WAS JUST COMPLETED
- Module 5 — Anomaly Ensemble
- Built `backend/engine/ensemble.py`:
  - `AnomalyEnsemble`: Dual-model consensus synthesizer ($w_{\text{IF}} = 0.5, w_{\text{AE}} = 0.5$)
  - Tier Assignment: `CRITICAL_CONSENSUS` (28 MPs), `TREE_ISOLATED` (34 MPs), `NEURAL_IRREGULARITY` (34 MPs), `NORMAL` (678 MPs)
  - Model Disagreement: $|S_{\text{IF}} - S_{\text{AE}}|$
  - Deterministic National Audit Priority Rank (1 to 774)
  - Full pipeline runner `run_ensemble_pipeline()`
- 29/29 unit tests pass in `tests/test_ensemble.py`
- Documented in `docs/modules/module-05-anomaly-ensemble.md`
- Checkpoint: `v0.6-anomaly-ensemble`

## FILES CHANGED (Module 5)
- `backend/engine/ensemble.py` (new — Anomaly Ensemble Engine)
- `tests/test_ensemble.py` (new — 29 unit tests)
- `docs/modules/module-05-anomaly-ensemble.md` (new)
- `docs/project-state/MODEL_STATE.md` (updated)
- `docs/project-state/MODULE_STATUS.md` (updated)
- `docs/project-state/MASTER_STATE.md` (updated)
- `docs/project-state/TEST_RESULTS.md` (updated)
- `docs/project-state/CHANGELOG.md` (updated)

## IMPORTANT CODE LOCATIONS
- Data loader: `backend/ingestion/loader.py`
- Data cleaner: `backend/cleaning/cleaner.py`
- Feature builder: `backend/features/builder.py`
- Isolation Forest engine: `backend/engine/isolation_forest.py`
- Autoencoder engine: `backend/engine/autoencoder.py`
- Anomaly Ensemble engine: `backend/engine/ensemble.py`
- Tests: `tests/test_ingestion.py`, `tests/test_cleaning.py`, `tests/test_features.py`, `tests/test_isolation_forest.py`, `tests/test_autoencoder.py`, `tests/test_ensemble.py`
- Dataset CSVs: `D:\sih 2026\mplads dataset\`

## MODEL STATE
- Module 4A (Isolation Forest): COMPLETE (25/25 PASS, Checkpoint: v0.4-isolation-forest)
- Module 4B (Autoencoder): COMPLETE (26/26 PASS, Checkpoint: v0.5-autoencoder)
- Module 5 (Anomaly Ensemble): COMPLETE (29/29 PASS, Checkpoint: v0.6-anomaly-ensemble)
- Module 6 (XGBoost): Supervised fraud labels do not exist; evaluated as unnecessary
- Module 7 (Vendor Network Intelligence): NOT STARTED -> Active next

## KNOWN BUGS
None.

## IMPORTANT DECISIONS
- DECISION-001 through DECISION-009 documented in `docs/project-state/DECISIONS.md`

## LAST STABLE CHECKPOINT
**v0.6-anomaly-ensemble** (2026-09-10)

## WHAT MUST NOT BE CHANGED
- `AnomalyEnsemble` schema (`ensemble_score`, `ensemble_tier`, `model_disagreement`, `audit_priority_rank`)
- Input feature signatures and model pipelines

## WHAT IS SAFE TO CHANGE
- Network analysis thresholds (e.g. min MP connections for cartel candidate) in Module 7 & 8

## EXACT NEXT STEP
1. Implement `backend/engine/vendor_intelligence.py` (Module 7)
2. Profile 28,206 vendors by total payouts, multi-MP presence, and transaction frequency
3. Identify contractor cartels (vendors receiving funds from multiple distinct MPs across state boundaries)
4. Create unit tests in `tests/test_vendor_intelligence.py`
5. Document in `docs/modules/module-07-vendor-intelligence.md`
6. Tag `v0.7-vendor-intelligence`

## COMMAND TO VERIFY CURRENT STATE
```bash
python "D:\sih 2026\sample mvp\NEXORAS-sample-mvp\tests\test_ensemble.py"
```

## HOW TO CONTINUE
1. Read docs/project-state/MASTER_STATE.md
2. Read docs/project-state/MODULE_STATUS.md
3. Read this HANDOFF.md
4. Read docs/modules/module-05-anomaly-ensemble.md
5. Run tests/test_ensemble.py
6. Proceed to implement Module 7 Vendor Intelligence





