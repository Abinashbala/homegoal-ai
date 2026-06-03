"""
HomeGoal AI — Wealth Engine
"""
from backend.engines.base import BaseEngine
from backend.config import CURRENT_YEAR, SAVINGS_RETURN, INVESTMENT_RETURN

class WealthEngine(BaseEngine):
    """Calculates future nominal wealth in AED based on savings and investment returns."""

    @staticmethod
    def calculate_future_wealth(
        current_savings_aed: float,
        current_investment_aed: float,
        monthly_savings_aed: float,
        monthly_investment_aed: float,
        target_year: int,
        scenario: str,
        custom_savings_return: float | None = None,
        custom_inv_return: float | None = None
    ) -> float:
        if scenario not in SAVINGS_RETURN:
            raise ValueError(f"Invalid scenario: {scenario}")
            
        years = target_year - CURRENT_YEAR
        months = years * 12
        
        # Determine rates (decimal format)
        r_sav = custom_savings_return / 100.0 if custom_savings_return is not None else SAVINGS_RETURN[scenario]
        r_inv = custom_inv_return / 100.0 if custom_inv_return is not None else INVESTMENT_RETURN[scenario]
        
        # Monthly rates
        r_sav_m = r_sav / 12
        r_inv_m = r_inv / 12
        
        # Future value of current balances (Compound Interest)
        fv_current_savings = current_savings_aed * ((1 + r_sav) ** years)
        fv_current_investment = current_investment_aed * ((1 + r_inv) ** years)
        
        # Future value of monthly contributions (Annuity)
        # FV = P * [ ((1 + r)^n - 1) / r ]
        if r_sav_m > 0:
            fv_monthly_savings = monthly_savings_aed * (((1 + r_sav_m) ** months - 1) / r_sav_m)
        else:
            fv_monthly_savings = monthly_savings_aed * months
            
        if r_inv_m > 0:
            fv_monthly_inv = monthly_investment_aed * (((1 + r_inv_m) ** months - 1) / r_inv_m)
        else:
            fv_monthly_inv = monthly_investment_aed * months
            
        total_future_wealth = fv_current_savings + fv_current_investment + fv_monthly_savings + fv_monthly_inv
        return total_future_wealth
