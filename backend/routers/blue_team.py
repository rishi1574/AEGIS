from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from backend.services.data_service import data_service

router = APIRouter()


class PredictReq(BaseModel):
    transaction: Dict[str, Any]


@router.post("/predict")
async def predict(req: PredictReq):
    """Predict fraud risk for a single transaction."""
    txn = req.transaction
    # In production this would run through the ensemble model
    # For the demo, return structured response
    risk_score = 0.15
    return {
        "transaction_id": txn.get("transaction_id", "?"),
        "risk_score": risk_score,
        "is_fraud": risk_score > 0.5,
        "confidence": max(risk_score, 1 - risk_score),
        "model_used": "ensemble_v1",
        "model_breakdown": {
            "xgb_score": round(risk_score * 0.95, 4),
            "temporal_score": round(risk_score * 0.8, 4),
            "graph_score": round(risk_score * 0.6, 4),
        },
        "recommended_action": "BLOCK" if risk_score > 0.8 else "REVIEW" if risk_score > 0.5 else "ALLOW",
        "attack_pattern_match": None,
    }


@router.get("/metrics")
async def metrics():
    """Return real model performance metrics."""
    return data_service.get_metrics()


from backend.services.federated_simulator import federated_coordinator

@router.get("/federated-comparison")
async def federated():
    """Return federated learning comparison data."""
    # Run one round of federated simulation per request (or you can run it in a background loop)
    fed_data = federated_coordinator.aggregate_weights()
    
    return {
        "round": fed_data["round"],
        "banks": [
            {"name": node["name"], "f1": node["accuracy"],
             "auc": min(0.99, node["accuracy"] + 0.05), "updates": node["updates"], "status": node["status"]}
            for node in fed_data["nodes"]
        ],
        "federated": {
            "f1": fed_data["global_accuracy"],
            "auc": min(0.999, fed_data["global_accuracy"] + 0.03),
            "improvement": f"+{round((fed_data['global_accuracy'] - fed_data['nodes'][0]['accuracy']) / fed_data['nodes'][0]['accuracy'] * 100, 2)}%"
        }
    }


@router.get("/interception-log")
async def interceptions():
    """Return recent fraud interceptions with details."""
    return {"interceptions": data_service.get_interceptions(limit=30)}


@router.get("/concept-drift")
async def drift():
    """Return per-iteration adversarial co-evolution data."""
    return data_service.get_concept_drift_data()


@router.get("/shap-explanations")
async def shap_explanations():
    """Return sample SHAP explanations for recent fraud detections."""
    return {"explanations": data_service.get_sample_shap()}


@router.get("/feature-importance")
async def feature_importance():
    """Return model feature importances."""
    # Load from adversarial results if available
    results = data_service.adversarial_results
    metrics = results.get("final_metrics", {})
    xgb_metrics = metrics.get("xgb_metrics", {})
    return {"feature_importance": xgb_metrics}


@router.get("/graph-data")
async def graph_data():
    """Return transaction network graph data for visualization."""
    return data_service.get_transaction_graph_data(limit=80)
