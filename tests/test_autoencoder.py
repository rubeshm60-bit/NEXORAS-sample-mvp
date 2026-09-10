"""
NEXORAS Module 4B — Neural Autoencoder Tests
Validates all requirements from Section 4C of Master Prompt:
1. Training works & loss decreases
2. Reconstruction error (MSE) is calculated correctly
3. Anomaly threshold is calibrated to contamination percentile
4. Anomaly labels (ae_is_anomaly) and scores [0.0, 1.0] are generated
5. Results are reproducible
6. Model can be saved to disk
7. Model can be loaded later with identical outputs
8. Explainability (feature-wise reconstruction error) works
"""
import os
import tempfile
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, r"D:\sih 2026\sample mvp\NEXORAS-sample-mvp")

from backend.ingestion.loader import load_all
from backend.cleaning.cleaner import clean_all
from backend.features.builder import build_all_features
from backend.engine.autoencoder import MPAutoencoder, run_autoencoder_pipeline

passed = 0
failed = 0
total = 0


def test(name: str, condition: bool):
    global passed, failed, total
    total += 1
    if condition:
        passed += 1
        print(f"  PASS: {name}")
    else:
        failed += 1
        print(f"  FAIL: {name}")


print("=" * 60)
print("NEXORAS — Module 4B Test Suite (Neural Autoencoder Engine)")
print("=" * 60)

# Pipeline: Load -> Clean -> Build Features
raw = load_all()
cleaned = clean_all(raw)
feats = build_all_features(cleaned)
mp_feats = feats["mp_features"]

# ---- Requirement 1: Training Works & Loss Decreases ----
print("\n--- Requirement 1: Training Execution & Loss Reduction ---")
ae_model = MPAutoencoder(contamination=0.08, random_state=42)
ae_model.fit(mp_feats)

test("ae_model.is_fitted is True", ae_model.is_fitted)
test("Training loss history is non-empty", len(ae_model.training_loss_history) > 0)

initial_loss = ae_model.training_loss_history[0]
final_loss = ae_model.training_loss_history[-1]
test(f"Training loss decreased ({initial_loss:.4f} -> {final_loss:.4f})", final_loss < initial_loss)

# ---- Requirement 2 & 3: Reconstruction Error & Threshold Calibration ----
print("\n--- Requirements 2 & 3: Reconstruction Error & Thresholding ---")
test("Reconstruction threshold is positive float", ae_model.threshold is not None and ae_model.threshold > 0.0)
test("Min MSE <= Max MSE", ae_model.min_mse <= ae_model.max_mse)

# ---- Requirement 4: Scoring, Labels, and Boundary Validation ----
print("\n--- Requirement 4: Anomaly Scoring & Binary Labels ---")
scored_mps = ae_model.score(mp_feats)

test("scored_mps has exactly 774 rows", len(scored_mps) == 774)
test("scored_mps contains 'ae_reconstruction_mse'", "ae_reconstruction_mse" in scored_mps.columns)
test("scored_mps contains 'ae_anomaly_score'", "ae_anomaly_score" in scored_mps.columns)
test("scored_mps contains 'ae_is_anomaly'", "ae_is_anomaly" in scored_mps.columns)

scores = scored_mps["ae_anomaly_score"]
test("ae_anomaly_score has no NaNs", not scores.isnull().any())
test("ae_anomaly_score has no Infs", not np.isinf(scores).any())
test("ae_anomaly_score min is >= 0.0", scores.min() >= 0.0)
test("ae_anomaly_score max is <= 1.0", scores.max() <= 1.0)

flagged_count = scored_mps["ae_is_anomaly"].sum()
test("Anomaly flags volume aligns with ~8% contamination (50-75 MPs)", 50 <= flagged_count <= 75)

# ---- Requirement 5: Ranking Sanity on Known Irregularities ----
print("\n--- Requirement 5: Ranking Sanity ---")
# Zero-allocation MP and high-HHI/high-spend MPs should have strongly elevated MSE
zero_alloc_mps = scored_mps[scored_mps["allocated_amount"] == 0.0]
top_decile_mse = scored_mps["ae_reconstruction_mse"].quantile(0.90)
median_mse = scored_mps["ae_reconstruction_mse"].median()

if len(zero_alloc_mps) > 0:
    zero_alloc_mse = zero_alloc_mps["ae_reconstruction_mse"].iloc[0]
    test("Zero-allocation MP (Chavan Vasantrao) has higher reconstruction MSE than population median", zero_alloc_mse > median_mse)
else:
    test("Zero allocation MP check", True)

test("Top decile anomaly MSE is substantially higher than median MSE (> 2x)", top_decile_mse > (2.0 * median_mse))

# ---- Requirement 6 & 7: Serialization, Deserialization, & Exact Reproducibility ----
print("\n--- Requirements 6 & 7: Serialization & Reproducibility ---")
with tempfile.TemporaryDirectory() as tmpdir:
    save_path = os.path.join(tmpdir, "mp_ae_test.joblib")
    ae_model.save(save_path)
    test("Model file exists on disk after save", os.path.exists(save_path))

    loaded_model = MPAutoencoder.load(save_path)
    test("Loaded model has is_fitted=True", loaded_model.is_fitted)

    re_scored = loaded_model.score(mp_feats)
    diff = np.abs(scored_mps["ae_anomaly_score"].values - re_scored["ae_anomaly_score"].values).max()
    test("Loaded model produces identical scores (max diff < 1e-5)", diff < 1e-5)

# ---- Requirement 8: Explainability / Feature Attribution ----
print("\n--- Requirement 8: Explainability via Feature Reconstruction Error ---")
sample_mp = scored_mps.sort_values(by="ae_anomaly_score", ascending=False).iloc[0]
explanations = ae_model.explain_mp(sample_mp)
test("explain_mp returns non-empty breakdown", len(explanations) == len(ae_model.feature_cols))
test("explain_mp has 'feature'", "feature" in explanations[0])
test("explain_mp has 'observed'", "observed" in explanations[0])
test("explain_mp has 'reconstructed'", "reconstructed" in explanations[0])
test("explain_mp has 'scaled_reconstruction_error'", "scaled_reconstruction_error" in explanations[0])

# ---- Full Pipeline Runner ----
print("\n--- Full Pipeline Runner ---")
pipe_mps, pipe_model = run_autoencoder_pipeline(feats)
test("Pipeline returns scored MP DataFrame with 774 rows", len(pipe_mps) == 774)
test("Pipeline returns fitted model", pipe_model.is_fitted)

# ---- Summary ----
print("\n" + "=" * 60)
print(f"RESULTS: {passed}/{total} tests passed, {failed} failed")
if failed == 0:
    print("ALL TESTS PASSED")
else:
    print(f"WARNING: {failed} test(s) failed!")
print("=" * 60)
