"""
MindOS AI - Crisis Detection Service
Detects self-harm, suicidal ideation, and abuse signals with severity scoring.
"""

import re
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

# Crisis keyword patterns organized by severity
CRISIS_PATTERNS = {
    "critical": [
        r"\b(kill\s+my\s*self|suicide|end\s+(my|it\s+all)|want\s+to\s+die|no\s+reason\s+to\s+live)\b",
        r"\b(overdose|slit|jump\s+off|hang\s+my\s*self|shoot\s+my\s*self)\b",
        r"\b(goodbye\s+forever|final\s+note|last\s+message|no\s+one\s+will\s+miss)\b",
    ],
    "high": [
        r"\b(self[\s-]*harm|cutting\s+my\s*self|hurt\s+my\s*self|don'?t\s+want\s+to\s+be\s+here)\b",
        r"\b(can'?t\s+go\s+on|can'?t\s+take\s+it|life\s+is\s+(pointless|meaningless))\b",
        r"\b(better\s+off\s+(dead|without\s+me)|nothing\s+matters)\b",
    ],
    "moderate": [
        r"\b(hopeless|worthless|useless|burden|trapped|suffocating)\b",
        r"\b(no\s+point|give\s+up|can'?t\s+cope|falling\s+apart)\b",
        r"\b(abuse|abused|violent|assault|domestic\s+violence)\b",
    ],
    "low": [
        r"\b(overwhelmed|exhausted|burned?\s*out|breaking\s+down)\b",
        r"\b(lonely|isolated|no\s+one\s+(cares|understands))\b",
        r"\b(hate\s+my\s+(life|self)|miserable|suffering)\b",
    ],
}

# Crisis resources by region
CRISIS_RESOURCES = {
    "global": [
        "🆘 Emergency: Call your local emergency number",
    ],
    "india": [
        "📞 AASRA: 9820466726 (24/7)",
        "📞 Vandrevala Foundation: 1860-2662-345 (24/7)",
        "📞 iCall: 9152987821",
        "📞 NIMHANS: 080-46110007",
    ],
    "us": [
        "📞 988 Suicide & Crisis Lifeline: Call or text 988",
        "📞 Crisis Text Line: Text HOME to 741741",
    ],
    "uk": [
        "📞 Samaritans: 116 123 (24/7, free)",
        "📞 Crisis Text Line UK: Text SHOUT to 85258",
    ],
}


class CrisisService:
    """Detects crisis signals and provides appropriate safety responses."""

    def __init__(self):
        # Pre-compile patterns for performance
        self._patterns = {}
        for level, patterns in CRISIS_PATTERNS.items():
            self._patterns[level] = [re.compile(p, re.IGNORECASE) for p in patterns]
        logger.info("Crisis Service initialized")

    def assess(self, text: str) -> Dict:
        """
        Assess text for crisis signals.

        Returns:
            {"level": str, "matched": list, "resources": list, "message": str}
        """
        if not text:
            return {"level": "none", "matched": [], "resources": [], "message": None}

        severity_order = ["critical", "high", "moderate", "low"]
        all_matched = []
        highest_level = "none"

        for level in severity_order:
            for pattern in self._patterns[level]:
                matches = pattern.findall(text)
                if matches:
                    all_matched.extend(matches)
                    if highest_level == "none":
                        highest_level = level

        if highest_level == "none":
            return {"level": "none", "matched": [], "resources": [], "message": None}

        resources = self._get_resources(highest_level)
        message = self._get_response_message(highest_level)

        logger.warning(f"Crisis detected: level={highest_level}, matched={all_matched[:3]}")

        return {
            "level": highest_level,
            "matched": all_matched[:5],
            "resources": resources,
            "message": message,
        }

    def _get_resources(self, level: str) -> List[str]:
        if level in ("critical", "high"):
            r = CRISIS_RESOURCES["global"] + CRISIS_RESOURCES["india"] + CRISIS_RESOURCES["us"] + CRISIS_RESOURCES["uk"]
            return r
        elif level == "moderate":
            return CRISIS_RESOURCES["india"] + CRISIS_RESOURCES["us"]
        return []

    def _get_response_message(self, level: str) -> str:
        from app.prompts.system_prompts import (
            CRISIS_RESPONSE_CRITICAL, CRISIS_RESPONSE_HIGH, CRISIS_RESPONSE_MODERATE
        )
        if level == "critical":
            return CRISIS_RESPONSE_CRITICAL
        elif level == "high":
            return CRISIS_RESPONSE_HIGH
        elif level == "moderate":
            return CRISIS_RESPONSE_MODERATE
        return None


crisis_service: CrisisService = None

def init_crisis() -> CrisisService:
    global crisis_service
    crisis_service = CrisisService()
    return crisis_service
