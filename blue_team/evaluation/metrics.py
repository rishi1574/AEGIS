"""Evaluation metrics for fraud detection models."""
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, roc_auc_score, confusion_matrix)
import numpy as np


def calculate_metrics(y_true, y_pred, y_prob) -> dict:
    """Calculate comprehensive fraud detection metrics.

    Args:
        y_true: Ground truth labels (0/1).
        y_pred: Predicted labels (0/1).
        y_prob: Predicted probabilities.

    Returns:
        Dict with accuracy, precision, recall, f1, auc, fpr, and confusion matrix.
    """
    y_true = np.asarray(y_true).astype(int)
    y_pred = np.asarray(y_pred).astype(int)
    y_prob = np.asarray(y_prob).astype(float)

    # Handle edge cases
    if len(y_true) == 0 or len(np.unique(y_true)) < 2:
        return {
            "accuracy": 0.0, "precision": 0.0, "recall": 0.0,
            "f1": 0.0, "auc": 0.5, "fpr": 0.0,
        }

    try:
        auc = roc_auc_score(y_true, y_prob)
    except ValueError:
        auc = 0.5

    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    fpr = fp / max(fp + tn, 1)

    return {
        "accuracy": round(accuracy_score(y_true, y_pred), 4),
        "precision": round(precision_score(y_true, y_pred, zero_division=0), 4),
        "recall": round(recall_score(y_true, y_pred, zero_division=0), 4),
        "f1": round(f1_score(y_true, y_pred, zero_division=0), 4),
        "auc": round(auc, 4),
        "fpr": round(fpr, 4),
        "true_positives": int(tp),
        "false_positives": int(fp),
        "true_negatives": int(tn),
        "false_negatives": int(fn),
    }
