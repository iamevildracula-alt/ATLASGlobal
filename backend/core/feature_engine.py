import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime

class PINNConstraintLayer:
    """
    Physics-Informed Neural Network (PINN) Pre-Processing Bounds.
    Ensures that raw feature vectors obey hard physical laws (Kirchhoff's, Thermal limits)
    before being passed to the deep learning Forecaster or Reinforcement Learning agents.
    """
    def __init__(self):
        # Physical Constants for a simulated AC Grid
        self.max_transformer_temp_c = 110.0
        self.base_frequency_hz = 50.0  # Or 60.0 depending on region
        
    def validate_and_clip(self, state_vector: Dict[str, float]) -> Dict[str, float]:
        """
        Enforce hard physical boundaries on the state vector.
        If a sensor reads a physical impossibility that passed L2 (unlikely, but possible),
        PINN bounds mathematically pull it back to the edge of reality.
        """
        corrected_vector = state_vector.copy()
        
        # 1. Thermal Physics Bound (No transformer stays operational above 120C without melting)
        if 'transformer_temp_c' in corrected_vector:
            temp = corrected_vector['transformer_temp_c']
            # If reading is absurdly high but slipped through, cap it to theoretical meltdown peak
            corrected_vector['transformer_temp_c'] = min(temp, self.max_transformer_temp_c * 1.5)
            
        # 2. Power Balance (Kirchhoff's Current Law proxy)
        # sum(Generation) must roughly equal sum(Load) + Losses. 
        # In a real PINN, this is a loss-function penalty. Here, it is a hard feature correction.
        total_gen = sum(v for k, v in corrected_vector.items() if 'gen_mw' in k)
        total_load = sum(v for k, v in corrected_vector.items() if 'load_mw' in k)
        
        # If the feature vector claims we are generating 100MW but consuming 500MW (without storage drain),
        # the state is physically unstable. We don't drop the packet, we flag the violation.
        power_delta = abs(total_gen - total_load)
        corrected_vector['pinn_balance_violation_mw'] = power_delta
        
        # 3. Frequency Bound (Grid collapses if frequency drops > 1-2Hz)
        if 'grid_frequency_hz' in corrected_vector:
            freq = corrected_vector['grid_frequency_hz']
            corrected_vector['grid_frequency_hz'] = max(45.0, min(55.0, freq)) # Hard physical clipping
            
        return corrected_vector

class TemporalEmbedder:
    """
    Translates raw timestamps into cyclical ML features (Sine/Cosine embeddings)
    so neural networks can naturally learn daily and seasonal load curves.
    """
    @staticmethod
    def embed(timestamp: datetime) -> Dict[str, float]:
        # Day of year (1-365)
        day_of_year = timestamp.timetuple().tm_yday
        # Minute of day (0-1439)
        minute_of_day = timestamp.hour * 60 + timestamp.minute
        
        # Sine/Cosine cyclical encoding
        return {
            'time_day_sin': np.sin(2 * np.pi * day_of_year / 365.25),
            'time_day_cos': np.cos(2 * np.pi * day_of_year / 365.25),
            'time_minute_sin': np.sin(2 * np.pi * minute_of_day / 1440),
            'time_minute_cos': np.cos(2 * np.pi * minute_of_day / 1440),
            'is_weekend': 1.0 if timestamp.weekday() >= 5 else 0.0
        }

class FeatureEngine:
    """
    L3 The Shield: Spatio-Temporal & PINN Feature Extraction.
    Transforms raw, L2-validated dictionaries into structured, purely numerical 
    NumPy-compatible state vectors ready for AI ingestion.
    """
    def __init__(self):
        self.pinn_layer = PINNConstraintLayer()

    def generate_state_vector(self, L2_validated_packet: Dict[str, Any], historical_window: Optional[List[Dict]] = None) -> Dict[str, float]:
        """
        Takes a clean packet from L2 and converts it into a machine-learning consumable state.
        """
        if not L2_validated_packet.get('is_verified', False):
            # If the data failed L2 Shield, we should technically not use it for AI training/forecasting.
            # In production, this might trigger a 'State Estimation' fallback routine.
            raise ValueError("Feature Engine cannot ingest unverified telemetry.")

        state_vector = {}
        
        # 1. Extract raw numerical values
        for key, value in L2_validated_packet.items():
            if isinstance(value, (int, float)) and key not in ['credibility_score']:
                state_vector[key] = float(value)
                
        # 2. Add Temporal Embeddings
        timestamp = L2_validated_packet.get('timestamp', datetime.utcnow())
        temporal_features = TemporalEmbedder.embed(timestamp)
        state_vector.update(temporal_features)
        
        # 3. Add Spatial/Topological Embeddings (if available in packet)
        # E.g., node centrality or electrical distance. 
        # For MVP, we pass through any pre-calculated spatial identifiers.
        
        # 4. Enforce Physical Laws (PINNs)
        state_vector = self.pinn_layer.validate_and_clip(state_vector)
        
        # 5. Append L2 Trust Metric
        state_vector['l2_credibility'] = L2_validated_packet.get('credibility_score', 1.0)
        
        return state_vector
