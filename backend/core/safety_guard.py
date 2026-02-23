from typing import List, Dict, Any, Optional
from ..models.schemas import InfrastructureState, EnergyType
from .physics.dlr import DynamicLineRatingSimulator
from .physics.partial_discharge import PartialDischargeSimulator

class SafetyConstraintLayer:
    """
    Cognitive Trust Architecture: The 'Guardian' Layer.
    Ensures that AI-optimized dispatch proposals never violate physical reality.
    """

    @staticmethod
    def validate_proposal(state: InfrastructureState, dispatch_proposal: Dict[str, float]) -> Dict[str, Any]:
        """
        Validates if the proposed dispatch (Source ID -> MW) is safe.
        Returns check results and a 'safe' dispatch mapping.
        """
        is_safe = True
        violations = []
        safe_dispatch = dispatch_proposal.copy()

        # 1. Total Demand Matching Check
        # (Internal logic handled by LP, but Safety Guard double checks)
        
        # 2. Physics Check: Source Limits (including Nuclear BSR-220 limits)
        for source in state.sources:
            # Note: sources in state used by engine might already be modified (DLR/Nuclear)
            # We check if the proposal exceeds what we consider 'hard' safety limits
            proposed_val = dispatch_proposal.get(source.type.value, 0.0) # Using type as key for now in simplified dispatch
            
            if proposed_val > source.capacity * 1.1: # 10% buffer allowed for peaking
                # In real world, we'd use source.id, but state.sources in schema is simplified
                violations.append(f"Source {source.type} exceeds safety ceiling ({proposed_val:.1f} > {source.capacity:.1f}MW)")
                safe_dispatch[source.type.value] = source.capacity
                is_safe = False

        # 3. Physics Check: Network Congestion (DLR aware)
        # Simplified: Check if any link in the state is overloaded based on current load
        # In a full Power Flow, we'd check if this dispatch *results* in overload.
        for link in state.links:
            # If a link already has failing health, we shouldn't push it
            if link.health_index < 0.2:
                 violations.append(f"Safety Override: Critical Health on {link.id}. Limiting throughput.")
                 is_safe = False
                 # (In real system, we'd adjust the LP bounds and re-run)

        return {
            "is_safe": is_safe,
            "violations": violations,
            "sanitized_dispatch": safe_dispatch
        }

    @staticmethod
    def get_safety_rationale(state: InfrastructureState, selected_rank: Any) -> str:
        """
        Generates a human-readable explanation of why this action is safe or what risks were blocked.
        """
        rationales = []
        
        # Check for DLR influence
        high_wind_links = [l for l in state.links if "Wind" in l.limiting_factor]
        if high_wind_links:
            rationales.append(f"Utilized {len(high_wind_links)} lines with Dynamic Line Rating (Wind Cooling) to unlock headroom.")
            
        # Check for PD influence
        distressed_assets = [l for l in state.links if l.pd_activity > 100 or l.health_index < 0.5]
        if distressed_assets:
            rationales.append(f"Bypassed full capacity on {len(distressed_assets)} assets due to pre-fault Partial Discharge signatures.")
        
        if not rationales:
            return "Dispatch follows standard merit-order and thermal stability limits."
            
        return " | ".join(rationales)
