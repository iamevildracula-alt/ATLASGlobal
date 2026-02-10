from pydantic import BaseModel, Field
from typing import Optional

class PolicyConstraints(BaseModel):
    max_cost_per_mwh: float = Field(default=100.0, ge=0)
    max_carbon_per_mwh: float = Field(default=0.5, ge=0) # tons/MWh
    min_reliability_score: float = Field(default=0.99, ge=0, le=1.0)
    risk_tolerance: str = Field(default="neutral", pattern="^(averse|neutral|seeking)$")
