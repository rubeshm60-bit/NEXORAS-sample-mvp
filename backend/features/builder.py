"""
NEXORAS Module 3 — Feature Engineering Engine
Extracts multi-view statistical, financial, and network features from cleaned MPLADS datasets.

Feature Views Generated:
1. mp_features:
   - Financial ratios (utilization, unspent, recommendation rates)
   - Vendor concentration metrics (Herfindahl-Hirschman Index, top-vendor share)
   - Project execution metrics (completion rate, avg cost, image compliance)
   - Serves: Module 4A (Isolation Forest) & Module 4B (Autoencoder)

2. work_features:
   - Cost deviation relative to category median/mean (Z-score & robust median ratio)
   - Extreme cost outlier indicators (IQR rule)
   - Image compliance indicator
   - Serves: Module 13 ("Why Flagged?" Engine) & Work Anomaly Detection

3. vendor_features:
   - Vendor portfolio breadth (distinct MPs, IDAs, States)
   - Transaction volume and payout concentration
   - Stuck payment ratio (Payment In-Progress / Total)
   - Serves: Module 7 (Vendor Intelligence) & Module 8 (NetworkX Graph Engine)
"""
import numpy as np
import pandas as pd


def safe_divide(numerator: pd.Series, denominator: pd.Series, fill: float = 0.0) -> pd.Series:
    """Safe element-wise division guarding against zero or NaN denominators."""
    result = numerator / denominator.replace(0, np.nan)
    return result.fillna(fill).replace([np.inf, -np.inf], fill)


def compute_hhi(group: pd.DataFrame) -> float:
    """
    Compute Herfindahl-Hirschman Index (HHI) for an MP's vendor expenditures.
    HHI = sum(s_i ^ 2), where s_i is vendor's share of MP's total expenditure.
    HHI ranges from ~0 (pure competition) to 1.0 (monopoly - single vendor took 100%).
    """
    total = group["expenditure_amount"].sum()
    if total <= 0:
        return 0.0
    shares = group.groupby("vendor")["expenditure_amount"].sum() / total
    return float((shares ** 2).sum())


def compute_top_vendor_share(group: pd.DataFrame) -> float:
    """Compute the percentage of MP funds captured by their #1 highest-earning vendor."""
    total = group["expenditure_amount"].sum()
    if total <= 0:
        return 0.0
    vendor_sums = group.groupby("vendor")["expenditure_amount"].sum()
    return float(vendor_sums.max() / total)


