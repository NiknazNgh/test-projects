import os
from textblob import TextBlob
from difflib import SequenceMatcher
import re

# Paths
RESUME_PATH = r"C:\Users\NEGAHDN\Downloads\test projects\career_ai\resume.txt"
JOB_PATH = r"C:\Users\NEGAHDN\Downloads\test projects\career_ai\jobs\target_job.txt"
OUTPUT_PATH = r"C:\Users\NEGAHDN\Downloads\test projects\career_ai\Improved_Resume.txt"

def read_file(path):
    if not os.path.exists(path):
        print(f"⚠️ Missing: {path}")
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def extract_keywords(text):
    # Extract nouns and verbs as core skill/tone indicators
    blob = TextBlob(text)
    words = [word.lower() for (word, pos) in blob.tags if pos.startswith(("NN", "VB"))]
    return set(words)

def suggest_rewrites(resume, job):
    resume_lines = resume.splitlines()
    resume_keywords = extract_keywords(resume)
    job_keywords = extract_keywords(job)
    missing = [w for w in job_keywords if w not in resume_keywords]

    new_lines = []
    for line in resume_lines:
        # Add stronger verbs dynamically
        strong_line = re.sub(r"\b(responsible for|helped|worked on|did)\b", "Led", line, flags=re.I)
        strong_line = re.sub(r"\b(made|performed|handled)\b", "Implemented", strong_line, flags=re.I)
        strong_line = re.sub(r"\b(used|utilized)\b", "Leveraged", strong_line, flags=re.I)
        new_lines.append(strong_line)

    suggestions = []
    for word in missing[:15]:
        suggestions.append(f"- Add reference to: '{word}' (appears in job but not resume)")

    return "\n".join(new_lines), suggestions

def similarity(a, b):
    return round(SequenceMatcher(None, a.lower(), b.lower()).ratio() * 100, 2)

if __name__ == "__main__":
    print("📄 Reading resume and target job...\n")
    resume = read_file(RESUME_PATH)
    job = read_file(JOB_PATH)

    if not resume or not job:
        print("⚠️ Missing files. Ensure resume.txt and jobs/target_job.txt exist.")
        exit()

    sim = similarity(resume, job)
    improved_resume, suggestions = suggest_rewrites(resume, job)

    # Save results
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("=== AI Resume Rewriter v2 ===\n\n")
        f.write(f"Job Match Similarity: {sim}%\n\n")
        f.write("=== Improved Resume ===\n")
        f.write(improved_resume + "\n\n")
        f.write("=== AI Suggestions ===\n")
        f.write("\n".join(suggestions))

    print(f"✅ Rewrite complete — similarity {sim}%")
    print(f"📁 Saved → {OUTPUT_PATH}")
