"""Adversarial Document Injection Agent (Cross-Border Trade Fraud).

Attack Pattern:
  1. GenAI generates pixel-perfect forged invoices and shipping manifests.
  2. Trade-based money laundering via over/under-invoicing.
  3. Letter-of-credit fraud using fabricated trade documents.
  4. Large international wire transfers with inflated values.

Characteristics:
  - International wire transfers (WIRE_INTL rail).
  - Very large amounts (₹10L - ₹2Cr).
  - Receiver in different country/city.
  - Irregular frequency (not periodic like real trade).
  - Amount doesn't correlate with historical trade volumes.
  - NRI or small_business_owner personas.
"""
import random
from datetime import datetime, timedelta
from typing import List, Optional
from red_team.agents.base_agent import BaseAgent, Account, Transaction
from red_team.simulator.india_specific_config import INDIAN_CITIES


def _sample_city():
    cities = list(INDIAN_CITIES.keys())
    weights = list(INDIAN_CITIES.values())
    return random.choices(cities, weights)[0]



class AdversarialDocumentAgent(BaseAgent):
    def __init__(self, account: Account, active_dates: List[datetime]):
        super().__init__(account)
        self.active_dates = [d.date() for d in active_dates]

    def generate_transactions(self, start: datetime, end: datetime,
                              merchants: List[str], accounts: List[Account]) -> List[Transaction]:
        txns = []
        day = start
        while day < end:
            if day.date() in self.active_dates and accounts:
                t = self._make_trade_fraud_txn(day, accounts)
                if t:
                    self.compute_velocity(t)
                    self.history.append(t)
                    txns.append(t)
            day += timedelta(days=1)
        return txns

    def _make_trade_fraud_txn(self, dt: datetime,
                               accounts: List[Account]) -> Optional[Transaction]:
        hour = random.randint(10, 16)
        dt = dt.replace(hour=hour, minute=random.randint(0, 59),
                        second=random.randint(0, 59))

        if dt.weekday() >= 5:
            return None

        # Over-invoiced trade amount
        amt = random.uniform(1000000, 20000000)  # ₹10L - ₹2Cr
        amt = round(amt / 10000) * 10000

        rcv = random.choice(accounts)
        dev = self.account.devices[0] if self.account.devices else Account.new_device()

        return Transaction(
            transaction_id=Transaction.new_id(), timestamp=dt,
            sender_id=self.account.account_id,
            receiver_id=rcv.account_id,
            amount_inr=amt,
            payment_rail="WIRE_INTL", mcc_code="5045",
            mcc_description="IT Services",
            sender_device_id=dev,
            sender_ip_hash=f"IP_{hash(self.account.city + self.account.account_id) % 100000:05d}",
            sender_city=self.account.city,
            receiver_city=_sample_city(),  # Different city
            channel="web", is_international=True,
            is_fraud=True, fraud_type="adversarial_document",
            fraud_campaign_id="CAMP_DOC_01",
            sender_account_age_days=self.account.account_age_days,
            sender_avg_monthly_txn_count=5,
            sender_avg_monthly_spend_inr=self.account.monthly_income * 0.3,
            sender_credit_score=self.account.credit_score,
            sender_persona=self.account.persona_type,
            hour_of_day=hour, day_of_week=dt.weekday(),
            is_weekend=False, is_festival_period=False)
