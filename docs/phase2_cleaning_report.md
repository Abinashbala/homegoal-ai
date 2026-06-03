# HomeGoal AI — Phase 2: Cleaning Summary & Validation Report

**Version:** 1.0  
**Date:** 2026-06-02  
**Status:** ✅ Complete — 29/29 Validation Checks Passed  

---

## Architecture Updates Applied

Before cleaning, the following architecture changes were applied:

| # | Change | Impact |
|---|---|---|
| 1 | Forecast model strategy: compare Linear, Exponential, Prophet, XGBoost — select best | Applies to Phase 5 modeling |
| 2 | Inflation: removed ML model. Use scenario-based assumptions (7.5% / 6.0% / 4.0%) | CPI data still cleaned and retained for real-wealth calculations |
| 3 | Added Affordability Ratio KPI: `real_wealth / future_property_cost` | Applies to Phase 6 backend engines |
| 4 | Added Required Monthly Savings KPI | Applies to Phase 6 backend engines |

---

## Cleaning Summary

### Dataset 1 — NHB Housing Price Index

| Property | Before | After |
|---|---|---|
| Rows | 51 | 51 |
| Columns | 3 | 10 |
| Nulls | 5 (`hpi_market` N/A strings) | 0 |
| Duplicates | 0 | 0 |
| File | `.xls.xlsx` | `nhb_hpi_clean.csv` |

**Transformations Applied:**
1. Renamed columns: `Quarter` → `quarter`, `HPI@Assessment Prices` → `hpi_assessment`, `HPI@Market Prices` → `hpi_market`
2. Converted 5 `'N/A'` string values in `hpi_market` → `NaN` using `pd.to_numeric(errors='coerce')`
3. Parsed `quarter` from `datetime.datetime` object to standardized `pd.Timestamp`
4. Derived `year`, `month`, `quarter_label` columns (e.g., `2013-Q2`)
5. Created `hpi_primary` = Market HPI where available, Assessment HPI for the 5 missing 2025 quarters
6. Tagged each row with `hpi_source`: `market` (46 rows) or `assessment_imputed` (5 rows)
7. Computed `hpi_qoq_pct` (quarter-over-quarter %) and `hpi_yoy_pct` (year-over-year %)
8. Created `nhb_hpi_annual.csv` with annual averages, YoY growth, and CAGR from 2013

**Key Statistics:**
- Quarter range: **2013-Q2 → 2025-Q4** (51 quarters)
- HPI start (2013 avg): **86.00**
- HPI end (2025 avg): **144.99**
- Full-period CAGR: **4.45% per year**

---

### Dataset 2 — World Bank Inflation (India CPI)

| Property | Before | After |
|---|---|---|
| Rows | 266 (all countries) | 12 (India only, 2013–2024) |
| Columns | 71 | 5 |
| Nulls | 0 (for India) | 0 |
| Duplicates | 0 | 0 |
| File | Wide-format CSV | `india_cpi_clean.csv` |

**Transformations Applied:**
1. Loaded with `skiprows=4` to skip World Bank metadata header
2. Filtered to India only (`Country Code == 'IND'`): 265 other country rows removed
3. Reshaped from wide format (1 row × 67 year-columns) to long format (12 rows × year, cpi_pct)
4. Filtered to relevant years: 2013–2024
5. Cast year to `int`, CPI to `float`
6. Computed `inflation_multiplier` = `1 + cpi_pct/100`
7. Computed `cumulative_inflation_index` = running product of multipliers (base 2013 = 1.0)

**Key Statistics:**
- Coverage: **2013–2024** (12 annual observations)
- CPI range: **3.33%** (2017) → **10.02%** (2013)
- Average CPI (2013–2024): **5.55%**
- Cumulative inflation (2013–2024): **1.91×** (₹1 in 2013 = ₹1.91 in 2024)
- 2025 not added — no ML model for CPI; scenario values used instead

**Scenario Inflation Parameters (confirmed from historical data):**
| Scenario | Rate | Rationale |
|---|---|---|
| Conservative | 7.5% | Above historical avg (worst case) |
| Expected | 6.0% | Close to historical average (5.55%) |
| Optimistic | 4.0% | Below historical average (best case) |

---

### Dataset 3 — AED-INR Exchange Rate

| Property | Before | After |
|---|---|---|
| Rows | 156 | 156 |
| Columns | 7 | 9 |
| Nulls | 156 (`Vol.` — 100% empty) | 0 |
| Duplicates | 0 | 0 |
| File | CSV (string dates) | `aed_inr_clean.csv` |

**Transformations Applied:**
1. Loaded with `encoding='utf-8-sig'` to handle BOM character in file header
2. Renamed all columns to snake_case
3. Dropped `vol` column (100% empty — no value)
4. Parsed `date` from string `MM/DD/YYYY` → `pd.Timestamp` using `format='%m/%d/%Y'`
5. Sorted by date ascending (original file was newest-first)
6. Cast `rate_close`, `rate_open`, `rate_high`, `rate_low` to `float`
7. Parsed `change_pct` from string `"0.58%"` → `float` `0.58`
8. Derived `year` and `month` columns
9. Computed `mom_change_pct` (month-over-month %) and `yoy_change_pct` (year-over-year %)
10. Created `aed_inr_annual.csv` with annual averages, min, max, and YoY growth

