# WTI Balance Monitor

A fundamentals-driven crude oil forecasting engine that ingests weekly EIA petroleum data, computes U.S. crude balance dynamics, normalizes inventory changes against seasonal patterns, and generates pre-release inventory forecasts.

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

## Why This Matters
Crude oil markets are driven by physical balance dynamics. This project is designed to mirror how a junior crude analyst would prepare for the weekly EIA WPSR release:
- What is the seasonal baseline?
- Are imports, exports, and refinery runs tightening or loosening the market?
- Is the upcoming inventory print likely to be bullish or bearish?

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