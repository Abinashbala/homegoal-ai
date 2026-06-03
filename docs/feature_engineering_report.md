# HomeGoal AI — Feature Engineering Report

**Version:** 1.0  
**Date:** 2026-06-03  
**Status:** ✅ Complete — 14/14 Validation Checks Passed  
**Outputs:** `features_annual.csv`, `hpi_model_input.csv`, `fx_model_input.csv`

---

## Architecture Principle

Features are split into two types:

| Type | Groups | Where Computed | When Computed |
|---|---|---|---|
| **Historical / Pre-computed** | 1, 2, 3 | `feature_engineer.py` → CSV files | At pipeline run time |
| **Runtime / Per-user** | 4, 5, 6 | `affordability_engine.py` (Phase 6) | On each API call |

Only historical features are stored in datasets. Runtime features are computed from user inputs + forecast outputs on every request.

---

## Group 1 — Housing Features

**Purpose:** Power the HPI forecasting model and the scenario parameter anchors.  
**Source:** `processed/nhb_hpi/nhb_hpi_annual.csv`  
**Saved to:** `processed/features_annual.csv`

| Feature | Formula | Values | Nulls | Use |
|---|---|---|---|---|
| `hpi_growth_pct` | `pct_change(hpi_primary_avg)` | 0.48% – 11.20% | 1 (2013) | Target variable in HPI model |
| `rolling_hpi_growth_3y` | `rolling(3).mean()` of growth | 1.17% – 8.72% | 2 (early years) | Moderate-term growth signal |
| `rolling_hpi_growth_5y` | `rolling(5).mean()` of growth | 2.35% – 6.84% | 3 (early years) | Long-term growth signal |
| `hpi_cagr_from_2013` | `(HPI_t / HPI_2013)^(1/n) − 1` | Varies 2.5%–5.5% | 1 (2013) | Scenario anchor |
| `post_covid_hpi_growth` | rolling(3).mean() where year ≥ 2021 | 5.24%–8.88% | 8 (pre-2021) | Post-COVID regime anchor |

### Scenario Parameter Anchors (embedded as constants in features_annual)

| Scenario | `scenario_*_hpi` | Basis |
|---|---|---|
| `scenario_conservative_hpi` | **3.19%** | Pre-COVID avg (2014–2019) |
| `scenario_expected_hpi` | **4.45%** | Full-period CAGR (2013–2025) |
| `scenario_optimistic_hpi` | **6.87%** | Post-COVID avg (2021–2025) |

---

## Group 2 — Currency Features

**Purpose:** Power the AED-INR forecasting model and FX scenario parameters.  
**Source:** `processed/exchange_rate/aed_inr_annual.csv`  
**Saved to:** `processed/features_annual.csv`

| Feature | Formula | Values | Nulls | Use |
|---|---|---|---|---|
| `fx_growth_pct` | YoY % change in annual avg rate | -3.45% – 6.70% | 1 (2013) | Target variable in FX model |
| `rolling_fx_growth_3y` | `rolling(3).mean()` of fx_growth | 0.83% – 5.26% | 2 (early) | Medium-term FX signal |
| `rolling_fx_growth_5y` | `rolling(5).mean()` of fx_growth | 2.02% – 4.23% | 3 (early) | Long-term FX signal |
| `fx_cagr_from_2013` | `(rate_t / rate_2013)^(1/n) − 1` | Varies 2.8%–3.5% | 1 (2013) | Scenario anchor |
| `currency_volatility_index` | `rolling(3).std()` of fx_growth | 0.85% – 4.23% | 2 (early) | FX risk in stress score |

### Scenario Parameter Anchors

| Scenario | `scenario_*_fx` | Basis |
|---|---|---|
| `scenario_conservative_fx` | **2.00%** | Below historical avg (adverse FX) |
| `scenario_expected_fx` | **3.34%** | Full-period CAGR (2013–2025) |
| `scenario_optimistic_fx` | **4.54%** | Recent 3-year avg (2022–2025) |

---

## Group 3 — Inflation Features

**Purpose:** Scenario-based inflation parameters and cumulative purchasing power deflation.  
**Source:** `processed/inflation/india_cpi_clean.csv`  
**Saved to:** `processed/features_annual.csv`

| Feature | Formula | Values | Nulls | Use |
|---|---|---|---|---|
| `cumulative_inflation_index` | `∏(1 + cpi_t/100)` from 2013 | 1.10 – 1.91 | 1 (2025) | Deflate future wealth to real terms |
| `rolling_inflation_3y` | `rolling(3).mean()` of cpi_pct | 4.39% – 7.20% | 2 (early) | Near-term inflation signal |
| `rolling_inflation_5y` | `rolling(5).mean()` of cpi_pct | 4.17% – 5.97% | 3 (early) | Medium-term inflation signal |
| `inflation_regime` | CPI < 4%→Low, 4-6%→Moderate, >6%→High | Low/Moderate/High | 1 (2025) | Scenario labeling in UI |

### Inflation Regime Distribution (2013–2024)

