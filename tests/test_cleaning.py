"""
NEXORAS Module 2 — Data Cleaning Tests
Tests that cleaning operations work correctly:
- Deduplication
- Null filling
- Category standardization
- No data loss on clean datasets
"""
import sys
sys.path.insert(0, r"D:\sih 2026\sample mvp\NEXORAS-sample-mvp")

from backend.ingestion.loader import load_all
from backend.cleaning.cleaner import clean_all

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
print("NEXORAS — Module 2 Test Suite (Data Cleaning)")
print("=" * 60)

# Load raw + clean
raw = load_all()
cleaned = clean_all(raw)

# ---- Test 1: Expenditures deduplication ----
print("\n--- Test: Expenditure deduplication ---")
test(
    "expenditures rows reduced after dedup",
    len(cleaned["expenditures"]) < len(raw["expenditures"]),
)
test(
    "expenditures has no remaining duplicates",
    cleaned["expenditures"].duplicated().sum() == 0,
)
test(
    "expenditures deduped to ~76313 rows",
    70000 < len(cleaned["expenditures"]) < 80000,
)

# ---- Test 2: MP summary preserved (no rows removed) ----
print("\n--- Test: MP summary preservation ---")
test(
    "mp_summary row count unchanged",
    len(cleaned["mp_summary"]) == len(raw["mp_summary"]),
)
test(
    "mp_summary has 774 rows",
    len(cleaned["mp_summary"]) == 774,
)

# ---- Test 3: Null work_description filled ----
print("\n--- Test: Null work_description filled ---")
test(
    "completed_works has 0 null work_descriptions",
    cleaned["completed_works"]["work_description"].isnull().sum() == 0,
)
test(
    "recommended_works has 0 null work_descriptions",
    cleaned["recommended_works"]["work_description"].isnull().sum() == 0,
)

# ---- Test 4: NaN categories standardized ----
print("\n--- Test: Category standardization ---")
test(
    "completed_works has no NaN categories",
    cleaned["completed_works"]["category"].isnull().sum() == 0,
)
test(
    "recommended_works has no NaN categories",
    cleaned["recommended_works"]["category"].isnull().sum() == 0,
)
test(
    "completed_works contains 'Uncategorized'",
    "Uncategorized" in cleaned["completed_works"]["category"].values,
)

# ---- Test 5: No negative financial values ----
print("\n--- Test: Financial value integrity ---")
test(
    "expenditures has no negative amounts",
    (cleaned["expenditures"]["expenditure_amount"] < 0).sum() == 0,
)
test(
    "completed_works has no negative amounts",
    (cleaned["completed_works"]["final_amount"] < 0).sum() == 0,
)
test(
    "recommended_works has no negative amounts",
    (cleaned["recommended_works"]["recommended_amount"] < 0).sum() == 0,
)

# ---- Test 6: No completely empty columns ----
print("\n--- Test: No empty columns ---")
for name, df in cleaned.items():
    empty_cols = [c for c in df.columns if df[c].isnull().all()]
    test(f"{name} has no fully empty columns", len(empty_cols) == 0)

# ---- Test 7: DataFrames not empty ----
print("\n--- Test: DataFrames not empty ---")
for name, df in cleaned.items():
    test(f"{name} is not empty", not df.empty)

# ---- Test 8: Column counts unchanged ----
print("\n--- Test: Column counts unchanged ---")
for name in cleaned:
    test(
        f"{name} column count unchanged",
        len(cleaned[name].columns) == len(raw[name].columns),
    )

# ---- Summary ----
print("\n" + "=" * 60)
print(f"RESULTS: {passed}/{total} tests passed, {failed} failed")
if failed == 0:
    print("ALL TESTS PASSED")
else:
    print(f"WARNING: {failed} test(s) failed!")
print("=" * 60)