**Key Statistics:**
- Coverage: **Jan 2013 → Dec 2025** (156 monthly observations — no gaps)
- AED/INR 2013 avg: **16.03 INR/AED**
- AED/INR 2025 avg: **23.78 INR/AED**
- Full-period CAGR: **+3.34% per year** (INR weakening vs AED)
- No outliers detected

---

## Master Annual Dataset

**File:** `processed/master_annual.csv`

| Column | Description | Coverage |
|---|---|---|
| `year` | Calendar year | 2013–2025 (13/13) |
| `hpi_index` | Annual average HPI (primary) | 2013–2025 (13/13) |
| `hpi_growth_pct` | Annual HPI growth % | 2014–2025 (12/13, first year NaN as expected) |
| `hpi_assessment` | Annual average Assessment HPI | 2013–2025 (13/13) |
| `cpi_pct` | India annual inflation % | 2013–2024 (12/13, 2025 not yet published) |
| `cumulative_inflation_index` | Cumulative CPI multiplier from 2013 | 2013–2024 (12/13) |
| `aed_inr_rate` | Annual average AED/INR rate | 2013–2025 (13/13) |
| `fx_growth_pct` | Annual FX growth % | 2014–2025 (12/13, first year NaN as expected) |

> **Note:** 2025 CPI is legitimately missing (not yet published). This is expected and is handled by scenario-based inflation assumptions.

---

## Validation Report

### Validation Scorecard

| Dataset | Checks Passed | Total Checks | Score | Status |
|---|---|---|---|---|
| NHB HPI (`nhb_hpi_clean.csv`) | 8 | 8 | 100% | ✅ Pass |
| India CPI (`india_cpi_clean.csv`) | 6 | 6 | 100% | ✅ Pass |
| AED-INR (`aed_inr_clean.csv`) | 7 | 7 | 100% | ✅ Pass |
| Master Annual (`master_annual.csv`) | 8 | 8 | 100% | ✅ Pass |
| **OVERALL** | **29** | **29** | **100%** | ✅ **All Pass** |

---

### Remaining Data Risks

| Risk | Dataset | Severity | Mitigation |
|---|---|---|---|
| NHB HPI is national-level only (not city-specific) | HPI | Low | Documented in architecture. User provides own price-per-sqft as anchor. |
| 5 quarters of Market HPI imputed from Assessment HPI (2025) | HPI | Low | Flagged via `hpi_source = assessment_imputed`. UI will show "estimated" label. |
| India CPI 2025 missing | CPI | Low | Scenario-based inflation used. No impact on MVP. |
| Small dataset size (13 annual HPI rows, 12 CPI rows) | All | Medium | Use simpler models (linear/exponential trend). Cross-validate carefully. |
| AED pegged to USD — FX movement = USD/INR movement | FX | Low | Documented in architecture. Acceptable for MVP forecasting purposes. |

---

## Output Files — Final Confirmation

| File | Path | Size | Status |
|---|---|---|---|
| `nhb_hpi_clean.csv` | `processed/nhb_hpi/` | 4,361 bytes | ✅ |
| `nhb_hpi_annual.csv` | `processed/nhb_hpi/` | 976 bytes | ✅ |
| `india_cpi_clean.csv` | `processed/inflation/` | 872 bytes | ✅ |
| `aed_inr_clean.csv` | `processed/exchange_rate/` | 10,287 bytes | ✅ |
| `aed_inr_annual.csv` | `processed/exchange_rate/` | 977 bytes | ✅ |
| `master_annual.csv` | `processed/` | 1,466 bytes | ✅ |

---

## Recommended Next Actions (Phase 3)

Once approved, proceed to **Phase 3 — Exploratory Data Analysis (EDA)**:

1. **HPI trend analysis** — Plot quarterly and annual HPI, growth rates, pre/post-COVID comparison
2. **CPI distribution analysis** — Bar chart of annual India CPI, rolling averages
3. **FX trend analysis** — Monthly AED/INR chart, rolling average, volatility bands
4. **Cross-dataset correlation** — Heatmap of HPI growth vs CPI vs FX change
5. **Historical CAGR derivation** — Compute scenario parameter anchors from data
6. **Plotly interactive dashboard** — Combined multi-axis time series
7. **Seaborn distribution plots** — Distribution of growth rates for each series

---

## ⏸️ STOP — Awaiting Approval

Phase 2 is complete. All 6 processed files are generated, all 29 validation checks pass.

**Do NOT proceed to EDA, Feature Engineering, Modeling, Backend, or Frontend without explicit approval.**

---

*End of Phase 2 Report*
