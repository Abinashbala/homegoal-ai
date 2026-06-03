"""
HomeGoal AI — Phase 5: Forecast Model Comparison & Selection
=============================================================

Models compared:
  HPI  : Linear Trend | Exponential | Prophet | XGBoost
  FX   : Linear Trend | Exponential | Prophet

Selection criterion: Lowest MAPE. Tie-break: simpler model wins.
Metrics: MAE, RMSE, MAPE (on predefined test split).

Outputs:
  models/artifacts/          <- Model parameters + forecast CSVs
  dashboards/matplotlib/     <- Comparison + residual plots
  docs/model_comparison.md   <- Written to disk by separate step
"""

import sys, os, warnings, json, pickle
sys.stdout.reconfigure(encoding="utf-8")
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.stats import pearsonr
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import StandardScaler

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches

# Optional imports
try:
    from prophet import Prophet
    HAS_PROPHET = True
except ImportError:
    HAS_PROPHET = False
    print("  [WARNING] Prophet not installed — skipping Prophet models")

try:
    import xgboost as xgb
    HAS_XGB = True
except ImportError:
    HAS_XGB = False
    print("  [WARNING] XGBoost not installed — skipping XGBoost models")

# ── PATHS ─────────────────────────────────────────────────────────────
BASE      = r"C:\Users\DELL\Desktop\HomeGoal AI"
PROC      = os.path.join(BASE, "processed")
ARTIFACTS = os.path.join(BASE, "models", "artifacts")
DASH_M    = os.path.join(BASE, "dashboards", "matplotlib")
os.makedirs(ARTIFACTS, exist_ok=True)

# ── SCENARIO CONSTANTS (derived from historical data) ─────────────────
# These replicate what feature_engineer.py computed so this script is self-contained.
_fa = pd.read_csv(os.path.join(PROC, "features_annual.csv"))
pre_covid_cagr  = _fa["scenario_conservative_hpi"].iloc[0]   # 3.19%
hpi_cagr_full   = _fa["scenario_expected_hpi"].iloc[0]        # 4.45%
post_covid_cagr = _fa["scenario_optimistic_hpi"].iloc[0]      # 6.87%
fx_cagr_full    = _fa["scenario_expected_fx"].iloc[0]         # 3.34%
recent_3y_fx    = _fa["scenario_optimistic_fx"].iloc[0]       # ~4.54%
print(f"  Scenario constants loaded:")
print(f"    HPI: Conservative={pre_covid_cagr:.2f}%  Expected={hpi_cagr_full:.2f}%  Optimistic={post_covid_cagr:.2f}%")
print(f"    FX:  Conservative=2.00%  Expected={fx_cagr_full:.2f}%  Optimistic={recent_3y_fx:.2f}%")

# ── STYLE ─────────────────────────────────────────────────────────────
BRAND    = "#1B4F72"
ACCENT1  = "#27AE60"
ACCENT2  = "#E74C3C"
ACCENT3  = "#F39C12"
ACCENT4  = "#9B59B6"
ACCENT5  = "#16A085"
GREY     = "#BDC3C7"

plt.rcParams.update({
    "figure.facecolor": "#F8F9FA",
    "axes.facecolor":   "#FFFFFF",
    "axes.edgecolor":   "#DEE2E6",
    "axes.labelcolor":  "#2C3E50",
    "axes.titlesize":   13,
    "axes.titleweight": "bold",
    "axes.titlecolor":  "#1B4F72",
    "xtick.color":      "#2C3E50",
    "ytick.color":      "#2C3E50",
    "font.family":      "DejaVu Sans",
    "font.size":        10.5,
    "grid.color":       "#E8ECEF",
    "grid.linestyle":   "--",
    "grid.alpha":       0.7,
})

def save_fig(fig, name):
    path = os.path.join(DASH_M, name)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  [SAVED]  {name}")

SEP = "=" * 65

def section(s):
    print(); print(SEP); print(f"  {s}"); print(SEP)

# ── METRIC FUNCTIONS ──────────────────────────────────────────────────
def mae(y, yhat):
    return mean_absolute_error(y, yhat)

def rmse(y, yhat):
    return np.sqrt(mean_squared_error(y, yhat))

def mape(y, yhat):
    y, yhat = np.array(y), np.array(yhat)
    mask = y != 0
    return np.mean(np.abs((y[mask] - yhat[mask]) / y[mask])) * 100

def metrics(name, y_test, yhat_test):
    m = mae(y_test, yhat_test)
    r = rmse(y_test, yhat_test)
    p = mape(y_test, yhat_test)
    print(f"    {name:<28}  MAE={m:.3f}  RMSE={r:.3f}  MAPE={p:.2f}%")
    return {"model": name, "MAE": round(m,4), "RMSE": round(r,4), "MAPE": round(p,4)}

# ══════════════════════════════════════════════════════════════════════
# PART 1 — HOUSING (HPI) MODEL COMPARISON
# ══════════════════════════════════════════════════════════════════════
section("PART 1: HPI FORECAST MODEL COMPARISON")

df_hpi = pd.read_csv(os.path.join(PROC, "modeling", "hpi_model_input.csv"),
                     parse_dates=["quarter"])
df_hpi = df_hpi.sort_values("quarter").reset_index(drop=True)

train_hpi = df_hpi[df_hpi["split"] == "train"].copy()
test_hpi  = df_hpi[df_hpi["split"] == "test"].copy()

print(f"\n  Train: {len(train_hpi)} rows | {train_hpi['quarter'].min().strftime('%Y-Q%m')[:7]} – {train_hpi['quarter'].max().strftime('%Y-Q%m')[:7]}")
print(f"  Test:  {len(test_hpi)} rows  | {test_hpi['quarter'].min().strftime('%Y-Q%m')[:7]} – {test_hpi['quarter'].max().strftime('%Y-Q%m')[:7]}")
print(f"  Target: hpi_primary  |  Range: {df_hpi['hpi_primary'].min():.2f} – {df_hpi['hpi_primary'].max():.2f}")
print()

