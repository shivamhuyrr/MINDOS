"""
MindOS AI - Emotion Detection Service
Text-based sentiment/emotion analysis using a lightweight transformer model.
Falls back to keyword-based detection when model is unavailable.
"""

import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

# Keyword-based fallback emotion detection
EMOTION_KEYWORDS = {
    "joy": ["happy", "glad", "excited", "wonderful", "great", "amazing", "love", "grateful", "blessed", "thrilled", "awesome"],
    "sadness": ["sad", "depressed", "lonely", "hopeless", "crying", "hurt", "miserable", "empty", "lost", "heartbroken", "grief"],
    "anger": ["angry", "frustrated", "furious", "annoyed", "irritated", "mad", "rage", "hate", "pissed", "resentful"],
    "fear": ["afraid", "scared", "anxious", "worried", "nervous", "panic", "terrified", "dread", "phobia", "overwhelmed", "stressed"],
    "surprise": ["surprised", "shocked", "amazed", "unexpected", "wow", "unbelievable", "astonished", "stunned"],
    "disgust": ["disgusted", "gross", "revolting", "sick", "repulsed", "awful", "terrible", "nasty"],
}


class EmotionService:
    """Text emotion detection with HuggingFace model or keyword fallback."""

    def __init__(self, use_model: bool = True):
        self.classifier = None
        self._model_available = False

        if use_model:
            try:
                from transformers import pipeline
                self.classifier = pipeline(
                    "text-classification",
                    model="j-hartmann/emotion-english-distilroberta-base",
                    top_k=None,
                    device=-1,  # CPU
                )
                self._model_available = True
                logger.info("Emotion Service: transformer model loaded")
            except Exception as e:
                logger.warning(f"Emotion model load failed, using keyword fallback: {e}")

        if not self._model_available:
            logger.info("Emotion Service: using keyword-based detection")

    def detect(self, text: str) -> Dict:
        """
        Detect emotion from text.

        Returns:
            {"emotion": str, "intensity": float, "valence": float, "all_scores": dict}
        """
        if not text or not text.strip():
            return {"emotion": "neutral", "intensity": 0.0, "valence": 0.0, "all_scores": {}}

        if self._model_available:
            return self._model_detect(text)
        return self._keyword_detect(text)

    def _model_detect(self, text: str) -> Dict:
        try:
            results = self.classifier(text[:512])[0]
            scores = {r["label"]: r["score"] for r in results}
            top = max(results, key=lambda x: x["score"])

            valence_map = {"joy": 0.8, "surprise": 0.3, "neutral": 0.0,
                          "sadness": -0.6, "fear": -0.5, "anger": -0.7, "disgust": -0.8}

            return {
                "emotion": top["label"],
                "intensity": round(top["score"], 3),
                "valence": valence_map.get(top["label"], 0.0),
                "all_scores": {k: round(v, 3) for k, v in scores.items()},
            }
        except Exception as e:
            logger.error(f"Model emotion detection failed: {e}")
            return self._keyword_detect(text)

    def _keyword_detect(self, text: str) -> Dict:
        text_lower = text.lower()
        scores = {}
        for emotion, keywords in EMOTION_KEYWORDS.items():
            count = sum(1 for kw in keywords if kw in text_lower)
            if count > 0:
                scores[emotion] = min(count * 0.3, 1.0)

        if not scores:
            return {"emotion": "neutral", "intensity": 0.0, "valence": 0.0, "all_scores": {}}

        top_emotion = max(scores, key=scores.get)
        valence_map = {"joy": 0.8, "surprise": 0.3, "neutral": 0.0,
                      "sadness": -0.6, "fear": -0.5, "anger": -0.7, "disgust": -0.8}

        return {
            "emotion": top_emotion,
            "intensity": round(scores[top_emotion], 3),
            "valence": valence_map.get(top_emotion, 0.0),
            "all_scores": scores,
        }


emotion_service: Optional[EmotionService] = None

def init_emotion(use_model: bool = True) -> EmotionService:
    global emotion_service
    emotion_service = EmotionService(use_model=use_model)
    return emotion_service
