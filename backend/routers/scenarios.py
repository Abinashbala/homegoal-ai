"""
HomeGoal AI — Scenarios Router
"""
from fastapi import APIRouter
from datetime import datetime
import uuid

from backend.schemas.requests import (
    ForecastRequest,
    ScenarioRequest,
    StressScoreRequest,
    PropertyAnalysisRequest
)
from backend.schemas.responses import (
    ForecastResponse,
    ScenarioResponse,
    StressScoreResponse,
    PropertyAnalysisResponse
)
from backend.engines.scenario import ScenarioEngine
from backend.engines.stress import StressScoreEngine
from backend.engines.property import PropertyEngine
from backend.config import CURRENT_YEAR

router = APIRouter(tags=["Forecasting & Scenarios"])

@router.post("/forecast", response_model=ForecastResponse)
def generate_forecast(req: ForecastRequest):
    """
    Generate a full affordability forecast including conservative,
    expected, and optimistic scenarios.
    """
    req_id = str(uuid.uuid4())
    now_str = datetime.utcnow().isoformat() + "Z"
    
    scen_c = ScenarioEngine.generate_scenario(req, "conservative")
    scen_e = ScenarioEngine.generate_scenario(req, "expected")
    scen_o = ScenarioEngine.generate_scenario(req, "optimistic")
    
    # Generate summary logic
    years = req.property.target_year - CURRENT_YEAR
    
    summary = {
        "recommended_scenario": "expected",
        "expected_affordability_ratio": scen_e.kpis.affordability_ratio,
        "is_achievable_in_expected": scen_e.kpis.goal_gap_inr <= 0,
        "years_to_target": years,
        "key_takeaway": scen_e.stress.recommendation
    }
    
    return ForecastResponse(
        request_id=req_id,
        computed_at=now_str,
        years_horizon=years,
        target_year=req.property.target_year,
        current_year=CURRENT_YEAR,
        city=req.property.city,
        locality=req.property.locality,
        conservative=scen_c,
        expected=scen_e,
        optimistic=scen_o,
        summary=summary
    )


@router.post("/scenarios", response_model=ScenarioResponse)
def compare_scenarios(req: ScenarioRequest):
    """
    Compare scenarios side-by-side. 
    Returns similar data to /forecast but optimized for tabular comparison.
    """
    req_id = str(uuid.uuid4())
    now_str = datetime.utcnow().isoformat() + "Z"
    
    scen_c = ScenarioEngine.generate_scenario(req, "conservative")
    scen_e = ScenarioEngine.generate_scenario(req, "expected")
    scen_o = ScenarioEngine.generate_scenario(req, "optimistic")
    
    comparison_table = {
        "future_property_value_inr": {
            "conservative": scen_c.property.future_value_inr,
            "expected": scen_e.property.future_value_inr,
            "optimistic": scen_o.property.future_value_inr,
        },
        "real_wealth_inr": {
            "conservative": scen_c.wealth.real_wealth_inr,
            "expected": scen_e.wealth.real_wealth_inr,
            "optimistic": scen_o.wealth.real_wealth_inr,
        },
        "goal_gap_inr": {
            "conservative": scen_c.kpis.goal_gap_inr,
            "expected": scen_e.kpis.goal_gap_inr,
            "optimistic": scen_o.kpis.goal_gap_inr,
        },
        "stress_category": {
            "conservative": scen_c.stress.category,
            "expected": scen_e.stress.category,
            "optimistic": scen_o.stress.category,
        }
    }
    
    return ScenarioResponse(
        request_id=req_id,
        computed_at=now_str,
        target_year=req.property.target_year,
        conservative=scen_c,
        expected=scen_e,
        optimistic=scen_o,
        comparison_table=comparison_table
    )


@router.post("/stress-score", response_model=StressScoreResponse)
def calculate_stress_score(req: StressScoreRequest):
    """
    Calculate stress score standalone given pre-computed values.
    """
    req_id = str(uuid.uuid4())
    now_str = datetime.utcnow().isoformat() + "Z"
    
    result = StressScoreEngine.calculate(
        goal_gap_inr=req.goal_gap_inr,
        future_property_cost_inr=req.future_property_cost_inr,
        real_wealth_inr=req.real_wealth_inr,
        monthly_expenses_aed=req.monthly_expenses_aed,
        monthly_salary_aed=req.monthly_salary_aed,
        risk_tolerance=req.risk_tolerance
    )
    
    return StressScoreResponse(
        request_id=req_id,
        computed_at=now_str,
        result=result
    )


@router.post("/property-analysis", response_model=PropertyAnalysisResponse)
def analyze_property(req: PropertyAnalysisRequest):
    """
    Standalone endpoint to see only property appreciation across scenarios.
    """
    req_id = str(uuid.uuid4())
    now_str = datetime.utcnow().isoformat() + "Z"
    
    scen_c = PropertyEngine.calculate(req.sqft, req.current_price_per_sqft_inr, req.target_year, "conservative")
    scen_e = PropertyEngine.calculate(req.sqft, req.current_price_per_sqft_inr, req.target_year, "expected")
    scen_o = PropertyEngine.calculate(req.sqft, req.current_price_per_sqft_inr, req.target_year, "optimistic")
    
    years = req.target_year - CURRENT_YEAR
    
    insight = f"In {years} years, the property is expected to cost ₹{scen_e.future_value_inr:,.0f}."
    
    return PropertyAnalysisResponse(
        request_id=req_id,
        computed_at=now_str,
        sqft=req.sqft,
        current_price_per_sqft_inr=req.current_price_per_sqft_inr,
        target_year=req.target_year,
        years_remaining=years,
        current_value_inr=scen_e.current_value_inr,
        scenarios={
            "conservative": scen_c,
            "expected": scen_e,
            "optimistic": scen_o
        },
        insight=insight
    )
