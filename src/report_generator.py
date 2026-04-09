import os
from datetime import datetime
from plotly.io import write_image
from src.charts import plot_inventory_vs_seasonal, plot_inventory_surprise, plot_balance_components, plot_forecast_vs_actual, plot_balance_error

def create_output_folder(base_path="outputs/charts"):
    today = datetime.today().strftime("%Y-%m-%d")
    folder_path = os.path.join(base_path, today)

    os.makedirs(folder_path, exist_ok=True)

    return folder_path


def save_figure(fig, path):
    write_image(fig, path, width=1200, height=600, scale=2)


def generate_all_charts(df, forecast_log_df=None):
    folder = create_output_folder()

    print(f"Saving charts to: {folder}")

    # 1. Inventory vs Seasonal
    fig1 = plot_inventory_vs_seasonal(df)
    save_figure(fig1, f"{folder}/inventory_vs_seasonal.png")

    # 2. Inventory Surprise
    fig2 = plot_inventory_surprise(df)
    save_figure(fig2, f"{folder}/inventory_surprise.png")

    # 3. Supply vs Demand
    fig3 = plot_balance_components(df)
    save_figure(fig3, f"{folder}/balance_components.png")

    # 4. Forecast vs Actual (only if log exists)
    if forecast_log_df is not None:
        fig4 = plot_forecast_vs_actual(forecast_log_df)
        save_figure(fig4, f"{folder}/forecast_vs_actual.png")

    # 5. Balance Error
    fig5 = plot_balance_error(df)
    save_figure(fig5, f"{folder}/balance_error.png")

    print("All charts saved successfully.")