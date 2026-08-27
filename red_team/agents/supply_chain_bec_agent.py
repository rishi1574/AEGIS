"""Supply Chain / Business Email Compromise (BEC) Agent.

Attack Pattern:
  1. GenAI generates fake vendor invoices, contracts, and email threads.
  2. Combined with deepfake executive voice authorization.
  3. B2B payment is redirected to attacker-controlled account.
  4. High-value single transactions (NEFT/RTGS) to new payees.

Characteristics:
  - Very large single transactions (₹5L - ₹50L).
  - NEFT/RTGS rail (B2B payment channels).
  - New receiver that was never transacted with before.
  - Business hours on weekdays (mimics corporate payment cycles).
  - Sender is typically a small_business_owner or it_professional persona.
  - Amount is near-exact match to a previous legitimate vendor payment (mimicry).
"""
import random
from datetime import datetime, timedelta
from typing import List, Optional
from red_team.agents.base_agent import BaseAgent, Account, Transaction


class SupplyChainBECAgent(BaseAgent):
    def __init__(self, account: Account, active_dates: List[datetime]):
        super().__init__(account)
        self.active_dates = [d.date() for d in active_dates]

    def generate_transactions(self, start: datetime, end: datetime,
                              merchants: List[str], accounts: List[Account]) -> List[Transaction]:
        txns = []
        day = start
        while day < end:
            if day.date() in self.active_dates and accounts:
                # BEC: 1-2 large redirected payments
                num_payments = random.randint(1, 2)
                for _ in range(num_payments):
                    t = self._make_bec_txn(day, accounts)
                    if t:
                        self.compute_velocity(t)
                        self.history.append(t)
                        txns.append(t)
            day += timedelta(days=1)
        return txns

    def _make_bec_txn(self, dt: datetime, accounts: List[Account]) -> Optional[Transaction]:
        # Business hours, weekdays only
        hour = random.randint(10, 17)
        dt = dt.replace(hour=hour, minute=random.randint(0, 59),
                        second=random.randint(0, 59))

        # If it's a weekend, BEC wouldn't happen (corporate)
        if dt.weekday() >= 5:
            return None

        # Large B2B amounts — vendor payment scale
        amt = random.uniform(500000, 5000000)
        amt = round(amt / 1000) * 1000  # Round to nearest 1000

        rail = "RTGS" if amt >= 200000 else "NEFT"
        rcv = random.choice(accounts)
        dev = self.account.devices[0] if self.account.devices else Account.new_device()

        return Transaction(
            transaction_id=Transaction.new_id(), timestamp=dt,
            sender_id=self.account.account_id,
            receiver_id=rcv.account_id,
            amount_inr=amt,
            payment_rail=rail, mcc_code="5045",
            mcc_description="IT Services",
            sender_device_id=dev,
            sender_ip_hash=f"IP_{hash(self.account.city + self.account.account_id) % 100000:05d}",
            sender_city=self.account.city,
            receiver_city=rcv.city,
            channel="web", is_international=False,
            is_fraud=True, fraud_type="supply_chain_bec",
            fraud_campaign_id="CAMP_BEC_01",
            sender_account_age_days=self.account.account_age_days,
            sender_avg_monthly_txn_count=30,
            sender_avg_monthly_spend_inr=self.account.monthly_income * 0.4,
            sender_credit_score=self.account.credit_score,
            sender_persona=self.account.persona_type,
            hour_of_day=hour, day_of_week=dt.weekday(),
            is_weekend=False, is_festival_period=False)
