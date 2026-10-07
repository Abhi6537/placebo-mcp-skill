"""
Google Gemini / Gemma provider using official google-genai SDK.
"""

import json
import os
from typing import Dict, Optional
from placebo.models.evidence import EvidencePackage, GroundedExplanation
from placebo.llm.guardrails import validate_explanation
from placebo.llm.prompts import SYSTEM_PROMPT, build_evidence_prompt

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class GeminiProvider:
    """Explains Evidence Packages using Google Gemini/Gemma models."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = os.getenv("GEMINI_MODEL", model)
        self._client = None
        if GENAI_AVAILABLE and self.api_key:
            self._client = genai.Client(api_key=self.api_key)

    def is_available(self) -> bool:
        return bool(GENAI_AVAILABLE and self._client)

    def explain(self, package: EvidencePackage) -> GroundedExplanation:
        if not self.is_available():
            raise RuntimeError(
                "Gemini provider not configured or GEMINI_API_KEY missing. "
                "Set GEMINI_API_KEY in your .env file or use Ollama provider."
            )

        prompt = build_evidence_prompt(package)
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.2,
            response_mime_type="application/json"
        )

        response = self._client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=config
        )

        try:
            parsed = json.loads(response.text)
        except Exception:
            parsed = {
                "headline": package.verdict.summary,
                "what_was_tested": package.hypothesis.claim_description,
                "what_was_observed": f"Effect: {package.statistical_result.effect_size}",
                "falsification_checks_summary": "Tests evaluated.",
                "verdict_explanation": package.verdict.summary,
                "recommended_action": package.verdict.recommendation
            }

        return validate_explanation(package, parsed, f"gemini:{self.model}")
