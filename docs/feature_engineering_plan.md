# HomeGoal AI — Feature Engineering Plan

**Version:** 1.0  
**Date:** 2026-06-02  
**Status:** Complete  

---

## 1. Overview

Feature engineering transforms the three cleaned datasets plus user inputs into the computational signals needed by every engine in the HomeGoal AI platform. This plan documents every derived feature, its formula, data source, and which platform module consumes it.

Features are organized into five groups:

| Group | Description |
|---|---|
| A — Time-Series Features | Derived from historical dataset trends |
| B — User Financial Features | Derived from user profile inputs |
| C — Property Features | Derived from user property inputs |
| D — Forecast Features | Model output signals used downstream |
| E — Scenario Features | Scenario-specific parameterized values |

---

## 2. Group A — Time-Series Features

These features are derived from the cleaned historical datasets during the EDA and modeling phase. They power the forecasting models.

### A1 — NHB HPI Features

| Feature | Formula | Source | Used In |
|---|---|---|---|
| `hpi_qoq_growth` | `(HPI_t / HPI_{t-1}) - 1` | NHB HPI (quarterly) | EDA, housing model |
| `hpi_yoy_growth` | `(HPI_t / HPI_{t-4}) - 1` | NHB HPI (quarterly) | Housing model training |
| `hpi_cagr_full` | `(HPI_end / HPI_start)^(1/n) - 1` where n = years | NHB HPI (annual) | Scenario assumptions |
| `hpi_cagr_5yr` | CAGR over last 5 years | NHB HPI (annual) | Short-horizon forecasting |
| `hpi_cagr_3yr` | CAGR over last 3 years | NHB HPI (annual) | Recent trend weighting |
| `hpi_rolling_4q_avg` | 4-quarter rolling mean of HPI | NHB HPI (quarterly) | Smoothed trend for Prophet |
| `hpi_rolling_4q_std` | 4-quarter rolling std of HPI | NHB HPI (quarterly) | Volatility measure |
| `hpi_pre_covid_cagr` | CAGR from 2013 to 2019 | NHB HPI | Conservative scenario anchor |
| `hpi_post_covid_cagr` | CAGR from 2020 to 2024 | NHB HPI | Optimistic scenario anchor |

**Derivation logic for CAGR:**
```
CAGR = (End_Value / Start_Value) ^ (1 / Number_of_Years) - 1
```

**Expected values:**
- Full period CAGR (2013–2025): ~4.8% per year (Assessment)
- Pre-COVID CAGR (2013–2019): ~3.5% per year
- Post-COVID CAGR (2020–2024): ~6.1% per year

---

### A2 — Inflation Features

| Feature | Formula | Source | Used In |
|---|---|---|---|
| `cpi_rolling_3yr_avg` | 3-year rolling average of annual CPI | World Bank CPI | Scenario calibration |
| `cpi_rolling_5yr_avg` | 5-year rolling average of annual CPI | World Bank CPI | Long-horizon inflation assumption |
| `cumulative_inflation_index` | `∏(1 + CPI_t/100)` from base year | World Bank CPI | Real wealth deflation |
| `real_rate_of_return` | `((1 + nominal_return) / (1 + inflation)) - 1` | CPI + investment input | Adjusted wealth growth |
| `inflation_forecast_conservative` | 3-year avg + 1.5σ | CPI | Conservative scenario |
| `inflation_forecast_expected` | 5-year rolling avg | CPI | Expected scenario |
| `inflation_forecast_optimistic` | Min of 3yr and 5yr avg | CPI | Optimistic scenario |

---

### A3 — Exchange Rate Features

| Feature | Formula | Source | Used In |
|---|---|---|---|
| `fx_mom_change` | `(Rate_t / Rate_{t-1}) - 1` | AED-INR monthly | FX model training |
| `fx_yoy_change` | `(Rate_t / Rate_{t-12}) - 1` | AED-INR monthly | Annual trend signal |
| `fx_cagr_full` | CAGR of annual avg rate 2013–2025 | AED-INR annual | Scenario assumptions |
| `fx_cagr_3yr` | CAGR of last 3 years | AED-INR annual | Near-term FX trend |
| `fx_rolling_12m_avg` | 12-month rolling mean | AED-INR monthly | Smoothed rate for Prophet |
| `fx_rolling_12m_std` | 12-month rolling std | AED-INR monthly | Volatility measure |
| `fx_volatility_band_upper` | `rolling_avg + 2σ` | AED-INR monthly | Scenario range |
| `fx_volatility_band_lower` | `rolling_avg - 2σ` | AED-INR monthly | Scenario range |

**Expected values:**
- Full period CAGR: ~4.3% per year (INR weakening vs AED)
- Recent 3yr CAGR (2022–2025): ~5.8% per year

---

## 3. Group B — User Financial Features

Computed from user profile inputs at runtime.

