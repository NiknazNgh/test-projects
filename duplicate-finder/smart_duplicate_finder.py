import os
import hashlib
import pandas as pd

FOLDER = r"C:\Users\NEGAHDN\Downloads"  # your target folder
SIMILAR_SIZE_TOLERANCE = 0.03  # 3% difference allowed

def file_hash(path):
    """Generate a SHA256 hash of a file."""
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return None

def scan_folder(folder):
    records = []
    for root, _, files in os.walk(folder):
        for f in files:
            path = os.path.join(root, f)
            try:
                size = os.path.getsize(path)
                hash_val = file_hash(path)
                records.append({"File": f, "Path": path, "Size": size, "Hash": hash_val})
            except Exception as e:
                print(f"⚠️ Skipped {f}: {e}")
    return pd.DataFrame(records)

def find_exact_and_similar(df):
    exact_dupes = df[df.duplicated("Hash", keep=False) & df["Hash"].notna()].copy()
    exact_dupes["Group"] = exact_dupes.groupby("Hash").ngroup() + 1

    similar = []
    names = df["File"].tolist()
    for i, name in enumerate(names):
        for j in range(i + 1, len(names)):
            if name.split(".")[0] == names[j].split(".")[0]:  # same base name
                size_a, size_b = df.iloc[i]["Size"], df.iloc[j]["Size"]
                diff = abs(size_a - size_b) / max(size_a, size_b)
                if diff <= SIMILAR_SIZE_TOLERANCE:
                    similar.append((df.iloc[i]["Path"], df.iloc[j]["Path"], round(diff * 100, 2)))

    similar_df = pd.DataFrame(similar, columns=["File1", "File2", "SizeDiff_%"])
    return exact_dupes, similar_df

def save_report(exact_df, similar_df, output_file):
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        if not exact_df.empty:
            exact_df.to_excel(writer, sheet_name="Exact Duplicates", index=False)
        if not similar_df.empty:
            similar_df.to_excel(writer, sheet_name="Similar Files", index=False)
    print(f"✅ Excel report saved: {output_file}")

if __name__ == "__main__":
    print(f"📂 Scanning folder: {FOLDER}")
    df = scan_folder(FOLDER)
    exact_df, similar_df = find_exact_and_similar(df)
    save_report(exact_df, similar_df, "Duplicate_Report.xlsx")
    print("🔎 Analysis complete — open Duplicate_Report.xlsx to view results.")

