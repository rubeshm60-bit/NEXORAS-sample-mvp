# MODULE 05 — ANOMALY ENSEMBLE ENGINE

## Purpose
Synthesize unsupervised tree partitioning (Isolation Forest, Module 4A) and deep neural reconstruction error (PyTorch Autoencoder, Module 4B) into an authoritative, multi-signal anomaly ensemble with confidence tiering and audit priority rankings.

## Why NEXORAS Needs It
Relying on a single anomaly detector creates blind spots:
- **Isolation Forest** splits on axis-aligned feature cuts, detecting extreme single-feature spikes (e.g., severe contractor monopoly $HHI \approx 1.0$), but struggles with subtle joint correlation drift.
- **Autoencoder** maps features onto a non-linear latent bottleneck, catching joint manifold violations, but can sometimes reconstruct smooth localized spikes.
- **Ensemble Synthesis** creates defense-in-depth: combining orthogonal mathematical paradigms provides high-confidence audit targets where models agree, while preserving specialized detections where they disagree.

## Ensemble Architecture & Mathematics
1. **Calibrated Consensus Score**:
   $$S_{\text{ensemble}} = w_{\text{IF}} \cdot S_{\text{IF}} + w_{\text{AE}} \cdot S_{\text{AE}}$$
   Where $w_{\text{IF}} = 0.50$ and $w_{\text{AE}} = 0.50$, producing a unified score in $[0.0, 1.0]$.
2. **Model Disagreement**:
   $$D = |S_{\text{IF}} - S_{\text{AE}}|$$
   Quantifies boundary ambiguity to flag edge cases for human auditor discretion.
3. **Audit Priority Ranking**:
   Rankings from $1$ (highest collective risk) to $774$ (lowest risk).

## Consensus Confidence Tiers
| Tier | Description | Logic | Action Plan | MP Count |
|---|---|---|---|---|
| **CRITICAL_CONSENSUS** | High-Confidence Outlier | $IF = \text{True} \land AE = \text{True}$ | Priority 1: Immediate on-ground physical inspection | 28 MPs |
| **TREE_ISOLATED** | Extreme Metric Spike | $IF = \text{True} \land AE = \text{False}$ | Priority 2: Audit specific spike feature (e.g. single vendor) | 34 MPs |
| **NEURAL_IRREGULARITY** | Complex Correlation Drift | $IF = \text{False} \land AE = \text{True}$ | Priority 3: Deep ledger review of expenditure vs works | 34 MPs |
| **NORMAL** | Standard Parliamentary Practice | $IF = \text{False} \land AE = \text{False}$ | Routine monitoring | 678 MPs |

## Empirical Ensemble Findings on MPLADS
- **Total Flagged Audit Candidates**: 96 MPs ($12.4\%$ of 774 parliamentarians)
- **Top Consensus Anomalies**:
  1. `Smt. Sudha Murty` (Rajya Sabha, Karnataka): $S_{\text{ensemble}} = 1.0000$ (Consensus Rank 1)
  2. `Smt. Nirmala Sitharaman` (Rajya Sabha, Karnataka): $S_{\text{ensemble}} = 0.8036$ (Consensus Rank 2)
  3. `Smt. Anupriya Patel` (Mirzapur, UP): $S_{\text{ensemble}} = 0.5874$ (Consensus Rank 3)
  4. `Shri Jogen Mohan` (Rajya Sabha, Assam): $S_{\text{ensemble}} = 0.5733$ (Consensus Rank 4, $HHI=1.0$)
  5. `Prof S.P. Singh Baghel` (Agra, UP): $S_{\text{ensemble}} = 0.5456$ (Consensus Rank 5)

## Files
| File | Purpose |
|---|---|
| `backend/engine/ensemble.py` | `AnomalyEnsemble`, multi-model tiering, end-to-end pipeline runner |
| `tests/test_ensemble.py` | 29-test comprehensive validation suite |

## Tests & Verification
29 unit tests covering:
- Complete output schema (ensemble score, tier, disagreement, consensus flags, priority rank)
- Score boundary validation: $S_{\text{ensemble}} \in [0.0, 1.0]$ with zero NaNs or Infs
- Mutual exclusivity and exhaustive coverage across the 4 consensus tiers
- Risk differentiation: Critical consensus anomalies score $> 2\times$ higher than normal MPs
- Audit priority rank correctness: Rank 1 corresponds strictly to maximum ensemble score
- Full pipeline integration across all 4 datasets and 3 ML models

## Test Results
**29/29 PASS** (2026-09-10)

## Definition of Done
✅ Ensemble combines Isolation Forest and Autoencoder scores
✅ Confidence tiers systematically categorize every MP
✅ High-confidence agreement and disagreement metrics verified
✅ Audit priority ranking generated deterministically
✅ 29/29 unit tests pass
✅ Documentation exists

## Current Status
COMPLETE

## Last Stable Checkpoint
v0.6-anomaly-ensemble

## Next Action
Module 6 & 7 — Vendor Intelligence & Network Analysis