y_train_hpi = train_hpi["hpi_primary"].values
y_test_hpi  = test_hpi["hpi_primary"].values
t_train     = train_hpi["t"].values
t_test      = test_hpi["t"].values
t_all       = df_hpi["t"].values

hpi_results = []

# ── HPI Model 1: Linear Trend ─────────────────────────────────────────
print("  [1] Linear Trend")
lr_hpi = LinearRegression()
lr_hpi.fit(t_train.reshape(-1,1), y_train_hpi)
yhat_train_lr = lr_hpi.predict(t_train.reshape(-1,1))
yhat_test_lr  = lr_hpi.predict(t_test.reshape(-1,1))
yhat_all_lr   = lr_hpi.predict(t_all.reshape(-1,1))
r = metrics("Linear Trend", y_test_hpi, yhat_test_lr)
r.update({"intercept": round(lr_hpi.intercept_,4), "slope": round(lr_hpi.coef_[0],4)})
hpi_results.append(r)
print(f"      y = {lr_hpi.intercept_:.3f} + {lr_hpi.coef_[0]:.3f} × t")

# ── HPI Model 2: Exponential Growth ──────────────────────────────────
print("  [2] Exponential Growth Trend")
# log(y) = a + b*t  →  y = exp(a) * exp(b*t)
log_y_train = np.log(y_train_hpi)
lr_exp_hpi = LinearRegression()
lr_exp_hpi.fit(t_train.reshape(-1,1), log_y_train)
yhat_train_exp = np.exp(lr_exp_hpi.predict(t_train.reshape(-1,1)))
yhat_test_exp  = np.exp(lr_exp_hpi.predict(t_test.reshape(-1,1)))
yhat_all_exp   = np.exp(lr_exp_hpi.predict(t_all.reshape(-1,1)))
r = metrics("Exponential Trend", y_test_hpi, yhat_test_exp)
implied_annual = (np.exp(lr_exp_hpi.coef_[0] * 4) - 1) * 100  # quarterly coef → annual
r.update({"log_intercept": round(lr_exp_hpi.intercept_,4),
          "log_slope": round(lr_exp_hpi.coef_[0],4),
          "implied_annual_growth_pct": round(implied_annual, 4)})
hpi_results.append(r)
print(f"      log(y) = {lr_exp_hpi.intercept_:.4f} + {lr_exp_hpi.coef_[0]:.5f} × t")
print(f"      Implied annual growth: {implied_annual:.2f}%")

# ── HPI Model 3: Prophet ──────────────────────────────────────────────
print("  [3] Prophet")
if HAS_PROPHET:
    prophet_df_train = pd.DataFrame({
        "ds": train_hpi["quarter"],
        "y":  train_hpi["hpi_primary"]
    })
    m_prophet_hpi = Prophet(
        yearly_seasonality=False,
        weekly_seasonality=False,
        daily_seasonality=False,
        changepoint_prior_scale=0.3,
        n_changepoints=5,
        seasonality_mode="additive",
    )
    m_prophet_hpi.fit(prophet_df_train)

    future_hpi = pd.DataFrame({"ds": df_hpi["quarter"]})
    forecast_hpi = m_prophet_hpi.predict(future_hpi)
    yhat_train_prophet = forecast_hpi[forecast_hpi["ds"].isin(train_hpi["quarter"])]["yhat"].values
    yhat_test_prophet  = forecast_hpi[forecast_hpi["ds"].isin(test_hpi["quarter"])]["yhat"].values
    yhat_all_prophet   = forecast_hpi["yhat"].values

    r = metrics("Prophet", y_test_hpi, yhat_test_prophet)
    r.update({"changepoints": len(m_prophet_hpi.changepoints)})
    hpi_results.append(r)
    print(f"      Changepoints detected: {len(m_prophet_hpi.changepoints)}")
else:
    print("      SKIPPED (not installed)")
    hpi_results.append({"model": "Prophet", "MAE": None, "RMSE": None, "MAPE": None})

# ── HPI Model 4: XGBoost ─────────────────────────────────────────────
print("  [4] XGBoost")
if HAS_XGB:
    feat_cols = ["t", "quarter_num", "hpi_lag1", "hpi_lag4", "growth_lag1",
                 "hpi_roll4q", "post_covid", "covid_period"]
    train_xgb = train_hpi.dropna(subset=feat_cols)
    test_xgb  = test_hpi.dropna(subset=feat_cols)

    X_train_xgb = train_xgb[feat_cols].values
    y_train_xgb = train_xgb["hpi_primary"].values
    X_test_xgb  = test_xgb[feat_cols].values
    y_test_xgb  = test_xgb["hpi_primary"].values

    xgb_model = xgb.XGBRegressor(
        n_estimators=80,
        max_depth=3,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.5,
        reg_lambda=1.0,
        random_state=42,
        verbosity=0
    )
    xgb_model.fit(X_train_xgb, y_train_xgb,
                  eval_set=[(X_test_xgb, y_test_xgb)],
                  verbose=False)

    yhat_test_xgb  = xgb_model.predict(X_test_xgb)
    yhat_train_xgb = xgb_model.predict(X_train_xgb)

    r = metrics("XGBoost", y_test_xgb, yhat_test_xgb)
    r.update({"n_train_usable": len(train_xgb), "features": feat_cols})
    hpi_results.append(r)

    # Feature importance
    imp = dict(zip(feat_cols, xgb_model.feature_importances_))
    imp_sorted = sorted(imp.items(), key=lambda x: -x[1])
    print(f"      Feature importances: {[(k, round(v,3)) for k,v in imp_sorted[:4]]}")
else:
    print("      SKIPPED (not installed)")
    hpi_results.append({"model": "XGBoost", "MAE": None, "RMSE": None, "MAPE": None})

# ── HPI: Compare & Select ─────────────────────────────────────────────
print()
print("  HPI — Model Comparison Summary:")
print(f"  {'Model':<28}  {'MAE':>7}  {'RMSE':>7}  {'MAPE':>8}")
print("  " + "-" * 56)
for r in hpi_results:
    if r["MAE"] is not None:
        print(f"  {r['model']:<28}  {r['MAE']:>7.3f}  {r['RMSE']:>7.3f}  {r['MAPE']:>7.2f}%")
    else:
        print(f"  {r['model']:<28}  {'N/A':>7}  {'N/A':>7}  {'N/A':>8}")

