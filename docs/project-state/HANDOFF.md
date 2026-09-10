# NEXORAS HANDOFF

## READ THIS FIRST
This document allows a new AI session to immediately continue NEXORAS development.

---

## PROJECT
NEXORAS

## PROBLEM
SIH26102 — AI-powered anomaly, fraud and inefficiency detection in MPLAD Scheme

## CURRENT STATUS
**Module 17 - Integration: COMPLETE** (pipeline executes perfectly)
MVP Core is COMPLETE. Ready for final review, cleanup, or launch.

## CURRENT MODULE
MVP COMPLETE

## CURRENT TASK
Run the application via FastAPI and React.

## WHAT WAS JUST COMPLETED
- Module 10 — NLP Project Intelligence Engine
- Module 11 — Unified Risk Scoring Engine
- Module 11 - Unified Risk Scoring Engine
- Built `backend/engine/network_graph.py`:
  - `MPLADSNetworkGraph`: Large-scale heterogeneous tripartite graph (MP ↔ Vendor ↔ IDA) with 29,745 nodes and 64,375 edges
  - Bipartite MP-Vendor projection with 31,585 disbursement edges
  - Mathematical PageRank calculation ($\sum PR = 1.0$) identifying macro-hub contractors
  - Core betweenness centrality identifying structural bridges
  - Connected component partitioning (89 components, giant component contains 97.8% of nodes)
  - Louvain modularity community detection discovering 310 community clusters
  - Bipartite clique mining identifying 50 regional contractor consortiums
  - Ego-subgraph extraction API formatting Cytoscape/UI JSON structures for frontend rendering
  - Full pipeline runner `run_network_graph_pipeline()`
- 12/12 unit tests pass in `tests/test_network_graph.py`
- Documented in `docs/modules/module-08-networkx-graph.md`
- Checkpoint: `v0.8-network-graph`

## FILES CHANGED (Module 8)
- `backend/engine/network_graph.py` (new — NetworkX Graph Engine)
- `tests/test_network_graph.py` (new — 12 unit tests)
- `docs/modules/module-08-networkx-graph.md` (new)
- `docs/project-state/MODULE_STATUS.md` (updated)
- `docs/project-state/MASTER_STATE.md` (updated)
- `docs/project-state/MODEL_STATE.md` (updated)
- `docs/project-state/TEST_RESULTS.md` (updated)
- `docs/project-state/CHANGELOG.md` (updated)
- `docs/project-state/HANDOFF.md` (updated)

## IMPORTANT CODE LOCATIONS
- Data loader: `backend/ingestion/loader.py`
- Data cleaner: `backend/cleaning/cleaner.py`
- Feature builder: `backend/features/builder.py`
- Isolation Forest engine: `backend/engine/isolation_forest.py`
- Autoencoder engine: `backend/engine/autoencoder.py`
- Anomaly Ensemble engine: `backend/engine/ensemble.py`
- Vendor Network Intelligence: `backend/engine/vendor_intelligence.py`
- NetworkX Graph Engine: `backend/engine/network_graph.py`
- Tests: `tests/test_ingestion.py`, `tests/test_cleaning.py`, `tests/test_features.py`, `tests/test_isolation_forest.py`, `tests/test_autoencoder.py`, `tests/test_ensemble.py`, `tests/test_vendor_intelligence.py`, `tests/test_network_graph.py`
- Dataset CSVs: `D:\sih 2026\mplads dataset\`

## MODEL STATE
- Module 4A (Isolation Forest): COMPLETE (25/25 PASS, Checkpoint: v0.4-isolation-forest)
- Module 4B (Autoencoder): COMPLETE (26/26 PASS, Checkpoint: v0.5-autoencoder)
- Module 5 (Anomaly Ensemble): COMPLETE (29/29 PASS, Checkpoint: v0.6-anomaly-ensemble)
- Module 7 (Vendor Network Intelligence): COMPLETE (14/14 PASS, Checkpoint: v0.7-vendor-intelligence)
- Module 8 (NetworkX Graph Engine): COMPLETE (12/12 PASS, Checkpoint: v0.8-network-graph)

## KNOWN BUGS
None.

## IMPORTANT DECISIONS
- DECISION-001 through DECISION-009 documented in `docs/project-state/DECISIONS.md`

## LAST STABLE CHECKPOINT
**v0.8-network-graph** (2026-09-10)

## WHAT MUST NOT BE CHANGED
- `MPLADSNetworkGraph` API and node/edge schemas
- `VendorProfile` and `VendorNetworkIntelligence` schemas
- `AnomalyEnsemble` schema (`ensemble_score`, `ensemble_tier`, `model_disagreement`, `audit_priority_rank`)

## WHAT IS SAFE TO CHANGE
- NLP vectorization thresholds and risk score weights in Module 10 & 11

## EXACT NEXT STEP
1. Implement `backend/engine/nlp_matcher.py` (Module 10) to detect duplicate / near-duplicate work descriptions
2. Implement `backend/scoring/risk_engine.py` (Module 11) to synthesize Tabular Anomaly Scores (Isolation Forest + Autoencoder), Vendor Risk Scores, Network Centrality Scores, and NLP duplicate flags into a Unified Constituency Risk Score (0-100)
3. Create unit tests and documentation
4. Tag `v0.9-risk-scoring`

## COMMAND TO VERIFY CURRENT STATE
```bash
python "D:\sih 2026\sample mvp\NEXORAS-sample-mvp\tests\test_network_graph.py"
```

## HOW TO CONTINUE
1. Read docs/project-state/MASTER_STATE.md
2. Read docs/project-state/MODULE_STATUS.md
3. Read this HANDOFF.md
4. Read docs/modules/module-08-networkx-graph.md
5. Run tests/test_network_graph.py
6. Proceed to implement Module 10 (NLP) & Module 11 (Unified Risk Engine)















