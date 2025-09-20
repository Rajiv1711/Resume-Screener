# resume_screener/feature_extraction.py
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from sentence_transformers import SentenceTransformer

# Initialize TF-IDF vectorizer
tfidf_vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))

# Load open-source embedding model (runs locally)
# Options: 'all-MiniLM-L6-v2' (fast, 384d), 'all-mpnet-base-v2' (better, 768d)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def fit_tfidf(resume_texts: list):
    """Fit TF-IDF model on corpus of resumes."""
    return tfidf_vectorizer.fit(resume_texts)

def get_tfidf_vector(text: str):
    """Transform text into TF-IDF vector."""
    return tfidf_vectorizer.transform([text])

def get_embedding(text: str):
    """Get local embedding vector using SentenceTransformers."""
    embedding = embedding_model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
    return np.array(embedding)

def extract_features(cleaned_text: str):
    """Return TF-IDF + embedding features."""
    tfidf_vec = get_tfidf_vector(cleaned_text)
    embedding = get_embedding(cleaned_text)
    return {
        "tfidf_vector": tfidf_vec,
        "embedding": embedding
    }
