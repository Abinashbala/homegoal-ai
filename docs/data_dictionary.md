# HomeGoal AI — Data Dictionary

**Version:** 1.0  
**Date:** 2026-06-02  
**Status:** Complete  

---

## Overview

This document defines every field across all raw datasets, processed datasets, and engineered features used in the HomeGoal AI platform. It serves as the single source of truth for all data definitions.

---

## Section 1 — Raw Datasets

### 1.1 NHB Housing Price Index (`india_housing_price_index_nhb_2013_2025.xls.xlsx`)

| Field Name | Data Type | Unit | Range | Description | Null Handling |
|---|---|---|---|---|---|
| `Quarter` | datetime | — | Q2 2013 – Q4 2025 | Start date of the quarter. NHB uses the first day of the quarter's last month (e.g., June 2013 = Q2 FY2013-14) | Not null |
| `HPI@Assessment Prices` | float | Index (base ≈ 2017-18 = 100) | 83.0 – 147.65 | NHB Housing Price Index computed from government/official assessment/registration valuations. More stable but lags market | Not null |
| `HPI@Market Prices` | float / string | Index (base ≈ 2017-18 = 100) | 85.0 – 142.95 | NHB HPI based on actual market transaction prices collected from banks and NBFCs. More volatile but more reflective of real demand | N/A string for Q4 2024 – Q4 2025 |

**Notes:**
- Base year for NHB HPI is approximately FY 2017-18 (index ≈ 100)
- HPI represents **national aggregate** — not city-specific
- A value of 147.65 means housing prices are 47.65% higher than the base year

---

### 1.2 World Bank CPI — India (`API_FP.CPI.TOTL.ZG_DS2_en_csv_v2_278989.csv`)

**Raw file structure (wide format — one row per country):**

| Field Name | Data Type | Unit | Description |
|---|---|---|---|
| `Country Name` | string | — | Full country name (e.g., "India") |
| `Country Code` | string | ISO Alpha-3 | 3-letter country code (e.g., "IND") |
| `Indicator Name` | string | — | Always: "Inflation, consumer prices (annual %)" |
| `Indicator Code` | string | — | Always: "FP.CPI.TOTL.ZG" |
| `1960` – `2024` | float | Percent (%) | Annual consumer price inflation rate for that year |
| `2025` | empty | — | Not yet published as of audit date |

**After filtering for India and reshaping to long format:**

| Field Name | Data Type | Unit | Range | Description |
|---|---|---|---|---|
| `year` | int | — | 1960 – 2024 | Calendar year |
| `cpi_pct` | float | Annual % | 3.33 – 11.99 (2013–2024) | India annual inflation rate. Positive = price increase; higher = faster erosion of purchasing power |

**India CPI Reference Values:**

| Year | CPI (%) | Economic Context |
|---|---|---|
| 2013 | 10.02 | Elevated food + fuel inflation |
| 2014 | 6.67 | RBI tightening, food price easing |
| 2015 | 4.91 | Oil price crash, demand slowdown |
| 2016 | 4.95 | Demonetization demand shock |
| 2017 | 3.33 | GST transition, base effects |
| 2018 | 3.94 | Moderate recovery |
| 2019 | 3.73 | Subdued demand |
| 2020 | 6.62 | COVID supply disruption |
| 2021 | 5.13 | Partial recovery |
| 2022 | 6.70 | Russia-Ukraine commodity spike |
| 2023 | 5.65 | Gradual moderation |
| 2024 | 4.95 | Continuing moderation |

---

### 1.3 AED-INR Exchange Rate (`AED_INR Historical Data.csv`)

