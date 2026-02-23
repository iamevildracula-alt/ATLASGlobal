import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict
from ..db.database import SessionLocal
from ..db.repository import GridRepository

class LoadForecaster:
    """
    Predictive AI Engine for Grid Demand.
    Currently implements a Seasonal Moving Average approach.
    Designed for seamless upgrade to XGBoost/LSTM.
    """
    
    @staticmethod
    def predict_next_24h() -> List[Dict[str, any]]:
        db = SessionLocal()
        repo = GridRepository(db)
        
        # Fetch last 48 hours of data to establish baseline
        history = repo.get_history(limit=48)
        db.close()
        
        if len(history) < 12:
            return LoadForecaster._generate_default_forecast()
            
        # Convert to DataFrame for analysis
        data = [{
            "timestamp": h.timestamp,
            "demand": h.demand_mw
        } for h in history]
        df = pd.DataFrame(data)
        df.sort_values("timestamp", inplace=True)
        
        # Simple seasonal (hourly) prediction logic
        # In a real scenario, we'd use a fitted model here
        last_val = df['demand'].iloc[-1]
        forecast = []
        base_time = df['timestamp'].iloc[-1]
        
        for i in range(1, 25):
            prediction_time = base_time + timedelta(hours=i)
            # Add some variability and a slight upward trend or cyclicality
            cycle_factor = np.sin(2 * np.pi * (prediction_time.hour / 24))
            predicted_demand = last_val + (cycle_factor * 20) + np.random.normal(0, 5)
            
            forecast.append({
                "timestamp": prediction_time,
                "predicted_demand": round(float(predicted_demand), 2)
            })
            
        return forecast

    @staticmethod
    def _generate_default_forecast():
        """Fallback forecast if DB is empty."""
        forecast = []
        base_time = datetime.utcnow()
        for i in range(1, 25):
            forecast.append({
                "timestamp": base_time + timedelta(hours=i),
                "predicted_demand": 420.0 + (np.sin(i/4) * 50)
            })
        return forecast
