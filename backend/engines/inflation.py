"""
HomeGoal AI — Inflation Engine
"""
from backend.engines.base import BaseEngine
from backend.config import CURRENT_YEAR, CPI

class InflationEngine(BaseEngine):
    """Calculates inflation adjustments for wealth to derive real purchasing power."""

    @staticmethod
    def calculate_real_wealth(
        nominal_wealth: float,
        target_year: int,
        scenario: str
    ) -> tuple[float, float]:
        """
        Returns (real_wealth, cumulative_inflation_multiplier)
        real_wealth = nominal_wealth / (1 + inflation_rate)^years
        """
        if scenario not in CPI:
            raise ValueError(f"Invalid scenario: {scenario}")
            
        years = target_year - CURRENT_YEAR
        inflation_rate = CPI[scenario]
        
        cumulative_mult = (1 + inflation_rate) ** years
        real_wealth = nominal_wealth / cumulative_mult
        
        return real_wealth, cumulative_mult
