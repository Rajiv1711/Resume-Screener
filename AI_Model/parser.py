import pdfplumber
import re
import json
import pandas as pd
import spacy
from rapidfuzz import process, fuzz

nlp = spacy.load("en_core_web_sm")

SKILLS = ["Python", "Java", "C++", "SQL", "Machine Learning", "Deep Learning",
          "AWS", "Azure", "Docker", "Kubernetes", "JavaScript", "HTML", "CSS"]

def parse_pdf(file_path: str) -> str:
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

# def parse_csv(file_path: str) -> str:
#     df = pd.read_csv(file_path)
#     return df.to_json(orient="records")

# def parse_json(file_path: str) -> str:
#     with open(file_path, "r", encoding="utf-8") as f:
#         return json.dumps(json.load(f))

def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^A-Za-z0-9.,;:?!()\[\]\n ]", "", text)
    return text.strip()

def tokenize_and_normalize(text: str) -> list:
    doc = nlp(text.lower())
    tokens = [tok.lemma_ for tok in doc if not tok.is_stop and tok.is_alpha]
    return tokens

def extract_skills(text: str, skills_list=SKILLS) -> list:
    found = []
    for skill in skills_list:
        match, score, _ = process.extractOne(skill, text.split(), scorer=fuzz.partial_ratio)
        if score > 80:
            found.append(skill)
    return list(set(found))

def preprocess_resume(file_path: str, file_type: str = "pdf") -> dict:
    if file_type == "pdf":
        raw = parse_pdf(file_path)
    # elif file_type == "csv":
    #     raw = parse_csv(file_path)
    # elif file_type == "json":
    #     raw = parse_json(file_path)
    else:
        raise ValueError("Unsupported file type")

    cleaned = clean_text(raw)
    tokens = tokenize_and_normalize(cleaned)
    skills = extract_skills(cleaned)

    return {
        "raw_text": raw,
        "cleaned_text": cleaned,
        "tokens": tokens,
        "skills": skills
    }
