# HomeGoal AI — Project Architecture

**Version:** 1.0  
**Date:** 2026-06-02  
**Status:** MVP Design  

---

## 1. Project Overview

HomeGoal AI is a full-stack fintech analytics platform for UAE-based Indian expats planning to purchase property in India. It combines personal finance forecasting, housing market analytics, inflation modelling, and currency scenario analysis into a single unified platform.

**This is NOT a property listing, mortgage, or financial advice platform.**  
It is a **forecasting, affordability planning, and scenario-analysis platform.**

---

## 2. Full Project Structure

```
HomeGoal AI/
│
├── raw/                                    # Original source datasets (do not modify)
│   ├── AED_INR Historical Data.csv         # AED-INR monthly exchange rates (2013-2025)
│   ├── API_FP.CPI.TOTL.ZG_DS2_en_csv_v2_278989.csv   # World Bank India CPI
│   └── india_housing_price_index_nhb_2013_2025.xls.xlsx   # NHB Housing Price Index
│
├── processed/                              # Cleaned, transformed datasets
│   ├── nhb_hpi/
│   │   ├── nhb_hpi_clean.csv               # Cleaned quarterly HPI
│   │   └── nhb_hpi_annual.csv              # Annual resampled HPI
│   ├── inflation/
│   │   └── india_cpi_clean.csv             # India-only CPI, long format
│   ├── exchange_rate/
│   │   ├── aed_inr_clean.csv               # Cleaned monthly FX rates
│   │   └── aed_inr_annual.csv              # Annual averaged FX rates
│   └── master_annual.csv                   # Joined master time-series (all 3 datasets)
│
├── notebooks/                              # Jupyter notebooks for analytics pipeline
│   ├── 01_data_audit.ipynb                 # Data profiling and quality checks
│   ├── 02_data_cleaning.ipynb              # All cleaning steps executed
│   ├── 03_eda.ipynb                        # Exploratory data analysis + visualizations
│   ├── 04_feature_engineering.ipynb        # Feature derivation and validation
│   └── 05_modeling.ipynb                   # Model training, evaluation, selection
│
├── models/                                 # Machine learning models
│   ├── artifacts/                          # Saved trained model files
│   │   ├── hpi_prophet_model.pkl           # Housing growth forecast model
│   │   ├── fx_prophet_model.pkl            # Currency trend forecast model
│   │   └── cpi_forecast_model.pkl          # Inflation forecast model
│   └── scripts/                            # Reusable Python scripts
│       ├── data_cleaner.py                 # Data cleaning functions
│       ├── feature_builder.py              # Feature engineering functions
│       ├── train_hpi_model.py              # HPI model training script
│       ├── train_fx_model.py               # FX model training script
│       └── train_cpi_model.py              # CPI model training script
│
├── backend/                                # FastAPI backend
│   ├── app/
│   │   ├── main.py                         # FastAPI app entry point
│   │   ├── routers/
│   │   │   ├── forecast.py                 # /api/forecast endpoint
│   │   │   ├── scenarios.py                # /api/scenarios endpoint
│   │   │   ├── stress.py                   # /api/stress-score endpoint
│   │   │   └── property.py                 # /api/property-analysis endpoint
│   │   ├── engines/
│   │   │   ├── wealth_engine.py            # Wealth projection calculations
│   │   │   ├── property_engine.py          # Property value projections
│   │   │   ├── stress_engine.py            # Stress score computation
│   │   │   ├── scenario_engine.py          # Scenario generation
│   │   │   └── forecast_engine.py          # Model inference wrapper
│   │   ├── schemas/
│   │   │   ├── user_inputs.py              # Pydantic input validation models
│   │   │   └── responses.py                # Pydantic response models
│   │   └── utils/
│   │       ├── model_loader.py             # Load trained model artifacts
│   │       └── constants.py                # Scenario parameters, thresholds
│   └── tests/
│       ├── test_wealth_engine.py
│       ├── test_stress_engine.py
│       └── test_scenario_engine.py
│
├── frontend/                               # React + TypeScript + Tailwind UI
│   ├── src/
│   │   ├── pages/
│   │   │   ├── HomePage.tsx                # Landing + input form
│   │   │   ├── ForecastPage.tsx            # Wealth & property forecast charts
│   │   │   ├── ScenarioPage.tsx            # Scenario comparison dashboard
│   │   │   ├── StressPage.tsx              # Stress score dashboard
│   │   │   └── RecruiterPage.tsx           # Portfolio showcase page
│   │   ├── components/
│   │   │   ├── ProfileForm.tsx             # Multi-step user input form
│   │   │   ├── WealthChart.tsx             # Plotly wealth trajectory
│   │   │   ├── PropertyChart.tsx           # Plotly property forecast
│   │   │   ├── ScenarioTable.tsx           # Side-by-side scenario view
│   │   │   ├── StressGauge.tsx             # Stress score gauge
│   │   │   ├── GoalGapCard.tsx             # Goal gap visualization
│   │   │   └── AffordabilityCard.tsx       # Budget tier display
│   │   ├── api/
│   │   │   └── client.ts                   # Axios client → FastAPI
│   │   └── hooks/
│   │       └── useForecast.ts              # Data fetching hook
│   └── public/
│       └── index.html
│
├── docs/                                   # Project documentation
│   ├── data_audit_report.md                # ← This file (data analysis)
│   ├── data_dictionary.md                  # Field definitions for all datasets
│   ├── cleaning_strategy.md                # Data quality + cleaning plan
│   ├── feature_engineering_plan.md         # Feature derivation formulas
│   └── project_architecture.md            # This file
│
├── dashboards/                             # Visualization outputs
│   ├── tableau/                            # Tableau workbook files (.twbx)
│   └── plotly/                             # Exported Plotly HTML dashboards
│
├── tests/                                  # Integration and end-to-end tests
│
├── .gitignore
├── README.md
└── requirements.txt
```

