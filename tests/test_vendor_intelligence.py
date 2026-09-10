"""
NEXORAS — Module 7 Test Suite: Vendor Network Intelligence Engine
================================================================
Verifies entity-relationship graph building, vendor profiling,
syndicate/monopoly pattern detection, risk scoring, and explainability APIs.
"""

import io
import os
import sys
import unittest
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# UTF-8 stdout wrapper for Windows terminals
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from backend.ingestion.loader import load_all
from backend.cleaning.cleaner import clean_all
from backend.engine.vendor_intelligence import (
    VendorNetworkIntelligence,
    VendorProfile,
    run_vendor_intelligence_pipeline,
)


class TestVendorNetworkIntelligence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Run data ingestion, cleaning, and vendor intelligence analysis once."""
        raw_data = load_all()
        cls.cleaned_data = clean_all(raw_data)
        cls.engine = VendorNetworkIntelligence(
            min_payout_threshold=500_000.0,
            syndicate_min_mps=3,
            syndicate_min_states=2,
            monopoly_share_threshold=0.50,
            ida_capture_share_threshold=0.60,
        )
        cls.profiles = cls.engine.analyze(cls.cleaned_data)
        cls.stats = cls.engine.get_summary_stats()

    def test_01_profile_schema_and_completeness(self):
        """Test that vendor profiles contain all required columns and correct row count."""
        expected_cols = [
            "vendor", "total_payout", "transaction_count", "mp_count",
            "constituency_count", "state_count", "ida_count",
            "avg_transaction_size", "max_single_payout", "in_progress_ratio",
            "vendor_risk_score", "risk_tier", "requires_audit_review",
            "risk_flags", "audit_rank"
        ]
        for col in expected_cols:
            self.assertIn(col, self.profiles.columns, f"Missing column: {col}")

        # Unique vendors in expenditures
        unique_vendors = self.cleaned_data["expenditures"]["vendor"].nunique()
        self.assertEqual(len(self.profiles), unique_vendors)
        self.assertEqual(len(self.profiles), 28206)
        print("  PASS: Vendor profiles have 28,206 rows and all expected columns")

    def test_02_score_bounds_and_finite(self):
        """Test that vendor risk scores are finite and within [0, 100]."""
        scores = self.profiles["vendor_risk_score"]
        self.assertFalse(scores.isna().any(), "Found NaNs in vendor_risk_score")
        self.assertFalse(np.isinf(scores).any(), "Found Infs in vendor_risk_score")
        self.assertGreaterEqual(scores.min(), 0.0)
        self.assertLessEqual(scores.max(), 100.0)

        ratios = self.profiles["in_progress_ratio"]
        self.assertFalse(ratios.isna().any(), "Found NaNs in in_progress_ratio")
        self.assertGreaterEqual(ratios.min(), 0.0)
        self.assertLessEqual(ratios.max(), 1.0)
        print("  PASS: Vendor risk scores & in-progress ratios are bounded and finite")

    def test_03_risk_tier_assignments(self):
        """Test that assigned risk tiers accurately reflect the score bands."""
        valid_tiers = {"HIGH_RISK", "MEDIUM_RISK", "LOW_RISK", "BENIGN"}
        assigned_tiers = set(self.profiles["risk_tier"].unique())
        self.assertTrue(assigned_tiers.issubset(valid_tiers))

        # Check that high risk is score >= 60
        high_risk = self.profiles[self.profiles["risk_tier"] == "HIGH_RISK"]
        if not high_risk.empty:
            self.assertTrue((high_risk["vendor_risk_score"] >= 60.0).all())

        # Check that benign is score == 0
        benign = self.profiles[self.profiles["risk_tier"] == "BENIGN"]
        self.assertTrue((benign["vendor_risk_score"] == 0.0).all())
        print("  PASS: Risk tiers align strictly with score cutoffs")

    def test_04_mp_vendor_relationships(self):
        """Test MP-Vendor relationship dataframe integrity."""
        mp_v = self.engine.mp_vendor_rel_df
        self.assertIsNotNone(mp_v)
        self.assertGreater(len(mp_v), 0)

        # Sum of payouts in mp_v must equal total expenditures
        total_exp = self.cleaned_data["expenditures"]["expenditure_amount"].sum()
        total_rel = mp_v["payout"].sum()
        self.assertAlmostEqual(total_exp, total_rel, places=2)

        # Shares must be between 0.0 and 1.0
        self.assertGreaterEqual(mp_v["share_of_mp_expenditure"].min(), 0.0)
        self.assertLessEqual(mp_v["share_of_mp_expenditure"].max(), 1.0001)
        print("  PASS: MP-Vendor relationship table matches raw financial totals")

    def test_05_vendor_ida_relationships(self):
        """Test Vendor-IDA relationship dataframe integrity."""
        v_ida = self.engine.vendor_ida_rel_df
        self.assertIsNotNone(v_ida)
        self.assertGreater(len(v_ida), 0)

        # Sum of payouts in v_ida must equal total expenditures
        total_exp = self.cleaned_data["expenditures"]["expenditure_amount"].sum()
        total_rel = v_ida["payout"].sum()
        self.assertAlmostEqual(total_exp, total_rel, places=2)
        print("  PASS: Vendor-IDA relationship table matches raw financial totals")

    def test_06_syndicate_detection(self):
        """Test multi-MP, multi-state contractor syndicate detection."""
        syndicates = self.engine.get_syndicate_vendors()
        self.assertIsNotNone(syndicates)
        self.assertGreater(len(syndicates), 0)

        # All detected syndicates must meet minimum MP & state criteria
        self.assertTrue((syndicates["mp_count"] >= self.engine.syndicate_min_mps).all())
        self.assertTrue((syndicates["state_count"] >= self.engine.syndicate_min_states).all())
        self.assertTrue((syndicates["total_payout"] >= self.engine.min_payout_threshold).all())

        # Prominent contractors should be detected
        syndicate_names = set(syndicates["vendor"].unique())
        self.assertIn("FORCE MOTORS LIMITED", syndicate_names)
        print(f"  PASS: Detected {len(syndicates)} cross-constituency syndicates")

    def test_07_monopoly_detection(self):
        """Test single-MP monopoly contractor detection."""
        monopolies = self.engine.monopoly_contracts_df
        self.assertIsNotNone(monopolies)
        self.assertGreater(len(monopolies), 0)

        # All must capture >= monopoly threshold
        self.assertTrue((monopolies["share_of_mp_expenditure"] >= self.engine.monopoly_share_threshold).all())
        self.assertTrue((monopolies["payout"] >= self.engine.min_payout_threshold).all())
        print(f"  PASS: Detected {len(monopolies)} monopoly contracts")

    def test_08_ida_conduit_detection(self):
        """Test IDA exclusive conduit detection."""
        conduits = self.engine.ida_conduits_df
        self.assertIsNotNone(conduits)
        self.assertGreater(len(conduits), 0)

        self.assertTrue((conduits["share_of_ida_expenditure"] >= self.engine.ida_capture_share_threshold).all())
        print(f"  PASS: Detected {len(conduits)} IDA exclusive conduits")

    def test_09_audit_priority_ranking(self):
        """Test audit priority ranking sanity."""
        self.assertEqual(self.profiles.iloc[0]["audit_rank"], 1)
        self.assertEqual(self.profiles.iloc[-1]["audit_rank"], len(self.profiles))

        # Rank 1 must have highest score
        self.assertEqual(self.profiles.iloc[0]["vendor_risk_score"], self.profiles["vendor_risk_score"].max())
        print("  PASS: Audit priority ranking is properly ordered")

    def test_10_vendor_profile_lookup(self):
        """Test get_vendor_profile for existing and non-existing vendors."""
        # Query known vendor
        vp = self.engine.get_vendor_profile("FORCE MOTORS LIMITED")
        self.assertIsNotNone(vp)
        self.assertIsInstance(vp, VendorProfile)
        self.assertEqual(vp.vendor_name, "FORCE MOTORS LIMITED")
        self.assertGreaterEqual(vp.mp_count, 10)
        self.assertGreater(len(vp.top_mps), 0)
        self.assertGreater(len(vp.top_idas), 0)
        self.assertTrue(vp.requires_audit_review)

        # Query non-existing vendor
        non_vp = self.engine.get_vendor_profile("NON_EXISTENT_VENDOR_XYZ")
        self.assertIsNone(non_vp)
        print("  PASS: get_vendor_profile handles existing and non-existing entities correctly")

    def test_11_mp_vendor_breakdown(self):
        """Test get_mp_vendor_breakdown for known MPs."""
        # Test known MP with transactions
        sample_mp = self.cleaned_data["expenditures"]["mp_name"].iloc[0]
        breakdown = self.engine.get_mp_vendor_breakdown(sample_mp)
        self.assertEqual(breakdown["mp_name"], sample_mp)
        self.assertGreater(breakdown["total_expenditure"], 0.0)
        self.assertGreater(breakdown["vendor_count"], 0)
        self.assertIsNotNone(breakdown["top_vendor"])
        self.assertGreaterEqual(breakdown["vendor_hhi"], 0.0)
        self.assertLessEqual(breakdown["vendor_hhi"], 1.0)
        self.assertGreater(len(breakdown["vendors"]), 0)

        # Test MP with 0 expenditures (CHAVAN VASANTRAO BALWANTRAO)
        zero_mp_breakdown = self.engine.get_mp_vendor_breakdown("CHAVAN VASANTRAO BALWANTRAO")
        self.assertEqual(zero_mp_breakdown["total_expenditure"], 0.0)
        self.assertEqual(zero_mp_breakdown["vendor_count"], 0)
        self.assertFalse(zero_mp_breakdown["has_monopoly_vendor"])
        print("  PASS: get_mp_vendor_breakdown handles standard and zero-expenditure MPs")

    def test_12_neutral_audit_language(self):
        """Verify that risk flags use neutral audit phrasing (no defamatory fraud labels)."""
        all_flags = " ".join(self.profiles["risk_flags"].dropna().tolist()).lower()
        self.assertNotIn("fraudulent", all_flags)
        self.assertNotIn("criminal", all_flags)
        self.assertNotIn("corrupt", all_flags)
        print("  PASS: Output flags strictly follow neutral audit terminology")

    def test_13_summary_statistics(self):
        """Test summary statistics consistency."""
        stats = self.stats
        self.assertEqual(stats["total_vendors_profiled"], 28206)
        total_tiered = (
            stats["high_risk_vendors"] +
            stats["medium_risk_vendors"] +
            stats["low_risk_vendors"] +
            stats["benign_vendors"]
        )
        self.assertEqual(total_tiered, stats["total_vendors_profiled"])
        self.assertGreater(stats["vendors_requiring_audit"], 0)
        self.assertGreater(stats["total_disbursed_funds"], 0.0)
        print("  PASS: Summary statistics sum to 100% of vendor population")

    def test_14_pipeline_runner(self):
        """Test convenience pipeline runner."""
        res = run_vendor_intelligence_pipeline(self.cleaned_data)
        self.assertIn("intelligence_engine", res)
        self.assertIn("vendor_profiles", res)
        self.assertIn("summary_stats", res)
        self.assertEqual(len(res["vendor_profiles"]), 28206)
        print("  PASS: run_vendor_intelligence_pipeline executes end-to-end")


if __name__ == "__main__":
    print("=" * 60)
    print("NEXORAS — Module 7 Test Suite (Vendor Network Intelligence)")
    print("=" * 60)
    unittest.main(verbosity=2)
