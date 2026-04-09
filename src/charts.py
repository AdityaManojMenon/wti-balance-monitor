import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# ── Bloomberg Dark Theme AI generated ────────────────────────────────────────────────────

BBG = dict(
    bg      = "#0A0A0A",
    panel   = "#111111",
    grid    = "#222222",
    border  = "#333333",
    text    = "#E8E8E8",
    subtext = "#888888",
    orange  = "#FF6600",
    cyan    = "#00BFFF",
    green   = "#00FF9F",
    red     = "#FF3B3B",
    yellow  = "#FFD700",
    white   = "#FFFFFF",
)

FONT = dict(family="'Courier New', monospace", color=BBG["text"])


def _base_layout(title: str, xlabel: str = "", ylabel: str = "") -> dict:
    """Return a Bloomberg-style base layout dict."""
    return dict(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(family=FONT["family"], size=16, color=BBG["orange"]),
            x=0.0, xanchor="left", pad=dict(l=10, t=10),
        ),
        paper_bgcolor=BBG["bg"],
        plot_bgcolor=BBG["panel"],
        font=FONT,
        xaxis=dict(
            title=xlabel,
            gridcolor=BBG["grid"],
            gridwidth=1,
            linecolor=BBG["border"],
            tickfont=dict(color=BBG["subtext"], size=10),
            title_font=dict(color=BBG["subtext"], size=11),
            showspikes=True,
            spikecolor=BBG["orange"],
            spikethickness=1,
            spikedash="dot",
        ),
        yaxis=dict(
            title=ylabel,
            gridcolor=BBG["grid"],
            gridwidth=1,
            linecolor=BBG["border"],
            tickfont=dict(color=BBG["subtext"], size=10),
            title_font=dict(color=BBG["subtext"], size=11),
            showspikes=True,
            spikecolor=BBG["orange"],
            spikethickness=1,
            spikedash="dot",
            zeroline=True,
            zerolinecolor=BBG["border"],
            zerolinewidth=1,
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor=BBG["border"],
            borderwidth=1,
            font=dict(color=BBG["text"], size=11),
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor=BBG["panel"],
            bordercolor=BBG["orange"],
            font=dict(color=BBG["text"], family=FONT["family"]),
        ),
        margin=dict(l=60, r=30, t=60, b=50),
    )


def _trim_2y(df: pd.DataFrame) -> pd.DataFrame:
    """FIX 1: Limit to rolling 2-year window for all plots."""
    return df[df.index >= df.index.max() - pd.DateOffset(years=2)]


# ── 1. Inventory vs Seasonal Range ─────────────────────────────────────────

def plot_inventory_vs_seasonal(df):
    df = df.copy()

    # FIX 4: Compute seasonal band from FULL history first (wider sample = truer range)
    df["week"] = df.index.isocalendar().week
    seasonal_min = df.groupby("week")["stocks"].transform("min")
    seasonal_max = df.groupby("week")["stocks"].transform("max")
    df["seasonal_min"] = seasonal_min
    df["seasonal_max"] = seasonal_max

    # FIX 1 + FIX 4: Trim display to recent 2 years only
    df_recent = _trim_2y(df)

    fig = go.Figure()

    # Seasonal band — full-history stats, 2Y display window
    fig.add_trace(go.Scatter(
        x=df_recent.index, y=df_recent["seasonal_max"],
        mode="lines", line=dict(width=0),
        name="Seasonal Max", showlegend=False,
        hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=df_recent.index, y=df_recent["seasonal_min"],
        mode="lines", line=dict(width=0),
        fill="tonexty",
        fillcolor="rgba(0,191,255,0.12)",
        name="Seasonal Range (5Y)",
        hoverinfo="skip",
    ))

    # Current stocks line
    fig.add_trace(go.Scatter(
        x=df_recent.index, y=df_recent["stocks"],
        mode="lines",
        line=dict(color=BBG["orange"], width=2),
        name="Current Stocks",
    ))

    fig.update_layout(
        **_base_layout(
            "US CRUDE INVENTORY vs SEASONAL RANGE",
            ylabel="Stocks (MMbbl)",
        )
    )
    return fig


# ── 2. Inventory Surprise (Change vs Seasonal Avg) ─────────────────────────

def plot_inventory_surprise(df):
    df = df.copy()

    # FIX 1: 2-year window
    df = _trim_2y(df)

    # FIX 2: Smooth noisy weekly series
    df["inventory_change_smooth"] = df["inventory_change"].rolling(4).mean()

    fig = go.Figure()

    # FIX 3: Smoothed line replaces cluttered bars
    fig.add_trace(go.Scatter(
        x=df.index, y=df["inventory_change_smooth"],
        mode="lines",
        line=dict(color=BBG["cyan"], width=2),
        name="Actual (4W Avg)",
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df["seasonal_avg"],
        mode="lines",
        line=dict(color=BBG["yellow"], width=1.5, dash="dash"),
        name="Seasonal Avg",
    ))

    # Shaded divergence area between smoothed actual and seasonal avg
    fig.add_trace(go.Scatter(
        x=df.index, y=df["inventory_change_smooth"],
        mode="lines", line=dict(width=0),
        fill="tonexty",
        fillcolor="rgba(0,191,255,0.08)",
        showlegend=False,
        hoverinfo="skip",
    ))

    fig.update_layout(
        **_base_layout(
            "INVENTORY CHANGE vs SEASONAL AVERAGE",
            ylabel="Change (MMbbl)",
        )
    )
    return fig


