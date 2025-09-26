from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ExperienceModel(BaseModel):
    job_title: str
    company: str
    duration: str
    description: str

class ResumeData(BaseModel):
    skills: List[str] = Field(..., description="List of extracted skills")
    experience: List[ExperienceModel] = Field(..., description="List of work experiences")

class CandidateBase(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    raw_text: str

class CandidateCreate(CandidateBase):
    pass

class Candidate(CandidateBase):
    id: int
    parsed_skills: List[str]
    parsed_experience: List[dict]
    created_at: datetime
    
    class Config:
        from_attributes = True