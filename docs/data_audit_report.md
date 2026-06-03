# HomeGoal AI — Data Audit Report

**Version:** 1.0  
**Date:** 2026-06-02  
**Author:** HomeGoal AI Analytics Team  
**Status:** Complete  

---

## 1. Executive Summary

This document provides a comprehensive audit of all three source datasets used by HomeGoal AI. The audit covers dataset structure, data quality, coverage, granularity, missing values, outliers, and suitability for modeling.

| Dataset | Source | Rows | Granularity | Coverage | Quality |
|---|---|---|---|---|---|
| NHB Housing Price Index | National Housing Bank | 51 | Quarterly | Q2 2013 – Q4 2025 | ✅ Good (minor fix needed) |
| World Bank CPI – India | World Bank Open Data | 266 countries | Annual | 1960 – 2024 | ✅ Good (2025 missing) |
| AED-INR Exchange Rate | Investing.com | 156 | Monthly | Jan 2013 – Dec 2025 | ✅ Excellent |

All three datasets are suitable for use in the HomeGoal AI MVP. Minor cleaning is required before modeling can begin.

---

## 2. Dataset 1 — NHB Housing Price Index (India)

### 2.1 Source Information

| Property | Value |
|---|---|
| Source | National Housing Bank (NHB), India |
| File | `india_housing_price_index_nhb_2013_2025.xls.xlsx` |
| File Size | 6.1 KB |
| Sheet Name | `india_housing_price_index_nhb_2` |
| Format | Excel (.xlsx) |

### 2.2 Structure

| Property | Value |
|---|---|
| Total Rows | 51 (excluding header) |
| Total Columns | 3 |
| Granularity | Quarterly |
| Date Range | Q2 2013 (June 2013) → Q4 2025 (December 2025) |
| Date Column Format | `datetime` (Python: `datetime.datetime`) |

**Columns:**

| Column Name | Data Type | Description |
|---|---|---|
| `Quarter` | datetime | Quarter start date (first day of each quarter month) |
| `HPI@Assessment Prices` | float | NHB HPI based on government/assessment valuations |
| `HPI@Market Prices` | float | NHB HPI based on actual market transaction prices |

### 2.3 Data Quality Assessment

| Check | Result | Detail |
|---|---|---|
| Null values | ⚠️ Partial | `HPI@Market Prices` has 5 `N/A` string values (Q4 2024 – Q4 2025) |
| Duplicate rows | ✅ None | 0 duplicate quarter entries |
| Outliers | ✅ None detected | HPI trends are smooth and monotonically increasing |
| Data type consistency | ⚠️ Mixed | `HPI@Market Prices` contains both `float` and `'N/A'` string |
| Coverage gap | ⚠️ Minor | Market prices missing for last 5 quarters (2025 data not yet published) |
| Monotonicity | ✅ Expected | Both HPI series show consistent upward trend |
| Quarter coverage | ✅ Complete | No gaps in quarterly sequence from Q2 2013 to Q4 2025 |

**Missing Values Detail:**

| Quarter | `HPI@Assessment` | `HPI@Market` |
|---|---|---|
| Q4 2024 | 140.61 | N/A |
| Q1 2025 | 143.29 | N/A |
| Q2 2025 | 143.98 | N/A |
| Q3 2025 | 145.02 | N/A |
| Q4 2025 | 147.65 | N/A |

**Interpretation:** Market price data for 2025 has not yet been published by NHB. Assessment price data is available through Q4 2025.

### 2.4 Statistical Summary

| Metric | HPI@Assessment | HPI@Market |
|---|---|---|
| Start Value (Q2 2013) | 83.00 | 85.00 |
| End Value (latest) | 147.65 | 142.95 (Q3 2024) |
| Total Appreciation | +77.9% | +68.2% |
| Approximate CAGR | ~4.8%/year | ~4.4%/year |
| Min | 83.00 | 85.00 |
| Max | 147.65 | 142.95 |

