"""
NEXORAS Module 1 — Data Validator
Validates loaded DataFrames for completeness, duplicates, and integrity.
"""
import pandas as pd


def validate_dataframe(df: pd.DataFrame, name: str) -> tuple[bool, list[str]]:
    """
    Validate a single DataFrame.

    Checks:
    1. Not empty
    2. No fully empty columns
    3. Duplicate row count
    4. Null percentage per column

    Returns:
        (is_valid, issues) — is_valid is True if no critical issues found.
    """
    issues = []

    # Check 1: Not empty
    if df.empty:
        issues.append(f"CRITICAL: {name} is empty!")
        return False, issues

    # Check 2: Fully empty columns
    empty_cols = [c for c in df.columns if df[c].isnull().all()]
    if empty_cols:
        issues.append(f"WARNING: {name} has fully empty columns: {empty_cols}")

    # Check 3: Duplicates
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        dup_pct = dup_count / len(df) * 100
        severity = "CRITICAL" if dup_pct > 50 else "WARNING"
        issues.append(
            f"{severity}: {name} has {dup_count} duplicate rows ({dup_pct:.1f}%)"
        )

    # Check 4: High null percentage
    for col in df.columns:
        null_pct = df[col].isnull().sum() / len(df) * 100
        if null_pct > 50:
            issues.append(
                f"INFO: {name}.{col} is {null_pct:.1f}% null"
            )

    # Print report
    print(f"\n--- Validation: {name} ---")
    print(f"  Rows: {len(df)} | Cols: {len(df.columns)}")
    print(f"  Duplicates: {dup_count}")
    if issues:
        for issue in issues:
            print(f"  {issue}")
    else:
        print("  All checks passed.")

    is_valid = not any("CRITICAL" in i for i in issues)
    return is_valid, issues


def validate_all(datasets: dict[str, pd.DataFrame]) -> dict[str, tuple[bool, list[str]]]:
    """
    Validate all datasets.

    Args:
        datasets: dict from load_all() — keys are dataset names, values are DataFrames.

    Returns:
        dict of {name: (is_valid, issues)}
    """
    print("=" * 60)
    print("NEXORAS — Validating all datasets")
    print("=" * 60)

    results = {}
    for name, df in datasets.items():
        is_valid, issues = validate_dataframe(df, name)
        results[name] = (is_valid, issues)

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    all_valid = True
    for name, (valid, issues) in results.items():
        status = "PASS" if valid else "FAIL"
        issue_count = len(issues)
        print(f"  {name}: {status} ({issue_count} issues)")
        if not valid:
            all_valid = False

    overall = "ALL PASSED" if all_valid else "ISSUES FOUND"
    print(f"\n  Overall: {overall}")
    return results


if __name__ == "__main__":
    # Quick standalone test
    import sys
    sys.path.insert(0, r"D:\sih 2026\sample mvp\NEXORAS-sample-mvp")
    from backend.ingestion.loader import load_all

    datasets = load_all()
    validate_all(datasets)
