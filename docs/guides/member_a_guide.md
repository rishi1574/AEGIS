# 🔴🔵 Member A — ML/Backend Lead: Complete Coding Guide

> **Role:** Build the Red Team engine (transaction simulator, fraud agents, RL) and Blue Team engine (XGBoost, GNN, Transformer, Federated, SHAP).  
> **Your directories:** `red_team/`, `blue_team/`, `backend/`  
> **Do NOT touch:** `frontend/`, `docs/walkthrough*`  
> **Language:** Python 3.11+  
> **Key libraries:** FastAPI, PyTorch, PyTorch Geometric, XGBoost, Stable-Baselines3, SHAP, LangChain, OpenAI

---

## SETUP (Run Once on Day 1 Morning)

```bash
cd /Users/swarup/Mastercard_Innovation_Challenge_2026/aegis

python3 -m venv .venv
source .venv/bin/activate

pip install \
  fastapi "uvicorn[standard]" websockets python-socketio \
  openai langchain langchain-openai \
  torch torchvision \
  xgboost scikit-learn \
  stable-baselines3 gymnasium \
  shap \
  pandas numpy scipy \
  redis pydantic python-dotenv \
  networkx joblib

# Create __init__.py for all packages
for dir in red_team red_team/agents red_team/simulator red_team/rl \
           blue_team blue_team/models blue_team/training blue_team/evaluation \
           backend backend/routers backend/services; do
  touch $dir/__init__.py
done
```

Create `.env` in project root:
```
OPENAI_API_KEY=sk-your-key-here
REDIS_URL=redis://localhost:6379
```

---

## DAY 1 — Foundation Files

### File 1: `data/schemas/transaction_schema.json`

```json
{
  "description": "AEGIS Transaction Schema — Single Source of Truth",
  "numeric_features": [
    "amount_inr", "hour_of_day", "day_of_week",
    "sender_account_age_days", "sender_avg_monthly_txn_count",
    "sender_avg_monthly_spend_inr", "sender_credit_score",
    "txn_count_last_1h", "txn_count_last_24h", "txn_amount_last_24h",
    "unique_receivers_last_24h", "unique_devices_last_7d",
    "amount_zscore", "time_since_last_txn_seconds"
  ],
  "boolean_features": [
    "is_weekend", "is_festival_period", "is_international",
    "is_new_receiver", "is_new_device"
  ],
  "categorical_features": [
    "payment_rail", "mcc_code", "sender_persona", "channel", "sender_city"
  ],
  "label": "is_fraud",
  "fraud_types": [
    "synthetic_id_bustout", "deepfake_ato", "adversarial_document",
    "txn_fuzzing", "api_exploit", "merchant_collusion",
    "vishing", "pig_butchering", "digital_arrest",
    "agentic_hijack", "model_poisoning", "supply_chain_bec"
  ],
  "payment_rails": [
    "UPI_P2P", "UPI_P2M", "CARD_CNP", "CARD_POS",
    "NEFT", "RTGS", "IMPS", "BNPL", "WIRE_INTL"
  ],
  "personas": [
    "college_student", "it_professional", "homemaker",
    "retired_officer", "small_business_owner", "nri"
  ]
}
```

---

### File 2: `red_team/simulator/india_specific_config.py`

