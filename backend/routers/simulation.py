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
