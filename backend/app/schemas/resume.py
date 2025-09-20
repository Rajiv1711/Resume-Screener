from pydantic import BaseModel
from typing import List, Optional, Dict

class ResumeResponse(BaseModel):
    resume_id: str
    status: str
    filename: Optional[str] = None
    extracted_data: Optional[Dict] = None

class RankingRequest(BaseModel):
    job_description: str
    resume_ids: List[str]

class RankingScore(BaseModel):
    resume_id: str
    score: float
    matching_skills: List[str] = []

class RankingResponse(BaseModel):
    rankings: List[RankingScore]