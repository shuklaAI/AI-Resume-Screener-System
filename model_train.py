import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import pickle
from resume_parser import clean_text, extract_features

# --- Example dataset (replace with your real data later) ---
data = {
    "resume_text": [
        "Experienced Python Developer skilled in Django, Flask, REST APIs.",
        "Fresh graduate with no relevant experience, seeking internship.",
        "5 years in Data Science with expertise in Machine Learning, pandas, NumPy.",
        "High school student applying for first job.",
        "Java Developer with 3 years experience, Spring Boot, Hibernate.",
        "Content Writer with creative writing skills, SEO optimization."
    ],
    "shortlisted": [1, 0, 1, 0, 1, 0]
}

df = pd.DataFrame(data)
df["cleaned"] = df["resume_text"].apply(lambda x: extract_features(clean_text(x)))

# --- TF-IDF Vectorization ---
vectorizer = TfidfVectorizer(max_features=1500)
X = vectorizer.fit_transform(df["cleaned"])
y = df["shortlisted"]

# --- Model Training ---
model = LogisticRegression()
model.fit(X, y)

# --- Save Trained Model ---
pickle.dump(model, open("models/model.pkl", "wb"))
pickle.dump(vectorizer, open("models/vectorizer.pkl", "wb"))

print("✅ Model training complete! Model and vectorizer saved in /models/")
