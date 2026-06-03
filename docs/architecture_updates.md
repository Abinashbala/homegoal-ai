# HomeGoal AI — Architecture Updates Log

**Version:** 1.1  
**Date:** 2026-06-02  
**Status:** Applied  

---

## Update 1 — Forecast Model Strategy

**Change:** Prophet is no longer assumed to be the default model.

For each forecasting task, all candidate models are compared using MAE, RMSE, and MAPE. The best performer is selected and documented.

### Housing Forecast Candidates
| Model | Notes |
|---|---|
| Linear Trend | Baseline — fast, interpretable |
| Exponential Growth Trend | Better for compounding growth |
| Prophet | Handles seasonality, holiday effects |
| XGBoost (time-series features) | If dataset size is sufficient |

### AED-INR Forecast Candidates
| Model | Notes |
|---|---|
| Linear Trend | Baseline |
| Exponential Growth Trend | Captures compounding depreciation |
| Prophet | Handles structural breaks |
| XGBoost (time-series features) | If monthly data is sufficient |

**Selection Criteria:** Lowest MAPE on held-out test set. Document winner and reason.

---

## Update 2 — Inflation Strategy Change

**Change:** CPI forecasting as a standalone ML model is REMOVED from MVP.

**Replacement:** Scenario-based fixed inflation assumptions.

| Scenario | Annual Inflation Assumption |
|---|---|
| Conservative | 7.5% |
| Expected | 6.0% |
| Optimistic | 4.0% |

CPI historical data is still used for:
- Real wealth calculations (cumulative deflation)
- Scenario calibration (the 6% expected is derived from historical average)
- Explainability context in the UI

---

## Update 3 — Affordability Ratio KPI (New)

**New primary business metric added:**

```python
affordability_ratio = real_wealth_inr / future_property_cost_inr
```

| Ratio | Category |
|---|---|
| < 0.5 | Difficult |
| 0.5 – 1.0 | Partially Affordable |
| 1.0 | Fully Affordable |
| > 1.0 | Comfortable |

**Included in:** Forecast output, Scenario output, Stress analysis output.

---

## Update 4 — Required Monthly Savings KPI (New)

**New KPI added:**

```python
# If goal_gap > 0 (user is short)
additional_monthly_savings_needed = goal_gap / (years_to_goal * 12)

# More precise: compound savings formula inverted
# monthly_savings_needed = goal_gap / (((1 + r)^n - 1) / r)
# where r = monthly rate, n = months remaining
```

**Example output:**
```
Goal Gap: ₹25,00,000
To reach your target by 2032, you need to save an additional ₹18,400/month.
```

**Included in:** All scenario outputs and stress analysis.

---

*These updates are reflected in: feature_engineering_plan.md, project_architecture.md*