```python
"""India-specific configuration for the AEGIS payment simulator."""
import random
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

INDIAN_CITIES = {
    "Mumbai": 0.18, "Delhi": 0.16, "Bangalore": 0.12,
    "Hyderabad": 0.08, "Chennai": 0.07, "Kolkata": 0.06,
    "Pune": 0.06, "Ahmedabad": 0.05, "Jaipur": 0.04,
    "Lucknow": 0.03, "Surat": 0.03, "Chandigarh": 0.02,
    "Kochi": 0.02, "Indore": 0.02, "Nagpur": 0.02,
    "Coimbatore": 0.01, "Bhopal": 0.01, "Visakhapatnam": 0.01,
    "Patna": 0.01, "Thiruvananthapuram": 0.01,
}

MCC_DISTRIBUTION = {
    "5411": ("Grocery Stores", 0.20),
    "5812": ("Restaurants", 0.12),
    "5311": ("Department Stores", 0.08),
    "5541": ("Gas Stations", 0.07),
    "5912": ("Pharmacies", 0.05),
    "5999": ("Misc Retail", 0.05),
    "4121": ("Taxi/Rideshare", 0.06),
    "5691": ("Clothing", 0.04),
    "5732": ("Electronics", 0.04),
    "5944": ("Jewelry", 0.02),
    "7011": ("Hotels", 0.03),
    "5814": ("Fast Food", 0.06),
    "4814": ("Telecom", 0.04),
    "6300": ("Insurance", 0.02),
    "8011": ("Medical", 0.03),
    "8211": ("Education", 0.03),
    "7832": ("Entertainment", 0.02),
    "5045": ("IT Services", 0.02),
    "6012": ("Financial Institutions", 0.01),
    "7299": ("Misc Services", 0.01),
}

RAIL_LIMITS = {
    "UPI_P2P":    {"daily": 100000,   "single_max": 100000,  "min": 1,      "typical": (50, 10000)},
    "UPI_P2M":    {"daily": 100000,   "single_max": 100000,  "min": 1,      "typical": (20, 5000)},
    "CARD_CNP":   {"daily": 500000,   "single_max": 200000,  "min": 10,     "typical": (200, 20000)},
    "CARD_POS":   {"daily": 500000,   "single_max": 200000,  "min": 10,     "typical": (100, 15000)},
    "NEFT":       {"daily": 10000000, "single_max": 10000000,"min": 1,      "typical": (1000, 100000)},
    "RTGS":       {"daily": 50000000, "single_max": 50000000,"min": 200000, "typical": (200000, 5000000)},
    "IMPS":       {"daily": 500000,   "single_max": 500000,  "min": 1,      "typical": (500, 50000)},
    "BNPL":       {"daily": 200000,   "single_max": 100000,  "min": 500,    "typical": (1000, 30000)},
    "WIRE_INTL":  {"daily": 50000000, "single_max": 50000000,"min": 10000,  "typical": (50000, 2000000)},
}

FESTIVAL_PERIODS = [
    (1, 14, 1, 16, "Pongal", 1.5),
    (3, 14, 3, 15, "Holi", 1.8),
    (3, 30, 4, 2, "Eid", 1.6),
    (8, 15, 8, 15, "Independence Day", 1.3),
    (10, 2, 10, 12, "Navratri/Dussehra", 2.0),
    (10, 20, 10, 24, "Diwali", 2.8),
    (12, 25, 12, 31, "Christmas/NY", 1.7),
]

@dataclass
class PersonaConfig:
    name: str
    income_range: Tuple[int, int]
    txn_count_range: Tuple[int, int]
    rails: Dict[str, float]
    top_mccs: List[str]
    amount_range: Tuple[int, int]
    credit_range: Tuple[int, int]
    active_hours: Tuple[int, int]
    weekend_mult: float
    age_range: Tuple[int, int]
    devices: Tuple[int, int]

PERSONAS = {
    "college_student": PersonaConfig(
        "College Student", (5000, 15000), (30, 80),
        {"UPI_P2P": .50, "UPI_P2M": .30, "CARD_CNP": .15, "BNPL": .05},
        ["5812","5814","5999","4121","7832"], (20, 2000),
        (650, 720), (8, 24), 1.5, (180, 1095), (1, 2)),
    "it_professional": PersonaConfig(
        "IT Professional", (80000, 200000), (40, 100),
        {"UPI_P2M": .30, "CARD_CNP": .25, "UPI_P2P": .20, "NEFT": .15, "BNPL": .10},
        ["5812","5411","5691","5732","7011"], (100, 25000),
        (720, 850), (7, 23), 1.3, (730, 3650), (1, 3)),
    "homemaker": PersonaConfig(
        "Homemaker", (0, 0), (20, 50),
        {"UPI_P2M": .45, "CARD_POS": .25, "UPI_P2P": .15, "NEFT": .10, "CARD_CNP": .05},
        ["5411","5912","8211","4814","5311"], (50, 10000),
        (680, 760), (8, 20), 1.2, (1825, 7300), (1, 1)),
    "retired_officer": PersonaConfig(
        "Retired Officer", (50000, 100000), (10, 30),
        {"NEFT": .35, "UPI_P2M": .25, "CARD_POS": .20, "UPI_P2P": .15, "IMPS": .05},
        ["5411","5912","8011","6300","4814"], (100, 15000),
        (750, 850), (6, 18), 0.9, (3650, 14600), (1, 1)),
    "small_business_owner": PersonaConfig(
        "Small Business Owner", (200000, 1000000), (60, 200),
        {"UPI_P2M": .25, "NEFT": .25, "CARD_POS": .15, "UPI_P2P": .15, "RTGS": .10, "IMPS": .10},
        ["5999","5045","5311","5411","4121"], (500, 100000),
        (700, 800), (7, 22), 0.7, (1095, 7300), (2, 4)),
    "nri": PersonaConfig(
        "NRI", (500000, 2000000), (5, 20),
        {"WIRE_INTL": .40, "UPI_P2P": .25, "NEFT": .20, "CARD_CNP": .15},
        ["7011","5691","5944","6300","5732"], (5000, 500000),
        (700, 830), (10, 22), 1.1, (1825, 10950), (1, 2)),
}

def sample_city():
    cities = list(INDIAN_CITIES.keys())
    weights = list(INDIAN_CITIES.values())
    return random.choices(cities, weights=weights, k=1)[0]

def sample_mcc():
    codes = list(MCC_DISTRIBUTION.keys())
    items = list(MCC_DISTRIBUTION.values())
    weights = [i[1] for i in items]
    idx = random.choices(range(len(codes)), weights=weights, k=1)[0]
    return codes[idx], items[idx][0]

def is_festival(month, day):
    for sm, sd, em, ed, name, mult in FESTIVAL_PERIODS:
        if sm == em:
            if month == sm and sd <= day <= ed:
                return True, mult
        else:
            if (month == sm and day >= sd) or (month == em and day <= ed):
                return True, mult
    return False, 1.0
```