### 2.5 Key Observations

1. **Both HPI series track upward** — the Indian housing market has appreciated consistently since 2013.
2. **Assessment prices slightly lead market prices** in growth — this is typical as assessment prices often capture infrastructure value uplift faster.
3. **2020 COVID plateau** — HPI stagnated at 112 for Assessment and 104 for Market during Q2–Q3 2020, reflecting pandemic-induced market slowdown.
4. **Acceleration post-2022** — both series show steeper growth from Q1 2022 onwards, reflecting India's post-pandemic real estate boom.
5. **The HPI is a national aggregate** — it does not break down by city or locality. This is acceptable given that users now provide their own price per sqft as the property anchor.

### 2.6 Usage in HomeGoal AI

| Use Case | Column(s) Used |
|---|---|
| Annual housing appreciation rate | `HPI@Assessment Prices` (primary) |
| Conservative scenario | Lower CAGR derived from HPI |
| Expected scenario | Historical average CAGR from HPI |
| Optimistic scenario | Upper CAGR range from HPI |
| Future property price projection | Apply CAGR to user-supplied base price |

---

## 3. Dataset 2 — World Bank Inflation Data (India CPI)

### 3.1 Source Information

| Property | Value |
|---|---|
| Source | World Bank Open Data |
| Indicator Code | `FP.CPI.TOTL.ZG` |
| Indicator Name | Inflation, consumer prices (annual %) |
| File | `API_FP.CPI.TOTL.ZG_DS2_en_csv_v2_278989.csv` |
| File Size | 215 KB |
| Format | CSV (World Bank standard export) |
| Last Updated | 2026-04-08 |

### 3.2 Structure

| Property | Value |
|---|---|
| Total Rows | 266 (countries + regional aggregates) |
| Total Columns | 71 (4 metadata + 67 year columns: 1960–2025 + trailing blank) |
| Granularity | Annual |
| Year Range | 1960 – 2024 (2025 empty) |
| Format Note | First 4 rows are metadata; actual data starts at row 5 |

**Columns:**

| Column | Description |
|---|---|
| `Country Name` | Full country name |
| `Country Code` | ISO 3-letter country code |
| `Indicator Name` | Always "Inflation, consumer prices (annual %)" |
| `Indicator Code` | Always "FP.CPI.TOTL.ZG" |
| `1960` – `2024` | Annual CPI % for each year |

### 3.3 India Data — Detailed Audit

**Country Code:** `IND` | **Country Name:** `India`

| Year | CPI (%) | Notes |
|---|---|---|
| 2010 | 11.99 | — |
| 2011 | 8.91 | — |
| 2012 | 9.48 | — |
| 2013 | 10.02 | Dataset start (aligned with other datasets) |
| 2014 | 6.67 | — |
| 2015 | 4.91 | — |
| 2016 | 4.95 | — |
| 2017 | 3.33 | Lowest in series |
| 2018 | 3.94 | — |
| 2019 | 3.73 | — |
| 2020 | 6.62 | COVID-driven spike |
| 2021 | 5.13 | — |
| 2022 | 6.70 | Russia-Ukraine commodity shock |
| 2023 | 5.65 | — |
| 2024 | 4.95 | — |
| 2025 | **MISSING** | Not yet published |

### 3.4 Data Quality Assessment

| Check | Result | Detail |
|---|---|---|
| Null values (India) | ⚠️ Minor | 2025 value missing |
| Duplicate countries | ✅ None | All 266 rows are unique |
| India row present | ✅ Yes | Country Code: IND |
| Data type consistency | ✅ Clean | All year values are float or empty string |
| Historical coverage | ✅ Excellent | India data available from 1960 |
| Relevant range (2013+) | ✅ Complete | All years 2013–2024 filled |
| Global scope | ℹ️ Note | 266 countries included; only India is needed for MVP |

### 3.5 Statistical Summary (India, 2013–2024)

