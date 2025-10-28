import os
import pandas as pd
import numpy as np
from textblob import TextBlob

FOLDER = r"C:\Users\NEGAHDN\Downloads\test projects\excel-insights\Reports"
OUTPUT = r"C:\Users\NEGAHDN\Downloads\test projects\excel-insights\Excel_Insights_Report.xlsx"
SUMMARY_FILE = r"C:\Users\NEGAHDN\Downloads\test projects\excel-insights\Summary.txt"

def merge_excels(folder):
    data_frames = []
    for file in os.listdir(folder):
        if file.endswith((".xlsb", ".xls")):
            path = os.path.join(folder, file)
            print(f"📂 Reading {file}")
            try:
                df = pd.read_excel(path)
                df["Source_File"] = file
                data_frames.append(df)
            except Exception as e:
                print(f"⚠️ Skipped {file}: {e}")
    if not data_frames:
        print("⚠️ No Excel files found.")
        return pd.DataFrame()
    merged = pd.concat(data_frames, ignore_index=True)
    return merged

def generate_ai_summary(df):
    if df.empty:
        return "No data available to summarize."

    text = []
    numeric_df = df.select_dtypes(include=np.number)

    # General stats
    avg = numeric_df.mean().mean()
    total_sum = numeric_df.sum().sum()
    text.append(f"The dataset contains {len(df)} rows across {len(df.columns)} columns.")
    text.append(f"Average value across numeric columns is {avg:.2f}.")
    text.append(f"Total sum of all numeric data points is {total_sum:,.0f}.")

    # Find top correlations
    corr = numeric_df.corr().abs()
    high_corr = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
    pairs = high_corr.stack().sort_values(ascending=False)
    if not pairs.empty:
        top_pair, strength = pairs.index[0], pairs.iloc[0]
        text.append(f"The strongest correlation is between '{top_pair[0]}' and '{top_pair[1]}' (r={strength:.2f}).")

    # Find column with most variation
    std_col = numeric_df.std().idxmax()
    text.append(f"'{std_col}' shows the highest variability among numeric fields.")

    # Add "AI style" interpretation
    interpretation = f"Overall, the data suggests a moderate variability with key relationships among major performance indicators. Values appear generally stable with some outliers."
    text.append(interpretation)

    blob = TextBlob(" ".join(text))
    ai_tone = blob.correct()  # simple grammar cleanup

    return str(ai_tone)

def save_results(df, summary_text):
    with pd.ExcelWriter(OUTPUT, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Merged Data")
        numeric_summary = df.describe(include=[np.number])
        numeric_summary.to_excel(writer, sheet_name="Numeric Summary")

    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        f.write(summary_text)

    print(f"✅ Excel insights saved to {OUTPUT}")
    print(f"🧠 AI-style summary saved to {SUMMARY_FILE}")

if __name__ == "__main__":
    os.makedirs(FOLDER, exist_ok=True)
    df = merge_excels(FOLDER)
    if not df.empty:
        summary = generate_ai_summary(df)
        save_results(df, summary)
        print("\n📜 AI Summary:\n", summary)
    else:
        print("💤 No Excel data found — add some files and rerun.")
