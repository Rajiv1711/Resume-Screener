from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from app.services import resume_service
from app.core.security import get_current_user

router = APIRouter()

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    try:
        result = await resume_service.upload_resume(file, current_user)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/analyze")
async def analyze_resumes(
    job_description: str,
    resume_ids: List[str],
    current_user = Depends(get_current_user)
):
    try:
        result = await resume_service.analyze_resumes(
            job_description,
            resume_ids,
            current_user
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))