| Metric | Value |
|---|---|
| Average CPI | ~6.0% |
| Minimum CPI | 3.33% (2017) |
| Maximum CPI | 10.02% (2013) |
| Standard Deviation | ~2.1% |
| Recent trend (2020–2024) | 4.9% – 6.7% range |

### 3.6 Usage in HomeGoal AI

| Use Case | Data Used |
|---|---|
| Inflation-adjusted wealth projection | India annual CPI |
| Real purchasing power calculation | Deflate nominal wealth by cumulative CPI |
| Conservative scenario | High inflation assumption (~7–8%) |
| Expected scenario | Historical average (~6%) |
| Optimistic scenario | Low inflation assumption (~4%) |
| Forecast 2025+ | Extrapolate using ARIMA / linear trend |

---

## 4. Dataset 3 — AED-INR Historical Exchange Rate

### 4.1 Source Information

| Property | Value |
|---|---|
| Source | Investing.com |
| Pair | UAE Dirham / Indian Rupee (AED/INR) |
| File | `AED_INR Historical Data.csv` |
| File Size | 8.6 KB |
| Format | CSV |

### 4.2 Structure

| Property | Value |
|---|---|
| Total Rows | 156 (excluding header) |
| Total Columns | 7 |
| Granularity | Monthly (first trading day of each month) |
| Date Range | January 2013 → December 2025 |
| Date Format | `MM/DD/YYYY` (e.g., `12/01/2025`) |

**Columns:**

| Column | Data Type | Description | Quality |
|---|---|---|---|
| `Date` | string (MM/DD/YYYY) | Month reference date | ✅ Complete |
| `Price` | float (string) | Closing AED/INR rate for the month | ✅ Complete |
| `Open` | float (string) | Opening rate | ✅ Complete |
| `High` | float (string) | Monthly high | ✅ Complete |
| `Low` | float (string) | Monthly low | ✅ Complete |
| `Vol.` | string | Trading volume | ❌ 100% empty — drop |
| `Change %` | string (e.g., "0.58%") | Month-over-month % change | ✅ Complete |

### 4.3 Data Quality Assessment

| Check | Result | Detail |
|---|---|---|
| Null values | ⚠️ One column | `Vol.` is 100% empty — will be dropped |
| Duplicate rows | ✅ None | 0 duplicate date entries |
| Missing months | ✅ None | All 156 months covered (Jan 2013 – Dec 2025) |
| Outliers (>3σ) | ✅ None | No extreme rate anomalies detected |
| Data type (Price) | ⚠️ Needs cast | Price stored as string with quotes — needs `float()` conversion |
| Date format | ⚠️ Needs parse | `MM/DD/YYYY` → must parse to `datetime` |
| BOM character | ⚠️ Minor | UTF-8 BOM present in file header — use `encoding='utf-8-sig'` |

### 4.4 Statistical Summary

| Metric | Value |
|---|---|
| Start Rate (Jan 2013) | ₹14.50 per AED |
| End Rate (Dec 2025) | ₹24.47 per AED |
| Minimum | ₹14.50 |
| Maximum | ₹24.47 |
| Average (2013–2025) | ₹19.59 |
| Total INR appreciation vs AED | +68.8% (INR weakened vs AED) |
| Approximate annual depreciation | ~4.3% per year |
| Volatility (monthly std dev) | ~₹2.5 |

### 4.5 Key Observations

1. **INR has consistently weakened against AED** — every ₹1 of AED purchasing power in 2013 buys ~₹24.47 in India now vs ₹14.50 in 2013. This benefits UAE expats sending money to India.
2. **Stable long-term trend** — no structural breaks or sudden shocks in the series. The depreciation is gradual and predictable.
3. **COVID 2020 bump** — slight spike in March 2020 (AED/INR hit ~₹20.51) followed by normalization.
4. **INR depreciation accelerated 2021–2025** — rate moved from ₹19.84 to ₹24.47 in 4 years (~+23%), the fastest stretch in the dataset.
5. **No outliers** — all values are within 3 standard deviations of the mean.

