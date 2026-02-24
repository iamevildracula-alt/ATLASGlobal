import numpy as np
from typing import Dict, Any, Tuple
from datetime import datetime

class AdversarialFilter:
    """
    Detects physically impossible data patterns indicative of cyber spoofing
    or critical sensor failure.
    """
    def __init__(self, max_rate_of_change_mw_per_sec: float = 500.0):
        self.max_roc = max_rate_of_change_mw_per_sec
        self.last_valid_state: Dict[str, float] = {}
        self.last_timestamp: datetime = None

    def check_payload(self, asset_id: str, new_value_mw: float, timestamp: datetime) -> Tuple[bool, str]:
        if asset_id not in self.last_valid_state or not self.last_timestamp:
            self.last_valid_state[asset_id] = new_value_mw
            self.last_timestamp = timestamp
            return True, "Baseline established"

        # Calculate Rate of Change (RoC)
        dt_seconds = (timestamp - self.last_timestamp).total_seconds()
        if dt_seconds <= 0:
            return False, "Timestamp anomaly: non-positive delta"

        delta_mw = abs(new_value_mw - self.last_valid_state[asset_id])
        roc = delta_mw / dt_seconds

        if roc > self.max_roc:
            return False, f"Adversarial alert: RoC ({roc:.2f} MW/s) exceeds physical limits"

        # Update state if valid
        self.last_valid_state[asset_id] = new_value_mw
        self.last_timestamp = timestamp
        return True, "Physically feasible"


class DriftMonitor:
    """
    Tracks distribution shifts in telemetry streams to detect insidious
    sensor degradation or slow-burn data poisoning.
    (Simplified KS-Test / Distribution tracking for MVP)
    """
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.history: Dict[str, list] = {}
        self.baseline_mean: Dict[str, float] = {}
        self.baseline_std: Dict[str, float] = {}

    def update_and_check(self, asset_id: str, value: float) -> Tuple[bool, float]:
        if asset_id not in self.history:
            self.history[asset_id] = []
            
        self.history[asset_id].append(value)
        
        # Maintain sliding window
        if len(self.history[asset_id]) > self.window_size:
            self.history[asset_id].pop(0)

        # Require enough data to establish a baseline
        if len(self.history[asset_id]) < self.window_size // 2:
            return True, 0.0 # No drift detected yet, not enough data

        # Calculate current statistics
        current_data = np.array(self.history[asset_id])
        current_mean = np.mean(current_data)
        current_std = np.std(current_data)

        # Baseline establishment (simplified: first full window becomes baseline)
        if asset_id not in self.baseline_mean:
            if len(self.history[asset_id]) == self.window_size:
                self.baseline_mean[asset_id] = current_mean
                self.baseline_std[asset_id] = current_std
                return True, 0.0
            else:
                return True, 0.0

        # Drift calculation (Z-score shift approximation)
        # In a full Sentient Grid, this uses Kolmogorov-Smirnov (KS) Test or PSI
        b_mean = self.baseline_mean[asset_id]
        b_std = max(self.baseline_std[asset_id], 0.001) # prevent div by zero
        
        shift_magnitude = abs(current_mean - b_mean) / b_std
        
        # If mean shifts by more than 3 standard deviations, flag as drifted
        is_stable = shift_magnitude < 3.0
        
        return is_stable, shift_magnitude

class DataValidator:
    """
    L2 The Shield: Decoupled Data Validation Pipeline
    """
    def __init__(self):
        self.adversarial_filter = AdversarialFilter()
        self.drift_monitor = DriftMonitor()

    def process_telemetry(self, raw_telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates incoming data packet. Completely decoupled from ingestion network layer.
        Returns a processed packet enriched with a 'credibility_score'.
        """
        asset_id = raw_telemetry.get("asset_id", "unknown")
        value = raw_telemetry.get("value_mw", 0.0)
        timestamp = raw_telemetry.get("timestamp", datetime.utcnow())

        processed_packet = raw_telemetry.copy()
        credibility_score = 1.0
        flags = []

        # 1. Adversarial Robustness Check
        is_physically_valid, adv_reason = self.adversarial_filter.check_payload(asset_id, value, timestamp)
        if not is_physically_valid:
            credibility_score *= 0.1 # Severe penalty for physics violation
            flags.append(adv_reason)

        # 2. Drift Monitoring Check
        is_stable, shift_mag = self.drift_monitor.update_and_check(asset_id, value)
        if not is_stable:
             # Gradual penalty based on magnitude of shift
             drift_penalty = max(0.5, 1.0 - (shift_mag * 0.1)) 
             credibility_score *= drift_penalty
             flags.append(f"Distribution drift detected (Magnitude: {shift_mag:.2f} std devs)")

        # 3. Compile Validated Payload
        processed_packet["credibility_score"] = max(0.0, min(1.0, credibility_score))
        processed_packet["is_verified"] = credibility_score >= 0.8
        processed_packet["shield_flags"] = flags
        
        return processed_packet

    def validate_measurement(self, asset_id: str, value: float) -> Dict[str, Any]:
        """ Wrapper for ingestion/main loops """
        packet = self.process_telemetry({
            "asset_id": asset_id,
            "value_mw": value,
            "timestamp": datetime.utcnow()
        })
        return {
            "is_valid": packet["is_verified"],
            "credibility_score": packet["credibility_score"],
            "flags": packet["shield_flags"]
        }

# Global instance for backend routes
validator = DataValidator()
