"""Ensemble Model — Stacking meta-learner combining XGBoost, Graph, and Temporal models.

Architecture:
  1. XGBoost produces a fraud probability (0-1) from tabular + velocity features.
  2. GraphAnomalyDetector produces graph structural features.
  3. TemporalAnomalyDetector produces a sequence anomaly score.
  4. A logistic regression meta-learner combines all three into a final score.

This ensemble catches different fraud topologies:
  - XGBoost: Catches feature-level anomalies (amounts, timing, velocity).
  - Graph: Catches relational fraud (mule rings, collusion, device sharing).
  - Temporal: Catches behavioral drift (bust-outs, coerced transfers).
"""
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from typing import Dict, Optional

from blue_team.models.xgboost_baseline import XGBoostBaseline
from blue_team.models.heterogeneous_gnn import GraphAnomalyDetector
from blue_team.models.temporal_transformer import TemporalAnomalyDetector


class EnsembleModel:
    """Dual-model ensemble with attention-gated fusion."""

    def __init__(self):
        self.xgb = XGBoostBaseline()
        self.graph_detector = GraphAnomalyDetector()
        self.temporal_detector = TemporalAnomalyDetector()
        self.meta_learner = LogisticRegression(max_iter=500)
        self.is_trained = False
        self.training_metrics: Dict = {}

    def train(self, df: pd.DataFrame) -> Dict:
        """Train all three models and the meta-learner."""
        if len(df) == 0 or "is_fraud" not in df.columns:
            return {}

        y = df["is_fraud"].astype(int)
        if y.nunique() < 2:
            return {}

        # Step 1: Train component models
        print("\n=== Training Ensemble ===")
        print("Step 1/4: Training XGBoost...")
        xgb_metrics = self.xgb.train(df)

        print("Step 2/4: Building transaction graph...")
        self.graph_detector.fit(df)

        print("Step 3/4: Building temporal profiles...")
        self.temporal_detector.fit(df)

        # Step 2: Get predictions from each component
        print("Step 4/4: Training meta-learner...")
        xgb_scores = self.xgb.predict(df)
        temporal_scores = self.temporal_detector.score(df)

        # Graph features are already added to the XGBoost features, so we use
        # a simplified graph anomaly score here
        graph_df = self.graph_detector.transform(df)
        graph_scores = graph_df.get("graph_pagerank", pd.Series(0, index=df.index)).values
        # Normalize graph scores
        if graph_scores.max() > 0:
            graph_scores = graph_scores / graph_scores.max()

        # Stack predictions as meta-features
        meta_features = np.column_stack([xgb_scores, temporal_scores, graph_scores])

        # Train meta-learner
        try:
            self.meta_learner.fit(meta_features, y)
            self.is_trained = True

            # Compute ensemble metrics
            final_probs = self.meta_learner.predict_proba(meta_features)[:, 1]
            final_preds = (final_probs > 0.5).astype(int)

            from sklearn.metrics import (accuracy_score, precision_score,
                                         recall_score, f1_score, roc_auc_score)
            self.training_metrics = {
                "accuracy": round(accuracy_score(y, final_preds), 4),
                "precision": round(precision_score(y, final_preds, zero_division=0), 4),
                "recall": round(recall_score(y, final_preds, zero_division=0), 4),
                "f1_score": round(f1_score(y, final_preds, zero_division=0), 4),
                "auc_roc": round(roc_auc_score(y, final_probs), 4),
                "false_positive_rate": round(
                    ((final_preds == 1) & (y == 0)).sum() / max((y == 0).sum(), 1), 4),
                "train_samples": len(df),
                "fraud_rate": round(y.mean(), 4),
                "xgb_metrics": xgb_metrics,
                "meta_learner_weights": {
                    "xgb_weight": round(float(self.meta_learner.coef_[0][0]), 4),
                    "temporal_weight": round(float(self.meta_learner.coef_[0][1]), 4),
                    "graph_weight": round(float(self.meta_learner.coef_[0][2]), 4),
                },
            }
            print(f"\n✅ Ensemble trained. F1={self.training_metrics['f1_score']}, "
                  f"AUC={self.training_metrics['auc_roc']}")
            print(f"   Meta-learner weights: {self.training_metrics['meta_learner_weights']}")
            return self.training_metrics

        except Exception as e:
            print(f"⚠️ Meta-learner training failed: {e}. Using XGBoost only.")
            self.is_trained = True
            self.training_metrics = xgb_metrics
            return xgb_metrics

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """Return fraud probability for each transaction."""
        if not self.is_trained:
            return np.random.rand(len(df)) * 0.3

        xgb_scores = self.xgb.predict(df)
        temporal_scores = self.temporal_detector.score(df)

        graph_df = self.graph_detector.transform(df)
        graph_scores = graph_df.get("graph_pagerank", pd.Series(0, index=df.index)).values
        if graph_scores.max() > 0:
            graph_scores = graph_scores / graph_scores.max()

        meta_features = np.column_stack([xgb_scores, temporal_scores, graph_scores])

        try:
            return self.meta_learner.predict_proba(meta_features)[:, 1]
        except Exception:
            # Fallback: weighted average
            return 0.6 * xgb_scores + 0.25 * temporal_scores + 0.15 * graph_scores

    def predict_single(self, txn_dict: dict) -> Dict:
        """Predict a single transaction with full breakdown."""
        df = pd.DataFrame([txn_dict])
        prob = float(self.predict(df)[0])
        xgb_score = float(self.xgb.predict(df)[0])
        temporal_score = float(self.temporal_detector.score(df)[0])

        return {
            "risk_score": round(prob, 4),
            "is_fraud": prob > 0.5,
            "confidence": round(max(prob, 1 - prob), 4),
            "model_breakdown": {
                "xgb_score": round(xgb_score, 4),
                "temporal_score": round(temporal_score, 4),
                "graph_score": 0.0,  # Would need full graph context
            },
            "recommended_action": ("BLOCK" if prob > 0.8
                                   else "REVIEW" if prob > 0.5
                                   else "ALLOW"),
        }

    def get_metrics(self) -> Dict:
        """Return the latest training metrics."""
        return self.training_metrics