---

### File 3: `red_team/agents/base_agent.py`

```python
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
```

---

### File 4: `backend/config.py`

```python
import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    CORS_ORIGINS = ["http://localhost:3000"]
```

---

### File 5: `backend/main.py`

```python
"""AEGIS Backend — FastAPI + WebSocket."""
import json
import uuid
from typing import Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from backend.config import Config
from backend.routers import red_team, blue_team, simulation
from backend.services.rl_controller import BattleSimulator

app = FastAPI(title="AEGIS API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=Config.CORS_ORIGINS,
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(red_team.router, prefix="/api/red-team", tags=["Red Team"])
app.include_router(blue_team.router, prefix="/api/blue-team", tags=["Blue Team"])
app.include_router(simulation.router, prefix="/api/simulation", tags=["Simulation"])

class SessionState:
    """Per-session state for each WebSocket connection."""
    def __init__(self, ws: WebSocket):
        self.ws = ws
        self.active_attack: Optional[str] = None
        self.battle_simulator = BattleSimulator()

class WSManager:
    """Manages per-session WebSocket connections and their independent state."""
    def __init__(self):
        self.sessions: dict[str, SessionState] = {}
    async def connect(self, ws: WebSocket) -> str:
        await ws.accept()
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = SessionState(ws)
        await ws.send_json({"type": "session_init", "session_id": session_id})
        return session_id
    def disconnect(self, session_id: str):
        self.sessions.pop(session_id, None)
    async def send_to_session(self, session_id: str, msg: dict):
        session = self.sessions.get(session_id)
        if session and session.ws:
            try: await session.ws.send_json(msg)
            except: self.sessions.pop(session_id, None)

manager = WSManager()

@app.websocket("/ws/live-feed")
async def ws_endpoint(ws: WebSocket):
    session_id = await manager.connect(ws)
    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)
            if msg.get("type") == "launch_attack":
                session = manager.get_session(session_id)
                if session:
                    session.active_attack = msg.get("attack_type")
                    session.battle_simulator.reset(msg.get("attack_type"))
                await ws.send_json({"type":"ack","message":f"Attack {msg.get('attack_type')} initiated"})
    except WebSocketDisconnect: manager.disconnect(session_id)

@app.get("/api/health")
async def health(): return {"status": "healthy", "service": "aegis-backend"}

app.state.ws_manager = manager
```

---

### File 6: `backend/routers/red_team.py`

