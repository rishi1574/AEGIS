import random
from datetime import datetime, timedelta
from typing import List, Optional
from red_team.agents.base_agent import BaseAgent, Account, Transaction

class AgenticHijackAgent(BaseAgent):
    """
    Agentic Commerce Hijack (AP4M):
    Prompt-injecting a user's shopping bot to buy gift cards or crypto.
    Characterized by machine-speed execution (multiple txns in seconds).
    """
    def __init__(self, account: Account, attack_dates: List[datetime]):
        super().__init__(account)
        self.attack_dates = [d.date() for d in attack_dates]

    def generate_transactions(self, start: datetime, end: datetime, merchants: List[str], accounts: List[Account]) -> List[Transaction]:
        txns = []
        day = start
        while day < end:
            if day.date() in self.attack_dates and merchants:
                # Machine speed burst
                dt = day.replace(hour=random.randint(2, 4), minute=random.randint(0,59), second=0)
                for i in range(random.randint(10, 20)):
                    dt = dt + timedelta(seconds=random.randint(1, 3)) # Seconds apart
                    t = self._make_fraud_txn(dt, merchants)
                    if t:
                        self.compute_velocity(t)
                        self.history.append(t)
                        txns.append(t)
            day += timedelta(days=1)
        return txns

    def _make_fraud_txn(self, dt: datetime, merchants) -> Optional[Transaction]:
        amt = random.uniform(500, 5000)
        rail = "CARD_CNP" 
        rid = random.choice(merchants)
        
        dev = self.account.devices[0]

        return Transaction(
            transaction_id=Transaction.new_id(), timestamp=dt,
            sender_id=self.account.account_id, receiver_id=rid, amount_inr=round(amt, 2),
            payment_rail=rail, mcc_code="5814", mcc_description="Fast Food", # Often hijacked for digital goods masked as something else
            sender_device_id=dev, sender_ip_hash=f"IP_{hash(self.account.city+self.account.account_id)%100000:05d}",
            sender_city=self.account.city, receiver_city=self.account.city,
            channel="api", is_international=False,
            is_fraud=True, fraud_type="agentic_hijack", fraud_campaign_id="CAMP_HIJACK_01",
            sender_account_age_days=self.account.account_age_days,
            sender_avg_monthly_txn_count=10, sender_avg_monthly_spend_inr=5000,
            sender_credit_score=self.account.credit_score, sender_persona=self.account.persona_type,
            hour_of_day=dt.hour, day_of_week=dt.weekday(), is_weekend=dt.weekday()>=5, is_festival_period=False)
