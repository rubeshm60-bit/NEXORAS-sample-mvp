"""
NEXORAS — Module 13: 'Why Flagged?' Engine
==========================================
Dedicated explanation layer translating raw SHAP feature attributions 
into human-readable audit evidence (Signal, Evidence, Baseline, Contribution).
"""

from typing import Dict, List, Any
import pandas as pd

class WhyFlaggedEngine:
    def __init__(self):
        """Initialize the explanation formatter."""
        pass
        
    def format_explanations(self, shap_explanations: List[Dict[str, Any]]) -> List[List[Dict[str, str]]]:
        """
        Translates SHAP attributions for multiple instances into formatted audit reasons.
        
        Args:
            shap_explanations: Output from ModelExplainer.explain_instances()
            
        Returns:
            A list (one per instance) of formatted evidence blocks.
        """
        formatted_results = []
        
        for exp in shap_explanations:
            instance_reasons = []
            
            for contrib in exp['top_anomalous_features']:
                feature = contrib['feature']
                observed = contrib['observed_value']
                baseline = contrib['baseline_median']
                push = contrib['anomaly_contribution']
                
                # Format numbers gracefully
                obs_str = f"{observed:.2f}" if isinstance(observed, float) else str(observed)
                base_str = f"{baseline:.2f}" if isinstance(baseline, float) else str(baseline)
                
                # Only include baseline deviation if baseline exists and is not zero
                if baseline is not None and baseline != 0:
                    deviation = ((observed - baseline) / abs(baseline)) * 100
                    dev_str = f"{deviation:+.1f}%"
                else:
                    dev_str = "N/A"
                    
                reason = {
                    "Signal": feature.replace("_", " ").title(),
                    "Evidence": f"Observed: {obs_str}",
                    "Baseline": f"Comparable median: {base_str}" if baseline is not None else "No baseline",
                    "Deviation": dev_str,
                    "Contribution": f"+{push:.2f} risk points"
                }
                
                instance_reasons.append(reason)
                
            formatted_results.append(instance_reasons)
            
        return formatted_results

    def generate_report_string(self, formatted_reasons: List[Dict[str, str]]) -> str:
        """Converts a single instance's formatted reasons into a readable string report."""
        if not formatted_reasons:
            return "No anomalous signals detected."
            
        lines = []
        for reason in formatted_reasons:
            lines.append(f"[{reason['Signal'].upper()}]")
            lines.append(f"  {reason['Evidence']}")
            lines.append(f"  {reason['Baseline']}")
            if reason['Deviation'] != "N/A":
                lines.append(f"  Deviation: {reason['Deviation']}")
            lines.append(f"  Risk contribution: {reason['Contribution']}\n")
            
        return "\n".join(lines).strip()
