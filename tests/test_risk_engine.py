"""
NEXORAS — Module 11 Test Suite: Unified Risk Scoring Engine
===========================================================
Verifies risk scoring calculations, normalizations, tier assignments,
and explanation generations.
"""

import os
import sys
import unittest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.scoring.risk_engine import UnifiedRiskEngine, run_risk_scoring

class TestUnifiedRiskEngine(unittest.TestCase):
    def setUp(self):
        # Create a mock dataframe of projects with various signal outputs
        self.data = pd.DataFrame({
            'project_id': ['P1', 'P2', 'P3', 'P4'],
            'anomaly_score': [0.9, 0.1, 0.5, np.nan],
            'vendor_risk': [100, 10, 50, 0],
            'graph_centrality': [0.8, 0.2, 0.4, 0.1],
            'financial_risk': [5.0, 1.0, 2.5, 0.0],
            'nlp_risk': [1.0, 0.0, 0.0, 0.0]
        })
        
        self.signal_cols = {
            'tabular_anomaly': 'anomaly_score',
            'vendor_network': 'vendor_risk',
            'networkx_centrality': 'graph_centrality',
            'financial_compliance': 'financial_risk',
            'nlp_contract_splitting': 'nlp_risk'
        }
        
        self.engine = UnifiedRiskEngine()

    def test_01_normalization(self):
        """Test Min-Max normalization of series."""
        s = pd.Series([10, 20, 30, 40, 50])
        norm_s = self.engine._normalize_series(s)
        self.assertAlmostEqual(norm_s.min(), 0.0)
        self.assertAlmostEqual(norm_s.max(), 1.0)
        self.assertAlmostEqual(norm_s.iloc[2], 0.5)

    def test_02_scoring_pipeline(self):
        """Test full scoring pipeline including weights and missing values."""
        df_scored = self.engine.score_projects(self.data, self.signal_cols)
        
        # P1 has max values across all columns, it should get 100 total score.
        # Wait, if nan is filled with 0, then max might be different.
        # anomaly_score: max is 0.9. P1 is 0.9 -> norm 1.0 -> 25 pts.
        # vendor_risk: max is 100. P1 is 100 -> norm 1.0 -> 25 pts.
        # graph_centrality: max is 0.8. P1 is 0.8 -> norm 1.0 -> 20 pts.
        # financial_risk: max is 5.0. P1 is 5.0 -> norm 1.0 -> 15 pts.
        # nlp_risk: max is 1.0. P1 is 1.0 -> norm 1.0 -> 15 pts.
        
        p1_score = df_scored.loc[df_scored['project_id'] == 'P1', 'unified_risk_score'].iloc[0]
        self.assertAlmostEqual(p1_score, 100.0)
        
        # P4 should have min score (since it has NaNs and min values)
        p4_score = df_scored.loc[df_scored['project_id'] == 'P4', 'unified_risk_score'].iloc[0]
        self.assertAlmostEqual(p4_score, 0.0)
        
        # Check tiers
        p1_tier = df_scored.loc[df_scored['project_id'] == 'P1', 'risk_tier'].iloc[0]
        self.assertEqual(p1_tier, 'CRITICAL_RISK')
        
        p4_tier = df_scored.loc[df_scored['project_id'] == 'P4', 'risk_tier'].iloc[0]
        self.assertEqual(p4_tier, 'LOW_RISK')

    def test_03_why_flagged(self):
        """Test generation of human-readable explanations."""
        df_scored = self.engine.score_projects(self.data, self.signal_cols)
        
        p1_reasons = df_scored.loc[df_scored['project_id'] == 'P1', 'why_flagged'].iloc[0]
        self.assertTrue(len(p1_reasons) > 0)
        self.assertTrue(any("High tabular anomaly score" in r for r in p1_reasons))
        
        p4_reasons = df_scored.loc[df_scored['project_id'] == 'P4', 'why_flagged'].iloc[0]
        self.assertEqual(len(p4_reasons), 0)

    def test_04_empty_dataframe(self):
        """Test handling of empty dataframe."""
        empty_df = pd.DataFrame()
        result = self.engine.score_projects(empty_df, self.signal_cols)
        self.assertTrue(result.empty)
        
    def test_05_missing_signal_columns(self):
        """Test behavior when a signal column is missing."""
        df = self.data.drop(columns=['anomaly_score'])
        df_scored = self.engine.score_projects(df, self.signal_cols)
        
        # P1 missing anomaly score should lose 25 points
        p1_score = df_scored.loc[df_scored['project_id'] == 'P1', 'unified_risk_score'].iloc[0]
        self.assertAlmostEqual(p1_score, 75.0)

if __name__ == '__main__':
    unittest.main()
