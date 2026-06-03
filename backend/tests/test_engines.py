"""
HomeGoal AI — Unit Tests
"""
import pytest
from datetime import date
from backend.config import CURRENT_YEAR
from backend.engines.property import PropertyEngine
from backend.engines.wealth import WealthEngine
from backend.engines.inflation import InflationEngine
from backend.engines.currency import CurrencyEngine
from backend.engines.stress import StressScoreEngine
from backend.engines.scenario import ScenarioEngine
from backend.schemas.requests import ForecastRequest

def test_property_engine():
    res = PropertyEngine.calculate(sqft=1000, current_price_per_sqft_inr=5000, target_year=CURRENT_YEAR + 5, scenario="expected")
    assert res.current_value_inr == 5_000_000
    assert res.future_value_inr > 5_000_000
    assert res.appreciation_pct > 0

def test_wealth_engine():
    res = WealthEngine.calculate_future_wealth(
        current_savings_aed=10000,
        current_investment_aed=5000,
        monthly_savings_aed=2000,
        monthly_investment_aed=1000,
        target_year=CURRENT_YEAR + 5,
        scenario="expected"
    )
    assert res > (10000 + 5000 + (2000*60) + (1000*60))

def test_inflation_engine():
    nominal = 10_000_000
    real, mult = InflationEngine.calculate_real_wealth(nominal, target_year=CURRENT_YEAR + 5, scenario="expected")
    assert real < nominal
    assert mult > 1.0

def test_currency_engine():
    aed_amount = 100_000
    rate, inr, tailwind = CurrencyEngine.calculate_conversion(aed_amount, target_year=CURRENT_YEAR + 5, scenario="expected")
    assert rate > 24.0
    assert inr == aed_amount * rate

def test_stress_score_engine():
    res = StressScoreEngine.calculate(
        goal_gap_inr=5_000_000,
        future_property_cost_inr=15_000_000,
        real_wealth_inr=10_000_000,
        monthly_expenses_aed=8000,
        monthly_salary_aed=15000,
        risk_tolerance="moderate"
    )
    assert 0 <= res.score <= 100
    assert res.category in ["Safe", "Comfortable", "Stretch", "Risky"]

def test_scenario_engine():
    req = ForecastRequest(
        property={"sqft": 1200, "current_price_per_sqft_inr": 8500, "target_year": CURRENT_YEAR + 6},
        income={"monthly_salary_aed": 20000, "monthly_expenses_aed": 10000},
        savings={"current_savings_aed": 50000, "current_investment_aed": 0, "monthly_investment_contrib_aed": 0},
        preferences={"risk_tolerance": "moderate"}
    )
    res = ScenarioEngine.generate_scenario(req, "expected")
    assert res.scenario == "expected"
    assert res.property.future_value_inr > 0
    assert res.wealth.future_wealth_aed > 0
    assert res.kpis.affordability_ratio >= 0
    assert res.stress.score >= 0
