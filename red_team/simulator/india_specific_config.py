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
