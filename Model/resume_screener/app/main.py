"""
Resume Screener API with Mistral via Ollama
"""

import logging
import re
import json
import requests
from datetime import datetime
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Resume Screener API",
    description="Resume parsing with Mistral via Ollama",
    version="2.1.0"
)

candidates_db = []

class MistralResumeParser:
    """Resume parser using Mistral via Ollama"""
    
    def __init__(self, ollama_base_url="http://localhost:11434"):
        self.ollama_base_url = ollama_base_url
        self.model_name = "mistral"  # Default Mistral model
        self.available_models = ["mistral", "mistral:instruct", "mistral:latest"]
        
    def check_ollama_connection(self):
        """Check if Ollama is running and available"""
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags")
            return response.status_code == 200
        except:
            return False
    
    def generate_with_mistral(self, prompt, max_tokens=512, temperature=0.1):
        """Generate text using Mistral via Ollama"""
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json=payload,
                timeout=120  # 2 minute timeout
            )
            
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            return None

    def create_few_shot_prompt(self, resume_text):
        """Create a few-shot learning prompt with examples"""
        
        examples = """
        Example 1:
        Resume: "John Smith - Software Engineer at Tech Corp (2020-Present). Skills: Python, Java, AWS. Developed web applications using React and Node.js."
        Output: {"skills": ["Python", "Java", "AWS", "React", "Node.js"], "experience": [{"job_title": "Software Engineer", "company": "Tech Corp", "duration": "2020-Present", "description": "Developed web applications"}]}

        Example 2:
        Resume: "Jane Doe - Data Scientist at Data Inc (2019-2022). Skills: Machine Learning, Python, SQL. Built predictive models for business analytics."
        Output: {"skills": ["Machine Learning", "Python", "SQL"], "experience": [{"job_title": "Data Scientist", "company": "Data Inc", "duration": "2019-2022", "description": "Built predictive models for business analytics"}]}

        Example 3:
        Resume: "Mike Johnson - Senior Developer at Startup Co (2021-Now). Technologies: JavaScript, React, AWS. Led team of 5 developers."
        Output: {"skills": ["JavaScript", "React", "AWS"], "experience": [{"job_title": "Senior Developer", "company": "Startup Co", "duration": "2021-Now", "description": "Led team of 5 developers"}]}
        """
        
        prompt = f"""
        You are an expert resume parser. Extract skills and work experience from the resume text below. 
        Return ONLY a valid JSON object with "skills" list and "experience" list. Do not include any other text.

        Instructions:
        - Extract all technical skills, programming languages, tools, and technologies
        - Extract work experience with job title, company, duration, and brief description
        - Return clean JSON format only

        {examples}

        Now extract from this resume:
        {resume_text[:2000]}

        Output JSON:
        """
        
        return prompt

    def parse_with_mistral(self, resume_text):
        """Parse using Mistral via Ollama"""
        try:
            if not self.check_ollama_connection():
                logger.warning("Ollama not available, using rule-based parser")
                return self.rule_based_parse(resume_text)
            
            prompt = self.create_few_shot_prompt(resume_text)
            
            output_text = self.generate_with_mistral(prompt)
            
            if output_text:
                # Extract JSON from output
                json_match = re.search(r'\{.*\}', output_text, re.DOTALL)
                if json_match:
                    try:
                        parsed_data = json.loads(json_match.group())
                        return parsed_data
                    except json.JSONDecodeError as e:
                        logger.warning(f"JSON parsing failed: {e}, trying to clean JSON")
                        # Try to clean and parse again
                        cleaned_json = self.clean_json_string(json_match.group())
                        try:
                            parsed_data = json.loads(cleaned_json)
                            return parsed_data
                        except:
                            logger.warning("JSON cleaning failed, using rule-based fallback")
                            return self.rule_based_parse(resume_text)
                else:
                    logger.warning("No JSON found in model output, using rule-based fallback")
                    return self.rule_based_parse(resume_text)
            else:
                logger.warning("Mistral generation failed, using rule-based fallback")
                return self.rule_based_parse(resume_text)
                
        except Exception as e:
            logger.error(f"Mistral parsing failed: {e}")
            return self.rule_based_parse(resume_text)

    def clean_json_string(self, json_string):
        """Clean JSON string by removing common formatting issues"""
        # Remove extra whitespace and newlines
        cleaned = re.sub(r'\s+', ' ', json_string)
        # Fix common JSON issues
        cleaned = re.sub(r',\s*}', '}', cleaned)
        cleaned = re.sub(r',\s*]', ']', cleaned)
        # Ensure proper quoting
        cleaned = re.sub(r'(\w+):', r'"\1":', cleaned)
        return cleaned

    def rule_based_parse(self, resume_text):
        """Rule-based fallback parser"""
        skills = self.extract_skills(resume_text)
        experience = self.extract_experience(resume_text)
        
        return {
            "skills": skills,
            "experience": experience
        }

    def extract_skills(self, text):
        """Extract skills using pattern matching"""
        skills_keywords = [
            'python', 'java', 'javascript', 'sql', 'aws', 'azure', 'docker', 
            'kubernetes', 'machine learning', 'ai', 'react', 'node.js',
            'mongodb', 'postgresql', 'git', 'jenkins', 'typescript', 'linux',
            'fastapi', 'flask', 'django', 'vue', 'angular', 'spring', 'tensorflow',
            'pytorch', 'pandas', 'numpy', 'scikit-learn', 'terraform', 'ansible'
        ]
        
        found_skills = []
        text_lower = text.lower()
        for skill in skills_keywords:
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                found_skills.append(skill.title())
        
        return found_skills

    def extract_experience(self, text):
        """Extract experience using pattern matching"""
        experience = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line_clean = line.strip()
            if not line_clean:
                continue
                
            # Look for job patterns
            job_indicators = ['engineer', 'developer', 'analyst', 'manager', 
                             'specialist', 'consultant', 'architect', 'director']
            
            if any(role in line_clean.lower() for role in job_indicators):
                # Try to extract dates
                dates = re.findall(r'(\d{4}[-–]\d{4}|\d{4}[-–](?:present|now)|(?:present|now))', line_clean)
                duration = dates[0] if dates else "Not specified"
                
                exp = {
                    "job_title": line_clean,
                    "company": "Extracted from resume",
                    "duration": duration,
                    "description": "Position details extracted from resume text"
                }
                experience.append(exp)
        
        return experience

    def parse_resume(self, resume_text):
        """Main parsing method"""
        # Try Mistral via Ollama first
        result = self.parse_with_mistral(resume_text)
        
        return {
            "skills": result.get("skills", []),
            "experience": result.get("experience", []),
            "parsing_method": "mistral_ollama" if self.check_ollama_connection() else "rule_based",
            "model_used": self.model_name if self.check_ollama_connection() else "rule_based"
        }

