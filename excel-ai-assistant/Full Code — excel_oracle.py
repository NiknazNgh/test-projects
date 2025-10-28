import os, re, warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from textblob import TextBlob

warnings.filterwarnings("ignore")

REPORTS = r"C:\Users\NEGAHDN\Downloads\test projects\excel-ai-assistant\Reports"
CHARTS  = r"C:\Users\NEGAHDN\Downloads\test projects\excel-ai-assistant\Charts\Oracle"
SUMMARY = r"C:\Users\NEGAHDN\Downloads\test projects\excel-ai-assistant\Oracle_Predictions.txt"

os.makedirs(REPORTS, exist_ok=True)
os.makedirs(CHARTS, exist_ok=True)

month_map = {m.lower(): i for i,m in enumerate(
    ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"], start=1)}

def extract_month(fname):
    for m in month_map:
        if m in fname.lower():
            return month_map[m]
    nums = re.findall(r"\d+", fname)
    return int(nums[0]) if nums else 0

def smart_read_sheet(path, sheet="Report"):
    """Read Excel or XLSB sheet, skip top header junk, detect where data starts."""
    try:
        if path.lower().endswith(".xlsb"):
            xls = pd.ExcelFile(path, engine="pyxlsb")
        else:
            xls = pd.ExcelFile(path)

        if sheet.lower() not in [s.lower() for s in xls.sheet_names]:
            return pd.DataFrame()

        for s in xls.sheet_names:
            if s.lower() == sheet.lower():
                raw = pd.read_excel(xls, sheet_name=s, header=None)

                # Find where numbers start
                first_data_row = None
                for i in range(len(raw)):
                    numeric_ratio = raw.iloc[i].apply(lambda x: isinstance(x, (int, float))).mean()
                    if numeric_ratio > 0.3:  # at least 30% numbers → data section
                        first_data_row = i
                        break

                if first_data_row is None:
                    first_data_row = 13  # fallback default

                df = pd.read_excel(xls, sheet_name=s, header=first_data_row)
                df = df.select_dtypes(include=np.number)
                return df
    except Exception as e:
        print(f"⚠️ Error reading {path}: {e}")
    return pd.DataFrame()

def oracle_predict():
    files = [f for f in os.listdir(REPORTS)
             if f.lower().endswith((".xlsx",".xls",".xlsb"))]
    if not files:
        print("💤 Drop Excel reports in the Reports folder first.")
        return
    files.sort(key=extract_month)

    all_preds, oracle_lines = [], []
    print(f"🔮 Summoning the Oracle for {len(files)} reports...")

    for metric_col in ["Report"]:
        monthly_data = []
        for file in files:
            df = smart_read_sheet(os.path.join(REPORTS,file), sheet=metric_col)
            if df.empty: 
                continue
            mean_vals = df.mean().to_dict()
            month_num = extract_month(file)
            for k,v in mean_vals.items():
                if not np.isnan(v):
                    monthly_data.append({"Month":month_num,"File":file,"Metric":k,"Mean":v})
        if not monthly_data:
            continue

        df_all = pd.DataFrame(monthly_data)
        for metric in df_all["Metric"].unique():
            sub = df_all[df_all["Metric"]==metric].sort_values("Month")
            if len(sub)<3: 
                continue
            X = sub[["Month"]]
            y = sub["Mean"]
            model = LinearRegression().fit(X,y)
            next_m = sub["Month"].max()+1
            pred = model.predict([[next_m]])[0]
            all_preds.append({
                "Metric":metric,
                "Last_Month":int(sub["Month"].max()),
                "Predicted_Month":next_m,
                "Predicted_Value":round(pred,2)
            })
            direction = "📈 going up" if model.coef_[0]>0 else "📉 sliding down"
            oracle_lines.append(f"'{metric}' is {direction} — forecast {pred:.2f} next month.")

    if not all_preds:
        print("😶 Oracle still sees no numbers. Check that sheet names are 'Report'.")
        return

    df_pred = pd.DataFrame(all_preds)
    df_pred.to_excel(os.path.join(CHARTS,"Oracle_Predictions.xlsx"),index=False)

    # Plot
    plt.figure(figsize=(8,5))
    sns.barplot(data=df_pred,x="Metric",y="Predicted_Value")
    plt.title("🔮 Excel Oracle Forecasts")
    plt.xticks(rotation=45,ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS,"Oracle_Forecast.png"),dpi=200)
    plt.close()

    story = "\n".join(oracle_lines)
    blob = TextBlob(story).correct()
    final_story = f"✨ ORACLE REPORT ✨\n{blob}\n\n🧠 Stay consistent with your data layout!"
    with open(SUMMARY,"w",encoding="utf-8") as f:
        f.write(final_story)

    print(f"✅ Forecast saved → {CHARTS}")
    print(f"🧠 Summary saved → {SUMMARY}")

if __name__ == "__main__":
    oracle_predict()
