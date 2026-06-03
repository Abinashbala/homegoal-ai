"""
HomeGoal AI — FastAPI Application Entrypoint
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from backend.config import APP_TITLE, APP_DESCRIPTION, APP_VERSION, CONTACT, LICENSE
from backend.routers import scenarios, analytics
from backend.schemas.responses import HealthResponse, VersionResponse

app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    contact=CONTACT,
    license_info=LICENSE,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS config
origins = [
    "http://localhost:5173",
    "https://homegoal-ai-frontend.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(scenarios.router)
app.include_router(analytics.router)


@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check():
    return HealthResponse(
        status="ok",
        version=APP_VERSION,
        engines={
            "property": "loaded",
            "wealth": "loaded",
            "inflation": "loaded",
            "currency": "loaded",
            "stress": "loaded",
            "scenario": "loaded"
        },
        timestamp=datetime.utcnow().isoformat() + "Z"
    )


@app.get("/version", response_model=VersionResponse, tags=["System"])
def version_info():
    return VersionResponse(
        version=APP_VERSION,
        app_name=APP_TITLE,
        description=APP_DESCRIPTION,
        phase="Phase 6 Complete",
        engines=["PropertyEngine", "WealthEngine", "InflationEngine", "CurrencyEngine", "StressScoreEngine", "ScenarioEngine"],
        data_vintage="Dec 2025"
    )

if __name__ == "__main__":
    import uvicorn
    # Typically run with: uvicorn backend.main:app --reload
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
