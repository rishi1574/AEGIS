"""Data Service — Singleton that loads generated data and serves the backend.

On startup, checks for pre-generated data in data/generated/.
If found, loads transaction CSVs and adversarial results JSON.
If not found, returns empty/null data clearly.

Also lazily loads the trained XGBoost model for real-time prediction.
"""
import json
import time
import pickle
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class DataService:
    """Singleton data service for the AEGIS backend."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self.transactions_df: Optional[pd.DataFrame] = None
        self.adversarial_results: Dict = {}
        self.model_metrics: Dict = {}
        self.interceptions: List[Dict] = []
        self.is_loaded = False
        self.data_dir = Path("data/generated")

        # Model state (lazy loaded)
        self._model = None
        self._model_loaded = False
        self._inference_latencies: List[float] = []  # track real latencies

    def load(self):
        """Load pre-generated data from disk."""
        try:
            # Load transactions
            txn_path = self.data_dir / "all_transactions.csv"
            if not txn_path.exists():
                txn_path = self.data_dir / "train_txns.csv"

            if txn_path.exists():
                self.transactions_df = pd.read_csv(txn_path)
                print(f"📦 Loaded {len(self.transactions_df)} transactions from {txn_path}")
            else:
                print("⚠️ No transaction data found. Run the adversarial loop first.")
                self.transactions_df = pd.DataFrame()

            # Load adversarial results
            results_path = self.data_dir / "adversarial_results.json"
            if results_path.exists():
                with open(results_path) as f:
                    self.adversarial_results = json.load(f)
                print(f"📦 Loaded adversarial results ({len(self.adversarial_results.get('iterations', []))} iterations)")
            else:
                print("⚠️ No adversarial results found.")
                self.adversarial_results = {
                    "iterations": [],
                    "final_metrics": {},
                    "attack_taxonomy": {},
                    "system_hardness_history": [],
                }

            # Extract metrics from real data only
            self.model_metrics = self.adversarial_results.get("final_metrics", {})

            # Build interception log from data
            self._build_interception_log()

            self.is_loaded = True
        except Exception as e:
            print(f"❌ Data loading error: {e}")
            self.is_loaded = False

    def _load_model(self):
        """Lazily load the trained XGBoost model from disk."""
        if self._model_loaded:
            return

        model_path = self.data_dir / "xgboost_model.pkl"
        if model_path.exists():
            try:
                with open(model_path, "rb") as f:
                    data = pickle.load(f)
                    self._model = data
                self._model_loaded = True
                print(f"📦 Model loaded from {model_path}")
            except Exception as e:
                print(f"⚠️ Failed to load model: {e}")
                self._model_loaded = False
        else:
            print("⚠️ No model file found at", model_path)
            self._model_loaded = False

    def predict_single(self, txn_dict: dict) -> Dict:
        """Run real prediction on a single transaction using the loaded model."""
        self._load_model()

        if not self._model_loaded or self._model is None:
            return {
                "risk_score": 0,
                "is_fraud": False,
                "confidence": 0,
                "model_status": "not_loaded",
                "model_breakdown": {},
                "recommended_action": "ALLOW",
                "attack_pattern_match": None,
            }

        try:
            from blue_team.models.xgboost_baseline import XGBoostBaseline

            xgb = XGBoostBaseline()
            xgb.model = self._model["model"]
            xgb.is_trained = self._model.get("is_trained", True)
            xgb.feature_cols = self._model.get("feature_cols", [])

            # Measure real inference latency
            start_time = time.perf_counter()
            result = xgb.predict_single(txn_dict)
            latency_ms = (time.perf_counter() - start_time) * 1000

            self._inference_latencies.append(latency_ms)
            # Keep only last 100 latencies
            if len(self._inference_latencies) > 100:
                self._inference_latencies = self._inference_latencies[-100:]

            result["model_status"] = "live"
            result["inference_latency_ms"] = round(latency_ms, 2)
            result["model_used"] = "xgboost_ensemble_v1"
            result["attack_pattern_match"] = None

            return result

        except Exception as e:
            return {
                "risk_score": 0,
                "is_fraud": False,
                "confidence": 0,
                "model_status": f"error: {str(e)}",
                "model_breakdown": {},
                "recommended_action": "ALLOW",
                "attack_pattern_match": None,
            }

    def _build_interception_log(self):
        """Build a log of intercepted fraud transactions."""
        if self.transactions_df is None or len(self.transactions_df) == 0:
            return

        df = self.transactions_df
        if "risk_score" in df.columns and "is_fraud" in df.columns:
            caught_fraud = df[(df["is_fraud"] == True) & (df["risk_score"] > 0.5)]
            # Take last 50 interceptions
            for _, row in caught_fraud.tail(50).iterrows():
                self.interceptions.append({
                    "transaction_id": row.get("transaction_id", "N/A"),
                    "timestamp": str(row.get("timestamp", "")),
                    "amount_inr": float(row.get("amount_inr", 0)),
                    "risk_score": round(float(row.get("risk_score", 0)), 4),
                    "fraud_type": row.get("fraud_type", "unknown"),
                    "payment_rail": row.get("payment_rail", ""),
                    "sender_id": row.get("sender_id", ""),
                    "receiver_id": row.get("receiver_id", ""),
                    "recommended_action": "BLOCKED",
                })

    def get_metrics(self) -> Dict:
        """Return model performance metrics. Only from real data — no hardcoded fallbacks."""
        m = self.model_metrics

        # If no real metrics, return zeros clearly labeled
        if not m:
            return {
                "accuracy": 0,
                "precision": 0,
                "recall": 0,
                "f1_score": 0,
                "auc_roc": 0,
                "false_positive_rate": 0,
                "avg_inference_latency_ms": self._get_avg_latency(),
                "total_predictions": 0,
                "adversarial_iteration": 0,
                "data_status": "no_data",
            }

        return {
            "accuracy": m.get("accuracy", 0),
            "precision": m.get("precision", 0),
            "recall": m.get("recall", 0),
            "f1_score": m.get("f1", 0),
            "auc_roc": m.get("auc", 0),
            "false_positive_rate": m.get("fpr", 0),
            "avg_inference_latency_ms": self._get_avg_latency(),
            "total_predictions": m.get("total_transactions", 0),
            "adversarial_iteration": len(self.adversarial_results.get("iterations", [])),
            "data_status": "live",
        }

    def _get_avg_latency(self) -> float:
        """Return real average inference latency, or 0 if not measured."""
        if self._inference_latencies:
            return round(sum(self._inference_latencies) / len(self._inference_latencies), 2)
        return 0

    def get_concept_drift_data(self) -> Dict:
        """Return per-iteration concept drift data for the chart."""
        iterations = self.adversarial_results.get("iterations", [])
        if not iterations:
            return {"iterations": [], "red_team_bypass_rate": [], "blue_team_accuracy": []}

        return {
            "iterations": [i["iteration"] for i in iterations],
            "red_team_bypass_rate": [i.get("bypass_rate", 0) for i in iterations],
            "blue_team_accuracy": [i.get("metrics", {}).get("accuracy", 0) for i in iterations],
            "blue_team_f1": [i.get("metrics", {}).get("f1", 0) for i in iterations],
            "blue_team_auc": [i.get("metrics", {}).get("auc", 0) for i in iterations],
            "system_hardness": [i.get("system_hardness", 0) for i in iterations],
        }

    def get_system_hardness(self) -> Dict:
        """Return current system hardness score."""
        hardness_history = self.adversarial_results.get("system_hardness_history", [])
        if not hardness_history:
            return {"score": 0, "label": "Not Started", "trend": "stable"}

        current = hardness_history[-1]
        prev = hardness_history[-2] if len(hardness_history) > 1 else current
        trend = "improving" if current > prev else "degrading" if current < prev else "stable"

        if current >= 0.9:
            label = "Battle-Hardened"
        elif current >= 0.7:
            label = "Resilient"
        elif current >= 0.5:
            label = "Developing"
        else:
            label = "Vulnerable"

        return {
            "score": round(current * 100, 1),
            "label": label,
            "trend": trend,
            "history": [round(h * 100, 1) for h in hardness_history],
        }

    def get_attack_taxonomy(self) -> Dict:
        """Return per-attack-type statistics."""
        return self.adversarial_results.get("attack_taxonomy", {})

    def get_interceptions(self, limit: int = 20) -> List[Dict]:
        """Return recent fraud interceptions."""
        return self.interceptions[-limit:]

    def get_sample_shap(self) -> List[Dict]:
        """Return sample SHAP explanations."""
        return self.adversarial_results.get("sample_shap_explanations", [])

    def get_transaction_graph_data(self, limit: int = 100) -> Dict:
        """Return transaction network data for the graph visualization."""
        if self.transactions_df is None or len(self.transactions_df) == 0:
            return {"nodes": [], "edges": []}

        df = self.transactions_df.tail(limit * 5)
        nodes_set = set()
        edges = []

        for _, row in df.iterrows():
            sender = str(row.get("sender_id", ""))
            receiver = str(row.get("receiver_id", ""))
            is_fraud = bool(row.get("is_fraud", False))
            caught = bool(row.get("risk_score", 0) > 0.5) if "risk_score" in row else False

            nodes_set.add(sender)
            nodes_set.add(receiver)
            edges.append({
                "source": sender,
                "target": receiver,
                "isFraud": is_fraud,
                "isCaught": is_fraud and caught,
                "amount": float(row.get("amount_inr", 0)),
            })

            if len(edges) >= limit:
                break

        # Classify nodes
        fraud_senders = set(df[df["is_fraud"] == True]["sender_id"].astype(str).unique())
        merchant_ids = set(n for n in nodes_set if n.startswith("MER_"))

        nodes = []
        for n in list(nodes_set)[:200]:  # Cap nodes
            if n in merchant_ids:
                ntype = "merchant"
            elif n in fraud_senders:
                ntype = "mule"
            else:
                ntype = "account"
            nodes.append({"id": n, "type": ntype})

        return {"nodes": nodes, "edges": edges}


# Global singleton
data_service = DataService()
