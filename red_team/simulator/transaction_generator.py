"""Orchestrates all agents to generate the full dataset."""
import random, pandas as pd
from datetime import datetime, timedelta
from typing import List
from pathlib import Path
from red_team.agents.base_agent import Account, Transaction
from red_team.agents.legitimate_personas import create_agent
from red_team.agents.synthetic_id_agent import SyntheticIDAgent
from red_team.agents.vishing_agent import VishingAgent
from red_team.agents.digital_arrest_agent import DigitalArrestAgent
from red_team.agents.txn_fuzzing_agent import TxnFuzzingAgent
from red_team.agents.agentic_hijack_agent import AgenticHijackAgent
from red_team.simulator.india_specific_config import PERSONAS

class TransactionGenerator:
    def __init__(self, num_accounts=10000, num_merchants=500, fraud_ratio=0.05):
        self.num_accounts = num_accounts
        self.num_merchants = num_merchants
        self.fraud_ratio = fraud_ratio
        self.accounts: List[Account] = []
        self.merchants: List[str] = []
        self.agents = []
        self.all_txns: List[Transaction] = []

    def setup(self):
        print(f"Setting up {self.num_accounts} accounts...")
        self.merchants = [f"MER_{i:05d}" for i in range(self.num_merchants)]
        weights = {"college_student":.20,"it_professional":.25,"homemaker":.15,
                   "retired_officer":.10,"small_business_owner":.20,"nri":.10}
        for i in range(self.num_accounts):
            pt = random.choices(list(weights.keys()), list(weights.values()))[0]
            agent = create_agent(pt)
            self.accounts.append(agent.account)
            
            # Decide if this agent turns malicious
            if random.random() < self.fraud_ratio:
                fraud_type = random.choice(["synthetic", "vishing", "digital_arrest", "fuzzing", "hijack"])
                attack_dates = [datetime(2026, 6, 1) + timedelta(days=random.randint(10, 25))]
                if fraud_type == "synthetic":
                    self.agents.append(SyntheticIDAgent(agent.account, attack_dates[0]))
                elif fraud_type == "vishing":
                    self.agents.append(VishingAgent(agent.account, attack_dates))
                elif fraud_type == "digital_arrest":
                    self.agents.append(DigitalArrestAgent(agent.account, attack_dates))
                elif fraud_type == "fuzzing":
                    self.agents.append(TxnFuzzingAgent(agent.account, attack_dates))
                elif fraud_type == "hijack":
                    self.agents.append(AgenticHijackAgent(agent.account, attack_dates))
            else:
                self.agents.append(agent)
                
            if (i+1) % 2000 == 0: print(f"  {i+1}/{self.num_accounts}")
        print(f"✅ {len(self.accounts)} accounts, {len(self.merchants)} merchants")

    def generate(self, start: datetime, end: datetime) -> pd.DataFrame:
        print(f"Generating txns {start.date()} to {end.date()}...")
        all_t = []
        for i, ag in enumerate(self.agents):
            txns = ag.generate_transactions(start, end, self.merchants, self.accounts)
            all_t.extend(txns)
            if (i+1) % 1000 == 0: print(f"  {i+1}/{len(self.agents)} agents, {len(all_t)} txns")
        self.all_txns = all_t
        df = pd.DataFrame([t.to_dict() for t in all_t]).sort_values("timestamp").reset_index(drop=True)
        print(f"✅ {len(df)} transactions generated")
        print(f"  Rails: {df.payment_rail.value_counts().to_dict()}")
        print(f"  Fraud: {df.is_fraud.mean():.4%}")
        return df

    def save(self, path, df):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
        print(f"💾 Saved to {path}")

if __name__ == "__main__":
    g = TransactionGenerator(1000, 100)
    g.setup()
    df = g.generate(datetime(2026,6,1), datetime(2026,6,30))
    g.save("data/generated/test_txns.csv", df)