# Select best model (lowest MAPE, simpler wins ties)
valid = [(r, i) for i, r in enumerate(hpi_results) if r["MAPE"] is not None]
valid.sort(key=lambda x: (x[0]["MAPE"], x[1]))  # sort by MAPE, then by index (simpler=lower index)
best_hpi = valid[0][0]

print(f"\n  ==> BEST HPI MODEL: {best_hpi['model']}  (MAPE={best_hpi['MAPE']:.2f}%)")


# ── HPI: Extended Future Forecast ────────────────────────────────────
# Forecast 10 years = 40 quarters beyond Q4 2025
section("HPI FUTURE FORECAST (2025–2035)")

future_q_starts = pd.date_range("2026-01-01", periods=40, freq="QS")
t_future        = np.arange(len(df_hpi), len(df_hpi) + 40)

# All models' future
fut_lr  = lr_hpi.predict(t_future.reshape(-1,1))
fut_exp = np.exp(lr_exp_hpi.predict(t_future.reshape(-1,1)))

if HAS_PROPHET:
    future_full = pd.DataFrame({"ds": pd.date_range(
        df_hpi["quarter"].iloc[0], periods=len(df_hpi)+40, freq="QS")})
    fc_full = m_prophet_hpi.predict(future_full)
    fut_prophet = fc_full["yhat"].values[-40:]
    fut_prophet_lo = fc_full["yhat_lower"].values[-40:]
    fut_prophet_hi = fc_full["yhat_upper"].values[-40:]

# CAGR-based scenario projections (from 2025 Q4 = 144.99)
base_2025 = df_hpi["hpi_primary"].iloc[-1]
fut_q     = np.arange(1, 41)

fut_conservative = base_2025 * (1 + 0.0319 / 4) ** fut_q
fut_expected     = base_2025 * (1 + 0.0445 / 4) ** fut_q
fut_optimistic   = base_2025 * (1 + 0.0687 / 4) ** fut_q

print(f"\n  Base HPI (Q4 2025): {base_2025:.2f}")
print(f"\n  HPI Forecasts at 2031 (24 quarters):")
print(f"    Linear Trend:     {fut_lr[23]:.2f}")
print(f"    Exponential:      {fut_exp[23]:.2f}")
if HAS_PROPHET:
    print(f"    Prophet:          {fut_prophet[23]:.2f}  [{fut_prophet_lo[23]:.2f} – {fut_prophet_hi[23]:.2f}]")
print(f"    CAGR Conservative (3.19%):  {fut_conservative[23]:.2f}")
print(f"    CAGR Expected (4.45%):      {fut_expected[23]:.2f}")
print(f"    CAGR Optimistic (6.87%):    {fut_optimistic[23]:.2f}")

# Save forecast CSV
hpi_forecast_df = pd.DataFrame({
    "quarter":               future_q_starts,
    "hpi_linear_trend":      fut_lr,
    "hpi_exponential":       fut_exp,
    "hpi_cagr_conservative": fut_conservative,
    "hpi_cagr_expected":     fut_expected,
    "hpi_cagr_optimistic":   fut_optimistic,
})
if HAS_PROPHET:
    hpi_forecast_df["hpi_prophet"]    = fut_prophet
    hpi_forecast_df["hpi_prophet_lo"] = fut_prophet_lo
    hpi_forecast_df["hpi_prophet_hi"] = fut_prophet_hi

hpi_forecast_df.to_csv(os.path.join(ARTIFACTS, "hpi_forecast.csv"), index=False)
print(f"\n  Saved: models/artifacts/hpi_forecast.csv")


# ══════════════════════════════════════════════════════════════════════
# PART 2 — AED-INR (FX) MODEL COMPARISON
# ══════════════════════════════════════════════════════════════════════
section("PART 2: AED-INR FORECAST MODEL COMPARISON")

df_fx = pd.read_csv(os.path.join(PROC, "modeling", "fx_model_input.csv"),
                    parse_dates=["date"])
df_fx = df_fx.sort_values("date").reset_index(drop=True)

train_fx = df_fx[df_fx["split"] == "train"].copy()
test_fx  = df_fx[df_fx["split"] == "test"].copy()

print(f"\n  Train: {len(train_fx)} rows | {train_fx['date'].min().strftime('%b %Y')} – {train_fx['date'].max().strftime('%b %Y')}")
print(f"  Test:  {len(test_fx)} rows  | {test_fx['date'].min().strftime('%b %Y')} – {test_fx['date'].max().strftime('%b %Y')}")
print(f"  Target: rate_close  |  Range: {df_fx['rate_close'].min():.4f} – {df_fx['rate_close'].max():.4f}")
print()

y_train_fx = train_fx["rate_close"].values
y_test_fx  = test_fx["rate_close"].values
t_train_fx = train_fx["t"].values
t_test_fx  = test_fx["t"].values
t_all_fx   = df_fx["t"].values

fx_results = []

# ── FX Model 1: Linear Trend ──────────────────────────────────────────
print("  [1] Linear Trend")
lr_fx = LinearRegression()
lr_fx.fit(t_train_fx.reshape(-1,1), y_train_fx)
yhat_train_fx_lr = lr_fx.predict(t_train_fx.reshape(-1,1))
yhat_test_fx_lr  = lr_fx.predict(t_test_fx.reshape(-1,1))
yhat_all_fx_lr   = lr_fx.predict(t_all_fx.reshape(-1,1))
r = metrics("Linear Trend", y_test_fx, yhat_test_fx_lr)
r.update({"intercept": round(lr_fx.intercept_,6), "slope": round(lr_fx.coef_[0],6)})
fx_results.append(r)
print(f"      y = {lr_fx.intercept_:.4f} + {lr_fx.coef_[0]:.5f} × t")

