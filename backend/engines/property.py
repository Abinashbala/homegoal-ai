"""
HomeGoal AI — Property Engine
"""
from backend.engines.base import BaseEngine
from backend.config import HPI_CAGR, CURRENT_YEAR
from backend.schemas.responses import PropertyValues

class PropertyEngine(BaseEngine):
    """Calculates current and future property values using HPI CAGR scenarios."""

    @staticmethod
    def calculate(sqft: float, current_price_per_sqft_inr: float, target_year: int, scenario: str) -> PropertyValues:
        if scenario not in HPI_CAGR:
            raise ValueError(f"Invalid scenario: {scenario}")
        if target_year <= CURRENT_YEAR:
            raise ValueError("Target year must be in the future")

        current_value_inr = sqft * current_price_per_sqft_inr
        years = target_year - CURRENT_YEAR
        
        cagr = HPI_CAGR[scenario]
        future_value_inr = current_value_inr * ((1 + cagr) ** years)
        
        appreciation_pct = ((future_value_inr / current_value_inr) - 1) * 100

        return PropertyValues(
            current_value_inr=round(current_value_inr, 2),
            future_value_inr=round(future_value_inr, 2),
            appreciation_pct=round(appreciation_pct, 2),
            hpi_cagr_used_pct=round(cagr * 100, 2)
        )
