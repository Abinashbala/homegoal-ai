"""
HomeGoal AI — Backend Configuration
====================================
Scenario parameters, constants, and paths.
All scenario rates are derived from Phase 4-5 analytics.
"""
import os
import json
from datetime import date

# ── BASE PATHS ─────────────────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTIFACTS_DIR = os.path.join(BASE_DIR, "models", "artifacts")
PROC_DIR      = os.path.join(BASE_DIR, "processed")

# ── APPLICATION ────────────────────────────────────────────────────────
APP_TITLE       = "HomeGoal AI"
APP_DESCRIPTION = (
    "AI-powered home affordability planning platform for UAE expats "
    "buying property in India. Combines personal finance forecasting, "
    "housing market analytics, and scenario planning."
)
APP_VERSION     = "1.0.0"
CONTACT         = {"name": "HomeGoal AI", "url": "https://homegoal.ai"}
LICENSE         = {"name": "Proprietary"}

# ── CURRENT REFERENCE YEAR ─────────────────────────────────────────────
CURRENT_YEAR    = date.today().year        # dynamic
BASE_HPI_YEAR   = 2025
BASE_HPI        = 147.65                   # Q4 2025 NHB HPI value
BASE_AED_INR    = 24.47                    # Dec 2025 AED/INR closing rate

# ── HPI CAGR SCENARIOS (annual rate, decimal) ──────────────────────────
# Source: Phase 4 feature engineering + Phase 5 model validation
HPI_CAGR = {
    "conservative": 0.0319,   # Pre-COVID avg growth (2014-2019)
    "expected":     0.0445,   # Full-period CAGR (2013-2025) — VALIDATED by exp model
    "optimistic":   0.0687,   # Post-COVID avg growth (2021-2025)
}

# ── FX CAGR SCENARIOS (annual rate, decimal) ───────────────────────────
# Source: Phase 5 — Prophet model validated full-period CAGR
FX_CAGR = {
    "conservative": 0.0200,   # Below historical avg (adverse FX)
    "expected":     0.0334,   # Full-period CAGR (2013-2025)
    "optimistic":   0.0428,   # Recent 3-year avg (2022-2025)
}

# ── CPI SCENARIOS (annual rate, decimal) ───────────────────────────────
# Source: Phase 3 EDA — scenario validation confirmed against historical avg 5.55%
CPI = {
    "conservative": 0.075,    # Above historical avg — adverse inflation
    "expected":     0.060,    # Close to historical mean
    "optimistic":   0.040,    # Achieved in 6 of 12 years
}

# ── SAVINGS RETURN SCENARIOS (annual rate, decimal) ────────────────────
SAVINGS_RETURN = {
    "conservative": 0.030,    # Bank FD / low-risk savings
    "expected":     0.045,    # Mixed savings + some fixed income
    "optimistic":   0.055,    # Higher-yield savings
}

# ── INVESTMENT RETURN SCENARIOS (annual rate, decimal) ─────────────────
INVESTMENT_RETURN = {
    "conservative": 0.060,    # Conservative equity/MF returns
    "expected":     0.090,    # Balanced portfolio
    "optimistic":   0.120,    # Aggressive equity allocation
}

# ── STRESS SCORE WEIGHTS ───────────────────────────────────────────────
STRESS_WEIGHTS = {
    "goal_gap_ratio":      0.40,
    "expense_ratio":       0.30,
    "coverage_shortfall":  0.30,
}
STRESS_RISK_MULTIPLIERS = {
    "conservative": 1.20,
    "moderate":     1.00,
    "aggressive":   0.85,
}
STRESS_BANDS = [
    (0,  30,  "Safe",        "Goal is comfortably achievable. Low financial stress."),
    (31, 60,  "Comfortable", "Goal is achievable with moderate savings discipline."),
    (61, 80,  "Stretch",     "Goal requires significant savings effort or timeline adjustment."),
    (81, 100, "Risky",       "Goal creates high financial stress. Reassessment recommended."),
]

# ── VALIDATION LIMITS ──────────────────────────────────────────────────
MIN_SALARY_AED       = 1_000
MAX_SALARY_AED       = 500_000
MIN_SQFT             = 100
MAX_SQFT             = 50_000
MIN_PRICE_PER_SQFT   = 500       # INR
MAX_PRICE_PER_SQFT   = 100_000   # INR
MIN_TARGET_YEAR      = CURRENT_YEAR + 1
MAX_TARGET_YEAR      = CURRENT_YEAR + 30
MIN_SAVINGS          = 0
MAX_SAVINGS          = 100_000_000   # AED 100M

# ── LOAD MODEL METRICS (for analytics endpoints) ───────────────────────
def load_model_metrics() -> dict:
    """Load Phase 5 model selection summary from artifacts."""
    path = os.path.join(ARTIFACTS_DIR, "model_selection_summary.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def load_scenario_parameters() -> dict:
    """Load Phase 5 scenario_parameters.json."""
    path = os.path.join(ARTIFACTS_DIR, "scenario_parameters.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}
