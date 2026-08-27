"""Temporal Sequence Anomaly Detector.

For each user, builds a behavioral profile from their transaction history
and scores each new transaction based on deviation from their expected patterns.

Uses Isolation Forest on per-user sequence features for anomaly detection.
This is a lightweight alternative to a full Transformer model that runs on
any machine without GPU dependencies.
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from collections import defaultdict
from typing import Dict, Optional


class TemporalAnomalyDetector:
    """Detects behavioral anomalies by analyzing user transaction sequences."""

    def __init__(self, window_size: int = 50):
        self.window_size = window_size
        self.user_profiles: Dict[str, Dict] = {}
        self.isolation_forest = IsolationForest(
            n_estimators=100,
            contamination=0.05,
            random_state=42,
        )
        self.is_fitted = False

    def fit(self, df: pd.DataFrame):
        """Build per-user behavioral profiles from historical data."""
        print("Building temporal profiles...")

        # Sort by timestamp
        df_sorted = df.sort_values("timestamp").copy()

        # Group by sender and compute profile statistics
        for sender_id, group in df_sorted.groupby("sender_id"):
            if len(group) < 3:
                continue

            amounts = group["amount_inr"].values
            hours = group["hour_of_day"].values

            # Compute inter-transaction intervals
            timestamps = pd.to_datetime(group["timestamp"], format="ISO8601")
            intervals = timestamps.diff().dt.total_seconds().dropna().values
            intervals = intervals[intervals > 0]  # Remove zero/negative

            self.user_profiles[sender_id] = {
                "mean_amount": float(np.mean(amounts)),
                "std_amount": float(max(np.std(amounts), 1.0)),
                "median_amount": float(np.median(amounts)),
                "max_amount": float(np.max(amounts)),
                "mean_hour": float(np.mean(hours)),
                "std_hour": float(max(np.std(hours), 1.0)),
                "mean_interval": float(np.mean(intervals)) if len(intervals) > 0 else 86400,
                "std_interval": float(max(np.std(intervals), 1.0)) if len(intervals) > 0 else 86400,
                "common_rail": group["payment_rail"].mode().iloc[0] if len(group) > 0 else "UPI_P2M",
                "txn_count": len(group),
                "unique_receivers": group["receiver_id"].nunique(),
            }

        # Train Isolation Forest on sequence features
        seq_features = self._compute_sequence_features(df_sorted)
        if len(seq_features) > 10:
            self.isolation_forest.fit(seq_features)

        self.is_fitted = True
        print(f"  Built profiles for {len(self.user_profiles)} users")

    def _compute_sequence_features(self, df: pd.DataFrame) -> np.ndarray:
        """Compute per-transaction sequence features for Isolation Forest."""
        features = []
        for _, row in df.iterrows():
            sender_id = row.get("sender_id", "")
            profile = self.user_profiles.get(sender_id, None)

            if profile is None:
                features.append([0, 0, 0, 0, 0, 0])
                continue

            amount = float(row.get("amount_inr", 0))
            hour = float(row.get("hour_of_day", 12))
            time_since = float(row.get("time_since_last_txn_seconds", 86400))

            # Z-scores relative to user's own profile
            amount_z = (amount - profile["mean_amount"]) / profile["std_amount"]
            hour_z = (hour - profile["mean_hour"]) / profile["std_hour"]
            interval_z = ((time_since - profile["mean_interval"]) /
                          profile["std_interval"])

            # Amount ratio to user's max
            max_ratio = amount / max(profile["max_amount"], 1)

            # Is this a new receiver for this user?
            is_new = float(row.get("is_new_receiver", 0))

            # Transaction velocity anomaly
            velocity = float(row.get("txn_count_last_1h", 0))
            expected_hourly = profile["txn_count"] / (30 * 24)  # avg txns per hour
            velocity_anomaly = velocity / max(expected_hourly, 0.01)

            features.append([
                amount_z, hour_z, interval_z,
                max_ratio, is_new, velocity_anomaly
            ])

        return np.array(features)

    def score(self, df: pd.DataFrame) -> np.ndarray:
        """Return anomaly score (0-1, higher = more anomalous) for each transaction."""
        if not self.is_fitted or len(self.user_profiles) == 0:
            return np.full(len(df), 0.1)

        seq_features = self._compute_sequence_features(df)

        # Isolation Forest decision_function returns negative for anomalies
        try:
            raw_scores = self.isolation_forest.decision_function(seq_features)
            # Normalize to 0-1 (invert: more negative = more anomalous = higher score)
            min_s, max_s = raw_scores.min(), raw_scores.max()
            if max_s > min_s:
                normalized = 1.0 - (raw_scores - min_s) / (max_s - min_s)
            else:
                normalized = np.full(len(raw_scores), 0.1)

            # Also compute user-profile-based anomaly
            profile_scores = self._profile_anomaly_scores(df)

            # Combine: weighted average
            combined = 0.6 * normalized + 0.4 * profile_scores
            return np.clip(combined, 0.0, 1.0)
        except Exception:
            return np.full(len(df), 0.1)

    def _profile_anomaly_scores(self, df: pd.DataFrame) -> np.ndarray:
        """Compute anomaly scores based on deviation from user profiles."""
        scores = []
        for _, row in df.iterrows():
            sender_id = row.get("sender_id", "")
            profile = self.user_profiles.get(sender_id, None)

            if profile is None:
                scores.append(0.3)  # Unknown user = moderate anomaly
                continue

            amount = float(row.get("amount_inr", 0))
            hour = float(row.get("hour_of_day", 12))

            # Amount deviation
            amount_z = abs(amount - profile["mean_amount"]) / profile["std_amount"]
            amount_score = min(1.0, amount_z / 5.0)

            # Hour deviation
            hour_z = abs(hour - profile["mean_hour"]) / profile["std_hour"]
            hour_score = min(1.0, hour_z / 4.0)

            # New receiver penalty
            new_receiver_score = 0.3 if row.get("is_new_receiver", False) else 0.0

            # Velocity penalty
            velocity = float(row.get("txn_count_last_1h", 0))
            expected = profile["txn_count"] / (30 * 24)
            velocity_score = min(1.0, velocity / max(expected * 5, 1))

            # Weighted combination
            score = (0.35 * amount_score + 0.2 * hour_score +
                     0.25 * new_receiver_score + 0.2 * velocity_score)
            scores.append(min(1.0, score))

        return np.array(scores)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add temporal anomaly score as a column."""
        df = df.copy()
        df["temporal_anomaly_score"] = self.score(df)
        return df
