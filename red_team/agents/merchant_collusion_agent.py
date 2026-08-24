"""Merchant Collusion Network Agent.

Attack Pattern:
  1. Fake merchant accounts are set up with synthetic identities.
  2. Stolen card data is processed through these merchants.
  3. Merchants are designed to look legitimate — with realistic transaction
     patterns, seasonal variations, and diverse customer base.
  4. High in-degree (many unique senders) but low repeat customer rate.
  5. Consistent medium-value transactions (sweet spot to avoid velocity alerts).

Characteristics:
  - Many unique senders → one merchant (high fan-in).
  - No repeat customers (unlike legitimate merchants).
  - Transactions clustered in specific MCC codes (electronics, gift cards).
  - Amount distribution is unusually uniform (not the typical power-law).
  - Merchant is recently registered (low account age).
"""
import random
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional
from red_team.agents.base_agent import BaseAgent, Account, Transaction


class MerchantCollusionAgent(BaseAgent):
    """Generates fraud as if the agent IS the fake merchant receiving stolen card txns."""

    def __init__(self, account: Account, active_dates: List[datetime]):
        super().__init__(account)
        self.active_dates = [d.date() for d in active_dates]
        # Override: this account is a recently-created merchant
        self.account.account_age_days = random.randint(7, 60)
        self.victim_cards_used: set = set()

    def generate_transactions(self, start: datetime, end: datetime,
                              merchants: List[str], accounts: List[Account]) -> List[Transaction]:
        txns = []
        day = start
        while day < end:
            if day.date() in self.active_dates and accounts:
                # Process 8-20 stolen card transactions per active day
                num_txns = random.randint(8, 20)
                # Use diverse victim accounts (never repeat a victim)
                available_victims = [a for a in accounts if a.account_id not in self.victim_cards_used]
                victims = random.sample(available_victims, min(num_txns, len(available_victims)))

                for victim in victims:
                    self.victim_cards_used.add(victim.account_id)
                    t = self._make_collusion_txn(day, victim)
                    if t:
                        self.compute_velocity(t)
                        self.history.append(t)
                        txns.append(t)
            day += timedelta(days=1)
        return txns

    def _make_collusion_txn(self, dt: datetime, victim: Account) -> Optional[Transaction]:
        # Spread across business hours to look legitimate
        hour = random.randint(10, 21)
        dt = dt.replace(hour=hour, minute=random.randint(0, 59), second=random.randint(0, 59))

        # Unusually uniform amount distribution (real merchants have power-law)
        # Sweet spot: ₹2,000-₹15,000 (above micro, below high-value alerts)
        amt = random.uniform(2000, 15000)
        amt = round(amt / 100) * 100  # Round to nearest 100

        rail = random.choice(["CARD_POS", "CARD_CNP"])
        # Target MCC: electronics, gift cards, jewelry (easy to resell)
        mcc_choices = [("5732", "Electronics"), ("5944", "Jewelry"),
                       ("5999", "Misc Retail"), ("5311", "Department Stores")]
        mcc_code, mcc_desc = random.choice(mcc_choices)

        # Sender is the victim, receiver is this merchant (the colluding entity)
        return Transaction(
            transaction_id=Transaction.new_id(), timestamp=dt,
            sender_id=victim.account_id,
            receiver_id=self.account.account_id,  # This agent IS the merchant
            amount_inr=amt,
            payment_rail=rail, mcc_code=mcc_code, mcc_description=mcc_desc,
            sender_device_id=Account.new_device(),  # Each victim uses different device
            sender_ip_hash=f"IP_{hash(victim.city + victim.account_id) % 100000:05d}",
            sender_city=victim.city,
            receiver_city=self.account.city,
            channel="pos_terminal" if rail == "CARD_POS" else "web",
            is_international=False,
            is_fraud=True, fraud_type="merchant_collusion",
            fraud_campaign_id="CAMP_COLLUSION_01",
            sender_account_age_days=victim.account_age_days,
            sender_avg_monthly_txn_count=random.randint(10, 40),
            sender_avg_monthly_spend_inr=random.uniform(5000, 50000),
            sender_credit_score=victim.credit_score,
            sender_persona=victim.persona_type,
            hour_of_day=hour, day_of_week=dt.weekday(),
            is_weekend=dt.weekday() >= 5, is_festival_period=False)