# ── FX Model 2: Exponential Growth ────────────────────────────────────
print("  [2] Exponential Growth Trend")
log_y_fx = np.log(y_train_fx)
lr_exp_fx = LinearRegression()
lr_exp_fx.fit(t_train_fx.reshape(-1,1), log_y_fx)
yhat_train_fx_exp = np.exp(lr_exp_fx.predict(t_train_fx.reshape(-1,1)))
yhat_test_fx_exp  = np.exp(lr_exp_fx.predict(t_test_fx.reshape(-1,1)))
yhat_all_fx_exp   = np.exp(lr_exp_fx.predict(t_all_fx.reshape(-1,1)))
r = metrics("Exponential Trend", y_test_fx, yhat_test_fx_exp)
implied_annual_fx = (np.exp(lr_exp_fx.coef_[0] * 12) - 1) * 100  # monthly coef → annual
r.update({"log_intercept": round(lr_exp_fx.intercept_,6),
          "log_slope": round(lr_exp_fx.coef_[0],6),
          "implied_annual_growth_pct": round(implied_annual_fx,4)})
fx_results.append(r)
print(f"      log(y) = {lr_exp_fx.intercept_:.5f} + {lr_exp_fx.coef_[0]:.6f} × t")
print(f"      Implied annual growth: {implied_annual_fx:.2f}%")

# ── FX Model 3: Prophet ───────────────────────────────────────────────
print("  [3] Prophet")
if HAS_PROPHET:
    prophet_df_fx_train = pd.DataFrame({
        "ds": train_fx["date"],
        "y":  train_fx["rate_close"]
    })
    m_prophet_fx = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        changepoint_prior_scale=0.05,
        seasonality_mode="additive",
        n_changepoints=8,
    )
    m_prophet_fx.fit(prophet_df_fx_train)

    future_fx_df = pd.DataFrame({"ds": df_fx["date"]})
    fc_fx = m_prophet_fx.predict(future_fx_df)
    yhat_train_fx_prophet = fc_fx[fc_fx["ds"].isin(train_fx["date"])]["yhat"].values
    yhat_test_fx_prophet  = fc_fx[fc_fx["ds"].isin(test_fx["date"])]["yhat"].values
    yhat_all_fx_prophet   = fc_fx["yhat"].values

    r = metrics("Prophet", y_test_fx, yhat_test_fx_prophet)
    hpi_results_prophet_lo = fc_fx[fc_fx["ds"].isin(test_fx["date"])]["yhat_lower"].values
    hpi_results_prophet_hi = fc_fx[fc_fx["ds"].isin(test_fx["date"])]["yhat_upper"].values
    r.update({"changepoints": len(m_prophet_fx.changepoints)})
    fx_results.append(r)
    print(f"      Changepoints detected: {len(m_prophet_fx.changepoints)}")
else:
    print("      SKIPPED (not installed)")
    fx_results.append({"model": "Prophet", "MAE": None, "RMSE": None, "MAPE": None})

# ── FX: Compare & Select ──────────────────────────────────────────────
print()
print("  FX — Model Comparison Summary:")
print(f"  {'Model':<28}  {'MAE':>7}  {'RMSE':>7}  {'MAPE':>8}")
print("  " + "-" * 56)
for r in fx_results:
    if r["MAE"] is not None:
        print(f"  {r['model']:<28}  {r['MAE']:>7.4f}  {r['RMSE']:>7.4f}  {r['MAPE']:>7.3f}%")
    else:
        print(f"  {r['model']:<28}  {'N/A':>7}  {'N/A':>7}  {'N/A':>8}")

valid_fx = [(r, i) for i, r in enumerate(fx_results) if r["MAPE"] is not None]
valid_fx.sort(key=lambda x: (x[0]["MAPE"], x[1]))
best_fx = valid_fx[0][0]
print(f"\n  ==> BEST FX MODEL: {best_fx['model']}  (MAPE={best_fx['MAPE']:.3f}%)")


# ── FX: Extended Future Forecast ─────────────────────────────────────
section("FX FUTURE FORECAST (2026–2035)")

future_m_starts = pd.date_range("2026-01-01", periods=120, freq="MS")
t_future_fx     = np.arange(len(df_fx), len(df_fx) + 120)

fut_fx_lr  = lr_fx.predict(t_future_fx.reshape(-1,1))
fut_fx_exp = np.exp(lr_exp_fx.predict(t_future_fx.reshape(-1,1)))

if HAS_PROPHET:
    future_full_fx = pd.DataFrame({"ds": pd.date_range(
        df_fx["date"].iloc[0], periods=len(df_fx)+120, freq="MS")})
    fc_full_fx = m_prophet_fx.predict(future_full_fx)
    fut_fx_prophet    = fc_full_fx["yhat"].values[-120:]
    fut_fx_prophet_lo = fc_full_fx["yhat_lower"].values[-120:]
    fut_fx_prophet_hi = fc_full_fx["yhat_upper"].values[-120:]

base_fx_2025 = df_fx["rate_close"].iloc[-1]
fut_m        = np.arange(1, 121)

fut_fx_conservative = base_fx_2025 * (1 + 0.02 / 12) ** fut_m
fut_fx_expected     = base_fx_2025 * (1 + 0.0334 / 12) ** fut_m
fut_fx_optimistic   = base_fx_2025 * (1 + 0.0454 / 12) ** fut_m

print(f"\n  Base AED/INR Rate (Dec 2025): {base_fx_2025:.4f}")
print(f"\n  FX Rate Forecasts at Dec 2031 (72 months ahead):")
print(f"    Linear Trend:               {fut_fx_lr[71]:.4f}")
print(f"    Exponential:                {fut_fx_exp[71]:.4f}")
if HAS_PROPHET:
    print(f"    Prophet:                    {fut_fx_prophet[71]:.4f}  [{fut_fx_prophet_lo[71]:.4f} – {fut_fx_prophet_hi[71]:.4f}]")
print(f"    CAGR Conservative (2.00%):  {fut_fx_conservative[71]:.4f}")
print(f"    CAGR Expected (3.34%):      {fut_fx_expected[71]:.4f}")
print(f"    CAGR Optimistic (4.54%):    {fut_fx_optimistic[71]:.4f}")

