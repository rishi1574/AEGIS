"""Reward Function for the Adversarial Evolution Loop.

Computes per-attack-type rewards based on Blue Team detection performance.
Positive reward = attack bypassed detection (Red Team wins).
Negative reward = attack was caught (Blue Team wins).
"""
import pandas as pd
import numpy as np
from typing import Dict


def compute_rewards(attack_df: pd.DataFrame, risk_scores: np.ndarray,
                    threshold: float = 0.5) -> Dict[str, Dict]:
    """Compute per-attack-type reward signals.

    Args:
        attack_df: DataFrame with 'is_fraud' and 'fraud_type' columns.
        risk_scores: Model-predicted fraud probabilities.
        threshold: Classification threshold.

    Returns:
        Dict mapping fraud_type -> {reward, bypass_rate, caught_count, missed_count}
    """
    results = {}

    fraud_mask = attack_df["is_fraud"] == True
    fraud_df = attack_df[fraud_mask].copy()
    fraud_scores = risk_scores[fraud_mask.values]

    if len(fraud_df) == 0:
        return results

    fraud_df = fraud_df.copy()
    fraud_df["risk_score"] = fraud_scores
    fraud_df["caught"] = fraud_scores > threshold
    fraud_df["bypassed"] = fraud_scores <= threshold

    for fraud_type, group in fraud_df.groupby("fraud_type"):
        if fraud_type is None:
            continue

        caught = int(group["caught"].sum())
        missed = int(group["bypassed"].sum())
        total = len(group)
        bypass_rate = missed / total if total > 0 else 0

        # Reward: positive for bypasses, negative for catches
        reward = (missed - caught) / total if total > 0 else 0

        results[fraud_type] = {
            "reward": round(reward, 4),
            "bypass_rate": round(bypass_rate, 4),
            "caught_count": caught,
            "missed_count": missed,
            "total_count": total,
            "avg_risk_score": round(float(group["risk_score"].mean()), 4),
        }

    return results


def compute_mutation_direction(rewards: Dict[str, Dict]) -> Dict[str, Dict]:
    """Based on rewards, suggest mutation directions for each attack type.

    If an attack was mostly caught → mutate MORE aggressively to evade.
    If an attack was mostly missed → mutate LESS (it's already working).

    Returns:
        Dict mapping fraud_type -> mutation parameters.
    """
    mutations = {}

    for fraud_type, r in rewards.items():
        bypass_rate = r["bypass_rate"]

        if bypass_rate < 0.3:
            # Attack is being caught easily → aggressive mutation
            mutations[fraud_type] = {
                "amount_shift": (-0.20, 0.20),     # ±20% amount variation
                "timing_shift": (-3, 3),             # ±3 hours
                "add_warmup_txns": True,             # Add legit txns before attack
                "rotate_mcc": True,                   # Change merchant category
                "device_strategy": "reuse_victim",    # Use victim's device
                "mutation_intensity": "aggressive",
            }
        elif bypass_rate < 0.6:
            # Moderate detection → moderate mutation
            mutations[fraud_type] = {
                "amount_shift": (-0.10, 0.10),
                "timing_shift": (-1, 1),
                "add_warmup_txns": random_bool(0.5),
                "rotate_mcc": random_bool(0.3),
                "device_strategy": "mixed",
                "mutation_intensity": "moderate",
            }
        else:
            # Attack is mostly evading → minimal mutation (don't fix what works)
            mutations[fraud_type] = {
                "amount_shift": (-0.05, 0.05),
                "timing_shift": (0, 0),
                "add_warmup_txns": False,
                "rotate_mcc": False,
                "device_strategy": "keep",
                "mutation_intensity": "minimal",
            }

    return mutations


def random_bool(probability: float) -> bool:
    import random
    return random.random() < probability