# Global parser instance
resume_parser = MistralResumeParser()

# FastAPI endpoints
@app.on_event("startup")
async def startup_event():
    logger.info("Mistral Resume Parser API starting up...")
    if resume_parser.check_ollama_connection():
        logger.info("Ollama connection successful - Mistral model available")
    else:
        logger.warning("Ollama not available - using rule-based parsing only")

@app.get("/")
async def root():
    ollama_status = "available" if resume_parser.check_ollama_connection() else "unavailable"
    return {
        "message": "Resume Screener with Mistral via Ollama",
        "model": "Mistral",
        "ollama_status": ollama_status,
        "approach": "Few-shot learning with Mistral"
    }

@app.get("/models")
async def list_models():
    """List available Ollama models"""
    try:
        response = requests.get(f"{resume_parser.ollama_base_url}/api/tags")
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Unable to fetch models"}
    except:
        return {"error": "Ollama not available"}

@app.post("/parse-resume/")
async def parse_resume(file: UploadFile = File(...)):
    try:
        # Read file content
        content = await file.read()
        
        if file.filename.lower().endswith('.pdf'):
            import io
            import pdfplumber
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                text = "\n".join([page.extract_text() or "" for page in pdf.pages])
        else:
            text = content.decode("utf-8")

        # Parse resume
        parsed_data = resume_parser.parse_resume(text)
        
        # Store result
        candidate_record = {
            "id": len(candidates_db) + 1,
            "filename": file.filename,
            "timestamp": datetime.now().isoformat(),
            **parsed_data
        }
        candidates_db.append(candidate_record)
        
        return {
            "success": True,
            "parsed_data": parsed_data,
            "candidate_id": candidate_record["id"]
        }
        
    except Exception as e:
        raise HTTPException(500, f"Error: {str(e)}")

@app.get("/candidates")
async def get_candidates():
    """Get all parsed candidates"""
    return {
        "count": len(candidates_db),
        "candidates": candidates_db
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)