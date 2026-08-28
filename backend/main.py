"""AEGIS Backend — FastAPI + WebSocket with real data integration."""
import json
import asyncio
import random
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from backend.config import Config
from backend.routers import red_team, blue_team, simulation
from backend.services.data_service import data_service

app = FastAPI(title="AEGIS API", version="1.0.0",
              description="Adversarial Evolution & Generative Intelligence Shield")
app.add_middleware(CORSMiddleware, allow_origins=Config.CORS_ORIGINS,
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(red_team.router, prefix="/api/red-team", tags=["Red Team"])
app.include_router(blue_team.router, prefix="/api/blue-team", tags=["Blue Team"])
app.include_router(simulation.router, prefix="/api/simulation", tags=["Simulation"])


class WSManager:
    def __init__(self): self.connections: list[WebSocket] = []
    async def connect(self, ws: WebSocket):
        await ws.accept(); self.connections.append(ws)
    def disconnect(self, ws): self.connections.remove(ws)
    async def broadcast(self, msg: dict):
        for c in list(self.connections):
            try: await c.send_json(msg)
            except: self.connections.remove(c)

manager = WSManager()


@app.websocket("/ws/live-feed")
async def ws_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)
            if msg.get("type") == "launch_attack":
                app.state.active_attack = msg.get("attack_type")
                await ws.send_json({
                    "type": "ack",
                    "message": f"Attack {msg.get('attack_type')} initiated"
                })
    except WebSocketDisconnect:
        manager.disconnect(ws)


