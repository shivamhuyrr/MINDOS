"""
MindOS AI - Pydantic Schemas
Request/response models for all API endpoints.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ── Chat ─────────────────────────────────────────────────

class ChatRequest(BaseModel):
    user_id: str = Field(..., description="Unique user identifier")
    message: str = Field(..., description="User's text message")
    session_id: Optional[str] = Field(None, description="Chat session ID (auto-created if empty)")


class EmotionResult(BaseModel):
    emotion: str = Field("neutral", description="Detected emotion label")
    intensity: float = Field(0.0, description="Emotion intensity 0-1")
    valence: float = Field(0.0, description="Emotional valence -1 to 1")


class CrisisAlert(BaseModel):
    level: str = Field("none", description="Crisis severity: none|low|moderate|high|critical")
    message: Optional[str] = Field(None, description="Safety response message")
    resources: List[str] = Field(default_factory=list, description="Crisis hotline numbers")


class ChatResponse(BaseModel):
    reply: str = Field(..., description="AI companion response")
    emotion: EmotionResult = Field(default_factory=EmotionResult)
    crisis: CrisisAlert = Field(default_factory=CrisisAlert)
    session_id: str = Field(..., description="Chat session ID")
    memories_used: int = Field(0, description="Number of past memories referenced")


# ── Mood ─────────────────────────────────────────────────

class MoodLogRequest(BaseModel):
    user_id: str
    score: int = Field(..., ge=1, le=10, description="Mood score 1-10")
    emotion: Optional[str] = None
    notes: Optional[str] = None


class MoodEntryResponse(BaseModel):
    id: str
    score: int
    emotion: Optional[str]
    notes: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True


class MoodSummary(BaseModel):
    average_score: float
    trend: str  # "improving" | "declining" | "stable"
    dominant_emotion: str
    entries_count: int
    ai_summary: Optional[str] = None


# ── User ─────────────────────────────────────────────────

class UserCreate(BaseModel):
    name: Optional[str] = None
    consent_given: bool = False


class UserProfile(BaseModel):
    id: str
    name: Optional[str]
    created_at: datetime
    consent_given: bool
    total_sessions: int = 0
    total_mood_entries: int = 0

    class Config:
        from_attributes = True


# ── Voice / WebSocket ────────────────────────────────────

class VoiceMessage(BaseModel):
    """Message format for WebSocket communication."""
    type: str  # "audio" | "text" | "status" | "error"
    data: Optional[str] = None  # base64 audio or text content
    metadata: Optional[dict] = None


# ── Health ───────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
    services: dict = Field(default_factory=dict)