# ── 3. Supply vs Demand Balance ────────────────────────────────────────────

def plot_balance_components(df):
    df = df.copy()

    # FIX 1: 2-year window
    df = _trim_2y(df)

    # FIX 5: Smooth high-frequency noise in supply and demand
    df["supply_smooth"] = (df["production"] + df["imports"]).rolling(4).mean()
    df["demand_smooth"] = (df["exports"] + df["refinery_runs"]).rolling(4).mean()
    net_balance = df["supply_smooth"] - df["demand_smooth"]

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.7, 0.3],
        vertical_spacing=0.06,
    )

    # FIX 5: Smoothed supply and demand lines
    fig.add_trace(go.Scatter(
        x=df.index, y=df["supply_smooth"],
        mode="lines",
        line=dict(color=BBG["green"], width=2),
        name="Total Supply (4W Avg)",
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df.index, y=df["demand_smooth"],
        mode="lines",
        line=dict(color=BBG["red"], width=2),
        name="Total Demand (4W Avg)",
    ), row=1, col=1)

    # Net balance bar sub-panel
    bar_colors = [BBG["green"] if v >= 0 else BBG["red"] for v in net_balance]
    fig.add_trace(go.Bar(
        x=df.index, y=net_balance,
        marker_color=bar_colors,
        opacity=0.75,
        name="Net Balance",
    ), row=2, col=1)

    base = _base_layout("SUPPLY vs DEMAND BALANCE COMPONENTS")
    base["yaxis"]  = {**base["yaxis"], "title": "MMbbl/d"}
    base["yaxis2"] = {
        **base["yaxis"],
        "title": "Net (MMbbl/d)",
        "gridcolor": BBG["grid"],
        "zeroline": True,
        "zerolinecolor": BBG["border"],
    }
    base["xaxis2"] = {**base["xaxis"]}
    fig.update_layout(**base)
    return fig


# ── 4. Forecast vs Actual ──────────────────────────────────────────────────

def plot_forecast_vs_actual(log_df):
    log_df = log_df.copy()

    # FIX 1: 2-year window (index by forecast_date temporarily)
    log_df = log_df.set_index("forecast_date")
    log_df = _trim_2y(log_df)
    log_df = log_df.reset_index()

    error = log_df["actual_inventory_change"] - log_df["forecast_inventory_change"]

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.65, 0.35],
        vertical_spacing=0.06,
    )

    fig.add_trace(go.Scatter(
        x=log_df["forecast_date"], y=log_df["forecast_inventory_change"],
        mode="lines",
        line=dict(color=BBG["cyan"], width=1.5, dash="dot"),
        name="Forecast",
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=log_df["forecast_date"], y=log_df["actual_inventory_change"],
        mode="lines",
        line=dict(color=BBG["orange"], width=2),
        name="Actual",
    ), row=1, col=1)

    err_colors = [BBG["green"] if v >= 0 else BBG["red"] for v in error]
    fig.add_trace(go.Bar(
        x=log_df["forecast_date"], y=error,
        marker_color=err_colors,
        opacity=0.7,
        name="Error (Actual − Forecast)",
    ), row=2, col=1)

    base = _base_layout("FORECAST vs ACTUAL INVENTORY CHANGE")
    base["yaxis"]  = {**base["yaxis"], "title": "Change (MMbbl)"}
    base["yaxis2"] = {**base["yaxis"], "title": "Error (MMbbl)"}
    base["xaxis2"] = {**base["xaxis"]}
    fig.update_layout(**base)
    return fig


# ── 5. Balance Model Error ─────────────────────────────────────────────────

def plot_balance_error(df):
    df = df.copy()

    # FIX 1: 2-year window
    df = _trim_2y(df)

    # FIX 2 + FIX 6: Compute smooth signal and keep raw for noise context
    df["balance_error_smooth"] = df["balance_error"].rolling(4).mean()

    # ±1σ band from rolling std of raw error
    rolling_sd = df["balance_error"].rolling(52).std()

    fig = go.Figure()

    # ±1σ shaded band
    fig.add_trace(go.Scatter(
        x=df.index, y=rolling_sd,
        mode="lines", line=dict(width=0),
        name="+1σ", showlegend=False, hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=-rolling_sd,
        mode="lines", line=dict(width=0),
        fill="tonexty",
        fillcolor="rgba(255,102,0,0.07)",
        name="±1σ Band",
        hoverinfo="skip",
    ))

    # FIX 6: Raw error faint in background — shows true noise
    fig.add_trace(go.Scatter(
        x=df.index, y=df["balance_error"],
        mode="lines",
        line=dict(color=BBG["orange"], width=1),
        opacity=0.2,
        name="Raw Error",
    ))

    # FIX 6: Smoothed signal on top — dominant, readable trend
    fig.add_trace(go.Scatter(
        x=df.index, y=df["balance_error_smooth"],
        mode="lines",
        line=dict(color=BBG["orange"], width=2),
        name="4W Avg Error",
    ))

    fig.add_hline(
        y=0,
        line=dict(color=BBG["border"], width=1, dash="dash"),
    )

    fig.update_layout(
        **_base_layout(
            "BALANCE MODEL ERROR",
            ylabel="Error (MMbbl/d)",
        )
    )
    return fig