---

## 3. System Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    USER BROWSER                         │
│         React + TypeScript + Tailwind + Plotly          │
│                                                         │
│  ┌──────────┐  ┌───────────┐  ┌─────────┐  ┌────────┐  │
│  │  Input   │  │ Forecast  │  │Scenario │  │Stress  │  │
│  │  Form    │  │ Dashboard │  │Dashboard│  │Score   │  │
│  └────┬─────┘  └─────┬─────┘  └────┬────┘  └───┬────┘  │
└───────┼──────────────┼─────────────┼────────────┼───────┘
        │              │             │            │
        └──────────────┴─────────────┴────────────┘
                              │
                    HTTP (REST API / JSON)
                              │
┌─────────────────────────────┼───────────────────────────┐
│                    FASTAPI BACKEND                       │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │                  API Routers                     │   │
│  │  /forecast  /scenarios  /stress-score  /property │   │
│  └──────────────────┬───────────────────────────────┘   │
│                     │                                   │
│  ┌──────────────────▼───────────────────────────────┐   │
│  │               Business Engines                   │   │
│  │  WealthEngine  PropertyEngine  ScenarioEngine    │   │
│  │  StressEngine  ForecastEngine                    │   │
│  └──────────────────┬───────────────────────────────┘   │
│                     │                                   │
│  ┌──────────────────▼───────────────────────────────┐   │
│  │              ML Model Artifacts                  │   │
│  │  HPI Prophet  │  FX Prophet  │  CPI Forecast     │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 4. Data Flow

```
Raw Datasets (raw/)
       │
       ▼
Cleaning Scripts (notebooks/02 or models/scripts/data_cleaner.py)
       │
       ▼
Processed Datasets (processed/)
  ├── nhb_hpi_clean.csv
  ├── india_cpi_clean.csv
  ├── aed_inr_clean.csv
  └── master_annual.csv
       │
       ▼
Feature Engineering (notebooks/04 or models/scripts/feature_builder.py)
       │
       ▼
Model Training (notebooks/05 or models/scripts/train_*.py)
       │
       ▼
Saved Model Artifacts (models/artifacts/*.pkl)
       │
       ▼ (at runtime)
FastAPI Backend (loads artifacts + accepts user inputs)
       │
       ▼
JSON Response → React Frontend
```

---

## 5. Technology Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| **Frontend** | React | 18+ | UI framework |
| **Frontend Language** | TypeScript | 5+ | Type safety |
| **Frontend Styling** | Tailwind CSS | 3+ | Utility-first CSS |
| **Frontend Charts** | Plotly.js | Latest | Interactive visualizations |
| **Backend** | FastAPI | Latest | REST API framework |
| **Backend Language** | Python | 3.11+ | All backend + ML logic |
| **Data** | Pandas + NumPy | Latest | Data manipulation |
| **ML – Forecasting** | Prophet | Latest | Time-series forecasting |
| **ML – Alternative** | XGBoost + sklearn | Latest | Fallback/comparison models |
| **Model Serialization** | joblib / pickle | Built-in | Save/load model artifacts |
| **Validation** | Pydantic v2 | Latest | Input/output schemas |
| **Notebooks** | Jupyter / JupyterLab | Latest | Analytics pipeline |
| **Visualization (EDA)** | Matplotlib + Seaborn | Latest | Static analysis charts |
| **BI Dashboard** | Tableau Public | Latest | Recruiter showcase |
| **Database** | Supabase PostgreSQL | Latest | Optional: store sessions |
| **Deployment – Frontend** | Render (Static) | — | Frontend hosting |
| **Deployment – Backend** | Render (Web Service) | — | FastAPI hosting |

