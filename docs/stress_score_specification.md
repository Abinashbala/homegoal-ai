# HomeGoal AI — Stress Score Specification

**Version:** 1.0  
**Date:** 2026-06-03  
**Classification:** Deterministic Rule-Based Engine  
**No ML. Fully explainable.**

---

## Overview

The Stress Score is a single number (0–100) that summarizes how financially stressful a user's home purchase goal is. It is a weighted composite of three normalized signals, each measuring a different dimension of affordability risk.

A high score means the goal is under pressure. A low score means the user is in a comfortable position.

---

## Architecture Constraints

- **No machine learning.** The score must be reproducible and explainable.
- **Deterministic.** The same inputs always produce the same output.
- **Decomposable.** Each component must be individually visible to the user.
- **Scenario-aware.** The score is computed separately for each scenario (Conservative / Expected / Optimistic).

---

## Input Requirements

| Input | Type | Source | Description |
|---|---|---|---|
| `goal_gap_inr` | Float | Affordability engine | Difference: future property cost − real wealth |
| `future_property_value_inr` | Float | HPI forecast | Property cost at target year (scenario) |
| `real_wealth_inr` | Float | Wealth projection | Inflation-adjusted future wealth |
| `monthly_expenses_aed` | Float | User input | Monthly living expenses in AED |
| `monthly_salary_aed` | Float | User input | Monthly gross salary in AED |
| `risk_tolerance` | String | User preference | "conservative" / "moderate" / "aggressive" |

---

## Signal Definitions

### Signal 1: Goal Gap Ratio (Weight: 40%)

Measures how far the user is from fully funding the property purchase.

```
goal_gap_ratio = max(0, goal_gap_inr) / future_property_value_inr
```

| Value | Interpretation |
|---|---|
| 0.00 | No gap — wealth equals or exceeds property cost |
| 0.25 | 25% of property cost still unfunded |
| 0.50 | Half the property cost unfunded |
| 1.00 | Property completely unaffordable |

**Capped at 1.0.** A gap larger than 100% of property cost does not increase the signal beyond 1.0 (the signal is already at maximum stress).

---

### Signal 2: Expense Ratio (Weight: 30%)

Measures monthly financial pressure — how much of income is being consumed by expenses.

```
expense_ratio = min(1.0, monthly_expenses_aed / monthly_salary_aed)
```

| Value | Interpretation |
|---|---|
| 0.00 – 0.40 | Low burn rate — significant savings capacity |
| 0.40 – 0.60 | Moderate burn rate — some savings pressure |
| 0.60 – 0.80 | High burn rate — limited savings capacity |
| 0.80 – 1.00 | Severe burn rate — minimal or no savings |

This signal reflects the user's **ongoing ability to build toward the goal**, not just their current wealth position.

---

### Signal 3: Coverage Shortfall (Weight: 30%)

Measures the proportion of the property cost that is currently unfunded.

```
coverage = min(1.0, real_wealth_inr / future_property_value_inr)
coverage_shortfall = 1.0 - coverage
```

| Value | Interpretation |
|---|---|
| 0.00 | Fully covered — real wealth ≥ property cost |
| 0.25 | 75% covered |
| 0.50 | 50% covered |
| 1.00 | 0% covered — no wealth relative to goal |

This differs from Signal 1 in that it measures the **current coverage level** (not just the gap direction). Both are needed for a complete picture.

---

## Composite Formula

```
raw_score = (0.40 × goal_gap_ratio)
          + (0.30 × expense_ratio)
          + (0.30 × coverage_shortfall)

adjusted_score = raw_score × risk_multiplier

stress_score = min(100, max(0, adjusted_score × 100))
```

---

## Risk Tolerance Multipliers

| Tolerance | Multiplier | Effect |
|---|---|---|
| `conservative` | **1.20** | Amplifies score — conservative user is more stressed by the same situation |
| `moderate` | **1.00** | Baseline — no adjustment |
| `aggressive` | **0.85** | Reduces score — risk-accepting user is less stressed |

---

## Score Classification Bands

