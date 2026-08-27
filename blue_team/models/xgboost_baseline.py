"""XGBoost Baseline Model with expanded feature set.

Uses HistGradientBoostingClassifier (equivalent to XGBoost, no libomp dependency).
Expanded from 10 to 25+ features including velocity, behavioral, and engineered features.
"""
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import numpy as np
import json
from pathlib import Path

# All features available from the Transaction dataclass
FEATURE_COLS = [
    # Base transaction features
    "amount_inr",
    "hour_of_day",
    "day_of_week",
    "is_weekend",
    "is_international",
    "is_festival_period",

    # Sender profile features
    "sender_account_age_days",
    "sender_avg_monthly_txn_count",
    "sender_avg_monthly_spend_inr",
    "sender_credit_score",

    # Velocity features (computed by BaseAgent.compute_velocity)
    "txn_count_last_1h",
    "txn_count_last_24h",
    "txn_amount_last_24h",
    "unique_receivers_last_24h",
    "unique_devices_last_7d",
    "amount_zscore",
    "time_since_last_txn_seconds",

    # Binary flags
    "is_new_receiver",
    "is_new_device",

    # Engineered features (computed during preprocessing)
    "amount_to_income_ratio",
    "amount_to_avg_spend_ratio",
    "rail_encoded",
    "channel_encoded",
    "mcc_risk_score",
    "is_round_amount",
    "hour_risk_bucket",
    "txn_velocity_ratio",
]

# MCC codes associated with higher fraud risk
HIGH_RISK_MCCS = {"5944", "5732", "5999", "6012", "5045", "7299"}
MEDIUM_RISK_MCCS = {"5311", "5691", "7011", "7832"}


