"""
MindOS AI - Text-to-Speech Service
ElevenLabs streaming TTS for natural voice output. Falls back to text-only mode.
"""

import io
import logging
from typing import Optional, AsyncGenerator

logger = logging.getLogger(__name__)


class TTSService:
    """Text-to-Speech service using ElevenLabs API."""

    def __init__(self, api_key: str = "", voice_id: str = "EXAVITQu4vr4xnSDxMaL"):
        self.voice_id = voice_id
        self.client = None
        self._available = False

        if api_key:
            try:
                from elevenlabs.client import AsyncElevenLabs
                self.client = AsyncElevenLabs(api_key=api_key)
                self._available = True
                logger.info(f"TTS Service initialized with voice: {voice_id}")
            except Exception as e:
                logger.warning(f"TTS Service init failed: {e}")

        if not self._available:
            logger.info("TTS Service running in text-only mode (no ElevenLabs key)")

    @property
    def is_available(self) -> bool:
        return self._available

    async def synthesize(self, text: str) -> Optional[bytes]:
        """
        Convert text to speech audio bytes.

        Args:
            text: Text to synthesize

        Returns:
            Audio bytes (mp3 format) or None if unavailable
        """
        if not self._available or not text.strip():
            return None

        try:
            audio = await self.client.text_to_speech.convert(
                voice_id=self.voice_id,
                text=text,
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128",
            )

            # Collect all audio chunks
            audio_bytes = b""
            async for chunk in audio:
                audio_bytes += chunk

            logger.info(f"TTS synthesized {len(audio_bytes)} bytes for {len(text)} chars")
            return audio_bytes

        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            return None

    async def synthesize_stream(self, text: str) -> AsyncGenerator[bytes, None]:
        """
        Stream audio chunks for lower latency playback.

        Args:
            text: Text to synthesize

        Yields:
            Audio byte chunks
        """
        if not self._available or not text.strip():
            return

        try:
            audio = await self.client.text_to_speech.convert(
                voice_id=self.voice_id,
                text=text,
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128",
            )

            async for chunk in audio:
                if chunk:
                    yield chunk

        except Exception as e:
            logger.error(f"TTS streaming failed: {e}")


# Singleton
tts_service: Optional[TTSService] = None


def init_tts(api_key: str, voice_id: str = "EXAVITQu4vr4xnSDxMaL") -> TTSService:
    global tts_service
    tts_service = TTSService(api_key=api_key, voice_id=voice_id)
    return tts_service
