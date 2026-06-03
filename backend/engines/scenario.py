"""
HomeGoal AI — Scenario Engine
"""
from backend.engines.base import BaseEngine
from backend.engines.property import PropertyEngine
from backend.engines.wealth import WealthEngine
from backend.engines.inflation import InflationEngine
from backend.engines.currency import CurrencyEngine
from backend.engines.stress import StressScoreEngine
from backend.schemas.requests import ForecastRequest
from backend.schemas.responses import SingleScenarioResult, WealthValues, AffordabilityKPIs
from backend.config import CURRENT_YEAR

class ScenarioEngine(BaseEngine):
    """Orchestrates all other engines to build a complete scenario projection."""

    @staticmethod
    def generate_scenario(req: ForecastRequest, scenario: str) -> SingleScenarioResult:
        # 1. Property Engine
        prop_vals = PropertyEngine.calculate(
            sqft=req.property.sqft,
            current_price_per_sqft_inr=req.property.current_price_per_sqft_inr,
            target_year=req.property.target_year,
            scenario=scenario
        )

        # 2. Wealth Engine (Nominal AED)
        monthly_savings_aed = req.income.monthly_salary_aed - req.income.monthly_expenses_aed
        future_wealth_aed = WealthEngine.calculate_future_wealth(
            current_savings_aed=req.savings.current_savings_aed,
            current_investment_aed=req.savings.current_investment_aed,
            monthly_savings_aed=monthly_savings_aed,
            monthly_investment_aed=req.savings.monthly_investment_contrib_aed,
            target_year=req.property.target_year,
            scenario=scenario,
            custom_savings_return=req.savings.savings_return_pct,
            custom_inv_return=req.savings.investment_return_pct
        )

        # 3. Currency Engine (AED -> INR)
        proj_rate, nominal_wealth_inr, fx_tailwind = CurrencyEngine.calculate_conversion(
            aed_amount=future_wealth_aed,
            target_year=req.property.target_year,
            scenario=scenario
        )

        # 4. Inflation Engine (Nominal INR -> Real INR)
        real_wealth_inr, cpi_mult = InflationEngine.calculate_real_wealth(
            nominal_wealth=nominal_wealth_inr,
            target_year=req.property.target_year,
            scenario=scenario
        )

        # Pack Wealth Values
        wealth_vals = WealthValues(
            future_wealth_aed=round(future_wealth_aed, 2),
            fx_rate_at_target=round(proj_rate, 4),
            future_wealth_inr_nominal=round(nominal_wealth_inr, 2),
            real_wealth_inr=round(real_wealth_inr, 2),
            cumulative_inflation_mult=round(cpi_mult, 4),
            monthly_savings_aed=round(monthly_savings_aed, 2),
            monthly_savings_rate_pct=round((monthly_savings_aed / req.income.monthly_salary_aed) * 100, 2)
        )

        # 5. Affordability KPIs
        if prop_vals.future_value_inr > 0:
            affordability_ratio = real_wealth_inr / prop_vals.future_value_inr
        else:
            affordability_ratio = 0.0
            
        goal_gap_inr = prop_vals.future_value_inr - real_wealth_inr
        
        years = req.property.target_year - CURRENT_YEAR
        months = years * 12
        
        if goal_gap_inr > 0:
            req_extra_inr = goal_gap_inr / months
            req_extra_aed = req_extra_inr / proj_rate
            gap_label = f"Shortfall of ₹{goal_gap_inr:,.0f}"
            if affordability_ratio < 0.5:
                aff_label = "Difficult"
            elif affordability_ratio < 0.95:
                aff_label = "Partial"
            else:
                aff_label = "Near Goal"
        else:
            req_extra_inr = 0.0
            req_extra_aed = 0.0
            gap_label = f"Surplus of ₹{abs(goal_gap_inr):,.0f}"
            if affordability_ratio > 1.2:
                aff_label = "Comfortable"
            else:
                aff_label = "At Goal"
                
        coverage_pct = affordability_ratio * 100

        kpis = AffordabilityKPIs(
            affordability_ratio=round(affordability_ratio, 3),
            affordability_label=aff_label,
            goal_gap_inr=round(goal_gap_inr, 2),
            goal_gap_label=gap_label,
            required_extra_savings_inr=round(req_extra_inr, 2),
            required_extra_savings_aed=round(req_extra_aed, 2),
            wealth_coverage_pct=round(coverage_pct, 1),
            fx_tailwind_pct=round(fx_tailwind, 2),
            years_remaining=years
        )

        # 6. Stress Score Engine
        stress_result = StressScoreEngine.calculate(
            goal_gap_inr=goal_gap_inr,
            future_property_cost_inr=prop_vals.future_value_inr,
            real_wealth_inr=real_wealth_inr,
            monthly_expenses_aed=req.income.monthly_expenses_aed,
            monthly_salary_aed=req.income.monthly_salary_aed,
            risk_tolerance=req.preferences.risk_tolerance
        )

        return SingleScenarioResult(
            scenario=scenario,
            property=prop_vals,
            wealth=wealth_vals,
            kpis=kpis,
            stress=stress_result
        )
