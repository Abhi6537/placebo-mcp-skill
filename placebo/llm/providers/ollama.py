"""
Ollama Provider for 100% free, local offline execution of Gemma 2/3.
"""

import json
import os
from typing import Optional
import httpx

from placebo.models.evidence import EvidencePackage, GroundedExplanation
from placebo.llm.guardrails import validate_explanation
from placebo.llm.prompts import SYSTEM_PROMPT, build_evidence_prompt


class OllamaProvider:
    """Local provider calling Ollama REST API on localhost:11434."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: str = "gemma2:27b",
        timeout: float = 30.0
    ):
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", model)
        self.timeout = timeout

    def is_available(self) -> bool:
        try:
            r = httpx.get(f"{self.base_url}/api/tags", timeout=1.5)
            return r.status_code == 200
        except Exception:
            return False

    def explain(self, package: EvidencePackage) -> GroundedExplanation:
        prompt = build_evidence_prompt(package)
        full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"

        try:
            r = httpx.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "format": "json",
                    "stream": False,
                    "options": {"temperature": 0.2}
                },
                timeout=self.timeout
            )
            r.raise_for_status()
            res_json = r.json()
            raw_text = res_json.get("response", "{}")
            parsed = json.loads(raw_text)
        except Exception as e:
            # Fallback
            parsed = {
                "headline": package.verdict.summary,
                "what_was_tested": package.hypothesis.claim_description,
                "what_was_observed": f"Effect: {package.statistical_result.effect_size}",
                "falsification_checks_summary": f"Ollama connection note: {e}",
                "verdict_explanation": package.verdict.summary,
                "recommended_action": package.verdict.recommendation
            }

        return validate_explanation(package, parsed, f"ollama:{self.model}")
