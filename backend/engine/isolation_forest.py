"""
NEXORAS Module 4A — Isolation Forest Anomaly Engine
Unsupervised multi-tree recursive partitioning for statistical anomaly detection.

Components:
1. MPIsolationForest:
   - Trained on MP-level aggregated financial, execution, and contractor concentration features
   - Assigns continuous anomaly score [0.0, 1.0] and binary flag (is_anomaly)
   - Generates feature attribution breakdown for explainability (Module 13 pre-cursor)

2. WorkIsolationForest:
   - Trained on project-level features (cost deviation Z-scores, median ratios, image presence)
   - Assigns project-level anomaly scores and flags specific high-risk works for ground inspection

Mathematics:
- Partitions feature space randomly across n_estimators = 200 trees
- Path length h(x) indicates anomaly likelihood: anomalies isolate in shorter paths
- Normalized anomaly score: 1.0 indicates maximum outlier deviation; 0.0 indicates typical behavior
"""
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


# Default feature sets
DEFAULT_MP_FEATURES = [
    "utilization_rate",
    "unspent_ratio",
    "completion_rate",
    "vendor_hhi",
    "top_vendor_share",
    "pending_payment_ratio",
    "avg_transaction_size",
    "image_compliance_rate",
    "avg_spend_per_vendor",
]

DEFAULT_WORK_FEATURES = [
    "final_amount",
    "cost_deviation_z",
    "cost_to_median_ratio",
]