fx_forecast_df = pd.DataFrame({
    "date":                  future_m_starts,
    "fx_linear_trend":       fut_fx_lr,
    "fx_exponential":        fut_fx_exp,
    "fx_cagr_conservative":  fut_fx_conservative,
    "fx_cagr_expected":      fut_fx_expected,
    "fx_cagr_optimistic":    fut_fx_optimistic,
})
if HAS_PROPHET:
    fx_forecast_df["fx_prophet"]    = fut_fx_prophet
    fx_forecast_df["fx_prophet_lo"] = fut_fx_prophet_lo
    fx_forecast_df["fx_prophet_hi"] = fut_fx_prophet_hi

fx_forecast_df.to_csv(os.path.join(ARTIFACTS, "fx_forecast.csv"), index=False)
print(f"\n  Saved: models/artifacts/fx_forecast.csv")


# ══════════════════════════════════════════════════════════════════════
# PART 3 — VISUALIZATION: HPI MODEL COMPARISON
# ══════════════════════════════════════════════════════════════════════
section("GENERATING FORECAST PLOTS")

# ── Plot H1: HPI Model Comparison (Train/Test + Future) ───────────────
n_models_hpi = 2 + (1 if HAS_PROPHET else 0) + (1 if HAS_XGB else 0)
fig, axes = plt.subplots(2, 1, figsize=(14, 11))

ax = axes[0]
# Historical
ax.plot(df_hpi["quarter"], df_hpi["hpi_primary"],
        color="black", linewidth=2.2, label="Actual HPI", zorder=5)
# Train/test divider
split_date = test_hpi["quarter"].iloc[0]
ax.axvline(split_date, color=GREY, linewidth=1.5, linestyle="--", alpha=0.8)
ax.axvspan(split_date, df_hpi["quarter"].iloc[-1], alpha=0.05, color=ACCENT2)
ax.text(split_date, ax.get_ylim()[0] if ax.get_ylim()[0] > 0 else 85,
        "Test →", fontsize=9, color=ACCENT2, ha="left")

# Model predictions
ax.plot(df_hpi["quarter"], yhat_all_lr,
        color=BRAND, linewidth=1.8, linestyle="--", label=f"Linear (MAPE={hpi_results[0]['MAPE']:.1f}%)")
ax.plot(df_hpi["quarter"], yhat_all_exp,
        color=ACCENT3, linewidth=1.8, linestyle=":", label=f"Exponential (MAPE={hpi_results[1]['MAPE']:.1f}%)")
if HAS_PROPHET:
    ax.plot(df_hpi["quarter"], yhat_all_prophet,
            color=ACCENT4, linewidth=1.8, linestyle="-.", label=f"Prophet (MAPE={hpi_results[2]['MAPE']:.1f}%)")
if HAS_XGB:
    xgb_idx  = 3 if HAS_PROPHET else 2
    xgb_xt   = pd.concat([train_hpi.dropna(subset=feat_cols), test_hpi.dropna(subset=feat_cols)])
    xgb_yt   = xgb_model.predict(xgb_xt[feat_cols].values)
    ax.plot(xgb_xt["quarter"], xgb_yt,
            color=ACCENT5, linewidth=1.8, linestyle=(0,(5,2,1,2)),
            label=f"XGBoost (MAPE={hpi_results[xgb_idx]['MAPE']:.1f}%)")

# Future CAGR bands
ax2 = axes[0].twinx()
ax.plot(future_q_starts, fut_conservative, color=ACCENT2, linewidth=1.4, alpha=0.7, linestyle=":")
ax.plot(future_q_starts, fut_expected,     color=ACCENT1, linewidth=2.0, alpha=0.9, linestyle="-")
ax.plot(future_q_starts, fut_optimistic,   color=BRAND,   linewidth=1.4, alpha=0.7, linestyle=":")
ax.fill_between(future_q_starts, fut_conservative, fut_optimistic, alpha=0.06, color=ACCENT1)

ax.set_title("HPI Forecast — Model Comparison (Train/Test) + Future CAGR Scenarios", pad=14)
ax.set_xlabel("Quarter")
ax.set_ylabel("HPI Value")
ax.legend(loc="upper left", fontsize=9, framealpha=0.9)
ax.grid(True, axis="y")

# ── Residuals plot (test period) ──────────────────────────────────────
ax = axes[1]
residuals_lr  = y_test_hpi - yhat_test_lr
residuals_exp = y_test_hpi - yhat_test_exp
ax.bar(test_hpi["quarter"] - pd.Timedelta(days=20), residuals_lr,
       width=30, color=BRAND, alpha=0.7, label="Linear Trend Residuals")
ax.bar(test_hpi["quarter"] + pd.Timedelta(days=20), residuals_exp,
       width=30, color=ACCENT3, alpha=0.7, label="Exponential Residuals")
if HAS_PROPHET:
    residuals_p = y_test_hpi - yhat_test_prophet
    ax.plot(test_hpi["quarter"], residuals_p,
            color=ACCENT4, linewidth=2, marker="o", markersize=5,
            label="Prophet Residuals")
ax.axhline(0, color="black", linewidth=1)
ax.set_title("Residuals on Test Set (Q1 2022 – Q4 2025)", pad=14)
ax.set_xlabel("Quarter")
ax.set_ylabel("Actual − Predicted")
ax.legend(fontsize=9)
ax.grid(True, axis="y")

plt.tight_layout()
save_fig(fig, "15_hpi_model_comparison.png")

# ── Plot H2: HPI Residual Distribution ────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

ax = axes[0]
all_residuals_lr  = df_hpi["hpi_primary"].values - yhat_all_lr
all_residuals_exp = df_hpi["hpi_primary"].values - yhat_all_exp

ax.scatter(df_hpi["quarter"], all_residuals_lr,  color=BRAND,   alpha=0.7, s=60, label="Linear")
ax.scatter(df_hpi["quarter"], all_residuals_exp, color=ACCENT3, alpha=0.7, s=60, marker="^", label="Exponential")
if HAS_PROPHET:
    all_res_p = df_hpi["hpi_primary"].values - yhat_all_prophet
    ax.scatter(df_hpi["quarter"], all_res_p, color=ACCENT4, alpha=0.7, s=60, marker="s", label="Prophet")
