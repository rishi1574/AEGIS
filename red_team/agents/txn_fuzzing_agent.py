import random
from datetime import datetime, timedelta
from typing import List, Optional
from red_team.agents.base_agent import BaseAgent, Account, Transaction

class TxnFuzzingAgent(BaseAgent):
    """
    Adversarial Txn Fuzzing:
    AI alters amounts slightly (e.g. 49,999 instead of 50,000) or alters frequency
    just under the threshold of the Blue Team model.
    """
    def __init__(self, account: Account, active_dates: List[datetime]):
        super().__init__(account)
        self.active_dates = [d.date() for d in active_dates]

    def generate_transactions(self, start: datetime, end: datetime, merchants: List[str], accounts: List[Account]) -> List[Transaction]:
        txns = []
        day = start
        while day < end:
            if day.date() in self.active_dates and merchants:
                # Burst of transactions just under the typical limit
                for _ in range(random.randint(5, 8)):
                    t = self._make_fraud_txn(day, merchants)
                    if t:
                        self.compute_velocity(t)
                        self.history.append(t)
                        txns.append(t)
            day += timedelta(days=1)
        return txns

    def _make_fraud_txn(self, dt: datetime, merchants) -> Optional[Transaction]:
        hour = random.randint(0, 23)
        dt = dt.replace(hour=hour, minute=random.randint(0,59), second=random.randint(0,59))
        
        # Fuzzing the amount just below round number thresholds
        amt = random.choice([4999, 9999, 49999, 99999]) - random.uniform(0.01, 1.0)
        rail = "CARD_CNP" 
        rid = random.choice(merchants)
        
        dev = Account.new_device()

        return Transaction(
            transaction_id=Transaction.new_id(), timestamp=dt,
            sender_id=self.account.account_id, receiver_id=rid, amount_inr=round(amt, 2),
            payment_rail=rail, mcc_code="5999", mcc_description="Misc Retail",
            sender_device_id=dev, sender_ip_hash=f"IP_{hash(self.account.city+self.account.account_id)%100000:05d}",
            sender_city=self.account.city, receiver_city=self.account.city,
            channel="web", is_international=False,
            is_fraud=True, fraud_type="txn_fuzzing", fraud_campaign_id="CAMP_FUZZ_01",
            sender_account_age_days=self.account.account_age_days,
            sender_avg_monthly_txn_count=20, sender_avg_monthly_spend_inr=10000,
            sender_credit_score=self.account.credit_score, sender_persona=self.account.persona_type,
            hour_of_day=hour, day_of_week=dt.weekday(), is_weekend=dt.weekday()>=5, is_festival_period=False)
