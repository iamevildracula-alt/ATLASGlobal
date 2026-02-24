from datetime import datetime, timedelta
from backend.core.data_validator import DataValidator

def test_data_validator_normal_payload():
    validator = DataValidator()
    
    # Establish baseline
    t1 = datetime.utcnow()
    payload1 = {"asset_id": "sub_01", "value_mw": 100.0, "timestamp": t1}
    res1 = validator.process_telemetry(payload1)
    
    assert res1["is_verified"] == True
    assert res1["credibility_score"] == 1.0

    # Normal increase (e.g. 5 MW over 2 seconds = 2.5 MW/s)
    t2 = t1 + timedelta(seconds=2)
    payload2 = {"asset_id": "sub_01", "value_mw": 105.0, "timestamp": t2}
    res2 = validator.process_telemetry(payload2)
    
    assert res2["is_verified"] == True
    assert res2["credibility_score"] == 1.0
    assert len(res2["shield_flags"]) == 0

def test_adversarial_poisoned_payload():
    validator = DataValidator()
    
    t1 = datetime.utcnow()
    payload1 = {"asset_id": "sub_01", "value_mw": 100.0, "timestamp": t1}
    validator.process_telemetry(payload1)
    
    # Adversarial attack: 500 MW jump in 1 second (physically impossible for this asset)
    t2 = t1 + timedelta(seconds=1)
    payload_attack = {"asset_id": "sub_01", "value_mw": 600.0, "timestamp": t2}
    res_attack = validator.process_telemetry(payload_attack)
    
    assert res_attack["is_verified"] == False
    assert res_attack["credibility_score"] < 0.5
    assert any("Adversarial alert" in flag for flag in res_attack["shield_flags"])

def test_drift_monitoring():
    validator = DataValidator()
    t = datetime.utcnow()
    
    # Establish baseline with 100 packets of around 50 MW
    for i in range(100):
        t += timedelta(seconds=1)
        validator.process_telemetry({"asset_id": "sensor_x", "value_mw": 50.0 + (i % 2), "timestamp": t})
        
    # Introduce slow drift (mean shifts to 80 MW suddenly for the next batch)
    for i in range(50):
        t += timedelta(seconds=1)
        res = validator.process_telemetry({"asset_id": "sensor_x", "value_mw": 80.0, "timestamp": t})
        
    # By the end of this batch, drift should be detected
    assert res["credibility_score"] < 1.0
    assert not res["is_verified"] or res["credibility_score"] < 1.0
    assert any("Distribution drift" in flag for flag in res["shield_flags"])
    
if __name__ == "__main__":
    test_data_validator_normal_payload()
    test_adversarial_poisoned_payload()
    test_drift_monitoring()
    print("All tests passed! Adversarial and Drift monitoring successfully validated.")
