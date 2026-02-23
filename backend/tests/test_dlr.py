from backend.core.physics.dlr import DynamicLineRatingSimulator
from backend.core.engine import DecisionEngine
from backend.models.schemas import InfrastructureState, Scenario, EnergySource, EnergyType
from backend.models.infrastructure import GridLink

def test_dlr_physics():
    # Cold & Windy
    factor_cold_wind = DynamicLineRatingSimulator.calculate_ampacity_factor(ambient_temp_c=10.0, wind_speed_mps=8.0)
    # Hot & Still
    factor_hot_still = DynamicLineRatingSimulator.calculate_ampacity_factor(ambient_temp_c=40.0, wind_speed_mps=0.2)
    
    print(f"Cold/Wind Factor: {factor_cold_wind:.2f}")
    print(f"Hot/Still Factor: {factor_hot_still:.2f}")
    
    assert factor_cold_wind > 1.0, "Cold/Wind should unlock capacity"
    assert factor_hot_still < 1.0, "Hot/Still should derate capacity"

def test_engine_dlr_dispatch():
    # Mock link with static rating 100
    link = GridLink(
        id="link-1", source_id="s", target_id="t",
        capacity_mw=100.0, current_load_mw=50.0,
        static_rating_mva=100.0, dynamic_rating_mva=100.0
    )
    
    source = EnergySource(type=EnergyType.GRID, capacity=100.0, cost_per_mwh=50.0, availability=1.0, carbon_intensity=0.1)
    
    state = InfrastructureState(
        sources=[source],
        storage_capacity_mwh=0,
        current_storage_mwh=0,
        links=[link],
        nodes=[]
    )
    
    scenario = Scenario(type="normal", description="Test DLR", impact_factor=1.0)
    
    # Mocking external hits
    from backend.core.forecaster import LoadForecaster
    LoadForecaster.predict_next_24h = lambda: []
    
    # We expect verify that evaluation runs and applies DLR
    # The current weather in engine.py is fixed to cold/windy (12C, 6.5mps)
    # Which should produce factor > 1
    
    # To check internal state, we can use a mock _run_evaluation capture
    original_run_eval = DecisionEngine._run_evaluation
    captured_state = None
    
    def mock_run_eval(s, sc, d, p):
        nonlocal captured_state
        captured_state = s
        from backend.models.schemas import DecisionOutput
        return DecisionOutput(summary="Mock", recommended_action="Mock", alternatives=[], risks=[], assumptions=[], confidence_level=1.0, next_steps=[], primary_factor="Mock")
    
    DecisionEngine._run_evaluation = mock_run_eval
    
    try:
        DecisionEngine.evaluate_options(state, scenario, demand_mw=80.0, policy=None)
        
        # Check if link capacity was boosted
        new_cap = captured_state.links[0].capacity_mw
        new_source_cap = captured_state.sources[0].capacity
        
        print(f"Original Link Cap: 100.0 -> Boosted Link Cap: {new_cap:.2f}")
        print(f"Original Source Cap: 100.0 -> Boosted Source Cap: {new_source_cap:.2f}")
        
        assert new_cap > 100.0, "Link capacity should be boosted by DLR"
        assert new_source_cap > 100.0, "Source capacity should be boosted by 'Headroom' logic"
        
    finally:
        DecisionEngine._run_evaluation = original_run_eval

if __name__ == "__main__":
    test_dlr_physics()
    test_engine_dlr_dispatch()
    print("All DLR tests passed!")
