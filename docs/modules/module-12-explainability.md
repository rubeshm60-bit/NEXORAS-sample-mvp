# Module 12: Explainability / SHAP

## Objective
Provide granular feature attribution for machine learning models (specifically the `IsolationForest` anomaly detectors), identifying *which* features contributed to a project or entity being flagged as anomalous, and by *how much*.

## Overview
Because tree-based anomaly detection models like Isolation Forest are opaque, we utilize SHAP (SHapley Additive exPlanations) via `shap.TreeExplainer`. This generates an additive attribution score for every feature that makes up an instance.

For `IsolationForest`, SHAP explains the *path length* required to isolate a point. Anomalies have significantly shorter path lengths. Thus, features with **negative SHAP values** are the ones driving the isolation process faster, thereby increasing the anomaly score. The module negates these values to produce a positive `anomaly_contribution` score, making it easier for down-stream layers (like Module 13) to interpret: *higher positive contribution = feature is highly anomalous*.

## Key Components
- **`ModelExplainer`**: A wrapper class in `backend/engine/shap_explainer.py` that takes a fitted NEXORAS model wrapper and its feature names.
- **`explain_instances()`**: Computes the exact SHAP attribution for each feature, maps negative path length deviations to positive anomaly risks, and fetches baseline medians from the training step.

## Status
- **Status**: COMPLETE
- **Code**: `backend/engine/shap_explainer.py`
- **Tests**: `tests/test_explainability.py`
