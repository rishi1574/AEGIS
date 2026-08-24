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
            red_msg = f"🔴 RL Agent mutated [{attack_name}] vector by {random.uniform(1.5, 8.0):.1f}%"
            bypass_rate = min(0.95, bypass_rate + random.uniform(0.01, 0.05))
        elif random.random() > 0.3:
            ftype = random.choice(list(attack_names.values()))
            red_msg = f"🔴 Probing [{ftype}] — mutation #{random.randint(1, 999)}"
        else:
            red_msg = None

        # Blue team log
        if random.random() > 0.25:
            score = random.uniform(0.65, 0.99)
            model_type = random.choice(["XGBoost", "Graph Detector", "Temporal Analyzer", "Ensemble"])
            action = "BLOCKED" if score > 0.7 else "FLAGGED"
            blue_msg = f"🛡️ {model_type} {action} anomalous sequence (Score: {score:.2f})"
            fraud_detected += random.randint(1, 3)
        else:
            blue_msg = None

        generations += 1
        
        # Slowly evolve metrics (simulate the loop progressing)
        if not active_attack:
            bypass_rate = max(0.01, bypass_rate - random.uniform(0.001, 0.01))
        drift_score += random.uniform(-0.02, 0.03)
        drift_score = max(0.0, min(drift_score, 1.0))

        # Advance through real data slowly
        if generations % 15 == 0 and current_iter_idx < len(real_bypass) - 1:
            current_iter_idx += 1
            
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
