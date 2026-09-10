"""
NEXORAS — Module 7: Vendor Network Intelligence Engine
=====================================================
Entity-relationship modeling, vendor profiling, syndicate/cartel detection,
and risk signal generation for MPLADS expenditure workflows.

Entities Analyzed:
  - MP (Member of Parliament)
  - Vendor (Contractor / Supplier)
  - IDA (Implementing District Authority / Agency)
  - Project / Work Description
  - Payment (Disbursement transactions)

Risk Patterns Detected:
  1. MONOPOLY_CONTRACTOR: Vendor capturing disproportionate share of an MP's total expenditures.
  2. MULTI_MP_SYNDICATE: Vendor receiving funds across >=3 MPs and >=2 states/IDAs.
  3. IDA_EXCLUSIVE_CONDUIT: Vendor receiving an unusually high share of an IDA's total disbursements.
  4. HIGH_IN_PROGRESS_RISK: Vendors with high ratio & volume of incomplete payments.
  5. HIGH_VALUE_OUTLIER: Vendors in the top 1% of total disbursements nationwide.

All signals adhere to neutral audit terminology:
  - "unusual concentration"
  - "suspicious pattern"
  - "requires audit review"
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd


def safe_divide(numerator: pd.Series, denominator: pd.Series, default: float = 0.0) -> pd.Series:
    """Safe division returning default where denominator is zero or null."""
    return np.where((denominator.isna()) | (denominator == 0), default, numerator / denominator)


@dataclass
class VendorProfile:
    """Detailed entity profile for an individual contractor/vendor."""
    vendor_name: str
    total_payout: float
    transaction_count: int
    mp_count: int
    constituency_count: int
    state_count: int
    ida_count: int
    avg_transaction_size: float
    max_single_payout: float
    in_progress_ratio: float
    vendor_risk_score: float
    risk_tier: str
    requires_audit_review: bool
    risk_flags: List[str] = field(default_factory=list)
    top_mps: List[Dict[str, Any]] = field(default_factory=list)
    top_idas: List[Dict[str, Any]] = field(default_factory=list)


class VendorNetworkIntelligence:
    """
    Core engine for vendor intelligence, entity relationship extraction,
    cartel detection, and composite risk scoring across MPLADS disbursements.
    """

    def __init__(
        self,
        min_payout_threshold: float = 500_000.0,  # ₹5 Lakh minimum for deep scrutiny
        syndicate_min_mps: int = 3,
        syndicate_min_states: int = 2,
        monopoly_share_threshold: float = 0.50,    # >= 50% of an MP's spend
        ida_capture_share_threshold: float = 0.60, # >= 60% of an IDA's spend
    ):
        self.min_payout_threshold = min_payout_threshold
        self.syndicate_min_mps = syndicate_min_mps
        self.syndicate_min_states = syndicate_min_states
        self.monopoly_share_threshold = monopoly_share_threshold
        self.ida_capture_share_threshold = ida_capture_share_threshold

        # Computed state
        self.vendor_profiles_df: Optional[pd.DataFrame] = None
        self.mp_vendor_rel_df: Optional[pd.DataFrame] = None
        self.vendor_ida_rel_df: Optional[pd.DataFrame] = None
        self.syndicate_vendors_df: Optional[pd.DataFrame] = None
        self.monopoly_contracts_df: Optional[pd.DataFrame] = None
        self.ida_conduits_df: Optional[pd.DataFrame] = None
        self.is_analyzed: bool = False

    def analyze(self, cleaned_datasets: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Execute full vendor intelligence analysis on cleaned datasets.

        Parameters:
            cleaned_datasets: Dictionary containing 'expenditures', 'mp_summary',
                             'completed_works', 'recommended_works'.

        Returns:
            pd.DataFrame: Comprehensive vendor profiles with risk metrics and audit signals.
        """
        exp = cleaned_datasets["expenditures"].copy()
        mp_sum = cleaned_datasets.get("mp_summary", pd.DataFrame()).copy()

        # Step 1: Base Vendor Aggregation
        v_agg = exp.groupby("vendor").agg(
            total_payout=("expenditure_amount", "sum"),
            transaction_count=("expenditure_amount", "count"),
            mp_count=("mp_name", "nunique"),
            constituency_count=("constituency", "nunique"),
            state_count=("state", "nunique"),
            ida_count=("ida", "nunique"),
            in_progress_count=("payment_status", lambda s: (s == "Payment In-Progress").sum()),
            successful_count=("payment_status", lambda s: (s == "Payment Success").sum()),
            avg_transaction_size=("expenditure_amount", "mean"),
            max_single_payout=("expenditure_amount", "max"),
        ).reset_index()

        v_agg["in_progress_ratio"] = safe_divide(v_agg["in_progress_count"], v_agg["transaction_count"])

        # Step 2: MP-Vendor Entity Relationships
        # Sum of expenditures per (mp_name, vendor)
        mp_v = exp.groupby(["mp_name", "vendor"]).agg(
            payout=("expenditure_amount", "sum"),
            transactions=("expenditure_amount", "count"),
            constituency=("constituency", "first"),
            state=("state", "first"),
        ).reset_index()

        # Total expenditure per MP for share calculation
        mp_totals = exp.groupby("mp_name")["expenditure_amount"].sum().reset_index()
        mp_totals.rename(columns={"expenditure_amount": "mp_total_expenditure"}, inplace=True)

        mp_v = mp_v.merge(mp_totals, on="mp_name", how="left")
        mp_v["share_of_mp_expenditure"] = safe_divide(mp_v["payout"], mp_v["mp_total_expenditure"])
        self.mp_vendor_rel_df = mp_v

        # Identify Monopoly Contracts (Vendor capturing high % of MP budget with min spend)
        monopoly_mask = (
            (mp_v["share_of_mp_expenditure"] >= self.monopoly_share_threshold) &
            (mp_v["payout"] >= self.min_payout_threshold)
        )
        self.monopoly_contracts_df = mp_v[monopoly_mask].copy()

        # Set of vendors with monopoly relationship in at least one constituency
        monopoly_vendors = set(self.monopoly_contracts_df["vendor"].unique())

        # Step 3: Vendor-IDA Entity Relationships
        v_ida = exp.groupby(["vendor", "ida"]).agg(
            payout=("expenditure_amount", "sum"),
            transactions=("expenditure_amount", "count"),
            mp_count=("mp_name", "nunique"),
        ).reset_index()

        # Total expenditure per IDA for share calculation
        ida_totals = exp.groupby("ida")["expenditure_amount"].sum().reset_index()
        ida_totals.rename(columns={"expenditure_amount": "ida_total_expenditure"}, inplace=True)

        v_ida = v_ida.merge(ida_totals, on="ida", how="left")
        v_ida["share_of_ida_expenditure"] = safe_divide(v_ida["payout"], v_ida["ida_total_expenditure"])
        self.vendor_ida_rel_df = v_ida

        # Identify IDA Conduits (Vendor capturing high % of an IDA's total budget)
        ida_conduit_mask = (
            (v_ida["share_of_ida_expenditure"] >= self.ida_capture_share_threshold) &
            (v_ida["payout"] >= self.min_payout_threshold)
        )
        self.ida_conduits_df = v_ida[ida_conduit_mask].copy()
        ida_conduit_vendors = set(self.ida_conduits_df["vendor"].unique())

        # Step 4: Multi-MP Syndicate / Cartel Candidates
        syndicate_mask = (
            (v_agg["mp_count"] >= self.syndicate_min_mps) &
            (v_agg["state_count"] >= self.syndicate_min_states) &
            (v_agg["total_payout"] >= self.min_payout_threshold)
        )
        self.syndicate_vendors_df = v_agg[syndicate_mask].copy()
        syndicate_vendors = set(self.syndicate_vendors_df["vendor"].unique())

        # Step 5: High Value Outlier (Top 1% nationwide payout)
        p99_payout = v_agg["total_payout"].quantile(0.99)
        v_agg["is_top_1pct_payout"] = v_agg["total_payout"] >= p99_payout

        # Step 6: Assign Risk Flags and Composite Risk Score
        risk_scores = []
        risk_flags_list = []
        requires_review_list = []

        for _, row in v_agg.iterrows():
            vendor = row["vendor"]
            score = 0.0
            flags = []

            is_monopoly = vendor in monopoly_vendors
            is_syndicate = vendor in syndicate_vendors
            is_ida_conduit = vendor in ida_conduit_vendors
            high_in_prog = (row["in_progress_ratio"] >= 0.25) and (row["in_progress_count"] >= 3)
            high_val = row["is_top_1pct_payout"]

            # 1. Multi-MP Syndicate (+30 pts)
            if is_syndicate:
                score += 30.0
                flags.append(f"MULTI_MP_SYNDICATE (Active across {int(row['mp_count'])} MPs in {int(row['state_count'])} states)")

            # 2. Monopoly Concentration (+25 pts)
            if is_monopoly:
                score += 25.0
                flags.append("MONOPOLY_CONTRACTOR (Captures >=50% of an MP's constituency fund)")

            # 3. IDA Exclusive Conduit (+20 pts)
            if is_ida_conduit:
                score += 20.0
                flags.append("IDA_EXCLUSIVE_CONDUIT (Dominates >=60% of an Implementing Agency's disbursements)")

            # 4. In-Progress Risk (+15 pts)
            if high_in_prog:
                score += 15.0
                flags.append(f"HIGH_IN_PROGRESS_RISK ({row['in_progress_ratio']:.1%} pending payments across {int(row['in_progress_count'])} disbursements)")

            # 5. Top 1% National Outlier (+10 pts)
            if high_val:
                score += 10.0
                flags.append(f"HIGH_VALUE_OUTLIER (Top 1% national payout)")

            # Scale adjustment for very high volume vendors with extreme multi-MP footprint
            if row["mp_count"] >= 10:
                score = min(100.0, score + 10.0)
                flags.append(f"EXTREME_MULTI_MP_FOOTPRINT (Works with {int(row['mp_count'])} different MPs)")

            score = min(100.0, max(0.0, score))
            requires_review = (score >= 30.0) or is_monopoly or is_syndicate or is_ida_conduit

            risk_scores.append(score)
            risk_flags_list.append("; ".join(flags) if flags else "NORMAL")
            requires_review_list.append(requires_review)

        v_agg["vendor_risk_score"] = risk_scores
        v_agg["risk_flags"] = risk_flags_list
        v_agg["requires_audit_review"] = requires_review_list

        # Assign Risk Tiers
        conditions = [
            v_agg["vendor_risk_score"] >= 60.0,
            v_agg["vendor_risk_score"] >= 30.0,
            v_agg["vendor_risk_score"] > 0.0,
        ]
        tier_choices = ["HIGH_RISK", "MEDIUM_RISK", "LOW_RISK"]
        v_agg["risk_tier"] = np.select(conditions, tier_choices, default="BENIGN")

        # Sort by risk score descending, then payout descending
        v_agg.sort_values(["vendor_risk_score", "total_payout"], ascending=[False, False], inplace=True)
        v_agg.reset_index(drop=True, inplace=True)
        v_agg["audit_rank"] = np.arange(1, len(v_agg) + 1)

        self.vendor_profiles_df = v_agg
        self.is_analyzed = True
        return v_agg

    def get_vendor_profile(self, vendor_name: str) -> Optional[VendorProfile]:
        """
        Retrieve structured audit profile and relationship breakdown for a specific vendor.
        """
        if not self.is_analyzed or self.vendor_profiles_df is None:
            raise RuntimeError("VendorNetworkIntelligence must be run via analyze() before querying.")

        matches = self.vendor_profiles_df[self.vendor_profiles_df["vendor"] == vendor_name]
        if matches.empty:
            return None

        row = matches.iloc[0]

        # Top MPs for this vendor
        top_mps = []
        if self.mp_vendor_rel_df is not None:
            v_mps = self.mp_vendor_rel_df[self.mp_vendor_rel_df["vendor"] == vendor_name].sort_values("payout", ascending=False)
            for _, r in v_mps.head(5).iterrows():
                top_mps.append({
                    "mp_name": r["mp_name"],
                    "constituency": r["constituency"],
                    "state": r["state"],
                    "payout": float(r["payout"]),
                    "transactions": int(r["transactions"]),
                    "share_of_mp_spend": float(r["share_of_mp_expenditure"]),
                })

        # Top IDAs for this vendor
        top_idas = []
        if self.vendor_ida_rel_df is not None:
            v_idas = self.vendor_ida_rel_df[self.vendor_ida_rel_df["vendor"] == vendor_name].sort_values("payout", ascending=False)
            for _, r in v_idas.head(5).iterrows():
                top_idas.append({
                    "ida": r["ida"],
                    "payout": float(r["payout"]),
                    "transactions": int(r["transactions"]),
                    "share_of_ida_spend": float(r["share_of_ida_expenditure"]),
                })

        flags = [f.strip() for f in str(row["risk_flags"]).split(";") if f.strip() and f.strip() != "NORMAL"]

        return VendorProfile(
            vendor_name=str(row["vendor"]),
            total_payout=float(row["total_payout"]),
            transaction_count=int(row["transaction_count"]),
            mp_count=int(row["mp_count"]),
            constituency_count=int(row["constituency_count"]),
            state_count=int(row["state_count"]),
            ida_count=int(row["ida_count"]),
            avg_transaction_size=float(row["avg_transaction_size"]),
            max_single_payout=float(row["max_single_payout"]),
            in_progress_ratio=float(row["in_progress_ratio"]),
            vendor_risk_score=float(row["vendor_risk_score"]),
            risk_tier=str(row["risk_tier"]),
            requires_audit_review=bool(row["requires_audit_review"]),
            risk_flags=flags,
            top_mps=top_mps,
            top_idas=top_idas,
        )

    def get_mp_vendor_breakdown(self, mp_name: str) -> Dict[str, Any]:
        """
        Retrieve vendor distribution, concentration metrics, and monopoly flags for an MP.
        """
        if not self.is_analyzed or self.mp_vendor_rel_df is None:
            raise RuntimeError("VendorNetworkIntelligence must be run via analyze() before querying.")

        mp_records = self.mp_vendor_rel_df[self.mp_vendor_rel_df["mp_name"] == mp_name].sort_values("payout", ascending=False)
        if mp_records.empty:
            return {
                "mp_name": mp_name,
                "total_expenditure": 0.0,
                "vendor_count": 0,
                "top_vendor": None,
                "top_vendor_share": 0.0,
                "vendor_hhi": 0.0,
                "has_monopoly_vendor": False,
                "vendors": [],
            }

        total_spend = mp_records["payout"].sum()
        shares = mp_records["payout"] / (total_spend if total_spend > 0 else 1.0)
        hhi = float((shares ** 2).sum())
        top_share = float(shares.iloc[0]) if not shares.empty else 0.0

        vendor_list = []
        for _, r in mp_records.head(10).iterrows():
            vendor_list.append({
                "vendor": r["vendor"],
                "payout": float(r["payout"]),
                "transactions": int(r["transactions"]),
                "share": float(r["share_of_mp_expenditure"]),
                "is_monopoly": float(r["share_of_mp_expenditure"]) >= self.monopoly_share_threshold,
            })

        return {
            "mp_name": mp_name,
            "total_expenditure": float(total_spend),
            "vendor_count": int(len(mp_records)),
            "top_vendor": str(mp_records.iloc[0]["vendor"]),
            "top_vendor_share": top_share,
            "vendor_hhi": round(hhi, 4),
            "has_monopoly_vendor": top_share >= self.monopoly_share_threshold,
            "vendors": vendor_list,
        }

    def get_top_risk_vendors(self, top_n: int = 50) -> pd.DataFrame:
        """Return the top N highest-risk vendors with audit signals."""
        if not self.is_analyzed or self.vendor_profiles_df is None:
            raise RuntimeError("VendorNetworkIntelligence must be run via analyze() before querying.")
        return self.vendor_profiles_df.head(top_n).copy()

    def get_syndicate_vendors(self) -> pd.DataFrame:
        """Return vendors identified as active across multiple MPs and states/IDAs."""
        if not self.is_analyzed or self.syndicate_vendors_df is None:
            raise RuntimeError("VendorNetworkIntelligence must be run via analyze() before querying.")
        return self.syndicate_vendors_df.copy()

    def get_summary_stats(self) -> Dict[str, Any]:
        """Return system-wide vendor intelligence summary statistics."""
        if not self.is_analyzed or self.vendor_profiles_df is None:
            raise RuntimeError("VendorNetworkIntelligence must be run via analyze() before querying.")

        df = self.vendor_profiles_df
        return {
            "total_vendors_profiled": int(len(df)),
            "high_risk_vendors": int((df["risk_tier"] == "HIGH_RISK").sum()),
            "medium_risk_vendors": int((df["risk_tier"] == "MEDIUM_RISK").sum()),
            "low_risk_vendors": int((df["risk_tier"] == "LOW_RISK").sum()),
            "benign_vendors": int((df["risk_tier"] == "BENIGN").sum()),
            "vendors_requiring_audit": int(df["requires_audit_review"].sum()),
            "multi_mp_syndicate_count": int(len(self.syndicate_vendors_df)) if self.syndicate_vendors_df is not None else 0,
            "monopoly_contracts_count": int(len(self.monopoly_contracts_df)) if self.monopoly_contracts_df is not None else 0,
            "ida_exclusive_conduits_count": int(len(self.ida_conduits_df)) if self.ida_conduits_df is not None else 0,
            "total_disbursed_funds": float(df["total_payout"].sum()),
        }


