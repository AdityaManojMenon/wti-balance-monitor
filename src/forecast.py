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
    runs_dev = (latest["refinery_runs"] * 7) - (runs_52w_avg * 7) if pd.notna(runs_52w_avg) else 0
    imports_dev = (latest["imports"] * 7) - (imports_52w_avg * 7) if pd.notna(imports_52w_avg) else 0
    exports_dev = (latest["exports"] * 7) - (exports_52w_avg * 7) if pd.notna(exports_52w_avg) else 0

    # Forecast logic
    # got weights from ingestion
    seasonal_base = latest["seasonal_avg"]

    runs_adjustment = -0.55877571 * runs_dev
    imports_adjustment = 0.54808454 * imports_dev
    exports_adjustment = -0.30471984 * exports_dev

    predicted_surprise = runs_adjustment + imports_adjustment + exports_adjustment
    forecast_inventory_change = latest["seasonal_avg"] + predicted_surprise

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

def attach_forecast_context(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add rolling context columns that help interpret the forecast.
    """
    out = df.copy()

    out["runs_52w_avg"] = out["refinery_runs"].rolling(52, min_periods=12).mean()
    out["imports_52w_avg"] = out["imports"].rolling(52, min_periods=12).mean()
    out["exports_52w_avg"] = out["exports"].rolling(52, min_periods=12).mean()

    out["runs_dev"] = out["refinery_runs"] - out["runs_52w_avg"]
    out["imports_dev"] = out["imports"] - out["imports_52w_avg"]
    out["exports_dev"] = out["exports"] - out["exports_52w_avg"]

    return out
