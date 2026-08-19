"""AEGIS Backend — FastAPI + WebSocket."""
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from backend.config import Config
from backend.routers import red_team, blue_team, simulation

app = FastAPI(title="AEGIS API", version="1.0.0")
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
                await ws.send_json({"type":"ack","message":f"Attack {msg.get('attack_type')} initiated"})
    except WebSocketDisconnect: manager.disconnect(ws)

import asyncio
import random
import time

async def simulation_telemetry_loop():
    """Background task to simulate live telemetry and broadcast to connected clients."""
    generations = 0
    drift_score = 0.1
    bypass_rate = 0.05
    fraud_detected = 0
    
    while True:
        await asyncio.sleep(2.0) # Tick every 2 seconds
        
        active_attack = getattr(app.state, "active_attack", None)
        
        # Simulate red team activity
        if active_attack:
            red_msg = f"RL Agent mutated [{active_attack}] vector by {random.uniform(1.5, 5.0):.1f}%"
        elif random.random() > 0.4:
            red_msg = f"RL Agent mutated [Baseline Fuzzing] vector by {random.uniform(1.5, 5.0):.1f}%"
        else:
            red_msg = None
            
        # Simulate blue team activity
        if random.random() > 0.3:
            blue_msg = f"Ensemble Model detected anomalous sequence (Score: {random.uniform(0.7, 0.99):.2f})"
            fraud_detected += random.randint(1, 5)
        else:
            blue_msg = None

        generations += 1
        
        # Slowly drift the bypass rate
        if active_attack:
            bypass_rate += random.uniform(0.005, 0.03) # Bypass rate goes up faster when active attack is running
        else:
            bypass_rate += random.uniform(-0.01, 0.015)
            
        bypass_rate = max(0.01, min(bypass_rate, 0.95))
        
        drift_score += random.uniform(-0.02, 0.03)
        drift_score = max(0.0, min(drift_score, 1.0))
            
        payload = {
            "type": "telemetry_update",
            "data": {
                "timestamp": time.time(),
                "generations_evolved": generations,
                "current_bypass_rate": bypass_rate,
                "concept_drift_score": drift_score,
                "total_fraud_detected": fraud_detected,
                "red_team_log": red_msg,
                "blue_team_log": blue_msg,
                "kya_anomalies": random.randint(0, 1)
            }
        }
        await manager.broadcast(payload)

@app.on_event("startup")
async def startup_event():
    app.state.active_attack = None
    asyncio.create_task(simulation_telemetry_loop())

@app.get("/api/health")
async def health(): return {"status": "healthy", "service": "aegis-backend"}

app.state.ws_manager = manager
