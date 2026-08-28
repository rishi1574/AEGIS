"""VANGUARD Backend — FastAPI + WebSocket with real data integration."""
import json
import asyncio
import random
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from backend.config import Config
from backend.routers import red_team, blue_team, simulation
from backend.services.data_service import data_service
from backend.services.rl_controller import BattleSimulator

battle_simulator = BattleSimulator()

app = FastAPI(title="VANGUARD API", version="1.0.0",
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
                attack_type = msg.get("attack_type")
                app.state.active_attack = attack_type
                # Reset the battle simulator for a new fight
                battle_simulator.reset(attack_type)
                await ws.send_json({
                    "type": "ack",
                    "message": f"Attack {attack_type} initiated"
                })
    except WebSocketDisconnect:
        manager.disconnect(ws)


async def simulation_telemetry_loop():
    """Background task that broadcasts live telemetry from real data."""
    generations = 0

    # Load real drift data if available
    drift_data = data_service.get_concept_drift_data()
    real_bypass = drift_data.get("red_team_bypass_rate", [])
    real_accuracy = drift_data.get("blue_team_accuracy", [])

    # Current state
    bypass_rate = real_bypass[0] if real_bypass else 0.0
    drift_score = 0.1
    fraud_detected = 0
    current_iter_idx = 0

    # Track which fraud transactions we've already used (rotate through dataset)
    fraud_txn_offset = 0

    # For IDLE mode: keep a stable small set of nodes instead of random sampling each tick
    idle_graph_cache = None
    idle_cache_tick = 0

    while True:
        await asyncio.sleep(2.0)

        active_attack = getattr(app.state, "active_attack", None)

        # Progress through real adversarial iteration data
        if current_iter_idx < len(real_bypass):
            bypass_rate = real_bypass[current_iter_idx]
            if current_iter_idx < len(real_accuracy):
                drift_score = 1.0 - real_accuracy[current_iter_idx]

        generations += 1

        # Advance through real adversarial iterations
        if generations % 15 == 0 and current_iter_idx < len(real_bypass) - 1:
            current_iter_idx += 1

        # ──────────────────────────────────────────────
        # BATTLE SIMULATOR: Feed real transactions
        # ──────────────────────────────────────────────
        battle_result = None
        red_msg = None
        blue_msg = None

        if active_attack and data_service.transactions_df is not None and len(data_service.transactions_df) > 0:
            df = data_service.transactions_df

            # Get fraud transactions matching the active attack type
            fraud_df = df[df["fraud_type"] == active_attack]
            if len(fraud_df) == 0:
                # Fallback: use any fraud transactions
                fraud_df = df[df["is_fraud"] == True]

            # Rotate through fraud transactions so we don't repeat the same ones
            fraud_sample_size = min(5, len(fraud_df))
            if fraud_txn_offset + fraud_sample_size > len(fraud_df):
                fraud_txn_offset = 0
            fraud_txns = fraud_df.iloc[fraud_txn_offset:fraud_txn_offset + fraud_sample_size].to_dict("records")
            fraud_txn_offset += fraud_sample_size

            # Get normal transactions
            normal_df = df[df["is_fraud"] == False]
            normal_txns = normal_df.sample(min(5, len(normal_df))).to_dict("records")

            # Run the battle tick
            battle_result = battle_simulator.process_tick(fraud_txns, normal_txns)
            red_msg = battle_result["red_msg"]
            blue_msg = battle_result["blue_msg"]

            # Update bypass rate from the battle
            bypass_rate = battle_result["red_team_success_rate"]

            fraud_detected += sum(1 for inst in battle_result["adversarial_instances"]
                                  if not inst["isEvaded"] and inst["phase"] != "RECON")

            # Clear idle cache when battle is active
            idle_graph_cache = None
        else:
            # No attack active — show a stable, clean normal traffic view
            if data_service.transactions_df is not None and len(data_service.transactions_df) > 0:
                # Refresh IDLE graph every 10 ticks (20 seconds) for variety
                if idle_graph_cache is None or (generations - idle_cache_tick) > 10:
                    normal_df = data_service.transactions_df[
                        data_service.transactions_df["is_fraud"] == False
                    ]
                    # Pick a small stable sample of 4 transactions → ~8 nodes
                    sample_txns = normal_df.sample(min(4, len(normal_df))).to_dict("records")

                    nodes_set = set()
                    edges = []
                    for txn in sample_txns:
                        sender = str(txn.get("sender_id", ""))[-6:]
                        receiver = str(txn.get("receiver_id", ""))[-6:]
                        nodes_set.add(sender)
                        nodes_set.add(receiver)
                        edges.append({
                            "source": sender,
                            "target": receiver,
                            "isFraud": False,
                            "isFeedback": False,
                            "amount": float(txn.get("amount_inr", 0)),
                        })

                    idle_graph_cache = {
                        "nodes": [
                            {
                                "id": n,
                                "type": "merchant" if n.startswith("MER_") else "account",
                                "txn_count": 1,
                                "risk": 0.01,
                                "blocked_count": 0,
                            }
                            for n in nodes_set
                        ],
                        "edges": edges,
                    }
                    idle_cache_tick = generations

                battle_result = {
                    "phase": "IDLE",
                    "tick": 0,
                    "transaction_graph": idle_graph_cache,
                    "adversarial_instances": [],
                    "detected_attack_type": None,
                    "detection_confidence": 0,
                    "red_team_success_rate": 0,
                    "blue_team_sensitivity": 0,
                    "mutation_generation": 0,
                    "mutation_params": {
                        "amount_multiplier": 1.0,
                        "velocity_shift_ms": 0,
                        "route_obfuscation": 0.0,
                    },
                }

        # Threat Intel Event based on actual active attack
        threat_intel = None
        if active_attack and random.random() > 0.8:
            intel_mapping = {
                "synthetic_id_bustout": {"type": "darkweb", "msg": "Mass synthetic identities detected on darkweb forum", "sev": "high"},
                "synthetic_id": {"type": "darkweb", "msg": "Mass synthetic identities detected on darkweb forum", "sev": "high"},
                "deepfake_ato": {"type": "apt", "msg": "Deepfake voice cloning service spotted on Genesis Market", "sev": "critical"},
                "txn_fuzzing": {"type": "botnet", "msg": "High-velocity API probing detected from known botnet IPs", "sev": "medium"},
                "digital_arrest": {"type": "mule", "msg": "New 'Digital Arrest' scam call center identified in Node 4", "sev": "high"},
                "merchant_collusion": {"type": "magecart", "msg": "Anomalous merchant chargebacks detected in APAC", "sev": "medium"},
                "vishing": {"type": "apt", "msg": "Hyper-personalized vishing scripts linked to Lazarus Group", "sev": "critical"},
                "pig_butchering": {"type": "darkweb", "msg": "LLM-powered pig butchering toolkit circulating on Telegram", "sev": "high"},
                "agentic_hijack": {"type": "apt", "msg": "Prompt injection payloads targeting AP4M agents detected", "sev": "critical"},
                "model_poisoning": {"type": "insider", "msg": "Coordinated false-positive generation campaign detected", "sev": "high"},
                "supply_chain_bec": {"type": "apt", "msg": "Deepfake CFO voice used in wire fraud attempt", "sev": "critical"},
                "api_exploit": {"type": "botnet", "msg": "Race condition exploit targeting payment gateway APIs", "sev": "high"},
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
                    "message": f"Signatures matching {active_attack.replace('_', ' ').title()} detected",
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
                "shap_explanation": shap_explanation,
                # Battle Simulator Data
                "transaction_graph": battle_result["transaction_graph"] if battle_result else {"nodes": [], "edges": []},
                "adversarial_instances": battle_result["adversarial_instances"] if battle_result else [],
                "battle_phase": battle_result["phase"] if battle_result else "IDLE",
                "battle_tick": battle_result["tick"] if battle_result else 0,
                "detected_attack_type": battle_result["detected_attack_type"] if battle_result else None,
                "detection_confidence": battle_result["detection_confidence"] if battle_result else 0,
                "red_team_success_rate": battle_result["red_team_success_rate"] if battle_result else 0,
                "blue_team_sensitivity": battle_result["blue_team_sensitivity"] if battle_result else 0,
                "mutation_generation": battle_result["mutation_generation"] if battle_result else 0,
                "mutation_params": battle_result["mutation_params"] if battle_result else {},
                "live_blue_metrics": battle_result.get("live_blue_metrics") if battle_result else None,
                "mutation_cycle": battle_result.get("mutation_cycle", 0) if battle_result else 0,
            }
        }
        # Store bypass rate on app state for federated endpoint
        app.state._current_bypass_rate = bypass_rate
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
        "service": "vanguard-backend",
        "data_loaded": data_service.is_loaded,
        "transactions": len(data_service.transactions_df) if data_service.transactions_df is not None else 0,
    }

app.state.ws_manager = manager