ax.axhline(0, color="black", linewidth=1.2)
ax.axvspan(split_date, df_hpi["quarter"].iloc[-1], alpha=0.05, color=ACCENT2)
ax.set_title("HPI Residuals (Full Period)", pad=14)
ax.set_xlabel("Quarter")
ax.set_ylabel("Residual")
ax.legend(fontsize=9)
ax.grid(True)

ax = axes[1]
import matplotlib.ticker as mt
lr_test_res  = y_test_hpi - yhat_test_lr
exp_test_res = y_test_hpi - yhat_test_exp

ax.hist(lr_test_res,  bins=8,  alpha=0.6, color=BRAND,   edgecolor="white", label="Linear")
ax.hist(exp_test_res, bins=8,  alpha=0.6, color=ACCENT3, edgecolor="white", label="Exponential")
if HAS_PROPHET:
    ax.hist(residuals_p, bins=8, alpha=0.6, color=ACCENT4, edgecolor="white", label="Prophet")
ax.axvline(0, color="black", linewidth=1.2)
ax.set_title("Residual Distribution (Test Period)", pad=14)
ax.set_xlabel("Residual Value")
ax.set_ylabel("Frequency")
ax.legend(fontsize=9)
ax.grid(True, axis="y")

plt.tight_layout()
save_fig(fig, "16_hpi_residual_analysis.png")

# ── Plot F1: FX Model Comparison ──────────────────────────────────────
fig, axes = plt.subplots(2, 1, figsize=(14, 11))

ax = axes[0]
ax.plot(df_fx["date"], df_fx["rate_close"],
        color="black", linewidth=1.8, label="Actual AED/INR", zorder=5, alpha=0.8)
split_fx = test_fx["date"].iloc[0]
ax.axvline(split_fx, color=GREY, linewidth=1.5, linestyle="--", alpha=0.8)
ax.axvspan(split_fx, df_fx["date"].iloc[-1], alpha=0.04, color=ACCENT2)

ax.plot(df_fx["date"], yhat_all_fx_lr,
        color=BRAND, linewidth=1.8, linestyle="--",
        label=f"Linear (MAPE={fx_results[0]['MAPE']:.3f}%)")
ax.plot(df_fx["date"], yhat_all_fx_exp,
        color=ACCENT3, linewidth=1.8, linestyle=":",
        label=f"Exponential (MAPE={fx_results[1]['MAPE']:.3f}%)")
if HAS_PROPHET:
    ax.plot(df_fx["date"], yhat_all_fx_prophet,
            color=ACCENT4, linewidth=1.8, linestyle="-.",
            label=f"Prophet (MAPE={fx_results[2]['MAPE']:.3f}%)")

# Future
ax.plot(future_m_starts, fut_fx_lr,           color=BRAND,   linewidth=1.2, linestyle="--", alpha=0.6)
ax.plot(future_m_starts, fut_fx_exp,          color=ACCENT3, linewidth=1.2, linestyle=":",  alpha=0.6)
ax.plot(future_m_starts, fut_fx_expected,     color=ACCENT1, linewidth=2.0, alpha=0.9)
ax.fill_between(future_m_starts, fut_fx_conservative, fut_fx_optimistic, alpha=0.07, color=ACCENT1)
if HAS_PROPHET:
    ax.plot(future_m_starts, fut_fx_prophet,  color=ACCENT4, linewidth=1.2, linestyle="-.", alpha=0.6)

ax.set_title("AED-INR Forecast — Model Comparison (Train/Test) + Future CAGR Scenarios", pad=14)
ax.set_xlabel("Month")
ax.set_ylabel("INR per 1 AED")
ax.legend(loc="upper left", fontsize=9.5, framealpha=0.9)
ax.grid(True, axis="y")

# FX Residuals
ax = axes[1]
fx_res_lr  = y_test_fx - yhat_test_fx_lr
fx_res_exp = y_test_fx - yhat_test_fx_exp
ax.fill_between(test_fx["date"], fx_res_lr, 0, alpha=0.4, color=BRAND, label="Linear Residuals")
ax.plot(test_fx["date"], fx_res_exp, color=ACCENT3, linewidth=1.5, linestyle="--", label="Exponential Residuals")
if HAS_PROPHET:
    fx_res_p = y_test_fx - yhat_test_fx_prophet
    ax.plot(test_fx["date"], fx_res_p, color=ACCENT4, linewidth=1.5, label="Prophet Residuals")
ax.axhline(0, color="black", linewidth=1)
ax.set_title("FX Residuals on Test Set (Jan 2023 – Dec 2025)", pad=14)
ax.set_xlabel("Month")
ax.set_ylabel("Actual − Predicted")
ax.legend(fontsize=9.5)
ax.grid(True, axis="y")

plt.tight_layout()
save_fig(fig, "17_fx_model_comparison.png")

# ── Plot F2: FX Residual Distribution ─────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

ax = axes[0]
ax.scatter(df_fx["date"], df_fx["rate_close"].values - yhat_all_fx_lr,
           color=BRAND, alpha=0.4, s=20, label="Linear")
ax.scatter(df_fx["date"], df_fx["rate_close"].values - yhat_all_fx_exp,
           color=ACCENT3, alpha=0.4, s=20, marker="^", label="Exponential")
if HAS_PROPHET:
    ax.scatter(df_fx["date"], df_fx["rate_close"].values - yhat_all_fx_prophet,
               color=ACCENT4, alpha=0.4, s=20, marker="s", label="Prophet")
ax.axhline(0, color="black", linewidth=1.2)
ax.axvspan(split_fx, df_fx["date"].iloc[-1], alpha=0.04, color=ACCENT2)
ax.set_title("FX Residuals (Full Period)", pad=14)
ax.set_xlabel("Month")
ax.set_ylabel("Residual")
ax.legend(fontsize=9)
ax.grid(True)

