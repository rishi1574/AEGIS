"""Training pipeline. Usage: python -m blue_team.training.train_pipeline --data data/generated/transactions_full.csv"""
import argparse, pandas as pd
from blue_team.models.xgboost_baseline import XGBoostBaseline, FEATURE_COLS
from blue_team.models.ensemble import EnsembleModel
from blue_team.models.explainer import SHAPExplainer


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", required=True)
    a = p.parse_args()
    df = pd.read_csv(a.data)
    print(f"Loaded {len(df)} rows, fraud={df.is_fraud.mean():.4%}")

    # Train ensemble (XGBoost + Graph + Temporal)
    ensemble = EnsembleModel()
    metrics = ensemble.train(df)
    print(f"Ensemble: {metrics}")

    # Save model
    ensemble.xgb.save()
    print("Training complete.")


if __name__ == "__main__":
    main()
