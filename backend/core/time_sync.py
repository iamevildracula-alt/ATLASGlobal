import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional

class TimeSynchronizer:
    def __init__(self, resolution_ms: int = 1000):
        """
        Initializes the synchronizer with a temporal resolution grid.
        Default is 1000ms (1 second). All incoming pulses within this grid 
        will be fused with the same contextual state.
        """
        self.resolution_ms = resolution_ms
        self.latest_context: Dict[str, Any] = {
            "weather": None,
            "market": None
        }
        
    def update_context(self, category: str, data: Any):
        """
        Updates the global continuous context (Weather, Market).
        """
        self.latest_context[category] = data

    def synchronize(self, measurement: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aligns a raw measurement to the grid's temporal grid and attaches 
        the latest global context (weather, market) to form a unified telemetry packet.
        """
        # Parse or generate timestamp
        ts_str = measurement.get("timestamp")
        if ts_str:
            try:
                # Try parsing standard ISO format
                if ts_str.endswith('Z'):
                    dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                else:
                    dt = datetime.fromisoformat(ts_str)
                ts_ms = int(dt.timestamp() * 1000)
            except ValueError:
                ts_ms = int(time.time() * 1000)
        else:
            ts_ms = int(time.time() * 1000)
            
        # Snap to grid resolution (e.g., nearest second)
        synced_ts_ms = (ts_ms // self.resolution_ms) * self.resolution_ms
        sycned_dt = datetime.fromtimestamp(synced_ts_ms / 1000.0, tz=timezone.utc)
        
        # Attach context to create a "State Vector Frame"
        return {
            "id": measurement.get("id"),
            "value": measurement.get("value"),
            "data_type": measurement.get("type", measurement.get("data_type")),
            "original_timestamp": ts_str,
            "synced_timestamp": sycned_dt.isoformat().replace('+00:00', 'Z'),
            "context": {
                "weather": self.latest_context["weather"],
                "market": self.latest_context["market"]
            }
        }

# Global synchronizer instance
synchronizer = TimeSynchronizer()
