AI Powered Resume Screening System

An intelligent web-based application that automatically analyzes, scores, and shortlists resumes based on a recruiter’s job description. Built with Flask, Python, and NLP, it simulates how a recruiter evaluates resumes — focusing on relevance, experience, and key skills.

🚀 Features

AI-Powered Resume Analysis:
Uses semantic similarity and keyword extraction to understand how well a resume matches the job description.

Dynamic Scoring Engine:
Calculates a score (0–100%) considering both textual relevance and years of experience.

Experience Detection & Correction:
For full-time roles, if the resume lacks experience details, the app asks the user to specify experience manually to re-score dynamically.

Smart Shortlisting System:
Automatically shortlists top candidates based on percentile-based thresholds or average scoring.

Detailed Candidate Reports:
Each resume includes matched/missing keywords, AI-generated suggestions, and a preview of the extracted text.

Multi-File Uploads:
Supports multiple PDFs or DOCX resumes in one go for batch analysis.

Self-Learning Data Storage:
Keeps analysis history (job descriptions, keyword stats, scores) to improve scoring consistency over time.

⚙️ Tech Stack

Backend: Flask (Python)

Frontend: HTML5, Bootstrap 5

Libraries: NumPy, NLTK, scikit-learn (TF-IDF & cosine similarity)

File Support: PDF, DOCX

Data Storage: JSON-based self-learning logs


📁 Project Structure
AI_Resume_Screener/
│
├── app.py                 # Main Flask application
├── resume_parser.py       # NLP logic for parsing & scoring
├── templates/             # HTML templates (index, dashboard, details)
├── static/                # CSS, JS, assets
├── uploads/               # Uploaded resumes
└── data.json              # Stores learning data

🧩 How to Run Locally

Clone the repo:
git clone https://github.com/yourusername/AI_Resume_Screener.git
cd AI_Resume_Screener


Install dependencies:
pip install -r requirements.txt


Run the app:
python app.py


Open your browser and go to:
http://127.0.0.1:5000/

🏆 Future Enhancements

Integration with OpenAI API for deeper semantic understanding.

Exportable PDF report for each candidate.

Recruiter dashboard with analytics.
