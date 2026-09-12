from typing import List
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "MEDLOCK AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "medlock-super-secret-production-key-change-in-prod-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./medlock.db")
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    
    # AI Risk Engine Configurable Weights & Thresholds
    RISK_WEIGHT_EXCEEDS_QTY: int = 25
    RISK_WEIGHT_RAPID_SWITCHING: int = 25   # >= 2 pharmacies in < 2 hours
    RISK_WEIGHT_MULTI_PROVIDER: int = 20    # >= 3 pharmacies in < 24 hours
    RISK_WEIGHT_RECENT_REJECTIONS: int = 20 # >= 2 rejections in last 48h
    RISK_WEIGHT_REATTEMPT_AFTER_DENIAL: int = 30 # reattempt within 30 min of rejection
    RISK_WEIGHT_ONLINE_PHYSICAL_BURST: int = 15  # online within 1h of physical
    
    # Risk Score Level Thresholds
    RISK_THRESHOLD_LOW_MAX: int = 24
    RISK_THRESHOLD_MEDIUM_MAX: int = 49
    RISK_THRESHOLD_HIGH_MAX: int = 74
    # 75-100 = CRITICAL
    
    # Gemini / LLM API Key (optional fallback to built-in structured reasoning)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    model_config = {"case_sensitive": True}


settings = Settings()