```python
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any

router = APIRouter()

ATTACKS = [
    {"id":"synthetic_id_bustout","name":"Synthetic ID Bust-Out","layer":"identity","risk":"critical"},
    {"id":"deepfake_ato","name":"Deepfake Voice/Video ATO","layer":"identity","risk":"critical"},
    {"id":"adversarial_document","name":"Document Injection","layer":"identity","risk":"high"},
    {"id":"txn_fuzzing","name":"Adversarial Txn Fuzzing","layer":"network","risk":"critical"},
    {"id":"api_exploit","name":"API Exploit & Replay","layer":"network","risk":"high"},
    {"id":"merchant_collusion","name":"Merchant Collusion","layer":"network","risk":"high"},
    {"id":"vishing","name":"Hyper-Personalized Vishing","layer":"human","risk":"critical"},
    {"id":"pig_butchering","name":"AI Pig Butchering","layer":"human","risk":"high"},
    {"id":"digital_arrest","name":"Digital Arrest Scam","layer":"human","risk":"high"},
    {"id":"agentic_hijack","name":"Agentic Commerce Hijack","layer":"emerging","risk":"critical"},
    {"id":"model_poisoning","name":"Model Poisoning","layer":"emerging","risk":"critical"},
    {"id":"supply_chain_bec","name":"Supply Chain BEC","layer":"emerging","risk":"high"},
]

class LaunchReq(BaseModel):
    attack_type: str
    params: Optional[Dict[str, Any]] = None

@router.post("/launch")
async def launch(req: LaunchReq):
    return {"campaign_id":"CAMP_001","status":"running","attack_type":req.attack_type,"message":f"Launched {req.attack_type}"}

@router.get("/attacks")
async def list_attacks(): return {"attacks": ATTACKS}

@router.get("/status/{cid}")
async def status(cid: str):
    return {"campaign_id":cid,"status":"running","transactions_generated":0,"bypass_rate":0.0,"mutations":0}
```

---

### File 7: `backend/routers/blue_team.py`

```python
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, Optional

router = APIRouter()

class PredictReq(BaseModel):
    transaction: Dict[str, Any]

@router.post("/predict")
async def predict(req: PredictReq):
    return {"transaction_id": req.transaction.get("transaction_id","?"),
            "risk_score":0.15,"is_fraud":False,"confidence":0.85,
            "model_used":"ensemble_v1",
            "shap_values":{"amount_zscore":0.05,"txn_count_last_1h":0.02},
            "recommended_action":"ALLOW","attack_pattern_match":None}

@router.get("/metrics")
async def metrics():
    return {"accuracy":0.942,"precision":0.917,"recall":0.961,"f1_score":0.938,
            "auc_roc":0.973,"false_positive_rate":0.004,"avg_inference_latency_ms":34.2,
            "total_predictions":0,"adversarial_iteration":0}

@router.get("/federated-comparison")
async def federated():
    return {"banks":[{"name":"Bank A","f1":0.82,"auc":0.89,"txn_count":35000},
                     {"name":"Bank B","f1":0.79,"auc":0.86,"txn_count":30000},
                     {"name":"Bank C","f1":0.84,"auc":0.91,"txn_count":35000}],
            "federated":{"f1":0.93,"auc":0.97,"improvement":"+12.8%"}}

@router.get("/interception-log")
async def interceptions(): return {"interceptions":[]}

@router.get("/concept-drift")
async def drift(): return {"iterations":[],"red_team_bypass_rate":[],"blue_team_accuracy":[]}
```

---

### File 8: `backend/routers/simulation.py`

```python
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class SimConfig(BaseModel):
    num_accounts: int = 10000
    num_merchants: int = 500
    time_horizon_days: int = 90
    fraud_ratio: float = 0.02

@router.post("/start")
async def start(cfg: SimConfig): return {"status":"started","config":cfg.model_dump()}

@router.get("/status")
async def status(): return {"status":"idle","progress":0.0,"transactions_generated":0,"adversarial_iteration":0}

@router.get("/system-hardness")
async def hardness(): return {"score":0,"label":"Not Started","trend":"stable"}
```

---

## DAY 2 — Legitimate Agents + Generator

### File 9: `red_team/agents/legitimate_personas.py`

```python
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
```

---

### File 10: `red_team/simulator/transaction_generator.py`

