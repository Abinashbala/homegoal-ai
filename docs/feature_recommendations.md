# HomeGoal AI — Feature Recommendations for Modeling

**Version:** 1.0  
**Date:** 2026-06-03  
**Based on:** Phase 3 EDA findings  
**Purpose:** Define what enters forecasting models, stress engine, and dashboard KPIs

---

## 1. Features for Forecasting Models

Two forecasting models are required: Housing (HPI) and Currency (AED-INR).
Inflation is handled by scenario assumptions only (no ML model).

---

### 1.1 Housing Forecast Model (Target: `hpi_index`)

**Training data:** `nhb_hpi_clean.csv` + `nhb_hpi_annual.csv`  
**Recommended granularity:** Quarterly (51 observations) — use annual only as fallback  
**Training window:** Q2 2013 – Q4 2024 (exclude 2025 — assess-imputed)

#### Candidate Features (Inputs)

| Feature | Source | Rationale |
|---|---|---|
| `hpi_primary` (lagged t-1) | NHB HPI quarterly | Strong autocorrelation — past HPI predicts future HPI |
| `hpi_primary` (lagged t-4) | NHB HPI quarterly | Year-ago value captures seasonality |
| `year` (numeric) | Derived | Captures long-run time trend |
| `quarter_num` (1–4) | Derived from quarter | Seasonal component |
| `hpi_qoq_pct` (lagged) | NHB HPI | Momentum signal |
| `post_covid_flag` (0/1) | Derived: year >= 2022 | Regime change variable — post-2022 acceleration |

#### Candidate Models (Compare all, select by MAPE)

| Model | Notes | Expected Performance |
|---|---|---|
| Linear Trend | Baseline. Simple, interpretable. | MAPE ~4-6% |
| Exponential Growth | Better for compound growth. | MAPE ~3-5% |
| Prophet | Handles trend + seasonality + breaks. | MAPE ~2-4% |
| XGBoost (time-series) | Lag features, requires careful CV. | MAPE ~2-5% |

**Recommendation:** Start with Exponential Trend as baseline. Prophet likely wins due to COVID break detection.

#### Evaluation Protocol
- Train: Q2 2013 – Q4 2021
- Test: Q1 2022 – Q4 2024
- Metric: MAE, RMSE, MAPE
- Minimum baseline to beat: Naïve last-value model

---

### 1.2 Currency Forecast Model (Target: `aed_inr_rate`)

**Training data:** `aed_inr_clean.csv` + `aed_inr_annual.csv`  
**Recommended granularity:** Monthly (156 observations) — strong dataset  
**Training window:** Jan 2013 – Dec 2023 (test on 2024)

#### Candidate Features (Inputs)

| Feature | Source | Rationale |
|---|---|---|
| `rate_close` (lagged t-1) | AED-INR monthly | Strong autocorrelation (AED peg = low noise) |
| `rate_close` (lagged t-12) | AED-INR monthly | Year-ago anchor |
| `mom_change_pct` (lagged) | AED-INR monthly | Momentum signal |
| `year`, `month` (numeric) | Derived | Long-run trend + seasonal |
| `rolling_12m_avg` | AED-INR monthly | Smoothed trend feature |

#### Candidate Models (Compare all, select by MAPE)

| Model | Notes | Expected Performance |
|---|---|---|
| Linear Trend | Baseline. AED trend is nearly linear. | MAPE ~1-3% |
| Exponential Growth | Compound depreciation model. | MAPE ~1-2% |
| Prophet | Monthly seasonality + trend. | MAPE ~1-2% |
| XGBoost | With lag features. | MAPE ~1-3% |
| ARIMA(1,1,0) | Classic time-series model. | MAPE ~2-3% |

**Recommendation:** Linear or Exponential Trend may actually beat Prophet here given the strong linear trend. Run all; document winner.

#### Evaluation Protocol
- Train: Jan 2013 – Dec 2022
- Test: Jan 2023 – Dec 2024
- Metric: MAE, RMSE, MAPE
- Minimum baseline: Naïve last-month model

---

### 1.3 Inflation — No Forecasting Model Required

Per architecture update (Phase 2): CPI is handled by **scenario-based fixed assumptions** only.

| Scenario | Inflation Rate | Basis |
|---|---|---|
| Conservative | 7.5% | Above historical avg (5.55%) — plausible shock |
| Expected | 6.0% | Close to historical avg |
| Optimistic | 4.0% | Achieved in 6 of 12 years |

Historical CPI data (`india_cpi_clean.csv`) is used **only** to:
1. Compute cumulative inflation deflator (2013–2024)
2. Validate scenario assumptions against historical range
3. Provide context in UI explainer cards

---

## 2. Features for Stress Score Engine

The stress score is a rule-based composite index (0–100). No ML. These features feed directly into the formula.

### Primary Signals

| Feature | Derived From | Formula Component | Weight |
|---|---|---|---|
| `goal_gap_ratio` | `(property_cost - real_wealth) / property_cost` | Shortfall as % of goal | 40% |
| `expense_ratio` | `monthly_expenses / monthly_salary` | Budget burn rate | 30% |
| `coverage_shortfall` | `1 - min(1, real_wealth / property_cost)` | Inverted wealth coverage | 30% |

### Input Features (From User)

| Feature | Type | Used In |
|---|---|---|
| `monthly_salary_aed` | User input | Both components |
| `monthly_expenses_aed` | User input | `expense_ratio` |
| `future_wealth_real_inr` | Computed | `coverage_shortfall`, `goal_gap_ratio` |
| `future_property_cost_inr` | Computed (HPI model) | `goal_gap_ratio`, `coverage_shortfall` |
| `risk_tolerance` | User input | Multiplier (0.85 / 1.00 / 1.20) |