### 4.6 Usage in HomeGoal AI

| Use Case | Data Used |
|---|---|
| Convert AED salary → INR wealth | Monthly closing `Price` |
| Currency appreciation forecast | Full monthly time-series for Prophet/ARIMA |
| Conservative scenario | Slower INR depreciation (~2% p.a.) |
| Expected scenario | Historical average depreciation (~4.3% p.a.) |
| Optimistic scenario | Faster INR depreciation (~6% p.a.) = more purchasing power |
| Wealth conversion | Future AED savings × forecast rate = INR wealth |

---

## 5. Cross-Dataset Alignment

| Property | NHB HPI | World Bank CPI | AED-INR |
|---|---|---|---|
| Start Date | Q2 2013 | 2013 (annual) | Jan 2013 |
| End Date | Q4 2025 | 2024 | Dec 2025 |
| Granularity | Quarterly | Annual | Monthly |
| Common Period | 2013–2024 (46 quarters) | 2013–2024 (12 years) | 2013–2024 (144 months) |
| Aligned format | Resample to annual | Already annual | Resample to annual |
| Missing tail | None | 2025 | None |

**Alignment Strategy:**
- All three datasets will be resampled to **annual frequency** for the core modeling pipeline.
- Quarterly NHB HPI → annual average.
- Monthly AED-INR → annual average.
- CPI already annual.

---

## 6. Data Sufficiency Assessment

| Modeling Task | Dataset Required | Sufficient? |
|---|---|---|
| Housing appreciation forecast | NHB HPI | ✅ Yes (12 years quarterly data) |
| Inflation forecast | World Bank CPI | ✅ Yes (12+ years annual data) |
| Currency trend forecast | AED-INR | ✅ Yes (12 years monthly data) |
| Wealth accumulation engine | AED-INR + CPI | ✅ Yes |
| Property price projection | NHB HPI | ✅ Yes |
| Stress score engine | All three (derived) | ✅ Yes |
| Scenario engine | All three | ✅ Yes |

---

## 7. Recommended Actions

| Priority | Action | Dataset |
|---|---|---|
| P1 | Convert `HPI@Market Prices` N/A strings to `NaN` | NHB HPI |
| P1 | Impute 2025 Market HPI using Assessment HPI trend | NHB HPI |
| P1 | Parse `Quarter` column to proper `datetime` with quarter label | NHB HPI |
| P1 | Extract India-only rows and reshape to long format | World Bank CPI |
| P1 | Impute 2025 CPI using linear extrapolation | World Bank CPI |
| P1 | Parse `Date` column from `MM/DD/YYYY` to `datetime` | AED-INR |
| P1 | Cast `Price`, `Open`, `High`, `Low` from string to float | AED-INR |
| P2 | Drop `Vol.` column from AED-INR | AED-INR |
| P2 | Compute annual average exchange rate from monthly | AED-INR |
| P2 | Compute quarterly YoY growth rate for HPI | NHB HPI |
| P2 | Compute annual YoY growth rate for HPI (annual resampled) | NHB HPI |
| P3 | Join all three datasets into master annual time-series | All |
| P3 | Save processed files to `processed/` subdirectories | All |

---

## 8. Risk Flags

| Flag | Description | Mitigation |
|---|---|---|
| ⚠️ Small dataset (NHB HPI) | Only 51 rows — insufficient for deep ML | Use simpler models (Prophet, linear trend); validate with cross-val |
| ⚠️ National-level HPI | NHB HPI is not city-specific | Document assumption; use user's own price per sqft as anchor |
| ⚠️ 2025 gaps | CPI (2025) and Market HPI (2025) missing | Extrapolate; clearly label as "estimated" in UI |
| ⚠️ AED peg | AED is pegged to USD; AED/INR movement = INR/USD movement | Document this dependency in model assumptions |

---

*End of Data Audit Report*
