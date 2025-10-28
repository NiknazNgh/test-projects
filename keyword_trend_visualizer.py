import os
import re
import pandas as pd
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
import nltk

# Setup NLTK
nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)

FOLDER = r"C:\Users\NEGAHDN\Downloads\test projects\keyword-visualizer\texts"
OUTPUT = r"C:\Users\NEGAHDN\Downloads\test projects\keyword-visualizer\Keyword_Trend_Report.xlsx"
CHARTS_DIR = r"C:\Users\NEGAHDN\Downloads\test projects\keyword-visualizer\charts"

def clean_words(text):
    stop_words = set(stopwords.words("english"))
    tokens = [w.lower() for w in word_tokenize(text) if w.isalnum()]
    return [w for w in tokens if w not in stop_words]

def extract_month(filename):
    months = ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"]
    for m in months:
        if m in filename.lower():
            return m.capitalize()
    return "Unknown"

def analyze_folder(folder):
    os.makedirs(CHARTS_DIR, exist_ok=True)
    results = []

    for file in os.listdir(folder):
        if file.endswith(".txt"):
            path = os.path.join(folder, file)
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

            words = clean_words(text)
            counts = Counter(words)
            top10 = counts.most_common(10)
            month = extract_month(file)

            for word, freq in top10:
                results.append({"File": file, "Month": month, "Keyword": word, "Frequency": freq})
            print(f"📄 Processed {file}")

    df = pd.DataFrame(results)
    return df

def create_charts(df):
    os.makedirs(CHARTS_DIR, exist_ok=True)
    for month, data in df.groupby("Month"):
        plt.figure(figsize=(8,5))
        plt.bar(data["Keyword"], data["Frequency"], color="skyblue")
        plt.title(f"Top Keywords in {month}")
        plt.xlabel("Keyword")
        plt.ylabel("Frequency")
        plt.xticks(rotation=45)
        plt.tight_layout()
        chart_path = os.path.join(CHARTS_DIR, f"{month}_chart.png")
        plt.savefig(chart_path)
        plt.close()
        print(f"📊 Saved chart for {month}")

def save_excel(df, output_path):
    summary = df.groupby("Keyword")["Frequency"].sum().reset_index().sort_values("Frequency", ascending=False)
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Monthly Keywords")
        summary.to_excel(writer, index=False, sheet_name="Overall Summary")
    print(f"✅ Excel report saved: {output_path}")

if __name__ == "__main__":
    df = analyze_folder(FOLDER)
    if not df.empty:
        create_charts(df)
        save_excel(df, OUTPUT)
        print("🎯 Keyword trend visualization complete!")
    else:
        print("⚠️ No text files found in folder.")
