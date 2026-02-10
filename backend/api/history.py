from fastapi import APIRouter
from ..models.history import HistoryResponse, TimeSeriesPoint
from datetime import datetime, timedelta
import random

router = APIRouter()

def generate_mock_history(days: int = 30) -> List[TimeSeriesPoint]:
    data = []
    base_time = datetime.now() - timedelta(days=days)
    for i in range(days * 24): # Hourly data
        t = base_time + timedelta(hours=i)
        
        # Simple seasonality
        hour = t.hour
        demand_base = 300 + (100 * (1 if 9 <= hour <= 18 else 0.5))
        demand = demand_base + random.uniform(-20, 20)
        
        supply = demand * 1.05 # Margin
        carbon = 40 + (20 * (1 if 9 <= hour <= 16 else 0)) # Solar reduces carbon? No, solar reduces intensity. Let's say random.
        
        data.append(TimeSeriesPoint(
            timestamp=t,
            demand_mw=round(demand, 1),
            supply_total_mw=round(supply, 1),
            carbon_intensity=round(carbon, 1),
            reliability_score=round(random.uniform(0.95, 1.0), 3)
        ))
    return data

MOCK_HISTORY = generate_mock_history()

@router.get("/series", response_model=HistoryResponse)
async def get_history(days: int = 30):
    # Slice appropriate range
    # For now just return full mock
    return HistoryResponse(
        start_date=MOCK_HISTORY[0].timestamp,
        end_date=MOCK_HISTORY[-1].timestamp,
        data=MOCK_HISTORY
    )