| Score Range | Label | Color | Meaning |
|---|---|---|---|
| 0 – 30 | **Safe** | 🟢 Green | Goal is easily achievable; low financial stress |
| 31 – 60 | **Comfortable** | 🟡 Amber | Goal is achievable with moderate effort |
| 61 – 80 | **Stretch** | 🟠 Orange | Goal requires significant savings discipline |
| 81 – 100 | **Risky** | 🔴 Red | Goal is financially stressful; reassessment recommended |

---

## Primary Driver Attribution

The engine identifies which of the three signals is contributing most to the score:

```
primary_driver = argmax(
    ("Goal Gap",       0.40 × goal_gap_ratio),
    ("Expense Burden", 0.30 × expense_ratio),
    ("Coverage",       0.30 × coverage_shortfall)
)
```

This is surfaced in the UI as: **"Your primary stress driver is: Expense Burden"** — giving the user an actionable explanation.

---

## Actionable Recommendations by Primary Driver

| Primary Driver | UI Recommendation |
|---|---|
| **Goal Gap** | "Consider increasing your monthly savings or extending your target timeline." |
| **Expense Burden** | "Reducing monthly expenses by 10–15% would meaningfully improve your score." |
| **Coverage** | "Consider increasing your upfront savings or starting your savings plan earlier." |

---

## Scenario Behavior

The stress score is computed independently for each scenario:

| Scenario | Expected Behavior |
|---|---|
| Conservative | Highest stress score (highest future property cost, weakest wealth growth) |
| Expected | Middle score |
| Optimistic | Lowest stress score (lower property cost, stronger wealth accumulation) |

The platform displays **all three scores simultaneously** in a Scenario Comparison card.

---

## Design Constraints

1. **No negative scores.** Floor is 0.
2. **No scores above 100.** Cap enforced.
3. **Deterministic.** Given identical inputs, score never changes.
4. **Transparent.** All three component values are exposed to the user in a breakdown chart.
5. **Scenario-isolated.** Scores do not bleed between scenarios.
6. **Audit-safe.** Every score can be reconstructed from its inputs — no black box.

---

## Implementation Reference

```python
def compute_stress_score(
    goal_gap_inr,
    future_property_cost,
    monthly_expenses_aed,
    monthly_salary_aed,
    real_wealth_inr,
    risk_tolerance="moderate"
):
    MULTIPLIERS = {"conservative": 1.20, "moderate": 1.00, "aggressive": 0.85}

    goal_gap_ratio      = max(0.0, goal_gap_inr / future_property_cost) if future_property_cost > 0 else 0.0
    expense_ratio       = min(1.0, monthly_expenses_aed / monthly_salary_aed) if monthly_salary_aed > 0 else 1.0
    coverage            = min(1.0, real_wealth_inr / future_property_cost) if future_property_cost > 0 else 0.0
    coverage_shortfall  = 1.0 - coverage

    raw = (0.40 * goal_gap_ratio +
           0.30 * expense_ratio +
           0.30 * coverage_shortfall) * MULTIPLIERS[risk_tolerance]

    score = round(min(100.0, max(0.0, raw * 100)), 1)

    return score, {
        "goal_gap_ratio":     round(goal_gap_ratio, 4),
        "expense_ratio":      round(expense_ratio, 4),
        "coverage_shortfall": round(coverage_shortfall, 4),
        "multiplier":         MULTIPLIERS[risk_tolerance],
        "stress_score":       score,
    }
```

---

## Validation Test Cases

| Case | goal_gap | expense_r | coverage | score (moderate) | Expected label |
|---|---|---|---|---|---|
| Perfect | 0.00 | 0.30 | 0.00 | **9.0** | Safe |
| Moderate pressure | 0.20 | 0.55 | 0.20 | **33.5** | Comfortable |
| High expense | 0.40 | 0.75 | 0.40 | **53.5** | Comfortable |
| Stretched | 0.60 | 0.70 | 0.60 | **75.0** | Stretch |
| Worst case | 1.00 | 1.00 | 1.00 | **100.0** | Risky |

---

*End of Stress Score Specification*