| Field Name | Data Type | Unit | Range | Description | Action |
|---|---|---|---|---|---|
| `Date` | string → datetime | MM/DD/YYYY | Jan 2013 – Dec 2025 | Reference month date. Records the first day of each month in the dataset | Parse to datetime |
| `Price` | string → float | INR per 1 AED | 14.50 – 24.47 | Monthly closing exchange rate — how many Indian Rupees one UAE Dirham buys | Cast to float |
| `Open` | string → float | INR per 1 AED | 14.50 – 24.47 | Opening rate for the month | Cast to float |
| `High` | string → float | INR per 1 AED | 14.45 – 24.80 | Highest rate recorded during the month | Cast to float |
| `Low` | string → float | INR per 1 AED | 14.40 – 24.30 | Lowest rate recorded during the month | Cast to float |
| `Vol.` | string | — | Always empty | Trading volume — not published by source | **DROP** |
| `Change %` | string | Percent (%) | -5.83% – +7.99% | Month-over-month percentage change in the AED/INR rate | Parse as float after stripping `%` |

**Key Rate Reference Points:**

| Date | Rate (INR/AED) | Event |
|---|---|---|
| Jan 2013 | 14.50 | Dataset start |
| Sep 2013 | 17.89 | INR crisis (US Fed taper tantrum) |
| Mar 2020 | 20.51 | COVID currency volatility |
| Dec 2025 | 24.47 | Dataset end |

---

## Section 2 — Processed Datasets

### 2.1 Processed NHB HPI (`processed/nhb_hpi/nhb_hpi_clean.csv`)

| Field Name | Data Type | Unit | Description |
|---|---|---|---|
| `quarter` | datetime | — | Quarter start date, standardized |
| `year` | int | — | Calendar year extracted from quarter |
| `quarter_label` | string | — | Human-readable label (e.g., "2013-Q2") |
| `hpi_assessment` | float | Index | Cleaned Assessment HPI |
| `hpi_market` | float / NaN | Index | Cleaned Market HPI (NaN for 2025 quarters) |
| `hpi_primary` | float | Index | Primary HPI used for modeling: Assessment where Market is null, else Market |
| `hpi_yoy_pct` | float | % | Year-over-year growth rate of `hpi_primary` |
| `hpi_qoq_pct` | float | % | Quarter-over-quarter growth rate of `hpi_primary` |

### 2.2 Processed NHB HPI — Annual (`processed/nhb_hpi/nhb_hpi_annual.csv`)

| Field Name | Data Type | Unit | Description |
|---|---|---|---|
| `year` | int | — | Calendar year |
| `hpi_annual_avg` | float | Index | Average of quarterly HPI values within the year |
| `hpi_annual_growth_pct` | float | % | Annual growth rate vs prior year |

### 2.3 Processed Inflation (`processed/inflation/india_cpi_clean.csv`)

| Field Name | Data Type | Unit | Description |
|---|---|---|---|
| `year` | int | — | Calendar year |
| `cpi_pct` | float | % | India annual consumer price inflation |
| `cumulative_inflation_index` | float | Index (2013=1.0) | Cumulative product of (1 + cpi/100) from 2013 |
| `is_estimated` | bool | — | True if value is extrapolated (2025) |

### 2.4 Processed Exchange Rate (`processed/exchange_rate/aed_inr_clean.csv`)

| Field Name | Data Type | Unit | Description |
|---|---|---|---|
| `date` | datetime | — | First day of the month |
| `year` | int | — | Year extracted |
| `month` | int | — | Month extracted |
| `rate_close` | float | INR/AED | Monthly closing rate |
| `rate_open` | float | INR/AED | Monthly opening rate |
| `rate_high` | float | INR/AED | Monthly high rate |
| `rate_low` | float | INR/AED | Monthly low rate |
| `mom_change_pct` | float | % | Month-over-month % change |
| `yoy_change_pct` | float | % | Year-over-year % change |

### 2.5 Processed Exchange Rate — Annual (`processed/exchange_rate/aed_inr_annual.csv`)

| Field Name | Data Type | Unit | Description |
|---|---|---|---|
| `year` | int | — | Calendar year |
| `rate_annual_avg` | float | INR/AED | Average of all monthly rates in the year |
| `rate_annual_yoy_pct` | float | % | Annual % change in average rate |

---

## Section 3 — User Input Fields

These fields are collected from the user through the HomeGoal AI web form. They are not stored in datasets — they are runtime inputs.

