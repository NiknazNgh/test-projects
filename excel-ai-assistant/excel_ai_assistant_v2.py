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
    name = col.lower()
    if any(x in name for x in ["cost","price","budget","expense"]): return "Finance"
    if any(x in name for x in ["flow","pressure","rate","volume"]): return "Operations"
    if any(x in name for x in ["chlorine","ph","turbidity","chemical"]): return "Chemistry"
    if any(x in name for x in ["energy","power","kw","kwh"]): return "Energy"
    if any(x in name for x in ["date","month","time"]): return "Date"
    return "Other"

def recommend_chart(dtype, topic):
    if dtype == "number":
        if topic in ["Finance","Operations","Energy"]: return "Line"
        if topic == "Chemistry": return "Scatter"
        return "Histogram"
    elif dtype == "category":
        return "Bar"
    return "CountPlot"

def analyze_sheet(df, file_name, sheet_name):
    """Analyze a single sheet and create summary + charts"""
    summary_lines = [f"\n📄 Sheet: {sheet_name}"]

    for col in df.columns:
        topic = classify_column(col)
        dtype = "number" if pd.api.types.is_numeric_dtype(df[col]) else "category"
        chart_type = recommend_chart(dtype, topic)
        summary_lines.append(f"• {col}: {topic} data → {chart_type} chart")

        # Try plotting
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
            plt.title(f"{file_name} - {sheet_name} - {col}")
            plt.tight_layout()
            safe_name = f"{os.path.splitext(file_name)[0]}_{sheet_name}_{col}".replace("/", "_").replace("\\", "_")
            plt.savefig(os.path.join(CHARTS, f"{safe_name}.png"))
            plt.close()
        except Exception as e:
            summary_lines.append(f"⚠️ Plot error for {col}: {e}")

    # Add numeric insights
    numeric_cols = df.select_dtypes(include=np.number)
    if not numeric_cols.empty:
        mean_val = numeric_cols.mean().mean()
        std_val = numeric_cols.std().mean()
        corr_val = numeric_cols.corr().abs().mean().mean()
        summary_lines.append(f"Mean={mean_val:.2f}, Std={std_val:.2f}, Avg Corr={corr_val:.2f}")

    return "\n".join(summary_lines)

def analyze_excel(path):
    """Open each sheet and process"""
    file_name = os.path.basename(path)
    print(f"📘 Analyzing {file_name}")
    results = []

    try:
        if file_name.lower().endswith(".xlsb"):
            xls = pd.ExcelFile(path, engine="pyxlsb")
        else:
            xls = pd.ExcelFile(path)

        for sheet in xls.sheet_names:
            try:
                df = pd.read_excel(xls, sheet_name=sheet)
                if not df.empty:
                    results.append(analyze_sheet(df, file_name, sheet))
            except Exception as e:
                results.append(f"⚠️ Failed to process sheet {sheet}: {e}")
    except Exception as e:
        results.append(f"⚠️ Could not open {file_name}: {e}")

    blob = TextBlob("\n".join(results)).correct()
    return str(blob)

if __name__ == "__main__":
    all_reports = []
    for file in os.listdir(REPORTS):
        if file.lower().endswith((".xlsx",".xls",".xlsb")):
            path = os.path.join(REPORTS, file)
            summary = analyze_excel(path)
            all_reports.append(f"\n=== {file} ===\n{summary}\n")

    if all_reports:
        with open(SUMMARY, "w", encoding="utf-8") as f:
            f.write("\n".join(all_reports))
        print(f"\n✅ Analysis complete. Charts → {CHARTS}")
        print(f"🧠 Summary → {SUMMARY}")
    else:
        print("💤 No Excel files found. Add some to the Reports folder and rerun.")
