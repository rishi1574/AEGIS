import random
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional
from red_team.agents.base_agent import BaseAgent, Account, Transaction
from red_team.simulator.india_specific_config import PERSONAS, sample_mcc, RAIL_LIMITS

class SyntheticIDAgent(BaseAgent):
    """
    Bust-out fraud with 3 phases:
    1. Trust building: Normal low-value txns for months.
    2. Escalation: Slowly increasing limits.
    3. Bust-out: Maxing out all credit via POS or P2M to controlled merchants.
    """
    def __init__(self, account: Account, bust_out_date: datetime):
        super().__init__(account)
        self.bust_out_date = bust_out_date
        self.phase = "trust" # trust, escalate, bust
        self.collusion_merchants = []

    def generate_transactions(self, start: datetime, end: datetime, merchants: List[str], accounts: List[Account]) -> List[Transaction]:
        self.collusion_merchants = random.sample(merchants, min(len(merchants), 3))
        txns = []
        day = start
        while day < end:
            # Determine phase
            days_to_bust = (self.bust_out_date - day).days
            if days_to_bust < 0:
                break # Account abandoned after bust out
            elif days_to_bust <= 2:
                self.phase = "bust"
            elif days_to_bust <= 30:
                self.phase = "escalate"
            else:
                self.phase = "trust"

            count = self._daily_count()
            for _ in range(count):
                t = self._make_txn(day, merchants, accounts)
                if t:
                    self.compute_velocity(t)
                    self.history.append(t)
                    txns.append(t)
            day += timedelta(days=1)
        return txns

    def _daily_count(self):
        if self.phase == "trust":
            return np.random.poisson(0.5)
        elif self.phase == "escalate":
            return np.random.poisson(1.5)
        else: # bust
            return random.randint(5, 15)

    def _make_txn(self, dt: datetime, merchants, accounts) -> Optional[Transaction]:
        hour = random.randint(8, 22) if self.phase != "bust" else random.randint(0, 23)
        dt = dt.replace(hour=hour, minute=random.randint(0,59), second=random.randint(0,59))
        
        if self.phase == "trust":
            amt = random.uniform(50, 500)
            rail = "UPI_P2M"
            rid = random.choice(merchants)
        elif self.phase == "escalate":
            amt = random.uniform(1000, 5000)
            rail = "CARD_POS"
            rid = random.choice(merchants)
        else: # bust
            amt = random.uniform(20000, 100000)
            rail = "CARD_CNP"
            rid = random.choice(self.collusion_merchants)

        mcc, mdesc = sample_mcc()
        dev = self.account.devices[0]

        is_fraud = (self.phase == "bust")
        
        return Transaction(
            transaction_id=Transaction.new_id(), timestamp=dt,
            sender_id=self.account.account_id, receiver_id=rid, amount_inr=round(amt, 2),
            payment_rail=rail, mcc_code=mcc, mcc_description=mdesc,
            sender_device_id=dev, sender_ip_hash=f"IP_SYN_{hash(self.account.account_id)%10000}",
            sender_city=self.account.city, receiver_city=self.account.city,
            channel="web" if rail=="CARD_CNP" else "mobile_app", is_international=False,
            is_fraud=is_fraud, fraud_type="synthetic_id_bustout" if is_fraud else None, 
            fraud_campaign_id="CAMP_SYN_01" if is_fraud else None,
            sender_account_age_days=self.account.account_age_days,
            sender_avg_monthly_txn_count=20, sender_avg_monthly_spend_inr=5000,
            sender_credit_score=self.account.credit_score, sender_persona=self.account.persona_type,
            hour_of_day=hour, day_of_week=dt.weekday(), is_weekend=dt.weekday()>=5, is_festival_period=False)
