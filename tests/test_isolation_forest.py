"""
NEXORAS Module 4A — Isolation Forest Tests
Tests model fitting, anomaly scoring, score calibration, serialization, explainability, and reproducibility.
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
from backend.engine.isolation_forest import (
    MPIsolationForest,
    WorkIsolationForest,
    run_isolation_forest_pipeline,
)

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
print("NEXORAS — Module 4A Test Suite (Isolation Forest Engine)")
print("=" * 60)

# Pipeline: Load -> Clean -> Build Features
raw = load_all()
cleaned = clean_all(raw)
feats = build_all_features(cleaned)

mp_feats = feats["mp_features"]
work_feats = feats["work_features"]

# ---- Test Group 1: MP-Level Isolation Forest ----
print("\n--- Test Group 1: MP-Level Model Fitting & Scoring ---")
mp_model = MPIsolationForest(contamination=0.08, random_state=42)
mp_model.fit(mp_feats)
test("mp_model.is_fitted is True", mp_model.is_fitted)

scored_mps = mp_model.score(mp_feats)
test("scored_mps contains 'if_anomaly_score'", "if_anomaly_score" in scored_mps.columns)
test("scored_mps contains 'if_is_anomaly'", "if_is_anomaly" in scored_mps.columns)
test("scored_mps has 774 rows", len(scored_mps) == 774)

scores = scored_mps["if_anomaly_score"]
test("if_anomaly_score has no NaNs", not scores.isnull().any())
test("if_anomaly_score has no Infs", not np.isinf(scores).any())
test("if_anomaly_score minimum is >= 0.0", scores.min() >= 0.0)
test("if_anomaly_score maximum is <= 1.0", scores.max() <= 1.0)

flagged_count = scored_mps["if_is_anomaly"].sum()
test("Anomaly flags generated within expected range (50-75 MPs for 8% contamination)", 50 <= flagged_count <= 75)

# ---- Test Group 2: Anomaly Ranking Sanity ----
print("\n--- Test Group 2: Ranking Sanity ---")
# MPs with HHI=1.0 and 0 completion should have above-average anomaly scores
monopoly_mps = scored_mps[(scored_mps["vendor_hhi"] >= 0.99) & (scored_mps["completion_rate"] == 0.0)]
if len(monopoly_mps) > 0:
    mean_monopoly_score = monopoly_mps["if_anomaly_score"].mean()
    overall_mean_score = scores.mean()
    test("Monopoly contractors have higher-than-average anomaly score", mean_monopoly_score > overall_mean_score)
else:
    test("Monopoly contractor check", True)

# ---- Test Group 3: Explainability Engine ----
print("\n--- Test Group 3: Explainability Output ---")
sample_mp = scored_mps.sort_values(by="if_anomaly_score", ascending=False).iloc[0]
explanations = mp_model.explain_mp(sample_mp)
test("explain_mp returns non-empty list", len(explanations) > 0)
test("explain_mp provides feature name", "feature" in explanations[0])
test("explain_mp provides observed value", "observed" in explanations[0])
test("explain_mp provides baseline median", "baseline_median" in explanations[0])
test("explain_mp provides percentage deviation", "pct_deviation" in explanations[0])

# ---- Test Group 4: Serialization & Reproducibility ----
print("\n--- Test Group 4: Serialization & Reproducibility ---")
with tempfile.TemporaryDirectory() as tmpdir:
    save_path = os.path.join(tmpdir, "mp_iso_test.joblib")
    mp_model.save(save_path)
    test("Model file exists on disk after save", os.path.exists(save_path))

    loaded_model = MPIsolationForest.load(save_path)
    test("Loaded model has is_fitted=True", loaded_model.is_fitted)

    re_scored = loaded_model.score(mp_feats)
    diff = np.abs(scored_mps["if_anomaly_score"].values - re_scored["if_anomaly_score"].values).max()
    test("Loaded model produces identical scores (max diff < 1e-6)", diff < 1e-6)

# ---- Test Group 5: Work-Level Isolation Forest ----
print("\n--- Test Group 5: Work-Level Isolation Forest ---")
work_model = WorkIsolationForest(contamination=0.03, random_state=42)
work_model.fit(work_feats)
test("work_model.is_fitted is True", work_model.is_fitted)

scored_works = work_model.score(work_feats)
test("scored_works has 44028 rows", len(scored_works) == 44028)
w_scores = scored_works["work_if_score"]
test("work_if_score within [0.0, 1.0]", (w_scores >= 0.0).all() and (w_scores <= 1.0).all())
test("work_is_anomaly flags projects (~1000-1600 works for 3% contamination)", 1000 <= scored_works["work_is_anomaly"].sum() <= 1600)

# ---- Test Group 6: Full Pipeline Runner ----
print("\n--- Test Group 6: Full Pipeline Runner ---")
pipe_mps, pipe_works, m1, m2 = run_isolation_forest_pipeline(feats)
test("Pipeline returns scored MP DataFrame", len(pipe_mps) == 774)
test("Pipeline returns scored Work DataFrame", len(pipe_works) == 44028)
test("Pipeline returns fitted models", m1.is_fitted and m2.is_fitted)

# ---- Summary ----
print("\n" + "=" * 60)
print(f"RESULTS: {passed}/{total} tests passed, {failed} failed")
if failed == 0:
    print("ALL TESTS PASSED")
else:
    print(f"WARNING: {failed} test(s) failed!")
print("=" * 60)
