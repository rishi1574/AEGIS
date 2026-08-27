"""AI-Powered Pig Butchering Agent.

Attack Pattern:
  1. LLM chatbot builds emotional trust with victim over weeks.
  2. Initial small "test" investments that show fake returns.
  3. Escalating transfer amounts as trust grows.
  4. Multiple victims funnel money to same receiver cluster.
  5. Final large withdrawal attempt before disappearing.

Characteristics:
  - Gradual escalation over weeks (₹500 → ₹5,000 → ₹50,000).
  - Always P2P transfers (UPI/NEFT) to same small set of receivers.
  - Transactions at odd hours (emotional manipulation during vulnerable times).
  - Multiple campaign victims → same receiver accounts.
"""
import random
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional
from red_team.agents.base_agent import BaseAgent, Account, Transaction


class PigButcheringAgent(BaseAgent):
    def __init__(self, account: Account, campaign_start: datetime = None):
        super().__init__(account)
        self.campaign_start = campaign_start or datetime(2026, 6, 5)
        self.investment_accounts = []  # Fake investment platform mule accounts
        self.phase = "seeding"
        self.total_invested = 0

    def generate_transactions(self, start: datetime, end: datetime,
                              merchants: List[str], accounts: List[Account]) -> List[Transaction]:
        # Pick 2-3 "investment platform" mule accounts
        if not self.investment_accounts and accounts:
            self.investment_accounts = random.sample(accounts, min(3, len(accounts)))

        txns = []
        day = start
        while day < end:
            days_in_campaign = (day - self.campaign_start).days
            if days_in_campaign < 0 or not self.investment_accounts:
                day += timedelta(days=1)
                continue

            # Phase logic
            if days_in_campaign < 5:
                self.phase = "seeding"
            elif days_in_campaign < 15:
                self.phase = "building"
            elif days_in_campaign < 22:
                self.phase = "escalating"
            else:
                self.phase = "draining"

            should_transact = random.random() < self._activity_probability()
            if should_transact:
                t = self._make_investment_txn(day)
                if t:
                    self.compute_velocity(t)
                    self.history.append(t)
                    txns.append(t)

            day += timedelta(days=1)
        return txns

    def _activity_probability(self):
        """How likely is a transaction on a given day per phase."""
        return {"seeding": 0.2, "building": 0.4,
                "escalating": 0.6, "draining": 0.9}.get(self.phase, 0.3)

    def _make_investment_txn(self, dt: datetime) -> Optional[Transaction]:
        # Late evening/night hours (emotional manipulation timing)
        hour = random.choice([21, 22, 23, 0, 1, 10, 11])
        dt = dt.replace(hour=hour, minute=random.randint(0, 59),
                        second=random.randint(0, 59))

        # Escalating amounts per phase
        amount_ranges = {
            "seeding": (500, 2000),
            "building": (2000, 10000),
            "escalating": (10000, 50000),
            "draining": (50000, 200000),
        }
        lo, hi = amount_ranges.get(self.phase, (1000, 5000))
        amt = round(random.uniform(lo, hi), 2)

        # Always to the same mule cluster
        target = random.choice(self.investment_accounts)
        rail = "UPI_P2P" if amt <= 100000 else "NEFT"
        dev = self.account.devices[0] if self.account.devices else Account.new_device()

        self.total_invested += amt

        return Transaction(
            transaction_id=Transaction.new_id(), timestamp=dt,
            sender_id=self.account.account_id,
            receiver_id=target.account_id,
            amount_inr=amt,
            payment_rail=rail, mcc_code="6012",
            mcc_description="Financial Institutions",
            sender_device_id=dev,
            sender_ip_hash=f"IP_{hash(self.account.city + self.account.account_id) % 100000:05d}",
            sender_city=self.account.city,
            receiver_city=target.city,
            channel="mobile_app", is_international=False,
            is_fraud=True, fraud_type="pig_butchering",
            fraud_campaign_id="CAMP_PIG_01",
            sender_account_age_days=self.account.account_age_days,
            sender_avg_monthly_txn_count=20,
            sender_avg_monthly_spend_inr=self.account.monthly_income * 0.6,
            sender_credit_score=self.account.credit_score,
            sender_persona=self.account.persona_type,
            hour_of_day=hour, day_of_week=dt.weekday(),
            is_weekend=dt.weekday() >= 5, is_festival_period=False)