def run_vendor_intelligence_pipeline(cleaned_datasets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """
    Convenience runner executing Module 7 end-to-end pipeline.

    Returns:
        Dict containing:
          - 'intelligence_engine': Fitted VendorNetworkIntelligence instance
          - 'vendor_profiles': pd.DataFrame of all scored vendors
          - 'summary_stats': Dict of system-wide vendor metrics
    """
    print("=" * 60)
    print("NEXORAS — Module 7: Running Vendor Network Intelligence Pipeline")
    print("=" * 60)
    engine = VendorNetworkIntelligence()
    profiles = engine.analyze(cleaned_datasets)
    stats = engine.get_summary_stats()

    print(f"  Profiled {stats['total_vendors_profiled']:,} vendors across all constituencies.")
    print(f"  High-Risk Vendors: {stats['high_risk_vendors']:,}")
    print(f"  Medium-Risk Vendors: {stats['medium_risk_vendors']:,}")
    print(f"  Vendors Requiring Audit Review: {stats['vendors_requiring_audit']:,}")
    print(f"  Cross-Constituency Syndicates: {stats['multi_mp_syndicate_count']:,}")
    print(f"  Monopoly Vendor Contracts: {stats['monopoly_contracts_count']:,}")
    print(f"  IDA Exclusive Conduits: {stats['ida_exclusive_conduits_count']:,}")
    print("=" * 60)

    return {
        "intelligence_engine": engine,
        "vendor_profiles": profiles,
        "summary_stats": stats,
    }


if __name__ == "__main__":
    import sys
    sys.path.insert(0, r"D:\sih 2026\sample mvp\NEXORAS-sample-mvp")
    from backend.ingestion.loader import load_all
    from backend.cleaning.cleaner import clean_all

    cleaned = clean_all(load_all())
    results = run_vendor_intelligence_pipeline(cleaned)
    top_risks = results["intelligence_engine"].get_top_risk_vendors(10)
    print("\nTop 10 High-Risk Vendors:")
    for _, r in top_risks.iterrows():
        print(f"  Rank #{r['audit_rank']}: {r['vendor']} | Score: {r['vendor_risk_score']:.1f} | Tier: {r['risk_tier']} | Payout: Rs {r['total_payout']:,.2f}")
