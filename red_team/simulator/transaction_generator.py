"""Orchestrates all agents to generate the full dataset."""
import random, pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict
from pathlib import Path
from red_team.agents.base_agent import Account, Transaction
from red_team.agents.legitimate_personas import create_agent
from red_team.agents.synthetic_id_agent import SyntheticIDAgent
from red_team.agents.vishing_agent import VishingAgent
from red_team.agents.digital_arrest_agent import DigitalArrestAgent
from red_team.agents.txn_fuzzing_agent import TxnFuzzingAgent
from red_team.agents.agentic_hijack_agent import AgenticHijackAgent
from red_team.agents.deepfake_ato_agent import DeepfakeATOAgent
from red_team.agents.merchant_collusion_agent import MerchantCollusionAgent
from red_team.agents.api_exploit_agent import APIExploitAgent
from red_team.agents.pig_butchering_agent import PigButcheringAgent
from red_team.agents.model_poisoning_agent import ModelPoisoningAgent
from red_team.agents.supply_chain_bec_agent import SupplyChainBECAgent
from red_team.agents.adversarial_document_agent import AdversarialDocumentAgent
from red_team.simulator.india_specific_config import PERSONAS

# All 12 attack types with their weights (probability of selection)
FRAUD_TYPES = {
    "synthetic_id":       {"weight": 0.12, "class": SyntheticIDAgent},
    "deepfake_ato":       {"weight": 0.10, "class": DeepfakeATOAgent},
    "adversarial_doc":    {"weight": 0.06, "class": AdversarialDocumentAgent},
    "txn_fuzzing":        {"weight": 0.12, "class": TxnFuzzingAgent},
    "api_exploit":        {"weight": 0.08, "class": APIExploitAgent},
    "merchant_collusion": {"weight": 0.10, "class": MerchantCollusionAgent},
    "vishing":            {"weight": 0.12, "class": VishingAgent},
    "pig_butchering":     {"weight": 0.10, "class": PigButcheringAgent},
    "digital_arrest":     {"weight": 0.08, "class": DigitalArrestAgent},
    "agentic_hijack":     {"weight": 0.06, "class": AgenticHijackAgent},
    "model_poisoning":    {"weight": 0.04, "class": ModelPoisoningAgent},
    "supply_chain_bec":   {"weight": 0.02, "class": SupplyChainBECAgent},
}


class TransactionGenerator:
    def __init__(self, num_accounts=10000, num_merchants=500, fraud_ratio=0.05,
                 mutation_params: Dict = None):
        self.num_accounts = num_accounts
        self.num_merchants = num_merchants
        self.fraud_ratio = fraud_ratio
        self.mutation_params = mutation_params or {}
        self.accounts: List[Account] = []
        self.merchants: List[str] = []
        self.agents = []
        self.all_txns: List[Transaction] = []
        self.fraud_type_counts: Dict[str, int] = {}

    def setup(self):
        print(f"Setting up {self.num_accounts} accounts...")
        self.merchants = [f"MER_{i:05d}" for i in range(self.num_merchants)]
        weights = {"college_student": .20, "it_professional": .25, "homemaker": .15,
                   "retired_officer": .10, "small_business_owner": .20, "nri": .10}

        fraud_type_names = list(FRAUD_TYPES.keys())
        fraud_type_weights = [FRAUD_TYPES[k]["weight"] for k in fraud_type_names]

        for i in range(self.num_accounts):
            pt = random.choices(list(weights.keys()), list(weights.values()))[0]
            agent = create_agent(pt)
            self.accounts.append(agent.account)

            if random.random() < self.fraud_ratio:
                fraud_type = random.choices(fraud_type_names, fraud_type_weights)[0]
                self.fraud_type_counts[fraud_type] = self.fraud_type_counts.get(fraud_type, 0) + 1

                # Generate attack dates within the simulation window
                attack_dates = [datetime(2026, 6, 1) + timedelta(days=random.randint(10, 25))]

                fraud_agent = self._create_fraud_agent(
                    fraud_type, agent.account, attack_dates)
                self.agents.append(fraud_agent)
            else:
                self.agents.append(agent)

            if (i + 1) % 2000 == 0:
                print(f"  {i + 1}/{self.num_accounts}")

        print(f"✅ {len(self.accounts)} accounts, {len(self.merchants)} merchants")
        print(f"   Fraud agent distribution: {self.fraud_type_counts}")

    def _create_fraud_agent(self, fraud_type: str, account: Account,
                             attack_dates: List[datetime]):
        """Create a fraud agent, applying any mutation params."""
        if fraud_type == "synthetic_id":
            return SyntheticIDAgent(account, attack_dates[0])
        elif fraud_type == "deepfake_ato":
            return DeepfakeATOAgent(account, attack_dates)
        elif fraud_type == "adversarial_doc":
            return AdversarialDocumentAgent(account, attack_dates)
        elif fraud_type == "txn_fuzzing":
            return TxnFuzzingAgent(account, attack_dates)
        elif fraud_type == "api_exploit":
            return APIExploitAgent(account, attack_dates)
        elif fraud_type == "merchant_collusion":
            return MerchantCollusionAgent(account, attack_dates)
        elif fraud_type == "vishing":
            return VishingAgent(account, attack_dates)
        elif fraud_type == "pig_butchering":
            return PigButcheringAgent(account, attack_dates[0])
        elif fraud_type == "digital_arrest":
            return DigitalArrestAgent(account, attack_dates)
        elif fraud_type == "agentic_hijack":
            return AgenticHijackAgent(account, attack_dates)
        elif fraud_type == "model_poisoning":
            return ModelPoisoningAgent(account, attack_dates)
        elif fraud_type == "supply_chain_bec":
            return SupplyChainBECAgent(account, attack_dates)
        else:
            # Fallback to legitimate if unknown type
            from red_team.agents.legitimate_personas import create_agent as _ca
            return _ca(account.persona_type)

    def generate(self, start: datetime, end: datetime) -> pd.DataFrame:
        print(f"Generating txns {start.date()} to {end.date()}...")
        all_t = []
        for i, ag in enumerate(self.agents):
            txns = ag.generate_transactions(start, end, self.merchants, self.accounts)
            all_t.extend(txns)
            if (i + 1) % 1000 == 0:
                print(f"  {i + 1}/{len(self.agents)} agents, {len(all_t)} txns")
        self.all_txns = all_t
        df = pd.DataFrame([t.to_dict() for t in all_t]).sort_values("timestamp").reset_index(drop=True)
        print(f"✅ {len(df)} transactions generated")
        if len(df) > 0:
            print(f"  Rails: {df.payment_rail.value_counts().to_dict()}")
            print(f"  Fraud: {df.is_fraud.mean():.4%}")
            if 'fraud_type' in df.columns:
                fraud_df = df[df.is_fraud == True]
                if len(fraud_df) > 0:
                    print(f"  Fraud Types: {fraud_df.fraud_type.value_counts().to_dict()}")
        return df

    def save(self, path, df):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
        print(f"💾 Saved to {path}")


if __name__ == "__main__":
    g = TransactionGenerator(1000, 100)
    g.setup()
    df = g.generate(datetime(2026, 6, 1), datetime(2026, 6, 30))
    g.save("data/generated/test_txns.csv", df)
