import os
import re
from textblob import TextBlob

TRANSCRIPTS = r"C:\Users\NEGAHDN\Downloads\test projects\meeting_ai\transcripts"
SUMMARIES = r"C:\Users\NEGAHDN\Downloads\test projects\meeting_ai\summaries"

os.makedirs(SUMMARIES, exist_ok=True)

def extract_action_items(text):
    pattern = r"\b(will|must|should|to)\b\s+([a-zA-Z\s]+)"
    items = re.findall(pattern, text, flags=re.IGNORECASE)
    clean_items = [f"- {verb.strip()} {task.strip().capitalize()}" for verb, task in items]
    return clean_items

def summarize_text(text):
    blob = TextBlob(text)
    sentences = blob.sentences
    summary = " ".join(str(s) for s in sentences[:5])  # first 5 sentences
    return summary

def process_transcript(path):
    print(f"📝 Reading {os.path.basename(path)}")
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    summary = summarize_text(text)
    actions = extract_action_items(text)
    sentiment = TextBlob(text).sentiment.polarity

    out = [
        f"=== Summary of {os.path.basename(path)} ===",
        f"Sentiment Score: {sentiment:.2f}",
        "\n--- Key Points ---\n" + summary,
        "\n--- Action Items ---",
        "\n".join(actions) if actions else "None detected.",
    ]

    output_path = os.path.join(SUMMARIES, f"{os.path.basename(path)}_summary.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))

    print(f"✅ Saved summary → {output_path}")

if __name__ == "__main__":
    for file in os.listdir(TRANSCRIPTS):
        if file.endswith(".txt"):
            process_transcript(os.path.join(TRANSCRIPTS, file))
