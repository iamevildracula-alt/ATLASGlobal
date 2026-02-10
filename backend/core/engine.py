from ..models.schemas import InfrastructureState, Scenario, DecisionOutput, DecisionRank, EnergyType, EnergySource, ScenarioType, TradeOff
from ..models.policy import PolicyConstraints
from .simulator import EDLSimulator
from typing import List, Dict, Any
import copy
import math

class DecisionEngine:
    @staticmethod
    def evaluate_options(state: InfrastructureState, scenario: Scenario, demand_mw: float, policy: PolicyConstraints) -> DecisionOutput:
        try:
            return DecisionEngine._run_evaluation(state, scenario, demand_mw, policy)
        except Exception as e:
            print(f"Decision Engine Error: {e}")
            return DecisionEngine._get_fallback_decision(f"Internal calculation error: {str(e)}")

    @staticmethod
    def _run_evaluation(state: InfrastructureState, scenario: Scenario, demand_mw: float, policy: PolicyConstraints) -> DecisionOutput:
        options = []
        
        # --- Strategy 1: Business as Usual (Baseline) ---
        baseline_results = EDLSimulator.simulate(state, scenario, demand_mw)
        options.append(DecisionEngine._create_rank(
            "Maintain Current Operations",
            baseline_results,
            "Baseline configuration. No active intervention.",
            state # Pass state to calculate trade-offs relative to others if needed, simplified here
        ))

        # --- Strategy 2: Reliability First (Mitigation) ---
        # Logic: If reliability < 1.0, throw everything at it.
        state_reliable = copy.deepcopy(state)
        # simplistic logic: boost battery discharge, turn on all backup
        state_reliable.current_storage_mwh = state.storage_capacity_mwh # Assume we can fully utilize reserves or emergency import
        results_reliable = EDLSimulator.simulate(state_reliable, scenario, demand_mw)
        options.append(DecisionEngine._create_rank(
            "Maximize Reliability (Emergency Dispatch)",
            results_reliable,
            "Prioritizes grid stability by maximizing storage and backup access.",
            state_reliable
        ))
        
        # --- Strategy 3: Cost Optimization ---
        # Logic: Reduce expensive sources if possible (mostly relevant for normal/oversupply)
        state_cost = copy.deepcopy(state)
        # naive logic: reduce capacity of most expensive source by 20%
        sorted_sources = sorted(state_cost.sources, key=lambda x: x.cost_per_mwh, reverse=True)
        if sorted_sources:
             # Reduce the most expensive one
             sorted_sources[0].capacity *= 0.8
        results_cost = EDLSimulator.simulate(state_cost, scenario, demand_mw)
        options.append(DecisionEngine._create_rank(
            "Cost Optimization Protocol",
            results_cost,
            "Reduces reliance on expensive peak generation to lower operating costs.",
            state_cost
        ))

        # --- Strategy 4: Green Energy (Carbon Reduction) ---
        # Logic: Maximize renewables, reduce fossil
        state_green = copy.deepcopy(state)
        for s in state_green.sources:
            if s.type in [EnergyType.SOLAR, EnergyType.WIND, EnergyType.NUCLEAR]:
                s.availability = 1.0 # Assume max theoretical availability (unrealistic but distinct strategy)
            if s.type in [EnergyType.GRID, EnergyType.BATTERY]: # simplification
                 pass
        results_green = EDLSimulator.simulate(state_green, scenario, demand_mw)
        options.append(DecisionEngine._create_rank(
            "Maximize Green Energy",
            results_green,
            "Prioritizes diverse renewable sources to minimize carbon footprint.",
            state_green
        ))

        # --- Selection Logic ---
        # Weighting based on Scenario
        # Normal: Cost > Reliability > Carbon
        # Spikes/Failures: Reliability >>> Cost > Carbon
        
        weighted_scores = []
        for opt in options:
            score = 0.0
            rel = opt.reliability_score
            cost = opt.cost_impact
            carbon = opt.carbon_impact
            
            # Normalize approximate values for scoring
            norm_cost = cost / 20000.0 # Arbitrary denominator for scaling
            norm_carbon = carbon / 5000.0
            
            if scenario.type in [ScenarioType.DEMAND_SPIKE, ScenarioType.SUPPLY_FAILURE]:
                 # Reliability critical
                 score = (rel * 1000) - (norm_cost * 10) - (norm_carbon * 5)
            else:
                 # Balanced
                 score = (rel * 500) - (norm_cost * 50) - (norm_carbon * 20)
            
            # --- Policy Constraints Penalties ---
            # Cost Penalty
            # Calculate approx cost/MWh. Mock cost is total cost.
            # Assuming average demand is demand_mw.
            current_cost_per_mwh = cost / demand_mw if demand_mw > 0 else 0
            if current_cost_per_mwh > policy.max_cost_per_mwh:
                score -= 1000 * (current_cost_per_mwh / policy.max_cost_per_mwh)
            
            # Reliability Penalty
            if rel < policy.min_reliability_score:
                score -= 2000 * (policy.min_reliability_score - rel)
                
            # Carbon Penalty
            # Mock carbon is total tons.
            carbon_intensity = carbon / demand_mw if demand_mw > 0 else 0
            if carbon_intensity > policy.max_carbon_per_mwh:
                score -= 500 * (carbon_intensity / policy.max_carbon_per_mwh)
            
            # Risk Tolerance Adjustments
            if policy.risk_tolerance == "averse":
                if rel < 0.999: score -= 500
            elif policy.risk_tolerance == "seeking":
                if current_cost_per_mwh < policy.max_cost_per_mwh: score += 200 # Boost cheap risky options
            
            opt.score = score
            weighted_scores.append(opt)
            
        weighted_scores.sort(key=lambda x: x.score, reverse=True)
        best = weighted_scores[0]
        
        # Identify Primary Factor
        primary_factor = "Balanced Performance"
        if scenario.type in [ScenarioType.DEMAND_SPIKE, ScenarioType.SUPPLY_FAILURE]:
             primary_factor = "Reliability Assurance"
        elif best.option_name == "Cost Optimization Protocol":
             primary_factor = "Cost Reduction"
        elif best.option_name == "Maximize Green Energy":
             primary_factor = "Carbon Reduction"

        return DecisionOutput(
            summary=f"Recommendation: {best.option_name}. This strategy provides the best outcome for the '{scenario.description}' scenario.",
            recommended_action=best.option_name,
            alternatives=weighted_scores[1:],
            risks=DecisionEngine._generate_risks(scenario, best),
            assumptions=[
                "Grid telemetry is accurate within 5%",
                "Assets are responsive to dispatch signals"
            ],
            confidence_level=0.92 if best.reliability_score > 0.98 else 0.75,
            next_steps=[
                "Approve dispatch schedule",
                "Monitor grid frequency"
            ],
            primary_factor=primary_factor
        )

    @staticmethod
    def _create_rank(name: str, results: Dict, reasoning: str, state: InfrastructureState) -> DecisionRank:
        # Generate Trade-offs
        trade_offs = []
        
        # Cost Trade-off
        # A simple heuristic: High cost if > 15000 (mock unit)
        if results["cost"] > 20000:
            trade_offs.append(TradeOff(aspect="Cost", impact="High", description="Expensive dispatch due to peak sourcing."))
        elif results["cost"] < 10000:
            trade_offs.append(TradeOff(aspect="Cost", impact="Low", description="Cost-efficient operation."))
        else:
            trade_offs.append(TradeOff(aspect="Cost", impact="Medium", description="Standard operating cost."))

        # Reliability Trade-off
        if results["reliability"] < 0.99:
             trade_offs.append(TradeOff(aspect="Reliability", impact="High", description="Significant risk of unserved energy."))
        elif results["reliability"] < 1.0:
             trade_offs.append(TradeOff(aspect="Reliability", impact="Medium", description="Minor load shedding possible."))
        else:
             trade_offs.append(TradeOff(aspect="Reliability", impact="Low", description="Full demand coverage."))

        # Carbon Trade-off
        if results["carbon"] > 5000:
             trade_offs.append(TradeOff(aspect="Carbon", impact="High", description="High emissions from fossil/grid Sources."))
        else:
             trade_offs.append(TradeOff(aspect="Carbon", impact="Low", description="Low emissions profile."))

        return DecisionRank(
            option_name=name,
            score=0.0, # Calculated later
            cost_impact=round(results["cost"], 2),
            reliability_score=round(results["reliability"], 4),
            risk_level="High" if results["reliability"] < 0.98 else "Low",
            carbon_impact=round(results["carbon"], 2),
            reasoning=reasoning,
            trade_offs=trade_offs
        )

    @staticmethod
    def _generate_risks(scenario: Scenario, rank: DecisionRank) -> List[str]:
        risks = []
        if rank.reliability_score < 1.0:
            risks.append("Immediate load shedding required.")
        if scenario.type == ScenarioType.DEMAND_SPIKE:
            risks.append("Transformer overheating risk if demand is sustained.")
        if scenario.type == ScenarioType.SUPPLY_FAILURE:
            risks.append("Cascading failure risk if reserve margin drops below 5%.")
        if not risks:
            risks.append("No significant operational risks identified.")
        return risks

    @staticmethod
    def _get_fallback_decision(reason: str) -> DecisionOutput:
        return DecisionOutput(
            summary="System entered Safety Mode due to calculation anomaly.",
            recommended_action="Maintain Current Operations (Safety Mode)",
            alternatives=[],
            risks=["Decision intelligence is operating in degraded mode.", reason],
            assumptions=["System telemetry may be unreliable."],
            confidence_level=0.0,
            next_steps=["Contact support", "Manual grid verification"],
            primary_factor="System Safety"
        )