async def simulation_telemetry_loop():
    """Background task that broadcasts live telemetry from real or simulated data."""
    generations = 0
    
    # Load real drift data if available
    drift_data = data_service.get_concept_drift_data()
    real_iterations = drift_data.get("iterations", [])
    real_bypass = drift_data.get("red_team_bypass_rate", [])
    real_accuracy = drift_data.get("blue_team_accuracy", [])
    
    # Current state
    bypass_rate = real_bypass[0] if real_bypass else 0.05
    drift_score = 0.1
    fraud_detected = 0
    current_iter_idx = 0

    while True:
        await asyncio.sleep(2.0)
        
        active_attack = getattr(app.state, "active_attack", None)
        
        # Progress through real adversarial iteration data
        if current_iter_idx < len(real_bypass):
            bypass_rate = real_bypass[current_iter_idx]
            if current_iter_idx < len(real_accuracy):
                drift_score = 1.0 - real_accuracy[current_iter_idx]
        
        # Red team log
        attack_names = {
            "synthetic_id_bustout": "Synthetic ID Bust-Out",
            "deepfake_ato": "Deepfake ATO",
            "txn_fuzzing": "Adversarial Txn Fuzzing",
            "vishing": "Hyper-Personalized Vishing",
            "digital_arrest": "Digital Arrest Scam",
            "agentic_hijack": "Agentic Commerce Hijack",
            "merchant_collusion": "Merchant Collusion",
            "api_exploit": "API Exploitation",
            "pig_butchering": "AI Pig Butchering",
            "model_poisoning": "Model Poisoning",
            "supply_chain_bec": "Supply Chain BEC",
            "adversarial_document": "Document Injection",
        }

        if active_attack:
            attack_name = attack_names.get(active_attack, active_attack)
            # Use real data sample for the red team simulation log if available
            recent = data_service.get_interceptions(limit=100)
            if recent:
                target = random.choice(recent)
                red_msg = f"🔴 Simulating {attack_name} vs Receiver {target.get('receiver_id', 'Unknown')[-4:]} (Amt: ₹{target.get('amount_inr', 0)})"
            else:
                red_msg = f"🔴 Initiating {attack_name} simulation..."
        else:
            red_msg = None

        # Blue team log - pull from actual interception records
        blue_msg = None
        if random.random() > 0.4:
            recent = data_service.get_interceptions(limit=50)
            if recent:
                intercept = random.choice(recent)
                blue_msg = f"🛡️ Ensembled Blocked: {intercept.get('fraud_type', 'Suspicious').replace('_', ' ')} (Txn: {intercept.get('transaction_id')}, Risk: {intercept.get('risk_score', 0):.2f})"
                fraud_detected += 1

        generations += 1
        
        # Advance through real adversarial iterations
        if generations % 15 == 0 and current_iter_idx < len(real_bypass) - 1:
            current_iter_idx += 1
            bypass_rate = real_bypass[current_iter_idx]
            if current_iter_idx < len(real_accuracy):
                drift_score = 1.0 - real_accuracy[current_iter_idx]
            
        # Threat Intel Event based on actual active attack
        threat_intel = None
        if active_attack and random.random() > 0.8:
            intel_mapping = {
                "synthetic_id_bustout": {"type": "darkweb", "msg": "Mass synthetic identities detected on darkweb forum", "sev": "high"},
                "deepfake_ato": {"type": "apt", "msg": "Deepfake voice cloning service spotted on Genesis Market", "sev": "critical"},
                "txn_fuzzing": {"type": "botnet", "msg": "High-velocity API probing detected from known botnet IPs", "sev": "medium"},
                "digital_arrest": {"type": "mule", "msg": "New 'Digital Arrest' scam call center identified in Node 4", "sev": "high"},
                "merchant_collusion": {"type": "magecart", "msg": "Anomalous merchant chargebacks detected in APAC", "sev": "medium"},
            }
            if active_attack in intel_mapping:
                choice = intel_mapping[active_attack]
                threat_intel = {
                    "id": random.randint(1000, 9999),
                    "type": choice["type"],
                    "message": choice["msg"],
                    "time": "Just now",
                    "severity": choice["sev"]
                }
            else:
                threat_intel = {
                    "id": random.randint(1000, 9999),
                    "type": "apt",
                    "message": f"Signatures matching {attack_names.get(active_attack, active_attack)} detected",
                    "time": "Just now",
                    "severity": "medium"
                }

        # Know Your Agent (KYA) Event from real intercepted transactions
        kya_event = None
        if random.random() > 0.7:
            recent_interceptions = data_service.get_interceptions(limit=20)
            if recent_interceptions:
                intercept = random.choice(recent_interceptions)
                kya_event = {
                    "id": intercept.get("transaction_id"),
                    "agent": f"Agent-{intercept.get('sender_id', 'Unknown')[-4:]}",
                    "action": f"Txn of ₹{intercept.get('amount_inr', 0)}",
                    "status": "blocked" if intercept.get("recommended_action") == "BLOCKED" else "allowed",
                    "reason": f"Flagged: {intercept.get('fraud_type', 'Suspicious')}"
                }

        # Dynamic SHAP Explanation from real models
        shap_explanation = None
        if random.random() > 0.85:
            real_shaps = data_service.get_sample_shap()
            if real_shaps:
                shap_explanation = random.choice(real_shaps)
            
        payload = {
            "type": "telemetry_update",
            "data": {
                "timestamp": time.time(),
                "generations_evolved": generations,
                "current_bypass_rate": round(bypass_rate, 4),
                "concept_drift_score": round(drift_score, 4),
                "total_fraud_detected": fraud_detected,
                "red_team_log": red_msg,
                "blue_team_log": blue_msg,
                "system_hardness": round((1.0 - bypass_rate) * 100, 1),
                "active_attack": active_attack,
                "threat_intel": threat_intel,
                "kya_event": kya_event,
                "shap_explanation": shap_explanation
            }
        }
        await manager.broadcast(payload)


@app.on_event("startup")
async def startup_event():
    app.state.active_attack = None
    # Load pre-generated data
    data_service.load()
    asyncio.create_task(simulation_telemetry_loop())


@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "service": "aegis-backend",
        "data_loaded": data_service.is_loaded,
        "transactions": len(data_service.transactions_df) if data_service.transactions_df is not None else 0,
    }

app.state.ws_manager = manager
