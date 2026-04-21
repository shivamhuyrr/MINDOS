"""
MindOS AI - Application Configuration
Loads settings from environment variables with sensible defaults.
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    # ── App ──────────────────────────────────────────────
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    # ── OpenAI ───────────────────────────────────────────
    OPENAI_API_KEY: str = ""
    GPT_MODEL: str = "gpt-4o"
    WHISPER_MODEL: str = "whisper-1"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS: int = 1536

    # ── ElevenLabs ───────────────────────────────────────
    ELEVENLABS_API_KEY: str = ""
    ELEVENLABS_VOICE_ID: str = "EXAVITQu4vr4xnSDxMaL"  # "Sarah"

    # ── Pinecone ─────────────────────────────────────────
    PINECONE_API_KEY: str = ""
    PINECONE_INDEX_NAME: str = "mindos-memory"
    PINECONE_ENVIRONMENT: str = "us-east-1"

    # ── Database ─────────────────────────────────────────
    DATABASE_URL: str = "sqlite+aiosqlite:///./mindos.db"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def has_openai(self) -> bool:
        return bool(self.OPENAI_API_KEY and self.OPENAI_API_KEY != "sk-your-openai-api-key-here")

    @property
    def has_elevenlabs(self) -> bool:
        return bool(self.ELEVENLABS_API_KEY and self.ELEVENLABS_API_KEY != "your-elevenlabs-api-key-here")

    @property
    def has_pinecone(self) -> bool:
        return bool(self.PINECONE_API_KEY and self.PINECONE_API_KEY != "your-pinecone-api-key-here")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Singleton settings instance
settings = Settings()
