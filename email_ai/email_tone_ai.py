import os
from textblob import TextBlob
import re

DRAFTS = r"C:\Users\NEGAHDN\Downloads\test projects\email_ai\drafts"
OUTPUT = r"C:\Users\NEGAHDN\Downloads\test projects\email_ai\improved_emails"
os.makedirs(OUTPUT, exist_ok=True)

TONE_MODES = {
    "professional": ["regards", "please", "thank you", "kindly", "sincerely"],
    "polite": ["hope you're doing well", "thank you for your time", "appreciate your help"],
    "confident": ["as discussed", "moving forward", "I recommend", "based on our results"]
}

def analyze_tone(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity < -0.2:
        return "Negative"
    elif polarity > 0.2:
        return "Positive"
    return "Neutral"

def rewrite_email(text, tone="professional"):
    # Fix spelling and grammar
    blob = TextBlob(text)
    corrected = str(blob.correct())

    # Enforce polite/confident tone
    if tone in TONE_MODES:
        additions = " ".join(TONE_MODES[tone])
        corrected += f"\n\n{additions.capitalize()}."
    
    # Clean up excessive whitespace
    corrected = re.sub(r"\s+", " ", corrected).strip()
    return corrected

def process_emails(tone="professional"):
    for file in os.listdir(DRAFTS):
        if not file.endswith(".txt"):
            continue

        path = os.path.join(DRAFTS, file)
        print(f"📧 Processing {file}...")

        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        tone_detected = analyze_tone(text)
        improved = rewrite_email(text, tone)

        out_path = os.path.join(OUTPUT, f"{os.path.splitext(file)[0]}_improved.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(f"=== Original Tone: {tone_detected} | Target: {tone} ===\n\n{improved}")

        print(f"✅ Saved → {out_path}")

if __name__ == "__main__":
    chosen_tone = input("Select tone (professional / polite / confident): ").strip().lower()
    if chosen_tone not in TONE_MODES:
        chosen_tone = "professional"
    process_emails(chosen_tone)
