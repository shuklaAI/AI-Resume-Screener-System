import os
from flask import Flask, render_template, request, redirect, url_for
from resume_parser import (
    extract_text_from_file, clean_text, similarity_score,
    detect_experience, extract_keywords_from_jobdesc,
    match_keywords, generate_suggestions
)
import numpy as np

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"

# keep last-run results in memory (reset on server restart)
# structure: filename -> dict with keys: filename, score, role_type, job_desc, text, detected_experience, matched, missed, suggestions
LAST_RESULTS = {}

def analyze_resumes(job_desc, role_type, files):
    results = []
    keywords = extract_keywords_from_jobdesc(job_desc, top_n=30)
    for f in files:
        filename = f.filename
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        f.save(save_path)

        text = extract_text_from_file(save_path)
        text_clean = clean_text(text)
        base_score = similarity_score(text_clean, job_desc)

        detected = None
        missing_experience = False
        exp_val = None
        if role_type == "job":
            detected = detect_experience(text)
            if detected == "fresher":
                exp_val = 1
                base_score -= 5
            elif isinstance(detected, int):
                exp_val = detected
            else:
                missing_experience = True

        matched, missed = match_keywords(text_clean, keywords)
        suggestions = generate_suggestions(role_type, matched, missed, text_clean, detected)

        # --- Fixed scoring ---
        score = round(min(max(base_score, 0.0), 100.0), 2)

        # Apply small additive bonus/penalty for experience
        if exp_val is not None:
            if exp_val >= 10:
                score += 8
            elif exp_val >= 5:
                score += 5
            elif exp_val >= 3:
                score += 2
            elif exp_val <= 1:
                score -= 5
        # final clamp
        score = round(min(max(score, 0.0), 100.0), 2)

        result = {
            "filename": filename,
            "score": score,
            "role_type": role_type,
            "job_desc": job_desc,
            "text": text_clean,
            "detected_experience": detected,
            "exp_val": exp_val,
            "missing_experience": missing_experience,
            "matched_keywords": matched,
            "missed_keywords": missed,
            "suggestions": suggestions
        }
        LAST_RESULTS[filename] = result
        results.append(result)

    # sort & shortlist
    results = sorted(results, key=lambda x: x["score"], reverse=True)
    shortlisted = [r for r in results if r["score"] >= 70.0]
    not_shortlisted = [r for r in results if r["score"] < 70.0]
    return shortlisted, not_shortlisted

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        job_desc = request.form.get("job_desc", "").strip()
        role_type = request.form.get("role_type", "internship")
        files = request.files.getlist("resumes")
        if not job_desc:
            return render_template("dashboard.html", error="Please describe job requirements.")
        if not files or files == [None]:
            return render_template("dashboard.html", error="Please upload at least one resume.")
        shortlisted, not_shortlisted = analyze_resumes(job_desc, role_type, files)
        return render_template("dashboard.html",
                               shortlisted=shortlisted,
                               not_shortlisted=not_shortlisted,
                               job_desc=job_desc,
                               role_type=role_type)
    return render_template("dashboard.html")

@app.route("/view/<filename>", methods=["GET"])
def view_details(filename):
    r = LAST_RESULTS.get(filename)
    if not r:
        return "Result not found", 404
    return render_template("detail.html", r=r)

@app.route("/rescore", methods=["POST"])
def rescore():
    filename = request.form.get("filename")
    exp_bucket = request.form.get("experience_bucket")
    entry = LAST_RESULTS.get(filename)
    if not entry:
        return redirect(url_for("index"))

    mapping = {
        "0-1": 0,
        "1-3": 2,
        "3-5": 4,
        "5-10": 7,
        "10+": 12
    }
    exp_val = mapping.get(exp_bucket, None)

    base_score = similarity_score(entry["text"], entry["job_desc"])
    # small additive bonus/penalty
    score = round(min(max(base_score, 0.0), 100.0), 2)
    if exp_val is not None:
        if exp_val >= 10:
            score += 8
        elif exp_val >= 5:
            score += 5
        elif exp_val >= 3:
            score += 2
        elif exp_val <= 1:
            score -= 5
    score = round(min(max(score, 0.0), 100.0), 2)

    entry["score"] = score
    entry["detected_experience"] = exp_bucket
    entry["exp_val"] = exp_val
    entry["missing_experience"] = False
    LAST_RESULTS[filename] = entry

    all_results = list(LAST_RESULTS.values())
    shortlisted = [r for r in all_results if r["score"] >= 70.0]
    not_shortlisted = [r for r in all_results if r["score"] < 70.0]

    return render_template("dashboard.html",
                           shortlisted=shortlisted,
                           not_shortlisted=not_shortlisted,
                           job_desc=entry["job_desc"],
                           role_type=entry["role_type"])

if __name__ == "__main__":
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    app.run(debug=True)
