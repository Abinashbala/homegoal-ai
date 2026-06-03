# HomeGoal AI — EDA Report

**Version:** 1.0  
**Date:** 2026-06-03  
**Status:** ✅ Complete  
**Data Period:** 2013–2025 (Housing & FX) | 2013–2024 (Inflation)

---

## 1. Housing — NHB Housing Price Index

### 1.1 Annual HPI Trend

India's housing market, as measured by the NHB Housing Price Index, has been on a consistent upward trajectory since 2013.

| Metric | Value |
|---|---|
| HPI 2013 (avg) | 86.00 |
| HPI 2025 (avg) | 144.99 |
| Total appreciation | +68.6% |
| Full-period CAGR | **4.45% per year** |
| Average annual growth | 4.50% |
| Growth std dev (volatility) | 3.36% |

**Chart Reference:** `01_hpi_annual_trend.png`

The HPI crossed the 100-mark (base year ~2017-18) in line with expectations. From 2022 onwards, growth accelerated significantly, with 3 consecutive years of above-average growth (7.47%, 11.20%, 9.60%).

---

### 1.2 Annual Growth Rate Analysis

| Category | Years | Avg Growth |
|---|---|---|
| Pre-COVID (2014–2019) | 6 years | **3.19%** |
| COVID period (2020) | 1 year | **0.48%** (worst) |
| Post-COVID recovery (2021–2025) | 5 years | **6.87%** |

