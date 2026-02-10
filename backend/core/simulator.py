from ..models.schemas import InfrastructureState, Scenario, ScenarioType, EnergyType
from typing import Dict, Any

class EDLSimulator:
    @staticmethod
    def simulate(state: InfrastructureState, scenario: Scenario, demand_mw: float) -> Dict[str, Any]:
        projected_supply = 0.0
        projected_cost = 0.0
        projected_carbon = 0.0
        
        # Safety check: Ensure positive demand
        actual_demand = max(0.0, demand_mw)
        
        # Apply scenario impacts
        modified_sources = []
        for source in state.sources:
            # Clamp availability between 0 and 1
            available_factor = max(0.0, min(1.0, source.availability))
            available_capacity = source.capacity * available_factor
            
            if scenario.type == ScenarioType.SUPPLY_FAILURE and scenario.affected_source == source.type:
                # Ensure impact factor is reasonable (0 to 1)
                safe_impact = max(0.0, min(1.0, scenario.impact_factor))
                available_capacity *= (1.0 - safe_impact)
            
            modified_sources.append({
                "type": source.type,
                "available": max(0.0, available_capacity), # Ensure non-negative
                "cost": source.cost_per_mwh,
                "carbon": source.carbon_intensity
            })

        # Apply demand spike
        if scenario.type == ScenarioType.DEMAND_SPIKE:
            actual_demand *= max(1.0, scenario.impact_factor) # Spike should generally increase demand

        # Merit Order Dispatch
        # Sort sources by cost (Cheapest first)
        modified_sources.sort(key=lambda x: x["cost"])
        
        remaining_demand = actual_demand
        for s in modified_sources:
            dispatch = min(remaining_demand, s["available"])
            projected_supply += dispatch
            projected_cost += dispatch * s["cost"]
            projected_carbon += dispatch * s["carbon"]
            remaining_demand -= dispatch
            if remaining_demand <= 0:
                break
        
        # Storage usage if needed
        # Only use storage if there is demand left
        if remaining_demand > 0 and state.current_storage_mwh > 0:
            storage_dispatch = min(remaining_demand, state.current_storage_mwh)
            projected_supply += storage_dispatch
            # Assume storage has a nominal cost (e.g., degradation cost) and 0 direect carbon (assuming charged from renewables/grid mix previously)
            projected_cost += storage_dispatch * 5.0 
            remaining_demand -= storage_dispatch

        # Reliability score calculation
        # Safely handle zero demand case
        if actual_demand > 0:
            reliability_score = projected_supply / actual_demand
        else:
            reliability_score = 1.0 # If no demand, we are reliable
            
        reliability_score = min(1.0, max(0.0, reliability_score))
        
        return {
            "demand": actual_demand,
            "supply": projected_supply,
            "cost": projected_cost,
            "carbon": projected_carbon,
            "reliability": reliability_score,
            "unmet_demand": max(0.0, remaining_demand)
        }
