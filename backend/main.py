from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
from backend.core.external_bridge import context_bridge
from backend.core.time_sync import synchronizer

from backend.core.event_bus import broadcaster
import random

@asynccontextmanager
async def lifespan(app: FastAPI):
    async def poll_context():
        while True:
            await asyncio.sleep(2)  # High-frequency tick for live dashboard
            try:
                # 1. Fetch Contextual L1 Data
                w = await context_bridge.get_current_weather()
                m = await context_bridge.get_market_price()
                synchronizer.update_context("weather", w.dict())
                synchronizer.update_context("market", m.dict())
                
                # 2. Push to connected clients via Event Bus
                await broadcaster.broadcast({
                    "type": "telemetry",
                    "data_type": "weather",
                    "temp_c": round(w.temperature, 1),
                    "wind_kph": round(w.wind_speed, 1),
                    "condition": w.condition,
                    "is_verified": True
                })
                
                await broadcaster.broadcast({
                    "type": "telemetry",
                    "data_type": "market",
                    "price_mwh": round(m.price_per_mwh, 2),
                    "region": "GLOBAL-ISO",
                    "is_verified": True
                })
                
                # 3. Simulate a live SCADA telemetry tick going through L2 Shield
                # (Normally this comes from POST /scada/push, but we simulate a live stream here)
                from backend.core.data_validator import validator
                raw_val = 450.0 + random.uniform(-10, 10)
                
                # Introduce a random adversarial attack/drift 5% of the time to show Shield working
                if random.random() < 0.05:
                    raw_val += 500.0  # Massive impossible jump
                    
                val_res = validator.validate_measurement("sub_main", raw_val)
                
                await broadcaster.broadcast({
                    "type": "telemetry",
                    "data_type": "demand_mw",
                    "asset": "sub_main",
                    "value": round(raw_val, 1) if val_res['is_valid'] else "BLOCK",
                    "is_verified": val_res["is_valid"],
                    "credibility": val_res['credibility_score'],
                    "flags": val_res['flags']
                })
                
            except Exception as e:
                print(f"L1 Live Feed Error: {e}")

    task = asyncio.create_task(poll_context())
    yield
    task.cancel()

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from backend.api import decisions, scenarios, ingestion, infrastructure, history, policy, telemetry

app = FastAPI(title="ATLASGlobal AI - Sentient Grid API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(decisions.router, prefix="/api/decisions", tags=["decisions"])
app.include_router(scenarios.router, prefix="/api/scenarios", tags=["scenarios"])
app.include_router(infrastructure.router, prefix="/api/infrastructure", tags=["infrastructure"])
app.include_router(history.router, prefix="/api/history", tags=["history"])
app.include_router(policy.router, prefix="/api/policy", tags=["Policy"])
app.include_router(ingestion.router, prefix="/api/ingestion", tags=["ingestion"])
app.include_router(telemetry.router, prefix="/api/telemetry", tags=["telemetry"])

# Serve Static Files in production
static_path = os.getenv("STATIC_FILES_DIR", "static")
if os.path.exists(static_path):
    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"message": "ATLASGlobal AI API v0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
