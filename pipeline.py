import os
import pandas as pd

from src.ingestion import fetch_all
from src.seasonal import compute_seasonal_baseline, compute_inventory_surprise
from src.forecast import generate_forecast, attach_forecast_context
from src.report_generator import generate_all_charts



PROCESSED_DIR = "data/processed"
FORECAST_LOG_PATH = os.path.join(PROCESSED_DIR, "forecast_log.csv")
LATEST_SNAPSHOT_PATH = os.path.join(PROCESSED_DIR, "latest_balance_snapshot.csv")


def ensure_dirs():
    os.makedirs(PROCESSED_DIR, exist_ok=True)


def log_forecast(forecast: dict, filepath: str = FORECAST_LOG_PATH):
    new_row = pd.DataFrame([forecast])

    if os.path.exists(filepath):
        existing = pd.read_csv(filepath)
        combined = pd.concat([existing, new_row], ignore_index=True)
    else:
        combined = new_row

    combined.to_csv(filepath, index=False)


def save_latest_snapshot(df: pd.DataFrame, filepath: str = LATEST_SNAPSHOT_PATH):
    df.reset_index().to_csv(filepath, index=False)


def main():
    ensure_dirs()

    print("Fetching and preparing crude balance data...")
    df = fetch_all()

    seasonal = compute_seasonal_baseline(df)
    df = compute_inventory_surprise(df, seasonal)
    df = attach_forecast_context(df)

    forecast = generate_forecast(df)

    generate_all_charts(df)

    print("\n=== LATEST FORECAST ===")
    for key, value in forecast.items():
        print(f"{key}: {value}")

    log_forecast(forecast)
    save_latest_snapshot(df.tail(20))

    print(f"\nSaved forecast log to: {FORECAST_LOG_PATH}")
    print(f"Saved latest snapshot to: {LATEST_SNAPSHOT_PATH}")


if __name__ == "__main__":
    main()