import numpy as np
from typing import List, Dict, Any, Optional
from backend.models.schemas import WeatherData, MarketPrice

class FeatureEngine:
    def __init__(self):
        # Normalization scales (Conceptual - based on grid specs)
        self.scales = {
            "demand_mw": 1000.0,
            "generation_mw": 1200.0,
            "price": 200.0,
            "irradiance": 1000.0,
            "temp": 50.0
        }
        
    def generate_state_vector(self, 
                             telemetry: List[Dict[str, Any]], 
                             weather: WeatherData, 
                             market: MarketPrice) -> np.ndarray:
        """
        Synthesizes a cross-domain state vector for the forecasting engine.
        Structure: [Demand_Norm, Weather_Norms..., Market_Norm]
        """
        # 1. Aggregate Telemetry (Simple mean for now)
        demands = [t['value'] for t in telemetry if t.get('data_type') == 'demand_mw']
        avg_demand = np.mean(demands) if demands else 0.0
        
        # 2. Physics-Aware Bound Enforcement
        # Ensure demand doesn't exceed theoretical system limit (e.g., 2000 MW)
        avg_demand = min(max(0, avg_demand), 2000.0)
        
        # 3. Normalization
        vec = [
            avg_demand / self.scales["demand_mw"],
            weather.temperature / self.scales["temp"],
            weather.irradiance / self.scales["irradiance"],
            weather.wind_speed / 25.0, # Beaufort scale approx
            market.price_per_mwh / self.scales["price"]
        ]
        
        return np.array(vec, dtype=np.float32)

    def get_spatio_temporal_tensor(self, history: List[np.ndarray]) -> np.ndarray:
        """
        Prepares a sequence tensor for recurrent/Bayesian models (LSTM/PINN).
        """
        if not history:
            return np.zeros((1, 1, 5))
        return np.expand_dims(np.stack(history), axis=0)

# Global feature engine instance
feature_engine = FeatureEngine()