| Feature | Formula | Description |
|---|---|---|
| `monthly_savings_aed` | `salary - expenses` | Monthly amount saved in AED |
| `savings_rate_pct` | `(monthly_savings / salary) × 100` | What percentage of salary is saved |
| `annual_savings_aed` | `monthly_savings × 12` | Annual savings amount |
| `expense_ratio_pct` | `(expenses / salary) × 100` | Expenses as % of salary (burn rate) |
| `years_to_goal` | `target_year - current_year` | Remaining years to hit purchase target |
| `total_liquid_wealth_aed` | `savings + investment_value` | Combined financial starting position |

---

### B1 — Future Wealth Projection (Core Engine)

The wealth engine projects the user's total AED wealth at the target purchase year.

**Components:**

#### Savings Growth (Compound)
```
FW_savings = current_savings × (1 + r_savings)^n
           + monthly_savings × [((1 + r_savings)^n - 1) / r_savings]
```
Where:
- `r_savings` = assumed savings interest rate (scenario-dependent, e.g., 3–4%)
- `n` = years to goal

**Note:** For the MVP, savings are treated as low-yield savings/deposits. Investment growth is modeled separately.

#### Investment Growth (Compound, Optional)
```
FW_investment = current_investment × (1 + r_invest)^n
              + monthly_contribution × [((1 + r_invest)^n - 1) / r_invest]
```
Where:
- `r_invest` = user-supplied expected return (or scenario default)

#### Total Future Wealth
```
future_wealth_aed = FW_savings + FW_investment
```

---

### B2 — Wealth Conversion (AED → INR)

```
future_wealth_inr = future_wealth_aed × fx_rate_forecast
```

Where `fx_rate_forecast` is the projected AED/INR exchange rate at the target year, generated by the FX forecasting model.

---

### B3 — Real Wealth (Inflation-Adjusted)

```
real_wealth_inr = future_wealth_inr / cumulative_inflation_index

cumulative_inflation_index = ∏(1 + cpi_t/100) for t in [current_year, target_year]
```

This converts nominal future INR wealth to **today's purchasing power equivalents**.

---

## 4. Group C — Property Features

Computed from user property inputs at runtime.

| Feature | Formula | Description |
|---|---|---|
| `current_property_value_inr` | `size_sqft × price_per_sqft` | Property baseline in INR |
| `current_property_value_lakhs` | `value_inr / 100,000` | Display in Lakhs |
| `current_property_value_crore` | `value_inr / 10,000,000` | Display in Crore |
| `future_property_cost_inr` | `current_value × (1 + hpi_cagr)^n` | Projected property price at target year |
| `future_property_cost_lakhs` | `future_cost / 100,000` | Display in Lakhs |
| `future_property_cost_crore` | `future_cost / 10,000,000` | Display in Crore |
| `appreciation_amount_inr` | `future_cost - current_value` | Total price increase expected |
| `appreciation_pct` | `(future_cost / current_value - 1) × 100` | % property will grow |

**Formula for future property cost:**
```
future_property_cost = current_property_value × (1 + hpi_cagr)^years_to_goal
```

Where `hpi_cagr` is scenario-specific (see Group E).

---

## 5. Group D — Forecast Features (Model Outputs)

These are output signals generated by the three ML models. They become inputs to the affordability engine and stress score engine.

| Feature | Model | Description |
|---|---|---|
| `hpi_forecast_value` | Housing Model | Predicted HPI at target year |
| `hpi_forecast_cagr` | Housing Model | Implied CAGR from model output |
| `hpi_forecast_lower` | Housing Model | Lower confidence bound |
| `hpi_forecast_upper` | Housing Model | Upper confidence bound |
| `cpi_forecast_pct` | Inflation Model | Predicted annual CPI at target year |
| `cpi_forecast_cumulative` | Inflation Model | Cumulative inflation multiplier to target year |
| `fx_forecast_rate` | FX Model | Predicted AED/INR rate at target year |
| `fx_forecast_lower` | FX Model | Lower bound AED/INR |
| `fx_forecast_upper` | FX Model | Upper bound AED/INR |

---

## 6. Group E — Scenario Features

Each of the three scenarios (Conservative, Expected, Optimistic) uses a distinct set of parameter assumptions.

### Scenario Parameter Table

| Parameter | Conservative | Expected | Optimistic | Source |
|---|---|---|---|---|
| `hpi_cagr` | 3.0% | 4.8% | 7.0% | NHB HPI historical ranges |
| `cpi_annual` | 7.5% | 6.0% | 4.0% | World Bank CPI ranges |
| `fx_annual_growth` | 2.0% | 4.3% | 6.5% | AED-INR CAGR ranges |
| `savings_rate_assumed` | 3.0% | 4.0% | 5.0% | Savings deposit rate proxy |
| `investment_return` | 6.0% | 9.0% | 12.0% | Market return ranges |

**Scenario interpretation:**
- **Conservative:** Slowest housing growth, highest inflation, weakest INR gain. User has less purchasing power.
- **Expected:** Based on historical averages across all three datasets.
- **Optimistic:** Fastest housing growth, low inflation, strong INR depreciation (more INR per AED). Most favorable conditions.

### Scenario Output Features

For each scenario, the following are computed:

