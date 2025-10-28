import os
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import seaborn as sns
from openpyxl import Workbook

# === PATHS ===
REPORTS = r"C:\Users\NEGAHDN\Downloads\test projects\excel-ai-assistant\Reports"
OUTPUT_EXCEL = r"C:\Users\NEGAHDN\Downloads\test projects\excel-ai-assistant\Excel_Dashboard.xlsx"
CHARTS = r"C:\Users\NEGAHDN\Downloads\test projects\excel-ai-assistant\Charts"

os.makedirs(REPORTS, exist_ok=True)
os.makedirs(CHARTS, exist_ok=True)

# === LOAD & CLEAN ===
def load_all_data(folder):
    """Read all Excel reports, scan 'Report' and 'Data' sheets, and extract numeric columns starting from row 14."""
    frames = []
    for file in os.listdir(folder):
        if file.endswith((".xlsb", ".xlsx", ".xls")):
            engine = "pyxlsb" if file.endswith(".xlsb") else None
            full_path = os.path.join(folder, file)
            try:
                xls = pd.ExcelFile(full_path, engine=engine)
                for sheet in xls.sheet_names:
                    if sheet.lower() in ("report", "data"):
                        try:
                            df = pd.read_excel(xls, sheet_name=sheet, header=13)
                            df.columns = df.columns.astype(str).str.strip()
                            numeric = df.select_dtypes(include=np.number)
                            if not numeric.empty:
                                numeric["Month"] = (
                                    file.split("_")[-1]
                                    .replace(".xlsb", "")
                                    .replace(".xlsx", "")
                                    .replace(".xls", "")
                                )
                                frames.append(numeric)
                        except Exception as e:
                            print(f"⚠️ Sheet {sheet} in {file}: {e}")
            except Exception as e:
                print(f"⚠️ Could not open {file}: {e}")
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

# === ANOMALY DETECTION ===
def detect_anomalies(df):
    """Flag anomalies using z-score."""
    zscores = (df - df.mean()) / df.std(ddof=0)
    anomalies = (abs(zscores) > 2).any(axis=1)
    return anomalies

# === FORECASTING ===
def forecast_next_month(df):
    """Predict next month's mean for each numeric column."""
    forecast = {}
    months = np.arange(len(df))
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            try:
                model = LinearRegression()
                X = months.reshape(-1, 1)
                y = df[col].fillna(method="ffill")
                model.fit(X, y)
                next_val = model.predict([[len(df)]])[0]
                forecast[col] = round(next_val, 2)
            except Exception:
                pass
    return forecast

# === EXPORT DASHBOARD ===
def export_dashboard(kpis, forecasts, anomalies):
    """Save KPIs, forecasts, and anomalies into a single Excel dashboard."""
    with pd.ExcelWriter(OUTPUT_EXCEL, engine="openpyxl") as writer:
        kpis.to_excel(writer, sheet_name="KPI Summary", index=False)
        if forecasts:
            pd.DataFrame([forecasts]).T.rename(columns={0: "Predicted Next Month"}).to_excel(
                writer, sheet_name="Forecasts"
            )
        if not anomalies.empty:
            anomalies.to_excel(writer, sheet_name="Anomalies", index=False)
    print(f"✅ Dashboard saved → {OUTPUT_EXCEL}")

# === MAIN PIPELINE ===
def main():
    print("📊 Loading all reports...")
    df = load_all_data(REPORTS)
    if df.empty:
        print("⚠️ No numeric data found.")
        return

    print(f"✅ Loaded {len(df)} rows from {len(os.listdir(REPORTS))} files")

    # === KPI summary per month ===
    kpis = df.groupby("Month").agg(["mean", "min", "max", "std"]).round(2)
    kpis.columns = ['_'.join(col) for col in kpis.columns]

    # === Detect anomalies ===
    df["Anomaly"] = detect_anomalies(df.select_dtypes(include=np.number))
    anomalies = df[df["Anomaly"]]

    # === Forecast next month ===
    pivot = df.groupby("Month").mean().T
    forecasts = forecast_next_month(pivot.T)

    # === Trend Chart ===
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=pivot)
    plt.title("Monthly Trends Across Metrics")
    plt.xlabel("Month")
    plt.ylabel("Average Values")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS, "Monthly_Trends.png"))
    plt.close()

    # === Export Excel Dashboard ===
    export_dashboard(kpis.reset_index(), forecasts, anomalies)

    print(f"📊 Charts → {CHARTS}")
    print("✅ Process completed successfully.")

if __name__ == "__main__":
    main()
