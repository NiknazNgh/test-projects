import pandas as pd
import os

def summarize_excel(folder, output_file):
    summaries = []

    for file in os.listdir(folder):
        if file.endswith((".xlsx", ".xls", ".xlsb")):
            path = os.path.join(folder, file)
            print(f"📂 Reading {file}...")

            # Use the correct engine for .xlsb files
            try:
                if file.endswith(".xlsb"):
                    df = pd.read_excel(path, engine="pyxlsb", sheet_name="Report", header=13)
                else:
                    df = pd.read_excel(path, sheet_name="Report", header=13)
            except Exception as e:
                print(f"⚠️ Could not read {file}: {e}")
                continue

            # Keep only numeric columns
            num_df = df.select_dtypes(include="number")

            if num_df.empty:
                print(f"⚠️ {file} has no numeric data.")
                continue

            summary = {
                "File": file,
                "Rows": len(num_df),
                "Columns": len(num_df.columns),
                "Sum": num_df.sum(numeric_only=True).sum(),
                "Average": num_df.mean(numeric_only=True).mean(),
                "Min": num_df.min(numeric_only=True).min(),
                "Max": num_df.max(numeric_only=True).max(),
            }

            summaries.append(summary)

    if not summaries:
        print("⚠️ No valid Excel data found.")
        return

    summary_df = pd.DataFrame(summaries)
    summary_df.to_excel(output_file, index=False)
    print(f"✅ Summary report saved to: {output_file}")

if __name__ == "__main__":
    summarize_excel(
        r"C:\Users\NEGAHDN\Downloads\test projects\excel-summary\Reports",
        r"C:\Users\NEGAHDN\Downloads\test projects\excel-summary\Excel_Summary_Report.xlsx"
    )
