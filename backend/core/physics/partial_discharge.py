import random
import math
from typing import Dict, Any

class PartialDischargeSimulator:
    """
    Simulates the physics of Partial Discharge (PD) in high-voltage insulation.
    Models asset degradation (Health Index) and stochastic PD activity (pC).
    """

    @staticmethod
    def update_asset_health(asset: Any, load_factor: float, dt_hours: float = 1.0) -> None:
        """
        Updates the health index of an asset (Node or Link) based on thermal stress.
        
        Args:
            asset: GridLinkModel or GridNodeModel
            load_factor: Current load / Rated capacity (0.0 to 1.X)
            dt_hours: Time step in hours
        """
        # 1. Base Degradation (Calendar Aging)
        # Assume 40 year life = ~0.000003 health drop per hour
        base_rate = 0.000003 
        
        # 2. Thermal Acceleration (Arrhenius-like exponential stress)
        # If load > 80%, degradation accelerates significantly
        stress_factor = 1.0
        if load_factor > 0.8:
            stress_factor = math.exp(5.0 * (load_factor - 0.8)) # Exp growth
        
        degradation = base_rate * stress_factor * dt_hours
        
        # Apply degradation
        asset.health_index = max(0.0, asset.health_index - degradation)
        
        # 3. Simulate PD Activity based on new Health
        PartialDischargeSimulator._update_pd_activity(asset)

    @staticmethod
    def _update_pd_activity(asset: Any) -> None:
        """
        Stochastically updates PD activity (picoCoulombs) based on Health Index.
        PD typically exhibits intermittent spikes before failure.
        """
        # Threshold where PD starts becoming visible (e.g., Health < 0.9)
        if asset.health_index > 0.9:
            asset.pd_activity = max(0.0, asset.pd_activity * 0.9) # Decay to 0
            return

        # Base PD level increases as health drops
        # 1.0 - Health = Damage. 
        damage = 1.0 - asset.health_index
        base_pd = damage * 100.0 # e.g., 0.2 damage -> 20 pC baseline
        
        # Stochastic Spiking (Intermittency)
        # The worse the health, the more frequent/severe the spikes
        spike_prob = damage * 0.1 # 10% chance at full failure
        spike_magnitude = 0.0
        
        if random.random() < spike_prob:
            spike_magnitude = random.uniform(50, 500) * damage
            
        # Smoothing: New value is weighted avg of old + target
        target_pd = base_pd + spike_magnitude
        asset.pd_activity = (asset.pd_activity * 0.7) + (target_pd * 0.3)

    @staticmethod
    def get_failure_probability(asset: Any) -> float:
        """
        Calculates probability of immediate failure (next 24h) based on PD and Health.
        """
        # Critical PD Threshold (e.g., > 100 pC is widely considered warning, > 500 danger)
        pd_risk = 0.0
        if asset.pd_activity > 100:
            pd_risk = (asset.pd_activity - 100) / 1000.0
            
        # Health Risk
        health_risk = 0.0
        if asset.health_index < 0.2:
            health_risk = (0.2 - asset.health_index) * 5.0 # Max 1.0
            
        # Combined Risk (MAX)
        return min(1.0, max(pd_risk, health_risk))
