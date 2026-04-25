"""
MindOS AI - Speech-to-Text Service
Uses OpenAI Whisper API for transcription. Falls back to mock for development.
"""

import io
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class STTService:
    """Speech-to-Text service using OpenAI Whisper API."""

    def __init__(self, api_key: str = "", model: str = "whisper-1"):
        self.model = model
        self.client = None
        self._available = False

        if api_key:
            try:
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(api_key=api_key)
                self._available = True
                logger.info("STT Service initialized with OpenAI Whisper API")
            except Exception as e:
                logger.warning(f"STT Service: OpenAI client init failed: {e}")

        if not self._available:
            logger.info("STT Service running in mock mode (no API key)")

    @property
    def is_available(self) -> bool:
        return self._available

    async def transcribe(self, audio_bytes: bytes, language: str = "en") -> Tuple[str, str]:
        """
        Transcribe audio bytes to text.

        Args:
            audio_bytes: Raw audio data (webm/opus/wav format)
            language: Expected language code

        Returns:
            Tuple of (transcribed_text, detected_language)
        """
        if not self._available:
            return self._mock_transcribe()

        try:
            # Create a file-like object from bytes
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = "audio.webm"

            response = await self.client.audio.transcriptions.create(
                model=self.model,
                file=audio_file,
                language=language,
                response_format="text",
            )

            text = response.strip() if isinstance(response, str) else response.text.strip()
            logger.info(f"STT transcribed: '{text[:100]}...'")
            return text, language

        except Exception as e:
            logger.error(f"STT transcription failed: {e}")
            return "", language

    def _mock_transcribe(self) -> Tuple[str, str]:
        """Return mock transcription for development without API key."""
        return "[Mock: Voice input received - configure OPENAI_API_KEY for real transcription]", "en"


# Singleton instance (initialized in main.py)
stt_service: Optional[STTService] = None


def init_stt(api_key: str, model: str = "whisper-1") -> STTService:
    global stt_service
    stt_service = STTService(api_key=api_key, model=model)
    return stt_service
