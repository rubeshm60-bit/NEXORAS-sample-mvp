"""
NEXORAS — Module 12: Explainability / SHAP
==========================================
Generates feature attributions for anomalies detected by Isolation Forest models.
Provides human-readable baseline comparisons and explains the magnitude and direction
of each feature's contribution to the anomaly score.
"""

import numpy as np
import pandas as pd
import shap
from typing import Dict, List, Any

class ModelExplainer:
    def __init__(self, model_wrapper, feature_names: List[str]):
        """
        Initialize the SHAP explainer for an Isolation Forest model.
        
        Args:
            model_wrapper: The NEXORAS model wrapper (e.g., MPIsolationForest).
                           Must have a fitted `.model` (sklearn IsolationForest) attribute
                           and a `.scaler` attribute.
            feature_names: List of feature names corresponding to the model input.
        """
        if not hasattr(model_wrapper, 'is_fitted') or not model_wrapper.is_fitted:
            raise ValueError("The provided model wrapper must be fitted before initialization.")
            
        self.wrapper = model_wrapper
        self.feature_names = feature_names
        self.model = self.wrapper.model
        self.scaler = self.wrapper.scaler
        
        # Initialize SHAP TreeExplainer
        # For IsolationForest, SHAP explains the tree path length.
        # A shorter path length indicates an anomaly.
        # Therefore, a negative SHAP value decreases the path length (increases anomaly risk).
        self.explainer = shap.TreeExplainer(self.model)

    def explain_instances(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Generate explanations for a dataframe of instances.
        Returns a list of explanation dictionaries, one per row.
        """
        if df.empty:
            return []
            
        # Ensure we only use the expected features
        X = df[self.feature_names].copy().fillna(0.0)
        
        # Scale the features as the model expects
        X_scaled = self.wrapper.scaler.transform(X)
        
        # Compute SHAP values
        # For a TreeExplainer on IsolationForest, shap_values has shape (n_samples, n_features)
        shap_values = self.explainer.shap_values(X_scaled)
        
        explanations = []
        
        for i in range(len(df)):
            row_raw = X.iloc[i]
            row_shap = shap_values[i]
            
            contributions = []
            for j, feature in enumerate(self.feature_names):
                shap_val = float(row_shap[j])
                raw_val = float(row_raw[feature])
                
                # Fetch the inlier median from the wrapper if available
                baseline = None
                if hasattr(self.wrapper, 'inlier_medians') and feature in self.wrapper.inlier_medians:
                    baseline = self.wrapper.inlier_medians[feature]
                
                # A negative SHAP value decreases path length, increasing anomaly risk.
                # We map this to a positive 'anomaly_contribution' for easier interpretation.
                anomaly_contribution = -shap_val
                
                contributions.append({
                    'feature': feature,
                    'observed_value': raw_val,
                    'baseline_median': baseline,
                    'shap_value': shap_val,
                    'anomaly_contribution': anomaly_contribution
                })
            
            # Sort contributions by how much they pushed towards anomaly (highest positive anomaly_contribution first)
            contributions.sort(key=lambda x: x['anomaly_contribution'], reverse=True)
            
            explanations.append({
                'base_path_length': float(self.explainer.expected_value[0] if isinstance(self.explainer.expected_value, (list, np.ndarray)) else self.explainer.expected_value),
                'contributions': contributions,
                'top_anomalous_features': [
                    c for c in contributions if c['anomaly_contribution'] > 0
                ][:3] # Top 3 contributing features
            })
            
        return explanations
