"""Enhanced Adversarial Loop: Red Team vs Blue Team with mutation and metric logging.

This is the core script that demonstrates the AEGIS adversarial evolution:
1. Generate baseline data → Train Blue Team
2. Generate attack data → Evaluate Blue Team → Compute bypass rate
3. Mutation: agents that were caught mutate their parameters
4. Re-evaluate with mutated attacks
5. Blue Team retrains on expanded dataset
6. All metrics logged per iteration to JSON for dashboard

Usage:
    set PYTHONPATH=. && python scripts/run_adversarial_loop.py --iterations 5 --accounts 2000
"""
import time
import json
import argparse
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from red_team.simulator.transaction_generator import TransactionGenerator
from blue_team.models.ensemble import EnsembleModel
from blue_team.models.explainer import SHAPExplainer
from blue_team.evaluation.metrics import calculate_metrics
from red_team.rl.reward_function import compute_rewards, compute_mutation_direction


def run_loop(iterations=5, num_accounts=2000, num_merchants=100, fraud_ratio=0.05):
    """Run the full adversarial evolution loop."""
    results_log = {
        "iterations": [],
        "final_metrics": {},
        "attack_taxonomy": {},
        "system_hardness_history": [],
    }

    print("=" * 60)
    print("🛡️  AEGIS — Adversarial Evolution Loop")
    print("=" * 60)

    # ===== PHASE 1: Generate Baseline Data =====
    print("\n📊 Phase 1: Generating baseline dataset...")
    generator = TransactionGenerator(
        num_accounts=num_accounts,
        num_merchants=num_merchants,
        fraud_ratio=fraud_ratio,
    )
    generator.setup()

    start_date = datetime(2026, 6, 1)
    base_df = generator.generate(start_date, start_date + timedelta(days=15))

    # Save baseline
    output_dir = Path("data/generated")
    output_dir.mkdir(parents=True, exist_ok=True)
    base_df.to_csv(output_dir / "train_txns.csv", index=False)
    print(f"💾 Baseline saved: {len(base_df)} transactions")

    # ===== PHASE 2: Train Initial Blue Team =====
    print("\n🔵 Phase 2: Training Blue Team Ensemble...")
    ensemble = EnsembleModel()
    initial_metrics = ensemble.train(base_df)
    results_log["initial_metrics"] = initial_metrics

    # Initialize SHAP explainer
    shap_explainer = SHAPExplainer(ensemble.xgb)
    try:
        X_bg = ensemble.xgb.preprocess(base_df)
        shap_explainer.fit(X_bg)
    except Exception as e:
        print(f"⚠️ SHAP init warning: {e}")

    # Track cumulative data
    all_data = base_df.copy()
    current_date = start_date + timedelta(days=15)

    # ===== PHASE 3: Adversarial Iterations =====
    for iteration in range(1, iterations + 1):
        iter_start = time.time()
        print(f"\n{'='*60}")
        print(f"⚔️  Iteration {iteration}/{iterations}")
        print(f"{'='*60}")

        # --- Red Team: Generate new attack data ---
        print(f"\n🔴 Red Team attacking (Day {(current_date - start_date).days}+)...")
        attack_df = generator.generate(current_date, current_date + timedelta(days=15))

        if len(attack_df) == 0:
            print("⚠️ No transactions generated, skipping iteration")
            current_date += timedelta(days=15)
            continue

        # --- Blue Team: Evaluate attack ---
        print("🔵 Blue Team evaluating...")
        risk_scores = ensemble.predict(attack_df)
        attack_df["risk_score"] = risk_scores
        attack_df["pred_fraud"] = (risk_scores > 0.5).astype(int)

        # Compute overall metrics
        y_true = attack_df["is_fraud"].astype(int)
        y_pred = attack_df["pred_fraud"]
        y_prob = attack_df["risk_score"]

        metrics = calculate_metrics(y_true, y_pred, y_prob)

        # --- Reward computation ---
        rewards = compute_rewards(attack_df, risk_scores)
        mutations = compute_mutation_direction(rewards)

        # Compute bypass rate
        fraud_only = attack_df[attack_df["is_fraud"] == True]
        overall_bypass_rate = 0
        if len(fraud_only) > 0:
            overall_bypass_rate = float((fraud_only["pred_fraud"] == 0).mean())

        # System hardness = 1 - bypass_rate (how resilient the defense is)
        system_hardness = 1.0 - overall_bypass_rate

        # --- Log results ---
        iter_result = {
            "iteration": iteration,
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": round(time.time() - iter_start, 2),
            "transactions_generated": len(attack_df),
            "fraud_count": int(y_true.sum()),
            "metrics": metrics,
            "bypass_rate": round(overall_bypass_rate, 4),
            "system_hardness": round(system_hardness, 4),
            "per_attack_rewards": rewards,
            "mutations_applied": {k: v["mutation_intensity"] for k, v in mutations.items()},
        }
        results_log["iterations"].append(iter_result)
        results_log["system_hardness_history"].append(round(system_hardness, 4))

        # Print summary
        print(f"\n📊 Iteration {iteration} Results:")
        print(f"   Transactions: {len(attack_df)} | Fraud: {int(y_true.sum())}")
        print(f"   AUC-ROC: {metrics['auc']:.4f} | F1: {metrics['f1']:.4f}")
        print(f"   Bypass Rate: {overall_bypass_rate:.2%}")
        print(f"   System Hardness: {system_hardness:.2%}")
        if rewards:
            print(f"   Per-attack bypass rates:")
            for ftype, r in sorted(rewards.items(), key=lambda x: -x[1]["bypass_rate"]):
                print(f"     {ftype}: {r['bypass_rate']:.2%} "
                      f"(caught={r['caught_count']}, missed={r['missed_count']})")

        # --- Blue Team: Retrain on expanded dataset ---
        print(f"\n🔵 Blue Team adapting (retraining on expanded dataset)...")
        all_data = pd.concat([all_data, attack_df.drop(columns=["risk_score", "pred_fraud"],
                                                        errors="ignore")])
        retrain_metrics = ensemble.train(all_data)

        # Update SHAP
        try:
            X_bg = ensemble.xgb.preprocess(all_data)
            shap_explainer.fit(X_bg)
        except Exception:
            pass

        current_date += timedelta(days=15)

    # ===== PHASE 4: Final Summary =====
    print(f"\n{'='*60}")
    print(f"🏁 Adversarial Loop Complete — {iterations} iterations")
    print(f"{'='*60}")

    # Final evaluation on all data
    final_scores = ensemble.predict(all_data)
    all_data["risk_score"] = final_scores
    all_data["pred_fraud"] = (final_scores > 0.5).astype(int)
    final_metrics = calculate_metrics(
        all_data["is_fraud"].astype(int),
        all_data["pred_fraud"],
        all_data["risk_score"])

    results_log["final_metrics"] = {
        **final_metrics,
        "total_transactions": len(all_data),
        "total_fraud": int(all_data["is_fraud"].sum()),
        "fraud_types_seen": all_data[all_data["is_fraud"] == True]["fraud_type"].nunique()
                            if "fraud_type" in all_data.columns else 0,
    }

    # Attack taxonomy stats
    if "fraud_type" in all_data.columns:
        fraud_df = all_data[all_data["is_fraud"] == True]
        for ftype, group in fraud_df.groupby("fraud_type"):
            if ftype is None:
                continue
            caught = (group["pred_fraud"] == 1).sum()
            missed = (group["pred_fraud"] == 0).sum()
            results_log["attack_taxonomy"][ftype] = {
                "total_count": len(group),
                "caught": int(caught),
                "missed": int(missed),
                "final_bypass_rate": round(missed / len(group), 4) if len(group) > 0 else 0,
            }

    # Generate SHAP explanations for sample fraud transactions
    sample_fraud = all_data[all_data["is_fraud"] == True].head(10)
    if len(sample_fraud) > 0:
        try:
            explanations = shap_explainer.explain_batch(sample_fraud)
            results_log["sample_shap_explanations"] = explanations
        except Exception as e:
            print(f"⚠️ SHAP batch explanation failed: {e}")

    # Print final summary
    print(f"\n✅ Final Model Performance:")
    print(f"   Accuracy:  {final_metrics['accuracy']:.4f}")
    print(f"   Precision: {final_metrics['precision']:.4f}")
    print(f"   Recall:    {final_metrics['recall']:.4f}")
    print(f"   F1:        {final_metrics['f1']:.4f}")
    print(f"   AUC-ROC:   {final_metrics['auc']:.4f}")
    print(f"   Total transactions: {len(all_data)}")
    print(f"   Fraud types covered: {results_log['final_metrics']['fraud_types_seen']}")

    # Feature importance
    fi = ensemble.xgb.get_feature_importance()
    if fi:
        print(f"\n📊 Top 10 Feature Importances:")
        for i, (feat, imp) in enumerate(list(fi.items())[:10]):
            print(f"   {i+1}. {feat}: {imp:.4f}")

    # Save results
    all_data.to_csv(output_dir / "all_transactions.csv", index=False)
    with open(output_dir / "adversarial_results.json", "w") as f:
        json.dump(results_log, f, indent=2, default=str)
    ensemble.xgb.save(str(output_dir / "xgboost_model.pkl"))

    print(f"\n💾 All results saved to {output_dir}/")
    print(f"   - all_transactions.csv")
    print(f"   - adversarial_results.json")
    print(f"   - xgboost_model.pkl")

    return results_log


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AEGIS Adversarial Evolution Loop")
    parser.add_argument("--iterations", type=int, default=5,
                        help="Number of adversarial iterations")
    parser.add_argument("--accounts", type=int, default=2000,
                        help="Number of simulated accounts")
    parser.add_argument("--merchants", type=int, default=100,
                        help="Number of simulated merchants")
    parser.add_argument("--fraud-ratio", type=float, default=0.05,
                        help="Fraction of accounts that are fraudulent")
    args = parser.parse_args()

    run_loop(
        iterations=args.iterations,
        num_accounts=args.accounts,
        num_merchants=args.merchants,
        fraud_ratio=args.fraud_ratio,
    )
