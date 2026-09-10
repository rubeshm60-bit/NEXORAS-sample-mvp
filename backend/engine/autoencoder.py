"""
NEXORAS Module 4B — Neural Autoencoder Anomaly Engine
Deep reconstruction-based unsupervised anomaly detection for MPLADS fund monitoring.

Theoretical Concept:
- An Autoencoder is a symmetric neural network trained to minimize reconstruction loss:
  L(x, x_hat) = ||x - g(f(x))||^2
- The network is forced through a low-dimensional bottleneck (latent dimension = 8).
- Under the bottleneck constraint, the network learns the principal non-linear manifold
  of normal MP expenditure behaviors (standard utilization rates, typical contractor spread).
- When anomalous MP profiles pass through the network (e.g., 100% single-contractor dominance
  with 0% ground completion), the network fails to reconstruct them faithfully.
- The resulting Mean Squared Error (MSE) is the anomaly signal:
  High Reconstruction MSE = High Risk of Fraud / Irregularity.

Architecture:
- Input: 9 normalized features
- Encoder: Linear(9 -> 32) -> ReLU -> Linear(32 -> 16) -> ReLU -> Linear(16 -> 8) [Bottleneck]
- Decoder: Linear(8 -> 16) -> ReLU -> Linear(16 -> 32) -> ReLU -> Linear(32 -> 9)
- Loss: Mean Squared Error (MSE)
- Threshold: 92nd percentile of training reconstruction error (8% contamination rate)
"""
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

# Check PyTorch availability
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False
    from sklearn.neural_network import MLPRegressor

# Default MP feature columns
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


if PYTORCH_AVAILABLE:
    class PyTorchAutoencoderNet(nn.Module):
        """Deep Bottleneck Autoencoder Neural Network."""

        def __init__(self, input_dim: int, latent_dim: int = 8):
            super().__init__()
            self.encoder = nn.Sequential(
                nn.Linear(input_dim, 32),
                nn.ReLU(),
                nn.Linear(32, 16),
                nn.ReLU(),
                nn.Linear(16, latent_dim),
                nn.ReLU(),
            )
            self.decoder = nn.Sequential(
                nn.Linear(latent_dim, 16),
                nn.ReLU(),
                nn.Linear(16, 32),
                nn.ReLU(),
                nn.Linear(32, input_dim),
            )

        def forward(self, x):
            latent = self.encoder(x)
            reconstructed = self.decoder(latent)
            return reconstructed, latent


