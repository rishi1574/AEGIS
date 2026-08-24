"""Deepfake Voice/Video Account Takeover Agent.

Attack Pattern:
  1. Attacker clones victim's voice from social media (3 seconds of audio).
  2. Calls bank customer service or tricks victim via deepfake video call.
  3. Victim's account credentials are compromised.
  4. Attacker makes rapid P2P transfers from victim's own device to mule chain.

Characteristics:
  - Transactions originate from victim's own device/IP (not a new device).
  - Sudden large P2P transfers to NEW receivers.
  - Occurs during a short burst window (all within 30 minutes).
  - Account goes dormant after the attack.
  - Amount is typically 80-95% of account's available balance.
"""
import random
from datetime import datetime, timedelta
from typing import List, Optional
from red_team.agents.base_agent import BaseAgent, Account, Transaction
from red_team.simulator.india_specific_config import sample_city


class DeepfakeATOAgent(BaseAgent):
    def __init__(self, account: Account, attack_dates: List[datetime]):
        super().__init__(account)
        self.attack_dates = [d.date() for d in attack_dates]
        self.mule_accounts: List[str] = []

    def generate_transactions(self, start: datetime, end: datetime,
                              merchants: List[str], accounts: List[Account]) -> List[Transaction]:
        txns = []
        # Generate some normal transactions before the attack to build history
        day = start
        while day < end:
            if day.date() in self.attack_dates and accounts:
                # The attack: rapid transfers to 3-5 mule accounts within 30 min
                num_mules = random.randint(3, 5)
                mule_targets = random.sample(accounts, min(num_mules, len(accounts)))
                self.mule_accounts = [m.account_id for m in mule_targets]

                # Attack window: 15-30 minutes
                attack_hour = random.randint(22, 23)  # Late night
                attack_dt = day.replace(hour=attack_hour, minute=random.randint(0, 30),
                                        second=random.randint(0, 59))

                # Total amount to drain: based on monthly income * months of savings
                total_drain = self.account.monthly_income * random.uniform(3, 8)
                per_mule = total_drain / num_mules

                for i, mule in enumerate(mule_targets):
                    # Each transfer seconds apart (rapid fire)
                    txn_dt = attack_dt + timedelta(seconds=random.randint(30, 180) * (i + 1))
                    amt = per_mule * random.uniform(0.8, 1.2)
                    amt = min(amt, 100000)  # UPI daily limit

                    t = self._make_ato_txn(txn_dt, mule, round(amt, 2))
                    if t:
                        self.compute_velocity(t)
                        self.history.append(t)
                        txns.append(t)
            else:
                # Normal day: 0-1 small transactions
                if random.random() < 0.3:
                    t = self._make_normal_txn(day, merchants, accounts)
                    if t:
                        self.compute_velocity(t)
                        self.history.append(t)
                        txns.append(t)
            day += timedelta(days=1)
        return txns

    def _make_ato_txn(self, dt: datetime, mule: Account, amt: float) -> Optional[Transaction]:
        # Uses victim's own device (ATO characteristic)
        dev = self.account.devices[0] if self.account.devices else Account.new_device()
        rail = "UPI_P2P" if amt <= 100000 else "IMPS"

        return Transaction(
            transaction_id=Transaction.new_id(), timestamp=dt,
            sender_id=self.account.account_id, receiver_id=mule.account_id,
            amount_inr=amt,
            payment_rail=rail, mcc_code="6012", mcc_description="Financial Institutions",
            sender_device_id=dev,
            sender_ip_hash=f"IP_{hash(self.account.city + self.account.account_id) % 100000:05d}",
            sender_city=self.account.city, receiver_city=mule.city,
            channel="mobile_app", is_international=False,
            is_fraud=True, fraud_type="deepfake_ato",
            fraud_campaign_id="CAMP_ATO_01",
            sender_account_age_days=self.account.account_age_days,
            sender_avg_monthly_txn_count=15,
            sender_avg_monthly_spend_inr=self.account.monthly_income * 0.6,
            sender_credit_score=self.account.credit_score,
            sender_persona=self.account.persona_type,
            hour_of_day=dt.hour, day_of_week=dt.weekday(),
            is_weekend=dt.weekday() >= 5, is_festival_period=False,
            mule_chain_depth=1)

    def _make_normal_txn(self, dt: datetime, merchants, accounts) -> Optional[Transaction]:
        hour = random.randint(9, 20)
        dt = dt.replace(hour=hour, minute=random.randint(0, 59), second=random.randint(0, 59))
        amt = random.uniform(50, 2000)
        dev = self.account.devices[0] if self.account.devices else Account.new_device()

        return Transaction(
            transaction_id=Transaction.new_id(), timestamp=dt,
            sender_id=self.account.account_id,
            receiver_id=random.choice(merchants),
            amount_inr=round(amt, 2),
            payment_rail="UPI_P2M", mcc_code="5411", mcc_description="Grocery Stores",
            sender_device_id=dev,
            sender_ip_hash=f"IP_{hash(self.account.city + self.account.account_id) % 100000:05d}",
            sender_city=self.account.city, receiver_city=self.account.city,
            channel="mobile_app", is_international=False,
            is_fraud=False, fraud_type=None, fraud_campaign_id=None,
            sender_account_age_days=self.account.account_age_days,
            sender_avg_monthly_txn_count=15,
            sender_avg_monthly_spend_inr=self.account.monthly_income * 0.6,
            sender_credit_score=self.account.credit_score,
            sender_persona=self.account.persona_type,
            hour_of_day=hour, day_of_week=dt.weekday(),
            is_weekend=dt.weekday() >= 5, is_festival_period=False)
