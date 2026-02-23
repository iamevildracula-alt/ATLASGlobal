from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum
from .infrastructure import GridNode, GridLink

class EnergyType(str, Enum):
    SOLAR = "solar"
    WIND = "wind"
    GRID = "grid"
    BATTERY = "battery"
    NUCLEAR = "nuclear"

class EnergySource(BaseModel):
    type: EnergyType
    capacity: float  # MW
    cost_per_mwh: float
    carbon_intensity: float # kgCO2/MWh
    availability: float = 1.0 # 0.0 to 1.0

class EnergyDemand(BaseModel):
    hour: int
    demand_mw: float

class MarketPrice(BaseModel):
    timestamp: str
    price_per_mwh: float
    currency: str = "USD"
    region: str = "GLOBAL"

class WeatherData(BaseModel):
    timestamp: str
    temperature: float  # Celsius
    wind_speed: float    # m/s
    irradiance: float    # W/m2
    condition: str       # 'sunny', 'cloudy', 'stormy', etc.

class InfrastructureState(BaseModel):
    sources: List[EnergySource]
    storage_capacity_mwh: float
    current_storage_mwh: float
    reliability_threshold: float = 0.99
    carbon_limit: Optional[float] = None
    nodes: List[GridNode] = []
    links: List[GridLink] = []

class ScenarioType(str, Enum):
    DEMAND_SPIKE = "demand_spike"
    SUPPLY_FAILURE = "supply_failure"
    PRICE_VOLATILITY = "price_volatility"
    STORAGE_DEGRADATION = "storage_degradation"
    NORMAL = "normal"

class Scenario(BaseModel):
    type: ScenarioType
    description: str
    impact_factor: float # e.g., 1.5 for 50% spike
    affected_source: Optional[EnergyType] = None

class TradeOff(BaseModel):
    aspect: str # Cost, Reliability, Carbon
    impact: str # "High", "Medium", "Low"
    description: str

class DecisionRank(BaseModel):
    option_name: str
    score: float
    cost_impact: float
    reliability_score: float
    risk_level: str
    carbon_impact: float
    reasoning: str
    trade_offs: List[TradeOff] = []

class DecisionOutput(BaseModel):
    summary: str
    recommended_action: str
    alternatives: List[DecisionRank]
    risks: List[str]
    assumptions: List[str]
    confidence_level: float
    next_steps: List[str]
    primary_factor: str # The main driver for this decision
    rationale: Optional[str] = None # Natural language explanation of physics/safety factors
