"""
MindOS AI - Mood Tracking Router
"""

import logging
from typing import List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_session, MoodEntry, User
from app.models.schemas import MoodLogRequest, MoodEntryResponse, MoodSummary

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["mood"])


@router.post("/mood", response_model=MoodEntryResponse)
async def log_mood(req: MoodLogRequest, db: AsyncSession = Depends(get_session)):
    """Log a mood entry."""
    user = await db.get(User, req.user_id)
    if not user:
        user = User(id=req.user_id)
        db.add(user)

    entry = MoodEntry(
        user_id=req.user_id,
        score=req.score,
        emotion=req.emotion,
        notes=req.notes,
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)

    return MoodEntryResponse(
        id=entry.id, score=entry.score, emotion=entry.emotion,
        notes=entry.notes, timestamp=entry.timestamp,
    )


@router.get("/mood/{user_id}", response_model=List[MoodEntryResponse])
async def get_mood_history(
    user_id: str,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_session),
):
    """Get mood history for a user."""
    since = datetime.utcnow() - timedelta(days=days)
    result = await db.execute(
        select(MoodEntry)
        .where(MoodEntry.user_id == user_id, MoodEntry.timestamp >= since)
        .order_by(MoodEntry.timestamp.desc())
    )
    entries = result.scalars().all()
    return [MoodEntryResponse(id=e.id, score=e.score, emotion=e.emotion,
                              notes=e.notes, timestamp=e.timestamp) for e in entries]


@router.get("/mood/{user_id}/summary", response_model=MoodSummary)
async def get_mood_summary(user_id: str, db: AsyncSession = Depends(get_session)):
    """Get AI-generated mood summary."""
    result = await db.execute(
        select(MoodEntry)
        .where(MoodEntry.user_id == user_id)
        .order_by(MoodEntry.timestamp.desc())
        .limit(30)
    )
    entries = result.scalars().all()

    if not entries:
        return MoodSummary(average_score=0, trend="stable",
                          dominant_emotion="neutral", entries_count=0)

    scores = [e.score for e in entries]
    avg = sum(scores) / len(scores)

    # Determine trend
    if len(scores) >= 3:
        recent = sum(scores[:3]) / 3
        older = sum(scores[-3:]) / 3
        if recent > older + 0.5:
            trend = "improving"
        elif recent < older - 0.5:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "stable"

    # Dominant emotion
    emotions = [e.emotion for e in entries if e.emotion]
    dominant = max(set(emotions), key=emotions.count) if emotions else "neutral"

    # AI summary
    ai_summary = None
    from app.services.llm_service import llm_service
    if llm_service and llm_service.is_available:
        mood_data = [{"score": e.score, "emotion": e.emotion,
                     "date": e.timestamp.isoformat()} for e in entries[:15]]
        ai_summary = await llm_service.generate_mood_summary(mood_data)

    return MoodSummary(
        average_score=round(avg, 1), trend=trend,
        dominant_emotion=dominant, entries_count=len(entries),
        ai_summary=ai_summary,
    )
