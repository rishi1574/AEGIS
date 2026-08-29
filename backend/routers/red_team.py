from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from backend.services.data_service import data_service

router = APIRouter()

ATTACKS = [
    {"id": "synthetic_id_bustout", "name": "Synthetic ID Bust-Out", "layer": "identity", "risk": "critical",
     "description": "GenAI-created identities nurtured for months, then simultaneous credit bust-out"},
    {"id": "deepfake_ato", "name": "Deepfake Voice/Video ATO", "layer": "identity", "risk": "critical",
     "description": "Voice-cloned deepfake bypasses KYC; rapid fund drain to mule chain"},
    {"id": "adversarial_document", "name": "Document Injection", "layer": "identity", "risk": "high",
     "description": "Pixel-perfect forged invoices for trade-based money laundering"},
    {"id": "txn_fuzzing", "name": "Adversarial Txn Fuzzing", "layer": "network", "risk": "critical",
     "description": "AI probes model decision boundary with ₹1 mutations to reverse-engineer classifier"},
    {"id": "api_exploit", "name": "API Exploit & Replay", "layer": "network", "risk": "high",
     "description": "Double-spend via concurrent API calls exploiting idempotency gaps"},
    {"id": "merchant_collusion", "name": "Merchant Collusion", "layer": "network", "risk": "high",
     "description": "Fake merchant network processes stolen cards with GenAI-generated legitimacy"},
    {"id": "vishing", "name": "Hyper-Personalized Vishing", "layer": "human", "risk": "critical",
     "description": "GenAI crafts contextual scripts using scraped delivery data + deepfake voice"},
    {"id": "pig_butchering", "name": "AI Pig Butchering", "layer": "human", "risk": "high",
     "description": "LLM chatbots maintain 10K+ simultaneous trust relationships for investment fraud"},
    {"id": "digital_arrest", "name": "Digital Arrest Scam", "layer": "human", "risk": "high",
     "description": "Deepfake video impersonating law enforcement; victim transfers life savings"},
    {"id": "agentic_hijack", "name": "Agentic Commerce Hijack", "layer": "emerging", "risk": "critical",
     "description": "Prompt injection in product descriptions hijacks AP4M shopping agents"},
    {"id": "model_poisoning", "name": "Model Poisoning", "layer": "emerging", "risk": "critical",
     "description": "Bait transactions designed to create false positives on competitor merchants"},
    {"id": "supply_chain_bec", "name": "Supply Chain BEC", "layer": "emerging", "risk": "high",
     "description": "GenAI-forged invoices + deepfake exec voice redirects B2B vendor payments"},
    {"id": "surrogate_evasion", "name": "Surrogate Evasion", "layer": "emerging", "risk": "critical",
     "description": "Shadow neural network calculates FGSM gradients to subtly alter transaction amounts"},
    {"id": "mislead_shap", "name": "MISLEAD SHAP", "layer": "emerging", "risk": "critical",
     "description": "Tricks Tree Explainers by artificially zeroing out high-importance features"},
    {"id": "tabular_epsilon", "name": "Tabular Epsilon", "layer": "emerging", "risk": "high",
     "description": "Constrained optimization pushing values to classification threshold boundaries"},
    {"id": "ctgan_mimicry", "name": "CTGAN Mimicry", "layer": "identity", "risk": "critical",
     "description": "Uses Conditional Tabular GANs to perfectly match legitimate covariant distributions"},
    {"id": "label_poisoning", "name": "Label Poisoning", "layer": "emerging", "risk": "critical",
     "description": "Generates borderline transactions to poison the Blue Team retraining loop"},
    {"id": "concept_drift", "name": "Concept Drift", "layer": "emerging", "risk": "critical",
     "description": "Mathematically shifts time-of-day distributions to induce Covariant Shift"},
    {"id": "graph_poisoning", "name": "Graph Poisoning", "layer": "network", "risk": "high",
     "description": "Sybil nodes inflate PageRank via micro-transactions before a bust-out"},
    {"id": "temporal_fuzzing", "name": "Temporal Fuzzing", "layer": "network", "risk": "critical",
     "description": "Evades LSTM anomaly detection using inverted Poisson distributions"},
    {"id": "marl_collusion", "name": "MARL Collusion", "layer": "network", "risk": "critical",
     "description": "PPO agents clipping Z-scores to stay below anomaly detection across accounts"},
    {"id": "boundary_probe", "name": "Boundary Probing", "layer": "network", "risk": "high",
     "description": "Tightly clusters transactions in the 0.49 probability margin to probe boundaries"},
    {"id": "backdoor_injection", "name": "Backdoor Injection", "layer": "emerging", "risk": "critical",
     "description": "Plants tabular triggers (e.g., ₹404.04) as backdoors into the Blue Team model"},
    {"id": "nlp_payload", "name": "NLP Payload Evasion", "layer": "emerging", "risk": "high",
     "description": "Generates highly optimized semantic MCC descriptions to bypass text scoring"},
    {"id": "ensemble_evasion", "name": "Ensemble Evasion", "layer": "emerging", "risk": "critical",
     "description": "Exploits linear weight equations of Meta-Learners across models"},
]


class LaunchReq(BaseModel):
    attack_type: str
    params: Optional[Dict[str, Any]] = None


@router.post("/launch")
async def launch(req: LaunchReq):
    # Attack state is managed per-session via WebSocket; this just returns stats
    taxonomy = data_service.get_attack_taxonomy()
    attack_stats = taxonomy.get(req.attack_type, {})
    
    return {
        "campaign_id": f"CAMP_{req.attack_type.upper()[:8]}",
        "status": "running",
        "attack_type": req.attack_type,
        "message": f"Launched {req.attack_type} campaign",
        "historical_bypass_rate": attack_stats.get("final_bypass_rate", 0),
        "historical_count": attack_stats.get("total_count", 0),
    }


@router.post("/stop")
async def stop():
    # Attack state is managed per-session via WebSocket
    return {"status": "stopped", "attack_type": None}


@router.get("/attacks")
async def list_attacks():
    # Enrich with real taxonomy data
    taxonomy = data_service.get_attack_taxonomy()
    enriched = []
    for atk in ATTACKS:
        atk_copy = dict(atk)
        stats = taxonomy.get(atk["id"], {})
        atk_copy["total_simulated"] = stats.get("total_count", 0)
        atk_copy["bypass_rate"] = stats.get("final_bypass_rate", 0)
        enriched.append(atk_copy)
    return {"attacks": enriched}


@router.get("/status/{cid}")
async def status(cid: str):
    taxonomy = data_service.get_attack_taxonomy()
    return {
        "campaign_id": cid,
        "status": "completed",
        "attack_taxonomy": taxonomy,
    }


@router.get("/taxonomy")
async def taxonomy():
    """Return full attack taxonomy with statistics."""
    return data_service.get_attack_taxonomy()
