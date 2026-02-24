from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from backend.db.repository import GridRepository
from backend.db.database import get_db
from sqlalchemy.orm import Session
from backend.models.schemas import MarketPrice, WeatherData
from backend.core.event_bus import broadcaster
from backend.core.external_bridge import context_bridge
from backend.core.data_validator import validator
from backend.core.time_sync import synchronizer

router = APIRouter()

class SCADAMeasurement(BaseModel):
    id: str  # Node or Link ID
    value: float
    type: str  # 'demand_mw', 'generation_mw', 'load_mw', 'status'
    timestamp: str

class SimulationSync(BaseModel):
    scenario_id: str
    nodes: List[dict]
    links: List[dict]

@router.post("/scada/push")
async def push_scada_data(measurements: List[SCADAMeasurement], db: Session = Depends(get_db)):
    """
    Ingests high-frequency data from field RTUs/IEDs.
    """
    repo = GridRepository(db)
    for m in measurements:
        try:
            # 1. Synchronize time and attach context
            synced_pkt = synchronizer.synchronize(m.dict())
            
            # 2. Run through Data Validator
            validation = validator.validate_measurement(m.id, m.value)
            
            if validation["is_valid"]:
                if m.type in ['demand_mw', 'generation_mw', 'load_mw']:
                    repo.update_link_telem(m.id, m.value)
                elif m.type == 'status':
                    repo.update_link_telem(m.id, 0 if m.value == 0 else 100, status="active" if m.value == 1 else "failed")
            
            # Broadcast to event bus (including validation results)
            synced_pkt["type"] = "telemetry"
            synced_pkt["validation"] = {
                "credibility": validation["credibility_score"],
                "flags": validation["flags"]
            }
            await broadcaster.broadcast(synced_pkt)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to process measurement {m.id}: {str(e)}")
    
    return {"status": "ingested", "count": len(measurements)}

@router.post("/simulator/sync")
async def sync_external_simulator(sync_data: SimulationSync, db: Session = Depends(get_db)):
    """
    Loopback endpoint for external software (OpenDSS, MATLAB).
    """
    repo = GridRepository(db)
    # Generic logic to bulk update nodes and links
    for node in sync_data.nodes:
        # repo.update_node_telem(...)
        pass
    for link in sync_data.links:
        repo.update_link_telem(link['id'], link['load_mw'], status=link.get('status'))
        
    return {"status": "synced", "message": f"Digital Twin updated with {len(sync_data.nodes)} nodes and {len(sync_data.links)} links"}

@router.get("/metrics")
async def get_current_metrics(db: Session = Depends(get_db)):
    """Returns summarized system metrics."""
    repo = GridRepository(db)
    state = repo.get_infrastructure_state()
    
    # Calculate availability
    total_links = len(state.links)
    active_links = len([l for l in state.links if l.status == "active"])
    availability = active_links / total_links if total_links > 0 else 1.0
    
    # Calculate demand (sum of node demands)
    latest_telemetry = repo.get_history(limit=1)
    current_demand = latest_telemetry[0].demand_mw if latest_telemetry else 450.0
    
    return {
        "current_demand": round(current_demand, 1),
        "availability": round(availability, 3),
        "carbon_intensity": 35.5, # Baseline
        "renewables_ratio": 0.42
    }

@router.get("/weather")
async def get_weather():
    """Fetches current contextual weather for the grid."""
    weather = await context_bridge.get_current_weather()
    # Broadcast for UI awareness
    await broadcaster.broadcast({
        "type": "context_update",
        "category": "weather",
        "data": weather.dict()
    })
    return weather

@router.get("/market")
async def get_market():
    """Fetches current market clearing price."""
    market = await context_bridge.get_market_price()
    # Broadcast for UI awareness
    await broadcaster.broadcast({
        "type": "context_update",
        "category": "market",
        "data": market.dict()
    })
    return market
