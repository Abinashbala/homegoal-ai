"""
HomeGoal AI — Pydantic Request Schemas
"""
from __future__ import annotations
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Literal, Optional
from datetime import date

from backend.config import (
    MIN_SALARY_AED, MAX_SALARY_AED,
    MIN_SQFT, MAX_SQFT,
    MIN_PRICE_PER_SQFT, MAX_PRICE_PER_SQFT,
    MIN_TARGET_YEAR, MAX_TARGET_YEAR,
    CURRENT_YEAR,
)

ScenarioName = Literal["conservative", "expected", "optimistic"]
RiskTolerance = Literal["conservative", "moderate", "aggressive"]


class PropertyInput(BaseModel):
    """Property being targeted for purchase."""
    sqft: float = Field(
        ..., gt=0, description="Property size in square feet",
        examples=[1200]
    )
    current_price_per_sqft_inr: float = Field(
        ..., gt=0, description="Current market price per sqft in INR",
        examples=[8500]
    )
    target_year: int = Field(
        ..., description="Year the user intends to purchase",
        examples=[2031]
    )
    city: Optional[str] = Field(
        None, description="Target city (informational, no price adjustment)",
        examples=["Chennai"]
    )
    locality: Optional[str] = Field(
        None, description="Target locality/area",
        examples=["Porur"]
    )

    @field_validator("target_year")
    @classmethod
    def validate_target_year(cls, v: int) -> int:
        if v < MIN_TARGET_YEAR:
            raise ValueError(f"target_year must be at least {MIN_TARGET_YEAR} (must be a future year)")
        if v > MAX_TARGET_YEAR:
            raise ValueError(f"target_year must be at most {MAX_TARGET_YEAR}")
        return v


class IncomeInput(BaseModel):
    """UAE-based user income and expense profile."""
    monthly_salary_aed: float = Field(
        ..., gt=0, description="Monthly gross salary in AED",
        examples=[15000]
    )
    monthly_expenses_aed: float = Field(
        ..., ge=0, description="Monthly living expenses in AED",
        examples=[8000]
    )

    @model_validator(mode="after")
    def expenses_below_salary(self) -> "IncomeInput":
        if self.monthly_expenses_aed >= self.monthly_salary_aed:
            raise ValueError("monthly_expenses_aed must be less than monthly_salary_aed")
        return self


class SavingsInput(BaseModel):
    """Current savings and investment profile."""
    current_savings_aed: float = Field(
        default=0.0, ge=0, description="Current liquid savings in AED",
        examples=[50000]
    )
    current_investment_aed: float = Field(
        default=0.0, ge=0, description="Current investment portfolio value in AED",
        examples=[20000]
    )
    monthly_investment_contrib_aed: float = Field(
        default=0.0, ge=0, description="Additional monthly investment contribution in AED",
        examples=[2000]
    )
    savings_return_pct: Optional[float] = Field(
        default=None, ge=0, le=20,
        description="Override savings return %. If None, uses scenario-based rates.",
        examples=[4.0]
    )
    investment_return_pct: Optional[float] = Field(
        default=None, ge=0, le=30,
        description="Override investment return %. If None, uses scenario-based rates.",
        examples=[10.0]
    )


class UserPreferences(BaseModel):
    """User-level preferences that modify scenario behavior."""
    risk_tolerance: RiskTolerance = Field(
        default="moderate",
        description="Risk tolerance for stress score multiplier",
        examples=["moderate"]
    )
    include_rental_savings: bool = Field(
        default=False,
        description="Whether to model potential rental income offset (future)"
    )


class ForecastRequest(BaseModel):
    """
    Full affordability forecast request.
    Used by POST /forecast — the primary endpoint.
    """
    property:     PropertyInput
    income:       IncomeInput
    savings:      SavingsInput = Field(default_factory=SavingsInput)
    preferences:  UserPreferences = Field(default_factory=UserPreferences)

    model_config = {
        "json_schema_extra": {
            "example": {
                "property": {
                    "sqft": 1200,
                    "current_price_per_sqft_inr": 8500,
                    "target_year": 2031,
                    "city": "Chennai",
                    "locality": "Porur"
                },
                "income": {
                    "monthly_salary_aed": 15000,
                    "monthly_expenses_aed": 8000
                },
                "savings": {
                    "current_savings_aed": 50000,
                    "current_investment_aed": 20000,
                    "monthly_investment_contrib_aed": 2000
                },
                "preferences": {
                    "risk_tolerance": "moderate"
                }
            }
        }
    }


class ScenarioRequest(BaseModel):
    """Request for scenario comparison table. Same as ForecastRequest."""
    property:     PropertyInput
    income:       IncomeInput
    savings:      SavingsInput = Field(default_factory=SavingsInput)
    preferences:  UserPreferences = Field(default_factory=UserPreferences)


class StressScoreRequest(BaseModel):
    """
    Standalone stress score request.
    Can be called with pre-computed affordability values.
    """
    goal_gap_inr:            float = Field(..., description="Goal gap in INR (positive = shortfall)")
    future_property_cost_inr: float = Field(..., gt=0, description="Future property cost in INR")
    real_wealth_inr:          float = Field(..., description="Inflation-adjusted future wealth in INR")
    monthly_expenses_aed:     float = Field(..., ge=0, description="Monthly expenses in AED")
    monthly_salary_aed:       float = Field(..., gt=0, description="Monthly salary in AED")
    risk_tolerance:           RiskTolerance = Field(default="moderate")


class PropertyAnalysisRequest(BaseModel):
    """
    Standalone property analysis request.
    Returns current value + future projections for all scenarios.
    """
    sqft: float = Field(..., gt=0, description="Property size in sqft", examples=[1200])
    current_price_per_sqft_inr: float = Field(
        ..., gt=0, description="Current price per sqft in INR", examples=[8500]
    )
    target_year: int = Field(..., description="Target purchase year", examples=[2031])

    @field_validator("target_year")
    @classmethod
    def validate_year(cls, v: int) -> int:
        if v <= CURRENT_YEAR:
            raise ValueError(f"target_year must be greater than {CURRENT_YEAR}")
        if v > MAX_TARGET_YEAR:
            raise ValueError(f"target_year must be at most {MAX_TARGET_YEAR}")
        return v
