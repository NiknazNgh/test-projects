import os
import re
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
import nltk

# Setup NLTK
nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)

FOLDER = r"C:\Users\NEGAHDN\Downloads\test projects\keyword-trends\texts"

def clean_words(text):
    stop_words = set(stopwords.words("english"))
    tokens = [w.lower() for w in word_tokenize(text) if w.isalnum()]
    return [w for w in tokens if w not in stop_words]

def extract_month(filename):
    months = [
        "jan","feb","mar","apr","may","jun",
        "jul","aug","sep","oct","nov","dec"
    ]
    for m in months:
        if m in filename.lower():
            return m.capitalize()
    return "Unknown"

def analyze_folder(folder):
    results = []
    total_counts = Counter()

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
                results.append({
                    "File": file,
                    "Month": month,
                    "Keyword": word,
                    "Frequency": freq
                })

            total_counts.update(counts)
            print(f"📄 Processed {file}")

    df = pd.DataFrame(results)
    summary = pd.DataFrame(total_counts.most_common(20), columns=["Keyword", "Total_Frequency"])

    with pd.ExcelWriter(os.path.join(folder, "Keyword_Trend_Report.xlsx")) as writer:
        df.to_excel(writer, index=False, sheet_name="Per File Top Keywords")
        summary.to_excel(writer, index=False, sheet_name="Overall Top Keywords")

    print("✅ Keyword trend report saved successfully!")

if __name__ == "__main__":
    analyze_folder(FOLDER)
