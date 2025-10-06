import os
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from collections import Counter

# One-time setup (downloads sentence/word data)
nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)

FOLDER = r"C:\Users\NEGAHDN\Downloads\test projects\text-summarizer\texts"

def summarize_text(text):
    sentences = sent_tokenize(text)
    words = [w.lower() for w in word_tokenize(text) if w.isalnum()]
    stop_words = set(stopwords.words("english"))
    filtered = [w for w in words if w not in stop_words]
    freq = Counter(filtered)

    # Rank sentences by word frequency importance
    sentence_scores = {}
    for sent in sentences:
        for word in word_tokenize(sent.lower()):
            if word in freq:
                sentence_scores[sent] = sentence_scores.get(sent, 0) + freq[word]

    # Top 3 sentences = summary
    summary_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:3]
    summary = " ".join(summary_sentences)

    return summary, len(words)

def process_folder(folder):
    summaries = []
    for file in os.listdir(folder):
        if file.endswith(".txt"):
            path = os.path.join(folder, file)
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

            summary, word_count = summarize_text(text)
            summaries.append({
                "File": file,
                "Word_Count": word_count,
                "Summary": summary
            })
            print(f"🧩 Summarized {file}")

    if summaries:
        df = pd.DataFrame(summaries)
        output = os.path.join(folder, "Text_Summary_Report.xlsx")
        df.to_excel(output, index=False)
        print(f"✅ Summaries saved to: {output}")
    else:
        print("⚠️ No text files found.")

if __name__ == "__main__":
    process_folder(FOLDER)
