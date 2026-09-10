# MODULE 04B — NEURAL AUTOENCODER ANOMALY ENGINE

## Purpose
Deploy a deep symmetric neural compression-reconstruction architecture to capture non-linear feature interactions and detect anomalies through reconstruction Mean Squared Error (MSE).

## Why NEXORAS Needs It
While tree-based Isolation Forest partitions feature space with axis-aligned orthogonal cuts, an Autoencoder maps features onto a non-linear low-dimensional manifold. High reconstruction error indicates that an MP's operational signature violates the underlying correlations of standard parliamentary operations.

## Architecture
- **Input Dimension**: 9 normalized features (`StandardScaler`)
- **Bottleneck Latent Dimension**: 8
- **Encoder**: Layer(9 -> 32) -> ReLU -> Layer(32 -> 16) -> ReLU -> Layer(16 -> 8)
- **Decoder**: Layer(8 -> 16) -> ReLU -> Layer(16 -> 32) -> ReLU -> Layer(32 -> 9)
- **Optimization**: Adam optimizer, initial loss 0.5361, final converged loss 0.0222

## Mathematical Foundation
- **Reconstruction MSE**:
  $$MSE(x) = \frac{1}{D} \sum_{j=1}^D (x_j - \hat{x}_j)^2$$
- **Threshold Calibration**: The anomaly threshold is dynamically set at the $(1 - \text{contamination}) \times 100$-th percentile (92nd percentile = 0.1186 for 8% contamination).
- **Normalized Score**: Normalized onto $[0.0, 1.0]$ where $1.0$ represents maximum reconstruction failure.

## Empirical Detection Highlights
Autoencoder identified distinct complex non-linear outliers:
- **MP Shri Ramji (Sitting Rajya Sabha, UP)**: Highest reconstruction MSE (1.7891) due to contradictory signals: above-average completion rate (62.8%) coupled with heavy single-contractor dominance (54.0% top vendor capture).
- **MP Chavan Vasantrao Balwantrao (Nanded)**: Flagged with second highest MSE (1.1322) driven by zero allocation status against non-zero operational overheads.
- **MP Pankaj Chowdhary (Maharajganj)**: High MSE (0.3456) driven by extreme contractor concentration ($HHI = 0.8898$).

## Files
| File | Purpose |
|---|---|
| `backend/engine/autoencoder.py` | `MPAutoencoder` architecture, training, thresholding, explainability |
| `tests/test_autoencoder.py` | 26-test unit validation suite |

## Tests & Verification
26 unit tests covering all Section 4C Master Prompt requirements:
- Loss minimization verification (loss decreased from 0.5361 to 0.0222)
- Positive reconstruction threshold calculation
- Zero NaNs or Infs across 774 MP scores
- Expected contamination volume (62 MPs flagged, exactly 8.0%)
- Substantial separation between top-decile anomaly MSE and median MSE (> 2x)
- Model serialization & deserialization with identical score outputs ($\Delta < 10^{-5}$)
- Feature-wise reconstruction attribution breakdown (`explain_mp`)

## Test Results
**26/26 PASS** (2026-09-10)

## Definition of Done
✅ Loss decreases smoothly during backpropagation
✅ Reconstruction error computed per observation
✅ Dynamic threshold calibrated to target contamination
✅ Binary anomaly flags and continuous scores generated
✅ Results verified reproducible across save/load cycles
✅ 26/26 unit tests pass
✅ Documentation exists

## Current Status
COMPLETE

## Last Stable Checkpoint
v0.5-autoencoder

## Next Action
Module 5 — Anomaly Ensemble (Combining Isolation Forest + Autoencoder)
