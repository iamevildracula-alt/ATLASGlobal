from datetime import datetime
from backend.core.feature_engine import FeatureEngine, TemporalEmbedder, PINNConstraintLayer

def test_temporal_embedding():
    # Test Midnight (start of cycle)
    t = datetime(2026, 1, 1, 0, 0) # Jan 1, Midnight
    features = TemporalEmbedder.embed(t)
    
    assert 'time_minute_sin' in features
    assert 'time_minute_cos' in features
    # Cosine should be peak at midnight (0 minutes)
    assert round(features['time_minute_cos'], 2) == 1.0
    assert round(features['time_minute_sin'], 2) == 0.0
    assert features['is_weekend'] == 0.0 # Jan 1 2026 is a Thursday

def test_pinn_clipping():
    pinn = PINNConstraintLayer()
    
    # Simulate a physically dangerous vector leaking through
    dangerous_state = {
        'transformer_temp_c': 300.0, # Impossible without melting
        'grid_frequency_hz': 20.0,   # Immediate blackout state
        'node1_gen_mw': 500.0,
        'city_load_mw': 100.0
    }
    
    safe_state = pinn.validate_and_clip(dangerous_state)
    
    # 1. Thermal bounds capped
    assert safe_state['transformer_temp_c'] == 165.0 # Max 110 * 1.5
    
    # 2. Frequency bounds capped
    assert safe_state['grid_frequency_hz'] == 45.0
    
    # 3. Kirchhoff violation tracked
    assert safe_state['pinn_balance_violation_mw'] == 400.0 # 500 gen - 100 load


def test_feature_engine_integration():
    engine = FeatureEngine()
    
    l2_packet = {
        "is_verified": True,
        "credibility_score": 0.95,
        "timestamp": datetime(2026, 1, 1, 12, 0),
        "sub_1_gen_mw": 100.0,
        "sub_1_load_mw": 98.0
    }
    
    state_vector = engine.generate_state_vector(l2_packet)
    
    # Verify core transfer
    assert state_vector['sub_1_gen_mw'] == 100.0
    assert state_vector['l2_credibility'] == 0.95
    
    # Verify temporal injection (Noon = cosine at -1, sine at 0)
    assert round(state_vector['time_minute_cos'], 2) == -1.0
    
    # Verify PINN physics calculation
    assert state_vector['pinn_balance_violation_mw'] == 2.0
    
    print("All L3 Feature Engine tests passed! PINNs and embeddings verified.")

if __name__ == "__main__":
    test_temporal_embedding()
    test_pinn_clipping()
    test_feature_engine_integration()