```python
"""Orchestrates all agents to generate the full dataset."""
import random, pandas as pd
from datetime import datetime, timedelta
from typing import List
from pathlib import Path
from red_team.agents.base_agent import Account, Transaction
from red_team.agents.legitimate_personas import create_agent
from red_team.simulator.india_specific_config import PERSONAS

class TransactionGenerator:
    def __init__(self, num_accounts=10000, num_merchants=500, fraud_ratio=0.02):
        self.num_accounts = num_accounts
        self.num_merchants = num_merchants
        self.fraud_ratio = fraud_ratio
        self.accounts: List[Account] = []
        self.merchants: List[str] = []
        self.agents = []
        self.all_txns: List[Transaction] = []

    def setup(self):
        print(f"Setting up {self.num_accounts} accounts...")
        self.merchants = [f"MER_{i:05d}" for i in range(self.num_merchants)]
        weights = {"college_student":.20,"it_professional":.25,"homemaker":.15,
                   "retired_officer":.10,"small_business_owner":.20,"nri":.10}
        for i in range(self.num_accounts):
            pt = random.choices(list(weights.keys()), list(weights.values()))[0]
            agent = create_agent(pt)
            self.accounts.append(agent.account)
            self.agents.append(agent)
            if (i+1) % 2000 == 0: print(f"  {i+1}/{self.num_accounts}")
        print(f"✅ {len(self.accounts)} accounts, {len(self.merchants)} merchants")

    def generate(self, start: datetime, end: datetime) -> pd.DataFrame:
        print(f"Generating txns {start.date()} to {end.date()}...")
        all_t = []
        for i, ag in enumerate(self.agents):
            txns = ag.generate_transactions(start, end, self.merchants, self.accounts)
            all_t.extend(txns)
            if (i+1) % 1000 == 0: print(f"  {i+1}/{len(self.agents)} agents, {len(all_t)} txns")
        self.all_txns = all_t
        df = pd.DataFrame([t.to_dict() for t in all_t]).sort_values("timestamp").reset_index(drop=True)
        print(f"✅ {len(df)} transactions generated")
        print(f"  Rails: {df.payment_rail.value_counts().to_dict()}")
        print(f"  Fraud: {df.is_fraud.mean():.4%}")
        return df

    def save(self, path, df):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
        print(f"💾 Saved to {path}")

if __name__ == "__main__":
    g = TransactionGenerator(1000, 100)
    g.setup()
    df = g.generate(datetime(2026,6,1), datetime(2026,6,30))
    g.save("data/generated/test_txns.csv", df)
```

**Test Day 2:**
```bash
cd /Users/swarup/Mastercard_Innovation_Challenge_2026/aegis
source .venv/bin/activate
python -m red_team.simulator.transaction_generator
# Should create data/generated/test_txns.csv with ~30K+ rows
```

---

## DAY 3-4 — Fraud Agents

### File 11: `red_team/agents/synthetic_id_agent.py`
(Bust-out fraud with 3 phases: trust → escalate → bust)

### File 12: `red_team/agents/vishing_agent.py`
(Coerced UPI transfers — large amounts, unusual timing, new receivers)

### File 13: `red_team/agents/digital_arrest_agent.py`
(Large NEFT/UPI to "government" mule accounts)

### File 14: `red_team/agents/txn_fuzzing_agent.py`
(Many small mutations probing detection boundaries)

### File 15: `red_team/agents/agentic_hijack_agent.py`
(Machine-speed micro-transactions via agent commerce)

### File 16-18: Remaining lighter agents
(deepfake_ato, merchant_collusion, pig_butchering, api_exploit, model_poisoning, supply_chain_bec)

**Every fraud agent MUST:**
1. Inherit `BaseAgent`
2. Set `is_fraud=True` on ALL generated transactions
3. Set `fraud_type` to one of the 12 enum values
4. Set `fraud_campaign_id` to group related txns
5. Call `self.compute_velocity(txn)` before appending

---

## DAY 7-8 — Blue Team Models

### File 19: `blue_team/models/xgboost_baseline.py`