**Best year:** 2023 — **11.20%** (India's post-pandemic real estate boom peak)  
**Worst year:** 2020 — **0.48%** (COVID lockdowns froze market activity)

**Chart Reference:** `02_hpi_growth_rate.png`

The pre-COVID CAGR of 3.19% almost doubled to 6.87% post-COVID. This structural acceleration is a critical input for modeling.

---

### 1.3 Quarterly Granularity

The quarterly NHB HPI dataset (51 observations, Q2 2013 – Q4 2025) reveals:

- **No quarters with negative growth** — HPI never declined
- **COVID plateau:** Q1 2020 – Q2 2021 — flat growth for 5 quarters
- **Post-2022 acceleration:** Steepest gradient in the entire 12-year series
- **Quarterly volatility is low** — QoQ changes are smooth (no spikes)

**Chart Reference:** `03_hpi_quarterly_trend.png`

---

### 1.4 Rolling CAGR Analysis

| Year (CAGR from 2013 base) | CAGR |
|---|---|
| 2015 | ~5.5% |
| 2017 | ~3.4% |
| 2019 | ~3.0% |
| 2021 | ~2.5% |
| 2023 | ~3.8% |
| 2025 | **4.45%** |

The rolling CAGR dipped below 3% between 2019–2021 (reflecting pre-COVID slowdown + COVID). It has since recovered to the 4.45% long-term average, driven by post-pandemic demand.

**Chart Reference:** `04_hpi_rolling_cagr.png`

---

### 1.5 Volatility Analysis

| Metric | Value | Interpretation |
|---|---|---|
| Annual std dev | 3.36% | Moderate volatility |
| Min growth | 0.48% | Never negative |
| Max growth | 11.20% | One exceptional year |
| CoV (std/mean) | 74.7% | High relative variability |

Housing growth is **positively skewed** — more upside surprises than downside. This is typical of real estate markets in emerging economies. The distribution is right-skewed with most years clustering in the 2-5% range and a fat tail toward high growth (2022–2024).

---

## 2. AED-INR Exchange Rate

### 2.1 Annual Rate Trend

The AED-INR exchange rate has been on a secular upward trend — meaning INR has consistently weakened against the AED.

| Metric | Value |
|---|---|
| Rate 2013 avg | 16.03 INR/AED |
| Rate 2025 avg | 23.78 INR/AED |
| Total INR depreciation | +48.3% |
| Full-period CAGR | **3.34% per year** |
| Average annual change | 3.38% |
| Std dev (annual volatility) | 2.86% |

**Chart Reference:** `05_fx_monthly_trend.png`, `06_fx_annual_trend_growth.png`

---

### 2.2 Currency Depreciation Breakdown

| Category | Period | Avg Annual Rate |
|---|---|---|
| Pre-2017 | 2013–2016 | +4.5% depreciation |
| GST/demonetization dip | 2017 | **-3.45%** (INR strengthened) |
| Steady depreciation | 2018–2021 | +3.2% |
| Accelerated depreciation | 2022–2025 | +4.3% |

**Best FX year for UAE expat:** 2022 — +6.70% (more INR per AED = more purchasing power)  
**Worst FX year for UAE expat:** 2017 — -3.45% (INR strengthened temporarily, reduced INR purchasing power)

---

### 2.3 Volatility Analysis

Monthly closing rate standard deviation: **±2.42 INR**

The rolling 12-month ±2σ volatility band shows:
- 2013–2016: Band width ~₹1.5 (low volatility)
- 2018–2021: Band width ~₹2.0 (moderate)
- 2022–2025: Band width ~₹3.0 (higher, but still predictable trend)

**No structural breaks or sudden shocks** were found in the series. The AED peg to USD makes this series one of the most stable in EM currency space.

**Chart Reference:** `07_fx_volatility_band.png`

---

## 3. Inflation (India CPI)

### 3.1 Annual CPI Trend

| Metric | Value |
|---|---|
| Average CPI (2013–2024) | **5.55%** |
| Standard deviation | 1.81% |
| Highest CPI | 2013: 10.02% |
| Lowest CPI | 2017: 3.33% |
| Recent 3-year avg (2022–2024) | 5.77% |
| Cumulative inflation (2013→2024) | **1.91×** |

**Chart Reference:** `08_cpi_annual_trend.png`

---

### 3.2 High vs Low Inflation Periods

**High inflation (≥7%):**
- 2013: 10.02% — Elevated food and fuel prices, pre-RBI reform

**Medium inflation (5–7%):**
- 2014, 2020, 2021, 2022, 2023 — Most years fall in this band

**Low inflation (<5%):**
- 2015, 2016, 2017, 2018, 2019, 2024 — Policy normalization years

The trend shows **inflation is moderating** over time — from double-digit in 2013 to the 5% range in 2024.

---

### 3.3 Cumulative Inflation Impact

| Year | Cumulative Index | Meaning |
|---|---|---|
| 2013 | 1.00 | Baseline |
| 2016 | 1.29 | Rs 1L in 2013 → Rs 1.29L |
| 2019 | 1.44 | Rs 1L in 2013 → Rs 1.44L |
| 2022 | 1.72 | Rs 1L in 2013 → Rs 1.72L |
| 2024 | **1.91** | Rs 1L in 2013 → Rs **1.91L** |

A rupee saved in 2013 has lost **48%** of its purchasing power by 2024. This is the core argument for why wealth growth must outpace inflation.

**Chart Reference:** `09_cumulative_inflation.png`

---

### 3.4 Scenario Assumptions — Validation from Data

| Scenario | Assumed CPI | Data Evidence |
|---|---|---|
| Conservative (7.5%) | Above historical avg | Only 2013 exceeded this. Plausible worst-case. |
| Expected (6.0%) | Close to historical avg (5.55%) | ✅ Well-supported |
| Optimistic (4.0%) | Below historical avg | Achieved in 2015, 2018, 2019, 2024. ✅ Realistic |

---

## 4. Cross-Dataset Analysis

### 4.1 Correlation Matrix

| | HPI Growth | CPI | FX Growth | AED/INR Rate |
|---|---|---|---|---|
| **HPI Growth** | 1.000 | 0.295 | 0.276 | **0.644** |
| **CPI** | 0.295 | 1.000 | **0.562** | 0.252 |
| **FX Growth** | 0.276 | **0.562** | 1.000 | 0.129 |
| **AED/INR Rate** | **0.644** | 0.252 | 0.129 | 1.000 |

**Chart Reference:** `10_correlation_heatmap.png`

---

### 4.2 Key Relationship Findings

**Finding 1: HPI Growth vs AED/INR Rate — Strong positive (r = 0.644)**  
As the AED/INR rate increases over time (INR weakens), HPI also rises. Both are driven by the same macro factor: time. This is a spurious time-trend correlation, not a causal relationship.

**Finding 2: CPI vs FX Growth — Moderate positive (r = 0.562)**  
When India experiences higher inflation, INR tends to depreciate more. This aligns with monetary economics (purchasing power parity theory) — higher inflation countries see currency weakness.

**Finding 3: HPI Growth vs CPI — Weak positive (r = 0.295)**  
Housing growth is weakly correlated with inflation. This means HPI does not simply track inflation — it has its own demand-supply dynamics. In fact, real HPI growth (HPI − CPI) is negative on average.

**Finding 4: HPI Growth vs FX Growth — Weak positive (r = 0.276)**  
Low correlation between housing growth and currency movement. These two series are largely independent in the short run.

---

### 4.3 Real HPI Growth (HPI − CPI)

| Year | HPI Growth | CPI | Real HPI Growth |
|---|---|---|---|
| 2014 | 4.94% | 6.67% | **-1.73%** |
| 2015 | 4.99% | 4.91% | **+0.08%** |
| 2016 | 2.11% | 4.95% | **-2.84%** |
| 2017 | 1.29% | 3.33% | **-2.04%** |
| 2018 | 3.57% | 3.94% | **-0.37%** |
| 2019 | 2.22% | 3.73% | **-1.51%** |
| 2020 | 0.48% | 6.62% | **-6.14%** |
| 2021 | 2.16% | 5.13% | **-2.97%** |
| 2022 | 7.47% | 6.70% | **+0.77%** |
| 2023 | 11.20% | 5.65% | **+5.55%** |
| 2024 | 9.60% | 4.95% | **+4.65%** |

**Average Real HPI Growth: -0.59% per year**

Housing only outpaced inflation in **4 of 11 years** (2015, 2022, 2023, 2024) — and the recent outperformance is concentrated in 2022–2024.

**Chart Reference:** `14_real_hpi_vs_inflation.png`

---

### 4.4 Net AED Cost Pressure (UAE Expat Perspective)

```
Net cost pressure = HPI Growth - FX Growth (AED/INR depreciation)
```

For a UAE-based buyer, the effective INR cost increase is **HPI growth minus the FX benefit**:

| Average | Value |
|---|---|
| Average HPI growth | 4.50% |
| Average FX benefit (INR weakening) | 3.38% |
| **Net cost pressure on AED buyer** | **+1.12% per year** |

This is a critical insight: **Indian housing costs UAE expats only about 1.12% more per year in AED terms** — far less than the 4.50% INR appreciation suggests. The INR weakening acts as a natural hedge.

---

## 5. Summary Statistics

| Series | CAGR | Avg Annual | Volatility | Min | Max |
|---|---|---|---|---|---|
| HPI | 4.45% | 4.50% | 3.36% | 0.48% | 11.20% |
| AED/INR Rate | 3.34% | 3.38% | 2.86% | -3.45% | 6.70% |
| CPI (India) | ~5.55% avg | 5.55% | 1.81% | 3.33% | 10.02% |

---

*End of EDA Report*
