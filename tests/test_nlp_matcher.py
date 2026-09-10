"""
NEXORAS — Module 10 Test Suite: NLP Project Intelligence Engine
==============================================================
Verifies text normalization, duplicate project detection, contract
splitting indicators, vague description auditing, and MP-level metrics.
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
from backend.engine.nlp_matcher import (
    NLPProjectMatcher,
    normalize_text,
    run_nlp_pipeline,
)


class TestNLPProjectMatcher(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Run data ingestion, cleaning, and NLP analysis once."""
        raw_data = load_all()
        cls.cleaned_data = clean_all(raw_data)
        cls.engine = NLPProjectMatcher(
            similarity_threshold=0.85,
            bulk_repeat_threshold=15,
            vague_word_limit=3,
        )
        cls.scored_works = cls.engine.analyze(cls.cleaned_data)
        cls.mp_metrics = cls.engine.mp_nlp_metrics_df
        cls.stats = cls.engine.get_summary_stats()

    def test_01_text_normalization(self):
        """Test text normalization helper function."""
        self.assertEqual(normalize_text("High Mast LED Light (150W)!"), "high mast led light 150w")
        self.assertEqual(normalize_text(""), "[no description]")
        self.assertEqual(normalize_text(None), "[no description]")
        self.assertEqual(normalize_text("  PUMP...   WATER   "), "pump water")
        print("  PASS: Text normalization correctly cleans punctuation, case, and spacing")

    def test_02_scored_works_schema(self):
        """Test that scored works DataFrame has expected NLP columns and rows."""
        expected_cols = [
            "normalized_description", "word_count", "is_vague_description",
            "global_repeat_count", "mp_repeat_count", "is_duplicate_in_constituency",
            "text_cluster_id"
        ]
        for col in expected_cols:
            self.assertIn(col, self.scored_works.columns, f"Missing column: {col}")

        self.assertEqual(len(self.scored_works), 44028)
        print("  PASS: Scored works contains all 44,028 rows and expected NLP columns")

    def test_03_mp_metrics_schema(self):
        """Test MP-level NLP metrics schema and completeness."""
        expected_cols = [
            "mp_name", "total_completed_works", "duplicate_works_count",
            "unique_descriptions_count", "duplicate_work_ratio",
            "max_single_description_repeat", "vague_descriptions_count",
            "vague_description_ratio", "has_contract_splitting_pattern",
            "nlp_risk_score", "nlp_risk_flags", "nlp_rank"
        ]
        for col in expected_cols:
            self.assertIn(col, self.mp_metrics.columns, f"Missing column: {col}")

        self.assertEqual(len(self.mp_metrics), 774)
        print("  PASS: MP metrics DataFrame contains all 774 MPs")

    def test_04_score_bounds_and_finite(self):
        """Test that NLP risk scores and ratios are bounded and finite."""
        scores = self.mp_metrics["nlp_risk_score"]
        self.assertFalse(scores.isna().any(), "Found NaNs in nlp_risk_score")
        self.assertFalse(np.isinf(scores).any(), "Found Infs in nlp_risk_score")
        self.assertGreaterEqual(scores.min(), 0.0)
        self.assertLessEqual(scores.max(), 100.0)

        dup_ratios = self.mp_metrics["duplicate_work_ratio"]
        self.assertGreaterEqual(dup_ratios.min(), 0.0)
        self.assertLessEqual(dup_ratios.max(), 1.0)
        print("  PASS: NLP risk scores are strictly bounded in [0, 100]")

    def test_05_contract_splitting_detection(self):
        """Test identification of bulk contract splitting patterns."""
        splitting_mps = self.mp_metrics[self.mp_metrics["has_contract_splitting_pattern"]]
        self.assertGreater(len(splitting_mps), 0)

        # All splitting MPs must have max repeat >= threshold (15)
        self.assertTrue((splitting_mps["max_single_description_repeat"] >= 15).all())

        # Prominent repetitive MPs should be detected
        splitting_names = set(splitting_mps["mp_name"])
        self.assertIn("SAMBIT PATRA", splitting_names)
        print(f"  PASS: Correctly identified {len(splitting_mps)} MPs with contract splitting patterns")

    def test_06_vague_description_audit(self):
        """Test detection of uninformative or vague project descriptions."""
        vague_works = self.scored_works[self.scored_works["is_vague_description"]]
        self.assertGreater(len(vague_works), 0)

        # Ensure '[no description]' entries are flagged as vague
        no_desc = self.scored_works[self.scored_works["normalized_description"] == "no description"]
        if not no_desc.empty:
            self.assertTrue(no_desc["is_vague_description"].all())
        print(f"  PASS: Detected {len(vague_works)} vague/low-information project descriptions")

    def test_07_mp_nlp_profile_lookup(self):
        """Test get_mp_nlp_profile query API."""
        # Active MP
        profile = self.engine.get_mp_nlp_profile("SAMBIT PATRA")
        self.assertIsNotNone(profile)
        self.assertEqual(profile["mp_name"], "SAMBIT PATRA")
        self.assertGreater(profile["total_completed_works"], 0)
        self.assertTrue(profile["has_contract_splitting_pattern"])
        self.assertGreater(len(profile["top_repeated_descriptions"]), 0)

        # Non-existent MP
        non_profile = self.engine.get_mp_nlp_profile("NON_EXISTENT_MP_XYZ")
        self.assertIsNone(non_profile)
        print("  PASS: get_mp_nlp_profile handles active and unknown MPs correctly")

    def test_08_summary_statistics(self):
        """Test summary statistics consistency."""
        stats = self.stats
        self.assertEqual(stats["total_works_analyzed"], 44028)
        self.assertGreater(stats["unique_text_descriptions"], 30000)
        self.assertGreater(stats["total_duplicate_works"], 0)
        self.assertGreater(stats["mps_with_contract_splitting"], 0)
        print("  PASS: Global NLP summary statistics verified")

    def test_09_pipeline_runner(self):
        """Test convenience runner."""
        res = run_nlp_pipeline(self.cleaned_data)
        self.assertIn("nlp_engine", res)
        self.assertIn("scored_works", res)
        self.assertIn("mp_nlp_metrics", res)
        self.assertIn("summary_stats", res)
        self.assertEqual(len(res["mp_nlp_metrics"]), 774)
        print("  PASS: run_nlp_pipeline executes end-to-end")


if __name__ == "__main__":
    print("=" * 60)
    print("NEXORAS — Module 10 Test Suite (NLP Project Intelligence)")
    print("=" * 60)
    unittest.main(verbosity=2)