```python
"""XGBoost baseline with SHAP explainability."""
import numpy as np, pandas as pd, xgboost as xgb, shap, joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score, f1_score
from sklearn.preprocessing import LabelEncoder
from pathlib import Path

FEATURES = ["amount_inr","hour_of_day","day_of_week","is_weekend","is_festival_period",
            "is_international","sender_account_age_days","sender_avg_monthly_txn_count",
            "sender_avg_monthly_spend_inr","sender_credit_score",
            "txn_count_last_1h","txn_count_last_24h","txn_amount_last_24h",
            "unique_receivers_last_24h","unique_devices_last_7d",
            "amount_zscore","time_since_last_txn_seconds","is_new_receiver","is_new_device"]
CAT_COLS = ["payment_rail","mcc_code","sender_persona","channel","sender_city"]

class XGBDetector:
    def __init__(self):
        self.model = None; self.explainer = None
        self.encoders = {}; self.feat_names = []

    def prep(self, df):
        f = df.copy()
        for c in CAT_COLS:
            if c in f.columns:
                if c not in self.encoders:
                    self.encoders[c] = LabelEncoder()
                    f[f"{c}_enc"] = self.encoders[c].fit_transform(f[c].astype(str))
                else:
                    classes = set(self.encoders[c].classes_)
                    f[f"{c}_enc"] = f[c].astype(str).apply(lambda x: self.encoders[c].transform([x])[0] if x in classes else -1)
        self.feat_names = FEATURES + [f"{c}_enc" for c in CAT_COLS if c in df.columns]
        for c in self.feat_names:
            if c in f.columns:
                f[c] = f[c].fillna(0)
                if f[c].dtype == bool: f[c] = f[c].astype(int)
        return f[self.feat_names]

    def train(self, df, test_size=0.2):
        X = self.prep(df); y = df["is_fraud"].astype(int)
        Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=test_size, stratify=y, random_state=42)
        spw = (ytr==0).sum() / max((ytr==1).sum(), 1)
        self.model = xgb.XGBClassifier(n_estimators=300, max_depth=8, learning_rate=0.05,
                                        scale_pos_weight=spw, eval_metric="logloss",
                                        use_label_encoder=False, random_state=42, n_jobs=-1)
        self.model.fit(Xtr, ytr, eval_set=[(Xte,yte)], verbose=50)
        yp = self.model.predict(Xte); yprob = self.model.predict_proba(Xte)[:,1]
        print(classification_report(yte, yp, target_names=["Legit","Fraud"]))
        f1 = f1_score(yte, yp); auc = roc_auc_score(yte, yprob)
        print(f"F1={f1:.4f} AUC={auc:.4f}")
        self.explainer = shap.TreeExplainer(self.model)
        return {"f1": f1, "auc": auc, "accuracy": (yp==yte).mean()}

    def predict(self, txn_dict):
        df = pd.DataFrame([txn_dict]); X = self.prep(df)
        prob = float(self.model.predict_proba(X)[0,1])
        sv = self.explainer.shap_values(X)
        shap_d = {self.feat_names[i]: float(sv[0][i]) for i in range(len(self.feat_names))}
        top = dict(sorted(shap_d.items(), key=lambda x: abs(x[1]), reverse=True)[:6])
        return {"risk_score":prob, "is_fraud":prob>0.5, "confidence":max(prob,1-prob),
                "shap_values":top, "recommended_action":"BLOCK" if prob>0.7 else "REVIEW" if prob>0.3 else "ALLOW"}

    def save(self, p="data/models/xgb.joblib"):
        Path(p).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"model":self.model,"enc":self.encoders,"feat":self.feat_names}, p)

    def load(self, p="data/models/xgb.joblib"):
        d = joblib.load(p)
        self.model=d["model"]; self.encoders=d["enc"]; self.feat_names=d["feat"]
        self.explainer = shap.TreeExplainer(self.model)
```

### File 20: `blue_team/models/federated.py`

