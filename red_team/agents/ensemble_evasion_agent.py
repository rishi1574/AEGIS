import random
import uuid
import numpy as np
from datetime import datetime, timedelta
from typing import List
from red_team.agents.base_agent import BaseAgent, Transaction, Account

class EnsembleEvasionAgent(BaseAgent):
    def generate_transactions(self, start: datetime, end: datetime, merchants: List[str], accounts: List[Account]) -> List[Transaction]:
        txns = []
        current = start
        while current < end:
            # Exploits the linear weights of the Meta-Learner by appearing safe to 2/3 of the base models.
            if random.random() < 0.06:
                receiver = random.choice(accounts).account_id if random.random() < 0.5 else random.choice(merchants)
                amount = random.uniform(50000, 100000)
                
                txn = Transaction(
                    transaction_id=Transaction.new_id(),
                    timestamp=current,
                    sender_id=self.account.account_id,
                    receiver_id=receiver,
                    amount_inr=amount,
                    payment_rail="UPI_P2P" if receiver.startswith("ACC") else "CARD_CNP",
                    mcc_code="0000",
                    mcc_description="Meta Exploit",
                    sender_device_id=self.account.devices[0],
                    sender_ip_hash=uuid.uuid4().hex[:8],
                    sender_city=self.account.city,
                    receiver_city="Unknown",
                    channel="MOBILE",
                    is_international=False,
                    is_fraud=True,
                    fraud_type="ensemble_evasion",
                    fraud_campaign_id="ensemble_evasion_campaign_1",
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
                txn.amount_zscore = 0; txn.mule_chain_depth = None # Safe to Temporal and Graph
                self.history.append(txn)
                txns.append(txn)
                current += timedelta(days=random.randint(1, 5))
            else:
                current += timedelta(hours=random.randint(1, 24))
        return txns
