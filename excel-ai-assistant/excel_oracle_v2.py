import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob

# === PATHS ===
REPORTS = r"C:\Users\NEGAHDN\Downloads\test projects\excel-ai-assistant\Reports"
CHARTS = r"C:\Users\NEGAHDN\Downloads\test projects\excel-ai-assistant\Charts"
SUMMARY = r"C:\Users\NEGAHDN\Downloads\test projects\excel-ai-assistant\Oracle_Summary.txt"

os.makedirs(REPORTS, exist_ok=True)
os.makedirs(CHARTS, exist_ok=True)

# === DATA LOADER ===
def load_numeric_data(path):
    """Read all sheets, start at row 14, keep numeric columns only."""
    data_frames = []
    try:
        engine = "pyxlsb" if path.endswith(".xlsb") else None
        xls = pd.ExcelFile(path, engine=engine)
        for sheet in xls.sheet_names:
            try:
                df = pd.read_excel(xls, sheet_name=sheet, header=13)
                df.columns = df.columns.astype(str).str.strip()  # clean headers
                numeric = df.select_dtypes(include=np.number)
                if not numeric.empty:
                    numeric["__sheet__"] = sheet
                    data_frames.append(numeric)
            except Exception as e:
                print(f"⚠️  Error in {os.path.basename(path)} [{sheet}]: {e}")
    except Exception as e:
        print(f"⚠️ Could not read {os.path.basename(path)}: {e}")
    return pd.concat(data_frames, ignore_index=True) if data_frames else pd.DataFrame()

# === ANALYSIS ENGINE ===
def analyze_trends(folder):
    print(f"🔮 Summoning the Oracle for reports in {os.path.basename(folder)}...\n")
    summaries = []
    trend_summary = []

    for file in sorted(os.listdir(folder)):
        if file.endswith((".xlsb", ".xlsx", ".xls")):
            path = os.path.join(folder, file)
            print(f"📘 Reading {file}")
            df = load_numeric_data(path)

            if df.empty:
                print(f"😶 {file} → no numeric data\n")
                continue

            numeric_df = df.select_dtypes(include=np.number)
            if numeric_df.empty:
                print(f"😶 {file} → no numeric columns\n")
                continue

            mean_vals = numeric_df.mean().dropna()
            top_high = mean_vals.sort_values(ascending=False).head(3)
            top_low = mean_vals.sort_values(ascending=True).head(3)

            summaries.append(f"\n=== {file} ===")
            summaries.append(f"Top ↑ Metrics:\n{top_high.to_string()}")
            summaries.append(f"\nTop ↓ Metrics:\n{top_low.to_string()}\n")

            # === Correlation heatmap ===
            try:
                corr = numeric_df.corr().abs()
                plt.figure(figsize=(8, 6))
                sns.heatmap(corr, cmap="YlGnBu")
                plt.title(f"Correlation Heatmap – {file}")
                plt.tight_layout()
                plt.savefig(os.path.join(CHARTS, f"{file}_heatmap.png"))
                plt.close()
            except Exception as e:
                print(f"⚠️ Could not plot heatmap for {file}: {e}")

            trend_summary.append(mean_vals)

    if not trend_summary:
        print("😶 Oracle still sees no numbers anywhere.")
        return

    # === Combine all months ===
    all_trends = pd.concat(trend_summary, axis=1)
    all_trends.columns = [f.split('.')[0] for f in sorted(os.listdir(folder)) if f.endswith(('.xlsb', '.xlsx', '.xls'))]

    # === Monthly Trend Line Chart ===
    plt.figure(figsize=(10, 6))
    all_trends.T.plot(ax=plt.gca())
    plt.title("📈 Monthly Trend Overview (Mean of Numeric Metrics)")
    plt.ylabel("Average Value")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS, "Monthly_Trends.png"))
    plt.close()

    # === Save Text Summary ===
    text = "\n".join(summaries)
    blob = TextBlob(text).correct()
    with open(SUMMARY, "w", encoding="utf-8") as f:
        f.write(str(blob))

    print(f"\n✅ Oracle finished reading all data!")
    print(f"🧠 Summary → {SUMMARY}")
    print(f"📊 Charts → {CHARTS}")

# === RUN ===
if __name__ == "__main__":
    analyze_trends(REPORTS)
