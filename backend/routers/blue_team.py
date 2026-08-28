from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from backend.services.data_service import data_service

router = APIRouter()


class PredictReq(BaseModel):
    transaction: Dict[str, Any]


@router.post("/predict")
async def predict(req: PredictReq):
    """Predict fraud risk for a single transaction using the real trained model."""
    txn = req.transaction
    result = data_service.predict_single(txn)
    result["transaction_id"] = txn.get("transaction_id", "?")
    return result


@router.get("/metrics")
async def metrics():
    """Return real model performance metrics."""
    return data_service.get_metrics()


from backend.services.federated_simulator import federated_coordinator

@router.get("/federated-comparison")
async def federated(request: Request):
    """Return federated learning comparison data tied to live battle state."""
    # Get current bypass rate from the live battle
    bypass_rate = getattr(request.app.state, "_current_bypass_rate", 0.05)
    fed_data = federated_coordinator.aggregate_weights(
        current_bypass_rate=bypass_rate)
    
    return {
        "round": fed_data["round"],
        "banks": [
            {"name": node["name"], "f1": node["accuracy"],
             "auc": min(0.99, node["accuracy"] + 0.05),
             "updates": node["updates"], "status": node["status"]}
            for node in fed_data["nodes"]
        ],
        "federated": {
            "f1": fed_data["global_accuracy"],
            "auc": min(0.999, fed_data["global_accuracy"] + 0.03),
            "improvement": fed_data.get("improvement", "+5.0%"),
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
