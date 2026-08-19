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

from fastapi import Request

@router.post("/launch")
async def launch(req: LaunchReq, request: Request):
    request.app.state.active_attack = req.attack_type
    return {"campaign_id":"CAMP_001","status":"running","attack_type":req.attack_type,"message":f"Launched {req.attack_type}"}

@router.get("/attacks")
async def list_attacks(): return {"attacks": ATTACKS}

@router.get("/status/{cid}")
async def status(cid: str):
    return {"campaign_id":cid,"status":"running","transactions_generated":0,"bypass_rate":0.0,"mutations":0}