```python
"""Federated learning simulation — cross-bank comparison."""
import numpy as np, pandas as pd, xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, roc_auc_score

class FederatedSim:
    def __init__(self, n_banks=3):
        self.n = n_banks; self.results = {}

    def run(self, df, features):
        print("🌐 Federated simulation...")
        senders = df["sender_id"].unique(); np.random.shuffle(senders)
        sz = len(senders)//self.n
        bank_map = {}
        for i in range(self.n):
            s, e = i*sz, (i+1)*sz if i<self.n-1 else len(senders)
            for sid in senders[s:e]: bank_map[sid] = i
        df = df.copy(); df["bank"] = df["sender_id"].map(bank_map)

        bank_res = []
        for i in range(self.n):
            bd = df[df["bank"]==i]
            X=bd[features].fillna(0); y=bd["is_fraud"].astype(int)
            if y.sum()<2: bank_res.append({"name":f"Bank {chr(65+i)}","f1":0.5,"auc":0.5,"txn_count":len(bd)}); continue
            Xtr,Xte,ytr,yte = train_test_split(X,y,test_size=.3,stratify=y,random_state=42)
            m = xgb.XGBClassifier(n_estimators=100,max_depth=6,learning_rate=.1,
                                   scale_pos_weight=(ytr==0).sum()/max((ytr==1).sum(),1),
                                   use_label_encoder=False,eval_metric="logloss",random_state=42)
            m.fit(Xtr,ytr,verbose=False)
            yp=m.predict(Xte); ypr=m.predict_proba(Xte)[:,1]
            f1=f1_score(yte,yp); auc=roc_auc_score(yte,ypr) if len(set(yte))>1 else .5
            bank_res.append({"name":f"Bank {chr(65+i)}","f1":round(f1,4),"auc":round(auc,4),"txn_count":len(bd)})
            print(f"  Bank {chr(65+i)}: F1={f1:.4f}")

        X=df[features].fillna(0); y=df["is_fraud"].astype(int)
        Xtr,Xte,ytr,yte = train_test_split(X,y,test_size=.3,stratify=y,random_state=42)
        fm = xgb.XGBClassifier(n_estimators=200,max_depth=8,learning_rate=.05,
                                scale_pos_weight=(ytr==0).sum()/max((ytr==1).sum(),1),
                                use_label_encoder=False,eval_metric="logloss",random_state=42)
        fm.fit(Xtr,ytr,verbose=False)
        yp=fm.predict(Xte); ypr=fm.predict_proba(Xte)[:,1]
        ff1=f1_score(yte,yp); fauc=roc_auc_score(yte,ypr)
        avg = np.mean([r["f1"] for r in bank_res])
        imp = ((ff1-avg)/avg)*100

        self.results = {"banks":bank_res,"federated":{"f1":round(ff1,4),"auc":round(fauc,4),"improvement":f"+{imp:.1f}%"}}
        print(f"  🌐 Federated: F1={ff1:.4f} (+{imp:.1f}%)")
        return self.results
```

### File 21: `blue_team/training/train_pipeline.py`

```python
"""Training pipeline. Usage: python -m blue_team.training.train_pipeline --data data/generated/transactions_full.csv"""
import argparse, pandas as pd
from blue_team.models.xgboost_baseline import XGBDetector, FEATURES, CAT_COLS
from blue_team.models.federated import FederatedSim

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", required=True)
    a = p.parse_args()
    df = pd.read_csv(a.data)
    print(f"Loaded {len(df)} rows, fraud={df.is_fraud.mean():.4%}")

    det = XGBDetector()
    m = det.train(df)
    det.save()
    print(f"XGBoost: {m}")

    fed = FederatedSim()
    fr = fed.run(df, FEATURES)
    print(f"Federated: {fr}")

if __name__=="__main__": main()
```

---

## API CONTRACT (Member A → Member B)

Member B calls these endpoints. Member A MUST return these EXACT shapes:

```
GET  /api/health → {status, service}
GET  /api/red-team/attacks → {attacks: [{id, name, layer, risk}]}
POST /api/red-team/launch → {campaign_id, status, attack_type, message}
GET  /api/blue-team/metrics → {accuracy, precision, recall, f1_score, auc_roc, false_positive_rate, avg_inference_latency_ms, total_predictions, adversarial_iteration}
POST /api/blue-team/predict → {transaction_id, risk_score, is_fraud, confidence, model_used, shap_values, recommended_action, attack_pattern_match}
GET  /api/blue-team/federated-comparison → {banks: [{name, f1, auc, txn_count}], federated: {f1, auc, improvement}}
GET  /api/blue-team/concept-drift → {iterations: [], red_team_bypass_rate: [], blue_team_accuracy: []}
GET  /api/blue-team/interception-log → {interceptions: [{transaction_id, timestamp, amount, risk_score, fraud_type, shap_top_features, action}]}
GET  /api/simulation/system-hardness → {score, label, trend}
WS   /ws/live-feed → emits {type, data}
```
