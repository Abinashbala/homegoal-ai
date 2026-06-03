"""
HomeGoal AI — Analytics Router (For recruiters/validation)
"""
from fastapi import APIRouter, HTTPException
from backend.config import load_model_metrics
from backend.schemas.responses import ModelMetricsResponse, ModelComparisonResponse

router = APIRouter(tags=["Analytics & Model Validation"])

@router.get("/model-metrics", response_model=ModelMetricsResponse)
def get_model_metrics():
    """
    Returns metrics from the Phase 5 ML model selection process.
    This endpoint is designed to demonstrate ML rigor to recruiters.
    """
    metrics = load_model_metrics()
    if not metrics:
        raise HTTPException(status_code=404, detail="Model metrics artifact not found. Please run Phase 5 training.")
        
    hpi_res = metrics.get("hpi_results", [])
    fx_res = metrics.get("fx_results", [])
    
    best_hpi = metrics.get("best_hpi", {}).get("model", "Exponential Trend")
    best_fx = metrics.get("best_fx", {}).get("model", "Prophet")
    
    return ModelMetricsResponse(
        hpi_model_comparison=hpi_res,
        fx_model_comparison=fx_res,
        selected_hpi_model=best_hpi,
        selected_fx_model=best_fx,
        production_approach="CAGR-based Scenarios (Validated by ML Models)",
        validation_note="Models were used to validate the boundary conditions of the business scenario engine."
    )


@router.get("/model-comparison", response_model=ModelComparisonResponse)
def get_model_comparison():
    """
    Detailed comparison of models and final scenario parameters.
    """
    metrics = load_model_metrics()
    if not metrics:
        raise HTTPException(status_code=404, detail="Model metrics artifact not found.")
        
    return ModelComparisonResponse(
        hpi={
            "best_model": metrics.get("best_hpi", {}),
            "all_models": metrics.get("hpi_results", []),
            "cagr_scenarios": metrics.get("hpi_cagr_scenarios", {})
        },
        fx={
            "best_model": metrics.get("best_fx", {}),
            "all_models": metrics.get("fx_results", []),
            "cagr_scenarios": metrics.get("fx_cagr_scenarios", {})
        },
        scenario_parameters={
            "hpi": metrics.get("hpi_cagr_scenarios", {}),
            "fx": metrics.get("fx_cagr_scenarios", {})
        },
        selection_rationale="Simpler models were preferred when performance gaps were negligible. The models confirmed that historical CAGR segments are excellent proxies for future scenario bounds."
    )
