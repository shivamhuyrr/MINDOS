"""
MindOS AI - Voice WebSocket Router
Real-time voice conversation: audio in → STT → emotion → memory → LLM → TTS → audio out
"""

import json
import base64
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.prompts.system_prompts import COMPANION_SYSTEM_PROMPT, EMOTION_MODIFIERS
from app.services.stt_service import stt_service
from app.services.llm_service import llm_service
from app.services.tts_service import tts_service
from app.services.memory_service import memory_service
from app.services.emotion_service import emotion_service
from app.services.crisis_service import crisis_service

logger = logging.getLogger(__name__)
router = APIRouter(tags=["voice"])


class ConnectionManager:
    """Manage active WebSocket connections."""

    def __init__(self):
        self.active: dict = {}

    async def connect(self, ws: WebSocket, user_id: str):
        await ws.accept()
        self.active[user_id] = ws
        logger.info(f"Voice connected: {user_id}")

    def disconnect(self, user_id: str):
        self.active.pop(user_id, None)
        logger.info(f"Voice disconnected: {user_id}")

    async def send_json(self, ws: WebSocket, data: dict):
        await ws.send_text(json.dumps(data))


manager = ConnectionManager()


@router.websocket("/ws/voice/{user_id}")
async def voice_stream(ws: WebSocket, user_id: str):
    """WebSocket endpoint for real-time voice conversation."""
    await manager.connect(ws, user_id)

    try:
        # Send ready signal
        await manager.send_json(ws, {
            "type": "status", "data": "connected",
            "tts_available": tts_service is not None and tts_service.is_available,
        })

        while True:
            raw = await ws.receive()

            # Handle text messages (JSON commands or text chat)
            if "text" in raw:
                msg = json.loads(raw["text"])
                msg_type = msg.get("type", "text")

                if msg_type == "text":
                    await _process_text(ws, user_id, msg.get("data", ""))
                elif msg_type == "ping":
                    await manager.send_json(ws, {"type": "pong"})

            # Handle binary audio data
            elif "bytes" in raw:
                audio_bytes = raw["bytes"]
                await _process_audio(ws, user_id, audio_bytes)

    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        logger.error(f"Voice WebSocket error for {user_id}: {e}")
        manager.disconnect(user_id)


async def _process_audio(ws: WebSocket, user_id: str, audio_bytes: bytes):
    """Process audio: STT → pipeline → TTS."""
    try:
        # Notify: processing
        await manager.send_json(ws, {"type": "status", "data": "processing"})

        # 1. Speech-to-Text
        text = ""
        if stt_service and stt_service.is_available:
            text, lang = await stt_service.transcribe(audio_bytes)
        if not text:
            await manager.send_json(ws, {
                "type": "error", "data": "Could not transcribe audio. Please try again."
            })
            return

        # Send transcription to client
        await manager.send_json(ws, {"type": "transcription", "data": text})

        # 2-6. Process through pipeline
        await _run_pipeline(ws, user_id, text)

    except Exception as e:
        logger.error(f"Audio processing error: {e}")
        await manager.send_json(ws, {"type": "error", "data": "Processing error. Please try again."})


async def _process_text(ws: WebSocket, user_id: str, text: str):
    """Process text message through pipeline."""
    if not text.strip():
        return
    await manager.send_json(ws, {"type": "status", "data": "processing"})
    await _run_pipeline(ws, user_id, text)


async def _run_pipeline(ws: WebSocket, user_id: str, text: str):
    """Core pipeline: emotion → crisis → memory → LLM → TTS."""
    try:
        # 2. Emotion detection
        emo = {"emotion": "neutral", "intensity": 0.0, "valence": 0.0}
        if emotion_service:
            emo = emotion_service.detect(text)
        await manager.send_json(ws, {"type": "emotion", "data": emo})

        # 3. Crisis check
        crisis = {"level": "none", "resources": [], "message": None}
        if crisis_service:
            crisis = crisis_service.assess(text)

        if crisis["level"] in ("critical", "high"):
            await manager.send_json(ws, {
                "type": "crisis",
                "data": {"level": crisis["level"], "resources": crisis.get("resources", [])},
            })

        # 4. Recall memories
        memories = []
        if memory_service:
            memories = await memory_service.recall_memories(user_id, text, top_k=5)

        # 5. Generate response
        if crisis["level"] in ("critical", "high") and crisis.get("message"):
            reply = crisis["message"]
        elif llm_service:
            modifier = EMOTION_MODIFIERS.get(emo["emotion"], "")
            reply = await llm_service.generate_response(
                user_id=user_id, message=text,
                system_prompt=COMPANION_SYSTEM_PROMPT,
                memories=memories, emotion=emo["emotion"],
                emotion_intensity=emo["intensity"],
                emotion_modifier=modifier,
            )
        else:
            reply = "I hear you. [Configure API keys for full AI responses]"

        # Send text reply
        await manager.send_json(ws, {
            "type": "reply",
            "data": reply,
            "memories_used": len(memories),
        })

        # 6. TTS — send audio if available
        if tts_service and tts_service.is_available:
            await manager.send_json(ws, {"type": "status", "data": "speaking"})
            audio = await tts_service.synthesize(reply)
            if audio:
                audio_b64 = base64.b64encode(audio).decode("utf-8")
                await manager.send_json(ws, {"type": "audio", "data": audio_b64})

        # 7. Store memory
        if memory_service:
            await memory_service.store_memory(
                user_id=user_id, text=text, emotion=emo["emotion"],
            )

        await manager.send_json(ws, {"type": "status", "data": "idle"})

    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        await manager.send_json(ws, {"type": "error", "data": str(e)})
