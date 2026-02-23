import asyncio
import websockets
import json
import requests
import time

API_BASE = "http://localhost:8000/api"
WS_URL = "ws://localhost:8000/api/telemetry/live"

async def test_telemetry_flow():
    print(f"Connecting to {WS_URL}...")
    try:
        async with websockets.connect(WS_URL) as websocket:
            print("Successfully connected to telemetry WebSocket.")
            
            # Prepare mock SCADA data
            mock_data = [
                {
                    "id": "node_1",
                    "value": 520.5,
                    "type": "demand_mw",
                    "timestamp": "2026-02-22T22:40:00Z"
                }
            ]
            
            # Push data via REST
            print("Pushing mock SCADA data via REST API...")
            response = requests.post(f"{API_BASE}/ingestion/scada/push", json=mock_data)
            assert response.status_code == 200
            print("Push successful.")
            
            # Wait for WebSocket message
            print("Waiting for WebSocket broadcast...")
            message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(message)
            
            print(f"Received message: {data}")
            assert data["id"] == "node_1"
            assert data["value"] == 520.5
            assert data["data_type"] == "demand_mw"
            
            print("\nVERIFICATION SUCCESS: Telemetry propagated from Ingestion -> Event Bus -> WebSocket -> Client.")
            
    except Exception as e:
        print(f"VERIFICATION FAILED: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_telemetry_flow())
