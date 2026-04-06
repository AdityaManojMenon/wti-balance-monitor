import pandas as pd

def generate_forecast(df):
    if df.empty:
        raise ValueError("Input DataFrame is empty.")

    latest = df.iloc[-1]

    required_cols = [
        "seasonal_avg",
        "refinery_runs",
        "imports",
        "exports",
    ]

    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns for forecasting: {missing}")

    # 52-week rolling baselines for flow variables
    runs_52w_avg = df["refinery_runs"].rolling(52, min_periods=12).mean().iloc[-1]
    imports_52w_avg = df["imports"].rolling(52, min_periods=12).mean().iloc[-1]
    exports_52w_avg = df["exports"].rolling(52, min_periods=12).mean().iloc[-1]

    # Deviations from "normal"
    runs_dev = latest["refinery_runs"] - runs_52w_avg if pd.notna(runs_52w_avg) else 0
    imports_dev = latest["imports"] - imports_52w_avg if pd.notna(imports_52w_avg) else 0
    exports_dev = latest["exports"] - exports_52w_avg if pd.notna(exports_52w_avg) else 0

    # Forecast logic
    # Higher refinery runs -> more crude demand -> more bullish / lower inventories
    # Higher imports -> more supply -> more bearish / higher inventories
    # Higher exports -> less domestic crude availability -> more bullish / lower inventories
    seasonal_base = latest["seasonal_avg"]

    runs_adjustment = -0.30 * runs_dev
    imports_adjustment = 0.25 * imports_dev
    exports_adjustment = -0.20 * exports_dev

    forecast_inventory_change = (seasonal_base + runs_adjustment + imports_adjustment + exports_adjustment)

    signal = "Bullish" if forecast_inventory_change < 0 else "Bearish"

    return {
        "forecast_date": latest.name,
        "forecast_generated_at": pd.Timestamp.now(),
        "seasonal_base": round(float(seasonal_base), 2),
        "runs_dev": round(float(runs_dev), 2),
        "imports_dev": round(float(imports_dev), 2),
        "exports_dev": round(float(exports_dev), 2),
        "runs_adjustment": round(float(runs_adjustment), 2),
        "imports_adjustment": round(float(imports_adjustment), 2),
        "exports_adjustment": round(float(exports_adjustment), 2),
        "forecast_inventory_change": round(float(forecast_inventory_change), 2),
        "forecast_signal": signal,
    }