class XGBoostBaseline:
    def __init__(self):
        self.model = HistGradientBoostingClassifier(
            max_iter=300,
            learning_rate=0.05,
            max_depth=8,
            min_samples_leaf=20,
            l2_regularization=1.0,
            max_bins=255,
        )
        self.is_trained = False
        self.rail_encoder = LabelEncoder()
        self.channel_encoder = LabelEncoder()
        self.known_rails = []
        self.known_channels = []
        self.feature_cols = FEATURE_COLS

    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer features and return model-ready DataFrame."""
        X = pd.DataFrame(index=df.index)

        # Copy base features
        for col in ["amount_inr", "hour_of_day", "day_of_week",
                     "sender_account_age_days", "sender_avg_monthly_txn_count",
                     "sender_avg_monthly_spend_inr", "sender_credit_score",
                     "txn_count_last_1h", "txn_count_last_24h",
                     "txn_amount_last_24h", "unique_receivers_last_24h",
                     "unique_devices_last_7d", "amount_zscore",
                     "time_since_last_txn_seconds"]:
            X[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        # Boolean features → int
        for col in ["is_weekend", "is_international", "is_festival_period",
                     "is_new_receiver", "is_new_device"]:
            if col in df.columns:
                X[col] = df[col].astype(int) if df[col].dtype != int else df[col]
            else:
                X[col] = 0

        # Engineered: amount ratios
        income = df.get("sender_avg_monthly_spend_inr", pd.Series(dtype=float)).fillna(1).replace(0, 1)
        X["amount_to_income_ratio"] = X["amount_inr"] / income
        X["amount_to_avg_spend_ratio"] = X["amount_inr"] / income.clip(lower=1)

        # Engineered: payment rail encoding
        if "payment_rail" in df.columns:
            rail_map = {"UPI_P2P": 0, "UPI_P2M": 1, "CARD_CNP": 2, "CARD_POS": 3,
                        "NEFT": 4, "RTGS": 5, "IMPS": 6, "BNPL": 7, "WIRE_INTL": 8}
            X["rail_encoded"] = df["payment_rail"].map(rail_map).fillna(9).astype(int)
        else:
            X["rail_encoded"] = 0

        # Engineered: channel encoding
        if "channel" in df.columns:
            ch_map = {"mobile_app": 0, "web": 1, "pos_terminal": 2, "api": 3}
            X["channel_encoded"] = df["channel"].map(ch_map).fillna(4).astype(int)
        else:
            X["channel_encoded"] = 0

        # Engineered: MCC risk score
        if "mcc_code" in df.columns:
            X["mcc_risk_score"] = df["mcc_code"].apply(
                lambda x: 3 if str(x) in HIGH_RISK_MCCS
                else 2 if str(x) in MEDIUM_RISK_MCCS else 1)
        else:
            X["mcc_risk_score"] = 1

        # Engineered: round amount flag
        X["is_round_amount"] = (X["amount_inr"] % 1000 == 0).astype(int)

        # Engineered: hour risk bucket (late night = high risk)
        X["hour_risk_bucket"] = X["hour_of_day"].apply(
            lambda h: 3 if 0 <= h <= 5 else 2 if 22 <= h <= 23 else 1)

        # Engineered: velocity ratio (txns in last hour vs avg daily)
        avg_daily = (X["sender_avg_monthly_txn_count"] / 30).clip(lower=0.1)
        X["txn_velocity_ratio"] = X["txn_count_last_1h"] / avg_daily

        # Fill any remaining NaN
        X = X.fillna(0)

        # Ensure all feature columns exist
        for col in self.feature_cols:
            if col not in X.columns:
                X[col] = 0

        return X[self.feature_cols]

    def train(self, df: pd.DataFrame) -> dict:
        """Train the model and return metrics."""
        if len(df) == 0:
            return {}

        X = self.preprocess(df)
        y = df["is_fraud"].astype(int)

        # Check that we have both classes
        if y.nunique() < 2:
            print("⚠️  Only one class in training data, skipping training.")
            return {}

        self.model.fit(X, y)
        self.is_trained = True

        # Training metrics
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
        y_pred = self.model.predict(X)
        y_prob = self.model.predict_proba(X)[:, 1]

        metrics = {
            "accuracy": round(accuracy_score(y, y_pred), 4),
            "precision": round(precision_score(y, y_pred, zero_division=0), 4),
            "recall": round(recall_score(y, y_pred, zero_division=0), 4),
            "f1": round(f1_score(y, y_pred, zero_division=0), 4),
            "auc": round(roc_auc_score(y, y_prob), 4),
            "train_samples": len(df),
            "fraud_rate": round(y.mean(), 4),
        }
        print(f"XGBoost trained on {len(X)} samples. Metrics: {metrics}")
        return metrics

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """Return fraud probability for each transaction."""
        if not self.is_trained:
            return np.random.rand(len(df)) * 0.3  # Low random scores if untrained

        X = self.preprocess(df)
        return self.model.predict_proba(X)[:, 1]

    def predict_single(self, txn_dict: dict) -> dict:
        """Predict a single transaction and return structured result."""
        df = pd.DataFrame([txn_dict])
        prob = self.predict(df)[0]
        return {
            "risk_score": round(float(prob), 4),
            "is_fraud": bool(prob > 0.5),
            "confidence": round(float(max(prob, 1 - prob)), 4),
            "recommended_action": "BLOCK" if prob > 0.8 else "REVIEW" if prob > 0.5 else "ALLOW",
        }

    def get_feature_importance(self) -> dict:
        """Return feature importances as a dict."""
        if not self.is_trained:
            return {}
        try:
            importances = self.model.feature_importances_
        except AttributeError:
            # HistGradientBoostingClassifier may not expose feature_importances_
            # in some sklearn versions — return empty dict gracefully
            return {}
        return {col: round(float(imp), 4)
                for col, imp in sorted(zip(self.feature_cols, importances),
                                       key=lambda x: -x[1])}

    def save(self, path: str = "data/models/xgboost_model.pkl"):
        """Save trained model to disk."""
        import pickle
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump({"model": self.model, "is_trained": self.is_trained,
                         "feature_cols": self.feature_cols}, f)
        print(f"💾 Model saved to {path}")

    def load(self, path: str = "data/models/xgboost_model.pkl"):
        """Load trained model from disk."""
        import pickle
        if Path(path).exists():
            with open(path, "rb") as f:
                data = pickle.load(f)
                self.model = data["model"]
                self.is_trained = data["is_trained"]
                self.feature_cols = data.get("feature_cols", FEATURE_COLS)
            print(f"📦 Model loaded from {path}")
