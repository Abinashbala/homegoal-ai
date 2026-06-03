"""
HomeGoal AI — Phase 3: Exploratory Data Analysis
=================================================
Produces all charts, statistics, and business insights.

Outputs:
    dashboards/matplotlib/  -> Static PNGs (Matplotlib + Seaborn)
    dashboards/plotly/      -> Interactive HTMLs (Plotly)
    docs/eda_statistics.txt -> All printed stats (captured separately)

Author: HomeGoal AI Analytics Pipeline
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")

import os
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches

import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ─── PATHS ────────────────────────────────────────────────────────────
BASE   = r"C:\Users\DELL\Desktop\HomeGoal AI"
PROC   = os.path.join(BASE, "processed")
DASH_M = os.path.join(BASE, "dashboards", "matplotlib")
DASH_P = os.path.join(BASE, "dashboards", "plotly")
os.makedirs(DASH_M, exist_ok=True)
os.makedirs(DASH_P, exist_ok=True)

# ─── LOAD DATA ────────────────────────────────────────────────────────
df        = pd.read_csv(os.path.join(PROC, "master_annual.csv"))
df_hpi_q  = pd.read_csv(os.path.join(PROC, "nhb_hpi",      "nhb_hpi_clean.csv"),  parse_dates=["quarter"])
df_hpi_a  = pd.read_csv(os.path.join(PROC, "nhb_hpi",      "nhb_hpi_annual.csv"))
df_cpi    = pd.read_csv(os.path.join(PROC, "inflation",     "india_cpi_clean.csv"))
df_fx     = pd.read_csv(os.path.join(PROC, "exchange_rate", "aed_inr_clean.csv"),  parse_dates=["date"])
df_fx_a   = pd.read_csv(os.path.join(PROC, "exchange_rate", "aed_inr_annual.csv"))

# Working copies — drop 2013 for growth charts (first-row NaN)
df_growth = df.dropna(subset=["hpi_growth_pct", "fx_growth_pct"]).copy()
df_model  = df[df["year"] <= 2024].dropna(subset=["cpi_pct"]).copy()
# For cross analysis: years where ALL three series are complete (2014-2024)
df_cross = df[
    (df["year"] >= 2014) &
    (df["year"] <= 2024) &
    df["hpi_growth_pct"].notna() &
    df["cpi_pct"].notna() &
    df["fx_growth_pct"].notna()
].copy()


# ─── STYLE ────────────────────────────────────────────────────────────
BRAND   = "#1B4F72"        # Deep navy
ACCENT1 = "#2ECC71"        # Green
ACCENT2 = "#E74C3C"        # Red
ACCENT3 = "#F39C12"        # Amber
ACCENT4 = "#9B59B6"        # Purple
GREY    = "#BDC3C7"

plt.rcParams.update({
    "figure.facecolor": "#F8F9FA",
    "axes.facecolor":   "#FFFFFF",
    "axes.edgecolor":   "#DEE2E6",
    "axes.labelcolor":  "#2C3E50",
    "axes.titlesize":   14,
    "axes.titleweight": "bold",
    "axes.titlecolor":  "#1B4F72",
    "xtick.color":      "#2C3E50",
    "ytick.color":      "#2C3E50",
    "font.family":      "DejaVu Sans",
    "font.size":        11,
    "grid.color":       "#E8ECEF",
    "grid.linestyle":   "--",
    "grid.alpha":       0.7,
})

SEP = "=" * 65

def save_fig(fig, name):
    path = os.path.join(DASH_M, name)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  [SAVED]  dashboards/matplotlib/{name}")

def save_plotly(fig, name):
    path = os.path.join(DASH_P, name)
    html_str = fig.to_html(include_plotlyjs="cdn")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html_str)
    print(f"  [SAVED]  dashboards/plotly/{name}")



# ═══════════════════════════════════════════════════════════════════════
# SECTION 1 — HOUSING (NHB HPI) ANALYSIS
# ═══════════════════════════════════════════════════════════════════════
print()
print(SEP)
print("  SECTION 1: HOUSING (NHB HPI) ANALYSIS")
print(SEP)

# ── STATS ──────────────────────────────────────────────────────────────
hpi_start   = df["hpi_index"].iloc[0]
hpi_end     = df["hpi_index"].iloc[-1]
n_years     = len(df) - 1
hpi_cagr    = ((hpi_end / hpi_start) ** (1/n_years) - 1) * 100
hpi_total   = (hpi_end / hpi_start - 1) * 100

growth_valid = df_growth["hpi_growth_pct"]
best_hpi_yr  = int(df_growth.loc[growth_valid.idxmax(), "year"])
best_hpi_val = growth_valid.max()
worst_hpi_yr = int(df_growth.loc[growth_valid.idxmin(), "year"])
worst_hpi_val = growth_valid.min()
hpi_avg_growth = growth_valid.mean()
hpi_std_growth = growth_valid.std()

pre_covid_growth  = df_growth[df_growth["year"] <= 2019]["hpi_growth_pct"].mean()
post_covid_growth = df_growth[df_growth["year"] >= 2021]["hpi_growth_pct"].mean()

print(f"\n  HPI Start (2013): {hpi_start:.2f}")
print(f"  HPI End   (2025): {hpi_end:.2f}")
print(f"  Total Appreciation: {hpi_total:.1f}%")
print(f"  Full-Period CAGR:   {hpi_cagr:.2f}% per year")
print(f"  Best Year:  {best_hpi_yr}  ({best_hpi_val:.2f}%)")
print(f"  Worst Year: {worst_hpi_yr} ({worst_hpi_val:.2f}%)")
print(f"  Avg Annual Growth:  {hpi_avg_growth:.2f}%")
print(f"  Growth Std Dev:     {hpi_std_growth:.2f}% (volatility)")
print(f"  Pre-COVID Avg (2014-2019):  {pre_covid_growth:.2f}%")
print(f"  Post-COVID Avg (2021-2025): {post_covid_growth:.2f}%")

# ── CHART 1: Annual HPI Trend (Matplotlib) ────────────────────────────
fig, ax = plt.subplots(figsize=(13, 5.5))
ax.fill_between(df["year"], df["hpi_index"], alpha=0.12, color=BRAND)
ax.plot(df["year"], df["hpi_index"], color=BRAND, linewidth=2.5, marker="o",
        markersize=7, markerfacecolor="white", markeredgewidth=2, label="HPI (Primary)")
ax.plot(df["year"], df["hpi_assessment"], color=ACCENT3, linewidth=1.6,
        linestyle="--", marker="s", markersize=5, alpha=0.8, label="HPI (Assessment only)")
ax.axvspan(2020, 2021, alpha=0.08, color=ACCENT2, label="COVID period")
ax.axhline(100, color=GREY, linewidth=1.2, linestyle=":", label="Base (≈2017-18 = 100)")

for _, row in df.iterrows():
    if row["year"] in [2013, 2017, 2020, 2022, 2025]:
        ax.annotate(f"{row['hpi_index']:.1f}",
                    xy=(row["year"], row["hpi_index"]),
                    xytext=(0, 12), textcoords="offset points",
                    ha="center", fontsize=9.5, color=BRAND, fontweight="bold")

ax.set_title("NHB Housing Price Index — Annual Trend (2013–2025)", pad=16)
ax.set_xlabel("Year")
ax.set_ylabel("HPI Value (Base ≈ 100)")
ax.set_xticks(df["year"])
ax.legend(loc="upper left", framealpha=0.9, fontsize=9.5)
ax.grid(True, axis="y")
plt.tight_layout()
save_fig(fig, "01_hpi_annual_trend.png")

# ── CHART 2: HPI Annual Growth Rate (Matplotlib) ──────────────────────
fig, ax = plt.subplots(figsize=(13, 5.5))
colors  = [ACCENT1 if v >= hpi_avg_growth else ACCENT3 if v >= 0 else ACCENT2
           for v in df_growth["hpi_growth_pct"]]
bars = ax.bar(df_growth["year"], df_growth["hpi_growth_pct"],
              color=colors, edgecolor="white", linewidth=0.8, width=0.65)
ax.axhline(hpi_avg_growth, color=BRAND, linewidth=2, linestyle="--",
           label=f"Average ({hpi_avg_growth:.2f}%)")
ax.axhline(hpi_cagr, color=ACCENT4, linewidth=1.5, linestyle=":",
           label=f"CAGR ({hpi_cagr:.2f}%)")

for bar, val in zip(bars, df_growth["hpi_growth_pct"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.15,
            f"{val:.1f}%", ha="center", va="bottom", fontsize=9, fontweight="bold",
            color="#2C3E50")

ax.set_title("NHB HPI — Annual Growth Rate (%) 2014–2025", pad=16)
ax.set_xlabel("Year")
ax.set_ylabel("Growth Rate (%)")
ax.set_xticks(df_growth["year"])
ax.set_ylim(bottom=min(df_growth["hpi_growth_pct"]) - 1, top=max(df_growth["hpi_growth_pct"]) + 2)
ax.legend(fontsize=10)
ax.grid(True, axis="y")

patch_g = mpatches.Patch(color=ACCENT1, label=f"Above avg (≥{hpi_avg_growth:.1f}%)")
patch_a = mpatches.Patch(color=ACCENT3, label="Below avg but positive")
ax.legend(handles=[patch_g, patch_a], loc="upper left", fontsize=9.5)
ax.axhline(hpi_avg_growth, color=BRAND, linewidth=1.8, linestyle="--")
plt.tight_layout()
save_fig(fig, "02_hpi_growth_rate.png")

# ── CHART 3: Quarterly HPI (Matplotlib) ───────────────────────────────
fig, ax = plt.subplots(figsize=(14, 5.5))
ax.fill_between(df_hpi_q["quarter"], df_hpi_q["hpi_assessment"], alpha=0.08, color=ACCENT3)
ax.fill_between(df_hpi_q["quarter"], df_hpi_q["hpi_primary"],    alpha=0.15, color=BRAND)
ax.plot(df_hpi_q["quarter"], df_hpi_q["hpi_primary"],    color=BRAND,   linewidth=2.2, label="HPI Primary (Market/Imputed)")
ax.plot(df_hpi_q["quarter"], df_hpi_q["hpi_assessment"], color=ACCENT3, linewidth=1.5, linestyle="--", label="HPI Assessment")

covid_start = pd.Timestamp("2020-03-01")
covid_end   = pd.Timestamp("2021-06-01")
ax.axvspan(covid_start, covid_end, alpha=0.08, color=ACCENT2)
ax.axvline(pd.Timestamp("2022-01-01"), color=ACCENT4, linewidth=1.2, linestyle=":", alpha=0.8)
ax.text(pd.Timestamp("2022-03-01"), df_hpi_q["hpi_primary"].min() + 2, "Post-COVID\nacceleration",
        fontsize=8.5, color=ACCENT4)

ax.set_title("NHB HPI — Quarterly Granularity (Q2 2013 – Q4 2025)", pad=16)
ax.set_xlabel("Quarter")
ax.set_ylabel("HPI Value")
ax.legend(fontsize=10)
ax.grid(True, axis="y")
plt.tight_layout()
save_fig(fig, "03_hpi_quarterly_trend.png")

# ── CHART 4: CAGR Rolling Analysis (Matplotlib) ───────────────────────
cagr_years, cagr_vals = [], []
base_hpi = df["hpi_index"].iloc[0]
base_yr  = int(df["year"].iloc[0])
for _, row in df.iterrows():
    yr = int(row["year"])
    n  = yr - base_yr
    if n > 0:
        c = ((row["hpi_index"] / base_hpi) ** (1/n) - 1) * 100
        cagr_years.append(yr)
        cagr_vals.append(c)

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(cagr_years, cagr_vals, color=ACCENT4, linewidth=2.5, marker="D",
        markersize=7, markerfacecolor="white", markeredgewidth=2)
ax.axhline(hpi_cagr, color=BRAND, linewidth=1.8, linestyle="--",
           label=f"Final CAGR: {hpi_cagr:.2f}%")
ax.fill_between(cagr_years, cagr_vals, hpi_cagr, alpha=0.12, color=ACCENT4)
ax.set_title("NHB HPI — Rolling CAGR from 2013 Base", pad=16)
ax.set_xlabel("Year (CAGR measured from 2013 to this year)")
ax.set_ylabel("CAGR (%)")
ax.set_xticks(cagr_years)
ax.legend(fontsize=10)
ax.grid(True)
plt.tight_layout()
save_fig(fig, "04_hpi_rolling_cagr.png")


# ═══════════════════════════════════════════════════════════════════════
# SECTION 2 — AED-INR EXCHANGE RATE ANALYSIS
# ═══════════════════════════════════════════════════════════════════════
print()
print(SEP)
print("  SECTION 2: AED-INR EXCHANGE RATE ANALYSIS")
print(SEP)

fx_start  = df_fx_a["rate_annual_avg"].iloc[0]
fx_end    = df_fx_a["rate_annual_avg"].iloc[-1]
fx_years  = len(df_fx_a) - 1
fx_cagr   = ((fx_end / fx_start) ** (1/fx_years) - 1) * 100
fx_total  = (fx_end / fx_start - 1) * 100

fx_growth  = df_growth["fx_growth_pct"]
best_fx_yr  = int(df_growth.loc[fx_growth.idxmax(), "year"])
best_fx_val = fx_growth.max()
worst_fx_yr = int(df_growth.loc[fx_growth.idxmin(), "year"])
worst_fx_val = fx_growth.min()
fx_avg   = fx_growth.mean()
fx_std   = fx_growth.std()
fx_monthly_std = df_fx["rate_close"].std()

print(f"\n  FX Rate Start (2013 avg): {fx_start:.4f} INR/AED")
print(f"  FX Rate End   (2025 avg): {fx_end:.4f} INR/AED")
print(f"  Total INR Depreciation: +{fx_total:.1f}%")
print(f"  Full-Period CAGR: {fx_cagr:.2f}% per year")
print(f"  Best FX Year:  {best_fx_yr}  (+{best_fx_val:.2f}%)")
print(f"  Worst FX Year: {worst_fx_yr} ({worst_fx_val:.2f}%)")
print(f"  Avg Annual FX Change: {fx_avg:.2f}%")
print(f"  FX Annual Std Dev: {fx_std:.2f}% (volatility)")
print(f"  Monthly Closing Rate Std Dev: {fx_monthly_std:.4f}")

# ── CHART 5: Monthly FX Rate + Rolling Average (Matplotlib) ───────────
df_fx_sorted = df_fx.sort_values("date")
rolling_12 = df_fx_sorted["rate_close"].rolling(12).mean()

fig, ax = plt.subplots(figsize=(14, 5.5))
ax.fill_between(df_fx_sorted["date"], df_fx_sorted["rate_close"], alpha=0.10, color=ACCENT1)
ax.plot(df_fx_sorted["date"], df_fx_sorted["rate_close"],
        color=ACCENT1, linewidth=1.2, alpha=0.7, label="Monthly Closing Rate")
ax.plot(df_fx_sorted["date"], rolling_12,
        color=BRAND, linewidth=2.4, label="12-Month Rolling Average")
ax.axhline(df_fx_sorted["rate_close"].mean(), color=GREY, linewidth=1.5,
           linestyle=":", label=f"Overall Mean ({df_fx_sorted['rate_close'].mean():.2f})")

ax.annotate("INR crisis\n(Sep 2013)", xy=(pd.Timestamp("2013-09-01"), 17.89),
            xytext=(20, -18), textcoords="offset points",
            arrowprops=dict(arrowstyle="->", color=ACCENT2), fontsize=8.5, color=ACCENT2)
ax.annotate("COVID\nvolatility", xy=(pd.Timestamp("2020-03-01"), 20.51),
            xytext=(20, 12), textcoords="offset points",
            arrowprops=dict(arrowstyle="->", color=ACCENT2), fontsize=8.5, color=ACCENT2)

ax.set_title("AED-INR Exchange Rate — Monthly Trend (Jan 2013 – Dec 2025)", pad=16)
ax.set_xlabel("Date")
ax.set_ylabel("INR per 1 AED")
ax.legend(fontsize=10)
ax.grid(True, axis="y")
plt.tight_layout()
save_fig(fig, "05_fx_monthly_trend.png")

# ── CHART 6: Annual FX Rate + Growth (Matplotlib dual-axis) ───────────
fig, ax1 = plt.subplots(figsize=(13, 5.5))
ax2 = ax1.twinx()

ax1.fill_between(df_fx_a["year"], df_fx_a["rate_annual_avg"], alpha=0.12, color=ACCENT1)
ax1.plot(df_fx_a["year"], df_fx_a["rate_annual_avg"],
         color=ACCENT1, linewidth=2.5, marker="o", markersize=7,
         markerfacecolor="white", markeredgewidth=2, label="Annual Avg Rate (Left)")
for _, row in df_fx_a.iterrows():
    ax1.annotate(f"{row['rate_annual_avg']:.2f}",
                 xy=(row["year"], row["rate_annual_avg"]),
                 xytext=(0, 10), textcoords="offset points",
                 ha="center", fontsize=8.5, color=ACCENT1)

growth_full = df_fx_a.dropna(subset=["rate_annual_yoy_pct"])
bar_colors  = [ACCENT1 if v >= 0 else ACCENT2 for v in growth_full["rate_annual_yoy_pct"]]
ax2.bar(growth_full["year"], growth_full["rate_annual_yoy_pct"],
        color=bar_colors, alpha=0.35, width=0.5, label="YoY Growth % (Right)")
ax2.axhline(0, color=GREY, linewidth=0.8)

ax1.set_title("AED-INR — Annual Average Rate & YoY Growth (2013–2025)", pad=16)
ax1.set_xlabel("Year")
ax1.set_ylabel("INR per 1 AED", color=ACCENT1)
ax2.set_ylabel("YoY Growth (%)", color=BRAND)
ax1.set_xticks(df_fx_a["year"])
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=9.5)
ax1.grid(True, axis="y")
plt.tight_layout()
save_fig(fig, "06_fx_annual_trend_growth.png")

# ── CHART 7: FX Volatility Band (Matplotlib) ──────────────────────────
rolling_avg = df_fx_sorted["rate_close"].rolling(12).mean()
rolling_std = df_fx_sorted["rate_close"].rolling(12).std()
upper = rolling_avg + 2 * rolling_std
lower = rolling_avg - 2 * rolling_std

fig, ax = plt.subplots(figsize=(14, 5.5))
ax.fill_between(df_fx_sorted["date"], lower, upper, alpha=0.15, color=ACCENT4, label="±2σ Band")
ax.plot(df_fx_sorted["date"], rolling_avg, color=ACCENT4, linewidth=2.2, label="12M Rolling Avg")
ax.plot(df_fx_sorted["date"], df_fx_sorted["rate_close"],
        color=GREY, linewidth=0.9, alpha=0.6, label="Monthly Rate")
ax.set_title("AED-INR — Rolling Average & Volatility Band (±2σ)", pad=16)
ax.set_xlabel("Date")
ax.set_ylabel("INR per 1 AED")
ax.legend(fontsize=10)
ax.grid(True, axis="y")
plt.tight_layout()
save_fig(fig, "07_fx_volatility_band.png")


# ═══════════════════════════════════════════════════════════════════════
# SECTION 3 — INFLATION (CPI) ANALYSIS
# ═══════════════════════════════════════════════════════════════════════
print()
print(SEP)
print("  SECTION 3: INFLATION ANALYSIS")
print(SEP)

cpi_avg   = df_cpi["cpi_pct"].mean()
cpi_max   = df_cpi["cpi_pct"].max()
cpi_min   = df_cpi["cpi_pct"].min()
cpi_std   = df_cpi["cpi_pct"].std()
yr_hi     = int(df_cpi.loc[df_cpi["cpi_pct"].idxmax(), "year"])
yr_lo     = int(df_cpi.loc[df_cpi["cpi_pct"].idxmin(), "year"])
cum_infl  = df_cpi["cumulative_inflation_index"].iloc[-1]
recent_3y = df_cpi[df_cpi["year"] >= 2022]["cpi_pct"].mean()

print(f"\n  CPI Average (2013-2024):    {cpi_avg:.2f}%")
print(f"  CPI Std Dev (volatility):   {cpi_std:.2f}%")
print(f"  Highest CPI: {yr_hi}  ({cpi_max:.2f}%)")
print(f"  Lowest CPI:  {yr_lo}  ({cpi_min:.2f}%)")
print(f"  Recent 3-Year Avg (2022-2024): {recent_3y:.2f}%")
print(f"  Cumulative Inflation (2013-2024): {cum_infl:.4f}x")
print(f"  => Rs 1 lakh in 2013 = Rs {cum_infl:.2f} lakh in 2024 terms")

# ── CHART 8: India CPI Annual Bar Chart (Matplotlib) ──────────────────
fig, ax = plt.subplots(figsize=(12, 5.5))
bar_colors = [ACCENT2 if v >= 7 else ACCENT3 if v >= 5 else ACCENT1
              for v in df_cpi["cpi_pct"]]
bars = ax.bar(df_cpi["year"], df_cpi["cpi_pct"],
              color=bar_colors, edgecolor="white", linewidth=0.8, width=0.65)
ax.axhline(cpi_avg, color=BRAND, linewidth=2, linestyle="--",
           label=f"Average: {cpi_avg:.2f}%")
ax.axhline(6.0, color=ACCENT3, linewidth=1.4, linestyle=":",
           label="Expected scenario: 6.0%")
ax.axhline(4.0, color=ACCENT1, linewidth=1.4, linestyle=":",
           label="Optimistic scenario: 4.0%")
ax.axhline(7.5, color=ACCENT2, linewidth=1.4, linestyle=":",
           label="Conservative scenario: 7.5%")

for bar, val in zip(bars, df_cpi["cpi_pct"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.08,
            f"{val:.1f}%", ha="center", va="bottom", fontsize=9.5, fontweight="bold")

ax.set_title("India Annual CPI Inflation (2013–2024) vs Scenario Thresholds", pad=16)
ax.set_xlabel("Year")
ax.set_ylabel("CPI Annual % Change")
ax.set_xticks(df_cpi["year"])
ax.legend(fontsize=9.5, loc="upper right")
ax.grid(True, axis="y")
patch_r = mpatches.Patch(color=ACCENT2, label="High (≥7%)")
patch_y = mpatches.Patch(color=ACCENT3, label="Medium (5-7%)")
patch_g = mpatches.Patch(color=ACCENT1, label="Low (<5%)")
ax.legend(handles=[patch_r, patch_y, patch_g], loc="upper right", fontsize=9.5)
plt.tight_layout()
save_fig(fig, "08_cpi_annual_trend.png")

# ── CHART 9: Cumulative Inflation Impact (Matplotlib) ─────────────────
fig, ax = plt.subplots(figsize=(12, 5.5))
ax.fill_between(df_cpi["year"], df_cpi["cumulative_inflation_index"], alpha=0.15, color=ACCENT2)
ax.plot(df_cpi["year"], df_cpi["cumulative_inflation_index"],
        color=ACCENT2, linewidth=2.5, marker="o", markersize=7,
        markerfacecolor="white", markeredgewidth=2)
ax.axhline(1.0, color=GREY, linewidth=1.2, linestyle="--", label="Base (2013 = 1.0)")

for _, row in df_cpi.iterrows():
    if row["year"] in [2013, 2016, 2019, 2022, 2024]:
        ax.annotate(f"{row['cumulative_inflation_index']:.2f}x",
                    xy=(row["year"], row["cumulative_inflation_index"]),
                    xytext=(0, 12), textcoords="offset points",
                    ha="center", fontsize=9.5, color=ACCENT2, fontweight="bold")

ax.text(2023.5, 1.03, "Rs 1L in 2013\n= Rs 1.91L\nin 2024",
        fontsize=10, color=ACCENT2, ha="center",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor=ACCENT2, alpha=0.9))

ax.set_title("Cumulative Inflation Impact — India (2013–2024, Base 2013 = 1.0)", pad=16)
ax.set_xlabel("Year")
ax.set_ylabel("Cumulative Price Level (x of 2013)")
ax.set_xticks(df_cpi["year"])
ax.legend(fontsize=10)
ax.grid(True, axis="y")
plt.tight_layout()
save_fig(fig, "09_cumulative_inflation.png")


# ═══════════════════════════════════════════════════════════════════════
# SECTION 4 — CROSS-DATASET ANALYSIS
# ═══════════════════════════════════════════════════════════════════════
print()
print(SEP)
print("  SECTION 4: CROSS-DATASET ANALYSIS")
print(SEP)

# Correlation on model years (2014-2024, all fields complete)
df_corr = df_model[df_model["year"] >= 2014].copy()
df_corr = df_corr[["hpi_growth_pct","cpi_pct","fx_growth_pct","aed_inr_rate"]].dropna()
corr_matrix = df_corr.corr()

print("\n  Correlation Matrix:")
print(corr_matrix.round(4).to_string())

hpi_cpi_r = corr_matrix.loc["hpi_growth_pct","cpi_pct"]
hpi_fx_r  = corr_matrix.loc["hpi_growth_pct","fx_growth_pct"]
cpi_fx_r  = corr_matrix.loc["cpi_pct","fx_growth_pct"]
print(f"\n  HPI Growth vs CPI:     r = {hpi_cpi_r:.4f}")
print(f"  HPI Growth vs FX:      r = {hpi_fx_r:.4f}")
print(f"  CPI vs FX Growth:      r = {cpi_fx_r:.4f}")

# ── CHART 10: Correlation Heatmap (Seaborn) ───────────────────────────
corr_labels = {
    "hpi_growth_pct":  "HPI Growth %",
    "cpi_pct":         "CPI Inflation %",
    "fx_growth_pct":   "FX Growth %",
    "aed_inr_rate":    "AED/INR Rate",
}
corr_renamed = corr_matrix.rename(index=corr_labels, columns=corr_labels)

fig, ax = plt.subplots(figsize=(8, 6))
mask = np.zeros_like(corr_renamed, dtype=bool)
mask[np.triu_indices_from(mask, k=1)] = True
sns.heatmap(corr_renamed, annot=True, fmt=".3f", cmap="RdBu_r",
            center=0, vmin=-1, vmax=1, linewidths=0.5,
            annot_kws={"size": 12, "weight": "bold"},
            cbar_kws={"shrink": 0.8}, ax=ax, mask=False)
ax.set_title("Cross-Dataset Correlation Matrix\n(HPI Growth, CPI, FX Growth, AED/INR Rate)", pad=16)
plt.tight_layout()
save_fig(fig, "10_correlation_heatmap.png")

# ── CHART 11: HPI Growth vs CPI Scatter (Seaborn) ────────────────────
fig, axes = plt.subplots(1, 3, figsize=(16, 5.5))

# Plot 1: HPI vs CPI
ax = axes[0]
sns.scatterplot(data=df_corr, x="cpi_pct", y="hpi_growth_pct",
                s=100, color=BRAND, edgecolor="white", linewidth=1.5, ax=ax)
z = np.polyfit(df_corr["cpi_pct"], df_corr["hpi_growth_pct"], 1)
p = np.poly1d(z)
xs = np.linspace(df_corr["cpi_pct"].min(), df_corr["cpi_pct"].max(), 50)
ax.plot(xs, p(xs), "--", color=ACCENT2, linewidth=1.8, alpha=0.8)
ax.set_title(f"HPI Growth vs CPI\n(r = {hpi_cpi_r:.3f})", fontsize=12)
ax.set_xlabel("CPI Inflation %")
ax.set_ylabel("HPI Annual Growth %")
ax.grid(True, alpha=0.5)
for _, row in df_corr.reset_index().iterrows():
    yr = int(df[df["hpi_growth_pct"] == row["hpi_growth_pct"]]["year"].values[0]) if not df[df["hpi_growth_pct"]==row["hpi_growth_pct"]].empty else ""
    ax.annotate(str(yr), (row["cpi_pct"], row["hpi_growth_pct"]),
                textcoords="offset points", xytext=(5, 4), fontsize=8, color=GREY)

# Plot 2: HPI vs FX
ax = axes[1]
sns.scatterplot(data=df_corr, x="fx_growth_pct", y="hpi_growth_pct",
                s=100, color=ACCENT3, edgecolor="white", linewidth=1.5, ax=ax)
z2 = np.polyfit(df_corr["fx_growth_pct"], df_corr["hpi_growth_pct"], 1)
p2 = np.poly1d(z2)
xs2 = np.linspace(df_corr["fx_growth_pct"].min(), df_corr["fx_growth_pct"].max(), 50)
ax.plot(xs2, p2(xs2), "--", color=ACCENT2, linewidth=1.8, alpha=0.8)
ax.set_title(f"HPI Growth vs FX Growth\n(r = {hpi_fx_r:.3f})", fontsize=12)
ax.set_xlabel("AED/INR Annual Growth %")
ax.set_ylabel("HPI Annual Growth %")
ax.grid(True, alpha=0.5)

# Plot 3: CPI vs FX
ax = axes[2]
sns.scatterplot(data=df_corr, x="fx_growth_pct", y="cpi_pct",
                s=100, color=ACCENT4, edgecolor="white", linewidth=1.5, ax=ax)
z3 = np.polyfit(df_corr["fx_growth_pct"], df_corr["cpi_pct"], 1)
p3 = np.poly1d(z3)
xs3 = np.linspace(df_corr["fx_growth_pct"].min(), df_corr["fx_growth_pct"].max(), 50)
ax.plot(xs3, p3(xs3), "--", color=ACCENT2, linewidth=1.8, alpha=0.8)
ax.set_title(f"CPI vs FX Growth\n(r = {cpi_fx_r:.3f})", fontsize=12)
ax.set_xlabel("AED/INR Annual Growth %")
ax.set_ylabel("CPI Inflation %")
ax.grid(True, alpha=0.5)

plt.suptitle("Cross-Dataset Scatter Relationships", fontsize=14, fontweight="bold", y=1.01)
plt.tight_layout()
save_fig(fig, "11_cross_scatter.png")

# ── CHART 12: Distribution Plots (Seaborn) ────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
sns.histplot(df_growth["hpi_growth_pct"], kde=True, bins=8,
             color=BRAND, edgecolor="white", ax=axes[0])
axes[0].axvline(hpi_avg_growth, color=ACCENT2, linewidth=2, linestyle="--",
                label=f"Mean: {hpi_avg_growth:.2f}%")
axes[0].set_title("Distribution of Annual HPI Growth", fontsize=12)
axes[0].set_xlabel("HPI Growth %")
axes[0].legend(fontsize=9)

sns.histplot(df_cpi["cpi_pct"], kde=True, bins=7,
             color=ACCENT2, edgecolor="white", ax=axes[1])
axes[1].axvline(cpi_avg, color=BRAND, linewidth=2, linestyle="--",
                label=f"Mean: {cpi_avg:.2f}%")
axes[1].set_title("Distribution of India CPI", fontsize=12)
axes[1].set_xlabel("CPI %")
axes[1].legend(fontsize=9)

monthly_mom = df_fx["mom_change_pct"].dropna()
sns.histplot(monthly_mom, kde=True, bins=20,
             color=ACCENT1, edgecolor="white", ax=axes[2])
axes[2].axvline(monthly_mom.mean(), color=ACCENT2, linewidth=2, linestyle="--",
                label=f"Mean: {monthly_mom.mean():.2f}%")
axes[2].set_title("Distribution of Monthly FX Change", fontsize=12)
axes[2].set_xlabel("MoM Change %")
axes[2].legend(fontsize=9)

plt.suptitle("Distribution Analysis — Growth Rates & Inflation", fontsize=14, fontweight="bold", y=1.01)
plt.tight_layout()
save_fig(fig, "12_distribution_plots.png")

# ── CHART 13: Combined 3-Series Overview (Matplotlib) ─────────────────
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(13, 12), sharex=True)

df_plot = df[df["year"] >= 2014].dropna(subset=["hpi_growth_pct","cpi_pct","fx_growth_pct"]).copy()

ax1.bar(df_plot["year"], df_plot["hpi_growth_pct"],
        color=[ACCENT1 if v >= hpi_avg_growth else ACCENT3 for v in df_plot["hpi_growth_pct"]],
        edgecolor="white", width=0.6)
ax1.axhline(hpi_avg_growth, color=BRAND, linewidth=1.5, linestyle="--",
            label=f"Avg HPI Growth: {hpi_avg_growth:.2f}%")
ax1.set_ylabel("HPI Growth %")
ax1.set_title("Housing (HPI) Growth %", fontsize=12, color=BRAND)
ax1.legend(fontsize=9)
ax1.grid(True, axis="y")

ax2.bar(df_plot["year"], df_plot["cpi_pct"],
        color=[ACCENT2 if v >= 7 else ACCENT3 if v >= 5 else ACCENT1 for v in df_plot["cpi_pct"]],
        edgecolor="white", width=0.6)
ax2.axhline(cpi_avg, color=BRAND, linewidth=1.5, linestyle="--",
            label=f"Avg CPI: {cpi_avg:.2f}%")
ax2.set_ylabel("CPI %")
ax2.set_title("India Inflation (CPI) %", fontsize=12, color=ACCENT2)
ax2.legend(fontsize=9)
ax2.grid(True, axis="y")

ax3.bar(df_plot["year"], df_plot["fx_growth_pct"],
        color=[ACCENT1 if v >= 0 else ACCENT2 for v in df_plot["fx_growth_pct"]],
        edgecolor="white", width=0.6)
ax3.axhline(fx_avg, color=BRAND, linewidth=1.5, linestyle="--",
            label=f"Avg FX Growth: {fx_avg:.2f}%")
ax3.set_ylabel("FX Change %")
ax3.set_title("AED-INR Annual Change %", fontsize=12, color=ACCENT1)
ax3.set_xticks(df_plot["year"])
ax3.legend(fontsize=9)
ax3.grid(True, axis="y")

fig.suptitle("Three-Series Annual Comparison: HPI | CPI | FX (2014–2024)",
             fontsize=14, fontweight="bold", y=1.01)
plt.tight_layout()
save_fig(fig, "13_three_series_comparison.png")

# ── CHART 14: Affordability Pressure Index (Matplotlib) ───────────────
# Proxy: HPI growth MINUS FX growth (net INR cost change for UAE expat)
df_plot2 = df_cross.copy()
df_plot2["net_cost_pressure"] = df_plot2["hpi_growth_pct"] - df_plot2["fx_growth_pct"]
df_plot2["real_hpi_growth"]   = df_plot2["hpi_growth_pct"] - df_plot2["cpi_pct"]

fig, ax = plt.subplots(figsize=(13, 5.5))
ax.bar(df_plot2["year"] - 0.2, df_plot2["hpi_growth_pct"],
       width=0.38, color=BRAND, alpha=0.85, label="HPI Growth")
ax.bar(df_plot2["year"] + 0.2, df_plot2["cpi_pct"],
       width=0.38, color=ACCENT2, alpha=0.85, label="CPI Inflation")
ax.plot(df_plot2["year"], df_plot2["real_hpi_growth"],
        color=ACCENT4, linewidth=2.2, marker="D", markersize=7,
        markerfacecolor="white", markeredgewidth=2, label="Real HPI Growth (HPI − CPI)")
ax.axhline(0, color=GREY, linewidth=0.8)

ax.set_title("HPI Growth vs CPI Inflation — Real Housing Appreciation (2014–2024)", pad=16)
ax.set_xlabel("Year")
ax.set_ylabel("Annual % Change")
ax.set_xticks(df_plot2["year"])
ax.legend(fontsize=10)
ax.grid(True, axis="y")
plt.tight_layout()
save_fig(fig, "14_real_hpi_vs_inflation.png")


# ═══════════════════════════════════════════════════════════════════════
# SECTION 5 — PLOTLY INTERACTIVE DASHBOARDS
# ═══════════════════════════════════════════════════════════════════════
print()
print(SEP)
print("  SECTION 5: PLOTLY INTERACTIVE DASHBOARDS")
print(SEP)

PLOTLY_COLORS = {
    "hpi":    "#1B4F72",
    "fx":     "#27AE60",
    "cpi":    "#E74C3C",
    "bg":     "#FAFBFC",
    "grid":   "#E8ECEF",
    "text":   "#2C3E50",
    "accent": "#9B59B6",
}

template_layout = dict(
    font=dict(family="Inter, Arial, sans-serif", color=PLOTLY_COLORS["text"]),
    paper_bgcolor=PLOTLY_COLORS["bg"],
    plot_bgcolor="#FFFFFF",
    xaxis=dict(gridcolor=PLOTLY_COLORS["grid"], showgrid=True),
    yaxis=dict(gridcolor=PLOTLY_COLORS["grid"], showgrid=True),
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)

# ── Plotly 1: HPI Interactive ─────────────────────────────────────────
fig_p1 = go.Figure()
fig_p1.add_trace(go.Scatter(
    x=df_hpi_q["quarter"], y=df_hpi_q["hpi_primary"],
    mode="lines", name="HPI Primary (Quarterly)",
    line=dict(color=PLOTLY_COLORS["hpi"], width=2),
    fill="tozeroy", fillcolor="rgba(27,79,114,0.08)",
    hovertemplate="<b>%{x|%Y-Q%q}</b><br>HPI: %{y:.2f}<extra></extra>",
))
fig_p1.add_trace(go.Scatter(
    x=df_hpi_a["year"], y=df_hpi_a["hpi_primary_avg"],
    mode="markers+lines", name="Annual Average",
    line=dict(color=PLOTLY_COLORS["accent"], width=2.5, dash="dot"),
    marker=dict(size=10, color=PLOTLY_COLORS["accent"], line=dict(color="white", width=2)),
    hovertemplate="<b>%{x}</b><br>Annual Avg HPI: %{y:.2f}<extra></extra>",
))
fig_p1.add_vrect(x0="2020-01-01", x1="2021-06-01",
                 fillcolor="rgba(231,76,60,0.08)", line_width=0,
                 annotation_text="COVID", annotation_position="top left")
fig_p1.update_layout(
    **template_layout,
    title=dict(text="<b>NHB Housing Price Index — Interactive (2013–2025)</b>",
               font=dict(size=18, color=PLOTLY_COLORS["hpi"])),
    xaxis_title="Quarter", yaxis_title="HPI Value",
    height=500,
)
save_plotly(fig_p1, "01_hpi_interactive.html")

# ── Plotly 2: FX Interactive ──────────────────────────────────────────
fig_p2 = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        subplot_titles=("Monthly AED-INR Rate", "Year-over-Year Change (%)"),
                        row_heights=[0.65, 0.35], vertical_spacing=0.08)
rolling_avg_p = df_fx_sorted["rate_close"].rolling(12).mean()
fig_p2.add_trace(go.Scatter(
    x=df_fx_sorted["date"], y=df_fx_sorted["rate_close"],
    mode="lines", name="Monthly Rate",
    line=dict(color=PLOTLY_COLORS["fx"], width=1.2),
    opacity=0.6, hovertemplate="<b>%{x|%b %Y}</b><br>Rate: Rs.%{y:.4f}<extra></extra>",
), row=1, col=1)
fig_p2.add_trace(go.Scatter(
    x=df_fx_sorted["date"], y=rolling_avg_p,
    mode="lines", name="12M Rolling Avg",
    line=dict(color=PLOTLY_COLORS["hpi"], width=2.5),
    hovertemplate="<b>%{x|%b %Y}</b><br>12M Avg: Rs.%{y:.4f}<extra></extra>",
), row=1, col=1)

yoy = df_fx_sorted["yoy_change_pct"].fillna(0)
colors_yoy = ["rgba(39,174,96,0.7)" if v >= 0 else "rgba(231,76,60,0.7)" for v in yoy]
fig_p2.add_trace(go.Bar(
    x=df_fx_sorted["date"], y=yoy, name="YoY Change %",
    marker_color=colors_yoy,
    hovertemplate="<b>%{x|%b %Y}</b><br>YoY: %{y:.2f}%<extra></extra>",
), row=2, col=1)

fig_p2.update_layout(
    **template_layout,
    title=dict(text="<b>AED-INR Exchange Rate — Interactive (2013–2025)</b>",
               font=dict(size=18, color=PLOTLY_COLORS["fx"])),
    height=600,
)
save_plotly(fig_p2, "02_fx_interactive.html")

# ── Plotly 3: Combined Dashboard ──────────────────────────────────────
fig_p3 = make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        "HPI Annual Growth %",
        "CPI Inflation %",
        "AED-INR Annual Rate",
        "Real HPI Growth (HPI - CPI)"
    ),
    vertical_spacing=0.14, horizontal_spacing=0.10,
)

hpi_g_colors = ["rgba(27,79,114,0.85)" if v >= hpi_avg_growth else "rgba(243,156,18,0.85)"
                for v in df_growth["hpi_growth_pct"]]
fig_p3.add_trace(go.Bar(x=df_growth["year"], y=df_growth["hpi_growth_pct"],
                         marker_color=hpi_g_colors, name="HPI Growth",
                         hovertemplate="<b>%{x}</b><br>HPI Growth: %{y:.2f}%<extra></extra>"),
                 row=1, col=1)

cpi_colors = ["rgba(231,76,60,0.85)" if v >= 7 else "rgba(243,156,18,0.85)" if v >= 5 else "rgba(39,174,96,0.85)"
              for v in df_cpi["cpi_pct"]]
fig_p3.add_trace(go.Bar(x=df_cpi["year"], y=df_cpi["cpi_pct"],
                         marker_color=cpi_colors, name="CPI",
                         hovertemplate="<b>%{x}</b><br>CPI: %{y:.2f}%<extra></extra>"),
                 row=1, col=2)

fig_p3.add_trace(go.Scatter(x=df_fx_a["year"], y=df_fx_a["rate_annual_avg"],
                              mode="lines+markers", name="AED/INR Rate",
                              line=dict(color=PLOTLY_COLORS["fx"], width=2.5),
                              marker=dict(size=8),
                              hovertemplate="<b>%{x}</b><br>Rate: Rs.%{y:.4f}<extra></extra>"),
                 row=2, col=1)

real_hpi = df_plot2["real_hpi_growth"]
r_colors = ["rgba(27,79,114,0.8)" if v >= 0 else "rgba(231,76,60,0.8)" for v in real_hpi]
fig_p3.add_trace(go.Bar(x=df_plot2["year"], y=real_hpi,
                         marker_color=r_colors, name="Real HPI",
                         hovertemplate="<b>%{x}</b><br>Real HPI: %{y:.2f}%<extra></extra>"),
                 row=2, col=2)
fig_p3.add_hline(y=0, row=2, col=2, line_dash="dot", line_color="grey", line_width=1)

fig_p3.update_layout(
    **template_layout,
    title=dict(text="<b>HomeGoal AI — EDA Summary Dashboard</b>",
               font=dict(size=18, color=PLOTLY_COLORS["hpi"])),
    height=700, showlegend=False,
)
save_plotly(fig_p3, "03_eda_dashboard.html")

# ── Plotly 4: Affordability Journey Simulator (for context) ───────────
# Illustrates: if someone bought in 2013 vs waited to 2025
ref_property_2013 = 100.0   # normalized to 100
aed_ref_2013      = 14.50   # AED/INR rate
hpi_series = df["hpi_index"].values
fx_series  = df["aed_inr_rate"].values
years_plot = df["year"].values

prop_inr_indexed = (hpi_series / hpi_series[0]) * ref_property_2013
prop_aed_indexed = prop_inr_indexed / (fx_series / aed_ref_2013)

fig_p4 = go.Figure()
fig_p4.add_trace(go.Scatter(
    x=years_plot, y=prop_inr_indexed,
    mode="lines+markers", name="Property Cost (INR-indexed)",
    line=dict(color=PLOTLY_COLORS["hpi"], width=2.5),
    fill="tozeroy", fillcolor="rgba(27,79,114,0.08)",
    hovertemplate="<b>%{x}</b><br>INR Index: %{y:.2f}<extra></extra>",
))
fig_p4.add_trace(go.Scatter(
    x=years_plot, y=prop_aed_indexed,
    mode="lines+markers", name="Property Cost (AED-adjusted)",
    line=dict(color=PLOTLY_COLORS["fx"], width=2.5, dash="dot"),
    hovertemplate="<b>%{x}</b><br>AED-Adjusted Index: %{y:.2f}<extra></extra>",
))
fig_p4.add_annotation(
    x=2025, y=prop_aed_indexed[-1], showarrow=True,
    text=f"AED-adjusted cost<br>is lower due to INR weakening",
    font=dict(size=11, color=PLOTLY_COLORS["fx"]),
    arrowcolor=PLOTLY_COLORS["fx"],
)
fig_p4.update_layout(
    **template_layout,
    title=dict(text="<b>Property Cost Journey — INR Index vs AED-Adjusted (Base 2013 = 100)</b>",
               font=dict(size=16, color=PLOTLY_COLORS["hpi"])),
    xaxis_title="Year", yaxis_title="Indexed Cost (2013 = 100)",
    height=480,
)
save_plotly(fig_p4, "04_property_cost_journey.html")


# ═══════════════════════════════════════════════════════════════════════
# SECTION 6 — KEY STATISTICS SUMMARY
# ═══════════════════════════════════════════════════════════════════════
print()
print(SEP)
print("  SECTION 6: KEY STATISTICS SUMMARY (for Reports)")
print(SEP)

real_hpi_avg    = df_plot2["real_hpi_growth"].mean()
net_cost_avg    = df_plot2["net_cost_pressure"].mean()
yrs_above_cpi   = (df_plot2["hpi_growth_pct"] > df_plot2["cpi_pct"]).sum()
yrs_below_cpi   = (df_plot2["hpi_growth_pct"] <= df_plot2["cpi_pct"]).sum()
fx_benefit_avg  = df_growth["fx_growth_pct"].mean()
total_fx_gain   = (fx_end / fx_start - 1) * 100

print(f"\n  === HOUSING ===")
print(f"  CAGR (2013-2025):         {hpi_cagr:.2f}%")
print(f"  Total Appreciation:       {hpi_total:.1f}%")
print(f"  Avg Annual Growth:        {hpi_avg_growth:.2f}%")
print(f"  Volatility (std dev):     {hpi_std_growth:.2f}%")
print(f"  Best Year:  {best_hpi_yr} ({best_hpi_val:.2f}%)")
print(f"  Worst Year: {worst_hpi_yr} ({worst_hpi_val:.2f}%)")
print(f"  Pre-COVID Avg:            {pre_covid_growth:.2f}%")
print(f"  Post-COVID Avg:           {post_covid_growth:.2f}%")
print(f"  Real HPI Growth (net CPI):{real_hpi_avg:.2f}%")
print(f"  Yrs HPI > CPI:            {yrs_above_cpi}/11")
print(f"  Yrs HPI < CPI:            {yrs_below_cpi}/11")

print(f"\n  === EXCHANGE RATE ===")
print(f"  CAGR (2013-2025):         {fx_cagr:.2f}%")
print(f"  Total INR Depreciation:   {total_fx_gain:.1f}%")
print(f"  Avg Annual FX Change:     {fx_avg:.2f}%")
print(f"  Volatility (std dev):     {fx_std:.2f}%")
print(f"  Best FX Year:  {best_fx_yr} ({best_fx_val:.2f}%)")
print(f"  Worst FX Year: {worst_fx_yr} ({worst_fx_val:.2f}%)")

print(f"\n  === INFLATION ===")
print(f"  Average CPI (2013-2024):  {cpi_avg:.2f}%")
print(f"  CPI Std Dev:              {cpi_std:.2f}%")
print(f"  High CPI (>=7%):          {yr_hi} ({cpi_max:.2f}%)")
print(f"  Low CPI:                  {yr_lo} ({cpi_min:.2f}%)")
print(f"  Recent 3Y Avg (2022-24):  {recent_3y:.2f}%")
print(f"  Cumulative 2013-2024:     {cum_infl:.4f}x")

print(f"\n  === CORRELATIONS ===")
print(f"  HPI Growth vs CPI:        r = {hpi_cpi_r:.4f}")
print(f"  HPI Growth vs FX Growth:  r = {hpi_fx_r:.4f}")
print(f"  CPI vs FX Growth:         r = {cpi_fx_r:.4f}")

print(f"\n  === AED EXPAT PERSPECTIVE ===")
print(f"  Net AED cost pressure (HPI - FX): {net_cost_avg:.2f}% avg/year")
print(f"  Interpretation: For a UAE expat, INR weakening partially offsets HPI.")

print()
print(SEP)
print("  ALL CHARTS GENERATED SUCCESSFULLY")
print(SEP)
print(f"  Matplotlib charts: {DASH_M}")
print(f"  Plotly dashboards: {DASH_P}")
print()
print("  Phase 3 EDA COMPLETE. Awaiting approval for Phase 4.")
