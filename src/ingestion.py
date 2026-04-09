import requests
import pandas as pd
import os
from dotenv import load_dotenv
from sklearn.linear_model import LinearRegression
from src.seasonal import compute_seasonal_baseline, compute_inventory_surprise
from src.forecast import attach_forecast_context

load_dotenv()

API_KEY = os.getenv("EIA_API_KEY")

SERIES = {
    "stocks": "PET.WCESTUS1.W",
    "production": "PET.WCRFPUS2.W",
    "imports": "PET.WCRIMUS2.W",
    "exports": "PET.WCREXUS2.W",
    "refinery_runs": "PET.WCRRIUS2.W",
}

def fetch_eia_data(series_id):

    url = f"https://api.eia.gov/v2/seriesid/{series_id}?api_key={API_KEY}"

    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"API request failed: {response.text}")
    
    data = response.json()
    try:
        records = data["response"]["data"]
    except KeyError:
        raise Exception(f"Unexpected API response: {data}")
    df = pd.DataFrame(records)
    df = df.rename(columns={
        "period": "date",
        "value": "value"
    })

    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    return df[["date", "value"]].dropna()

def fetch_all():
    dfs = []

    for name,series_id in SERIES.items():
        print(f"Fetching {name}...")
        df = fetch_eia_data(series_id)
        df = df.rename(columns = {"value": name})
        dfs.append(df)
    
    # Merge all series
    df_merged = dfs[0]
    for df in dfs[1:]:
        df_merged = df_merged.merge(df, on = "date", how = "outer")
    
    df_merged = df_merged.sort_values("date")
    df_merged = df_merged.set_index("date").ffill()
    df_merged["inventory_change"] = df_merged["stocks"].diff()
    df_merged["implied_balance"] = (df_merged["production"] + df_merged["imports"] - df_merged["exports"] - df_merged["refinery_runs"])
    df_merged["balance_error"] = df_merged["inventory_change"] - df_merged["implied_balance"]

    return df_merged

if __name__ == "__main__":
    df = fetch_all()
    print(df.tail())

    seasonal = compute_seasonal_baseline(df)
    df = compute_inventory_surprise(df, seasonal)
    df = attach_forecast_context(df)

    print("\n=========================")
    print(df.tail().reset_index("date"))

    df["runs_weekly"] = df["refinery_runs"] * 7
    df["imports_weekly"] = df["imports"] * 7
    df["exports_weekly"] = df["exports"] * 7

    df["runs_dev"] = df["runs_weekly"] - df["runs_weekly"].rolling(52).mean()
    df["imports_dev"] = df["imports_weekly"] - df["imports_weekly"].rolling(52).mean()
    df["exports_dev"] = df["exports_weekly"] - df["exports_weekly"].rolling(52).mean()

    train_df = df.iloc[:-1]

    features = train_df[["runs_dev", "imports_dev", "exports_dev"]].dropna()
    target = train_df["inventory_change"].loc[features.index]

    model = LinearRegression()
    model.fit(features, target)

    print("Coefficients:", model.coef_)
    print("Intercept:", model.intercept_)