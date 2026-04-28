"""
MindOS AI - Chat Router (REST text-based chat)
"""

import logging
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schemas import ChatRequest, ChatResponse, EmotionResult, CrisisAlert
from app.models.database import get_session, User, ChatSession, ChatMessage
from app.prompts.system_prompts import COMPANION_SYSTEM_PROMPT, EMOTION_MODIFIERS
from app.services.llm_service import llm_service
from app.services.memory_service import memory_service
from app.services.emotion_service import emotion_service
from app.services.crisis_service import crisis_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, db: AsyncSession = Depends(get_session)):
    """Process a text chat message through the full AI pipeline."""

    # 1. Ensure user exists
    user = await db.get(User, req.user_id)
    if not user:
        user = User(id=req.user_id)
        db.add(user)
        await db.commit()

    # 2. Get or create session
    session_id = req.session_id
    if not session_id:
        session = ChatSession(user_id=req.user_id)
        db.add(session)
        await db.commit()
        session_id = session.id

    # 3. Detect emotion
    emo = {"emotion": "neutral", "intensity": 0.0, "valence": 0.0}
    if emotion_service:
        emo = emotion_service.detect(req.message)

    # 4. Check for crisis
    crisis = {"level": "none", "matched": [], "resources": [], "message": None}
    if crisis_service:
        crisis = crisis_service.assess(req.message)

    # 5. Recall memories
    memories = []
    memories_count = 0
    if memory_service:
        memories = await memory_service.recall_memories(req.user_id, req.message, top_k=5)
        memories_count = len(memories)

    # 6. Generate response
    reply = ""
    if crisis["level"] in ("critical", "high") and crisis.get("message"):
        reply = crisis["message"]
    elif llm_service:
        modifier = EMOTION_MODIFIERS.get(emo["emotion"], "")
        reply = await llm_service.generate_response(
            user_id=req.user_id,
            message=req.message,
            system_prompt=COMPANION_SYSTEM_PROMPT,
            memories=memories,
            emotion=emo["emotion"],
            emotion_intensity=emo["intensity"],
            emotion_modifier=modifier,
            user_name=user.name or "",
        )
    else:
        reply = "I'm here for you. [Configure API keys to enable AI responses]"

    # 7. Store memory
    if memory_service:
        await memory_service.store_memory(
            user_id=req.user_id,
            text=req.message,
            emotion=emo["emotion"],
            session_id=session_id,
        )

    # 8. Save messages to DB
    user_msg = ChatMessage(session_id=session_id, role="user", content=req.message,
                           emotion=emo["emotion"], emotion_score=emo["intensity"],
                           crisis_level=crisis["level"])
    bot_msg = ChatMessage(session_id=session_id, role="assistant", content=reply)
    db.add_all([user_msg, bot_msg])
    await db.commit()

    return ChatResponse(
        reply=reply,
        emotion=EmotionResult(emotion=emo["emotion"], intensity=emo["intensity"], valence=emo["valence"]),
        crisis=CrisisAlert(level=crisis["level"], message=crisis.get("message"),
                           resources=crisis.get("resources", [])),
        session_id=session_id,
        memories_used=memories_count,
    )
