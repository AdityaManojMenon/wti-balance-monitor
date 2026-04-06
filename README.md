# WTI Balance Monitor
---

A fundamentals-driven crude oil forecasting engine that ingests weekly EIA petroleum data, computes U.S. crude balance dynamics, normalizes inventory changes against seasonal patterns, and generates pre-release inventory forecasts.

---

## What It Does
- Pulls weekly EIA crude market data
- Computes actual weekly inventory change
- Builds an implied crude balance using:
  - production
  - imports
  - exports
  - refinery runs
- Calculates inventory surprise vs 5-year seasonal norms
- Generates a pre-release directional inventory forecast
- Logs forecasts for track-record building and later evaluation

---

## Why This Matters
Crude oil markets are driven by physical balance dynamics. This project is designed to mirror how a junior crude analyst would prepare for the weekly EIA WPSR release:
- What is the seasonal baseline?
- Are imports, exports, and refinery runs tightening or loosening the market?
- Is the upcoming inventory print likely to be bullish or bearish?

---

## Repo Structure
```bash
wti-balance-monitor/
├── data/
│   ├── raw/
│   └── processed/
├── src/
│   ├── ingestion.py
│   ├── seasonal.py
│   └── forecast.py
├── pipeline.py
├── requirements.txt
└── README.md
```

---

## Current Methodology

### 1. Ingestion
Weekly crude market data is fetched from the **EIA API** for the following variables:
* **Crude Stocks:** Total inventory levels (Excl. SPR).
* **Production:** Domestic field production.
* **Imports:** Gross crude oil imports.
* **Exports:** Gross crude oil exports.
* **Refinery Runs:** Total crude oil input to refineries.

### 2. Balance Construction
The model calculates the physical flow of oil to identify the delta between supply and demand:
$$\text{Implied Balance} = \text{Production} + \text{Imports} - \text{Exports} - \text{Refinery Runs}$$

### 3. Seasonal Normalization
Inventory changes are benchmarked against a **5-year weekly seasonal baseline**. This determines whether the latest build or draw is a structural shift or merely a seasonal norm (e.g., refinery maintenance season).

### 4. Forecasting
A predictive model starts with the **Seasonal Baseline** and applies directional alpha adjustments based on high-frequency deviations:
* **Refinery Runs:** Deviation from the 52-week moving average.
* **Imports:** Deviation from the 52-week moving average.
* **Exports:** Deviation from the 52-week moving average.

---

## Example Output
| Metric | Value |
| :--- | :--- |
| **Seasonal Baseline** | +1.7M bbl |
| **Forecast Inventory Change** | +2.4M bbl |
| **Signal** | **BEARISH** |