"""
NEXORAS Module 5 — Anomaly Ensemble Engine
Synthesizes tree-partitioning (Isolation Forest) and neural reconstruction (Autoencoder)
into a unified consensus risk score with confidence tiering.

Why Ensemble?
- Tree Partitioning (Isolation Forest): Excels at detecting axis-aligned extreme spikes
  (e.g., vendor monopoly HHI = 1.0, extreme transaction sizes).
- Neural Reconstruction (Autoencoder): Excels at discovering non-linear manifold violations
  (e.g., unexpected joint interactions between completion rate, utilization, and vendor spread).
- Ensemble Synthesis: Combines orthogonal statistical paradigms to achieve defense-in-depth,
  reducing false positives while catching subtle irregularities.

Consensus Classification:
- CRITICAL_CONSENSUS: Both models flag anomaly (Highest Priority Audit Target)
- TREE_ISOLATED: Isolation Forest only flags (Extreme single-feature outlier)
- NEURAL_IRREGULARITY: Autoencoder only flags (Complex correlation breakdown)
- NORMAL: Neither model flags (Standard parliamentary operation)
"""
import os
import joblib
import numpy as np
import pandas as pd
from backend.engine.isolation_forest import MPIsolationForest, WorkIsolationForest
from backend.engine.autoencoder import MPAutoencoder


