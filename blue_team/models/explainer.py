"""SHAP Explainer for the Ensemble Model.

Provides human-readable explanations for fraud predictions using SHAP values.
Works with the XGBoost component of the ensemble (which captures most signal).
"""
import shap
import pandas as pd
import numpy as np
from typing import Dict, List, Optional


# Human-readable feature descriptions for the UI
FEATURE_DESCRIPTIONS = {
    "amount_inr": "Transaction amount",
    "hour_of_day": "Time of transaction",
    "day_of_week": "Day of week",
    "is_weekend": "Weekend transaction",
    "is_international": "International transaction",
    "is_festival_period": "Festival season",
    "sender_account_age_days": "Account age",
    "sender_avg_monthly_txn_count": "Avg monthly transaction count",
    "sender_avg_monthly_spend_inr": "Avg monthly spending",
    "sender_credit_score": "Credit score",
    "txn_count_last_1h": "Transactions in last hour",
    "txn_count_last_24h": "Transactions in last 24h",
    "txn_amount_last_24h": "Amount spent in last 24h",
    "unique_receivers_last_24h": "Unique receivers in 24h",
    "unique_devices_last_7d": "Devices used in 7 days",
    "amount_zscore": "Amount deviation from normal",
    "time_since_last_txn_seconds": "Time since last transaction",
    "is_new_receiver": "First-time receiver",
    "is_new_device": "New device used",
    "amount_to_income_ratio": "Amount vs income ratio",
    "amount_to_avg_spend_ratio": "Amount vs avg spend ratio",
    "rail_encoded": "Payment channel type",
    "channel_encoded": "Transaction channel",
    "mcc_risk_score": "Merchant category risk",
    "is_round_amount": "Round amount flag",
    "hour_risk_bucket": "Time-of-day risk",
    "txn_velocity_ratio": "Transaction velocity anomaly",
}


class SHAPExplainer:
    def __init__(self, model_instance):
        """
        Args:
            model_instance: An XGBoostBaseline instance (or ensemble.xgb).
        """
        self.model_instance = model_instance
        self.explainer = None
        self.background_data = None

    def fit(self, X_background: pd.DataFrame):
        """Initialize the SHAP explainer with background data."""
        if not self.model_instance.is_trained:
            return

        # Sample background data for efficiency
        n_bg = min(100, len(X_background))
        self.background_data = X_background.sample(n_bg, random_state=42)

        try:
            self.explainer = shap.TreeExplainer(self.model_instance.model)
            print(f"✅ SHAP TreeExplainer initialized with {n_bg} background samples")
        except Exception as e:
            print(f"⚠️ TreeExplainer failed ({e}), using KernelExplainer...")
            try:
                self.explainer = shap.KernelExplainer(
                    self.model_instance.model.predict_proba,
                    self.background_data)
            except Exception as e2:
                print(f"❌ KernelExplainer also failed: {e2}")
                self.explainer = None

    def explain(self, df: pd.DataFrame, top_k: int = 5) -> Dict:
        """Explain predictions for one or more transactions.

        Returns:
            Dict with 'features' (list of top contributing features) and
            'explanation_text' (human-readable summary).
        """
        if not self.explainer:
            return {"features": [], "explanation_text": "Explainer not initialized"}

        X = self.model_instance.preprocess(df)

        try:
            shap_values = self.explainer.shap_values(X)
        except Exception as e:
            return {"features": [], "explanation_text": f"SHAP failed: {e}"}

        # Handle different SHAP output formats
        if isinstance(shap_values, list):
            # Binary classification: shap_values[1] = fraud class
            vals = shap_values[1][0] if len(shap_values) > 1 else shap_values[0][0]
        elif isinstance(shap_values, np.ndarray):
            vals = shap_values[0]
        else:
            return {"features": [], "explanation_text": "Unexpected SHAP format"}

        feature_names = list(X.columns)
        feature_values = X.iloc[0].values

        # Sort by absolute impact
        impacts = []
        for i in range(len(vals)):
            name = feature_names[i]
            shap_val = float(vals[i])
            feat_val = float(feature_values[i])
            description = FEATURE_DESCRIPTIONS.get(name, name)
            direction = "🔴" if shap_val > 0 else "🟢"

            impacts.append({
                "feature": name,
                "description": description,
                "shap_value": round(shap_val, 4),
                "feature_value": round(feat_val, 4),
                "direction": direction,
                "contribution": "increases risk" if shap_val > 0 else "decreases risk",
            })

        impacts.sort(key=lambda x: abs(x["shap_value"]), reverse=True)
        top_features = impacts[:top_k]

        # Generate human-readable explanation
        explanation_parts = []
        for f in top_features[:3]:
            explanation_parts.append(
                f"{f['direction']} {f['description']}: {f['feature_value']:.1f} "
                f"({f['contribution']}, SHAP: {f['shap_value']:+.3f})")

        return {
            "features": top_features,
            "all_features": impacts,
            "explanation_text": " | ".join(explanation_parts),
        }

    def explain_batch(self, df: pd.DataFrame, top_k: int = 3) -> List[Dict]:
        """Explain each transaction in a batch."""
        results = []
        for i in range(min(len(df), 50)):  # Cap at 50 for performance
            row_df = df.iloc[[i]]
            result = self.explain(row_df, top_k=top_k)
            result["transaction_id"] = df.iloc[i].get("transaction_id", f"TXN_{i}")
            results.append(result)
        return results
