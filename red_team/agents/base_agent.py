"""Base classes for all AEGIS simulation agents."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import uuid, random
import numpy as np


@dataclass
class Account:
    account_id: str
    persona_type: str
    city: str
    monthly_income: float
    credit_score: Optional[int]
    account_age_days: int
    devices: List[str]
    is_mule: bool = False

    @staticmethod
    def new_id(): return f"ACC_{random.randint(10000,99999)}"
    @staticmethod
    def new_device(): return f"DEV_{uuid.uuid4().hex[:8].upper()}"


@dataclass
class Transaction:
    transaction_id: str
    timestamp: datetime
    sender_id: str
    receiver_id: str
    amount_inr: float
    payment_rail: str
    mcc_code: str
    mcc_description: str
    sender_device_id: str
    sender_ip_hash: str
    sender_city: str
    receiver_city: str
    channel: str
    is_international: bool
    is_fraud: bool
    fraud_type: Optional[str]
    fraud_campaign_id: Optional[str]
    sender_account_age_days: int
    sender_avg_monthly_txn_count: float
    sender_avg_monthly_spend_inr: float
    sender_credit_score: Optional[int]
    sender_persona: str
    hour_of_day: int
    day_of_week: int
    is_weekend: bool
    is_festival_period: bool
    txn_count_last_1h: int = 0
    txn_count_last_24h: int = 0
    txn_amount_last_24h: float = 0.0
    unique_receivers_last_24h: int = 0
    unique_devices_last_7d: int = 0
    amount_zscore: float = 0.0
    time_since_last_txn_seconds: float = 0.0
    is_new_receiver: bool = False
    is_new_device: bool = False
    mule_chain_depth: Optional[int] = None

    @staticmethod
    def new_id(): return f"TXN_{random.randint(1000000000,9999999999)}"

    def to_dict(self):
        d = {}
        for k, v in self.__dict__.items():
            d[k] = v.isoformat() if isinstance(v, datetime) else v
        return d


class BaseAgent(ABC):
    def __init__(self, account: Account):
        self.account = account
        self.history: List[Transaction] = []
        self.seen_receivers: set = set()

    @abstractmethod
    def generate_transactions(self, start: datetime, end: datetime,
                              merchants: List[str], accounts: List[Account]) -> List[Transaction]:
        pass

    def compute_velocity(self, txn: Transaction):
        now = txn.timestamp
        h1 = [t for t in self.history if t.timestamp >= now - timedelta(hours=1)]
        h24 = [t for t in self.history if t.timestamp >= now - timedelta(hours=24)]
        h7d = [t for t in self.history if t.timestamp >= now - timedelta(days=7)]
        txn.txn_count_last_1h = len(h1)
        txn.txn_count_last_24h = len(h24)
        txn.txn_amount_last_24h = sum(t.amount_inr for t in h24)
        txn.unique_receivers_last_24h = len(set(t.receiver_id for t in h24))
        txn.unique_devices_last_7d = len(set(t.sender_device_id for t in h7d))
        if len(self.history) > 5:
            amts = [t.amount_inr for t in self.history[-100:]]
            mu, sig = np.mean(amts), max(np.std(amts), 1.0)
            txn.amount_zscore = (txn.amount_inr - mu) / sig
        txn.time_since_last_txn_seconds = (now - self.history[-1].timestamp).total_seconds() if self.history else 86400
        txn.is_new_receiver = txn.receiver_id not in self.seen_receivers
        txn.is_new_device = txn.sender_device_id != (self.account.devices[0] if self.account.devices else "")
        self.seen_receivers.add(txn.receiver_id)
