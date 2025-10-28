import os
import pandas as pd

folder = r"C:\Users\NEGAHDN\Downloads\test projects\excel-ai-assistant\Reports"

for file in os.listdir(folder):
    if file.endswith((".xlsb", ".xlsx", ".xls")):
        path = os.path.join(folder, file)
        try:
            if path.endswith(".xlsb"):
                xls = pd.ExcelFile(path, engine="pyxlsb")
            else:
                xls = pd.ExcelFile(path)
            print(f"\n📘 {file}: {xls.sheet_names}")
        except Exception as e:
            print(f"⚠️ Could not read {file}: {e}")
