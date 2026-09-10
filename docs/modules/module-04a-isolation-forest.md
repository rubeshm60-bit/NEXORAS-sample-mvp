# MODULE 04A — ISOLATION FOREST ANOMALY ENGINE

## Purpose
Deploy unsupervised tree-based recursive partitioning to isolate multi-dimensional statistical outliers across parliamentarians (MP level) and community development projects (Work level).

## Why NEXORAS Needs It
Government expenditure datasets for MPLADS lack supervised fraud labels. We cannot train a supervised classifier because ground-truth fraud classifications do not exist in open portal data. Isolation Forest detects anomalies without labels by exploiting the fundamental property that fraudulent, monopolistic, or grossly inefficient operations are structurally "few and different", requiring fewer random splits to isolate.

## Theoretical Foundations
1. **Tree Partitioning**: An ensemble of 200 Isolation Trees randomly subsamples data points and recursively chooses random split values between the feature extrema.
2. **Path Length $h(x)$**: Anomalous data points have values far removed from dense normal clusters; hence they isolate near the root of the tree with short path lengths.
3. **Anomaly Score Formulation**:
   $$s(x, n) = 2^{-\frac{E(h(x))}{c(n)}}$$
   Where $E(h(x))$ is the average path length across all 200 trees, and $c(n) = 2(\ln(n - 1) + 0.5772) - \frac{2(n - 1)}{n}$ is the average depth of an unsuccessful BST search.
4. **Normalized Calibration**: Decision function values are calibrated to $[0.0, 1.0]$, where $1.0$ represents maximum outlier confidence.

## Input
Engineered feature matrices from Module 3:
- `mp_features`: 774 rows
  - Features used (9): `utilization_rate`, `unspent_ratio`, `completion_rate`, `vendor_hhi`, `top_vendor_share`, `pending_payment_ratio`, `avg_transaction_size`, `image_compliance_rate`, `avg_spend_per_vendor`
- `work_features`: 44,028 rows
  - Features used (3): `final_amount`, `cost_deviation_z`, `cost_to_median_ratio`

## Output
1. `scored_mps`:
   - `if_anomaly_score`: Continuous anomaly probability $[0.0, 1.0]$
   - `if_is_anomaly`: Boolean indicator (top 8.0% outliers, 62 MPs flagged)
2. `scored_works`:
   - `work_if_score`: Continuous anomaly probability $[0.0, 1.0]$
   - `work_is_anomaly`: Boolean indicator (top 3.0% outliers, 1,310 works flagged)
3. Local Feature Attribution (`explain_mp`):
   - Computes percentage deviation of each feature relative to inlier median baseline for transparent explainability.

## Empirical Findings & Detection Highlights
Top flagged anomalies in real MPLADS data:
- **MP Shri Jogen Mohan (Assam)**:
  - `vendor_hhi` = 1.000 (100% of all public funds allocated to a single contractor)
  - `top_vendor_share` = 1.000
  - `completion_rate` = 0.000 (Zero completed projects on ground)
  - `if_anomaly_score` = 0.9566 (Flagged outlier)
- **MP Smt. Sudha Murty (Karnataka)**:
  - `vendor_hhi` = 0.8691
  - `top_vendor_share` = 0.9296
  - `completion_rate` = 0.000
  - `if_anomaly_score` = 1.0000 (Maximum outlier)

## Files
| File | Purpose |
|---|---|
| `backend/engine/__init__.py` | Engine package init |
| `backend/engine/isolation_forest.py` | `MPIsolationForest`, `WorkIsolationForest`, pipeline orchestration |
| `tests/test_isolation_forest.py` | 25-test unit validation suite |

## Tests & Verification
25 unit tests covering:
- Model fitting and score bounds ($0.0 \le s \le 1.0$)
- Anomaly flag volume alignment with contamination hyperparameter (62 MPs for 8% contamination)
- Monopoly contractor sensitivity verification (MPs with $HHI=1.0$ receive above-average anomaly scores)
- Local explainability feature attribution output
- Serialization test: `joblib` save and load produces exact numerical identity ($\Delta < 10^{-6}$)
- Work-level model execution on 44,028 rows (1,310 flagged works)

## Test Results
**25/25 PASS** (2026-09-10)

## Hyperparameter Calibration
- `MPIsolationForest`: `n_estimators=200`, `contamination=0.08`, `random_state=42`
- `WorkIsolationForest`: `n_estimators=150`, `contamination=0.03`, `random_state=42`

## Limitations
- Sensitive to extreme unnormalized feature scale; mitigated by preceding `StandardScaler`.
- Does not model relational graph topologies (addressed in Module 8 NetworkX).
- High score indicates statistical novelty, not definitive legal guilt; acts as a prioritization shield for physical auditing.

## Definition of Done
✅ Both MP and Work models train deterministically
✅ Continuous scores calibrated into $[0.0, 1.0]$ with 0 NaNs
✅ Contamination rate yields expected audit batch sizes
✅ Serialized models reload with exact reproducibility
✅ 25/25 unit tests pass
✅ Documentation exists

## Current Status
COMPLETE

## Last Stable Checkpoint
v0.4-isolation-forest

## Next Action
Module 4B — Autoencoder (Neural Reconstruction Error Engine)
