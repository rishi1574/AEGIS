import time
import pandas as pd
from datetime import datetime, timedelta
from red_team.simulator.transaction_generator import TransactionGenerator
from blue_team.models.xgboost_baseline import XGBoostBaseline
from blue_team.evaluation.metrics import calculate_metrics

def run_loop(iterations=3):
    print("Initializing Simulation...")
    # 1. Generate Base Data
    generator = TransactionGenerator(num_accounts=1000, num_merchants=50, fraud_ratio=0.05)
    generator.setup()
    
    start_date = datetime(2026, 6, 1)
    print("Generating base dataset...")
    base_df = generator.generate(start_date, start_date + timedelta(days=15))
    base_df.to_csv("data/generated/train_txns.csv", index=False)
    
    # 2. Train Initial Blue Team
    blue_team = XGBoostBaseline()
    print("Training Blue Team Baseline...")
    blue_team.train(base_df)
    
    for i in range(iterations):
        print(f"\n--- Iteration {i+1} ---")
        print("Red Team attacking... (generating new mutated data)")
        # Advance time
        start_date = start_date + timedelta(days=15)
        attack_df = generator.generate(start_date, start_date + timedelta(days=15))
        
        # 3. Evaluate Attack
        if len(attack_df) > 0:
            attack_df['risk_score'] = blue_team.predict(attack_df)
            attack_df['pred_fraud'] = (attack_df['risk_score'] > 0.5).astype(int)
            
            fraud_only = attack_df[attack_df['is_fraud'] == True]
            if len(fraud_only) > 0:
                bypass_rate = (fraud_only['pred_fraud'] == 0).mean()
                print(f"Bypass Rate: {bypass_rate*100:.2f}%")
            
            metrics = calculate_metrics(attack_df['is_fraud'].astype(int), attack_df['pred_fraud'], attack_df['risk_score'])
            print(f"Blue Team AUC-ROC: {metrics['auc']:.4f}")
            
        print("Blue Team adapting... (Retraining on new zero-days)")
        blue_team.train(pd.concat([base_df, attack_df]))
        base_df = pd.concat([base_df, attack_df])
        
    print("\nAdversarial Loop Finished.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=3)
    args = parser.parse_args()
    run_loop(args.iterations)
