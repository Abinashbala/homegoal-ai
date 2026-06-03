# HomeGoal AI — Backend Architecture

**Version:** 1.0  
**Date:** 2026-06-03  
**Status:** ✅ Phase 6 Complete  

---

## 1. Overview

The HomeGoal AI backend is a deterministic, scenario-based forecasting API built with FastAPI. It translates the data analytics and ML validations from Phases 1-5 into a scalable, stateless business engine. 

The backend is fully decoupled from the machine learning training pipeline. It relies on pre-computed CAGR scenarios (Conservative, Expected, Optimistic) which have been rigorously validated against historical data and time-series models.

---

## 2. Tech Stack

- **Framework:** FastAPI (Python 3.11+)
- **Validation:** Pydantic v2
- **Testing:** Pytest
- **Server:** Uvicorn
- **Architecture:** Modular, Service-Oriented (Engines + Routers)

---

## 3. Directory Structure

```text
backend/
├── main.py                  # FastAPI application entrypoint
├── config.py                # Business constants, validated scenario parameters
├── engines/                 # Pure business logic (Stateless)
│   ├── base.py
│   ├── property.py          # Property appreciation logic
│   ├── wealth.py            # Savings & investment growth
│   ├── inflation.py         # Purchasing power adjustment
│   ├── currency.py          # AED-INR FX projection
│   ├── stress.py            # Deterministic stress scoring
│   └── scenario.py          # Orchestrates engines for a full scenario
├── routers/                 # API Endpoints
│   ├── scenarios.py         # Core business endpoints
│   └── analytics.py         # ML/Recruiter demonstration endpoints
├── schemas/                 # Pydantic validation
│   ├── requests.py
│   └── responses.py
└── tests/                   # Pytest suite
    └── test_engines.py
```

---

## 4. Business Engines

All engines are implemented as stateless classes with `@staticmethod` functions to maximize testability and performance.

### 4.1 Property Engine
- **Input:** Current sqft, price per sqft, target year, scenario
- **Logic:** Applies the validated HPI CAGR to calculate future property cost in INR.
- **CAGR Validated:** 4.45% Expected (Validated by Phase 5 Exponential Trend model).

### 4.2 Wealth Engine
- **Input:** Current savings/investments, monthly contributions, target year, scenario
- **Logic:** Computes nominal future wealth in AED using compound interest for base capital and annuity formulas for monthly contributions.

### 4.3 Currency Engine
- **Input:** Nominal future AED wealth, target year, scenario
- **Logic:** Applies validated FX depreciation CAGR to base rate (Dec 2025: 24.47). Converts AED to nominal INR.
- **CAGR Validated:** 3.34% Expected (Validated by Phase 5 Prophet model).

### 4.4 Inflation Engine
- **Input:** Nominal future INR wealth, target year, scenario
- **Logic:** Discounts nominal wealth using CPI scenarios (Expected: 6.0%) to produce "Real Wealth" representing true purchasing power relative to today's property prices.

### 4.5 Stress Score Engine
- **Input:** Goal gap, property cost, real wealth, income, expenses, risk tolerance
- **Logic:** A purely deterministic scoring system based on three signals:
  1. Goal Gap Ratio (40% weight)
  2. Expense Burden (30% weight)
  3. Coverage Shortfall (30% weight)
- **Output:** A 0-100 score mapped to categories: Safe, Comfortable, Stretch, Risky.

### 4.6 Scenario Engine
- **Input:** Full user profile (Property, Income, Savings, Preferences)
- **Logic:** Orchestrates all sub-engines. For a given scenario (e.g., "expected"), it passes data through Property -> Wealth -> Currency -> Inflation -> Stress sequentially, packaging the result into a standardized KPI response.

---

## 5. API Endpoints

FastAPI automatically generates OpenAPI documentation (Swagger) accessible at `/docs` when the server is running.

### Core Business Flow
- `POST /forecast` — Main application endpoint. Generates a complete 3-scenario projection including summary metrics and recommendations.
- `POST /scenarios` — Similar to forecast but tailored for side-by-side tabular comparison in the UI.
- `POST /stress-score` — Standalone endpoint for calculating stress without running full projections.
- `POST /property-analysis` — Standalone endpoint highlighting only the property appreciation aspect.

### ML & Validation (For Recruiters)
- `GET /model-metrics` — Returns the MAE/RMSE/MAPE model comparison results from Phase 5.
- `GET /model-comparison` — Returns detailed justification for why the simpler CAGR scenario approach was chosen for production over black-box ML models.

### System
- `GET /health` — Service health check.
- `GET /version` — Version and vintage metadata.

---

## 6. Testing Strategy

- `pytest backend/tests/` covers all core calculation engines.
- Test suite validates compound math, bounds, and stress categorizations.
- **Status:** All tests passing.

---

## 7. Next Steps

The backend is structurally complete, documented, and tested. It is ready to serve the frontend.
**Phase 7 (React Frontend)** can now begin.
