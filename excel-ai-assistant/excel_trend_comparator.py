import os, re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob

REPORTS = r"C:\Users\NEGAHDN\Downloads\test projects\excel-ai-assistant\Reports"
CHARTS  = r"C:\Users\NEGAHDN\Downloads\test projects\excel-ai-assistant\Charts\Trends"
OUTPUT  = r"C:\Users\NEGAHDN\Downloads\test projects\excel-ai-assistant\Trend_Report.xlsx"
SUMMARY = r"C:\Users\NEGAHDN\Downloads\test projects\excel-ai-assistant\AI_Trend_Summary.txt"

os.makedirs(REPORTS, exist_ok=True)
os.makedirs(CHARTS, exist_ok=True)

# --- helpers ---------------------------------------------------------

month_map = {m.lower(): i for i,m in enumerate(
    ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"], start=1)}

def extract_month(fname):
    for m in month_map:
        if m in fname.lower():
            return month_map[m]
    # fallback to number if present
    nums = re.findall(r"\d+", fname)
    return int(nums[0]) if nums else 0

def read_any_excel(path):
    if path.lower().endswith(".xlsb"):
        return pd.read_excel(path, engine="pyxlsb")
    return pd.read_excel(path)

# --- main analysis ---------------------------------------------------

def compare_trends():
    files = [f for f in os.listdir(REPORTS)
             if f.lower().endswith((".xlsx",".xls",".xlsb"))]
    if not files:
        print("💤 No Excel files found.")
        return

    files.sort(key=extract_month)
    trend_records, ai_lines = [], []

    for i in range(1, len(files)):
        f_prev, f_curr = files[i-1], files[i]
        print(f"📊 Comparing {f_prev} → {f_curr}")

        try:
            df1, df2 = read_any_excel(os.path.join(REPORTS, f_prev)), \
                       read_any_excel(os.path.join(REPORTS, f_curr))
        except Exception as e:
            ai_lines.append(f"⚠️ Failed reading {f_curr}: {e}")
            continue

        # numeric intersection
        common_cols = [c for c in df1.columns if c in df2.columns
                       and pd.api.types.is_numeric_dtype(df1[c])
                       and pd.api.types.is_numeric_dtype(df2[c])]
        if not common_cols:
            ai_lines.append(f"No numeric overlap between {f_prev} and {f_curr}.")
            continue

        for c in common_cols:
            v1, v2 = df1[c].mean(skipna=True), df2[c].mean(skipna=True)
            if v1 == 0 or np.isnan(v1) or np.isnan(v2): 
                continue
            change = ((v2 - v1) / v1) * 100
            trend_records.append({
                "Metric": c,
                "From": f_prev,
                "To": f_curr,
                "Change_%": round(change, 2)
            })

            direction = "increased" if change > 0 else "decreased"
            ai_lines.append(f"{c} {direction} by {abs(change):.1f}% from {f_prev} to {f_curr}.")

    if not trend_records:
        print("⚠️ No trends computed.")
        return

    trends = pd.DataFrame(trend_records)
    trends.to_excel(OUTPUT, index=False)

    # --- plot trends ---
    plt.figure(figsize=(9,5))
    sns.barplot(data=trends, x="Metric", y="Change_%", hue="To")
    plt.xticks(rotation=45, ha="right")
    plt.axhline(0, color="black", lw=0.8)
    plt.title("Month-to-Month % Change")
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS, "Trend_Comparison.png"), dpi=200)
    plt.close()

    # --- AI style summary ---
    text = "\n".join(ai_lines)
    ai_summary = TextBlob(text).correct()
    with open(SUMMARY, "w", encoding="utf-8") as f:
        f.write(str(ai_summary))

    print(f"\n✅ Trend analysis saved to {OUTPUT}")
    print(f"🧠 AI summary saved to {SUMMARY}")
    print(f"📉 Chart → {os.path.join(CHARTS, 'Trend_Comparison.png')}")

# --- run -------------------------------------------------------------
if __name__ == "__main__":
    compare_trends()
