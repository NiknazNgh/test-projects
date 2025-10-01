import pandas as pd
import os

def merge_excels(folder, output_file):
    all_data = []
    
    for file in os.listdir(folder):
        if file.endswith((".xlsx", ".xls", ".xlsb")):  # handle multiple formats
            path = os.path.join(folder, file)
            print(f"📂 Reading {file}...")

            # choose engine based on file type
            if file.endswith(".xlsb"):
                df = pd.read_excel(path, engine="pyxlsb", skiprows=13)  # skip first 13 rows → start at row 14
            else:
                df = pd.read_excel(path, skiprows=13)

            df["Source_File"] = file
            all_data.append(df)

    if not all_data:
        print("⚠️ No Excel files found in folder.")
        return

    merged = pd.concat(all_data, ignore_index=True)
    merged.to_excel(output_file, index=False)
    print(f"✅ Merged {len(all_data)} files → {output_file}")

if __name__ == "__main__":
    merge_excels(
        r"C:\Users\NEGAHDN\Downloads\test projects\excel-merger\Reports",
        r"C:\Users\NEGAHDN\Downloads\test projects\excel-merger\merged_output.xlsx"
    )