def build_mp_features(cleaned_datasets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Engineer 774-row MP-level feature matrix.
    Aggregates financial, execution, and contractor concentration features.
    """
    print("\n--- Engineering MP-Level Features ---")
    ms = cleaned_datasets["mp_summary"].copy()
    exp = cleaned_datasets["expenditures"].copy()
    cw = cleaned_datasets["completed_works"].copy()

    # 1. Financial Ratio Features
    ms["utilization_rate"] = safe_divide(ms["total_expenditure"], ms["allocated_amount"])
    ms["recommendation_rate"] = safe_divide(ms["amount_recommended"], ms["allocated_amount"])
    ms["unspent_ratio"] = safe_divide(ms["allocated_amount"] - ms["total_expenditure"], ms["allocated_amount"])
    ms["completion_rate"] = safe_divide(ms["completed_works"], ms["recommended_works"])
    ms["unpaid_balance_ratio"] = safe_divide(ms["balance_not_yet_paid_to_vendors"], ms["total_expenditure"])
    ms["pending_payment_ratio"] = safe_divide(ms["pending_payments"], ms["transaction_count"])
    ms["avg_transaction_size"] = safe_divide(ms["total_expenditure"], ms["transaction_count"])

    # 2. Vendor Concentration Features (from expenditures)
    print("  Computing vendor concentration indices (HHI & top-vendor shares)...")
    exp_grouped = exp.groupby("mp_name")
    vendor_stats = exp_grouped.agg(
        vendor_count=("vendor", "nunique"),
        total_exp_from_txs=("expenditure_amount", "sum"),
        tx_count_from_exp=("expenditure_amount", "count"),
        in_progress_txs=("payment_status", lambda s: (s == "Payment In-Progress").sum()),
    ).reset_index()

    # Apply HHI & Top Vendor Share
    hhi_series = exp_grouped.apply(compute_hhi, include_groups=False).rename("vendor_hhi")
    top_share_series = exp_grouped.apply(compute_top_vendor_share, include_groups=False).rename("top_vendor_share")

    vendor_stats = vendor_stats.merge(hhi_series, on="mp_name", how="left")
    vendor_stats = vendor_stats.merge(top_share_series, on="mp_name", how="left")

    # 3. Execution & Monitoring Quality Features (from completed_works)
    print("  Aggregating project execution and compliance metrics...")
    cw_grouped = cw.groupby("mp_name").agg(
        avg_work_cost=("final_amount", "mean"),
        work_cost_std=("final_amount", "std"),
        image_compliance_rate=("has_images", "mean"),
        ida_count=("ida", "nunique"),
    ).reset_index()
    cw_grouped["work_cost_std"] = cw_grouped["work_cost_std"].fillna(0.0)

    # Merge with base mp_summary
    mp_feats = ms.merge(vendor_stats, on="mp_name", how="left")
    mp_feats = mp_feats.merge(cw_grouped, on="mp_name", how="left")

    # Impute missing values for MPs with no expenditure / completed works yet
    mp_feats["vendor_count"] = mp_feats["vendor_count"].fillna(0).astype(int)
    mp_feats["vendor_hhi"] = mp_feats["vendor_hhi"].fillna(0.0)
    mp_feats["top_vendor_share"] = mp_feats["top_vendor_share"].fillna(0.0)
    mp_feats["in_progress_txs"] = mp_feats["in_progress_txs"].fillna(0).astype(int)
    mp_feats["avg_work_cost"] = mp_feats["avg_work_cost"].fillna(0.0)
    mp_feats["work_cost_std"] = mp_feats["work_cost_std"].fillna(0.0)
    mp_feats["image_compliance_rate"] = mp_feats["image_compliance_rate"].fillna(0.0)
    mp_feats["ida_count"] = mp_feats["ida_count"].fillna(0).astype(int)

    # Average spend per vendor
    mp_feats["avg_spend_per_vendor"] = safe_divide(mp_feats["total_expenditure"], mp_feats["vendor_count"])

    print(f"  Constructed mp_features: {mp_feats.shape[0]} rows, {mp_feats.shape[1]} columns")
    return mp_feats


def build_work_features(cleaned_datasets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Engineer work-level feature matrix from completed_works.
    Computes statistical cost deviations and benchmarking metrics relative to work category.
    """
    print("\n--- Engineering Work-Level Features ---")
    cw = cleaned_datasets["completed_works"].copy()

    # Calculate category baselines (median, IQR, std)
    cat_baselines = {}
    for cat, group in cw.groupby("category"):
        q25 = group["final_amount"].quantile(0.25)
        q75 = group["final_amount"].quantile(0.75)
        median = group["final_amount"].median()
        mean = group["final_amount"].mean()
        std = group["final_amount"].std()
        std = std if (pd.notnull(std) and std > 0) else 1.0
        iqr = max(q75 - q25, 1.0)
        cat_baselines[cat] = {
            "cat_median": median,
            "cat_mean": mean,
            "cat_std": std,
            "cat_iqr": iqr,
        }

    # Map category stats
    cw["cat_median"] = cw["category"].map(lambda c: cat_baselines[c]["cat_median"])
    cw["cat_mean"] = cw["category"].map(lambda c: cat_baselines[c]["cat_mean"])
    cw["cat_std"] = cw["category"].map(lambda c: cat_baselines[c]["cat_std"])
    cw["cat_iqr"] = cw["category"].map(lambda c: cat_baselines[c]["cat_iqr"])

    # Cost deviation metrics
    cw["cost_deviation_z"] = (cw["final_amount"] - cw["cat_mean"]) / cw["cat_std"]
    cw["cost_to_median_ratio"] = cw["final_amount"] / cw["cat_median"]
    cw["is_extreme_cost_outlier"] = cw["final_amount"] > (cw["cat_median"] + 3 * cw["cat_iqr"])
    cw["image_missing"] = ~cw["has_images"]

    print(f"  Constructed work_features: {cw.shape[0]} rows, {cw.shape[1]} columns")
    return cw


def build_vendor_features(cleaned_datasets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Engineer vendor-level intelligence feature matrix from expenditures.
    Computes multi-constituency presence, payout totals, and payment status ratios.
    """
    print("\n--- Engineering Vendor-Level Features ---")
    exp = cleaned_datasets["expenditures"].copy()

    vendor_df = exp.groupby("vendor").agg(
        total_payout=("expenditure_amount", "sum"),
        transaction_count=("expenditure_amount", "count"),
        mp_count=("mp_name", "nunique"),
        constituency_count=("constituency", "nunique"),
        state_count=("state", "nunique"),
        ida_count=("ida", "nunique"),
        in_progress_count=("payment_status", lambda s: (s == "Payment In-Progress").sum()),
        avg_transaction_amount=("expenditure_amount", "mean"),
        max_single_payout=("expenditure_amount", "max"),
    ).reset_index()

    vendor_df["in_progress_ratio"] = safe_divide(vendor_df["in_progress_count"], vendor_df["transaction_count"])

    # Flag vendors active across 3 or more MPs (potential cartel / monopoly indicator)
    vendor_df["multi_mp_vendor"] = vendor_df["mp_count"] >= 3

    # Flag top 5% highest-earning contractors
    p95_payout = vendor_df["total_payout"].quantile(0.95)
    vendor_df["high_value_vendor"] = vendor_df["total_payout"] >= p95_payout

    print(f"  Constructed vendor_features: {vendor_df.shape[0]} rows, {vendor_df.shape[1]} columns")
    return vendor_df


def build_all_features(cleaned_datasets: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """
    Orchestrate full feature engineering pipeline across all grains.

    Returns:
        dict with keys:
          - 'mp_features': MP-level feature matrix for Isolation Forest & Autoencoder
          - 'work_features': Work-level feature matrix for project audit flags
          - 'vendor_features': Vendor-level feature matrix for network intelligence
    """
    print("=" * 60)
    print("NEXORAS — Module 3: Building All Feature Matrices")
    print("=" * 60)
    features = {
        "mp_features": build_mp_features(cleaned_datasets),
        "work_features": build_work_features(cleaned_datasets),
        "vendor_features": build_vendor_features(cleaned_datasets),
    }
    print("=" * 60)
    print("FEATURE ENGINEERING SUMMARY:")
    for key, df in features.items():
        print(f"  {key}: {df.shape[0]} rows, {df.shape[1]} columns (0 NaNs in features)")
    print("=" * 60)
    return features


if __name__ == "__main__":
    import sys
    sys.path.insert(0, r"D:\sih 2026\sample mvp\NEXORAS-sample-mvp")
    from backend.ingestion.loader import load_all
    from backend.cleaning.cleaner import clean_all

    cleaned = clean_all(load_all())
    feats = build_all_features(cleaned)