| Feature | Description |
|---|---|
| `scenario_future_property_cost` | Projected property price |
| `scenario_future_wealth_nominal` | Projected AED wealth in nominal INR |
| `scenario_future_wealth_real` | Inflation-adjusted INR wealth |
| `scenario_goal_gap` | Property cost − real wealth |
| `scenario_coverage_ratio` | Real wealth / property cost |
| `scenario_stress_score` | 0–100 stress score |
| `scenario_monthly_saving_needed` | Extra monthly saving needed to close gap |

---

## 7. Group F — Stress Score Engine (Rule-Based)

The stress score is a **composite index** ranging 0–100. It does NOT use machine learning — it uses deterministic, explainable business rules.

### Input Signals

| Signal | Weight | Description |
|---|---|---|
| `goal_gap_ratio` | 40% | `max(0, goal_gap / property_cost)` — how large is the gap as % of property cost |
| `expense_ratio` | 30% | `expenses / salary` — how stretched is the user's current budget |
| `wealth_coverage_ratio` | 30% | `1 - min(1, real_wealth / property_cost)` — inverted coverage |

### Stress Score Formula

```python
def compute_stress_score(
    goal_gap_inr: float,
    future_property_cost_inr: float,
    monthly_expenses_aed: float,
    monthly_salary_aed: float,
    future_wealth_real_inr: float,
    risk_tolerance: str  # 'conservative', 'moderate', 'aggressive'
) -> float:

    # Signal 1: Goal gap as ratio of property cost (0 = no gap, 1 = full gap)
    goal_gap_ratio = max(0.0, goal_gap_inr / future_property_cost_inr)

    # Signal 2: Burn rate (expense ratio)
    expense_ratio = monthly_expenses_aed / monthly_salary_aed

    # Signal 3: Shortfall on wealth coverage (0 = fully covered, 1 = zero coverage)
    coverage = min(1.0, future_wealth_real_inr / future_property_cost_inr)
    coverage_shortfall = 1.0 - coverage

    # Risk tolerance adjustment
    tolerance_multiplier = {
        'conservative': 1.20,   # Penalizes stress more
        'moderate': 1.00,       # No adjustment
        'aggressive': 0.85,     # Slight downward adjustment
    }[risk_tolerance]

    # Weighted raw score (0 to 1)
    raw_score = (
        0.40 * goal_gap_ratio +
        0.30 * expense_ratio +
        0.30 * coverage_shortfall
    ) * tolerance_multiplier

    # Scale to 0–100 and clip
    stress_score = min(100.0, max(0.0, raw_score * 100))
    return round(stress_score, 1)
```

### Stress Score Categories

| Score Range | Category | Meaning |
|---|---|---|
| 0 – 30 | 🟢 Safe | Wealth will comfortably cover the property. Goal is highly achievable. |
| 31 – 60 | 🟡 Comfortable | Goal is achievable with consistent discipline. Minor adjustments may help. |
| 61 – 80 | 🟠 Stretch | Goal is ambitious. Significant savings discipline or longer timeline needed. |
| 81 – 100 | 🔴 Risky | Goal is very difficult with current parameters. Reconsider timeline or budget. |

### Stress Score Explainability (Required)

Every stress score output must include:
1. **Primary driver** — which signal contributed most
2. **Breakdown** — contribution of each of the 3 signals
3. **Recommendation** — one actionable suggestion

---

## 8. Feature Computation Order (Pipeline)

```
Step 1: Load cleaned datasets (HPI, CPI, FX)
Step 2: Compute time-series features (Group A)
Step 3: Train forecasting models (HPI, CPI, FX models)
Step 4: Accept user inputs
Step 5: Compute user financial features (Group B)
Step 6: Compute property features (Group C)
Step 7: Run forecasting models → generate Group D features
Step 8: Apply scenario parameters → compute Group E features per scenario
Step 9: Compute stress scores (Group F) per scenario
Step 10: Return all results to frontend
```

---

## 9. Feature Summary Table

| Feature | Group | Runtime | Scenario-Specific |
|---|---|---|---|
| `hpi_cagr_full` | A | Pre-computed | No |
| `fx_cagr_full` | A | Pre-computed | No |
| `cpi_rolling_5yr_avg` | A | Pre-computed | No |
| `monthly_savings_aed` | B | Runtime | No |
| `future_wealth_aed` | B | Runtime | Yes |
| `future_wealth_inr` | B | Runtime | Yes |
| `real_wealth_inr` | B | Runtime | Yes |
| `current_property_value_inr` | C | Runtime | No |
| `future_property_cost_inr` | C | Runtime | Yes |
| `goal_gap_inr` | C | Runtime | Yes |
| `hpi_forecast_value` | D | Model output | Yes |
| `fx_forecast_rate` | D | Model output | Yes |
| `scenario_stress_score` | E + F | Runtime | Yes |

---

## 10. Implementation Notes

- All feature engineering for historical data: `notebooks/04_feature_engineering.ipynb`
- Runtime features for user inputs: `backend/app/engines/wealth_engine.py`
- Stress score engine: `backend/app/engines/stress_engine.py`
- Scenario engine: `backend/app/engines/scenario_engine.py`
- Property features: `backend/app/engines/property_engine.py`

---

*End of Feature Engineering Plan*
