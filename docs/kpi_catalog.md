# HomeGoal AI — KPI Catalog

**Version:** 1.0  
**Date:** 2026-06-03  
**Purpose:** Define every user-facing metric produced by the platform  
**Audience:** Product, Design, Engineering, QA

---

## Catalog Structure

Each KPI entry contains:
- Display name and description
- Formula
- Source inputs
- Display format
- Priority tier
- Dashboard location
- Business rationale

---

## Priority 0 KPIs — Core Dashboard (Always Visible)

---

### KPI-01: Current Property Value

| Property | Value |
|---|---|
| **Display Name** | Current Property Value |
| **Description** | Estimated market value of the target property today |
| **Formula** | `property_size_sqft × current_price_per_sqft_inr` |
| **Inputs** | User: property size, current price per sqft |
| **Unit** | Indian Rupees (INR) |
| **Format** | Rs 85.00 Lakh / Rs 1.02 Crore |
| **Priority** | P0 |
| **Location** | Property Summary card, top of dashboard |
| **Scenario-specific** | No — fixed at user input |
| **Business Rationale** | Anchors the user's goal. First number they need to understand. |

---

### KPI-02: Future Property Value

| Property | Value |
|---|---|
| **Display Name** | Future Property Cost |
| **Description** | Estimated cost of the same property at the user's target year |
| **Formula** | `property_value × (1 + hpi_scenario_rate)^years_remaining` |
| **Inputs** | KPI-01, HPI scenario rate, target year |
| **Unit** | INR |
| **Format** | Rs 1.32 Crore in 2031 |
| **Priority** | P0 |
| **Location** | Property Forecast card |
| **Scenario-specific** | Yes — shown for all 3 scenarios |
| **Business Rationale** | Communicates the "cost of waiting" — the most powerful motivator for action. |

---

### KPI-03: Future Real Wealth

| Property | Value |
|---|---|
| **Display Name** | Future Real Wealth |
| **Description** | Projected total wealth at target year, adjusted for inflation |
| **Formula** | `future_wealth_inr / (1 + cpi_rate)^years` |
| **Inputs** | Current savings (AED), investments (AED), monthly surplus, FX forecast, CPI scenario |
| **Unit** | INR (real, base-year purchasing power) |
| **Format** | Rs 1.75 Crore (real) |
| **Priority** | P0 |
| **Location** | Wealth Projection card |
| **Scenario-specific** | Yes |
| **Business Rationale** | The correct comparison to future property cost. Nominal wealth is misleading. |

---

### KPI-04: Goal Gap

| Property | Value |
|---|---|
| **Display Name** | Goal Gap |
| **Description** | Difference between future property cost and future real wealth |
| **Formula** | `future_property_value - real_wealth_inr` |
| **Inputs** | KPI-02, KPI-03 |
| **Unit** | INR |
| **Format** | Rs 25.00 Lakh shortfall / Rs 42.39 Lakh surplus |
| **Priority** | P0 |
| **Location** | Goal Gap card — prominently highlighted |
| **Scenario-specific** | Yes |
| **Color Coding** | Red = shortfall, Green = surplus |
| **Business Rationale** | The single most important number for users who are behind on their goal. |

---

### KPI-05: Affordability Ratio

| Property | Value |
|---|---|
| **Display Name** | Affordability Ratio |
| **Description** | Fraction of property cost covered by projected real wealth |
| **Formula** | `real_wealth_inr / future_property_value` |
| **Inputs** | KPI-03, KPI-02 |
| **Unit** | Dimensionless ratio |
| **Format** | 0.72 → "72% Funded" / 1.32 → "Comfortable" |
| **Priority** | P0 |
| **Location** | Affordability Gauge (circular progress indicator) |
| **Scenario-specific** | Yes |
| **Threshold labels** | < 0.5: Difficult · 0.5–0.99: Partial · ≥1.0: Achievable |
| **Business Rationale** | Normalizes the goal gap into a universally understandable percentage. Primary headline metric. |

---

### KPI-06: Required Monthly Savings

| Property | Value |
|---|---|
| **Display Name** | Additional Monthly Savings Required |
| **Description** | Extra monthly savings needed (beyond current rate) to close the goal gap |
| **Formula** | `goal_gap × r / ((1+r)^n_months - 1)` where r = savings rate/12 |
| **Inputs** | KPI-04, savings rate scenario, years remaining |
| **Unit** | AED and INR (both shown) |
| **Format** | +AED 1,840/month · Rs 43,500/month |
| **Priority** | P0 |
| **Location** | Action card — "What do I need to do?" |
| **Scenario-specific** | Yes |
| **Edge case** | If gap ≤ 0 (surplus), display "On track — no extra savings needed" |
| **Business Rationale** | The most actionable output. Converts abstract shortfalls into a concrete monthly commitment. |

---

### KPI-07: Stress Score

| Property | Value |
|---|---|
| **Display Name** | Financial Stress Score |
| **Description** | Composite measure of how financially stressful the home purchase goal is |
| **Formula** | Weighted composite: Goal Gap (40%) + Expense Ratio (30%) + Coverage Shortfall (30%) |
| **Inputs** | KPI-04, expense ratio, KPI-05 |
| **Unit** | 0–100 score |
| **Format** | Score: 64 — Stretch |
| **Priority** | P0 |
| **Location** | Stress Score gauge with breakdown chart |
| **Scenario-specific** | Yes — displayed for all 3 scenarios |
| **Color Coding** | Green (0–30), Amber (31–60), Orange (61–80), Red (81–100) |
| **Business Rationale** | Provides an emotional summary that users can internalize immediately. Drives engagement and return visits. |

