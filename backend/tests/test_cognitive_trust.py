from backend.core.safety_guard import SafetyConstraintLayer
from backend.core.engine import DecisionEngine
from backend.models.schemas import InfrastructureState, Scenario, EnergySource, EnergyType, ScenarioType
from backend.models.infrastructure import GridLink
from backend.models.policy import PolicyConstraints

def test_explainability_bridge():
    # Setup state with DLR and PD triggers
    link_dlr = GridLink(
        id="link-dlr", source_id="s1", target_id="t1",
        capacity_mw=100.0, current_load_mw=50.0,
        limiting_factor="Wind Cooling (DLR)"
    )
    link_pd = GridLink(
        id="link-pd", source_id="s2", target_id="t2",
        capacity_mw=100.0, current_load_mw=50.0,
        health_index=0.4, pd_activity=150.0
    )
    
    source = EnergySource(type=EnergyType.GRID, capacity=100.0, cost_per_mwh=50.0, availability=1.0, carbon_intensity=0.1)
    
    state = InfrastructureState(
        sources=[source],
        storage_capacity_mwh=0,
        current_storage_mwh=0,
        links=[link_dlr, link_pd],
        nodes=[]
    )
    
    rationale = SafetyConstraintLayer.get_safety_rationale(state, None)
    print(f"Generated Rationale: {rationale}")
    
    assert "Wind Cooling" in rationale
    assert "Partial Discharge" in rationale

def test_engine_rationale_population():
    source = EnergySource(type=EnergyType.GRID, capacity=100.0, cost_per_mwh=50.0, availability=1.0, carbon_intensity=0.1)
    state = InfrastructureState(
        sources=[source],
        storage_capacity_mwh=0,
        current_storage_mwh=0,
        links=[],
        nodes=[]
    )
    scenario = Scenario(type=ScenarioType.NORMAL, description="Test Rationale", impact_factor=1.0)
    
    # Mock forecaster
    from backend.core.forecaster import LoadForecaster
    LoadForecaster.predict_next_24h = lambda: []
    
    policy = PolicyConstraints(max_cost_per_mwh=100.0, max_carbon_per_mwh=0.5, min_reliability_score=0.99)
    output = DecisionEngine.evaluate_options(state, scenario, demand_mw=50.0, policy=policy)
    
    print(f"Engine Rationale: {output.rationale}")
    assert output.rationale is not None
    assert len(output.rationale) > 0

if __name__ == "__main__":
    test_explainability_bridge()
    test_engine_rationale_population()
    print("Cognitive Trust tests passed!")
