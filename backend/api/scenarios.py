from fastapi import APIRouter
from ..models.schemas import Scenario, ScenarioType
from typing import List

router = APIRouter()

@router.get("/", response_model=List[Scenario])
async def get_scenarios():
    return [
        Scenario(type=ScenarioType.NORMAL, description="Typical operating conditions", impact_factor=1.0),
        Scenario(type=ScenarioType.DEMAND_SPIKE, description="Extreme heatwave causing 40% demand spike", impact_factor=1.4),
        Scenario(type=ScenarioType.SUPPLY_FAILURE, description="Grid interconnect failure (30% loss)", impact_factor=0.3, affected_source="grid"),
        Scenario(type=ScenarioType.SUPPLY_FAILURE, description="Solar eclipse / cloud cover (80% loss)", impact_factor=0.8, affected_source="solar"),
    ]
