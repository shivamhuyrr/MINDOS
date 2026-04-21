"""
MindOS AI - LLM Service
GPT-4o integration with empathetic therapy system prompt, memory injection, and function calling.
"""

import json
import logging
from typing import Optional, List, Dict, AsyncGenerator

logger = logging.getLogger(__name__)


class LLMService:
    """GPT-4o powered empathetic conversation engine."""

    def __init__(self, api_key: str = "", model: str = "gpt-4o"):
        self.model = model
        self.client = None
        self._available = False
        self._conversation_histories: Dict[str, List[dict]] = {}
        self._max_history = 20  # Keep last 20 messages per user

        if api_key:
            try:
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(api_key=api_key)
                self._available = True
                logger.info(f"LLM Service initialized with model: {model}")
            except Exception as e:
                logger.warning(f"LLM Service init failed: {e}")

        if not self._available:
            logger.info("LLM Service running in mock mode")

    @property
    def is_available(self) -> bool:
        return self._available

    def _build_system_prompt(
        self,
        base_prompt: str,
        memories: List[str] = None,
        emotion: str = "neutral",
        emotion_intensity: float = 0.0,
        emotion_modifier: str = "",
        user_name: str = "",
    ) -> str:
        """Build the full system prompt with context injection."""
        from app.prompts.system_prompts import MEMORY_CONTEXT_TEMPLATE

        # Build memory section
        memory_text = "No previous conversations recorded yet."
        if memories:
            memory_text = "\n".join(f"- {m}" for m in memories[:5])

        # Build context
        context = MEMORY_CONTEXT_TEMPLATE.format(
            memories=memory_text,
            emotion=emotion,
            intensity=f"{emotion_intensity:.1%}",
            recent_history="(See message history below)",
        )

        if user_name:
            context += f"\nThe user's name is: {user_name}\n"

        if emotion_modifier:
            context += f"\n## Tone Guidance\n{emotion_modifier}\n"

        return base_prompt.format(context=context)

    def _get_history(self, user_id: str) -> List[dict]:
        """Get conversation history for a user, creating if needed."""
        if user_id not in self._conversation_histories:
            self._conversation_histories[user_id] = []
        return self._conversation_histories[user_id]

    def _trim_history(self, user_id: str):
        """Keep conversation history within limits."""
        history = self._get_history(user_id)
        if len(history) > self._max_history * 2:
            self._conversation_histories[user_id] = history[-(self._max_history * 2):]

    async def generate_response(
        self,
        user_id: str,
        message: str,
        system_prompt: str,
        memories: List[str] = None,
        emotion: str = "neutral",
        emotion_intensity: float = 0.0,
        emotion_modifier: str = "",
        user_name: str = "",
    ) -> str:
        """
        Generate an empathetic response using GPT-4o.

        Args:
            user_id: Unique user identifier
            message: User's current message
            system_prompt: Base system prompt
            memories: Retrieved past memories
            emotion: Detected emotion label
            emotion_intensity: Emotion intensity 0-1
            emotion_modifier: Additional tone guidance
            user_name: User's name if known

        Returns:
            AI companion response text
        """
        if not self._available:
            return self._mock_response(message)

        try:
            # Build full system prompt with context
            full_system = self._build_system_prompt(
                system_prompt, memories, emotion, emotion_intensity,
                emotion_modifier, user_name,
            )

            # Get and update conversation history
            history = self._get_history(user_id)
            history.append({"role": "user", "content": message})

            # Build messages array
            messages = [
                {"role": "system", "content": full_system},
                *history,
            ]

            # Call GPT-4o
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.8,
                max_tokens=500,
                presence_penalty=0.3,
                frequency_penalty=0.3,
            )

            reply = response.choices[0].message.content.strip()

            # Store assistant reply in history
            history.append({"role": "assistant", "content": reply})
            self._trim_history(user_id)

            logger.info(f"LLM generated response ({len(reply)} chars)")
            return reply

        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return "I'm having a moment — could you say that again? I want to make sure I understand you."

    async def generate_stream(
        self,
        user_id: str,
        message: str,
        system_prompt: str,
        memories: List[str] = None,
        emotion: str = "neutral",
        emotion_intensity: float = 0.0,
        emotion_modifier: str = "",
        user_name: str = "",
    ) -> AsyncGenerator[str, None]:
        """Stream response tokens for lower latency."""
        if not self._available:
            yield self._mock_response(message)
            return

        try:
            full_system = self._build_system_prompt(
                system_prompt, memories, emotion, emotion_intensity,
                emotion_modifier, user_name,
            )

            history = self._get_history(user_id)
            history.append({"role": "user", "content": message})

            messages = [
                {"role": "system", "content": full_system},
                *history,
            ]

            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.8,
                max_tokens=500,
                presence_penalty=0.3,
                frequency_penalty=0.3,
                stream=True,
            )

            full_reply = ""
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    full_reply += token
                    yield token

            history.append({"role": "assistant", "content": full_reply})
            self._trim_history(user_id)

        except Exception as e:
            logger.error(f"LLM streaming failed: {e}")
            yield "I'm having a moment — could you say that again?"

    async def generate_mood_summary(self, mood_data: List[dict]) -> str:
        """Generate an AI summary of mood trends."""
        if not self._available:
            return "Mood tracking is active. Connect OpenAI API for AI-powered insights."

        try:
            prompt = f"""Analyze these mood entries and provide a brief, compassionate summary of trends.
            Be encouraging and note any patterns. Keep it under 3 sentences.

            Mood data: {json.dumps(mood_data[:30])}"""

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a caring wellness analyst. Be warm and encouraging."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=200,
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Mood summary generation failed: {e}")
            return "Unable to generate summary at this time."

    def clear_history(self, user_id: str):
        """Clear conversation history for a user."""
        self._conversation_histories.pop(user_id, None)

    def _mock_response(self, message: str) -> str:
        """Return a warm mock response for development."""
        responses = [
            "I hear you. That's a really valid feeling, and I appreciate you sharing it with me. What else is on your mind?",
            "Thank you for opening up. It takes courage to talk about how you're feeling. Would you like to explore that a bit more?",
            "I'm glad you felt comfortable enough to share that. Let's take a moment — what do you think would help right now?",
            "That sounds like it's weighing on you. Remember, it's okay to not have all the answers right away. I'm here with you.",
        ]
        import hashlib
        idx = int(hashlib.md5(message.encode()).hexdigest(), 16) % len(responses)
        return f"[Demo Mode] {responses[idx]}"


# Singleton
llm_service: Optional[LLMService] = None


def init_llm(api_key: str, model: str = "gpt-4o") -> LLMService:
    global llm_service
    llm_service = LLMService(api_key=api_key, model=model)
    return llm_service
