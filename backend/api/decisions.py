from fastapi import APIRouter, HTTPException
from ..models.schemas import DecisionOutput, Scenario, InfrastructureState
from ..core.engine import DecisionEngine
from ..db.mock_data import MockDataService

router = APIRouter()

@router.post("/run", response_model=DecisionOutput)
async def run_decision(scenario: Scenario, state: InfrastructureState = None):
    # Ensure legitimate mock state if none provided
    if state is None:
        state = MockDataService.get_default_state()
    
    # Use mock demand if not available in state (simplified for v1)
    # In a real app, demand would be part of the request context or live telemetry
    demand = 400.0 
    
    # Fetch current policy
    from .policy import get_policy
    policy = await get_policy()

    # The Engine now handles internal errors and returns a fallback DecisionOutput
    # so we can directly return its result.
    decision = DecisionEngine.evaluate_options(state, scenario, demand, policy)
    return decision

@router.get("/default-state", response_model=InfrastructureState)
async def get_default_state():
    return MockDataService.get_default_state()
