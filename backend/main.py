from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
from backend.core.external_bridge import context_bridge
from backend.core.time_sync import synchronizer

@asynccontextmanager
async def lifespan(app: FastAPI):
    async def poll_context():
        # Initial poll
        try:
            w = await context_bridge.get_current_weather()
            m = await context_bridge.get_market_price()
            synchronizer.update_context("weather", w.dict())
            synchronizer.update_context("market", m.dict())
        except Exception:
            pass
        
        while True:
            await asyncio.sleep(300) # Every 5 minutes
            try:
                w = await context_bridge.get_current_weather()
                m = await context_bridge.get_market_price()
                synchronizer.update_context("weather", w.dict())
                synchronizer.update_context("market", m.dict())
            except Exception as e:
                print(f"Context Polling Error: {e}")

    task = asyncio.create_task(poll_context())
    yield
    task.cancel()

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from backend.api import decisions, scenarios, ingestion, infrastructure, history, policy, telemetry

app = FastAPI(title="ATLASGlobal AI - Energy Decision Layer", lifespan=lifespan)

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
