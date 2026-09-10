# Module 13: "Why Flagged?" Engine

## Objective
Translate raw mathematical anomaly attributions (like SHAP values) into human-readable evidence blocks that auditors and domain experts can instantly understand without ML knowledge.

## Overview
While Module 11 provides a high-level explanation of *which intelligence pillars* fired, and Module 12 calculates *which numerical features* drove the anomaly, Module 13 bridges the gap to the end user. It consumes the output of the SHAP `ModelExplainer` and formats it.

## Key Features
- **Signal**: Extracts the human-readable feature name.
- **Evidence**: Displays the exact raw value observed for the entity (e.g., `Observed: 48.50`).
- **Baseline**: Displays the expected median value of typical inliers for comparison (e.g., `Comparable median: 27.10`).
- **Deviation**: Calculates the percentage deviation from the baseline.
- **Risk Contribution**: Displays the normalized mathematical contribution of that feature towards the anomaly score.

Example Output format:
```
[COST DEVIATION Z]
  Observed: 3.50
  Comparable median: 0.20
  Deviation: +1650.0%
  Risk contribution: +1.24 risk points
```

## Status
- **Status**: COMPLETE
- **Code**: `backend/engine/why_flagged.py`
- **Tests**: `tests/test_explainability.py`
