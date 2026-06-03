# HomeGoal AI

> AI-powered home affordability planning platform for UAE expats buying property in India.

---

## What is HomeGoal AI?

HomeGoal AI helps UAE-based Indian expats make informed property purchase decisions by combining:

- **Wealth forecasting** — How much will I accumulate?
- **Property price projection** — How much will my target property cost?
- **Inflation impact analysis** — What is my real purchasing power?
- **Currency movement analysis** — How does AED/INR movement affect my goal?
- **Scenario analysis** — Conservative / Expected / Optimistic paths
- **Stress score** — Am I stretching too far financially?

**This is NOT a property listing, mortgage, or financial advice platform.**

---

## Project Structure

```
HomeGoal AI/
├── raw/                    # Source datasets (do not modify)
├── processed/              # Cleaned & transformed data
├── notebooks/              # Jupyter analytics pipeline
├── models/                 # ML models and scripts
├── backend/                # FastAPI backend
├── frontend/               # React + TypeScript UI
├── docs/                   # Documentation
├── dashboards/             # Tableau + Plotly exports
└── tests/                  # Test suite
```

---

## Datasets

| Dataset | Source | Coverage |
|---|---|---|
| NHB Housing Price Index | National Housing Bank India | Q2 2013 – Q4 2025 |
| India CPI Inflation | World Bank Open Data | 2013 – 2024 |
| AED-INR Exchange Rate | Investing.com | Jan 2013 – Dec 2025 |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React + TypeScript + Tailwind CSS |
| Charts | Plotly.js |
| Backend | FastAPI (Python) |
| ML | Prophet, XGBoost, scikit-learn |
| Data | Pandas, NumPy |
| Database | Supabase PostgreSQL |
| Deployment | Render (Frontend + Backend) |

---

## Analytics Pipeline

```
01_data_audit.ipynb       → Data profiling
02_data_cleaning.ipynb    → Cleaning & processing
03_eda.ipynb              → Exploratory analysis
04_feature_engineering.ipynb → Feature derivation
05_modeling.ipynb         → Model training & evaluation
```

---

## Documentation

| Document | Purpose |
|---|---|
| `docs/data_audit_report.md` | Full dataset analysis |
| `docs/data_dictionary.md` | All field definitions |
| `docs/cleaning_strategy.md` | Data quality & cleaning steps |
| `docs/feature_engineering_plan.md` | Feature formulas |
| `docs/project_architecture.md` | System design |

---

## Development Status

| Phase | Task | Status |
|---|---|---|
| Phase 0 | Data Audit | ✅ Complete |
| Phase 1 | Project Structure + Docs | ✅ Complete |
| Phase 2 | Data Cleaning | ⏳ Next |
| Phase 3 | EDA | ⏳ Pending |
| Phase 4 | Feature Engineering | ⏳ Pending |
| Phase 5 | Modeling | ⏳ Pending |
| Phase 6 | Backend | ⏳ Pending |
| Phase 7 | Frontend | ⏳ Pending |
| Phase 8 | Deployment | ⏳ Pending |

---

## Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Launch Jupyter
jupyter lab notebooks/

# Run backend (after development)
cd backend && uvicorn app.main:app --reload

# Run frontend (after development)
cd frontend && npm install && npm run dev
```

---

## Author

**Abinash Balasubramanian**  
Data Analyst | ML Engineer Portfolio Project

---

*HomeGoal AI is a portfolio project for demonstration purposes. It does not provide financial advice.*
