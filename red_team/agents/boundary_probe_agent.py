import random
import uuid
import numpy as np
from datetime import datetime, timedelta
from typing import List
from red_team.agents.base_agent import BaseAgent, Transaction, Account

class BoundaryProbeAgent(BaseAgent):
    def generate_transactions(self, start: datetime, end: datetime, merchants: List[str], accounts: List[Account]) -> List[Transaction]:
        txns = []
        current = start
        while current < end:
            # Probes the 0.49 probability margin of XGBoost to map the geometric decision boundary.
            if random.random() < 0.08:
                receiver = random.choice(accounts).account_id if random.random() < 0.5 else random.choice(merchants)
                amount = random.uniform(15000, 16000)
                
                txn = Transaction(
                    transaction_id=Transaction.new_id(),
                    timestamp=current,
                    sender_id=self.account.account_id,
                    receiver_id=receiver,
                    amount_inr=amount,
                    payment_rail="UPI_P2P" if receiver.startswith("ACC") else "CARD_CNP",
                    mcc_code="0000",
                    mcc_description="Margin Probe",
                    sender_device_id=self.account.devices[0],
                    sender_ip_hash=uuid.uuid4().hex[:8],
                    sender_city=self.account.city,
                    receiver_city="Unknown",
                    channel="MOBILE",
                    is_international=False,
                    is_fraud=True,
                    fraud_type="boundary_probe",
                    fraud_campaign_id="boundary_probe_campaign_1",
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
                txn.txn_count_last_1h = 2 # Forces specific boundary conditions
                self.history.append(txn)
                txns.append(txn)
                current += timedelta(hours=random.randint(1, 3))
            else:
                current += timedelta(hours=random.randint(1, 24))
        return txns
