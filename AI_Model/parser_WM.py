import pdfplumber
import re
import json
import pandas as pd
import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Extended skills dictionary with categories
CATEGORIZED_SKILLS = {
    "Languages": ["Python", "Java", "C++", "C#", "Kotlin", "JavaScript", "TypeScript", "HTML", "CSS", "XML", "R"],
    "Frameworks": ["React", "Angular", "Vue", "Bootstrap", "Django", "Flask", "Spring", "Node.js"],
    "Libraries": ["TensorFlow", "PyTorch", "Keras", "Scikit-learn"],
    "ML Concepts": ["NLP", "RNN", "LSTM", "Bi-LSTM", "Transformers", "GPT-2"],
    "Databases": ["MySQL", "PostgreSQL", "MongoDB", "Oracle", "SQLite"],
    "Cloud": ["AWS", "Azure", "GCP"],
    "Tools": ["Git", "GitHub", "Bitbucket", "Jira", "VS Code", "Android Studio", "Android SDK", "Docker", "Kubernetes"]
}


def parse_pdf(file_path: str) -> str:
    """Extract raw text from PDF resumes."""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text


def parse_csv(file_path: str) -> str:
    """Parse CSV resumes into JSON string."""
    df = pd.read_csv(file_path)
    return df.to_json(orient="records")


def parse_json(file_path: str) -> str:
    """Parse JSON resume file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.dumps(json.load(f))


def clean_text(text: str) -> str:
    """Clean extra spaces and junk characters."""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tokenize_and_normalize(text: str) -> list:
    """Tokenize and lemmatize text with spaCy."""
    doc = nlp(text.lower())
    tokens = [tok.lemma_ for tok in doc if not tok.is_stop and tok.is_alpha]
    return tokens


def extract_skills_section(text: str) -> list:
    """Extract skills from Skills/Technical Skills/Core Competencies section."""
    section_keywords = [
        "skills", "technical skills", "key skills", "technologies",
        "core competencies", "expertise", "strengths"
    ]
    stop_keywords = [
        "experience", "education", "projects", "certifications",
        "awards", "work history", "employment"
    ]

    lines = text.splitlines()
    skills_found, capture = [], False

    for line in lines:
        line_clean = line.strip()

        # Start capture when skills section found
        if any(re.search(rf"\b{kw}\b", line_clean, re.IGNORECASE) for kw in section_keywords):
            capture = True
            continue

        # Stop when another section heading found
        if capture and any(re.search(rf"\b{kw}\b", line_clean, re.IGNORECASE) for kw in stop_keywords):
            break

        if capture and line_clean:
            if ":" in line_clean or "-" in line_clean:
                parts = re.split(r"[:\-]", line_clean, 1)
                if len(parts) > 1:
                    skills_found.append(parts[1])
                else:
                    skills_found.append(line_clean)
            else:
                skills_found.append(line_clean)

    # Split by common separators
    skills_text = " ".join(skills_found)
    skills = re.split(r"[,;|•]", skills_text)
    return [s.strip() for s in skills if s.strip()]


def extract_skills_global(text: str, dictionary: dict) -> list:
    """Fallback: detect skills from entire text using dictionary."""
    found = []
    for category, skills in dictionary.items():
        for skill in skills:
            if re.search(rf"\b{re.escape(skill)}\b", text, re.IGNORECASE):
                found.append(skill)
    return list(set(found))


def normalize_skills(skills: list) -> list:
    """Normalize duplicates & variants."""
    mapping = {
        "androidstudios": "Android Studio",
        "bootstrap": "Bootstrap",
        "vs code": "VS Code",
        "tensorflow ": "TensorFlow"
    }
    normalized = []
    for skill in skills:
        s = skill.strip()
        s = mapping.get(s.lower(), s)  # apply mapping if exists
        normalized.append(s)
    return sorted(set(normalized))


def categorize_skills(skills: list, dictionary: dict) -> dict:
    """Categorize extracted skills into groups."""
    categorized = {cat: [] for cat in dictionary.keys()}
    for skill in skills:
        for category, skill_list in dictionary.items():
            if skill in skill_list:
                categorized[category].append(skill)
    # Remove empty categories
    categorized = {k: v for k, v in categorized.items() if v}
    return categorized


def extract_all_skills(text: str, dictionary: dict) -> list:
    """Combine section-based + global skills + normalize (flat list)."""
    section_skills = extract_skills_section(text)
    global_skills = extract_skills_global(text, dictionary)
    all_skills = normalize_skills(section_skills + global_skills)
    return all_skills


def preprocess_resume(file_path: str, file_type: str = "pdf") -> dict:
    """Main pipeline: parse → clean → tokenize → extract skills."""
    if file_type == "pdf":
        raw = parse_pdf(file_path)
    elif file_type == "csv":
        raw = parse_csv(file_path)
    elif file_type == "json":
        raw = parse_json(file_path)
    else:
        raise ValueError("Unsupported file type")

    cleaned = clean_text(raw)
    tokens = tokenize_and_normalize(cleaned)
    skills = extract_all_skills(raw, CATEGORIZED_SKILLS)

    return {
        "raw_text": raw,
        "cleaned_text": cleaned,
        "tokens": tokens,
        "skills": skills
    }