import shap
import pandas as pd
import numpy as np

class SHAPExplainer:
    def __init__(self, model_instance):
        self.model_instance = model_instance
        self.explainer = None
        
    def fit(self, X_background):
        if not self.model_instance.is_trained:
            return
        
        # Take a small background sample for TreeExplainer
        bg = X_background.sample(min(100, len(X_background)))
        
        # TreeExplainer is fast for gradient boosting
        # For HistGradientBoosting, shap sometimes prefers KernelExplainer or specific wrappers, 
        # but TreeExplainer works with many sklearn tree ensembles. If it fails, fallback to Kernel.
        try:
            self.explainer = shap.TreeExplainer(self.model_instance.model)
        except:
            # Fallback for HistGradientBoosting if TreeExplainer fails
            self.explainer = shap.KernelExplainer(self.model_instance.model.predict_proba, bg)
        
    def explain(self, df):
        if not self.explainer:
            return {}
            
        X = self.model_instance.preprocess(df)
        shap_values = self.explainer.shap_values(X)
        
        # Return top 3 features for the first transaction
        if len(X) == 0:
            return {}
            
        vals = shap_values[0]
        feature_names = X.columns
        
        # Sort by absolute impact
        impacts = [(feature_names[i], float(vals[i])) for i in range(len(vals))]
        impacts.sort(key=lambda x: abs(x[1]), reverse=True)
        
        # Format for UI
        result = {}
        for feat, val in impacts[:3]:
            result[feat] = round(val, 3)
            
        return result
