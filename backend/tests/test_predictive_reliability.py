
from backend.core.engine import DecisionEngine
from backend.models.schemas import InfrastructureState, Scenario, ScenarioType, EnergySource, EnergyType
from backend.models.infrastructure import GridNode, GridLink, NodeType, NodeStatus, LinkStatus
from backend.models.policy import PolicyConstraints
from backend.core.physics.partial_discharge import PartialDischargeSimulator

def test_partial_discharge_physics():
    # Test 1: Physics Logic
    class MockAsset:
        health_index = 1.0
        pd_activity = 0.0
    
    asset = MockAsset()
    
    # Run heavy load simulation (aging)
    for _ in range(100):
        PartialDischargeSimulator.update_asset_health(asset, load_factor=1.2, dt_hours=24.0)
    
    print(f"Health after stress: {asset.health_index}")
    assert asset.health_index < 1.0, "Asset should degrade under stress"
    
    # Test PD Spiking
    asset.health_index = 0.5 # Force degradation
    PartialDischargeSimulator._update_pd_activity(asset)
    print(f"PD Activity at 0.5 Health: {asset.pd_activity}")
    assert asset.pd_activity > 0.0, "Should show PD activity when degraded"

def test_engine_predictive_alert():
    # Test 2: Decision Engine Integration
    
    # Create critical link
    bad_link = GridLink(
        id="link-critical", source_id="n1", target_id="n2",
        capacity_mw=100.0, current_load_mw=95.0, # High load
        health_index=0.1, pd_activity=600.0 # Very bad link
    )
    
    state = InfrastructureState(
        sources=[],
        storage_capacity_mwh=0,
        current_storage_mwh=0,
        nodes=[],
        links=[bad_link]
    )
    
    scenario = Scenario(type=ScenarioType.NORMAL, description="Normal Ops", impact_factor=1.0)
    policy = PolicyConstraints()
    
    # MOCK _run_evaluation to avoid running the full engine/LP solver
    original_run_eval = DecisionEngine._run_evaluation
    
    captured_scenario = None
    
    def mock_run_eval(state, scen, demand, pol):
        nonlocal captured_scenario
        captured_scenario = scen
        from backend.models.schemas import DecisionOutput, DecisionRank
        return DecisionOutput(
            summary=f"Mock Result: {scen.description}",
            recommended_action="Mock Action",
            alternatives=[],
            risks=[],
            assumptions=[],
            confidence_level=0.9,
            next_steps=[],
            primary_factor="Reliability Assurance" if scen.type == ScenarioType.SUPPLY_FAILURE else "Mock"
        )
    
    DecisionEngine._run_evaluation = mock_run_eval
    
    DecisionEngine._run_evaluation = mock_run_eval
    
    # MOCK LoadForecaster to avoid DB hits
    from backend.core.forecaster import LoadForecaster
    original_forecast = LoadForecaster.predict_next_24h
    LoadForecaster.predict_next_24h = lambda: []
    
    try:
        # Run Decision Engine
        decision = DecisionEngine.evaluate_options(state, scenario, demand_mw=50.0, policy=policy)
        
        print(f"Decision Summary: {decision.summary}")
        print(f"Primary Factor: {decision.primary_factor}")
        
        # EXPECTATION: The engine should detect the imminent failure and switch mode
        # We check the captured scenario passed to the evaluation
        assert captured_scenario.type == ScenarioType.SUPPLY_FAILURE, "Scenario should be upgraded to SUPPLY_FAILURE"
        assert "PREDICTIVE ALERT" in captured_scenario.description, "Description should contain alert"
        
    finally:
        # Restore
        DecisionEngine._run_evaluation = original_run_eval
        LoadForecaster.predict_next_24h = original_forecast

if __name__ == "__main__":
    test_partial_discharge_physics()
    test_engine_predictive_alert()
    print("All Predictive Reliability tests passed!")
