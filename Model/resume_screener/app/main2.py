"""
Hybrid Resume Screener API - Combining Multiple Parsing Methods
"""

import logging
import re
from datetime import datetime
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Resume Screener API",
    description="Hybrid resume parsing system using multiple methods",
    version="2.0.0"
)

# Simple in-memory database
candidates_db = []

class HybridResumeParser:
    """Hybrid resume parser combining section-based, pattern-based, and dictionary approaches"""
    
    def __init__(self):
        # Comprehensive section headers
        self.section_headers = {
            'contact': ['contact', 'personal', 'details', 'information'],
            'summary': ['summary', 'objective', 'profile'],
            'experience': ['experience', 'work experience', 'employment', 'work history', 'professional experience'],
            'education': ['education', 'academic', 'qualifications', 'degrees'],
            'skills': ['skills', 'technical skills', 'technologies', 'expertise', 'competencies', 'TECHNICAL SKILLS'],
            'projects': ['projects', 'personal projects', 'project experience'],
            'certifications': ['certifications', 'certificates', 'courses']
        }
        
        # Comprehensive skills database
        self.skills_db = [
            # Programming Languages
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 
            'swift', 'kotlin', 'php', 'ruby', 'scala', 'r', 'matlab',
            
            # Web Technologies
            'html', 'css', 'react', 'angular', 'vue', 'django', 'flask', 'fastapi', 
            'spring', 'express', 'node.js', 'asp.net', 'laravel',
            
            # Databases
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sqlite',
            'cassandra', 'dynamodb',
            
            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'terraform',
            'ansible', 'github actions', 'gitlab ci',
            
            # Data Science & AI
            'machine learning', 'ai', 'artificial intelligence', 'deep learning',
            'nlp', 'computer vision', 'data science', 'pandas', 'numpy', 
            'scikit-learn', 'tensorflow', 'pytorch', 'keras',
            
            # Tools & Platforms
            'git', 'github', 'gitlab', 'jira', 'confluence', 'docker', 'kubernetes',
            'linux', 'windows', 'bash',
            
            # Methodologies
            'agile', 'scrum', 'devops', 'ci/cd', 'microservices', 'rest api'
        ]
        
        # Job title indicators
        self.job_title_indicators = [
            'engineer', 'developer', 'analyst', 'manager', 'architect', 'specialist', 
            'consultant', 'lead', 'principal', 'senior', 'junior', 'associate'
        ]
        
        # Date patterns
        self.date_pattern = r'(\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4}\s*[-–—]\s*(?:present|now|(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4})|\b\d{4}\s*[-–—]\s*(?:present|now|\d{4})\b)'
        
        # Company pattern
        self.company_pattern = r'([A-Z][a-zA-Z0-9&\.\-\s]+,?\s*(?:Inc|LLC|Ltd|Corp|Company|Solutions|Technologies|Group)?)'

    def clean_text(self, text):
        """Clean and normalize resume text"""
        # Replace multiple whitespaces with single space
        text = re.sub(r'\s+', ' ', text)
        # Fix common OCR issues
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        return text.strip()

    def identify_sections(self, text):
        """Identify resume sections based on headers"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        sections = {}
        current_section = 'preamble'
        current_content = []
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            is_section_header = False
            detected_section = None
            
            # Check for section headers
            for section_name, headers in self.section_headers.items():
                for header in headers:
                    # Match whole words to avoid false positives
                    if re.search(r'\b' + re.escape(header) + r'\b', line_lower):
                        if self._is_likely_section_header(line, i, lines):
                            detected_section = section_name
                            is_section_header = True
                            break
                if is_section_header:
                    break
            
            if is_section_header and detected_section:
                # Save previous section
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)
                
                # Start new section
                current_section = detected_section
                current_content = []
            else:
                current_content.append(line)
        
        # Save final section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)
            
        return sections

    def _is_likely_section_header(self, line, line_num, all_lines):
        """Determine if a line is likely a real section header"""
        if len(line) > 80:  # Headers are usually short
            return False
            
        # Headers often have specific formatting
        if (line.isupper() or 
            line.istitle() or 
            re.search(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*:', line)):
            return True
            
        # Check if it's followed by content (not another header)
        if line_num < len(all_lines) - 1:
            next_line = all_lines[line_num + 1]
            if next_line and not self._is_likely_section_header(next_line, line_num + 1, all_lines):
                return True
                
        return False

    def parse_experience_section(self, experience_text):
        """Parse experience section using multiple strategies"""
        if not experience_text:
            return []
            
        experiences = []
        
        # Strategy 1: Split by likely job blocks (empty lines or date patterns)
        blocks = self._split_experience_blocks(experience_text)
        
        for block in blocks:
            experience = self._parse_experience_block(block)
            if experience and self._is_valid_experience(experience):
                experiences.append(experience)
        
        return experiences

    def _split_experience_blocks(self, text):
        """Split experience text into individual job blocks"""
        # Split by empty lines or major separators
        blocks = re.split(r'\n\s*\n', text)
        
        # Further split blocks that might contain multiple jobs
        refined_blocks = []
        for block in blocks:
            # Check if block contains date patterns that might indicate multiple jobs
            date_matches = list(re.finditer(self.date_pattern, block, re.IGNORECASE))
            if len(date_matches) > 1:
                # Split by dates
                positions = []
                last_end = 0
                for match in date_matches:
                    if match.start() > last_end:
                        positions.append(block[last_end:match.start()].strip())
                    positions.append(block[match.start():].strip())
                    last_end = match.end()
                
                # Filter out empty positions
                refined_blocks.extend([p for p in positions if p and len(p) > 10])
            else:
                refined_blocks.append(block)
        
        return [b for b in refined_blocks if b and len(b.strip()) > 20]

    def _parse_experience_block(self, block):
        """Parse a single experience block"""
        lines = [line.strip() for line in block.split('\n') if line.strip()]
        if not lines:
            return None
        
        # First line typically contains job title, company, and dates
        first_line = lines[0]
        
        # Extract dates
        dates = re.findall(self.date_pattern, first_line, re.IGNORECASE)
        duration = dates[0] if dates else "Not specified"
        
        # Remove dates from first line
        title_company_line = re.sub(self.date_pattern, '', first_line, flags=re.IGNORECASE).strip()
        
        # Extract job title and company
        job_title, company = self._extract_title_company(title_company_line)
        
        # Extract description from remaining lines
        description = self._extract_description(lines[1:])
        
        return {
            "job_title": job_title,
            "company": company,
            "duration": duration,
            "description": description
        }

    def _extract_title_company(self, text):
        """Extract job title and company from text"""
        # Common separators
        separators = [',', ' at ', ' - ', ' | ', ' – ']
        
        for sep in separators:
            if sep in text:
                parts = text.split(sep, 1)
                if len(parts) == 2:
                    title = parts[0].strip()
                    company = parts[1].strip()
                    
                    # Clean up titles and companies
                    title = re.sub(r'^[•\-]\s*', '', title)
                    company = re.sub(r'[,\-]\s*$', '', company)
                    
                    return title, company
        
        # If no clear separator, try to identify based on patterns
        words = text.split()
        if len(words) >= 2:
            # Look for company indicators
            company_indicators = ['inc', 'llc', 'ltd', 'corp', 'company', 'technologies']
            for i, word in enumerate(words):
                if any(indicator in word.lower() for indicator in company_indicators):
                    title = ' '.join(words[:i])
                    company = ' '.join(words[i:])
                    return title, company
        
        # Default: assume it's mostly title
        return text, "Unknown"

    def _extract_description(self, lines):
        """Extract job description from lines"""
        description_lines = []
        
        for line in lines:
            # Clean bullet points and limit line length
            clean_line = re.sub(r'^[•\-]\s*', '', line)
            if len(clean_line) < 150:  # Reasonable length for description
                description_lines.append(clean_line)
        
        return ' | '.join(description_lines) if description_lines else "Responsibilities not specified"

    def _is_valid_experience(self, experience):
        """Validate if the extracted experience is reasonable"""
        title = experience['job_title'].lower()
        company = experience['company'].lower()
        
        # Check if title contains job indicators
        has_job_indicator = any(indicator in title for indicator in self.job_title_indicators)
        
        # Check if company doesn't look like a description
        company_valid = (company != "unknown" and 
                        len(company) > 2 and 
                        not any(word in company for word in ['engineered', 'developed', 'built']))
        
        # Check if title is not too long (likely a description mistaken as title)
        title_valid = len(experience['job_title']) < 80
        
        return has_job_indicator and company_valid and title_valid

    def extract_skills(self, text):
        """Extract skills using dictionary-based approach with context awareness"""
        text_lower = text.lower()
        found_skills = set()
        
        # Method 1: Extract from skills section specifically
        skills_sections = re.findall(
            r'(?:skills|technical skills|technologies|expertise)[:\s]*([^•\n]+(?:\n[^•\n]+)*)', 
            text_lower, re.IGNORECASE
        )
        
        # Extract from skills sections first (most reliable)
        for section in skills_sections:
            for skill in self.skills_db:
                if re.search(r'\b' + re.escape(skill) + r'\b', section):
                    found_skills.add(skill.title())
        
        # Method 2: Extract from entire text but with context validation
        for skill in self.skills_db:
            skill_pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(skill_pattern, text_lower):
                # Additional context validation
                matches = list(re.finditer(skill_pattern, text_lower))
                for match in matches:
                    start, end = match.span()
                    # Get context around the match
                    context_start = max(0, start - 20)
                    context_end = min(len(text_lower), end + 20)
                    context = text_lower[context_start:context_end]
                    
                    # Check if it's likely a real skill mention
                    if self._is_likely_skill_mention(context, skill):
                        found_skills.add(skill.title())
                        break
        
        return sorted(list(found_skills))

    def _is_likely_skill_mention(self, context, skill):
        """Determine if a skill mention is likely genuine"""
        positive_indicators = [
            'skill', 'experience', 'knowledge', 'proficient', 'familiar',
            'using', 'with', 'knowledge of', 'experience with'
        ]
        
        negative_indicators = [
            'project', 'description', 'developed', 'built', 'created', 'engineered'
        ]
        
        # Check for positive context
        has_positive = any(indicator in context for indicator in positive_indicators)
        
        # Check for negative context (likely a project description)
        has_negative = any(indicator in context for indicator in negative_indicators)
        
        return has_positive and not has_negative

    def parse_resume(self, text):
        """Main parsing method using hybrid approach"""
        # Clean text first
        text = self.clean_text(text)
        
        # Step 1: Identify sections
        sections = self.identify_sections(text)
        
        # Step 2: Extract skills (prioritize skills section)
        skills_text = sections.get('skills', '') + ' ' + text  # Include full text as fallback
        skills = self.extract_skills(skills_text)
        
        # Step 3: Extract experience (only from experience section)
        experience_text = sections.get('experience', '')
        experience = self.parse_experience_section(experience_text)
        
        # Step 4: Fallback if section parsing didn't work well
        if len(experience) == 0 and len(skills) < 3:
            logger.info("Section parsing weak, using fallback pattern-based approach")
            skills = self._fallback_skill_extraction(text)
            experience = self._fallback_experience_extraction(text)
        
        return {
            "skills": skills,
            "experience": experience,
            "sections_identified": list(sections.keys()),
            "parsing_method": "hybrid"
        }

    def _fallback_skill_extraction(self, text):
        """Fallback skill extraction when section parsing fails"""
        text_lower = text.lower()
        found_skills = set()
        
        for skill in self.skills_db:
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                found_skills.add(skill.title())
        
        return sorted(list(found_skills))

    def _fallback_experience_extraction(self, text):
        """Fallback experience extraction when section parsing fails"""
        experiences = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line_clean = line.strip()
            if not line_clean:
                continue
                
            # Look for lines that might contain experience information
            if any(indicator in line_clean.lower() for indicator in self.job_title_indicators):
                dates = re.findall(self.date_pattern, line_clean, re.IGNORECASE)
                if dates:
                    experience = {
                        "job_title": line_clean,
                        "company": "Extracted from text",
                        "duration": dates[0],
                        "description": "Automatically extracted"
                    }
                    experiences.append(experience)
        
        return experiences

# Global parser instance
resume_parser = HybridResumeParser()

@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    logger.info("Hybrid Resume Screener API starting up...")
    logger.info("Server ready at http://localhost:8000")
    logger.info("API documentation available at http://localhost:8000/docs")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Hybrid Resume Screener API is running!",
        "version": "2.0.0",
        "features": [
            "Section-based parsing",
            "Pattern recognition", 
            "Dictionary-based skill extraction",
            "Context-aware validation",
            "Fallback mechanisms"
        ],
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "parse_resume": "POST /parse-resume/",
            "list_candidates": "GET /candidates/"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "hybrid_resume_screener",
        "timestamp": datetime.now().isoformat(),
        "parser_ready": True
    }

@app.post("/parse-resume/")
async def parse_resume(file: UploadFile = File(...)):
    """Parse a resume file using hybrid parsing approach"""
    try:
        logger.info(f"Processing file: {file.filename}")
        
        # Read file content
        content = await file.read()
        
        # Handle different file types
        if file.filename.lower().endswith('.pdf'):
            try:
                import io
                import pdfplumber
                
                with pdfplumber.open(io.BytesIO(content)) as pdf:
                    text_pages = []
                    for page in pdf.pages:
                        page_text = page.extract_text() or ""
                        text_pages.append(page_text)
                    text = "\n".join(text_pages)
                    logger.info(f"PDF processed: {len(pdf.pages)} pages, {len(text)} characters")
                    
            except Exception as e:
                logger.warning(f"PDF processing failed: {e}, using as text")
                text = content.decode('utf-8', errors='ignore')
        else:
            text = content.decode('utf-8', errors='ignore')

        if not text.strip():
            raise HTTPException(status_code=400, detail="No text content found in file")
        
        logger.info(f"Text extracted: {len(text)} characters")
        
        # Parse the resume with hybrid approach
        parsed_data = resume_parser.parse_resume(text)
        
        # Store in database
        candidate_record = {
            "id": len(candidates_db) + 1,
            "filename": file.filename,
            "timestamp": datetime.now().isoformat(),
            "skills": parsed_data["skills"],
            "experience": parsed_data["experience"],
            "sections_identified": parsed_data["sections_identified"],
            "parsing_method": parsed_data["parsing_method"],
            "text_preview": text[:300] + "..." if len(text) > 300 else text
        }
        candidates_db.append(candidate_record)
        
        logger.info(f"Resume parsed successfully: {len(parsed_data['skills'])} skills, {len(parsed_data['experience'])} experiences")
        
        return {
            "success": True,
            "filename": file.filename,
            "parsed_data": {
                "skills": parsed_data["skills"],
                "experience": parsed_data["experience"]
            },
            "metadata": {
                "sections_identified": parsed_data["sections_identified"],
                "parsing_method": parsed_data["parsing_method"],
                "candidate_id": candidate_record["id"]
            }
        }
        
    except Exception as e:
        logger.error(f"Error processing resume: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.get("/candidates/")
async def list_candidates():
    """Get list of all parsed candidates"""
    return {
        "count": len(candidates_db),
        "candidates": candidates_db
    }

@app.get("/candidates/{candidate_id}")
async def get_candidate(candidate_id: int):
    """Get specific candidate by ID"""
    if candidate_id < 1 or candidate_id > len(candidates_db):
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    return candidates_db[candidate_id - 1]

@app.get("/parser-info")
async def parser_info():
    """Get information about the parser"""
    return {
        "parser_type": "Hybrid Resume Parser",
        "methods_used": [
            "Section-based parsing",
            "Pattern recognition", 
            "Dictionary-based skill extraction",
            "Context validation",
            "Fallback mechanisms"
        ],
        "skills_database_size": len(resume_parser.skills_db),
        "supported_sections": list(resume_parser.section_headers.keys())
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")