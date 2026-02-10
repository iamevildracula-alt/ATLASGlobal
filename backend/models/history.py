from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TimeSeriesPoint(BaseModel):
    timestamp: datetime
    demand_mw: float
    supply_total_mw: float
    carbon_intensity: float
    reliability_score: float

class HistoryResponse(BaseModel):
    start_date: datetime
    end_date: datetime
    data: List[TimeSeriesPoint]