class MPAutoencoder:
    """
    Autoencoder Anomaly Detector for MP-level fund monitoring.
    Uses PyTorch if installed, with a verified scikit-learn MLPRegressor fallback.
    """

    def __init__(
        self,
        feature_cols: list[str] = None,
        latent_dim: int = 8,
        epochs: int = 80,
        lr: float = 0.005,
        contamination: float = 0.08,
        random_state: int = 42,
    ):
        self.feature_cols = feature_cols or DEFAULT_MP_FEATURES
        self.input_dim = len(self.feature_cols)
        self.latent_dim = latent_dim
        self.epochs = epochs
        self.lr = lr
        self.contamination = contamination
        self.random_state = random_state

        self.scaler = StandardScaler()
        self.is_fitted = False
        self.threshold = None
        self.min_mse = None
        self.max_mse = None
        self.training_loss_history = []
        self.backend_type = "pytorch" if PYTORCH_AVAILABLE else "sklearn"
        self.model = None

    def fit(self, mp_df: pd.DataFrame) -> "MPAutoencoder":
        """Train the Autoencoder on MP feature vectors to minimize reconstruction loss."""
        print(f"  Fitting MPAutoencoder ({self.backend_type.upper()}) on {len(mp_df)} MPs with {self.input_dim} features...")
        X = mp_df[self.feature_cols].copy().fillna(0.0)
        X_scaled = self.scaler.fit_transform(X)

        if PYTORCH_AVAILABLE:
            torch.manual_seed(self.random_state)
            np.random.seed(self.random_state)
            self.model = PyTorchAutoencoderNet(self.input_dim, self.latent_dim)
            optimizer = optim.Adam(self.model.parameters(), lr=self.lr, weight_decay=1e-5)
            criterion = nn.MSELoss()

            tensor_x = torch.tensor(X_scaled, dtype=torch.float32)
            self.model.train()
            self.training_loss_history = []

            for epoch in range(self.epochs):
                optimizer.zero_grad()
                reconstructed, _ = self.model(tensor_x)
                loss = criterion(reconstructed, tensor_x)
                loss.backward()
                optimizer.step()
                self.training_loss_history.append(float(loss.item()))

            # Compute training reconstruction errors
            self.model.eval()
            with torch.no_grad():
                recon, _ = self.model(tensor_x)
                sq_errors = ((tensor_x - recon) ** 2).numpy()
                mse_errors = sq_errors.mean(axis=1)

        else:
            # Fallback using scikit-learn MLPRegressor as symmetric autoencoder (y = X)
            np.random.seed(self.random_state)
            self.model = MLPRegressor(
                hidden_layer_sizes=(32, 16, self.latent_dim, 16, 32),
                activation="relu",
                solver="adam",
                alpha=1e-4,
                learning_rate_init=self.lr,
                max_iter=self.epochs * 3,
                random_state=self.random_state,
                tol=1e-4,
            )
            self.model.fit(X_scaled, X_scaled)
            recon = self.model.predict(X_scaled)
            sq_errors = (X_scaled - recon) ** 2
            mse_errors = sq_errors.mean(axis=1)
            self.training_loss_history = [float(l) for l in self.model.loss_curve_]

        # Calibrate threshold at (1.0 - contamination) percentile
        percentile_target = (1.0 - self.contamination) * 100.0
        self.threshold = float(np.percentile(mse_errors, percentile_target))
        self.min_mse = float(mse_errors.min())
        self.max_mse = float(mse_errors.max())
        self.is_fitted = True

        first_loss = self.training_loss_history[0] if self.training_loss_history else 0.0
        final_loss = self.training_loss_history[-1] if self.training_loss_history else 0.0
        print(f"  Training complete: Initial Loss={first_loss:.4f}, Final Loss={final_loss:.4f}")
        print(f"  Calibrated Anomaly Threshold={self.threshold:.4f} (MSE > threshold = anomaly)")
        return self

    def score(self, mp_df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute reconstruction error for each MP and return scored DataFrame with:
        - ae_reconstruction_mse: raw MSE
        - ae_anomaly_score: float in [0.0, 1.0] (1.0 = highest reconstruction error)
        - ae_is_anomaly: bool (True = MSE > threshold)
        """
        if not self.is_fitted:
            raise RuntimeError("MPAutoencoder must be fitted before scoring.")

        result = mp_df.copy()
        X = result[self.feature_cols].copy().fillna(0.0)
        X_scaled = self.scaler.transform(X)

        if self.backend_type == "pytorch" and PYTORCH_AVAILABLE:
            self.model.eval()
            with torch.no_grad():
                tensor_x = torch.tensor(X_scaled, dtype=torch.float32)
                recon, _ = self.model(tensor_x)
                sq_errors = ((tensor_x - recon) ** 2).numpy()
                mse_errors = sq_errors.mean(axis=1)
        else:
            recon = self.model.predict(X_scaled)
            sq_errors = (X_scaled - recon) ** 2
            mse_errors = sq_errors.mean(axis=1)

        # Normalize MSE into [0.0, 1.0]
        mse_range = max(self.max_mse - self.min_mse, 1e-6)
        normalized_scores = np.clip((mse_errors - self.min_mse) / mse_range, 0.0, 1.0)

        result["ae_reconstruction_mse"] = np.round(mse_errors, 6)
        result["ae_anomaly_score"] = np.round(normalized_scores, 4)
        result["ae_is_anomaly"] = mse_errors >= self.threshold
        return result

    def explain_mp(self, mp_row: pd.Series) -> list[dict]:
        """
        Show feature-by-feature reconstruction error for an individual MP.
        Features with the highest reconstruction error are the primary drivers of anomaly.
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before explaining.")

        row_df = pd.DataFrame([mp_row[self.feature_cols].fillna(0.0)])
        X_scaled = self.scaler.transform(row_df)

        if self.backend_type == "pytorch" and PYTORCH_AVAILABLE:
            self.model.eval()
            with torch.no_grad():
                tensor_x = torch.tensor(X_scaled, dtype=torch.float32)
                recon, _ = self.model(tensor_x)
                recon_scaled = recon.numpy()
        else:
            recon_scaled = self.model.predict(X_scaled)

        # Inverse transform reconstruction back to original physical scale
        recon_orig = self.scaler.inverse_transform(recon_scaled)[0]
        actual_orig = row_df.iloc[0].values

        explanations = []
        for idx, col in enumerate(self.feature_cols):
            actual = float(actual_orig[idx])
            reconstructed = float(recon_orig[idx])
            feature_sq_err = float((X_scaled[0][idx] - recon_scaled[0][idx]) ** 2)

            explanations.append({
                "feature": col,
                "observed": round(actual, 4),
                "reconstructed": round(reconstructed, 4),
                "scaled_reconstruction_error": round(feature_sq_err, 4),
            })

        # Sort by highest reconstruction error
        explanations.sort(key=lambda x: x["scaled_reconstruction_error"], reverse=True)
        return explanations

    def save(self, filepath: str):
        """Serialize Autoencoder model and scaler to disk."""
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        state = {
            "backend_type": self.backend_type,
            "scaler": self.scaler,
            "feature_cols": self.feature_cols,
            "input_dim": self.input_dim,
            "latent_dim": self.latent_dim,
            "epochs": self.epochs,
            "lr": self.lr,
            "contamination": self.contamination,
            "random_state": self.random_state,
            "threshold": self.threshold,
            "min_mse": self.min_mse,
            "max_mse": self.max_mse,
            "training_loss_history": self.training_loss_history,
            "is_fitted": self.is_fitted,
        }

        if self.backend_type == "pytorch" and PYTORCH_AVAILABLE:
            state["model_state_dict"] = self.model.state_dict()
        else:
            state["model"] = self.model

        joblib.dump(state, filepath)
        print(f"  Saved MPAutoencoder to {filepath}")

    @classmethod
    def load(cls, filepath: str) -> "MPAutoencoder":
        """Deserialize Autoencoder model from disk."""
        state = joblib.load(filepath)
        instance = cls(
            feature_cols=state["feature_cols"],
            latent_dim=state["latent_dim"],
            epochs=state["epochs"],
            lr=state["lr"],
            contamination=state["contamination"],
            random_state=state["random_state"],
        )
        instance.backend_type = state["backend_type"]
        instance.scaler = state["scaler"]
        instance.threshold = state["threshold"]
        instance.min_mse = state["min_mse"]
        instance.max_mse = state["max_mse"]
        instance.training_loss_history = state["training_loss_history"]
        instance.is_fitted = state["is_fitted"]

        if instance.backend_type == "pytorch" and PYTORCH_AVAILABLE:
            instance.model = PyTorchAutoencoderNet(instance.input_dim, instance.latent_dim)
            instance.model.load_state_dict(state["model_state_dict"])
            instance.model.eval()
        else:
            instance.model = state["model"]

        print(f"  Loaded MPAutoencoder ({instance.backend_type.upper()}) from {filepath}")
        return instance


def run_autoencoder_pipeline(
    feature_dict: dict[str, pd.DataFrame],
    save_dir: str = None,
) -> tuple[pd.DataFrame, MPAutoencoder]:
    """Train Autoencoder and score all MPs."""
    print("=" * 60)
    print("NEXORAS — Module 4B: Running Autoencoder Pipeline")
    print("=" * 60)
    ae_model = MPAutoencoder(contamination=0.08, random_state=42)
    ae_model.fit(feature_dict["mp_features"])
    scored_mps = ae_model.score(feature_dict["mp_features"])

    flagged_mps = scored_mps["ae_is_anomaly"].sum()
    print(f"  Autoencoder complete: {flagged_mps} / {len(scored_mps)} MPs flagged anomalous ({flagged_mps/len(scored_mps)*100:.1f}%)")

    if save_dir:
        ae_path = os.path.join(save_dir, "mp_autoencoder.joblib")
        ae_model.save(ae_path)

    print("=" * 60)
    return scored_mps, ae_model


if __name__ == "__main__":
    import sys
    sys.path.insert(0, r"D:\sih 2026\sample mvp\NEXORAS-sample-mvp")
    from backend.ingestion.loader import load_all
    from backend.cleaning.cleaner import clean_all
    from backend.features.builder import build_all_features

    feats = build_all_features(clean_all(load_all()))
    scored_mps, ae_model = run_autoencoder_pipeline(feats)

    print("\nTop 5 Flagged MPs by Autoencoder:")
    top_mps = scored_mps.sort_values(by="ae_anomaly_score", ascending=False)[
        ["mp_name", "constituency", "state", "vendor_hhi", "top_vendor_share", "ae_anomaly_score"]
    ]
    print(top_mps.head(5).to_string())
