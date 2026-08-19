"""Training pipeline. Usage: python -m blue_team.training.train_pipeline --data data/generated/transactions_full.csv"""
import argparse, pandas as pd
from blue_team.models.xgboost_baseline import XGBDetector, FEATURES, CAT_COLS
from blue_team.models.federated import FederatedSim

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", required=True)
    a = p.parse_args()
    df = pd.read_csv(a.data)
    print(f"Loaded {len(df)} rows, fraud={df.is_fraud.mean():.4%}")

    det = XGBDetector()
    m = det.train(df)
    det.save()
    print(f"XGBoost: {m}")

    fed = FederatedSim()
    fr = fed.run(df, FEATURES)
    print(f"Federated: {fr}")

if __name__=="__main__": main()
