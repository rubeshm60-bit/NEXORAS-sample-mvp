"""
NEXORAS Module 3 — Feature Engineering Tests
Tests feature construction, boundary validity, mathematical sanity, and absence of NaNs/Infs.
"""
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, r"D:\sih 2026\sample mvp\NEXORAS-sample-mvp")

from backend.ingestion.loader import load_all
from backend.cleaning.cleaner import clean_all
from backend.features.builder import build_all_features

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
print("NEXORAS — Module 3 Test Suite (Feature Engineering)")
print("=" * 60)

# Pipeline: Load -> Clean -> Build Features
raw = load_all()
cleaned = clean_all(raw)
feats = build_all_features(cleaned)

mp_feats = feats["mp_features"]
work_feats = feats["work_features"]
vendor_feats = feats["vendor_features"]

# ---- Test Group 1: MP-Level Features ----
print("\n--- Test Group 1: MP-Level Features ---")
test("mp_features has exactly 774 rows", len(mp_feats) == 774)

key_mp_cols = [
    "utilization_rate",
    "unspent_ratio",
    "recommendation_rate",
    "completion_rate",
    "vendor_hhi",
    "top_vendor_share",
    "avg_transaction_size",
    "image_compliance_rate",
]

for col in key_mp_cols:
    has_nan = mp_feats[col].isnull().any()
    has_inf = np.isinf(mp_feats[col]).any()
    test(f"mp_features.{col} has no NaN or Inf", not (has_nan or has_inf))

test("vendor_hhi values are within [0.0, 1.0]", (mp_feats["vendor_hhi"] >= 0.0).all() and (mp_feats["vendor_hhi"] <= 1.0).all())
test("top_vendor_share values are within [0.0, 1.0]", (mp_feats["top_vendor_share"] >= 0.0).all() and (mp_feats["top_vendor_share"] <= 1.0).all())
test("image_compliance_rate values are within [0.0, 1.0]", (mp_feats["image_compliance_rate"] >= 0.0).all() and (mp_feats["image_compliance_rate"] <= 1.0).all())

# ---- Test Group 2: Work-Level Features ----
print("\n--- Test Group 2: Work-Level Features ---")
test("work_features has 44028 rows", len(work_feats) == 44028)

key_work_cols = ["cost_deviation_z", "cost_to_median_ratio", "is_extreme_cost_outlier", "image_missing"]
for col in key_work_cols:
    has_nan = work_feats[col].isnull().any()
    has_inf = np.isinf(work_feats[col]).any()
    test(f"work_features.{col} has no NaN or Inf", not (has_nan or has_inf))

test("work_features has positive median ratio", (work_feats["cost_to_median_ratio"] >= 0.0).all())
test("work_features identifies outliers", work_feats["is_extreme_cost_outlier"].sum() > 0)

# ---- Test Group 3: Vendor-Level Features ----
print("\n--- Test Group 3: Vendor-Level Features ---")
test("vendor_features has 28206 rows", len(vendor_feats) == 28206)

key_vendor_cols = ["total_payout", "transaction_count", "mp_count", "in_progress_ratio"]
for col in key_vendor_cols:
    has_nan = vendor_feats[col].isnull().any()
    has_inf = np.isinf(vendor_feats[col]).any()
    test(f"vendor_features.{col} has no NaN or Inf", not (has_nan or has_inf))

test("in_progress_ratio is within [0.0, 1.0]", (vendor_feats["in_progress_ratio"] >= 0.0).all() and (vendor_feats["in_progress_ratio"] <= 1.0).all())
test("multi_mp_vendor identifies vendors serving >= 3 MPs", (vendor_feats["multi_mp_vendor"] == (vendor_feats["mp_count"] >= 3)).all())
test("vendor_features has high_value_vendor flags", vendor_feats["high_value_vendor"].sum() > 0)

# ---- Summary ----
print("\n" + "=" * 60)
print(f"RESULTS: {passed}/{total} tests passed, {failed} failed")
if failed == 0:
    print("ALL TESTS PASSED")
else:
    print(f"WARNING: {failed} test(s) failed!")
print("=" * 60)
