import redis
import json
from backend.config import Config

class FeatureStore:
    def __init__(self):
        try:
            self.client = redis.Redis.from_url(Config.REDIS_URL, decode_responses=True)
            self.client.ping()
        except:
            self.client = None
            
    def update_velocity(self, account_id: str, amount: float):
        if not self.client: return
        key = f"acc:{account_id}:vel_24h"
        self.client.incrbyfloat(key, amount)
        self.client.expire(key, 86400)
        
    def get_velocity(self, account_id: str) -> float:
        if not self.client: return 0.0
        val = self.client.get(f"acc:{account_id}:vel_24h")
        return float(val) if val else 0.0