### 3.1 Financial Profile

| Field Name | Type | Unit | Validation | Description |
|---|---|---|---|---|
| `monthly_salary_aed` | float | AED | > 0 | User's gross monthly salary in UAE Dirhams |
| `monthly_expenses_aed` | float | AED | ≥ 0, < salary | Total monthly living expenses in AED |
| `current_savings_aed` | float | AED | ≥ 0 | Current total savings in AED (cash + bank deposits) |

### 3.2 Investment Information (Optional)

| Field Name | Type | Unit | Validation | Description |
|---|---|---|---|---|
| `current_investment_value_aed` | float | AED | ≥ 0 | Current market value of all investments in AED |
| `monthly_investment_contribution_aed` | float | AED | ≥ 0 | Monthly amount added to investments |
| `expected_investment_return_pct` | float | % | 0 – 25 | Expected annual return on investments |

### 3.3 Property Information

| Field Name | Type | Unit | Validation | Description |
|---|---|---|---|---|
| `city` | string | — | Non-empty | Target Indian city (e.g., "Chennai") |
| `locality` | string | — | Non-empty | Target locality within the city (e.g., "Mogappair") |
| `property_size_sqft` | float | sqft | > 0 | Desired property area in square feet |
| `current_price_per_sqft_inr` | float | INR | > 0 | Current price per square foot in the target locality (user-researched) |

**Derived field (computed immediately on input):**

| Field Name | Formula | Unit | Description |
|---|---|---|---|
| `current_property_value_inr` | `property_size_sqft × current_price_per_sqft_inr` | INR | Current estimated property value at user's target location |
| `current_property_value_lakhs` | `current_property_value_inr / 100000` | Lakhs | Same value in Indian Lakhs for display |
| `current_property_value_crore` | `current_property_value_inr / 10000000` | Crore | Same value in Indian Crore for display |

### 3.4 Goal Information

| Field Name | Type | Validation | Description |
|---|---|---|---|
| `target_purchase_year` | int | Current year + 1 to current year + 20 | Year in which user aims to purchase property |
| `risk_tolerance` | enum | `conservative`, `moderate`, `aggressive` | User's financial risk appetite — determines scenario parameters |

---

## Section 4 — Engineered Features

Refer to `docs/feature_engineering_plan.md` for full derivation logic.

| Feature Name | Derived From | Description |
|---|---|---|
| `monthly_savings_aed` | `salary - expenses` | Monthly surplus available to save |
| `savings_rate_pct` | `savings / salary × 100` | What % of salary is saved |
| `years_to_goal` | `target_year - current_year` | Total time horizon in years |
| `future_wealth_aed` | Compound formula | Projected total AED wealth at target year |
| `future_wealth_inr` | `wealth_aed × forecast_rate` | AED wealth converted to INR |
| `future_property_cost_inr` | HPI CAGR on base price | Projected property price at target year |
| `real_wealth_inr` | `nominal_wealth / cumulative_inflation` | Inflation-adjusted INR wealth |
| `goal_gap_inr` | `property_cost - real_wealth` | Shortfall (negative = surplus, positive = gap) |
| `wealth_coverage_ratio` | `wealth / property_cost` | % of property cost covered by wealth |
| `stress_score` | Rule-based formula | 0–100 financial stress score |
| `hpi_cagr_pct` | NHB HPI | Compound annual growth rate of Indian housing |
| `cpi_forecast_pct` | World Bank CPI | Projected future inflation rate |
| `fx_rate_forecast` | AED-INR model | Projected future AED/INR rate |

---

## Section 5 — Scenario Parameters

| Scenario | `hpi_cagr` | `cpi_pct` | `fx_annual_growth` | `investment_return` |
|---|---|---|---|---|
| Conservative | 3.0% | 7.5% | 2.0% | 6.0% |
| Expected | 4.8% | 6.0% | 4.3% | 9.0% |
| Optimistic | 7.0% | 4.0% | 6.5% | 12.0% |

---

*End of Data Dictionary*
