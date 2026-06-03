# HomeGoal AI — Data Quality Assessment & Cleaning Strategy

**Version:** 1.0  
**Date:** 2026-06-02  
**Status:** Complete  

---

## 1. Executive Summary

All three datasets are in **good condition** and require only minor, well-defined cleaning steps. No dataset has structural issues that would block modeling. The cleaning work is estimated to take **1–2 hours** of implementation time.

| Dataset | Overall Quality | Issues Found | Effort |
|---|---|---|---|
| NHB HPI | 🟡 Good | 5 N/A strings, date parsing, mixed types | Low |
| World Bank CPI | 🟢 Excellent | 1 missing year (2025), wide→long reshape | Very Low |
| AED-INR Rate | 🟢 Excellent | 1 empty column, type casting, BOM | Very Low |

---

## 2. Issue Registry

### 2.1 NHB HPI Issues

| ID | Issue | Severity | Column Affected |
|---|---|---|---|
| HPI-01 | `HPI@Market Prices` contains `'N/A'` string values in 5 rows | Medium | `HPI@Market Prices` |
| HPI-02 | Date column parsed as `datetime.datetime` object, needs standardization | Low | `Quarter` |
| HPI-03 | Mixed data types in `HPI@Market Prices` (float + string) | Medium | `HPI@Market Prices` |
| HPI-04 | Dataset starts at Q2 2013 (not Q1) — slight misalignment with Jan 2013 start of other datasets | Low | `Quarter` |
| HPI-05 | No quarterly labels (Q1/Q2/Q3/Q4) — need to derive | Low | (new column) |

### 2.2 World Bank CPI Issues

| ID | Issue | Severity | Column Affected |
|---|---|---|---|
| CPI-01 | File has 4 metadata rows before actual header | Low | File structure |
| CPI-02 | Wide format (one column per year) — needs reshaping to long format | Low | All year columns |
| CPI-03 | Contains 266 countries — need to filter India only | Low | `Country Code` |
| CPI-04 | 2025 CPI value is missing for India | Low | `2025` column |
| CPI-05 | Year columns are stored as strings — need int conversion | Low | Column names |

### 2.3 AED-INR Issues

| ID | Issue | Severity | Column Affected |
|---|---|---|---|
| FX-01 | `Vol.` column is 100% empty | Low | `Vol.` |
| FX-02 | `Date` stored as string `MM/DD/YYYY` — needs datetime conversion | Low | `Date` |
| FX-03 | Price columns stored as float strings with possible commas | Low | `Price`, `Open`, `High`, `Low` |
| FX-04 | `Change %` stored as string (e.g., `"0.58%"`) — needs numeric conversion | Low | `Change %` |
| FX-05 | UTF-8 BOM character in file — needs `encoding='utf-8-sig'` | Very Low | File header |

---

## 3. Cleaning Steps — NHB HPI

### Step 1: Load the Excel File

```python
import pandas as pd

df_hpi = pd.read_excel(
    'raw/india_housing_price_index_nhb_2013_2025.xls.xlsx',
    sheet_name='india_housing_price_index_nhb_2'
)
```

### Step 2: Rename Columns (Addresses HPI-02, HPI-05)

```python
df_hpi.columns = ['quarter', 'hpi_assessment', 'hpi_market']
```

### Step 3: Fix Mixed Types in `hpi_market` (Addresses HPI-01, HPI-03)

```python
import numpy as np

df_hpi['hpi_market'] = pd.to_numeric(df_hpi['hpi_market'], errors='coerce')
# Replaces 'N/A' strings with NaN — pandas-safe numeric column
```

### Step 4: Parse and Standardize the Quarter Column (Addresses HPI-02)

```python
df_hpi['quarter'] = pd.to_datetime(df_hpi['quarter'])
df_hpi['year'] = df_hpi['quarter'].dt.year
df_hpi['month'] = df_hpi['quarter'].dt.month
df_hpi['quarter_label'] = df_hpi['quarter'].dt.to_period('Q').astype(str)
# Produces labels like "2013Q2", "2013Q3", etc.
```

### Step 5: Create Primary HPI Column (Addresses HPI-01, HPI-03)

```python
# Use Market HPI where available; fall back to Assessment HPI for 2025 gaps
df_hpi['hpi_primary'] = df_hpi['hpi_market'].fillna(df_hpi['hpi_assessment'])
```

### Step 6: Impute Market HPI for 2025 (Addresses HPI-01)

