import os
import re
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from textblob import TextBlob

RESUME_PATH = r"C:\Users\NEGAHDN\Downloads\career_ai\resume.txt"
JOBS_FOLDER = r"C:\Users\NEGAHDN\Downloads\career_ai\jobs"
OUTPUT_REPORT = r"C:\Users\NEGAHDN\Downloads\career_ai\Skill_Match_Report.txt"
OUTPUT_CHART = r"C:\Users\NEGAHDN\Downloads\career_ai\Skill_Match_Chart.png"

os.makedirs(JOBS_FOLDER, exist_ok=True)

def clean_text(text):
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    return text.lower()

def load_resume(path):
    with open(path, "r", encoding="utf-8") as f:
        return clean_text(f.read())

def load_jobs(folder):
    jobs = {}
    for f in os.listdir(folder):
        if f.endswith((".txt", ".docx")):
            with open(os.path.join(folder, f), "r", encoding="utf-8", errors="ignore") as file:
                jobs[f] = clean_text(file.read())
    return jobs

def analyze_resume(resume_text, jobs):
    vectorizer = TfidfVectorizer(stop_words="english")
    all_docs = [resume_text] + list(jobs.values())
    tfidf_matrix = vectorizer.fit_transform(all_docs)
    scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    skill_tokens = vectorizer.get_feature_names_out()
    job_combined = " ".join(jobs.values())
    missing = [w for w in skill_tokens if w in job_combined and w not in resume_text]

    return pd.DataFrame({
        "Job File": list(jobs.keys()),
        "Match %": (scores * 100).round(2)
    }), missing[:20]

def sentiment_strength(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity

if __name__ == "__main__":
    print("📄 Reading resume and job descriptions...")
    resume_text = load_resume(RESUME_PATH)
    jobs = load_jobs(JOBS_FOLDER)

    if not jobs:
        print("⚠️ No job files found.")
    else:
        matches, missing_skills = analyze_resume(resume_text, jobs)
        matches.to_string(index=False)

        avg_sentiment = sentiment_strength(resume_text)
        advice = (
            "Your resume uses strong, confident language."
            if avg_sentiment > 0.2
            else "Try using more active verbs and positive phrasing."
        )

        report = []
        report.append("=== Resume vs Job Match ===")
        report.append(matches.to_string(index=False))
        report.append("\n=== Missing Skills ===")
        report.append(", ".join(missing_skills) if missing_skills else "None detected.")
        report.append(f"\n=== Language Tone ===\n{advice}")

        with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
            f.write("\n".join(report))

        # Visualization
        plt.figure(figsize=(8,5))
        plt.barh(matches["Job File"], matches["Match %"], color="skyblue")
        plt.xlabel("Match Percentage")
        plt.title("Resume vs Job Description Match")
        plt.tight_layout()
        plt.savefig(OUTPUT_CHART)
        plt.close()

        print(f"✅ Report saved → {OUTPUT_REPORT}")
        print(f"📊 Chart saved → {OUTPUT_CHART}")
