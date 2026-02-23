import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_decision_pipeline():
    print("Testing ATLASGlobal Real-World Decision Pipeline...")
    
    # 1. Check Infrastructure State (should come from DB now)
    print("\n1. Fetching Infrastructure State from persistent DB...")
    r = requests.get(f"{BASE_URL}/api/decisions/state")
    if r.status_code == 200:
        state = r.json()
        print(f"Success. Found {len(state['sources'])} energy sources.")
    else:
        print(f"Failed to fetch state: {r.text}")
        return

    # 2. Check History (should show ingested IEX data)
    print("\n2. Fetching Historical Telemetry...")
    r = requests.get(f"{BASE_URL}/api/history/series")
    if r.status_code == 200:
        history = r.json()
        print(f"Success. Found {len(history['data'])} historical data points.")
    else:
        print(f"Failed to fetch history: {r.text}")

    # 3. Run Decision Simulation (uses LP + AI Forecaster)
    print("\n3. Running Physics-Constrained Decision Simulation (LP Optimized)...")
    payload = {
        "type": "demand_spike",
        "description": "Verification Test Spike",
        "impact_factor": 1.5,
        "affected_source": "none"
    }
    
    start_time = time.time()
    r = requests.post(f"{BASE_URL}/api/decisions/run", json=payload)
    end_time = time.time()
    
    if r.status_code == 200:
        decision = r.json()
        print(f"Success. Simulation completed in {(end_time - start_time)*1000:.2f}ms")
        print(f"Recommended Action: {decision['recommended_action']}")
        print(f"Confidence Level: {decision['confidence_level']}")
        print(f"Primary Factor: {decision['primary_factor']}")
        
        # Verify if 'AI-Optimized' is in the results
        opt_found = any(alt['option_name'] == "AI-Optimized Smart Dispatch" for alt in decision['alternatives'])
        if decision['recommended_action'] == "AI-Optimized Smart Dispatch" or opt_found:
            print("VERIFIED: AI-Optimized Dispatch Strategy (LP) is active.")
        else:
            print("WARNING: AI-Optimized strategy not found in output.")
    else:
        print(f"Failed to run simulation: {r.text}")

if __name__ == "__main__":
    test_decision_pipeline()
