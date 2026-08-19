import random
from datetime import datetime, timedelta
from typing import List, Optional
from red_team.agents.base_agent import BaseAgent, Account, Transaction

class DigitalArrestAgent(BaseAgent):
    """
    Digital Arrest Scam:
    Victim is told they are under "digital arrest" by fake law enforcement.
    Requires immediate transfer of almost all funds to a "safe account".
    """
    def __init__(self, account: Account, attack_dates: List[datetime]):
        super().__init__(account)
        self.attack_dates = [d.date() for d in attack_dates]

    def generate_transactions(self, start: datetime, end: datetime, merchants: List[str], accounts: List[Account]) -> List[Transaction]:
        txns = []
        day = start
        while day < end:
            if day.date() in self.attack_dates and accounts:
                t = self._make_fraud_txn(day, accounts)
                if t:
                    self.compute_velocity(t)
                    self.history.append(t)
                    txns.append(t)
            day += timedelta(days=1)
        return txns

    def _make_fraud_txn(self, dt: datetime, accounts) -> Optional[Transaction]:
        hour = random.randint(9, 23)
        dt = dt.replace(hour=hour, minute=random.randint(0,59), second=random.randint(0,59))
        
        # Massive amounts, clearing the bank account
        amt = random.uniform(200000, 1000000)
        rail = "RTGS" 
        rcv = random.choice(accounts)
        
        dev = self.account.devices[0]

        return Transaction(
            transaction_id=Transaction.new_id(), timestamp=dt,
            sender_id=self.account.account_id, receiver_id=rcv.account_id, amount_inr=round(amt, 2),
            payment_rail=rail, mcc_code="6012", mcc_description="Financial Institutions",
            sender_device_id=dev, sender_ip_hash=f"IP_{hash(self.account.city+self.account.account_id)%100000:05d}",
            sender_city=self.account.city, receiver_city=rcv.city,
            channel="web", is_international=False,
            is_fraud=True, fraud_type="digital_arrest", fraud_campaign_id="CAMP_ARREST_01",
            sender_account_age_days=self.account.account_age_days,
            sender_avg_monthly_txn_count=15, sender_avg_monthly_spend_inr=20000,
            sender_credit_score=self.account.credit_score, sender_persona=self.account.persona_type,
            hour_of_day=hour, day_of_week=dt.weekday(), is_weekend=dt.weekday()>=5, is_festival_period=False)
