import logging
import json
import re
import requests

# Configure logging
logger = logging.getLogger(__name__)

class MistralResumeParser:
    def __init__(self, ollama_base_url="http://localhost:11434", use_ai=True):
        self.use_ai = use_ai
        self.ollama_base_url = ollama_base_url
        self.model_name = "mistral"
        
    def check_ollama_available(self):
        """Check if Ollama is available"""
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def generate_with_mistral(self, prompt, max_tokens=512):
        """Generate using Mistral via Ollama"""
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": max_tokens
                }
            }
            
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                return response.json().get("response", "")
            return None
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            return None

    def parse_resume(self, resume_text: str):
        """Parse resume with Mistral or basic extraction"""
        if self.use_ai and self.check_ollama_available():
            return self.parse_with_mistral(resume_text)
        else:
            return self.basic_extraction(resume_text)

    def parse_with_mistral(self, resume_text: str):
        """Parse using Mistral"""
        try:
            prompt = f"""
            Extract skills and work experience from this resume. Return ONLY valid JSON with 'skills' list and 'experience' list.
            
            Resume: {resume_text[:2000]}
            
            JSON format: {{"skills": [], "experience": [{{"job_title": "", "company": "", "duration": "", "description": ""}}]}}
            
            JSON:
            """
            
            output = self.generate_with_mistral(prompt)
            if output:
                json_match = re.search(r'\{.*\}', output, re.DOTALL)
                if json_match:
                    parsed_data = json.loads(json_match.group())
                    return parsed_data
            return self.basic_extraction(resume_text)
        except Exception as e:
            logger.error(f"Mistral parsing failed: {e}")
            return self.basic_extraction(resume_text)

    def basic_extraction(self, resume_text: str):
        """Basic keyword-based extraction"""
        # Skill extraction
        skills_keywords = [
            'python', 'java', 'javascript', 'sql', 'aws', 'azure', 'docker', 
            'kubernetes', 'machine learning', 'ai', 'fastapi', 'react', 
            'node.js', 'mongodb', 'postgresql', 'git', 'jenkins', 'html',
            'css', 'typescript', 'linux', 'windows', 'agile', 'scrum'
        ]
        
        found_skills = []
        text_lower = resume_text.lower()
        for skill in skills_keywords:
            if skill in text_lower:
                found_skills.append(skill.title())
        
        # Experience extraction
        experience = []
        lines = [line.strip() for line in resume_text.split('\n') if line.strip()]
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(role in line_lower for role in ['engineer', 'developer', 'analyst', 'manager']):
                exp = {
                    "job_title": line,
                    "company": lines[i-1] if i > 0 and len(lines[i-1]) < 100 else "Unknown",
                    "duration": "Not specified",
                    "description": "Extracted from resume"
                }
                experience.append(exp)
        
        return {"skills": found_skills, "experience": experience}

# Create parser instance
resume_parser = MistralResumeParser()