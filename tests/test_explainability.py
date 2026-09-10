"""
NEXORAS — Module 12 & 13 Test Suite: Explainability & Why Flagged
=================================================================
Verifies SHAP value generation for Isolation Forest, baseline extraction,
and translation into human-readable evidence logs.
"""

import os
import sys
import unittest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.engine.isolation_forest import MPIsolationForest
from backend.engine.shap_explainer import ModelExplainer
from backend.engine.why_flagged import WhyFlaggedEngine

class TestExplainability(unittest.TestCase):
    def setUp(self):
        # Create a mock dataset for MP Isolation Forest
        np.random.seed(42)
        # Normal data
        data = np.random.randn(100, 3) * 0.1
        # Anomalies
        data[0] = [5.0, 5.0, -5.0]
        data[1] = [-4.0, 0.0, 4.0]
        
        self.feature_names = ["utilization_rate", "cost_deviation_z", "vendor_hhi"]
        self.df = pd.DataFrame(data, columns=self.feature_names)
        
        # Train model
        self.model_wrapper = MPIsolationForest(
            feature_cols=self.feature_names,
            n_estimators=50,
            contamination=0.05,
            random_state=42
        )
        self.model_wrapper.fit(self.df)
        
    def test_01_shap_explainer(self):
        """Test SHAP explainer correctly attributes anomaly score contributions."""
        explainer = ModelExplainer(self.model_wrapper, self.feature_names)
        
        # Test on the obvious anomaly
        anomaly_df = self.df.iloc[[0]]
        explanations = explainer.explain_instances(anomaly_df)
        
        self.assertEqual(len(explanations), 1)
        exp = explanations[0]
        
        self.assertIn('base_path_length', exp)
        self.assertIn('contributions', exp)
        self.assertTrue(len(exp['top_anomalous_features']) > 0)
        
        # The first feature should have a high positive anomaly_contribution
        top_feature = exp['top_anomalous_features'][0]
        self.assertTrue(top_feature['anomaly_contribution'] > 0)
        
    def test_02_why_flagged_engine(self):
        """Test translation of SHAP attributions into readable reports."""
        explainer = ModelExplainer(self.model_wrapper, self.feature_names)
        shap_explanations = explainer.explain_instances(self.df.iloc[[0, 50]]) # 1 anomaly, 1 normal
        
        wf_engine = WhyFlaggedEngine()
        formatted_reasons = wf_engine.format_explanations(shap_explanations)
        
        self.assertEqual(len(formatted_reasons), 2)
        
        # Anomaly instance
        anomaly_reasons = formatted_reasons[0]
        self.assertTrue(len(anomaly_reasons) > 0)
        self.assertIn("Signal", anomaly_reasons[0])
        self.assertIn("Evidence", anomaly_reasons[0])
        
        # Convert to string
        report = wf_engine.generate_report_string(anomaly_reasons)
        self.assertIn("[", report) # e.g. [UTILIZATION RATE]
        self.assertIn("Observed:", report)
        self.assertIn("Risk contribution:", report)
        
    def test_03_no_anomalies(self):
        """Test empty handling."""
        explainer = ModelExplainer(self.model_wrapper, self.feature_names)
        wf_engine = WhyFlaggedEngine()
        
        empty_explanations = explainer.explain_instances(pd.DataFrame(columns=self.feature_names))
        self.assertEqual(empty_explanations, [])
        
        formatted = wf_engine.format_explanations(empty_explanations)
        self.assertEqual(formatted, [])

if __name__ == '__main__':
    unittest.main()
