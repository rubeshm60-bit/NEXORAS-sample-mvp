"""
NEXORAS Module 1 — Data Ingestion Tests
Tests that all 4 datasets load correctly, columns are normalized,
dates are parsed, and useless columns are dropped.
"""
import sys
sys.path.insert(0, r"D:\sih 2026\sample mvp\NEXORAS-sample-mvp")

from backend.ingestion.loader import (
    load_mp_summary,
    load_completed_works,
    load_expenditures,
    load_recommended_works,
    load_all,
)
from backend.ingestion.validator import validate_all

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
print("NEXORAS — Module 1 Test Suite")
print("=" * 60)

# ---- Load all datasets ----
print("\n--- Loading datasets ---")
data = load_all()

# ---- Test 1: Row counts ----
print("\n--- Test: Row counts ---")
test("mp_summary has 774 rows", data["mp_summary"].shape[0] == 774)
test("completed_works has ~44028 rows", data["completed_works"].shape[0] > 43000)
test("expenditures has ~108695 rows", data["expenditures"].shape[0] > 100000)
test("recommended_works has ~88880 rows", data["recommended_works"].shape[0] > 85000)

# ---- Test 2: Column names are snake_case (no spaces, no special chars) ----
print("\n--- Test: Column name normalization ---")
import re
for name, df in data.items():
    all_snake = all(re.match(r'^[a-z][a-z0-9_]*$', c) for c in df.columns)
    test(f"{name} columns are snake_case", all_snake)
    if not all_snake:
        bad = [c for c in df.columns if not re.match(r'^[a-z][a-z0-9_]*$', c)]
        print(f"    Bad columns: {bad}")

# ---- Test 3: Date columns are datetime ----
print("\n--- Test: Date parsing ---")
import pandas as pd
test(
    "completed_works.completed_date is datetime",
    pd.api.types.is_datetime64_any_dtype(data["completed_works"]["completed_date"]),
)
test(
    "expenditures.expenditure_date is datetime",
    pd.api.types.is_datetime64_any_dtype(data["expenditures"]["expenditure_date"]),
)
test(
    "recommended_works.recommendation_date is datetime",
    pd.api.types.is_datetime64_any_dtype(data["recommended_works"]["recommendation_date"]),
)

# ---- Test 4: average_rating column dropped ----
print("\n--- Test: Useless columns dropped ---")
test(
    "mp_summary has no average_rating",
    "average_rating" not in data["mp_summary"].columns,
)
test(
    "completed_works has no average_rating",
    "average_rating" not in data["completed_works"].columns,
)

# ---- Test 5: No completely empty DataFrames ----
print("\n--- Test: DataFrames not empty ---")
for name, df in data.items():
    test(f"{name} is not empty", not df.empty)

# ---- Test 6: Validation ----
print("\n--- Test: Validation passes ---")
results = validate_all(data)
for name, (valid, issues) in results.items():
    test(f"{name} passes validation", valid)

# ---- Summary ----
print("\n" + "=" * 60)
print(f"RESULTS: {passed}/{total} tests passed, {failed} failed")
if failed == 0:
    print("ALL TESTS PASSED")
else:
    print(f"WARNING: {failed} test(s) failed!")
print("=" * 60)
