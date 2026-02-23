from fastapi import APIRouter, Depends, HTTPException
from ..models.schemas import DecisionOutput, Scenario, InfrastructureState
from ..core.engine import DecisionEngine
from ..db.database import get_db
from ..db.repository import GridRepository
from sqlalchemy.orm import Session
import random

router = APIRouter()

@router.post("/run", response_model=DecisionOutput)
async def run_decision(scenario: Scenario, db: Session = Depends(get_db)):
    repo = GridRepository(db)
    
    # Get current real state from DB
    state = repo.get_infrastructure_state()
    
    # Fetch current demand from latest telemetry (ingested via real-world feed)
    latest_telemetry = repo.get_history(limit=1)
    if latest_telemetry:
        demand = latest_telemetry[0].demand_mw
    else:
        # Fallback for fresh DBs before ingestion
        demand = 400.0 + random.uniform(-10, 10)
    
    # Fetch active policy from DB
    policy_model = repo.get_active_policy()
    from ..models.policy import PolicyConstraints
    policy = PolicyConstraints(
        max_cost_per_mwh=policy_model.max_cost_per_mwh if policy_model else 100.0,
        max_carbon_per_mwh=policy_model.max_carbon_per_mwh if policy_model else 0.5,
        min_reliability_score=policy_model.min_reliability_score if policy_model else 0.99,
        risk_tolerance=policy_model.risk_tolerance if policy_model else "neutral"
    )

    # The Engine now handles internal errors and returns a fallback DecisionOutput
    decision = DecisionEngine.evaluate_options(state, scenario, demand, policy)
    return decision

@router.get("/state", response_model=InfrastructureState)
async def get_current_state(db: Session = Depends(get_db)):
    repo = GridRepository(db)
    return repo.get_infrastructure_state()
