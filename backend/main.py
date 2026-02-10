from fastapi import FastAPI # Force reload
from fastapi.middleware.cors import CORSMiddleware
from .api import decisions, scenarios, ingestion, infrastructure, history, policy

app = FastAPI(title="Energy Decision Layer (EDL)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(decisions.router, prefix="/api/decisions", tags=["Decisions"])
app.include_router(scenarios.router, prefix="/api/scenarios", tags=["Scenarios"])
app.include_router(infrastructure.router, prefix="/api/infrastructure", tags=["Infrastructure"])
app.include_router(history.router, prefix="/api/history", tags=["History"])
app.include_router(policy.router, prefix="/api/policy", tags=["Policy"])

@app.get("/")
async def root():
    return {"message": "Energy Decision Layer (EDL) API v0"}
