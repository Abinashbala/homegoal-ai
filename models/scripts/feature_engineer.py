"""
HomeGoal AI — Phase 4: Feature Engineering Pipeline
====================================================

Groups 1–3: Historical features (pre-computed, saved to disk).
Groups 4–6: Runtime formula library (documented and implemented here).

Outputs:
    processed/features_annual.csv        <- Groups 1-3 combined
    processed/modeling/hpi_model_input.csv   <- HPI model training set
    processed/modeling/fx_model_input.csv    <- FX model training set

Author: HomeGoal AI Analytics Pipeline
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")

import os, warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

# ── PATHS ─────────────────────────────────────────────────────────────
BASE = r"C:\Users\DELL\Desktop\HomeGoal AI"
PROC = os.path.join(BASE, "processed")

# ── LOAD ──────────────────────────────────────────────────────────────
df_master = pd.read_csv(os.path.join(PROC, "master_annual.csv"))
df_hpi_q  = pd.read_csv(os.path.join(PROC, "nhb_hpi", "nhb_hpi_clean.csv"), parse_dates=["quarter"])
df_hpi_a  = pd.read_csv(os.path.join(PROC, "nhb_hpi", "nhb_hpi_annual.csv"))
df_fx     = pd.read_csv(os.path.join(PROC, "exchange_rate", "aed_inr_clean.csv"), parse_dates=["date"])
df_fx_a   = pd.read_csv(os.path.join(PROC, "exchange_rate", "aed_inr_annual.csv"))
df_cpi    = pd.read_csv(os.path.join(PROC, "inflation", "india_cpi_clean.csv"))

SEP = "=" * 65

def section(title):
    print(); print(SEP); print(f"  {title}"); print(SEP)

def check(condition, msg):
    print(f"  {'[PASS]' if condition else '[FAIL]'}  {msg}")
    return condition

# ══════════════════════════════════════════════════════════════════════
# GROUP 1 — HOUSING FEATURES
# ══════════════════════════════════════════════════════════════════════
section("GROUP 1: HOUSING FEATURES")

df_hpi = df_hpi_a.copy()
df_hpi = df_hpi.sort_values("year").reset_index(drop=True)

# 1. hpi_growth_pct — already in annual file, verify & keep
df_hpi["hpi_growth_pct"] = df_hpi["hpi_primary_avg"].pct_change() * 100

# 2. rolling_hpi_growth_3y — 3-year centered rolling mean
df_hpi["rolling_hpi_growth_3y"] = (
    df_hpi["hpi_growth_pct"].rolling(window=3, min_periods=2).mean()
)

# 3. rolling_hpi_growth_5y — 5-year rolling mean
df_hpi["rolling_hpi_growth_5y"] = (
    df_hpi["hpi_growth_pct"].rolling(window=5, min_periods=3).mean()
)

# 4. hpi_cagr_from_2013 — CAGR from the 2013 base each year
base_hpi = df_hpi["hpi_primary_avg"].iloc[0]
base_yr  = int(df_hpi["year"].iloc[0])
def cagr_from_base(val, yr):
    n = yr - base_yr
    if n <= 0 or base_hpi <= 0: return np.nan
    return ((val / base_hpi) ** (1/n) - 1) * 100

df_hpi["hpi_cagr_from_2013"] = df_hpi.apply(
    lambda r: cagr_from_base(r["hpi_primary_avg"], int(r["year"])), axis=1
)

# 5. post_covid_hpi_growth — rolling 3y avg restricted to post-2021 years
# For historical rows: flag and compute rolling avg within post-COVID window
df_hpi["is_post_covid"] = (df_hpi["year"] >= 2021).astype(int)
df_hpi["post_covid_hpi_growth"] = np.where(
    df_hpi["is_post_covid"] == 1,
    df_hpi["hpi_growth_pct"].rolling(window=3, min_periods=1).mean(),
    np.nan
)

# Derived constants for scenario engine
hpi_cagr_full    = cagr_from_base(df_hpi["hpi_primary_avg"].iloc[-1], int(df_hpi["year"].iloc[-1]))
hpi_cagr_5yr     = cagr_from_base(
    df_hpi[df_hpi["year"] == 2025]["hpi_primary_avg"].iloc[0],
    2025
) if not df_hpi[df_hpi["year"] == 2025].empty else np.nan

pre_covid_cagr   = df_hpi[(df_hpi["year"] >= 2014) & (df_hpi["year"] <= 2019)]["hpi_growth_pct"].mean()
post_covid_cagr  = df_hpi[df_hpi["year"] >= 2021]["hpi_growth_pct"].mean()
recent_3y_hpi    = df_hpi[df_hpi["year"] >= 2022]["hpi_growth_pct"].mean()

print(f"\n  hpi_cagr_full (2013-2025):   {hpi_cagr_full:.2f}%")
print(f"  pre_covid_cagr (2014-2019):  {pre_covid_cagr:.2f}%")
print(f"  post_covid_cagr (2021-2025): {post_covid_cagr:.2f}%")
print(f"  recent_3y_hpi (2022-2024):   {recent_3y_hpi:.2f}%")
print(f"\n  Housing features added: {['hpi_growth_pct','rolling_hpi_growth_3y','rolling_hpi_growth_5y','hpi_cagr_from_2013','post_covid_hpi_growth']}")
print(f"\n  HPI feature sample (last 5 rows):")
cols_hpi = ["year","hpi_primary_avg","hpi_growth_pct","rolling_hpi_growth_3y","rolling_hpi_growth_5y","hpi_cagr_from_2013","post_covid_hpi_growth"]
print(df_hpi[cols_hpi].tail(5).round(4).to_string(index=False))


# ══════════════════════════════════════════════════════════════════════
# GROUP 2 — CURRENCY FEATURES
# ══════════════════════════════════════════════════════════════════════
section("GROUP 2: CURRENCY FEATURES")

df_fx_feat = df_fx_a.copy()
df_fx_feat = df_fx_feat.sort_values("year").reset_index(drop=True)

# 1. fx_growth_pct — already in file as rate_annual_yoy_pct, rename
df_fx_feat["fx_growth_pct"] = df_fx_feat["rate_annual_yoy_pct"]

# 2. rolling_fx_growth_3y
df_fx_feat["rolling_fx_growth_3y"] = (
    df_fx_feat["fx_growth_pct"].rolling(window=3, min_periods=2).mean()
)

# 3. rolling_fx_growth_5y
df_fx_feat["rolling_fx_growth_5y"] = (
    df_fx_feat["fx_growth_pct"].rolling(window=5, min_periods=3).mean()
)

# 4. fx_cagr_from_2013
base_fx = df_fx_feat["rate_annual_avg"].iloc[0]
def fx_cagr_from_base(val, yr):
    n = yr - 2013
    if n <= 0 or base_fx <= 0: return np.nan
    return ((val / base_fx) ** (1/n) - 1) * 100

df_fx_feat["fx_cagr_from_2013"] = df_fx_feat.apply(
    lambda r: fx_cagr_from_base(r["rate_annual_avg"], int(r["year"])), axis=1
)

# 5. currency_volatility_index — rolling 3-year std dev of annual FX growth
df_fx_feat["currency_volatility_index"] = (
    df_fx_feat["fx_growth_pct"].rolling(window=3, min_periods=2).std()
)

# Derived constants
fx_cagr_full   = fx_cagr_from_base(df_fx_feat["rate_annual_avg"].iloc[-1], int(df_fx_feat["year"].iloc[-1]))
recent_3y_fx   = df_fx_feat[df_fx_feat["year"] >= 2022]["fx_growth_pct"].mean()
recent_5y_fx   = df_fx_feat[df_fx_feat["year"] >= 2020]["fx_growth_pct"].mean()
avg_volatility = df_fx_feat["currency_volatility_index"].mean()

print(f"\n  fx_cagr_full (2013-2025):    {fx_cagr_full:.2f}%")
print(f"  recent_3y_fx (2022-2025):    {recent_3y_fx:.2f}%")
print(f"  recent_5y_fx (2020-2025):    {recent_5y_fx:.2f}%")
print(f"  avg_volatility_index:        {avg_volatility:.2f}%")

print(f"\n  FX feature sample (last 5 rows):")
cols_fx = ["year","rate_annual_avg","fx_growth_pct","rolling_fx_growth_3y","rolling_fx_growth_5y","fx_cagr_from_2013","currency_volatility_index"]
print(df_fx_feat[cols_fx].tail(5).round(4).to_string(index=False))


# ══════════════════════════════════════════════════════════════════════
# GROUP 3 — INFLATION FEATURES
# ══════════════════════════════════════════════════════════════════════
section("GROUP 3: INFLATION FEATURES")

df_infl = df_cpi.copy()
df_infl = df_infl.sort_values("year").reset_index(drop=True)

# 1. cumulative_inflation_index — already exists, verify
assert "cumulative_inflation_index" in df_infl.columns
print(f"\n  cumulative_inflation_index already present (2013-2024)")

# 2. rolling_inflation_3y
df_infl["rolling_inflation_3y"] = (
    df_infl["cpi_pct"].rolling(window=3, min_periods=2).mean()
)

# 3. rolling_inflation_5y
df_infl["rolling_inflation_5y"] = (
    df_infl["cpi_pct"].rolling(window=5, min_periods=3).mean()
)

# 4. inflation_regime — Low / Moderate / High
def classify_inflation(pct):
    if pct < 4.0:   return "Low"
    if pct <= 6.0:  return "Moderate"
    return "High"

df_infl["inflation_regime"] = df_infl["cpi_pct"].apply(classify_inflation)

# Derived statistics
avg_infl   = df_infl["cpi_pct"].mean()
roll3_last = df_infl["rolling_inflation_3y"].dropna().iloc[-1]
roll5_last = df_infl["rolling_inflation_5y"].dropna().iloc[-1]
regime_counts = df_infl["inflation_regime"].value_counts()

print(f"\n  Average CPI (2013-2024):     {avg_infl:.2f}%")
print(f"  Rolling 3Y avg (last):       {roll3_last:.2f}%")
print(f"  Rolling 5Y avg (last):       {roll5_last:.2f}%")
print(f"\n  Inflation Regime Distribution:")
for regime, count in regime_counts.items():
    print(f"    {regime}: {count} year(s)")

print(f"\n  Inflation features sample:")
cols_infl = ["year","cpi_pct","cumulative_inflation_index","rolling_inflation_3y","rolling_inflation_5y","inflation_regime"]
print(df_infl[cols_infl].to_string(index=False))


# ══════════════════════════════════════════════════════════════════════
# COMBINE — MASTER FEATURES ANNUAL DATASET
# ══════════════════════════════════════════════════════════════════════
section("BUILDING FEATURES ANNUAL DATASET")

# Base: master
feat = df_master.copy()

# Merge HPI features
hpi_merge = df_hpi[["year","hpi_growth_pct","rolling_hpi_growth_3y","rolling_hpi_growth_5y",
                     "hpi_cagr_from_2013","post_covid_hpi_growth","is_post_covid"]]
feat = feat.merge(hpi_merge, on="year", how="left", suffixes=("", "_hpi"))
# hpi_growth_pct exists in master; the merged one may create a dup — resolve
if "hpi_growth_pct_hpi" in feat.columns:
    feat["hpi_growth_pct"] = feat["hpi_growth_pct"].fillna(feat["hpi_growth_pct_hpi"])
    feat.drop(columns=["hpi_growth_pct_hpi"], inplace=True)

# Merge FX features
fx_merge  = df_fx_feat[["year","fx_growth_pct","rolling_fx_growth_3y","rolling_fx_growth_5y",
                          "fx_cagr_from_2013","currency_volatility_index"]]
feat = feat.merge(fx_merge, on="year", how="left", suffixes=("","_fx"))
if "fx_growth_pct_fx" in feat.columns:
    feat["fx_growth_pct"] = feat["fx_growth_pct"].fillna(feat["fx_growth_pct_fx"])
    feat.drop(columns=["fx_growth_pct_fx"], inplace=True)

# Merge inflation features
infl_merge = df_infl[["year","rolling_inflation_3y","rolling_inflation_5y","inflation_regime"]]
feat = feat.merge(infl_merge, on="year", how="left")

feat = feat.sort_values("year").reset_index(drop=True)

# Derived scenario anchors (constants — not per-row features)
feat["scenario_conservative_hpi"]  = pre_covid_cagr        # 3.19%
feat["scenario_expected_hpi"]       = round(hpi_cagr_full, 4)  # 4.45%
feat["scenario_optimistic_hpi"]     = round(post_covid_cagr, 4) # 6.87%

feat["scenario_conservative_fx"]   = 2.00
feat["scenario_expected_fx"]        = round(fx_cagr_full, 4)    # 3.34%
feat["scenario_optimistic_fx"]      = round(recent_3y_fx, 4)    # ~4.5%

feat["scenario_conservative_cpi"]  = 7.50
feat["scenario_expected_cpi"]       = 6.00
feat["scenario_optimistic_cpi"]     = 4.00

out_path = os.path.join(PROC, "features_annual.csv")
feat.to_csv(out_path, index=False)
print(f"\n  Saved: processed/features_annual.csv")
print(f"  Shape: {feat.shape[0]} rows x {feat.shape[1]} columns")
print(f"\n  All columns in features_annual.csv:")
for i, c in enumerate(feat.columns, 1):
    n_null = feat[c].isna().sum()
    print(f"    {i:2}. {c:<40}  nulls={n_null}")


# ══════════════════════════════════════════════════════════════════════
# MODELING INPUT DATASET 1 — HPI MODEL TRAINING DATA
# ══════════════════════════════════════════════════════════════════════
section("HPI MODEL INPUT DATASET (Quarterly)")

df_q = df_hpi_q.copy().sort_values("quarter").reset_index(drop=True)

# Time features
df_q["year"]        = df_q["quarter"].dt.year
df_q["month"]       = df_q["quarter"].dt.month
df_q["quarter_num"] = df_q["month"].map({3:1, 6:2, 9:3, 12:4})
df_q["t"]           = range(len(df_q))            # linear time index

# Lag features
df_q["hpi_lag1"]    = df_q["hpi_primary"].shift(1)   # t-1 quarter
df_q["hpi_lag4"]    = df_q["hpi_primary"].shift(4)   # t-4 (1 year ago)
df_q["hpi_lag8"]    = df_q["hpi_primary"].shift(8)   # t-8 (2 years ago)
df_q["growth_lag1"] = df_q["hpi_qoq_pct"].shift(1)

# Rolling average (4-quarter = 1 year)
df_q["hpi_roll4q"]  = df_q["hpi_primary"].rolling(4, min_periods=2).mean()

# Regime flag
df_q["post_covid"]  = (df_q["year"] >= 2022).astype(int)
df_q["covid_period"]= ((df_q["year"] == 2020) | (df_q["year"] == 2021)).astype(int)

# Log transform for exponential model
df_q["log_hpi"]     = np.log(df_q["hpi_primary"])

# Train / test split flag (train: up to Q4 2021, test: Q1 2022 onwards)
df_q["split"] = np.where(df_q["year"] <= 2021, "train", "test")

# Save
hpi_model_cols = [
    "quarter","year","quarter_num","t",
    "hpi_primary","log_hpi",
    "hpi_lag1","hpi_lag4","hpi_lag8",
    "growth_lag1","hpi_roll4q",
    "hpi_qoq_pct","hpi_yoy_pct",
    "post_covid","covid_period",
    "hpi_source","split"
]
df_hpi_model = df_q[hpi_model_cols].copy()
hpi_out = os.path.join(PROC, "modeling", "hpi_model_input.csv")
df_hpi_model.to_csv(hpi_out, index=False)

train_n = (df_hpi_model["split"] == "train").sum()
test_n  = (df_hpi_model["split"] == "test").sum()
print(f"\n  HPI Model Input: {len(df_hpi_model)} quarterly rows")
print(f"  Train: {train_n} rows (Q2 2013 – Q4 2021)")
print(f"  Test:  {test_n} rows  (Q1 2022 – Q4 2025)")
print(f"  Saved: processed/modeling/hpi_model_input.csv")
print(f"\n  Columns: {df_hpi_model.columns.tolist()}")
print(f"\n  First row with full features (after lag fill):")
first_complete = df_hpi_model.dropna(subset=["hpi_lag8"]).iloc[0]
print(f"    quarter={first_complete['quarter']}  hpi={first_complete['hpi_primary']:.2f}  lag4={first_complete['hpi_lag4']:.2f}")


# ══════════════════════════════════════════════════════════════════════
# MODELING INPUT DATASET 2 — FX MODEL TRAINING DATA
# ══════════════════════════════════════════════════════════════════════
section("FX MODEL INPUT DATASET (Monthly)")

df_m = df_fx.copy().sort_values("date").reset_index(drop=True)

# Time features
df_m["t"]             = range(len(df_m))
df_m["month_num"]     = df_m["month"]

# Lag features
df_m["rate_lag1"]     = df_m["rate_close"].shift(1)
df_m["rate_lag3"]     = df_m["rate_close"].shift(3)
df_m["rate_lag6"]     = df_m["rate_close"].shift(6)
df_m["rate_lag12"]    = df_m["rate_close"].shift(12)
df_m["mom_lag1"]      = df_m["mom_change_pct"].shift(1)

# Rolling averages
df_m["roll3m"]        = df_m["rate_close"].rolling(3,  min_periods=2).mean()
df_m["roll6m"]        = df_m["rate_close"].rolling(6,  min_periods=3).mean()
df_m["roll12m"]       = df_m["rate_close"].rolling(12, min_periods=6).mean()

# Volatility
df_m["vol12m"]        = df_m["rate_close"].rolling(12, min_periods=6).std()

# Log transform for exponential model
df_m["log_rate"]      = np.log(df_m["rate_close"])

# Train / test split (train: Jan 2013 – Dec 2022, test: 2023+)
df_m["split"]         = np.where(df_m["year"] <= 2022, "train", "test")

fx_model_cols = [
    "date","year","month_num","t",
    "rate_close","log_rate",
    "rate_lag1","rate_lag3","rate_lag6","rate_lag12",
    "mom_lag1","mom_change_pct","yoy_change_pct",
    "roll3m","roll6m","roll12m","vol12m",
    "split"
]
df_fx_model = df_m[fx_model_cols].copy()
fx_out = os.path.join(PROC, "modeling", "fx_model_input.csv")
df_fx_model.to_csv(fx_out, index=False)

train_n_fx = (df_fx_model["split"] == "train").sum()
test_n_fx  = (df_fx_model["split"] == "test").sum()
print(f"\n  FX Model Input: {len(df_fx_model)} monthly rows")
print(f"  Train: {train_n_fx} rows (Jan 2013 – Dec 2022)")
print(f"  Test:  {test_n_fx} rows  (Jan 2023 – Dec 2025)")
print(f"  Saved: processed/modeling/fx_model_input.csv")
print(f"\n  Columns: {df_fx_model.columns.tolist()}")


# ══════════════════════════════════════════════════════════════════════
# GROUP 4 — RUNTIME AFFORDABILITY FORMULAS (documented)
# ══════════════════════════════════════════════════════════════════════
section("GROUP 4: AFFORDABILITY ENGINE FORMULAS (Verification)")

# These are computed at runtime per user. Verified here with example.
# Example user profile
ex = {
    "monthly_salary_aed":           15000,
    "monthly_expenses_aed":          8000,
    "current_savings_aed":          50000,
    "current_investment_aed":       20000,
    "monthly_investment_contrib":    2000,
    "investment_return_pct":         9.0,
    "property_size_sqft":            1200,
    "current_price_per_sqft_inr":    8500,
    "target_year":                   2031,
    "current_year":                  2025,
    "scenario":                      "expected",
}

# Scenario parameters
SCENARIOS = {
    "conservative": {"hpi": pre_covid_cagr/100,     "fx": 0.02,             "cpi": 0.075, "savings_r": 0.03, "invest_r": 0.06},
    "expected":     {"hpi": hpi_cagr_full/100,       "fx": fx_cagr_full/100, "cpi": 0.06,  "savings_r": 0.04, "invest_r": 0.09},
    "optimistic":   {"hpi": post_covid_cagr/100,     "fx": recent_3y_fx/100, "cpi": 0.04,  "savings_r": 0.05, "invest_r": 0.12},
}

def compute_affordability(profile, scenario_name):
    s = SCENARIOS[scenario_name]
    n = profile["target_year"] - profile["current_year"]

    # --- property_value (current)
    property_value = profile["property_size_sqft"] * profile["current_price_per_sqft_inr"]

    # --- future_property_value
    future_property_value = property_value * (1 + s["hpi"]) ** n

    # --- future_wealth (AED)
    monthly_savings = profile["monthly_salary_aed"] - profile["monthly_expenses_aed"]
    r_s  = s["savings_r"] / 12          # monthly savings rate
    r_i  = (s["invest_r"] if profile["monthly_investment_contrib"] > 0
            else s["invest_r"]) / 12    # monthly invest rate
    n_m  = n * 12                       # months

    # Compound savings (annuity + lump sum)
    fv_savings = (profile["current_savings_aed"] * (1 + r_s) ** n_m +
                  monthly_savings * (((1 + r_s) ** n_m - 1) / r_s))

    # Compound investment
    fv_invest  = (profile["current_investment_aed"] * (1 + r_i) ** n_m +
                  profile["monthly_investment_contrib"] * (((1 + r_i) ** n_m - 1) / r_i))

    future_wealth_aed = fv_savings + fv_invest

    # --- future_wealth_inr (convert at forecasted FX)
    current_rate = 23.78   # 2025 avg
    fx_forecast  = current_rate * (1 + s["fx"]) ** n
    future_wealth_inr = future_wealth_aed * fx_forecast

    # --- real_wealth_inr (deflate by cumulative CPI)
    cum_inflation = (1 + s["cpi"]) ** n
    real_wealth_inr = future_wealth_inr / cum_inflation

    # --- affordability_ratio
    affordability_ratio = real_wealth_inr / future_property_value

    # --- goal_gap_inr
    goal_gap_inr = future_property_value - real_wealth_inr

    # --- required_monthly_savings (to close gap over n years)
    if goal_gap_inr > 0:
        r_gap = s["savings_r"] / 12
        n_gap = n * 12
        required_extra_savings_inr = goal_gap_inr * r_gap / ((1 + r_gap) ** n_gap - 1)
        required_extra_savings_aed = required_extra_savings_inr / fx_forecast
    else:
        required_extra_savings_inr = 0
        required_extra_savings_aed = 0

    # --- monthly_savings_rate
    monthly_savings_rate = (monthly_savings / profile["monthly_salary_aed"]) * 100

    return {
        "scenario":                   scenario_name,
        "years_remaining":            n,
        "property_value_inr":         round(property_value, 0),
        "future_property_value_inr":  round(future_property_value, 0),
        "future_wealth_aed":          round(future_wealth_aed, 0),
        "fx_forecast_rate":           round(fx_forecast, 4),
        "future_wealth_inr_nominal":  round(future_wealth_inr, 0),
        "real_wealth_inr":            round(real_wealth_inr, 0),
        "affordability_ratio":        round(affordability_ratio, 4),
        "goal_gap_inr":               round(goal_gap_inr, 0),
        "required_extra_savings_inr": round(required_extra_savings_inr, 0),
        "required_extra_savings_aed": round(required_extra_savings_aed, 0),
        "monthly_savings_rate_pct":   round(monthly_savings_rate, 2),
        "monthly_savings_aed":        round(monthly_savings, 0),
    }

print(f"\n  Example Profile:")
print(f"    Salary: AED {ex['monthly_salary_aed']:,}/mo | Expenses: AED {ex['monthly_expenses_aed']:,}/mo")
print(f"    Savings: AED {ex['current_savings_aed']:,} | Investment: AED {ex['current_investment_aed']:,}")
print(f"    Property: {ex['property_size_sqft']} sqft @ Rs {ex['current_price_per_sqft_inr']:,}/sqft")
print(f"    Target Year: {ex['target_year']}  ({ex['target_year']-ex['current_year']} years)")
print()

all_results = {}
for scenario in ["conservative", "expected", "optimistic"]:
    result = compute_affordability(ex, scenario)
    all_results[scenario] = result
    ratio_label = (
        "Difficult"          if result["affordability_ratio"] < 0.5 else
        "Partially Affordable" if result["affordability_ratio"] < 1.0 else
        "Fully Affordable"   if result["affordability_ratio"] == 1.0 else
        "Comfortable"
    )
    print(f"  [{scenario.upper()}]")
    print(f"    Current Property Value:  Rs {result['property_value_inr']/100000:.2f}L")
    print(f"    Future Property Cost:    Rs {result['future_property_value_inr']/100000:.2f}L")
    print(f"    Future Real Wealth:      Rs {result['real_wealth_inr']/100000:.2f}L")
    print(f"    Affordability Ratio:     {result['affordability_ratio']:.3f}  → {ratio_label}")
    print(f"    Goal Gap:                Rs {result['goal_gap_inr']/100000:.2f}L")
    print(f"    Required Extra Savings:  Rs {result['required_extra_savings_inr']:,.0f}/mo")
    print(f"    Monthly Savings Rate:    {result['monthly_savings_rate_pct']}%")
    print()


# ══════════════════════════════════════════════════════════════════════
# GROUP 5 — STRESS SCORE (deterministic, verified)
# ══════════════════════════════════════════════════════════════════════
section("GROUP 5: STRESS SCORE ENGINE (Verification)")

def compute_stress_score(
    goal_gap_inr,
    future_property_cost,
    monthly_expenses_aed,
    monthly_salary_aed,
    real_wealth_inr,
    risk_tolerance="moderate"
):
    """
    Deterministic stress score 0-100. No ML.

    Components:
        goal_gap_ratio      (40%) : Normalized shortfall
        expense_ratio       (30%) : Monthly burn rate
        coverage_shortfall  (30%) : Inverted wealth coverage

    Returns: (score, breakdown_dict)
    """
    # Signal 1: Goal gap as fraction of target
    goal_gap_ratio = max(0.0, goal_gap_inr / future_property_cost) if future_property_cost > 0 else 0.0

    # Signal 2: Expense ratio (burn rate)
    expense_ratio = monthly_expenses_aed / monthly_salary_aed if monthly_salary_aed > 0 else 1.0
    expense_ratio = min(expense_ratio, 1.0)  # cap at 1

    # Signal 3: Coverage shortfall
    coverage = min(1.0, real_wealth_inr / future_property_cost) if future_property_cost > 0 else 0.0
    coverage_shortfall = 1.0 - coverage

    # Risk tolerance multiplier
    multiplier = {"conservative": 1.20, "moderate": 1.00, "aggressive": 0.85}[risk_tolerance]

    # Weighted raw score
    raw = (0.40 * goal_gap_ratio +
           0.30 * expense_ratio +
           0.30 * coverage_shortfall) * multiplier

    score = round(min(100.0, max(0.0, raw * 100)), 1)

    breakdown = {
        "goal_gap_ratio":       round(goal_gap_ratio,      4),
        "expense_ratio":        round(expense_ratio,        4),
        "coverage_shortfall":   round(coverage_shortfall,   4),
        "multiplier":           multiplier,
        "raw_weighted_score":   round(raw,                  4),
        "stress_score":         score,
        "primary_driver":       max(
            ("Goal Gap",       0.40 * goal_gap_ratio),
            ("Expense Burden", 0.30 * expense_ratio),
            ("Coverage",       0.30 * coverage_shortfall),
            key=lambda x: x[1]
        )[0]
    }
    return score, breakdown

print(f"\n  Stress Score Examples (from affordability results above):")
for scenario, res in all_results.items():
    score, bkdn = compute_stress_score(
        goal_gap_inr         = res["goal_gap_inr"],
        future_property_cost = res["future_property_value_inr"],
        monthly_expenses_aed = ex["monthly_expenses_aed"],
        monthly_salary_aed   = ex["monthly_salary_aed"],
        real_wealth_inr      = res["real_wealth_inr"],
        risk_tolerance       = "moderate"
    )
    stress_label = (
        "Safe"        if score <= 30 else
        "Comfortable" if score <= 60 else
        "Stretch"     if score <= 80 else
        "Risky"
    )
    print(f"\n  [{scenario.upper()}]  Score={score}  → {stress_label}")
    print(f"    Goal gap ratio:     {bkdn['goal_gap_ratio']:.3f}  (weight 40%)")
    print(f"    Expense ratio:      {bkdn['expense_ratio']:.3f}  (weight 30%)")
    print(f"    Coverage shortfall: {bkdn['coverage_shortfall']:.3f}  (weight 30%)")
    print(f"    Primary driver:     {bkdn['primary_driver']}")


# ══════════════════════════════════════════════════════════════════════
# GROUP 6 — KPI CATALOG VALIDATION
# ══════════════════════════════════════════════════════════════════════
section("GROUP 6: DASHBOARD KPI VALIDATION")

print(f"\n  Sample KPI Output (Expected Scenario, Example Profile):")
r = all_results["expected"]
print(f"    Current Property Value:   Rs {r['property_value_inr']/100000:.2f} Lakh")
print(f"    Future Property Value:    Rs {r['future_property_value_inr']/100000:.2f} Lakh")
print(f"    Future Wealth (real):     Rs {r['real_wealth_inr']/100000:.2f} Lakh")
print(f"    Goal Gap:                 Rs {r['goal_gap_inr']/100000:.2f} Lakh")
print(f"    Affordability Ratio:      {r['affordability_ratio']:.3f}")
print(f"    Required Extra Savings:   Rs {r['required_extra_savings_inr']:,.0f}/month  (AED {r['required_extra_savings_aed']:,.0f}/month)")
score_ex, _ = compute_stress_score(r["goal_gap_inr"], r["future_property_value_inr"],
                                    ex["monthly_expenses_aed"], ex["monthly_salary_aed"],
                                    r["real_wealth_inr"])
print(f"    Stress Score:             {score_ex}")
print(f"    Monthly Savings Rate:     {r['monthly_savings_rate_pct']}%")
print(f"    Years Remaining:          {r['years_remaining']}")


# ══════════════════════════════════════════════════════════════════════
# VALIDATION SUMMARY
# ══════════════════════════════════════════════════════════════════════
section("FEATURE ENGINEERING VALIDATION")

checks = []
checks.append(check(os.path.exists(os.path.join(PROC, "features_annual.csv")),
                    "features_annual.csv saved"))
checks.append(check(os.path.exists(hpi_out),
                    "hpi_model_input.csv saved"))
checks.append(check(os.path.exists(fx_out),
                    "fx_model_input.csv saved"))
checks.append(check("rolling_hpi_growth_3y" in feat.columns,
                    "rolling_hpi_growth_3y present"))
checks.append(check("rolling_hpi_growth_5y" in feat.columns,
                    "rolling_hpi_growth_5y present"))
checks.append(check("hpi_cagr_from_2013" in feat.columns,
                    "hpi_cagr_from_2013 present"))
checks.append(check("post_covid_hpi_growth" in feat.columns,
                    "post_covid_hpi_growth present"))
checks.append(check("rolling_fx_growth_3y" in feat.columns,
                    "rolling_fx_growth_3y present"))
checks.append(check("currency_volatility_index" in feat.columns,
                    "currency_volatility_index present"))
checks.append(check("rolling_inflation_3y" in feat.columns,
                    "rolling_inflation_3y present"))
checks.append(check("inflation_regime" in feat.columns,
                    "inflation_regime present"))
checks.append(check("scenario_expected_hpi" in feat.columns,
                    "Scenario constants embedded in features_annual"))
checks.append(check(all_results["expected"]["affordability_ratio"] > 0,
                    "Affordability ratio computed successfully"))
checks.append(check(score_ex >= 0 and score_ex <= 100,
                    f"Stress score in valid range [0-100]: {score_ex}"))

passed = sum(checks)
total  = len(checks)
print(f"\n  OVERALL: {passed}/{total} validation checks passed")
print()
print(SEP)
print("  Phase 4 Feature Engineering COMPLETE.")
print("  Awaiting approval to proceed to Phase 5 (Model Training).")
print(SEP)
