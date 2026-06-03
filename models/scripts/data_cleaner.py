"""
HomeGoal AI — Phase 2: Data Cleaning Pipeline
==============================================
Cleans all 3 raw datasets and produces 6 processed output files
plus a master annual dataset.

Outputs:
    processed/nhb_hpi/nhb_hpi_clean.csv
    processed/nhb_hpi/nhb_hpi_annual.csv
    processed/inflation/india_cpi_clean.csv
    processed/exchange_rate/aed_inr_clean.csv
    processed/exchange_rate/aed_inr_annual.csv
    processed/master_annual.csv

Author: HomeGoal AI Analytics Pipeline
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────
BASE = r"C:\Users\DELL\Desktop\HomeGoal AI"
RAW  = os.path.join(BASE, "raw")
PROC = os.path.join(BASE, "processed")

RAW_HPI = os.path.join(RAW, "india_housing_price_index_nhb_2013_2025.xls.xlsx")
RAW_CPI = os.path.join(RAW, "API_FP.CPI.TOTL.ZG_DS2_en_csv_v2_278989.csv")
RAW_FX  = os.path.join(RAW, "AED_INR Historical Data.csv")

OUT_HPI_CLEAN  = os.path.join(PROC, "nhb_hpi",       "nhb_hpi_clean.csv")
OUT_HPI_ANN    = os.path.join(PROC, "nhb_hpi",       "nhb_hpi_annual.csv")
OUT_CPI_CLEAN  = os.path.join(PROC, "inflation",      "india_cpi_clean.csv")
OUT_FX_CLEAN   = os.path.join(PROC, "exchange_rate",  "aed_inr_clean.csv")
OUT_FX_ANN     = os.path.join(PROC, "exchange_rate",  "aed_inr_annual.csv")
OUT_MASTER     = os.path.join(PROC, "master_annual.csv")

# ─────────────────────────────────────────────
# UTILITY FUNCTIONS
# ─────────────────────────────────────────────
PASS = "[PASS]"
FAIL = "[FAIL]"
INFO = "[INFO]"

def section(title):
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)

def check(condition, message):
    status = PASS if condition else FAIL
    print(f"  {status}  {message}")
    return condition

def cagr(start, end, periods):
    """Compound Annual Growth Rate"""
    if start <= 0 or periods <= 0:
        return np.nan
    return (end / start) ** (1 / periods) - 1

# Store cleaning summaries
summaries = {}
validation_results = {}

# ═══════════════════════════════════════════════════════════
# DATASET 1: NHB HOUSING PRICE INDEX
# ═══════════════════════════════════════════════════════════
section("DATASET 1 — NHB Housing Price Index")

# ── Load ──────────────────────────────────────────────────
df_hpi_raw = pd.read_excel(RAW_HPI, sheet_name=0)
orig_rows = len(df_hpi_raw)
orig_cols = len(df_hpi_raw.columns)
print(f"\n  Loaded: {orig_rows} rows x {orig_cols} columns")
print(f"  Columns: {df_hpi_raw.columns.tolist()}")

df_hpi = df_hpi_raw.copy()

# ── Step 1: Rename columns ────────────────────────────────
df_hpi.columns = ["quarter", "hpi_assessment", "hpi_market"]
print(f"\n  Renamed columns: {df_hpi.columns.tolist()}")

# ── Step 2: Fix mixed types — convert N/A strings to NaN ──
before_na = df_hpi["hpi_market"].isna().sum()
df_hpi["hpi_market"] = pd.to_numeric(df_hpi["hpi_market"], errors="coerce")
after_na = df_hpi["hpi_market"].isna().sum()
converted = after_na - before_na
print(f"\n  hpi_market: converted {converted} 'N/A' strings -> NaN")

# ── Step 3: Parse quarter column ──────────────────────────
df_hpi["quarter"] = pd.to_datetime(df_hpi["quarter"])
df_hpi = df_hpi.sort_values("quarter").reset_index(drop=True)
df_hpi["year"]  = df_hpi["quarter"].dt.year
df_hpi["month"] = df_hpi["quarter"].dt.month

# Derive quarter label (Q1=Jan/Feb/Mar, Q2=Apr/May/Jun, etc.)
def month_to_quarter(m):
    return f"Q{((m - 1) // 3) + 1}"

df_hpi["quarter_label"] = df_hpi.apply(
    lambda r: f"{r['year']}-{month_to_quarter(r['month'])}", axis=1
)
print(f"  Quarter range: {df_hpi['quarter_label'].iloc[0]} -> {df_hpi['quarter_label'].iloc[-1]}")

# ── Step 4: Create hpi_primary (Assessment where Market is NaN) ──
df_hpi["hpi_primary"] = df_hpi["hpi_market"].fillna(df_hpi["hpi_assessment"])
df_hpi["hpi_source"]  = np.where(df_hpi["hpi_market"].isna(), "assessment_imputed", "market")
print(f"\n  hpi_primary source breakdown:")
print(f"    market:             {(df_hpi['hpi_source']=='market').sum()} rows")
print(f"    assessment_imputed: {(df_hpi['hpi_source']=='assessment_imputed').sum()} rows")

# ── Step 5: Compute quarter-over-quarter and year-over-year growth ──
df_hpi = df_hpi.sort_values("quarter").reset_index(drop=True)
df_hpi["hpi_qoq_pct"] = df_hpi["hpi_primary"].pct_change(1) * 100
df_hpi["hpi_yoy_pct"] = df_hpi["hpi_primary"].pct_change(4) * 100  # 4 quarters

# ── Step 6: Validate quarterly continuity ─────────────────
quarters = pd.date_range(
    start=df_hpi["quarter"].min(),
    end=df_hpi["quarter"].max(),
    freq="QS-JUN"   # Quarter starts in Jun, Sep, Dec, Mar (NHB pattern)
)
# More robust check: just verify count is 51 and dates are sorted
actual_count   = len(df_hpi)
is_sorted      = df_hpi["quarter"].is_monotonic_increasing
has_no_dups    = df_hpi["quarter"].nunique() == len(df_hpi)

# ── Save cleaned HPI ──────────────────────────────────────
df_hpi.to_csv(OUT_HPI_CLEAN, index=False)
print(f"\n  Saved: {OUT_HPI_CLEAN}")

# ── Step 7: Create annual resampled dataset ───────────────
df_hpi_annual = (
    df_hpi.groupby("year")
    .agg(
        hpi_assessment_avg = ("hpi_assessment", "mean"),
        hpi_market_avg     = ("hpi_market",     "mean"),   # NaN for 2025
        hpi_primary_avg    = ("hpi_primary",    "mean"),
        quarters_in_year   = ("quarter",        "count"),
    )
    .reset_index()
)
df_hpi_annual["hpi_annual_growth_pct"] = df_hpi_annual["hpi_primary_avg"].pct_change() * 100

# Compute full-period CAGR
start_val = df_hpi_annual["hpi_primary_avg"].iloc[0]
end_val   = df_hpi_annual["hpi_primary_avg"].iloc[-1]
n_years   = len(df_hpi_annual) - 1
full_cagr = cagr(start_val, end_val, n_years)
df_hpi_annual["hpi_cagr_from_2013"] = [
    cagr(start_val, row["hpi_primary_avg"], row["year"] - df_hpi_annual["year"].iloc[0])
    if row["year"] > df_hpi_annual["year"].iloc[0] else np.nan
    for _, row in df_hpi_annual.iterrows()
]

df_hpi_annual.to_csv(OUT_HPI_ANN, index=False)
print(f"  Saved: {OUT_HPI_ANN}")
print(f"\n  Annual HPI Summary:")
print(f"    Years covered: {df_hpi_annual['year'].iloc[0]} - {df_hpi_annual['year'].iloc[-1]}")
print(f"    Full-period CAGR: {full_cagr*100:.2f}% per year")
print(f"    HPI start (2013 avg): {start_val:.2f}")
print(f"    HPI end ({df_hpi_annual['year'].iloc[-1]} avg): {end_val:.2f}")

# ── Validation ────────────────────────────────────────────
print(f"\n  Validation — nhb_hpi_clean.csv:")
checks_hpi = []
checks_hpi.append(check(len(df_hpi) == 51,                           f"Row count = 51 (got {len(df_hpi)})"))
checks_hpi.append(check(len(df_hpi.columns) == 10,                   f"Column count = 10 (got {len(df_hpi.columns)})"))
checks_hpi.append(check(df_hpi["hpi_primary"].isna().sum() == 0,     f"hpi_primary has 0 nulls"))
checks_hpi.append(check(df_hpi["hpi_assessment"].isna().sum() == 0,  f"hpi_assessment has 0 nulls"))
checks_hpi.append(check(is_sorted,                                    f"Quarters are monotonically increasing"))
checks_hpi.append(check(has_no_dups,                                  f"No duplicate quarters"))
checks_hpi.append(check(df_hpi["hpi_primary"].between(80, 160).all(), f"HPI values in expected range [80, 160]"))
checks_hpi.append(check(df_hpi["hpi_source"].isin(["market","assessment_imputed"]).all(), f"hpi_source values valid"))

# Track summary
summaries["nhb_hpi"] = {
    "original_rows": orig_rows, "final_rows": len(df_hpi),
    "original_cols": orig_cols, "final_cols": len(df_hpi.columns),
    "rows_removed": 0, "cols_added": len(df_hpi.columns) - orig_cols,
    "nulls_handled": converted,
    "transformations": ["Renamed columns", "N/A->NaN conversion", "Date parsing",
                        "hpi_primary column", "QoQ/YoY growth rates", "Annual resampling"],
}
validation_results["nhb_hpi"] = {"total": len(checks_hpi), "passed": sum(checks_hpi)}


# ═══════════════════════════════════════════════════════════
# DATASET 2: WORLD BANK INFLATION (India CPI)
# ═══════════════════════════════════════════════════════════
section("DATASET 2 — World Bank Inflation (India CPI)")

# ── Load ──────────────────────────────────────────────────
df_cpi_raw = pd.read_csv(RAW_CPI, skiprows=4, encoding="utf-8")
orig_rows_cpi = len(df_cpi_raw)
orig_cols_cpi = len(df_cpi_raw.columns)
print(f"\n  Loaded: {orig_rows_cpi} rows x {orig_cols_cpi} columns")

# ── Step 1: Filter India only ─────────────────────────────
df_india = df_cpi_raw[df_cpi_raw["Country Code"] == "IND"].copy()
print(f"  India row found: {len(df_india) == 1}")

# ── Step 2: Reshape wide -> long ──────────────────────────
year_cols = [c for c in df_india.columns if c.strip().isdigit()]
df_cpi = df_india[year_cols].T.reset_index()
df_cpi.columns = ["year", "cpi_pct"]
df_cpi["year"]    = df_cpi["year"].astype(int)
df_cpi["cpi_pct"] = pd.to_numeric(df_cpi["cpi_pct"], errors="coerce")

# ── Step 3: Keep relevant years (2013–2024) ───────────────
df_cpi = df_cpi[df_cpi["year"].between(2013, 2024)].copy()
df_cpi = df_cpi[df_cpi["cpi_pct"].notna()].copy()
df_cpi = df_cpi.sort_values("year").reset_index(drop=True)
print(f"  Filtered to {len(df_cpi)} rows (2013-2024)")
print(f"  India CPI range: {df_cpi['cpi_pct'].min():.2f}% - {df_cpi['cpi_pct'].max():.2f}%")
print(f"  India CPI average (2013-2024): {df_cpi['cpi_pct'].mean():.2f}%")

# ── Step 4: Cumulative inflation index (base 2013 = 1.0) ──
df_cpi["inflation_multiplier"]      = 1 + df_cpi["cpi_pct"] / 100
df_cpi["cumulative_inflation_index"] = df_cpi["inflation_multiplier"].cumprod()
df_cpi["is_estimated"]              = False

# ── Step 5: Validate annual continuity ───────────────────
expected_years = list(range(2013, 2025))
actual_years   = df_cpi["year"].tolist()

# ── Save ──────────────────────────────────────────────────
df_cpi.to_csv(OUT_CPI_CLEAN, index=False)
print(f"\n  Saved: {OUT_CPI_CLEAN}")
print(f"  Cumulative inflation 2013->2024: {df_cpi['cumulative_inflation_index'].iloc[-1]:.4f}x")
print(f"  (₹1 in 2013 = ₹{df_cpi['cumulative_inflation_index'].iloc[-1]:.2f} in 2024)")

# ── Scenario inflation params confirmed ──────────────────
avg_cpi = df_cpi["cpi_pct"].mean()
print(f"\n  Scenario Inflation Assumptions (scenario-based, no ML):")
print(f"    Conservative: 7.5%  (above historical avg {avg_cpi:.1f}%)")
print(f"    Expected:     6.0%  (close to historical avg)")
print(f"    Optimistic:   4.0%  (below historical avg)")

# ── Validation ────────────────────────────────────────────
print(f"\n  Validation — india_cpi_clean.csv:")
checks_cpi = []
checks_cpi.append(check(len(df_cpi) == 12,                          f"Row count = 12 (2013-2024) (got {len(df_cpi)})"))
checks_cpi.append(check(df_cpi["cpi_pct"].isna().sum() == 0,        f"No null CPI values"))
checks_cpi.append(check(actual_years == expected_years,              f"All years 2013-2024 present"))
checks_cpi.append(check(df_cpi["year"].is_unique,                   f"No duplicate years"))
checks_cpi.append(check(df_cpi["cpi_pct"].between(0, 20).all(),     f"CPI values in expected range [0, 20]"))
checks_cpi.append(check(df_cpi["cumulative_inflation_index"].is_monotonic_increasing,
                                                                      f"Cumulative inflation index is monotonic"))

summaries["india_cpi"] = {
    "original_rows": orig_rows_cpi, "final_rows": len(df_cpi),
    "original_cols": orig_cols_cpi, "final_cols": len(df_cpi.columns),
    "rows_removed": orig_rows_cpi - 1,  # kept only India
    "cols_added": len(df_cpi.columns) - 2,
    "nulls_handled": 0,
    "transformations": ["Filtered India only (IND)", "Wide->Long reshape",
                        "Year range filter (2013-2024)", "Cumulative inflation index computed"],
}
validation_results["india_cpi"] = {"total": len(checks_cpi), "passed": sum(checks_cpi)}


# ═══════════════════════════════════════════════════════════
# DATASET 3: AED-INR EXCHANGE RATE
# ═══════════════════════════════════════════════════════════
section("DATASET 3 — AED-INR Exchange Rate")

# ── Load ──────────────────────────────────────────────────
df_fx_raw = pd.read_csv(RAW_FX, encoding="utf-8-sig")
orig_rows_fx = len(df_fx_raw)
orig_cols_fx = len(df_fx_raw.columns)
print(f"\n  Loaded: {orig_rows_fx} rows x {orig_cols_fx} columns")
print(f"  Columns: {df_fx_raw.columns.tolist()}")

df_fx = df_fx_raw.copy()

# ── Step 1: Rename columns ────────────────────────────────
df_fx.columns = ["date", "rate_close", "rate_open", "rate_high", "rate_low", "vol", "change_pct"]

# ── Step 2: Drop Vol column (100% empty) ─────────────────
df_fx = df_fx.drop(columns=["vol"])
print(f"  Dropped 'vol' column (was 100% empty)")

# ── Step 3: Parse date ────────────────────────────────────
df_fx["date"] = pd.to_datetime(df_fx["date"], format="%m/%d/%Y")
df_fx = df_fx.sort_values("date").reset_index(drop=True)
df_fx["year"]  = df_fx["date"].dt.year
df_fx["month"] = df_fx["date"].dt.month
print(f"  Date range: {df_fx['date'].iloc[0].strftime('%Y-%m')} -> {df_fx['date'].iloc[-1].strftime('%Y-%m')}")

# ── Step 4: Cast price columns to float ──────────────────
for col in ["rate_close", "rate_open", "rate_high", "rate_low"]:
    df_fx[col] = df_fx[col].astype(str).str.replace(",", "").astype(float)

# ── Step 5: Parse change % ───────────────────────────────
df_fx["mom_change_pct"] = (
    df_fx["change_pct"]
    .astype(str)
    .str.replace("%", "")
    .str.strip()
    .astype(float)
)
df_fx = df_fx.drop(columns=["change_pct"])

# ── Step 6: Year-over-Year change ────────────────────────
df_fx["yoy_change_pct"] = df_fx["rate_close"].pct_change(12) * 100

# ── Step 7: Validate monthly continuity ──────────────────
expected_months = pd.date_range("2013-01-01", "2025-12-01", freq="MS")
actual_dates    = df_fx["date"].tolist()
missing_months  = [d for d in expected_months if d not in actual_dates]

print(f"  Missing months: {len(missing_months)}")
print(f"  Total rows: {len(df_fx)} (expected 156)")

# ── Save cleaned FX ───────────────────────────────────────
df_fx.to_csv(OUT_FX_CLEAN, index=False)
print(f"\n  Saved: {OUT_FX_CLEAN}")

# ── Step 8: Create annual average ────────────────────────
df_fx_annual = (
    df_fx.groupby("year")
    .agg(
        rate_annual_avg   = ("rate_close", "mean"),
        rate_annual_min   = ("rate_low",   "min"),
        rate_annual_max   = ("rate_high",  "max"),
        rate_annual_open  = ("rate_open",  "first"),
        rate_annual_close = ("rate_close", "last"),
        months_in_year    = ("date",       "count"),
    )
    .reset_index()
)
df_fx_annual["rate_annual_yoy_pct"] = df_fx_annual["rate_annual_avg"].pct_change() * 100

# Full-period CAGR
fx_start = df_fx_annual["rate_annual_avg"].iloc[0]
fx_end   = df_fx_annual["rate_annual_avg"].iloc[-1]
fx_years = len(df_fx_annual) - 1
fx_cagr  = cagr(fx_start, fx_end, fx_years)
print(f"\n  Annual FX Summary:")
print(f"    Years covered: {df_fx_annual['year'].iloc[0]} - {df_fx_annual['year'].iloc[-1]}")
print(f"    Rate 2013 avg: {fx_start:.2f} INR/AED")
print(f"    Rate 2025 avg: {fx_end:.2f} INR/AED")
print(f"    Full-period CAGR: {fx_cagr*100:.2f}% per year")

df_fx_annual.to_csv(OUT_FX_ANN, index=False)
print(f"  Saved: {OUT_FX_ANN}")

# ── Validation ────────────────────────────────────────────
print(f"\n  Validation — aed_inr_clean.csv:")
checks_fx = []
checks_fx.append(check(len(df_fx) == 156,                           f"Row count = 156 (got {len(df_fx)})"))
checks_fx.append(check(len(missing_months) == 0,                    f"No missing months"))
checks_fx.append(check(df_fx["rate_close"].isna().sum() == 0,       f"No null closing rates"))
checks_fx.append(check(df_fx["date"].is_monotonic_increasing,       f"Dates are sorted ascending"))
checks_fx.append(check(df_fx["date"].nunique() == len(df_fx),       f"No duplicate dates"))
checks_fx.append(check(df_fx["rate_close"].between(10, 30).all(),   f"Rate values in expected range [10, 30]"))
checks_fx.append(check("vol" not in df_fx.columns,                  f"Vol column removed"))

summaries["aed_inr"] = {
    "original_rows": orig_rows_fx, "final_rows": len(df_fx),
    "original_cols": orig_cols_fx, "final_cols": len(df_fx.columns),
    "rows_removed": 0, "cols_removed": 1,
    "nulls_handled": 0,
    "transformations": ["Renamed columns", "Dropped Vol column",
                        "Parsed date to datetime", "Cast price columns to float",
                        "Parsed Change% to float", "Computed MoM/YoY change",
                        "Annual average dataset created"],
}
validation_results["aed_inr"] = {"total": len(checks_fx), "passed": sum(checks_fx)}


# ═══════════════════════════════════════════════════════════
# MASTER ANNUAL DATASET
# ═══════════════════════════════════════════════════════════
section("MASTER ANNUAL DATASET")

# Join HPI annual + CPI + FX annual on year
df_master = df_hpi_annual[["year", "hpi_primary_avg", "hpi_annual_growth_pct"]].copy()
df_master.rename(columns={
    "hpi_primary_avg":       "hpi_index",
    "hpi_annual_growth_pct": "hpi_growth_pct",
}, inplace=True)

# Add assessment-only column for reference
df_master = df_master.merge(
    df_hpi_annual[["year", "hpi_assessment_avg"]].rename(columns={"hpi_assessment_avg": "hpi_assessment"}),
    on="year", how="left"
)

# Merge CPI
df_master = df_master.merge(
    df_cpi[["year", "cpi_pct", "cumulative_inflation_index"]],
    on="year", how="left"
)

# Merge FX annual
df_master = df_master.merge(
    df_fx_annual[["year", "rate_annual_avg", "rate_annual_yoy_pct"]].rename(columns={
        "rate_annual_avg":     "aed_inr_rate",
        "rate_annual_yoy_pct": "fx_growth_pct",
    }),
    on="year", how="left"
)

df_master = df_master.sort_values("year").reset_index(drop=True)

print(f"\n  Master dataset: {len(df_master)} rows x {len(df_master.columns)} columns")
print(f"  Columns: {df_master.columns.tolist()}")
print(f"\n  Coverage per column (non-null):")
for col in df_master.columns:
    n_valid = df_master[col].notna().sum()
    print(f"    {col}: {n_valid}/{len(df_master)} years")

df_master.to_csv(OUT_MASTER, index=False)
print(f"\n  Saved: {OUT_MASTER}")

# Validate master
print(f"\n  Validation — master_annual.csv:")
checks_master = []
checks_master.append(check(len(df_master) >= 12,               f"At least 12 years of data"))
checks_master.append(check("year"         in df_master.columns, f"year column present"))
checks_master.append(check("hpi_index"    in df_master.columns, f"hpi_index column present"))
checks_master.append(check("hpi_growth_pct" in df_master.columns, f"hpi_growth_pct column present"))
checks_master.append(check("cpi_pct"      in df_master.columns, f"cpi_pct column present"))
checks_master.append(check("aed_inr_rate" in df_master.columns, f"aed_inr_rate column present"))
checks_master.append(check("fx_growth_pct" in df_master.columns, f"fx_growth_pct column present"))
checks_master.append(check(df_master["year"].is_monotonic_increasing, f"Years are sorted"))

validation_results["master"] = {"total": len(checks_master), "passed": sum(checks_master)}


# ═══════════════════════════════════════════════════════════
# FINAL SUMMARY REPORT
# ═══════════════════════════════════════════════════════════
section("CLEANING SUMMARY REPORT")

datasets = {
    "nhb_hpi":   ("NHB HPI",           OUT_HPI_CLEAN),
    "india_cpi": ("India CPI",         OUT_CPI_CLEAN),
    "aed_inr":   ("AED-INR Rate",      OUT_FX_CLEAN),
}

for key, (name, path) in datasets.items():
    s = summaries[key]
    v = validation_results[key]
    quality_score = round(v["passed"] / v["total"] * 100)
    print(f"\n  {name}")
    print(f"    Original:       {s['original_rows']} rows x {s['original_cols']} cols")
    print(f"    Final:          {s['final_rows']} rows x {s['final_cols']} cols")
    print(f"    Rows removed:   {s.get('rows_removed', 0)}")
    print(f"    Nulls handled:  {s.get('nulls_handled', 0)}")
    print(f"    Validation:     {v['passed']}/{v['total']} checks passed")
    print(f"    Quality score:  {quality_score}%")

print()
print("  Master dataset:")
mv = validation_results["master"]
print(f"    Validation: {mv['passed']}/{mv['total']} checks passed")

print()
print("=" * 60)
print("  OUTPUT FILES")
print("=" * 60)
outputs = [
    OUT_HPI_CLEAN, OUT_HPI_ANN, OUT_CPI_CLEAN,
    OUT_FX_CLEAN,  OUT_FX_ANN,  OUT_MASTER,
]
for f in outputs:
    exists = os.path.exists(f)
    size   = os.path.getsize(f) if exists else 0
    status = "[OK]" if exists else "[MISSING]"
    print(f"  {status}  {os.path.relpath(f, BASE)}  ({size:,} bytes)")

print()
all_checks = sum(v["passed"] for v in validation_results.values())
all_total  = sum(v["total"]  for v in validation_results.values())
print(f"  OVERALL: {all_checks}/{all_total} validation checks passed")
print()
print("  Phase 2 — Data Cleaning COMPLETE.")
print("  Awaiting approval to proceed to Phase 3 (EDA).")
print()
