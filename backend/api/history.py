from fastapi import APIRouter, Depends
from ..models.history import HistoryResponse, TimeSeriesPoint
from ..db.database import get_db
from ..db.repository import GridRepository
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

router = APIRouter()

@router.get("/series", response_model=HistoryResponse)
async def get_history(limit: int = 100, db: Session = Depends(get_db)):
    repo = GridRepository(db)
    history_models = repo.get_history(limit=limit)
    
    if not history_models:
        return HistoryResponse(
            start_date=datetime.now(),
            end_date=datetime.now(),
            data=[]
        )
    
    # Map DB models to Schema points
    points = [
        TimeSeriesPoint(
            timestamp=m.timestamp,
            demand_mw=m.demand_mw,
            supply_total_mw=m.supply_mw,
            carbon_intensity=m.carbon_intensity,
            reliability_score=m.reliability_score
        ) for m in history_models
    ]
    
    # Sort for chrono order (DB returns desc)
    points.sort(key=lambda x: x.timestamp)
    
    return HistoryResponse(
        start_date=points[0].timestamp,
        end_date=points[-1].timestamp,
        data=points
    )