class MPIsolationForest:
    """Isolation Forest anomaly detection model operating on MP-level feature matrix."""

    def __init__(
        self,
        feature_cols: list[str] = None,
        n_estimators: int = 200,
        contamination: float = 0.08,
        random_state: int = 42,
    ):
        self.feature_cols = feature_cols or DEFAULT_MP_FEATURES
        self.n_estimators = n_estimators
        self.contamination = contamination
        self.random_state = random_state

        self.model = IsolationForest(
            n_estimators=self.n_estimators,
            contamination=self.contamination,
            random_state=self.random_state,
        )
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.inlier_medians = {}
        self.min_raw_score = None
        self.max_raw_score = None

    def fit(self, mp_df: pd.DataFrame) -> "MPIsolationForest":
        """Fit scaler and Isolation Forest on MP feature matrix."""
        print(f"  Fitting MPIsolationForest on {len(mp_df)} MPs with {len(self.feature_cols)} features...")
        X = mp_df[self.feature_cols].copy().fillna(0.0)
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)

        # Compute inlier baselines for explainability
        preds = self.model.predict(X_scaled)
        inliers_df = X[preds == 1]
        for col in self.feature_cols:
            self.inlier_medians[col] = float(inliers_df[col].median()) if len(inliers_df) > 0 else float(X[col].median())

        raw_scores = self.model.decision_function(X_scaled)
        self.min_raw_score = float(raw_scores.min())
        self.max_raw_score = float(raw_scores.max())
        self.is_fitted = True
        return self

    def score(self, mp_df: pd.DataFrame) -> pd.DataFrame:
        """
        Score MP records. Returns a copy of mp_df with added columns:
        - if_anomaly_score: float in [0.0, 1.0] (1.0 = highest anomaly confidence)
        - if_is_anomaly: bool (True = flagged outlier by contamination threshold)
        """
        if not self.is_fitted:
            raise RuntimeError("MPIsolationForest must be fitted before scoring.")

        result = mp_df.copy()
        X = result[self.feature_cols].copy().fillna(0.0)
        X_scaled = self.scaler.transform(X)

        raw_scores = self.model.decision_function(X_scaled)
        preds = self.model.predict(X_scaled)

        # Normalize score into [0.0, 1.0] where 1.0 is most anomalous
        score_range = max(self.max_raw_score - self.min_raw_score, 1e-6)
        normalized_scores = 1.0 - np.clip((raw_scores - self.min_raw_score) / score_range, 0.0, 1.0)

        result["if_anomaly_score"] = np.round(normalized_scores, 4)
        result["if_is_anomaly"] = preds == -1
        return result

    def explain_mp(self, mp_row: pd.Series) -> list[dict]:
        """
        Produce a rank-ordered list of feature deviation contributions for a single MP.
        Shows observed value vs normal inlier median.
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before explaining.")

        explanations = []
        for col in self.feature_cols:
            observed = float(mp_row.get(col, 0.0))
            baseline = self.inlier_medians.get(col, 0.0)
            diff = observed - baseline
            pct_diff = (diff / max(abs(baseline), 1e-4)) * 100.0

            explanations.append({
                "feature": col,
                "observed": round(observed, 4),
                "baseline_median": round(baseline, 4),
                "absolute_diff": round(diff, 4),
                "pct_deviation": round(pct_diff, 1),
            })

        # Sort features by absolute percentage deviation
        explanations.sort(key=lambda x: abs(x["pct_deviation"]), reverse=True)
        return explanations

    def save(self, filepath: str):
        """Serialize model to disk."""
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        state = {
            "model": self.model,
            "scaler": self.scaler,
            "feature_cols": self.feature_cols,
            "n_estimators": self.n_estimators,
            "contamination": self.contamination,
            "random_state": self.random_state,
            "inlier_medians": self.inlier_medians,
            "min_raw_score": self.min_raw_score,
            "max_raw_score": self.max_raw_score,
            "is_fitted": self.is_fitted,
        }
        joblib.dump(state, filepath)
        print(f"  Saved MPIsolationForest to {filepath}")

    @classmethod
    def load(cls, filepath: str) -> "MPIsolationForest":
        """Deserialize model from disk."""
        state = joblib.load(filepath)
        instance = cls(
            feature_cols=state["feature_cols"],
            n_estimators=state["n_estimators"],
            contamination=state["contamination"],
            random_state=state["random_state"],
        )
        instance.model = state["model"]
        instance.scaler = state["scaler"]
        instance.inlier_medians = state["inlier_medians"]
        instance.min_raw_score = state["min_raw_score"]
        instance.max_raw_score = state["max_raw_score"]
        instance.is_fitted = state["is_fitted"]
        print(f"  Loaded MPIsolationForest from {filepath}")
        return instance


class WorkIsolationForest:
    """Isolation Forest anomaly detection model operating on completed project records."""

    def __init__(
        self,
        feature_cols: list[str] = None,
        n_estimators: int = 150,
        contamination: float = 0.03,
        random_state: int = 42,
    ):
        self.feature_cols = feature_cols or DEFAULT_WORK_FEATURES
        self.n_estimators = n_estimators
        self.contamination = contamination
        self.random_state = random_state

        self.model = IsolationForest(
            n_estimators=self.n_estimators,
            contamination=self.contamination,
            random_state=self.random_state,
        )
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.min_raw_score = None
        self.max_raw_score = None

    def fit(self, work_df: pd.DataFrame) -> "WorkIsolationForest":
        """Fit scaler and Isolation Forest on project feature matrix."""
        print(f"  Fitting WorkIsolationForest on {len(work_df)} works with {len(self.feature_cols)} features...")
        X = work_df[self.feature_cols].copy().fillna(0.0)
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)

        raw_scores = self.model.decision_function(X_scaled)
        self.min_raw_score = float(raw_scores.min())
        self.max_raw_score = float(raw_scores.max())
        self.is_fitted = True
        return self

    def score(self, work_df: pd.DataFrame) -> pd.DataFrame:
        """Score work records."""
        if not self.is_fitted:
            raise RuntimeError("WorkIsolationForest must be fitted before scoring.")

        result = work_df.copy()
        X = result[self.feature_cols].copy().fillna(0.0)
        X_scaled = self.scaler.transform(X)

        raw_scores = self.model.decision_function(X_scaled)
        preds = self.model.predict(X_scaled)

        score_range = max(self.max_raw_score - self.min_raw_score, 1e-6)
        normalized_scores = 1.0 - np.clip((raw_scores - self.min_raw_score) / score_range, 0.0, 1.0)

        result["work_if_score"] = np.round(normalized_scores, 4)
        result["work_is_anomaly"] = preds == -1
        return result

    def save(self, filepath: str):
        """Serialize model to disk."""
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        state = {
            "model": self.model,
            "scaler": self.scaler,
            "feature_cols": self.feature_cols,
            "n_estimators": self.n_estimators,
            "contamination": self.contamination,
            "random_state": self.random_state,
            "min_raw_score": self.min_raw_score,
            "max_raw_score": self.max_raw_score,
            "is_fitted": self.is_fitted,
        }
        joblib.dump(state, filepath)
        print(f"  Saved WorkIsolationForest to {filepath}")

    @classmethod
    def load(cls, filepath: str) -> "WorkIsolationForest":
        """Deserialize model from disk."""
        state = joblib.load(filepath)
        instance = cls(
            feature_cols=state["feature_cols"],
            n_estimators=state["n_estimators"],
            contamination=state["contamination"],
            random_state=state["random_state"],
        )
        instance.model = state["model"]
        instance.scaler = state["scaler"]
        instance.min_raw_score = state["min_raw_score"]
        instance.max_raw_score = state["max_raw_score"]
        instance.is_fitted = state["is_fitted"]
        print(f"  Loaded WorkIsolationForest from {filepath}")
        return instance


def run_isolation_forest_pipeline(
    feature_dict: dict[str, pd.DataFrame],
    save_dir: str = None,
) -> tuple[pd.DataFrame, pd.DataFrame, MPIsolationForest, WorkIsolationForest]:
    """
    Train and evaluate Isolation Forest models across both MP and Work grains.

    Returns:
        (scored_mp_df, scored_work_df, mp_model, work_model)
    """
    print("=" * 60)
    print("NEXORAS — Module 4A: Running Isolation Forest Pipeline")
    print("=" * 60)

    # 1. MP-Level Model
    mp_model = MPIsolationForest(contamination=0.08, random_state=42)
    mp_model.fit(feature_dict["mp_features"])
    scored_mps = mp_model.score(feature_dict["mp_features"])
    flagged_mps = scored_mps["if_is_anomaly"].sum()
    print(f"  MP Model complete: {flagged_mps} / {len(scored_mps)} MPs flagged anomalous ({flagged_mps/len(scored_mps)*100:.1f}%)")

    # 2. Work-Level Model
    work_model = WorkIsolationForest(contamination=0.03, random_state=42)
    work_model.fit(feature_dict["work_features"])
    scored_works = work_model.score(feature_dict["work_features"])
    flagged_works = scored_works["work_is_anomaly"].sum()
    print(f"  Work Model complete: {flagged_works} / {len(scored_works)} works flagged anomalous ({flagged_works/len(scored_works)*100:.1f}%)")

    # 3. Optional persistence
    if save_dir:
        mp_path = os.path.join(save_dir, "mp_isolation_forest.joblib")
        work_path = os.path.join(save_dir, "work_isolation_forest.joblib")
        mp_model.save(mp_path)
        work_model.save(work_path)

    print("=" * 60)
    return scored_mps, scored_works, mp_model, work_model


if __name__ == "__main__":
    import sys
    sys.path.insert(0, r"D:\sih 2026\sample mvp\NEXORAS-sample-mvp")
    from backend.ingestion.loader import load_all
    from backend.cleaning.cleaner import clean_all
    from backend.features.builder import build_all_features

    feats = build_all_features(clean_all(load_all()))
    scored_mps, scored_works, mp_model, work_model = run_isolation_forest_pipeline(feats)

    print("\nTop 5 Flagged MPs:")
    top_mps = scored_mps.sort_values(by="if_anomaly_score", ascending=False)[
        ["mp_name", "constituency", "state", "vendor_hhi", "top_vendor_share", "if_anomaly_score"]
    ]
    print(top_mps.head(5).to_string())
