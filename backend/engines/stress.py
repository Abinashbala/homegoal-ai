"""
HomeGoal AI — Stress Score Engine
"""
from backend.engines.base import BaseEngine
from backend.config import STRESS_WEIGHTS, STRESS_RISK_MULTIPLIERS, STRESS_BANDS
from backend.schemas.responses import StressScoreResult, StressBreakdown

class StressScoreEngine(BaseEngine):
    """Calculates deterministic financial stress score."""

    @staticmethod
    def calculate(
        goal_gap_inr: float,
        future_property_cost_inr: float,
        real_wealth_inr: float,
        monthly_expenses_aed: float,
        monthly_salary_aed: float,
        risk_tolerance: str = "moderate"
    ) -> StressScoreResult:
        if risk_tolerance not in STRESS_RISK_MULTIPLIERS:
            risk_tolerance = "moderate"

        # 1. Goal Gap Ratio (40%)
        # How big is the gap relative to the property cost?
        # If gap is <= 0 (surplus), ratio is 0.
        if goal_gap_inr <= 0:
            goal_gap_ratio = 0.0
        else:
            goal_gap_ratio = min(1.0, goal_gap_inr / future_property_cost_inr)

        # 2. Expense Ratio (30%)
        # Current lifestyle burden
        if monthly_salary_aed > 0:
            expense_ratio = min(1.0, monthly_expenses_aed / monthly_salary_aed)
        else:
            expense_ratio = 1.0
            
        # Penalize if expenses are > 70% of income
        if expense_ratio > 0.7:
            expense_ratio = min(1.0, expense_ratio * 1.2)

        # 3. Coverage Shortfall (30%)
        # Inverse of wealth coverage. 
        if future_property_cost_inr > 0:
            wealth_coverage = max(0.0, real_wealth_inr / future_property_cost_inr)
            coverage_shortfall = max(0.0, 1.0 - wealth_coverage)
        else:
            coverage_shortfall = 0.0

        # Weighted raw score
        raw_score = (
            (goal_gap_ratio * STRESS_WEIGHTS["goal_gap_ratio"]) +
            (expense_ratio * STRESS_WEIGHTS["expense_ratio"]) +
            (coverage_shortfall * STRESS_WEIGHTS["coverage_shortfall"])
        )

        # Apply risk multiplier
        risk_mult = STRESS_RISK_MULTIPLIERS[risk_tolerance]
        final_score = min(100.0, max(0.0, raw_score * risk_mult * 100))

        # Determine category and explanation
        category = "Unknown"
        explanation = ""
        for (low, high, cat, exp) in STRESS_BANDS:
            if low <= final_score <= high:
                category = cat
                explanation = exp
                break

        # Determine primary driver
        drivers = {
            "High Goal Gap": goal_gap_ratio * STRESS_WEIGHTS["goal_gap_ratio"],
            "High Living Expenses": expense_ratio * STRESS_WEIGHTS["expense_ratio"],
            "Low Wealth Coverage": coverage_shortfall * STRESS_WEIGHTS["coverage_shortfall"]
        }
        primary_driver = max(drivers, key=drivers.get)
        if final_score < 20:
            primary_driver = "None (Goal is well-funded)"
            
        # Determine Recommendation
        if category == "Safe":
            rec = "Proceed with current plan. Consider optimizing tax efficiency."
        elif category == "Comfortable":
            rec = "Maintain savings discipline. Small increases in monthly investment will improve safety margin."
        elif category == "Stretch":
            rec = "Review expenses. Try to increase monthly savings or extend the target timeline by 1-2 years."
        else:
            rec = "High risk of shortfall. Significant changes needed: lower property budget, increase timeline, or drastically increase savings."

        breakdown = StressBreakdown(
            goal_gap_ratio=round(goal_gap_ratio, 4),
            expense_ratio=round(expense_ratio, 4),
            coverage_shortfall=round(coverage_shortfall, 4),
            risk_multiplier=risk_mult,
            weighted_raw_score=round(raw_score, 4)
        )

        return StressScoreResult(
            score=round(final_score, 1),
            category=category,
            primary_driver=primary_driver,
            explanation=explanation,
            recommendation=rec,
            breakdown=breakdown
        )