The Market HPI for Q4 2024 – Q4 2025 is not yet published. We impute using the **Assessment HPI trend ratio**:

```python
# Calculate the ratio of Assessment to Market where both exist (pre-2024)
known = df_hpi[df_hpi['hpi_market'].notna()].copy()
ratio = (known['hpi_market'] / known['hpi_assessment']).mean()

# Impute missing Market HPI
mask = df_hpi['hpi_market'].isna()
df_hpi.loc[mask, 'hpi_market_imputed'] = df_hpi.loc[mask, 'hpi_assessment'] * ratio
df_hpi.loc[mask, 'hpi_market_is_estimated'] = True
df_hpi.loc[~mask, 'hpi_market_is_estimated'] = False
```

### Step 7: Compute Growth Rates

```python
df_hpi = df_hpi.sort_values('quarter').reset_index(drop=True)
df_hpi['hpi_qoq_pct'] = df_hpi['hpi_primary'].pct_change() * 100
df_hpi['hpi_yoy_pct'] = df_hpi['hpi_primary'].pct_change(4) * 100  # 4 quarters = 1 year
```

### Step 8: Create Annual Summary

```python
df_hpi_annual = df_hpi.groupby('year').agg(
    hpi_annual_avg=('hpi_primary', 'mean'),
).reset_index()
df_hpi_annual['hpi_annual_growth_pct'] = df_hpi_annual['hpi_annual_avg'].pct_change() * 100
```

### Step 9: Save Processed Files

```python
df_hpi.to_csv('processed/nhb_hpi/nhb_hpi_clean.csv', index=False)
df_hpi_annual.to_csv('processed/nhb_hpi/nhb_hpi_annual.csv', index=False)
```

---

## 4. Cleaning Steps — World Bank CPI

### Step 1: Load with Correct Skip Rows (Addresses CPI-01)

```python
df_cpi_raw = pd.read_csv(
    'raw/API_FP.CPI.TOTL.ZG_DS2_en_csv_v2_278989.csv',
    skiprows=4,
    encoding='utf-8'
)
```

### Step 2: Filter for India (Addresses CPI-03)

```python
df_india = df_cpi_raw[df_cpi_raw['Country Code'] == 'IND'].copy()
# Result: 1 row
```

### Step 3: Reshape Wide to Long (Addresses CPI-02, CPI-05)

```python
year_cols = [c for c in df_india.columns if c.isdigit()]

df_cpi = df_india[year_cols].T.reset_index()
df_cpi.columns = ['year', 'cpi_pct']
df_cpi['year'] = df_cpi['year'].astype(int)
df_cpi['cpi_pct'] = pd.to_numeric(df_cpi['cpi_pct'], errors='coerce')

# Keep only years with data (drop pre-1960 empties and post-2024 empties)
df_cpi = df_cpi[df_cpi['cpi_pct'].notna()].copy()
```

### Step 4: Filter Relevant Years

```python
df_cpi = df_cpi[df_cpi['year'] >= 2013].copy()
```

### Step 5: Impute 2025 CPI (Addresses CPI-04)

```python
# Method: Use 3-year average of 2022-2024 as the 2025 estimate
recent_avg = df_cpi[df_cpi['year'].isin([2022, 2023, 2024])]['cpi_pct'].mean()
row_2025 = pd.DataFrame({'year': [2025], 'cpi_pct': [round(recent_avg, 2)], 'is_estimated': [True]})
df_cpi['is_estimated'] = False
df_cpi = pd.concat([df_cpi, row_2025], ignore_index=True)
```

### Step 6: Compute Cumulative Inflation Index

```python
df_cpi = df_cpi.sort_values('year').reset_index(drop=True)
df_cpi['inflation_multiplier'] = 1 + df_cpi['cpi_pct'] / 100
df_cpi['cumulative_inflation_index'] = df_cpi['inflation_multiplier'].cumprod()
# Base = 2013; index shows how many rupees in year N = 1 rupee in 2013
```

### Step 7: Save Processed File

```python
df_cpi.to_csv('processed/inflation/india_cpi_clean.csv', index=False)
```

---

## 5. Cleaning Steps — AED-INR Exchange Rate

### Step 1: Load with BOM Encoding (Addresses FX-05)

```python
df_fx = pd.read_csv(
    'raw/AED_INR Historical Data.csv',
    encoding='utf-8-sig'  # Handles BOM character
)
```

### Step 2: Rename Columns

