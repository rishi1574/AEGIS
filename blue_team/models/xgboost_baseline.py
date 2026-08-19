from sklearn.ensemble import HistGradientBoostingClassifier
import pandas as pd
import numpy as np

class XGBoostBaseline:
    def __init__(self):
        # We use HistGradientBoostingClassifier as it's equivalent to XGBoost but avoids Mac libomp issues
        self.model = HistGradientBoostingClassifier(
            max_iter=100,
            learning_rate=0.1,
            max_depth=6
        )
        self.is_trained = False
        self.feature_cols = [
            "amount_inr", "sender_account_age_days", "sender_avg_monthly_txn_count",
            "sender_avg_monthly_spend_inr", "sender_credit_score", "hour_of_day",
            "day_of_week", "is_weekend", "is_international", "is_festival_period"
        ]
        
    def preprocess(self, df):
        # Fill missing values and ensure boolean are int
        X = df[self.feature_cols].copy()
        X = X.fillna(0)
        if 'is_weekend' in X.columns:
            X['is_weekend'] = X['is_weekend'].astype(int)
        if 'is_international' in X.columns:
            X['is_international'] = X['is_international'].astype(int)
        if 'is_festival_period' in X.columns:
            X['is_festival_period'] = X['is_festival_period'].astype(int)
        return X

    def train(self, df):
        if len(df) == 0:
            return
            
        X = self.preprocess(df)
        y = df['is_fraud'].astype(int)
        
        self.model.fit(X, y)
        self.is_trained = True
        print(f"XGBoost Model trained on {len(X)} transactions.")
        
    def predict(self, df):
        if not self.is_trained:
            # Random guessing if untrained
            return np.random.rand(len(df))
            
        X = self.preprocess(df)
        return self.model.predict_proba(X)[:, 1]
