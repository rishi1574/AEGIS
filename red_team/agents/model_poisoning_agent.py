"""Adversarial Model Poisoning Agent (The Meta-Attack).

Attack Pattern:
  1. Attacker deliberately creates transactions that LOOK fraudulent but are
     actually legitimate — targeting a competitor's merchant ID.
  2. Goal: Train the bank's fraud model to associate the competitor's merchant
     with fraud, causing false positives on real customers.
  3. Uses patterns known to trigger fraud models: unusual hours, high velocity,
     round amounts, new devices.

Characteristics:
  - Transactions are NOT actually stealing money.
  - They are designed to POISON the training data of the Blue Team model.
  - Targeted at specific merchant IDs (competitors).
  - Mix of "suspicious-looking legitimate" patterns:
    - Round amounts at unusual hours
    - Multiple devices in short windows
    - Geographic anomalies
  - is_fraud=True because the INTENT is adversarial (attacking the model itself).
"""
import random
from datetime import datetime, timedelta
from typing import List, Optional
from red_team.agents.base_agent import BaseAgent, Account, Transaction


class ModelPoisoningAgent(BaseAgent):
    def __init__(self, account: Account, active_dates: List[datetime]):
        super().__init__(account)
        self.active_dates = [d.date() for d in active_dates]
        self.target_merchants: List[str] = []  # "Competitor" merchants to poison

    def generate_transactions(self, start: datetime, end: datetime,
                              merchants: List[str], accounts: List[Account]) -> List[Transaction]:
        # Pick 2-3 merchants to target (the "competitors" we want to poison)
        if not self.target_merchants and merchants:
            self.target_merchants = random.sample(merchants, min(3, len(merchants)))

        txns = []
        day = start
        while day < end:
            if day.date() in self.active_dates:
                # Generate 10-20 bait transactions per day
                for _ in range(random.randint(10, 20)):
                    t = self._make_poison_txn(day)
                    if t:
                        self.compute_velocity(t)
                        self.history.append(t)
                        txns.append(t)
            day += timedelta(days=1)
        return txns

    def _make_poison_txn(self, dt: datetime) -> Optional[Transaction]:
        # Deliberately suspicious timing (2-5 AM)
        hour = random.randint(2, 5)
        dt = dt.replace(hour=hour, minute=random.randint(0, 59),
                        second=random.randint(0, 59))

        # Deliberately round amounts (fraud signal)
        amt = random.choice([5000, 10000, 15000, 20000, 25000, 50000])
        amt += random.uniform(-50, 50)  # Slight variation

        # New device each time (fraud signal)
        dev = Account.new_device()

        # Target competitor merchant
        merchant = random.choice(self.target_merchants) if self.target_merchants else "MER_POISON"

        return Transaction(
            transaction_id=Transaction.new_id(), timestamp=dt,
            sender_id=self.account.account_id,
            receiver_id=merchant,
            amount_inr=round(amt, 2),
            payment_rail="CARD_CNP", mcc_code="5732",
            mcc_description="Electronics",
            sender_device_id=dev,
            # Different IP each time (VPN rotation — another fraud signal)
            sender_ip_hash=f"IP_POISON_{random.randint(10000, 99999)}",
            sender_city=random.choice(["Mumbai", "Delhi", "Bangalore"]),
            receiver_city=self.account.city,
            channel="web", is_international=False,
            is_fraud=True, fraud_type="model_poisoning",
            fraud_campaign_id="CAMP_POISON_01",
            sender_account_age_days=self.account.account_age_days,
            sender_avg_monthly_txn_count=20,
            sender_avg_monthly_spend_inr=15000,
            sender_credit_score=self.account.credit_score,
            sender_persona=self.account.persona_type,
            hour_of_day=hour, day_of_week=dt.weekday(),
            is_weekend=dt.weekday() >= 5, is_festival_period=False)
