"""
HomeGoal AI — Currency Engine
"""
from backend.engines.base import BaseEngine
from backend.config import CURRENT_YEAR, FX_CAGR, BASE_AED_INR

class CurrencyEngine(BaseEngine):
    """Calculates projected AED-INR exchange rates and converts wealth."""

    @staticmethod
    def calculate_conversion(
        aed_amount: float,
        target_year: int,
        scenario: str
    ) -> tuple[float, float, float]:
        """
        Returns (projected_fx_rate, converted_inr_amount, fx_tailwind_pct)
        """
        if scenario not in FX_CAGR:
            raise ValueError(f"Invalid scenario: {scenario}")
            
        years = target_year - CURRENT_YEAR
        cagr = FX_CAGR[scenario]
        
        projected_rate = BASE_AED_INR * ((1 + cagr) ** years)
        converted_inr = aed_amount * projected_rate
        
        fx_tailwind_pct = ((projected_rate / BASE_AED_INR) - 1) * 100
        
        return projected_rate, converted_inr, fx_tailwind_pct