---

## Priority 1 KPIs — Detail Cards (Visible on Expand)

---

### KPI-08: Wealth Coverage %

| Property | Value |
|---|---|
| **Formula** | `min(100, real_wealth_inr / future_property_value × 100)` |
| **Format** | 72% of goal funded |
| **Location** | Below Affordability Gauge |
| **Business Rationale** | Alternative framing of KPI-05 for users who prefer percentages over decimals. |

---

### KPI-09: FX Tailwind

| Property | Value |
|---|---|
| **Formula** | `((1 + fx_rate)^years - 1) × 100` |
| **Format** | +34% more INR per AED by 2031 |
| **Location** | Currency card |
| **Business Rationale** | Makes the unique UAE expat advantage tangible. Motivates saving in AED rather than converting to INR prematurely. |

---

### KPI-10: Monthly Savings Rate

| Property | Value |
|---|---|
| **Formula** | `(salary - expenses) / salary × 100` |
| **Format** | Saving 46.7% of income |
| **Location** | Income card |
| **Business Rationale** | Benchmarks user's savings discipline. Industry standard: 20%+ is healthy for homebuyers. |

---

### KPI-11: Years to Full Affordability

| Property | Value |
|---|---|
| **Formula** | Solve for n where `affordability_ratio(n) = 1.0` |
| **Format** | Fully affordable in 2034 |
| **Location** | Timeline card |
| **Business Rationale** | For users who are currently below 100% — tells them when they'll cross the threshold without extra effort. |

---

### KPI-12: Inflation-Adjusted Savings Erosion

| Property | Value |
|---|---|
| **Formula** | `current_savings_inr × ((1+cpi)^years - 1)` |
| **Format** | Rs 18L of savings lost to inflation over 6 years |
| **Location** | Inflation explainer card |
| **Business Rationale** | Makes inflation tangible and personal. Encourages users to invest rather than leave money in low-yield accounts. |

---

## Priority 2 KPIs — Scenario Comparison Table

The following KPIs are shown in a **3-column comparison table** (Conservative / Expected / Optimistic):

| KPI | Conservative | Expected | Optimistic |
|---|---|---|---|
| Future Property Value | Rs X Crore | Rs Y Crore | Rs Z Crore |
| Future Real Wealth | Rs A Crore | Rs B Crore | Rs C Crore |
| Goal Gap | Largest | Mid | Smallest |
| Affordability Ratio | Lowest | Mid | Highest |
| Required Extra Savings | Highest | Mid | Lowest |
| Stress Score | Highest | Mid | Lowest |

---

## KPI Dependency Map

```
User Inputs
├── monthly_salary_aed
├── monthly_expenses_aed
├── current_savings_aed
├── current_investment_aed
├── monthly_investment_contrib
├── property_size_sqft
├── current_price_per_sqft_inr
└── target_year

            ↓

Forecast Outputs (Phase 5)
├── hpi_scenario_rate
├── fx_scenario_rate
└── cpi_scenario_rate (fixed)

            ↓

Computed KPIs (Phase 6 Engine)
├── KPI-01: property_value
├── KPI-02: future_property_value        ← uses HPI forecast
├── KPI-03: real_wealth                  ← uses FX + CPI forecast
├── KPI-04: goal_gap                     ← KPI-02 - KPI-03
├── KPI-05: affordability_ratio          ← KPI-03 / KPI-02
├── KPI-06: required_monthly_savings     ← derived from KPI-04
├── KPI-07: stress_score                 ← uses KPI-04, KPI-05, expense_ratio
├── KPI-08: wealth_coverage_%            ← derived from KPI-05
├── KPI-09: fx_tailwind                  ← derived from FX forecast
├── KPI-10: monthly_savings_rate         ← user inputs only
├── KPI-11: years_to_affordability       ← solver using KPI-05 curve
└── KPI-12: savings_erosion              ← uses CPI scenario
```

---

## KPI Output Requirements for API

The backend affordability engine must return all P0 KPIs in every response, and all P1 KPIs on request. Format:

```json
{
  "scenario": "expected",
  "years_remaining": 6,
  "kpis": {
    "current_property_value_inr": 10200000,
    "future_property_value_inr": 13244000,
    "future_wealth_nominal_inr": 19800000,
    "real_wealth_inr": 17483000,
    "goal_gap_inr": -4239000,
    "affordability_ratio": 1.32,
    "required_extra_savings_inr": 0,
    "required_extra_savings_aed": 0,
    "stress_score": 16.0,
    "stress_label": "Safe",
    "stress_primary_driver": "Expense Burden",
    "monthly_savings_rate_pct": 46.67,
    "fx_tailwind_pct": 22.4,
    "wealth_coverage_pct": 100.0
  },
  "stress_breakdown": {
    "goal_gap_ratio": 0.0,
    "expense_ratio": 0.533,
    "coverage_shortfall": 0.0,
    "multiplier": 1.0
  }
}
```

---

*End of KPI Catalog*
