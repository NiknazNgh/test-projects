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

def read_all_sheets(path):
    try:
        if path.lower().endswith(".xlsb"):
            xls = pd.ExcelFile(path, engine="pyxlsb")
        else:
            xls = pd.ExcelFile(path)
        data = {}
        for s in xls.sheet_names:
            try:
                df = pd.read_excel(xls, sheet_name=s)
                if not df.empty:
                    data[s.lower()] = df.select_dtypes(include=np.number)
            except Exception:
                pass
        return data
    except Exception:
        return {}

def oracle_predict():
    files = [f for f in os.listdir(REPORTS)
             if f.lower().endswith((".xlsx",".xls",".xlsb"))]
    if not files:
        print("💤 Drop some Excel files first, Oracle awaits your tribute.")
        return
    files.sort(key=extract_month)

    all_preds, oracle_lines = [], []
    print(f"🔮 Summoning the Oracle for {len(files)} reports...")

    for sheetname in ["report", "summary"]:
        # stack monthly means per metric
        monthly_data = []
        for file in files:
            sheets = read_all_sheets(os.path.join(REPORTS,file))
            if sheetname not in sheets: 
                continue
            df = sheets[sheetname]
            means = df.mean().to_dict()
            month_num = extract_month(file)
            for k,v in means.items():
                monthly_data.append({"Month": month_num,"File":file,"Metric":k,"Mean":v})
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
                "Sheet":sheetname,
                "Metric":metric,
                "Last_Month":int(sub["Month"].max()),
                "Predicted_Month":next_m,
                "Predicted_Value":round(pred,2)
            })
            direction = "📈 going up" if model.coef_[0]>0 else "📉 sliding down"
            oracle_lines.append(
                f"In sheet '{sheetname}', '{metric}' is {direction} — forecast {pred:.2f} next month."
            )

    if not all_preds:
        print("😶 Oracle sees nothing (no numeric data).")
        return

    df_pred = pd.DataFrame(all_preds)
    df_pred.to_excel(os.path.join(CHARTS,"Oracle_Predictions.xlsx"),index=False)

    # plot
    plt.figure(figsize=(8,5))
    sns.barplot(data=df_pred,x="Metric",y="Predicted_Value",hue="Sheet")
    plt.title("🔮 Oracle Forecasts for Next Month")
    plt.xticks(rotation=45,ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS,"Oracle_Forecast.png"),dpi=200)
    plt.close()

    # sassy AI summary
    story = "\n".join(oracle_lines)
    blob = TextBlob(story).correct()
    story_final = f"✨ ORACLE REPORT ✨\n{blob}\n\nStay hydrated. Automate boldly."
    with open(SUMMARY,"w",encoding="utf-8") as f:
        f.write(story_final)

    print(f"✅ Predictions done → {CHARTS}")
    print(f"🧠 Oracle summary saved → {SUMMARY}")

if __name__ == "__main__":
    oracle_predict()
