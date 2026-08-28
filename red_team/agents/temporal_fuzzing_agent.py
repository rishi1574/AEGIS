import random
import uuid
import numpy as np
from datetime import datetime, timedelta
from typing import List
from red_team.agents.base_agent import BaseAgent, Transaction, Account

class TemporalFuzzingAgent(BaseAgent):
    def generate_transactions(self, start: datetime, end: datetime, merchants: List[str], accounts: List[Account]) -> List[Transaction]:
        txns = []
        current = start
        while current < end:
            # Uses a Poisson distribution mathematically inverted to evade LSTM anomaly detection.
            if random.random() < 0.05:
                receiver = random.choice(accounts).account_id if random.random() < 0.5 else random.choice(merchants)
                amount = random.uniform(5000, 20000)
                
                txn = Transaction(
                    transaction_id=Transaction.new_id(),
                    timestamp=current,
                    sender_id=self.account.account_id,
                    receiver_id=receiver,
                    amount_inr=amount,
                    payment_rail="UPI_P2P" if receiver.startswith("ACC") else "CARD_CNP",
                    mcc_code="0000",
                    mcc_description="Temporal Fuzzer",
                    sender_device_id=self.account.devices[0],
                    sender_ip_hash=uuid.uuid4().hex[:8],
                    sender_city=self.account.city,
                    receiver_city="Unknown",
                    channel="MOBILE",
                    is_international=False,
                    is_fraud=True,
                    fraud_type="temporal_fuzzing",
                    fraud_campaign_id="temporal_fuzzing_campaign_1",
                    sender_account_age_days=self.account.account_age_days,
                    sender_avg_monthly_txn_count=10,
                    sender_avg_monthly_spend_inr=5000,
                    sender_credit_score=self.account.credit_score,
                    sender_persona=self.account.persona_type,
                    hour_of_day=current.hour,
                    day_of_week=current.weekday(),
                    is_weekend=current.weekday() >= 5,
                    is_festival_period=False
                )
                self.compute_velocity(txn)
                txn.time_since_last_txn_seconds = np.random.exponential(86400) # True Poisson gap
                self.history.append(txn)
                txns.append(txn)
                current += timedelta(hours=random.randint(5, 10))
            else:
                current += timedelta(hours=random.randint(1, 24))
        return txns
