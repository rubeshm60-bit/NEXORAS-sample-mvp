import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
import shap

X = pd.DataFrame(np.random.randn(100, 4), columns=['A', 'B', 'C', 'D'])
model = IsolationForest(random_state=42).fit(X)
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X.iloc[:5])
print("SHAP values shape:", np.array(shap_values).shape)
print("SHAP values first row:", shap_values[0])
print("Decision function first row:", model.decision_function(X.iloc[:5])[0])
print("Expected value:", explainer.expected_value)