```python
df_fx.columns = ['date', 'rate_close', 'rate_open', 'rate_high', 'rate_low', 'vol', 'change_pct']
```

### Step 3: Drop Volume Column (Addresses FX-01)

```python
df_fx = df_fx.drop(columns=['vol'])
```

### Step 4: Parse Date Column (Addresses FX-02)

```python
df_fx['date'] = pd.to_datetime(df_fx['date'], format='%m/%d/%Y')
df_fx = df_fx.sort_values('date').reset_index(drop=True)
df_fx['year'] = df_fx['date'].dt.year
df_fx['month'] = df_fx['date'].dt.month
```

### Step 5: Cast Price Columns to Float (Addresses FX-03)

```python
for col in ['rate_close', 'rate_open', 'rate_high', 'rate_low']:
    df_fx[col] = df_fx[col].astype(str).str.replace(',', '').astype(float)
```

### Step 6: Parse Change % to Float (Addresses FX-04)

```python
df_fx['mom_change_pct'] = df_fx['change_pct'].str.replace('%', '').astype(float)
df_fx = df_fx.drop(columns=['change_pct'])
```

### Step 7: Compute YoY Change

```python
df_fx['yoy_change_pct'] = df_fx['rate_close'].pct_change(12) * 100
```

### Step 8: Create Annual Average

```python
df_fx_annual = df_fx.groupby('year').agg(
    rate_annual_avg=('rate_close', 'mean'),
    rate_annual_min=('rate_low', 'min'),
    rate_annual_max=('rate_high', 'max'),
).reset_index()
df_fx_annual['rate_annual_yoy_pct'] = df_fx_annual['rate_annual_avg'].pct_change() * 100
```

### Step 9: Save Processed Files

```python
df_fx.to_csv('processed/exchange_rate/aed_inr_clean.csv', index=False)
df_fx_annual.to_csv('processed/exchange_rate/aed_inr_annual.csv', index=False)
```

---

## 6. Master Dataset Assembly

After individual cleaning, all three annual datasets are joined into a single master time-series for modeling:

```python
df_master = df_hpi_annual \
    .merge(df_cpi[['year', 'cpi_pct', 'cumulative_inflation_index', 'is_estimated']], on='year', how='left') \
    .merge(df_fx_annual[['year', 'rate_annual_avg', 'rate_annual_yoy_pct']], on='year', how='left')

# Rename for clarity
df_master.rename(columns={
    'rate_annual_avg': 'aed_inr_rate',
    'rate_annual_yoy_pct': 'fx_yoy_pct',
    'is_estimated': 'cpi_is_estimated',
}, inplace=True)

df_master.to_csv('processed/master_annual.csv', index=False)
```

**Expected master columns:**

| Column | Source |
|---|---|
| `year` | All |
| `hpi_annual_avg` | NHB HPI |
| `hpi_annual_growth_pct` | NHB HPI |
| `cpi_pct` | World Bank |
| `cumulative_inflation_index` | World Bank |
| `cpi_is_estimated` | World Bank |
| `aed_inr_rate` | AED-INR |
| `fx_yoy_pct` | AED-INR |

---

## 7. Validation Checks (Post-Cleaning)

Run these assertions after cleaning to confirm data integrity:

```python
# NHB HPI
assert df_hpi['hpi_primary'].isna().sum() == 0, "hpi_primary must have no nulls"
assert df_hpi['hpi_assessment'].between(80, 160).all(), "HPI out of expected range"
assert df_hpi['quarter'].is_monotonic_increasing, "Quarters must be sorted"

# CPI
assert len(df_cpi) >= 12, "Must have at least 2013-2024"
assert df_cpi['cpi_pct'].between(0, 20).all(), "CPI out of expected range for India"
assert df_cpi['year'].is_unique, "Duplicate years in CPI"

# AED-INR
assert df_fx['rate_close'].isna().sum() == 0, "No nulls in closing rate"
assert df_fx['rate_close'].between(10, 30).all(), "Rate out of expected range"
assert df_fx['date'].is_monotonic_increasing, "Dates must be sorted"
assert len(df_fx) == 156, "Expected 156 monthly rows"
```

---

## 8. Cleaning Implementation File

All cleaning code will be implemented in:
- **Notebook:** `notebooks/02_data_cleaning.ipynb`
- **Script:** `models/scripts/data_cleaner.py` (reusable for backend)

---

*End of Cleaning Strategy*
