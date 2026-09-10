"""
NEXORAS — Module 11: Unified Risk Scoring Engine
================================================
Synthesizes 5 independent intelligence pillars into a 0-100 unified risk score,
assigns severity tiers, and generates human-readable audit explanations ("Why Flagged").

Weights:
1. Tabular Anomaly Ensemble (25%)
2. Vendor Network Risk (25%)
3. NetworkX Graph Centrality (20%)
4. Financial/Compliance (15%)
5. NLP Contract Splitting (15%)
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional


class UnifiedRiskEngine:
    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        critical_threshold: float = 80.0,
        high_threshold: float = 60.0,
        medium_threshold: float = 40.0
    ):
        """
        Initialize the Risk Engine with weights and tier thresholds.
        """
        self.weights = weights or {
            'tabular_anomaly': 0.25,
            'vendor_network': 0.25,
            'networkx_centrality': 0.20,
            'financial_compliance': 0.15,
            'nlp_contract_splitting': 0.15
        }
        
        # Ensure weights sum to 1.0 (approximately)
        total_weight = sum(self.weights.values())
        if not np.isclose(total_weight, 1.0):
            self.weights = {k: v / total_weight for k, v in self.weights.items()}

        self.thresholds = {
            'CRITICAL_RISK': critical_threshold,
            'HIGH_RISK': high_threshold,
            'MEDIUM_RISK': medium_threshold
        }

    def _normalize_series(self, series: pd.Series) -> pd.Series:
        """Min-Max normalization of a pandas Series to 0-1 range."""
        s_min = series.min()
        s_max = series.max()
        if pd.isna(s_min) or pd.isna(s_max) or s_min == s_max:
            return pd.Series(0.0, index=series.index)
        return (series - s_min) / (s_max - s_min)

    def generate_explanations(self, row: pd.Series) -> List[str]:
        """
        Generate human-readable audit reasons ('Why Flagged') for a single project based on points.
        """
        reasons = []
        
        if row.get('tabular_anomaly_points', 0) > (self.weights['tabular_anomaly'] * 100 * 0.5):
            reasons.append(f"High tabular anomaly score ({row['tabular_anomaly_points']:.1f} pts).")
            
        if row.get('vendor_network_points', 0) > (self.weights['vendor_network'] * 100 * 0.5):
            reasons.append(f"Suspicious vendor network behavior ({row['vendor_network_points']:.1f} pts).")
            
        if row.get('networkx_centrality_points', 0) > (self.weights['networkx_centrality'] * 100 * 0.5):
            reasons.append(f"Unusual graph centrality metrics ({row['networkx_centrality_points']:.1f} pts).")
            
        if row.get('financial_compliance_points', 0) > (self.weights['financial_compliance'] * 100 * 0.5):
            reasons.append(f"Financial/compliance irregularities detected ({row['financial_compliance_points']:.1f} pts).")
            
        if row.get('nlp_contract_splitting_points', 0) > (self.weights['nlp_contract_splitting'] * 100 * 0.5):
            reasons.append(f"NLP detected potential contract splitting ({row['nlp_contract_splitting_points']:.1f} pts).")
            
        if not reasons and row.get('unified_risk_score', 0) >= self.thresholds['MEDIUM_RISK']:
            reasons.append("Cumulative multi-pillar minor signals elevated the risk score.")
            
        return reasons

    def score_projects(self, df: pd.DataFrame, signal_cols: Dict[str, str]) -> pd.DataFrame:
        """
        Calculate the 0-100 unified risk score for a dataframe of projects.
        
        Args:
            df: DataFrame containing project records.
            signal_cols: Mapping of pillar name to the column in df.
                Example:
                {
                    'tabular_anomaly': 'ensemble_anomaly_score',
                    'vendor_network': 'vendor_risk_signal',
                    ...
                }
        Returns:
            df_scored: A new DataFrame with scoring columns appended.
        """
        if df.empty:
            return df.copy()
            
        df_scored = df.copy()
        
        # 1. Normalize sub-scores and calculate points
        total_score = pd.Series(0.0, index=df_scored.index)
        
        for pillar in self.weights.keys():
            col_name = signal_cols.get(pillar)
            if col_name and col_name in df_scored.columns:
                # Fill missing with 0
                raw_series = df_scored[col_name].fillna(0)
                # Normalize 0-1
                normalized_series = self._normalize_series(raw_series)
                # Calculate points (0 to weight * 100)
                points = normalized_series * self.weights[pillar] * 100
                df_scored[f'{pillar}_points'] = points
                total_score += points
            else:
                # If a signal column is missing, that pillar contributes 0 points.
                df_scored[f'{pillar}_points'] = 0.0

        df_scored['unified_risk_score'] = total_score
        
        # 2. Assign tiers
        def assign_tier(score):
            if score >= self.thresholds['CRITICAL_RISK']:
                return 'CRITICAL_RISK'
            elif score >= self.thresholds['HIGH_RISK']:
                return 'HIGH_RISK'
            elif score >= self.thresholds['MEDIUM_RISK']:
                return 'MEDIUM_RISK'
            else:
                return 'LOW_RISK'
                
        df_scored['risk_tier'] = df_scored['unified_risk_score'].apply(assign_tier)
        
        # 3. Generate "Why Flagged" explanations
        df_scored['why_flagged'] = df_scored.apply(self.generate_explanations, axis=1)
        
        return df_scored

def run_risk_scoring(df: pd.DataFrame, signal_cols: Dict[str, str]) -> pd.DataFrame:
    """Helper function to execute the risk scoring pipeline."""
    engine = UnifiedRiskEngine()
    return engine.score_projects(df, signal_cols)