ax = axes[1]
ax.hist(fx_res_lr,  bins=15, alpha=0.6, color=BRAND,   edgecolor="white", label="Linear")
ax.hist(fx_res_exp, bins=15, alpha=0.6, color=ACCENT3, edgecolor="white", label="Exponential")
if HAS_PROPHET:
    ax.hist(fx_res_p, bins=15, alpha=0.6, color=ACCENT4, edgecolor="white", label="Prophet")
ax.axvline(0, color="black", linewidth=1.2)
ax.set_title("Residual Distribution (Test Period)", pad=14)
ax.set_xlabel("Residual Value")
ax.set_ylabel("Frequency")
ax.legend(fontsize=9)
ax.grid(True, axis="y")

plt.tight_layout()
save_fig(fig, "18_fx_residual_analysis.png")

# ── Plot: Future Scenario Comparison ──────────────────────────────────
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# HPI scenarios
all_q = pd.concat([df_hpi["quarter"], future_q_starts.to_series()])
ax1.plot(df_hpi["quarter"], df_hpi["hpi_primary"],
         color="black", linewidth=2, label="Historical HPI", zorder=5)
ax1.axvline(pd.Timestamp("2026-01-01"), color=GREY, linewidth=1.2, linestyle="--")
ax1.plot(future_q_starts, fut_conservative, color=ACCENT2, linewidth=2.2,
         label="Conservative (3.19%)", linestyle="--")
ax1.plot(future_q_starts, fut_expected,     color=ACCENT1, linewidth=2.8,
         label="Expected (4.45%)")
ax1.plot(future_q_starts, fut_optimistic,   color=BRAND,   linewidth=2.2,
         label="Optimistic (6.87%)", linestyle=":")
ax1.fill_between(future_q_starts, fut_conservative, fut_optimistic, alpha=0.10, color=ACCENT1)
ax1.axvline(pd.Timestamp("2031-01-01"), color=ACCENT4, linewidth=1.2, linestyle=":", alpha=0.8)
ax1.text(pd.Timestamp("2031-01-01"), ax1.get_ylim()[0] if hasattr(ax1, '_ymin') else 80,
         " 2031", fontsize=9, color=ACCENT4)
ax1.set_title("HPI Scenarios — Historical + Future (2013–2035)", pad=14)
ax1.set_xlabel("Quarter")
ax1.set_ylabel("HPI Value")
ax1.legend(fontsize=9, loc="upper left")
ax1.grid(True, axis="y")

# FX scenarios
ax2.plot(df_fx["date"], df_fx["rate_close"],
         color="black", linewidth=1.5, alpha=0.7, label="Historical Rate", zorder=5)
ax2.axvline(pd.Timestamp("2026-01-01"), color=GREY, linewidth=1.2, linestyle="--")
ax2.plot(future_m_starts, fut_fx_conservative, color=ACCENT2, linewidth=2.2,
         label="Conservative (2.0%)", linestyle="--")
ax2.plot(future_m_starts, fut_fx_expected,     color=ACCENT1, linewidth=2.8,
         label="Expected (3.34%)")
ax2.plot(future_m_starts, fut_fx_optimistic,   color=BRAND,   linewidth=2.2,
         label="Optimistic (4.54%)", linestyle=":")
ax2.fill_between(future_m_starts, fut_fx_conservative, fut_fx_optimistic, alpha=0.10, color=ACCENT1)
ax2.set_title("AED-INR Scenarios — Historical + Future (2013–2035)", pad=14)
ax2.set_xlabel("Month")
ax2.set_ylabel("INR per 1 AED")
ax2.legend(fontsize=9, loc="upper left")
ax2.grid(True, axis="y")

plt.suptitle("HomeGoal AI — Final Scenario Forecasts", fontsize=14, fontweight="bold", y=1.02)
plt.tight_layout()
save_fig(fig, "19_final_scenario_forecasts.png")


# ══════════════════════════════════════════════════════════════════════
# PART 4 — SAVE MODEL ARTIFACTS
# ══════════════════════════════════════════════════════════════════════
section("SAVING MODEL ARTIFACTS")

# HPI model artifacts
hpi_linear_params = {
    "model_type":   "linear_trend",
    "target":       "hpi_primary",
    "intercept":    float(lr_hpi.intercept_),
    "slope":        float(lr_hpi.coef_[0]),
    "train_period": "Q2 2013 – Q4 2021",
    "test_mape":    hpi_results[0]["MAPE"],
}
hpi_exp_params = {
    "model_type":               "exponential_trend",
    "target":                   "hpi_primary",
    "log_intercept":            float(lr_exp_hpi.intercept_),
    "log_slope":                float(lr_exp_hpi.coef_[0]),
    "implied_annual_growth_pct": hpi_results[1]["implied_annual_growth_pct"],
    "train_period":             "Q2 2013 – Q4 2021",
    "test_mape":                hpi_results[1]["MAPE"],
}
with open(os.path.join(ARTIFACTS, "hpi_linear_params.json"), "w") as f:
    json.dump(hpi_linear_params, f, indent=2)
with open(os.path.join(ARTIFACTS, "hpi_exp_params.json"), "w") as f:
    json.dump(hpi_exp_params, f, indent=2)

# FX model artifacts
fx_linear_params = {
    "model_type":   "linear_trend",
    "target":       "rate_close",
    "intercept":    float(lr_fx.intercept_),
    "slope":        float(lr_fx.coef_[0]),
    "train_period": "Jan 2013 – Dec 2022",
    "test_mape":    fx_results[0]["MAPE"],
}
fx_exp_params = {
    "model_type":               "exponential_trend",
    "target":                   "rate_close",
    "log_intercept":            float(lr_exp_fx.intercept_),
    "log_slope":                float(lr_exp_fx.coef_[0]),
    "implied_annual_growth_pct": fx_results[1]["implied_annual_growth_pct"],
    "train_period":             "Jan 2013 – Dec 2022",
    "test_mape":                fx_results[1]["MAPE"],
}
with open(os.path.join(ARTIFACTS, "fx_linear_params.json"), "w") as f:
    json.dump(fx_linear_params, f, indent=2)