---

## 6. API Endpoint Design

### `POST /api/forecast`
**Purpose:** Generate wealth + property forecast for a given user profile.

**Input:**
```json
{
  "monthly_salary_aed": 15000,
  "monthly_expenses_aed": 8000,
  "current_savings_aed": 50000,
  "current_investment_value_aed": 20000,
  "monthly_investment_contribution_aed": 2000,
  "expected_investment_return_pct": 9.0,
  "city": "Chennai",
  "locality": "Mogappair",
  "property_size_sqft": 1200,
  "current_price_per_sqft_inr": 8500,
  "target_purchase_year": 2031,
  "risk_tolerance": "moderate"
}
```

**Output:**
```json
{
  "current_property_value_inr": 10200000,
  "future_property_cost": { "conservative": ..., "expected": ..., "optimistic": ... },
  "future_wealth_real_inr": { "conservative": ..., "expected": ..., "optimistic": ... },
  "goal_gap": { "conservative": ..., "expected": ..., "optimistic": ... },
  "wealth_trajectory": [...],
  "property_trajectory": [...],
  "fx_forecast": [...],
  "inflation_forecast": [...]
}
```

---

### `POST /api/stress-score`
**Input:** Same as `/forecast`  
**Output:**
```json
{
  "conservative": { "score": 72, "category": "Stretch", "drivers": {...} },
  "expected":     { "score": 54, "category": "Comfortable", "drivers": {...} },
  "optimistic":   { "score": 31, "category": "Comfortable", "drivers": {...} }
}
```

---

### `POST /api/scenarios`
**Input:** Same as `/forecast`  
**Output:** Side-by-side comparison of all 3 scenarios across all metrics.

---

### `POST /api/property-analysis`
**Input:** `property_size_sqft`, `current_price_per_sqft_inr`, `target_year`  
**Output:** Property value now vs future, appreciation trajectory.

---

## 7. ML Model Design

| Model | Purpose | Algorithm | Input Features | Output |
|---|---|---|---|---|
| Housing Growth Model | Forecast future HPI | Prophet (primary) | `hpi_quarterly`, time features | HPI at target year + confidence bounds |
| Currency Trend Model | Forecast AED/INR rate | Prophet (primary) | `fx_monthly`, time features | FX rate at target year + bounds |
| Inflation Forecast Model | Forecast India CPI | Linear trend / ARIMA | `cpi_annual`, time features | CPI% at target year |

**Validation Protocol:**
- Train/test split: 80% train, 20% test (time-based)
- Metrics: MAE, RMSE, MAPE
- Baseline: Naïve last-value and linear trend
- Selection: Best MAPE wins

---

## 8. Frontend Dashboard Pages

| Page | Route | Purpose |
|---|---|---|
| Home | `/` | Project intro + user input form |
| Forecast | `/forecast` | Wealth trajectory + property price forecast |
| Scenarios | `/scenarios` | Conservative / Expected / Optimistic comparison |
| Stress Score | `/stress` | Stress gauge + goal gap + affordability |
| Recruiter | `/recruiter` | EDA highlights, model performance, architecture |

---

## 9. Development Phase Plan

| Phase | Task | Status |
|---|---|---|
| Phase 0 | Data Audit | ✅ Complete |
| Phase 1 | Project Structure + Documentation | ✅ Complete |
| Phase 2 | Data Cleaning (`notebooks/02`) | ⏳ Next |
| Phase 3 | EDA (`notebooks/03`) | ⏳ Pending |
| Phase 4 | Feature Engineering (`notebooks/04`) | ⏳ Pending |
| Phase 5 | Model Training + Validation (`notebooks/05`) | ⏳ Pending |
| Phase 6 | Backend Development (FastAPI engines) | ⏳ Pending |
| Phase 7 | Frontend Development (React UI) | ⏳ Pending |
| Phase 8 | Tableau Dashboard | ⏳ Pending |
| Phase 9 | Deployment (Render + Supabase) | ⏳ Pending |

---

## 10. Non-Functional Requirements

| Requirement | Target |
|---|---|
| Forecast generation time | < 10 seconds |
| API response time | < 3 seconds |
| Mobile responsive | Yes — all screen sizes |
| Input validation | Strict (Pydantic) |
| Error handling | Graceful with user-friendly messages |
| Explainability | Every forecast includes assumptions + sources |
| Accessibility | WCAG 2.1 AA |

---

*End of Project Architecture Document*
