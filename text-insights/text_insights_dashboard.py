import os
import pandas as pd
from textblob import TextBlob
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from collections import Counter
import nltk

# One-time setup
nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)

FOLDER = r"C:\Users\NEGAHDN\Downloads\test projects\text-insights\texts"

def analyze_text(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity

    # Clean and tokenize words
    words = [w.lower() for w in word_tokenize(text) if w.isalnum()]
    stop_words = set(stopwords.words("english"))
    words = [w for w in words if w not in stop_words]

    word_count = len(words)
    sentence_count = len(sent_tokenize(text))
    avg_sentence_len = round(word_count / max(sentence_count, 1), 2)

    # Top 10 keywords
    common_words = Counter(words).most_common(10)
    top_keywords = ", ".join([w for w, _ in common_words])
    most_freq_word = common_words[0][0] if common_words else None

    if sentiment > 0.1:
        sentiment_label = "Positive"
    elif sentiment < -0.1:
        sentiment_label = "Negative"
    else:
        sentiment_label = "Neutral"

    return {
        "Sentiment": sentiment_label,
        "Sentiment_Score": round(sentiment, 3),
        "Word_Count": word_count,
        "Avg_Sentence_Len": avg_sentence_len,
        "Most_Common_Word": most_freq_word,
        "Top_10_Keywords": top_keywords
    }

def process_folder(folder):
    results = []
    for file in os.listdir(folder):
        if file.endswith(".txt"):
            path = os.path.join(folder, file)
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

            stats = analyze_text(text)
            stats["File"] = file
            results.append(stats)
            print(f"📄 Analyzed {file}")

    if results:
        df = pd.DataFrame(results)
        output_path = os.path.join(folder, "Text_Insights_Dashboard.xlsx")
        df.to_excel(output_path, index=False)
        print(f"✅ Dashboard saved to: {output_path}")
    else:
        print("⚠️ No .txt files found.")

if __name__ == "__main__":
    process_folder(FOLDER)
