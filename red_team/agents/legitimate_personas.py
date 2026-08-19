"""Legitimate persona agents generating realistic transactions."""
import random
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional
from red_team.agents.base_agent import BaseAgent, Account, Transaction
from red_team.simulator.india_specific_config import (
    PERSONAS, sample_city, sample_mcc, RAIL_LIMITS, is_festival
)

class LegitAgent(BaseAgent):
    def __init__(self, account: Account, cfg):
        super().__init__(account)
        self.cfg = cfg
        self.income = random.randint(*cfg.income_range) if cfg.income_range[1] > 0 else 30000
        self.budget = self.income * random.uniform(0.5, 0.85)
        self.regular_merchants = []

    def generate_transactions(self, start, end, merchants, accounts):
        self.regular_merchants = random.sample(merchants, min(len(merchants), random.randint(5, 15)))
        txns = []
        day = start
        while day < end:
            for _ in range(self._daily_count(day)):
                t = self._make_txn(day, merchants, accounts)
                if t:
                    self.compute_velocity(t)
                    self.history.append(t)
                    txns.append(t)
            day += timedelta(days=1)
        return txns

    def _daily_count(self, dt):
        base = np.mean(self.cfg.txn_count_range) / 30
        if dt.weekday() >= 5: base *= self.cfg.weekend_mult
        fest, m = is_festival(dt.month, dt.day)
        if fest: base *= m
        if dt.day in [1,15,28,30]: base *= 1.4
        return max(0, np.random.poisson(max(base, 0.5)))

    def _make_txn(self, dt, merchants, accounts) -> Optional[Transaction]:
        rail = random.choices(list(self.cfg.rails.keys()), list(self.cfg.rails.values()))[0]
        hour = self._pick_hour()
        amt = self._pick_amount(dt)
        lim = RAIL_LIMITS.get(rail, RAIL_LIMITS["UPI_P2M"])
        amt = max(lim["min"], min(amt, lim["single_max"]))

        if rail in ("UPI_P2P","NEFT","RTGS","IMPS","WIRE_INTL"):
            if not accounts: return None
            rcv = random.choice(accounts)
            rid, rcity = rcv.account_id, rcv.city
        else:
            rid = random.choice(self.regular_merchants) if random.random()<0.7 and self.regular_merchants else random.choice(merchants)
            rcity = self.account.city

        mcc, mdesc = (random.choice(self.cfg.top_mccs), "Preferred") if random.random()<0.6 and self.cfg.top_mccs else sample_mcc()
        dev = self.account.devices[0] if self.account.devices else Account.new_device()
        fest, _ = is_festival(dt.month, dt.day)
        ch_map = {"UPI_P2P":"mobile_app","UPI_P2M":"mobile_app","CARD_CNP":"web",
                  "CARD_POS":"pos_terminal","NEFT":"web","RTGS":"web","IMPS":"mobile_app",
                  "BNPL":"web","WIRE_INTL":"web"}

        return Transaction(
            transaction_id=Transaction.new_id(), timestamp=dt.replace(hour=hour, minute=random.randint(0,59), second=random.randint(0,59)),
            sender_id=self.account.account_id, receiver_id=rid, amount_inr=round(amt,2),
            payment_rail=rail, mcc_code=mcc, mcc_description=mdesc,
            sender_device_id=dev, sender_ip_hash=f"IP_{hash(self.account.city+self.account.account_id)%100000:05d}",
            sender_city=self.account.city, receiver_city=rcity,
            channel=ch_map.get(rail,"mobile_app"), is_international=(rail=="WIRE_INTL"),
            is_fraud=False, fraud_type=None, fraud_campaign_id=None,
            sender_account_age_days=self.account.account_age_days,
            sender_avg_monthly_txn_count=np.mean(self.cfg.txn_count_range),
            sender_avg_monthly_spend_inr=self.budget,
            sender_credit_score=self.account.credit_score, sender_persona=self.account.persona_type,
            hour_of_day=hour, day_of_week=dt.weekday(), is_weekend=dt.weekday()>=5, is_festival_period=fest)

    def _pick_hour(self):
        lo, hi = self.cfg.active_hours
        while True:
            h = int(np.random.normal((lo+hi)/2, 3))
            if lo <= h < min(hi, 24): return h

    def _pick_amount(self, dt):
        lo, hi = self.cfg.amount_range
        amt = np.random.lognormal(np.log((lo+hi)/2), 0.8)
        amt = max(lo*0.5, min(amt, hi*2))
        fest, m = is_festival(dt.month, dt.day)
        if fest: amt *= random.uniform(1.0, m)
        if amt < 100: amt = round(amt)
        elif amt < 1000: amt = round(amt/10)*10
        else: amt = round(amt/100)*100
        return float(max(1, amt))

def create_agent(persona_type, city=None):
    cfg = PERSONAS[persona_type]
    if not city: city = sample_city()
    nd = random.randint(*cfg.devices)
    acc = Account(Account.new_id(), persona_type, city,
                  random.randint(*cfg.income_range) if cfg.income_range[1]>0 else 0,
                  random.randint(*cfg.credit_range), random.randint(*cfg.age_range),
                  [Account.new_device() for _ in range(nd)])
    return LegitAgent(acc, cfg)