| Regime | Count | Years |
|---|---|---|
| Low (<4%) | 3 | 2017, 2018, 2019 |
| Moderate (4–6%) | 7 | 2015, 2016, 2021, 2023, 2024, 2015, 2016 |
| High (>6%) | 2 | 2013, 2020, 2022 |

### Scenario Parameter Anchors

| Scenario | Rate | Basis |
|---|---|---|
| `scenario_conservative_cpi` | **7.5%** | Above historical avg — adverse case |
| `scenario_expected_cpi` | **6.0%** | Close to historical mean (5.55%) |
| `scenario_optimistic_cpi` | **4.0%** | Achieved in 3 of 12 years |

---

## Group 4 — Affordability Engine Formulas

These are **runtime features** computed on each user request. No dataset storage.

### Core Formulas

**`property_value` (current)**
```
property_value_inr = property_size_sqft × current_price_per_sqft_inr
```

**`future_property_value`**
```
future_property_value = property_value × (1 + hpi_scenario_rate)^years_remaining
```

**`future_wealth` (AED, nominal)**
```
monthly_savings = monthly_salary_aed - monthly_expenses_aed

FV_savings = current_savings_aed × (1 + r_s)^n_m
           + monthly_savings × [((1 + r_s)^n_m - 1) / r_s]

FV_invest  = current_investment_aed × (1 + r_i)^n_m
           + monthly_invest_contrib × [((1 + r_i)^n_m - 1) / r_i]

future_wealth_aed = FV_savings + FV_invest

where:
  r_s = savings_return / 12   (monthly rate)
  r_i = investment_return / 12
  n_m = years_remaining × 12
```

**`future_wealth_inr` (nominal)**
```
fx_forecast = current_aed_inr_rate × (1 + fx_scenario_rate)^years_remaining
future_wealth_inr = future_wealth_aed × fx_forecast
```

**`real_wealth_inr` (inflation-adjusted)**
```
cumulative_inflation = (1 + cpi_scenario_rate)^years_remaining
real_wealth_inr = future_wealth_inr / cumulative_inflation
```

**`affordability_ratio`**
```
affordability_ratio = real_wealth_inr / future_property_value

Interpretation:
  < 0.5   → Difficult
  0.5–0.99 → Partially Affordable
  1.0     → At Goal
  > 1.0   → Comfortable
```

**`goal_gap`**
```
goal_gap_inr = future_property_value - real_wealth_inr
(positive = shortfall; negative = surplus)
```

**`years_remaining`**
```
years_remaining = target_year - current_year
```

**`monthly_savings_rate`**
```
monthly_savings_rate = (monthly_salary - monthly_expenses) / monthly_salary × 100
```

**`required_monthly_savings`**
```
If goal_gap > 0:
  required_extra_savings_inr = goal_gap × r / ((1 + r)^n_m - 1)
  required_extra_savings_aed = required_extra_savings_inr / fx_forecast

where r = savings_rate / 12,  n_m = years × 12
```

---

## Group 5 — Stress Score

Full specification in [stress_score_specification.md](stress_score_specification.md).

**Formula Summary:**
```
raw = (0.40 × goal_gap_ratio) + (0.30 × expense_ratio) + (0.30 × coverage_shortfall)
stress_score = min(100, max(0, raw × 100 × multiplier))
```

**Verification results (example profile):**
- Conservative: **16.0** → Safe
- Expected: **16.0** → Safe  
- Optimistic: **16.0** → Safe  
*(This profile had surplus in all scenarios — primary stress driver was expense burden at 53%)*

---

## Group 6 — Dashboard KPIs

Full specification in [kpi_catalog.md](kpi_catalog.md).

**Sample output (Expected scenario, example user):**

| KPI | Value |
|---|---|
| Current Property Value | Rs 102.00 Lakh |
| Future Property Value | Rs 132.44 Lakh |
| Future Real Wealth | Rs 174.83 Lakh |
| Goal Gap | Rs -42.39 Lakh (surplus) |
| Affordability Ratio | 1.320 — Comfortable |
| Required Extra Savings | Rs 0/month |
| Stress Score | 16.0 — Safe |
| Monthly Savings Rate | 46.67% |
| Years Remaining | 6 |

---

## Engineered Dataset Summary

### `processed/features_annual.csv`

| Property | Value |
|---|---|
| Rows | 13 (2013–2025) |
| Columns | 29 |
| Historical features | 18 |
| Scenario constants | 9 |
| Validation | All 14 checks passed |

### `processed/modeling/hpi_model_input.csv`

| Property | Value |
|---|---|
| Rows | 51 (quarterly, Q2 2013 – Q4 2025) |
| Columns | 17 |
| Train rows | 35 (Q2 2013 – Q4 2021) |
| Test rows | 16 (Q1 2022 – Q4 2025) |
| Target variable | `hpi_primary` (and `log_hpi` for exponential) |

### `processed/modeling/fx_model_input.csv`

| Property | Value |
|---|---|
| Rows | 156 (monthly, Jan 2013 – Dec 2025) |
| Columns | 18 |
| Train rows | 120 (Jan 2013 – Dec 2022) |
| Test rows | 36 (Jan 2023 – Dec 2025) |
| Target variable | `rate_close` (and `log_rate` for exponential) |

---

*End of Feature Engineering Report*
