# HomeGoal AI

A property affordability planning platform designed for UAE-based professionals targeting home purchases in India.

HomeGoal AI helps users estimate future property costs, required wealth targets, affordability, savings requirements, and financial stress under multiple economic scenarios using historical housing, inflation, and currency data.

---

## Live Demo

### Frontend

https://homegoal-ai.onrender.com

### Backend API Documentation

https://homegoal-ai-backend.onrender.com/docs

---

## Project Overview

Purchasing property in India while earning abroad introduces several financial uncertainties:

* Housing price appreciation
* Inflation
* Currency exchange fluctuations
* Wealth accumulation requirements
* Affordability constraints

HomeGoal AI combines these factors into a single planning experience.

Users can:

* Estimate future property values
* Compare Conservative, Expected, and Optimistic scenarios
* Calculate required wealth targets
* Determine required monthly savings
* Evaluate affordability ratios
* Assess financial stress scores
* Review forecasting assumptions and model validation results

---

## Key Features

### Property Planning

* Target property size (sq ft)
* Custom price per sq ft input
* Target purchase year selection
* Future property valuation

### Wealth Forecasting

* Current savings
* Monthly investments
* Salary-based planning
* Long-term wealth accumulation projections

### Economic Adjustments

* Housing Price Index trends
* Inflation-adjusted calculations
* AED-INR exchange rate analysis

### Scenario Analysis

#### Conservative

Higher inflation and stronger property appreciation assumptions.

#### Expected

Based on historical averages and observed trends.

#### Optimistic

Lower inflation and favorable affordability assumptions.

### Financial Health Metrics

* Goal Gap
* Required Monthly Savings
* Affordability Ratio
* Stress Score (0–100)

### Recruiter Insights Dashboard

Technical reviewers can explore:

* Dataset audits
* Exploratory Data Analysis
* Feature Engineering
* Forecasting methodology
* Model comparison results
* Architecture documentation

---

## Datasets Used

### National Housing Bank (NHB) Housing Price Index

* Quarterly housing price index
* 2013–2025
* Used for housing appreciation analysis

### World Bank Inflation Data

* India Consumer Price Inflation
* 2013–2024
* Used for inflation scenarios

### AED-INR Exchange Rate Data

* Monthly exchange rates
* 2013–2025
* Used for currency impact analysis

---

## Forecasting Methodology

### Housing Prices

Models evaluated:

* Linear Trend
* Exponential Trend
* Prophet
* XGBoost

Selected model:

* Exponential Trend

Performance:

* MAE: 16.48
* RMSE: 18.74
* MAPE: 11.98%

### Currency Forecasting

Models evaluated:

* Linear Trend
* Exponential Trend
* Prophet

Selected model:

* Prophet

Performance:

* MAE: 0.382
* RMSE: 0.475
* MAPE: 1.66%

### Production Engine

For interpretability and transparency, the live platform uses scenario-driven forecasting rather than opaque black-box predictions.

---

## Technology Stack

### Frontend

* React
* TypeScript
* Vite
* Tailwind CSS
* Axios
* Plotly.js

### Backend

* FastAPI
* Pydantic
* Uvicorn

### Data Science

* Python
* Pandas
* NumPy
* Scikit-learn
* Prophet
* XGBoost
* Matplotlib
* Seaborn
* Plotly

### Deployment

* Render (Frontend)
* Render (Backend)
* GitHub

---

## Architecture

Frontend (React + TypeScript)

↓

FastAPI Backend

↓

Business Logic Engines

* Property Engine
* Wealth Engine
* Inflation Engine
* Currency Engine
* Stress Engine
* Scenario Engine

↓

Processed Economic Datasets

---

## Project Structure

```text
HomeGoal AI/
├── backend/
├── frontend/
├── models/
├── notebooks/
├── processed/
├── raw/
├── dashboards/
├── docs/
└── tests/
```

---

## Local Development

### Clone Repository

```bash
git clone https://github.com/Abinashbala/homegoal-ai.git
cd homegoal-ai
```

### Backend

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

Backend available at:

```text
http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend available at:

```text
http://localhost:5173
```

---

## Future Enhancements

* City-level housing datasets
* Mortgage affordability calculator
* Interactive retirement planning
* User authentication
* Portfolio tracking
* AI-assisted financial recommendations
* Real estate market intelligence dashboards

---

## Author

**Abinash Balasubramanian**

GitHub:
https://github.com/Abinashbala

LinkedIn:
https://www.linkedin.com/in/abinashbala/

---

## Disclaimer

This application is intended for educational, analytical, and planning purposes only. It should not be considered financial, investment, or real estate advice.

