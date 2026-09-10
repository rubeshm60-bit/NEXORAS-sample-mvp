"""
NEXORAS Module 1 — Data Loader
Loads, normalizes, and returns the 4 MPLADS CSV datasets as pandas DataFrames.

Dataset source: eSAKSHI portal data via dataful.in
All column names are normalized to snake_case.
Date columns are parsed to datetime. Rupee symbol removed from column names.
"""
import os
import re
import pandas as pd

# ============================================================
# CONFIGURATION
# ============================================================
DATASET_DIR = r"D:\sih 2026\mplads dataset"

# File names
MP_SUMMARY_FILE = "mplads_mp_summary_2026-09-10.csv"
COMPLETED_WORKS_FILE = "mplads_completed_works_2026-09-10.csv"
EXPENDITURES_FILE = "mplads_expenditures_2026-09-10.csv"
RECOMMENDED_WORKS_FILE = "mplads_recommended_works_2026-09-10.csv"


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize column names to snake_case.
    - Strip whitespace
    - Remove rupee symbol and parentheses
    - Replace spaces with underscores
    - Lowercase everything
    - Remove consecutive underscores
    """
    new_cols = {}
    for col in df.columns:
        clean = col.strip()
        clean = clean.replace("₹", "").replace("(", "").replace(")", "")
        clean = clean.replace("%", "pct")
        clean = re.sub(r"\s+", "_", clean)
        clean = re.sub(r"_+", "_", clean)
        clean = clean.strip("_").lower()
        new_cols[col] = clean
    return df.rename(columns=new_cols)


def _parse_dates(df: pd.DataFrame, date_cols: list[str]) -> pd.DataFrame:
    """Parse ISO date string columns to datetime."""
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", utc=True)
            df[col] = df[col].dt.tz_localize(None)  # Remove timezone for simplicity
    return df


def load_mp_summary() -> pd.DataFrame:
    """
    Load the MP summary dataset.
    774 rows × 16 columns.
    Contains per-MP: allocated, recommended, expenditure, utilization,
    completed/recommended works count, completion rate, vendor balance,
    transaction counts.
    """
    path = os.path.join(DATASET_DIR, MP_SUMMARY_FILE)
    df = pd.read_csv(path, low_memory=False)
    df = _normalize_columns(df)

    # Drop average_rating (770/774 null — useless)
    if "average_rating" in df.columns:
        df = df.drop(columns=["average_rating"])

    print(f"Loaded mp_summary: {df.shape[0]} rows, {df.shape[1]} cols")
    return df


def load_completed_works() -> pd.DataFrame:
    """
    Load the completed works dataset.
    45,817 rows × 12 columns.
    Contains per-work: Work ID, description, category, MP, constituency,
    state, house, final amount, completed date, has images, IDA.
    """
    path = os.path.join(DATASET_DIR, COMPLETED_WORKS_FILE)
    df = pd.read_csv(path, low_memory=False)
    df = _normalize_columns(df)
    df = _parse_dates(df, ["completed_date"])

    # Drop average_rating (ALL NULL)
    if "average_rating" in df.columns:
        df = df.drop(columns=["average_rating"])

    print(f"Loaded completed_works: {df.shape[0]} rows, {df.shape[1]} cols")
    return df


def load_expenditures() -> pd.DataFrame:
    """
    Load the expenditures dataset.
    108,695 rows × 10 columns.
    Contains per-transaction: MP, constituency, state, house,
    work description, VENDOR, IDA, expenditure amount, date, payment status.

    CRITICAL: This is the only dataset with Vendor information —
    essential for NetworkX graph construction.
    """
    path = os.path.join(DATASET_DIR, EXPENDITURES_FILE)
    df = pd.read_csv(path, low_memory=False)
    df = _normalize_columns(df)
    df = _parse_dates(df, ["expenditure_date"])

    print(f"Loaded expenditures: {df.shape[0]} rows, {df.shape[1]} cols")
    return df


def load_recommended_works() -> pd.DataFrame:
    """
    Load the recommended works dataset.
    88,880 rows × 11 columns.
    Contains per-work: Work ID, description, category, MP, constituency,
    state, house, recommended amount, recommendation date, has images, IDA.
    """
    path = os.path.join(DATASET_DIR, RECOMMENDED_WORKS_FILE)
    df = pd.read_csv(path, low_memory=False)
    df = _normalize_columns(df)
    df = _parse_dates(df, ["recommendation_date"])

    print(f"Loaded recommended_works: {df.shape[0]} rows, {df.shape[1]} cols")
    return df


def load_all() -> dict[str, pd.DataFrame]:
    """
    Load all 4 MPLADS datasets and return as a dictionary.

    Returns:
        dict with keys: 'mp_summary', 'completed_works', 'expenditures', 'recommended_works'
    """
    print("=" * 60)
    print("NEXORAS — Loading all MPLADS datasets...")
    print("=" * 60)
    datasets = {
        "mp_summary": load_mp_summary(),
        "completed_works": load_completed_works(),
        "expenditures": load_expenditures(),
        "recommended_works": load_recommended_works(),
    }
    print("=" * 60)
    total_rows = sum(df.shape[0] for df in datasets.values())
    print(f"Total: {total_rows} rows across {len(datasets)} datasets")
    print("=" * 60)
    return datasets


# ============================================================
# STANDALONE TEST
# ============================================================
if __name__ == "__main__":
    data = load_all()
    print()
    for name, df in data.items():
        print(f"{name}: columns = {list(df.columns)}")