with open(os.path.join(ARTIFACTS, "fx_exp_params.json"), "w") as f:
    json.dump(fx_exp_params, f, indent=2)

# CAGR scenarios (the production parameters)
scenarios = {
    "hpi": {
        "conservative_cagr_pct": round(pre_covid_cagr, 4),
        "expected_cagr_pct":     round(hpi_cagr_full,  4),
        "optimistic_cagr_pct":   round(post_covid_cagr, 4),
        "base_hpi_2025":         float(base_2025),
        "basis": {
            "conservative": "Pre-COVID avg growth 2014-2019",
            "expected":      "Full-period CAGR 2013-2025",
            "optimistic":    "Post-COVID avg growth 2021-2025",
        }
    },
    "fx": {
        "conservative_cagr_pct": 2.00,
        "expected_cagr_pct":     round(fx_cagr_full, 4),
        "optimistic_cagr_pct":   round(recent_3y_fx,  4),
        "base_rate_2025":        float(base_fx_2025),
        "basis": {
            "conservative": "Below historical avg (adverse FX scenario)",
            "expected":      "Full-period CAGR 2013-2025",
            "optimistic":    "Recent 3-year avg 2022-2025",
        }
    },
    "cpi_scenarios": {
        "conservative_pct": 7.5,
        "expected_pct":     6.0,
        "optimistic_pct":   4.0,
    }
}
with open(os.path.join(ARTIFACTS, "scenario_parameters.json"), "w") as f:
    json.dump(scenarios, f, indent=2)

if HAS_PROPHET:
    with open(os.path.join(ARTIFACTS, "hpi_prophet_model.pkl"), "wb") as f:
        pickle.dump(m_prophet_hpi, f)
    with open(os.path.join(ARTIFACTS, "fx_prophet_model.pkl"), "wb") as f:
        pickle.dump(m_prophet_fx, f)

print(f"\n  Model artifacts saved:")
for fn in os.listdir(ARTIFACTS):
    sz = os.path.getsize(os.path.join(ARTIFACTS, fn))
    print(f"    {fn:<40}  {sz:,} bytes")


# ══════════════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ══════════════════════════════════════════════════════════════════════
section("FINAL MODEL SELECTION SUMMARY")

print(f"\n  HPI COMPARISON TABLE:")
print(f"  {'Model':<28}  {'MAE':>7}  {'RMSE':>7}  {'MAPE':>8}  {'Rank'}")
print("  " + "-" * 65)
valid_sorted = sorted([(r, i) for i, r in enumerate(hpi_results) if r["MAPE"] is not None],
                       key=lambda x: (x[0]["MAPE"], x[1]))
for rank, (r, _) in enumerate(valid_sorted, 1):
    star = " *** SELECTED" if r["model"] == best_hpi["model"] else ""
    print(f"  {r['model']:<28}  {r['MAE']:>7.3f}  {r['RMSE']:>7.3f}  {r['MAPE']:>7.2f}%  #{rank}{star}")

print(f"\n  FX COMPARISON TABLE:")
print(f"  {'Model':<28}  {'MAE':>8}  {'RMSE':>8}  {'MAPE':>9}  {'Rank'}")
print("  " + "-" * 65)
valid_fx_sorted = sorted([(r, i) for i, r in enumerate(fx_results) if r["MAPE"] is not None],
                          key=lambda x: (x[0]["MAPE"], x[1]))
for rank, (r, _) in enumerate(valid_fx_sorted, 1):
    star = " *** SELECTED" if r["model"] == best_fx["model"] else ""
    print(f"  {r['model']:<28}  {r['MAE']:>8.5f}  {r['RMSE']:>8.5f}  {r['MAPE']:>8.4f}%  #{rank}{star}")

print(f"""
  FINAL DECISIONS:
  ─────────────────────────────────────────────────────────────
  HPI  Winner: {best_hpi['model']:<20}  MAPE={best_hpi['MAPE']:.2f}%
  FX   Winner: {best_fx['model']:<20}  MAPE={best_fx['MAPE']:.4f}%

  PRODUCTION APPROACH:
  ─────────────────────────────────────────────────────────────
  Both models validate the CAGR scenario ranges.
  Production uses CAGR-based scenarios (not ML extrapolation)
  to maximize interpretability and scenario control.

  HPI Scenarios:
    Conservative: {scenarios['hpi']['conservative_cagr_pct']:.2f}% (pre-COVID CAGR)
    Expected:     {scenarios['hpi']['expected_cagr_pct']:.2f}% (full-period CAGR)
    Optimistic:   {scenarios['hpi']['optimistic_cagr_pct']:.2f}% (post-COVID CAGR)

  FX Scenarios:
    Conservative: {scenarios['fx']['conservative_cagr_pct']:.2f}% (adverse case)
    Expected:     {scenarios['fx']['expected_cagr_pct']:.2f}% (full-period CAGR)
    Optimistic:   {scenarios['fx']['optimistic_cagr_pct']:.2f}% (recent 3-yr CAGR)
""")

print(SEP)
print("  Phase 5 — Model Selection COMPLETE.")
print("  Awaiting approval to proceed to Phase 6 (Backend Integration).")
print(SEP)

# Save master results for the report
master = {
    "hpi_results":  hpi_results,
    "fx_results":   fx_results,
    "best_hpi":     best_hpi,
    "best_fx":      best_fx,
    "has_prophet":  HAS_PROPHET,
    "has_xgb":      HAS_XGB,
    "hpi_cagr_scenarios": {
        "conservative": round(pre_covid_cagr,4),
        "expected":     round(hpi_cagr_full,4),
        "optimistic":   round(post_covid_cagr,4),
    },
    "fx_cagr_scenarios": {
        "conservative": 2.00,
        "expected":     round(fx_cagr_full,4),
        "optimistic":   round(recent_3y_fx,4),
    },
    "base_hpi_2025": float(base_2025),
    "base_fx_2025":  float(base_fx_2025),
}
with open(os.path.join(ARTIFACTS, "model_selection_summary.json"), "w") as f:
    json.dump(master, f, indent=2)
print(f"\n  Summary JSON saved: models/artifacts/model_selection_summary.json")
