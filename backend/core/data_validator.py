import numpy as np
from scipy import stats
from typing import List, Dict, Any, Optional
import time

class DataValidator:
    def __init__(self, history_window: int = 100):
        self.history_window = history_window
        self.sensor_history: Dict[str, List[float]] = {}
        
    def validate_measurement(self, sensor_id: str, value: float) -> Dict[str, Any]:
        """
        Validates a single measurement and returns its credibility profile.
        """
        if sensor_id not in self.sensor_history:
            self.sensor_history[sensor_id] = []
            
        history = self.sensor_history[sensor_id]
        
        # 1. Noise Suppression (Simple Moving Average / Jitter check)
        # For now, we just compare against the last value
        jitter = 0.0
        if history:
            jitter = abs(value - history[-1])
            
        # 2. Outlier Detection (Z-Score)
        is_outlier = False
        z_score = 0.0
        if len(history) > 30:
            mean = np.mean(history)
            std = np.std(history)
            if std > 0:
                z_score = abs(value - mean) / std
                if z_score > 3.0: # 3-sigma rule
                    is_outlier = True

        # 3. Drift Monitoring (KS-Test)
        # We compare the last 50 samples against the previous 50
        drift_p_value = 1.0
        has_drifted = False
        if len(history) >= self.history_window:
            window_size = self.history_window // 2
            group_a = history[-self.history_window : -window_size]
            group_b = history[-window_size:]
            
            # Perform KS Test
            _, drift_p_value = stats.ks_2samp(group_a, group_b)
            if drift_p_value < 0.05: # Statistical significance
                has_drifted = True

        # 4. Credibility Scoring
        credibility = 1.0
        if is_outlier: credibility -= 0.5
        if has_drifted: credibility -= 0.3
        if jitter > 100.0: credibility -= 0.2 # Arbitrary threshold for demo
        
        # Update history
        history.append(value)
        if len(history) > self.history_window * 2:
            self.sensor_history[sensor_id] = history[-self.history_window * 2:]
            
        return {
            "sensor_id": sensor_id,
            "value": value,
            "is_valid": credibility > 0.4,
            "credibility_score": max(0.0, credibility),
            "flags": {
                "outlier": is_outlier,
                "drift_detected": has_drifted,
                "drift_p_value": drift_p_value,
                "z_score": z_score
            }
        }

# Global validator instance
validator = DataValidator()
