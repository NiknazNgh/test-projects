import win32com.client
from textblob import TextBlob
import re
import time

# === CONFIG ===
TONE_MODES = {
    "professional": ["thank you", "please", "regards", "sincerely", "I appreciate your time"],
    "polite": ["hope you're doing well", "thank you for your patience", "appreciate your help"],
    "confident": ["as discussed", "moving forward", "I recommend", "based on our results"]
}

# --- Detect and strip signatures ---
def remove_signature(body):
    """
    Removes common Outlook signature patterns:
    - Lines starting with '--', 'Best', 'Regards', 'Sincerely'
    - HTML signature delimiters (if any)
    """
    signature_patterns = [
        r"(?i)^--.*$",          # -- or -- 
        r"(?i)^best[, ]?.*$",
        r"(?i)^regards[, ]?.*$",
        r"(?i)^sincerely[, ]?.*$",
        r"(?i)^cheers[, ]?.*$",
        r"(?i)^thanks[, ]?.*$",
        r"(?i)^sent from my.*$",
        r"(?i)^confidential.*$"
    ]
    lines = body.splitlines()
    cleaned = []
    for line in lines:
        if any(re.match(pat, line.strip()) for pat in signature_patterns):
            break  # stop at start of signature
        cleaned.append(line)
    return "\n".join(cleaned).strip()

# --- Tone & Rewrite functions ---
def analyze_tone(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity < -0.2:
        return "Negative"
    elif polarity > 0.2:
        return "Positive"
    return "Neutral"

def rewrite_text(text, tone="professional"):
    blob = TextBlob(text)
    corrected = str(blob.correct())

    if tone in TONE_MODES:
        additions = " ".join(TONE_MODES[tone])
        corrected += f"\n\n{additions.capitalize()}."
    corrected = re.sub(r"\s+", " ", corrected).strip()
    return corrected

# --- Outlook automation ---
def improve_drafts(tone="professional", limit=3):
    print(f"📬 Scanning Outlook Drafts... ({tone.title()} tone)")

    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    drafts = outlook.GetDefaultFolder(16).Items  # Folder 16 = Drafts
    improved = 0

    for item in list(drafts)[:limit]:
        if not item.Body.strip():
            continue

        print(f"\n✉️ Improving: {item.Subject or '(no subject)'}")

        # Remove signature block before analyzing
        clean_body = remove_signature(item.Body)
        if len(clean_body.split()) < 5:
            print("⚠️ Skipping: body too short or only signature.")
            continue

        tone_detected = analyze_tone(clean_body)
        new_body = rewrite_text(clean_body, tone)

        # Add your original untouched signature back if it exists
        signature = item.Body[len(clean_body):].strip()
        if signature:
            new_body += "\n\n" + signature

        # Save new version
        new_mail = outlook.GetDefaultFolder(16).Items.Add("IPM.Note")
        new_mail.Subject = f"[AI-Improved] {item.Subject}"
        new_mail.Body = (
            f"=== Original Tone: {tone_detected} | Target: {tone.title()} ===\n\n{new_body}"
        )
        new_mail.Save()
        improved += 1
        time.sleep(0.5)

    print(f"\n✅ Done! Improved {improved} draft(s). Check Outlook → Drafts folder.")

if __name__ == "__main__":
    tone = input("Select tone (professional / polite / confident): ").strip().lower()
    if tone not in TONE_MODES:
        tone = "professional"
    improve_drafts(tone)
