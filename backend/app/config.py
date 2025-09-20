from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Resume Screener"
    DEBUG_MODE: bool = True
    
    # Azure Blob Storage settings
    AZURE_STORAGE_CONNECTION_STRING: str = ""
    AZURE_CONTAINER_NAME: str = "resumes"
    
    # ML Model settings
    MODEL_PATH: str = "models/resume_ranking_model.pkl"
    
    class Config:
        env_file = ".env"

settings = Settings()