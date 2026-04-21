"""
MindOS AI - Application Configuration
"""

import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    CORS_ORIGINS: str = "http://localhost:3000"
    OPENAI_API_KEY: str = ""
    GPT_MODEL: str = "gpt-4o"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
