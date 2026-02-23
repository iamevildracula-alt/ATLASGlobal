from fastapi.testclient import TestClient
from ..main import app
from ..db.database import Base, engine

# TestClient uses the actual app logic but simulates HTTP calls
client = TestClient(app)

def test_full_workflow():
    print("\n[VERIFICATION] Starting Integration Test...")
    
    # 1. Test State Retrieval
    print("Testing /api/decisions/state...")
    response = client.get("/api/decisions/state")
    assert response.status_code == 200
    state = response.json()
    assert "sources" in state
    print(f"Verified: Persistence layer returned {len(state['sources'])} sources.")

    # 2. Test History retrieval (from IEX ingestion)
    print("Testing /api/history/series...")
    response = client.get("/api/history/series")
    assert response.status_code == 200
    history = response.json()
    assert "data" in history
    print(f"Verified: History layer returned {len(history['data'])} telemetry points.")

    # 3. Test Decision Execution (LP Optimization + AI Forecast)
    print("Testing /api/decisions/run (LP Optimization)...")
    payload = {
        "type": "demand_spike",
        "description": "Integration Test Peak",
        "impact_factor": 1.2,
        "affected_source": None
    }
    response = client.post("/api/decisions/run", json=payload)
    if response.status_code != 200:
        print(f"FAILED /api/decisions/run with {response.status_code}: {response.text}")
    assert response.status_code == 200
    decision = response.json()
    
    assert "recommended_action" in decision
    assert decision["primary_factor"] in ["Reliability Assurance", "Cost Reduction", "Carbon Reduction", "Balanced Performance"]
    
    # Check if the AI-Optimized result is present (even if not chosen as recommended)
    is_lp_active = (decision["recommended_action"] == "AI-Optimized Smart Dispatch" or 
                   any(alt["option_name"] == "AI-Optimized Smart Dispatch" for alt in decision["alternatives"]))
    
    assert is_lp_active, "LP Optimizer was not found in decision strategies"
    print(f"Verified: Decision Engine recommendation: {decision['recommended_action']}")
    print(f"Verified: LP Optimization (Antigravity Logic) is ACTIVE.")

if __name__ == "__main__":
    test_full_workflow()
