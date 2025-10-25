import re
from PyPDF2 import PdfReader
import docx2txt
import spacy

nlp = spacy.load("en_core_web_md")  # medium model for similarity

EXPERIENCE_REGEX = re.compile(r'(\d+)\s*(?:\+)?\s*(?:year|years|yrs)\b', re.I)
FRESHER_WORDS = {"fresher", "recent graduate", "fresh graduate", "entry level", "entry-level", "new grad"}

def extract_text_from_file(file_path):
    text = ""
    if file_path.lower().endswith(".pdf"):
        reader = PdfReader(file_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    elif file_path.lower().endswith(".docx"):
        text = docx2txt.process(file_path) or ""
    else:
        # fallback: try reading as txt
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except Exception:
            text = ""
    return text.strip()

def clean_text(text):
    return re.sub(r'\s+', ' ', (text or "")).strip()

def similarity_score(resume_text, job_desc):
    # returns 0-100
    if not resume_text:
        return 0.0
    doc_r = nlp(resume_text)
    doc_j = nlp(job_desc)
    return float(doc_r.similarity(doc_j) * 100)

def detect_experience(resume_text):
    """
    Try to extract years of experience as int.
    Returns:
      - int number of years if found (first match)
      - "fresher" if fresher-like word found
      - None if not found
    """
    t = resume_text.lower()
    for w in FRESHER_WORDS:
        if w in t:
            return "fresher"
    m = EXPERIENCE_REGEX.search(resume_text)
    if m:
        try:
            return int(m.group(1))
        except:
            return None
    return None

def extract_keywords_from_jobdesc(job_desc, top_n=25):
    """
    Extract candidate keywords from job description using spaCy tokens:
    non-stop alpha tokens, lemmatized, prioritized by POS (NOUN/PROPN/VERB).
    """
    doc = nlp(job_desc)
    kws = []
    for token in doc:
        if token.is_stop or not token.is_alpha or len(token.lemma_) < 3:
            continue
        if token.pos_ in ("NOUN", "PROPN", "VERB", "ADJ"):
            kws.append(token.lemma_.lower())
    # return unique preserving order
    seen = set()
    out = []
    for w in kws:
        if w not in seen:
            out.append(w)
            seen.add(w)
        if len(out) >= top_n:
            break
    return out

def match_keywords(resume_text, keywords):
    resume_low = resume_text.lower()
    matched = []
    missed = []
    for k in keywords:
        if k in resume_low:
            matched.append(k)
        else:
            missed.append(k)
    return matched, missed

def generate_suggestions(role_type, matched, missed, resume_text, detected_experience):
    suggestions = []
    # Suggest adding missing high-priority keywords
    if missed:
        # suggest up to 5 concrete keyword additions
        top_missed = missed[:8]
        suggestions.append("Add or emphasize these keywords: " + ", ".join(top_missed))

    # Projects / Achievements suggestion
    if "project" not in resume_text.lower() and role_type == "internship":
        suggestions.append("Add details about academic/projects or internships showing hands-on work.")
    if "project" not in resume_text.lower() and role_type == "job":
        suggestions.append("Add 1-2 projects with outcomes (metrics, scale) to show practical experience.")
    # Experience suggestions
    if role_type == "job":
        if detected_experience == "fresher":
            suggestions.append("Resume indicates 'fresher'; for experienced roles, mention internships, contracts, or freelance work.")
        elif detected_experience is None:
            suggestions.append("Specify total years of professional experience clearly (e.g., '3 years of experience').")
        elif isinstance(detected_experience, int) and detected_experience < 2:
            suggestions.append("If applying to mid-level roles, highlight longer-tenure projects or lead responsibilities.")
    # Achievements and metrics
    if "achiev" not in resume_text.lower() and "result" not in resume_text.lower() and role_type == "job":
        suggestions.append("Add specific achievements with numbers (e.g., 'reduced load time by 30%', 'handled 1000 users').")

    # keep unique
    unique = []
    for s in suggestions:
        if s not in unique:
            unique.append(s)
    return unique
