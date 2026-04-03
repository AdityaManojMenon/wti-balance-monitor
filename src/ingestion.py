import requests
import pandas as pd
import os
from dotenv import load_dotenv

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

    return df_merged

if __name__ == "__main__":
    df = fetch_all()
    print(df.tail())
