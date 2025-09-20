# resume_screener/main.py
from parser_WM import preprocess_resume
from Feature_extraction_Transformers import fit_tfidf, extract_features

if __name__ == "__main__":
    # Example usage
    resume = preprocess_resume("sample_resume.pdf", file_type="pdf")

    corpus = [resume["cleaned_text"]]   # normally multiple resumes
    fit_tfidf(corpus)

    features = extract_features(resume["cleaned_text"])

    print("Extracted Skills:", resume["skills"])
    print("TF-IDF Vector Shape:", features["tfidf_vector"].shape)
    print("Embedding Dimension:", features["embedding"].shape)
    # print("TF-IDF Vector Shape:", features["tfidf_vector"])
    # print("Embedding Dimension:", features["embedding"])
    print("\n🔹 Total Tokens Extracted:", len(resume["tokens"]))