class AnomalyEnsemble:
    """
    Multi-model anomaly synthesis combining Isolation Forest and Neural Autoencoder.
    """

    def __init__(self, if_weight: float = 0.50, ae_weight: float = 0.50):
        total_w = if_weight + ae_weight
        self.if_weight = if_weight / total_w
        self.ae_weight = ae_weight / total_w

    def combine(
        self,
        if_df: pd.DataFrame,
        ae_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Combine scored DataFrames from MPIsolationForest and MPAutoencoder.

        Returns DataFrame containing:
        - ensemble_score: weighted average anomaly score [0.0, 1.0]
        - ensemble_tier: CRITICAL_CONSENSUS, TREE_ISOLATED, NEURAL_IRREGULARITY, NORMAL
        - ensemble_flagged: bool (True if either model flags)
        - consensus_flagged: bool (True if BOTH models flag)
        - model_disagreement: float [0.0, 1.0] indicating absolute divergence between models
        - audit_priority_rank: integer (1 = highest risk)
        """
        result = if_df.copy()

        # Merge in Autoencoder columns
        result["ae_reconstruction_mse"] = ae_df["ae_reconstruction_mse"]
        result["ae_anomaly_score"] = ae_df["ae_anomaly_score"]
        result["ae_is_anomaly"] = ae_df["ae_is_anomaly"]

        # 1. Calibrated Weighted Consensus Score
        if_scores = result["if_anomaly_score"].clip(0.0, 1.0)
        ae_scores = result["ae_anomaly_score"].clip(0.0, 1.0)
        ensemble_score = (self.if_weight * if_scores) + (self.ae_weight * ae_scores)
        result["ensemble_score"] = np.round(ensemble_score, 4)

        # 2. Model Disagreement
        disagreement = np.abs(if_scores - ae_scores)
        result["model_disagreement"] = np.round(disagreement, 4)

        # 3. Consensus Flags
        result["consensus_flagged"] = result["if_is_anomaly"] & result["ae_is_anomaly"]
        result["ensemble_flagged"] = result["if_is_anomaly"] | result["ae_is_anomaly"]

        # 4. Confidence Tier Assignment
        tiers = []
        for _, row in result.iterrows():
            if row["if_is_anomaly"] and row["ae_is_anomaly"]:
                tiers.append("CRITICAL_CONSENSUS")
            elif row["if_is_anomaly"]:
                tiers.append("TREE_ISOLATED")
            elif row["ae_is_anomaly"]:
                tiers.append("NEURAL_IRREGULARITY")
            else:
                tiers.append("NORMAL")
        result["ensemble_tier"] = tiers

        # 5. Audit Priority Ranking (1 = highest risk)
        result["audit_priority_rank"] = result["ensemble_score"].rank(ascending=False, method="min").astype(int)

        return result

    def get_summary_stats(self, ensemble_df: pd.DataFrame) -> dict:
        """Compute summary counts across consensus tiers."""
        tier_counts = ensemble_df["ensemble_tier"].value_counts().to_dict()
        return {
            "total_mps": len(ensemble_df),
            "critical_consensus": tier_counts.get("CRITICAL_CONSENSUS", 0),
            "tree_isolated_only": tier_counts.get("TREE_ISOLATED", 0),
            "neural_irregularity_only": tier_counts.get("NEURAL_IRREGULARITY", 0),
            "normal": tier_counts.get("NORMAL", 0),
            "mean_ensemble_score": float(ensemble_df["ensemble_score"].mean()),
            "mean_disagreement": float(ensemble_df["model_disagreement"].mean()),
        }


def run_ensemble_pipeline(
    feature_dict: dict[str, pd.DataFrame],
    save_dir: str = None,
) -> tuple[pd.DataFrame, pd.DataFrame, AnomalyEnsemble, MPIsolationForest, MPAutoencoder, WorkIsolationForest]:
    """
    Execute end-to-end multi-model anomaly detection pipeline:
    1. Train & Score MPIsolationForest
    2. Train & Score WorkIsolationForest
    3. Train & Score MPAutoencoder
    4. Synthesize into AnomalyEnsemble

    Returns:
        (ensemble_mp_df, scored_work_df, ensemble, if_model, ae_model, work_if_model)
    """
    print("=" * 60)
    print("NEXORAS — Module 5: Running End-to-End Anomaly Ensemble Pipeline")
    print("=" * 60)

    # 1. Isolation Forest (MP + Work)
    if_mp_model = MPIsolationForest(contamination=0.08, random_state=42)
    if_mp_model.fit(feature_dict["mp_features"])
    if_scored_mps = if_mp_model.score(feature_dict["mp_features"])

    if_work_model = WorkIsolationForest(contamination=0.03, random_state=42)
    if_work_model.fit(feature_dict["work_features"])
    scored_works = if_work_model.score(feature_dict["work_features"])

    # 2. Neural Autoencoder (MP)
    ae_model = MPAutoencoder(contamination=0.08, random_state=42)
    ae_model.fit(feature_dict["mp_features"])
    ae_scored_mps = ae_model.score(feature_dict["mp_features"])

    # 3. Ensemble Synthesis
    ensemble = AnomalyEnsemble(if_weight=0.50, ae_weight=0.50)
    ensemble_mps = ensemble.combine(if_scored_mps, ae_scored_mps)
    stats = ensemble.get_summary_stats(ensemble_mps)

    print("=" * 60)
    print("ENSEMBLE CONSENSUS MATRIX:")
    print(f"  Critical Consensus Anomalies (Both Flag): {stats['critical_consensus']} MPs")
    print(f"  Tree-Isolated Outliers (IF Only):         {stats['tree_isolated_only']} MPs")
    print(f"  Neural Irregularities (AE Only):          {stats['neural_irregularity_only']} MPs")
    print(f"  Normal Constituencies (Neither Flag):     {stats['normal']} MPs")
    print(f"  Total Flagged Audit Candidates:          {stats['critical_consensus'] + stats['tree_isolated_only'] + stats['neural_irregularity_only']} MPs")
    print("=" * 60)

    # Optional Persistence
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
        if_mp_model.save(os.path.join(save_dir, "mp_isolation_forest.joblib"))
        if_work_model.save(os.path.join(save_dir, "work_isolation_forest.joblib"))
        ae_model.save(os.path.join(save_dir, "mp_autoencoder.joblib"))

    return ensemble_mps, scored_works, ensemble, if_mp_model, ae_model, if_work_model


if __name__ == "__main__":
    import sys
    sys.path.insert(0, r"D:\sih 2026\sample mvp\NEXORAS-sample-mvp")
    from backend.ingestion.loader import load_all
    from backend.cleaning.cleaner import clean_all
    from backend.features.builder import build_all_features

    feats = build_all_features(clean_all(load_all()))
    ensemble_mps, scored_works, ensemble, m1, m2, m3 = run_ensemble_pipeline(feats)

    print("\nTop 5 Critical Consensus Anomalies (Priority 1 Ground Audit):")
    top_critical = ensemble_mps[ensemble_mps["ensemble_tier"] == "CRITICAL_CONSENSUS"].sort_values(
        by="ensemble_score", ascending=False
    )[["audit_priority_rank", "mp_name", "constituency", "state", "vendor_hhi", "ensemble_score"]]
    print(top_critical.head(5).to_string())