### Secondary Signals (Explainability)

| Feature | Used For |
|---|---|
| `savings_rate_pct` | Explain "burn rate driver" in stress breakdown |
| `years_to_goal` | Modulate urgency (less time = more stress) |
| `affordability_ratio` | Primary KPI output |
| `monthly_savings_needed` | Actionable KPI output |

---

## 3. Features for Dashboard KPIs

These are the primary user-facing metrics produced by the platform. They are **computed output features** rather than inputs.

### Primary KPIs (Show on Main Dashboard)

| KPI | Formula | Display Format | Priority |
|---|---|---|---|
| **Affordability Ratio** | `real_wealth_inr / future_property_cost_inr` | `0.72 — Partially Affordable` | P0 |
| **Goal Gap** | `future_property_cost - real_wealth_real` | `Rs 25,00,000 shortfall` | P0 |
| **Stress Score** | Rule-based 0–100 | `Score: 64 — Stretch` | P0 |
| **Required Monthly Savings** | `goal_gap / (years × 12)` | `+Rs 18,400/month needed` | P0 |
| **Future Property Cost** | `current_value × (1 + hpi_cagr)^n` | `Rs 1.42 Crore in 2031` | P0 |
| **Future Wealth (Real)** | Wealth projection deflated by CPI | `Rs 1.05 Crore (real terms)` | P0 |

### Secondary KPIs (Show on Scenario Cards)

| KPI | Formula | Display Format | Priority |
|---|---|---|---|
| **Wealth Coverage %** | `real_wealth / property_cost × 100` | `72% of goal funded` | P1 |
| **FX Tailwind** | `fx_cagr × years_to_goal` | `+34% INR from AED by 2031` | P1 |
| **Savings Rate** | `(salary - expenses) / salary` | `Saving 35% of income` | P1 |
| **Current Property Value** | `size × price_per_sqft` | `Rs 85 lakh today` | P1 |
| **Inflation Cost** | `cumulative_inflation × wealth - wealth` | `Rs 18L lost to inflation` | P2 |
| **Years to Affordability** | Solve for n where ratio = 1.0 | `Fully affordable in 2034` | P2 |

### Scenario Comparison KPIs (Show on Scenario Table)

| KPI | Conservative | Expected | Optimistic |
|---|---|---|---|
| Future Property Cost | Highest | Mid | Lowest |
| Future Real Wealth | Lowest | Mid | Highest |
| Affordability Ratio | Lowest | Mid | Highest |
| Stress Score | Highest | Mid | Lowest |
| Monthly Savings Needed | Highest | Mid | Lowest |

---

## 4. Feature Engineering Priorities for Phase 4

Based on EDA, the following features should be engineered in Phase 4:

### Tier 1 — Must Build

| Feature | Notebook Section | Notes |
|---|---|---|
| `hpi_cagr_full` | Section A1 | Already computed in EDA (4.45%) |
| `hpi_cagr_3yr` | Section A1 | Recent 3-year: ~8.6% — useful for optimistic |
| `hpi_cagr_5yr` | Section A1 | 5-year: ~6.5% — good for expected/optimistic |
| `hpi_pre_covid_cagr` | Section A1 | 3.19% — Conservative anchor |
| `hpi_post_covid_cagr` | Section A1 | 6.87% — Optimistic anchor |
| `fx_cagr_full` | Section A3 | Already computed (3.34%) |
| `fx_cagr_3yr` | Section A3 | Recent 3-year |
| `cpi_rolling_3yr_avg` | Section A2 | 5.77% — Near-term expected |
| `cpi_rolling_5yr_avg` | Section A2 | ~5.5% — Medium-term expected |
| `cumulative_inflation_index` | Section A2 | Already computed |

### Tier 2 — Build for Models

| Feature | Used In | Notes |
|---|---|---|
| `hpi_qoq_pct_lag1` | HPI model | Momentum feature |
| `hpi_qoq_pct_lag4` | HPI model | Year-ago quarter |
| `post_covid_flag` | HPI model | Regime variable |
| `fx_mom_lag1` | FX model | Momentum |
| `fx_rolling_12m_avg` | FX model | Smoothed level |
| `fx_volatility_band` | FX model | Confidence bounds |

### Tier 3 — Build for Scenario Validation

| Feature | Used In | Notes |
|---|---|---|
| `real_hpi_growth_annual` | Scenario context | Average: -0.59% |
| `net_aed_cost_pressure` | Scenario context | Average: +1.12% |
| `inflation_quintile` | Scenario calibration | High / Medium / Low classification |

---

## 5. Summary Recommendations Table

| Destination | Features Entering | Source |
|---|---|---|
| **HPI Forecast Model** | hpi_primary lags, year, quarter, post_covid_flag | nhb_hpi_clean.csv |
| **FX Forecast Model** | rate_close lags, year, month, rolling_12m_avg | aed_inr_clean.csv |
| **Inflation (Scenario)** | Fixed values: 7.5% / 6.0% / 4.0% | Hard-coded |
| **Stress Score Engine** | goal_gap_ratio, expense_ratio, coverage_shortfall, risk_tolerance | User input + forecast output |
| **Dashboard KPIs** | affordability_ratio, goal_gap, stress_score, monthly_savings_needed | Computed from all engines |
| **Scenario Engine** | hpi_cagr variants, fx_cagr variants, cpi scenario | Derived from EDA CAGR analysis |

---

## ⏸️ STOP — Awaiting Approval for Phase 4

Phase 3 EDA is complete. All features are identified and prioritized.

**Do NOT proceed to Feature Engineering or Model Training without explicit approval.**

---

*End of Feature Recommendations*
