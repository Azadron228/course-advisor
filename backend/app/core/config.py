import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # Core
    PROJECT_NAME: str = "Course Advisor"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Database
    DATABASE_URL: str = "postgresql://advisor:advisor_password@db:5432/course_advisor"
    TESTING: bool = False

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # External APIs
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    TAVILY_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

settings = Settings()
