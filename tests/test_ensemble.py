"""
NEXORAS Module 5 — Anomaly Ensemble Tests
Validates multi-model consensus, confidence tiers, score calibration, and disagreement analysis.
"""
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, r"D:\sih 2026\sample mvp\NEXORAS-sample-mvp")

from backend.ingestion.loader import load_all
from backend.cleaning.cleaner import clean_all
from backend.features.builder import build_all_features
from backend.engine.isolation_forest import MPIsolationForest
from backend.engine.autoencoder import MPAutoencoder
from backend.engine.ensemble import AnomalyEnsemble, run_ensemble_pipeline

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
print("NEXORAS — Module 5 Test Suite (Anomaly Ensemble Engine)")
print("=" * 60)

# Pipeline: Load -> Clean -> Build Features
raw = load_all()
cleaned = clean_all(raw)
feats = build_all_features(cleaned)
mp_feats = feats["mp_features"]

# Train both models
if_model = MPIsolationForest(contamination=0.08, random_state=42).fit(mp_feats)
ae_model = MPAutoencoder(contamination=0.08, random_state=42).fit(mp_feats)

if_df = if_model.score(mp_feats)
ae_df = ae_model.score(mp_feats)

# Instantiate Ensemble
ensemble = AnomalyEnsemble(if_weight=0.50, ae_weight=0.50)
combined_df = ensemble.combine(if_df, ae_df)

# ---- Test Group 1: Output Schema & Dimensions ----
print("\n--- Test Group 1: Schema & Completeness ---")
test("combined_df has 774 rows", len(combined_df) == 774)

required_cols = [
    "ensemble_score",
    "ensemble_tier",
    "ensemble_flagged",
    "consensus_flagged",
    "model_disagreement",
    "audit_priority_rank",
]
for col in required_cols:
    test(f"combined_df contains '{col}'", col in combined_df.columns)

# ---- Test Group 2: Mathematical Boundary Validation ----
print("\n--- Test Group 2: Score Bounds & Sanity ---")
scores = combined_df["ensemble_score"]
test("ensemble_score has no NaNs", not scores.isnull().any())
test("ensemble_score has no Infs", not np.isinf(scores).any())
test("ensemble_score min >= 0.0", scores.min() >= 0.0)
test("ensemble_score max <= 1.0", scores.max() <= 1.0)

disagreement = combined_df["model_disagreement"]
test("model_disagreement min >= 0.0", disagreement.min() >= 0.0)
test("model_disagreement max <= 1.0", disagreement.max() <= 1.0)

# ---- Test Group 3: Tier Consistency & Mutual Exclusivity ----
print("\n--- Test Group 3: Tier Classification Logic ---")
valid_tiers = {"CRITICAL_CONSENSUS", "TREE_ISOLATED", "NEURAL_IRREGULARITY", "NORMAL"}
all_tiers_valid = set(combined_df["ensemble_tier"]).issubset(valid_tiers)
test("All assigned tiers are in valid set", all_tiers_valid)

# Consistency checks
both_flag = combined_df["if_is_anomaly"] & combined_df["ae_is_anomaly"]
test("CRITICAL_CONSENSUS exactly matches both flags", (combined_df["ensemble_tier"] == "CRITICAL_CONSENSUS").equals(both_flag))

if_only = combined_df["if_is_anomaly"] & ~combined_df["ae_is_anomaly"]
test("TREE_ISOLATED exactly matches IF only", (combined_df["ensemble_tier"] == "TREE_ISOLATED").equals(if_only))

ae_only = ~combined_df["if_is_anomaly"] & combined_df["ae_is_anomaly"]
test("NEURAL_IRREGULARITY exactly matches AE only", (combined_df["ensemble_tier"] == "NEURAL_IRREGULARITY").equals(ae_only))

neither = ~combined_df["if_is_anomaly"] & ~combined_df["ae_is_anomaly"]
test("NORMAL exactly matches neither flag", (combined_df["ensemble_tier"] == "NORMAL").equals(neither))

test("consensus_flagged is boolean", combined_df["consensus_flagged"].dtype == bool)
test("ensemble_flagged captures union of anomalies", (combined_df["ensemble_flagged"] == (both_flag | if_only | ae_only)).all())

# ---- Test Group 4: Risk Differentiation ----
print("\n--- Test Group 4: Risk Differentiation ---")
critical_mean = combined_df[combined_df["ensemble_tier"] == "CRITICAL_CONSENSUS"]["ensemble_score"].mean()
normal_mean = combined_df[combined_df["ensemble_tier"] == "NORMAL"]["ensemble_score"].mean()
test("Critical consensus anomaly score is significantly higher than normal score (> 2x)", critical_mean > (2.0 * normal_mean))

# ---- Test Group 5: Priority Ranking Validation ----
print("\n--- Test Group 5: Audit Priority Ranking ---")
ranks = combined_df["audit_priority_rank"]
test("audit_priority_rank has rank 1", ranks.min() == 1)
test("audit_priority_rank max is within 774", ranks.max() <= 774)
test("Rank 1 has the highest ensemble score", combined_df.loc[ranks.idxmin(), "ensemble_score"] == scores.max())

# ---- Test Group 6: Summary Statistics Engine ----
print("\n--- Test Group 6: Summary Statistics Engine ---")
stats = ensemble.get_summary_stats(combined_df)
test("Total MPs in stats equals 774", stats["total_mps"] == 774)
test("Sum of tiers equals total MPs", (stats["critical_consensus"] + stats["tree_isolated_only"] + stats["neural_irregularity_only"] + stats["normal"]) == 774)

# ---- Test Group 7: End-to-End Pipeline Runner ----
print("\n--- Test Group 7: End-to-End Pipeline Runner ---")
pipe_mps, pipe_works, pipe_ens, m1, m2, m3 = run_ensemble_pipeline(feats)
test("Pipeline returns 774 scored MPs", len(pipe_mps) == 774)
test("Pipeline returns 44028 scored works", len(pipe_works) == 44028)
test("Pipeline returns fitted models", m1.is_fitted and m2.is_fitted and m3.is_fitted)

# ---- Summary ----
print("\n" + "=" * 60)
print(f"RESULTS: {passed}/{total} tests passed, {failed} failed")
if failed == 0:
    print("ALL TESTS PASSED")
else:
    print(f"WARNING: {failed} test(s) failed!")
print("=" * 60)
