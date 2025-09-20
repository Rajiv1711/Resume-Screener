# resume_screener/feature_extraction.py
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import openai

openai.api_key = "YOUR_API_KEY_HERE"   # <- put in env var for security

tfidf_vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1,2))

def fit_tfidf(resume_texts: list):
    return tfidf_vectorizer.fit(resume_texts)

def get_tfidf_vector(text: str):
    return tfidf_vectorizer.transform([text])

def get_openai_embedding(text: str, model="text-embedding-3-small"):
    response = openai.Embedding.create(
        model=model,
        input=text[:3000]  # truncate long resumes
    )
    return np.array(response['data'][0]['embedding'])

def extract_features(cleaned_text: str):
    tfidf_vec = get_tfidf_vector(cleaned_text)
    embedding = get_openai_embedding(cleaned_text)
    return {
        "tfidf_vector": tfidf_vec,
        "embedding": embedding
    }
