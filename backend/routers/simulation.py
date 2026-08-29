from fastapi import APIRouter
from pydantic import BaseModel
from backend.services.data_service import data_service

router = APIRouter()


class SimConfig(BaseModel):
    num_accounts: int = 10000
    num_merchants: int = 500
    time_horizon_days: int = 90
    fraud_ratio: float = 0.02


@router.post("/start")
async def start(cfg: SimConfig):
    """Reset the live battle simulation state."""
    # Per-session attack state is managed via WebSocket connections
    return {
        "status": "started",
        "message": "Simulation state reset. Launch an attack to begin the battle.",
        "config": cfg.model_dump(),
        "data_loaded": data_service.is_loaded,
        "transactions_available": len(data_service.transactions_df) if data_service.transactions_df is not None else 0,
    }


@router.get("/status")
async def status():
    iterations = data_service.adversarial_results.get("iterations", [])
    total_txns = len(data_service.transactions_df) if data_service.transactions_df is not None else 0

    return {
        "status": "completed" if data_service.is_loaded else "idle",
        "progress": 1.0 if data_service.is_loaded else 0.0,
        "transactions_generated": total_txns,
        "adversarial_iteration": len(iterations),
    }


@router.get("/system-hardness")
async def hardness():
    """Return system hardness from real adversarial loop data."""
    return data_service.get_system_hardness()
