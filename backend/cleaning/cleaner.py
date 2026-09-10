"""
NEXORAS Module 2 — Data Cleaning & Validation
Cleans raw DataFrames produced by Module 1 (loader.py).

Cleaning operations:
1. Deduplicate expenditures (32,382 true export duplicates)
2. Fill null work_description with "[No description]"
3. Standardize NaN category values to "Uncategorized"
4. Strip whitespace from all string columns
5. Flag zero-allocation MPs

Each function returns a NEW DataFrame (no in-place mutation).
Every cleaning step is logged with before/after counts.
"""
import pandas as pd


def _log(name: str, action: str, before: int, after: int):
    """Print a cleaning log line."""
    removed = before - after
    print(f"  [{name}] {action}: {before} -> {after} ({removed} removed)")


def _strip_strings(df: pd.DataFrame) -> pd.DataFrame:
    """Strip leading/trailing whitespace from all string columns."""
    str_cols = df.select_dtypes(include=["object", "string"]).columns
    for col in str_cols:
        df[col] = df[col].str.strip()
    return df


def clean_mp_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the MP summary dataset.

    Operations:
    - Strip whitespace from string columns
    - Flag MPs with zero allocation (keeps them in dataset but logs them)

    No rows are removed — every MP should be preserved.
    """
    print("\n--- Cleaning: mp_summary ---")
    result = df.copy()
    result = _strip_strings(result)

    # Flag zero-allocation MPs (don't remove — they're real data)
    zero_alloc = result[result["allocated_amount"] == 0]
    if len(zero_alloc) > 0:
        print(f"  WARNING: {len(zero_alloc)} MP(s) with zero allocation:")
        for _, row in zero_alloc.iterrows():
            print(f"    - {row['mp_name']} ({row['constituency']}, {row['state']})")

    _log("mp_summary", "Final", len(df), len(result))
    return result


def clean_completed_works(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the completed works dataset.

    Operations:
    - Strip whitespace from string columns
    - Fill null work_description with "[No description]"
    - Standardize NaN category to "Uncategorized"
    - Remove exact duplicate rows (if any)
    """
    print("\n--- Cleaning: completed_works ---")
    before = len(df)
    result = df.copy()

    # Strip strings
    result = _strip_strings(result)

    # Fill null work descriptions
    null_desc = result["work_description"].isnull().sum()
    if null_desc > 0:
        result["work_description"] = result["work_description"].fillna("[No description]")
        print(f"  Filled {null_desc} null work_description(s)")

    # Standardize NaN category
    null_cat = result["category"].isnull().sum()
    if null_cat > 0:
        result["category"] = result["category"].fillna("Uncategorized")
        print(f"  Filled {null_cat} null category -> 'Uncategorized'")

    # Remove exact duplicates
    result = result.drop_duplicates()
    _log("completed_works", "Dedup", before, len(result))

    return result


def clean_expenditures(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the expenditures dataset.

    Operations:
    - Strip whitespace from string columns
    - Remove 32,382 exact duplicate rows (data export artifacts)
    - Validate: no negative or zero amounts (already confirmed clean)

    This is the most critical cleaning step — expenditures had 29.8% duplicates.
    """
    print("\n--- Cleaning: expenditures ---")
    before = len(df)
    result = df.copy()

    # Strip strings
    result = _strip_strings(result)

    # Deduplicate — this is the big one
    result = result.drop_duplicates()
    _log("expenditures", "Dedup", before, len(result))

    return result


def clean_recommended_works(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the recommended works dataset.

    Operations:
    - Strip whitespace from string columns
    - Fill null work_description with "[No description]"
    - Standardize NaN category to "Uncategorized"
    - Remove exact duplicate rows (if any)
    """
    print("\n--- Cleaning: recommended_works ---")
    before = len(df)
    result = df.copy()

    # Strip strings
    result = _strip_strings(result)

    # Fill null work descriptions
    null_desc = result["work_description"].isnull().sum()
    if null_desc > 0:
        result["work_description"] = result["work_description"].fillna("[No description]")
        print(f"  Filled {null_desc} null work_description(s)")

    # Standardize NaN category
    null_cat = result["category"].isnull().sum()
    if null_cat > 0:
        result["category"] = result["category"].fillna("Uncategorized")
        print(f"  Filled {null_cat} null category -> 'Uncategorized'")

    # Remove exact duplicates
    result = result.drop_duplicates()
    _log("recommended_works", "Dedup", before, len(result))

    return result


def clean_all(datasets: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """
    Clean all 4 datasets.

    Args:
        datasets: dict from loader.load_all()

    Returns:
        dict with same keys, cleaned DataFrames as values.
    """
    print("=" * 60)
    print("NEXORAS — Cleaning all datasets")
    print("=" * 60)

    cleaned = {
        "mp_summary": clean_mp_summary(datasets["mp_summary"]),
        "completed_works": clean_completed_works(datasets["completed_works"]),
        "expenditures": clean_expenditures(datasets["expenditures"]),
        "recommended_works": clean_recommended_works(datasets["recommended_works"]),
    }

    print("\n" + "=" * 60)
    print("CLEANING SUMMARY")
    print("=" * 60)
    total_before = sum(len(df) for df in datasets.values())
    total_after = sum(len(df) for df in cleaned.values())
    print(f"  Total rows before: {total_before}")
    print(f"  Total rows after:  {total_after}")
    print(f"  Rows removed:      {total_before - total_after}")
    print("=" * 60)

    return cleaned


# ============================================================
# STANDALONE TEST
# ============================================================
if __name__ == "__main__":
    import sys
    sys.path.insert(0, r"D:\sih 2026\sample mvp\NEXORAS-sample-mvp")
    from backend.ingestion.loader import load_all

    raw = load_all()
    cleaned = clean_all(raw)

    print("\n--- Column check after cleaning ---")
    for name, df in cleaned.items():
        null_total = df.isnull().sum().sum()
        print(f"  {name}: {df.shape[0]} rows, {df.shape[1]} cols, {null_total} total nulls")
