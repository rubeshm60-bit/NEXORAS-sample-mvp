"""
NEXORAS Module 1 — Data Inspection Script
Profiles all 4 CSV datasets from the MPLADS dataset directory.
Outputs: shape, columns, dtypes, null counts, duplicates, sample values.
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import os

DATASET_DIR = r"D:\sih 2026\mplads dataset"

files = sorted([f for f in os.listdir(DATASET_DIR) if f.endswith(".csv")])

for fname in files:
    path = os.path.join(DATASET_DIR, fname)
    size_mb = os.path.getsize(path) / 1024 / 1024

    print("=" * 80)
    print(f"FILE: {fname}")
    print(f"SIZE: {size_mb:.2f} MB")

    # Read only first 1000 rows for large files to speed up inspection
    if size_mb > 10:
        df_sample = pd.read_csv(path, nrows=1000, low_memory=False)
        # Also get total row count without loading everything
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            total_rows = sum(1 for _ in fh) - 1  # subtract header
        print(f"TOTAL ROWS: {total_rows} (sampled first 1000 for profiling)")
    else:
        df_sample = pd.read_csv(path, low_memory=False)
        total_rows = len(df_sample)
        print(f"TOTAL ROWS: {total_rows}")

    print(f"COLUMNS ({len(df_sample.columns)}):")
    for col in df_sample.columns:
        non_null = df_sample[col].dropna()
        sample_val = str(non_null.iloc[0])[:60] if len(non_null) > 0 else "ALL NULL"
        null_count = df_sample[col].isnull().sum()
        print(f"  {col}")
        print(f"    dtype={df_sample[col].dtype} | nulls={null_count}/{len(df_sample)} | sample: {sample_val}")

    print(f"\nDUPLICATES in sample: {df_sample.duplicated().sum()}")
    print(f"\nFIRST 2 ROWS:")
    print(df_sample.head(2).to_string())
    print()
