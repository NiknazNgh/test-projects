import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob

REPORTS = r"C:\Users\NEGAHDN\Downloads\test projects\excel-ai-assistant\Reports"
CHARTS = r"C:\Users\NEGAHDN\Downloads\test projects\excel-ai-assistant\Charts"
SUMMARY = r"C:\Users\NEGAHDN\Downloads\test projects\excel-ai-assistant\Summary.txt"

os.makedirs(REPORTS, exist_ok=True)
os.makedirs(CHARTS, exist_ok=True)

def classify_column(col):
    """Roughly guess what a column represents based on its name."""
    name = col.lower()
    if any(x in name for x in ["cost","price","budget","expense"]): return "Finance"
    if any(x in name for x in ["flow","pressure","rate","volume"]): return "Operations"
    if any(x in name for x in ["chlorine","ph","turbidity","chemical"]): return "Chemistry"
    if any(x in name for x in ["energy","power","kw","kwh"]): return "Energy"
    if any(x in name for x in ["date","month","time"]): return "Date"
    return "Other"

def recommend_chart(dtype, topic):
    """Suggest chart type."""
    if dtype == "number":
        if topic in ["Finance","Operations","Energy"]: return "Line"
        if topic == "Chemistry": return "Scatter"
        return "Histogram"
    elif dtype == "category":
        return "Bar"
    else:
        return "CountPlot"

def analyze_excel(path):
    print(f"📄 Analyzing {os.path.basename(path)}")
    df = pd.read_excel(path)
    summary_lines = []

    for col in df.columns:
        topic = classify_column(col)
        dtype = "number" if pd.api.types.is_numeric_dtype(df[col]) else "category"
        chart_type = recommend_chart(dtype, topic)
        summary_lines.append(f"• {col}: {topic} data → recommended chart: {chart_type}")

        # Auto-plot
        plt.figure(figsize=(6,4))
        try:
            if chart_type == "Line":
                plt.plot(df[col])
            elif chart_type == "Scatter":
                sns.scatterplot(x=df.index, y=df[col])
            elif chart_type == "Histogram":
                sns.histplot(df[col].dropna(), kde=True)
            elif chart_type == "Bar":
                df[col].value_counts().head(10).plot(kind="bar")
            elif chart_type == "CountPlot":
                sns.countplot(x=df[col])
            plt.title(f"{col} ({chart_type})")
            plt.tight_layout()
            plt.savefig(os.path.join(CHARTS, f"{os.path.basename(path)}_{col}.png"))
            plt.close()
        except Exception as e:
            summary_lines.append(f"⚠️ Could not plot {col}: {e}")

    # basic numeric summary
    numeric_cols = df.select_dtypes(include=np.number)
    if not numeric_cols.empty:
        mean_val = numeric_cols.mean().mean()
        corr_val = numeric_cols.corr().abs().mean().mean()
        summary_lines.append(f"Average numeric mean: {mean_val:.2f}, avg correlation: {corr_val:.2f}")

    text = "\n".join(summary_lines)
    blob = TextBlob(text).correct()
    return str(blob)

if __name__ == "__main__":
    full_report = []
    for file in os.listdir(REPORTS):
        if file.endswith((".xlsx",".xls")):
            summary = analyze_excel(os.path.join(REPORTS,file))
            full_report.append(f"\n=== {file} ===\n{summary}\n")

    if full_report:
        with open(SUMMARY,"w",encoding="utf-8") as f:
            f.write("\n".join(full_report))
        print(f"\n✅ Analysis complete. Charts → {CHARTS}")
        print(f"🧠 Summary → {SUMMARY}")
    else:
        print("💤 No Excel files found. Add some to the Reports folder and rerun.")
