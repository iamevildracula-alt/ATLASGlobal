from fastapi import APIRouter
from ..models.schemas import InfrastructureState
from ..db.mock_data import MockDataService

router = APIRouter()

@router.post("/")
async def ingest_data(state: InfrastructureState):
    # In a real app, this would save to DB. For v0, we just return success.
    return {"status": "success", "received": state.dict()}

@router.get("/metrics")
async def get_latest_metrics():
    # Mock current metrics
    return {
        "current_demand": 380.0,
        "availability": 0.95,
        "active_sources": 5
    }
