import pandas as pd

def compute_seasonal_baseline(df, years=5):
    df = df.copy()

    df["week"] = df.index.isocalendar().week

    # Filter last N years
    cutoff = df.index.max() - pd.DateOffset(years=years)
    df_recent = df[df.index >= cutoff]

    seasonal = (
        df_recent.groupby("week")["inventory_change"]
        .mean()
        .rename("seasonal_avg")
    )

    return seasonal

def compute_inventory_surprise(df, seasonal):
    df = df.copy()
    df["week"] = df.index.isocalendar().week

    df["seasonal_avg"] = df["week"].map(seasonal)

    df["inventory_surprise"] = df["inventory_change"] - df["seasonal_avg"]

    df["signal"] = df["inventory_surprise"].apply(lambda x: "Bullish" if x < 0 else "Bearish")

    return df