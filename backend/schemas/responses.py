"""
HomeGoal AI — Pydantic Response Schemas
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, Any


# ── Shared sub-schemas ─────────────────────────────────────────────────

class PropertyValues(BaseModel):
    current_value_inr:  float = Field(..., description="Current property value in INR")
    future_value_inr:   float = Field(..., description="Future property value at target year in INR")
    appreciation_pct:   float = Field(..., description="Total % appreciation from now to target year")
    hpi_cagr_used_pct:  float = Field(..., description="HPI CAGR rate applied (%)")


class WealthValues(BaseModel):
    future_wealth_aed:          float = Field(..., description="Projected future wealth in AED (nominal)")
    fx_rate_at_target:          float = Field(..., description="Projected AED/INR rate at target year")
    future_wealth_inr_nominal:  float = Field(..., description="Future wealth converted to INR (nominal)")
    real_wealth_inr:            float = Field(..., description="Future wealth in INR, inflation-adjusted")
    cumulative_inflation_mult:  float = Field(..., description="Inflation multiplier over the period")
    monthly_savings_aed:        float = Field(..., description="Monthly savings capacity (salary - expenses)")
    monthly_savings_rate_pct:   float = Field(..., description="Savings rate as % of income")


class AffordabilityKPIs(BaseModel):
    affordability_ratio:            float  = Field(..., description="real_wealth / future_property_value")
    affordability_label:            str    = Field(..., description="Difficult / Partial / At Goal / Comfortable")
    goal_gap_inr:                   float  = Field(..., description="Shortfall (positive) or surplus (negative) in INR")
    goal_gap_label:                 str    = Field(..., description="Human-readable gap description")
    required_extra_savings_inr:     float  = Field(..., description="Additional monthly INR savings to close gap")
    required_extra_savings_aed:     float  = Field(..., description="Additional monthly AED savings to close gap")
    wealth_coverage_pct:            float  = Field(..., description="% of property cost covered by wealth")
    fx_tailwind_pct:                float  = Field(..., description="Total FX tailwind over horizon (%)")
    years_remaining:                int    = Field(..., description="Years to target year")


class StressBreakdown(BaseModel):
    goal_gap_ratio:      float = Field(..., description="Normalized goal gap signal [0–1]")
    expense_ratio:       float = Field(..., description="Expense burden signal [0–1]")
    coverage_shortfall:  float = Field(..., description="Coverage shortfall signal [0–1]")
    risk_multiplier:     float = Field(..., description="Risk tolerance multiplier applied")
    weighted_raw_score:  float = Field(..., description="Pre-scaled raw score before ×100")


class StressScoreResult(BaseModel):
    score:          float         = Field(..., ge=0, le=100, description="Stress score 0–100")
    category:       str           = Field(..., description="Safe / Comfortable / Stretch / Risky")
    primary_driver: str           = Field(..., description="Which signal contributes most")
    explanation:    str           = Field(..., description="Plain-English explanation of the score")
    recommendation: str           = Field(..., description="Actionable advice")
    breakdown:      StressBreakdown


class SingleScenarioResult(BaseModel):
    scenario:     str            = Field(..., description="conservative / expected / optimistic")
    property:     PropertyValues
    wealth:       WealthValues
    kpis:         AffordabilityKPIs
    stress:       StressScoreResult


# ── Primary response schemas ───────────────────────────────────────────

class ForecastResponse(BaseModel):
    """
    Full affordability forecast — response to POST /forecast.
    Contains all three scenarios + summary metadata.
    """
    request_id:    str
    computed_at:   str
    years_horizon: int
    target_year:   int
    current_year:  int
    city:          Optional[str] = None
    locality:      Optional[str] = None
    conservative:  SingleScenarioResult
    expected:      SingleScenarioResult
    optimistic:    SingleScenarioResult
    summary: Dict[str, Any] = Field(
        ..., description="Quick-glance summary with recommended scenario highlighted"
    )


class ScenarioResponse(BaseModel):
    """Response to POST /scenarios — scenario comparison table."""
    request_id:   str
    computed_at:  str
    target_year:  int
    conservative: SingleScenarioResult
    expected:     SingleScenarioResult
    optimistic:   SingleScenarioResult
    comparison_table: Dict[str, Any] = Field(
        ..., description="Side-by-side KPI comparison across scenarios"
    )


class StressScoreResponse(BaseModel):
    """Response to POST /stress-score."""
    request_id:   str
    computed_at:  str
    result:       StressScoreResult


class PropertyAnalysisResponse(BaseModel):
    """Response to POST /property-analysis."""
    request_id:           str
    computed_at:          str
    sqft:                 float
    current_price_per_sqft_inr: float
    target_year:          int
    years_remaining:      int
    current_value_inr:    float
    scenarios: Dict[str, PropertyValues]
    insight:              str = Field(..., description="Key insight about this property")


# ── Utility responses ──────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status:   Literal["ok", "degraded"] = "ok"
    version:  str
    engines:  Dict[str, str]
    timestamp: str


class VersionResponse(BaseModel):
    version:      str
    app_name:     str
    description:  str
    phase:        str
    engines:      list[str]
    data_vintage: str


class ModelMetricsResponse(BaseModel):
    """Response to GET /model-metrics (recruiter analytics endpoint)."""
    hpi_model_comparison: list[Dict[str, Any]]
    fx_model_comparison:  list[Dict[str, Any]]
    selected_hpi_model:   str
    selected_fx_model:    str
    production_approach:  str
    validation_note:      str


class ModelComparisonResponse(BaseModel):
    """Response to GET /model-comparison."""
    hpi: Dict[str, Any]
    fx:  Dict[str, Any]
    scenario_parameters: Dict[str, Any]
    selection_rationale: str
