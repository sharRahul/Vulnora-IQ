from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class AssistantSettings:
    provider: str
    model: str
    temperature: float
    system_prompt: str
    max_tokens: int


class AssistantOrchestrator:
    DEFAULT_SYSTEM_PROMPT = "Provide concise evidence-grounded guidance for authorised internal assessment work."

    def __init__(self) -> None:
        self.provider = os.getenv("VULNORAIQ_ASSISTANT_PROVIDER", "local").strip().lower()
        self.default_model = os.getenv("VULNORAIQ_ASSISTANT_MODEL", "vulnoraiq-local-assistant").strip()
        self.allowed_models = {
            item.strip()
            for item in os.getenv("VULNORAIQ_ASSISTANT_ALLOWED_MODELS", self.default_model).split(",")
            if item.strip()
        }

    def available_config(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "default_model": self.default_model,
            "allowed_models": sorted(self.allowed_models),
            "default_temperature": 0.2,
            "default_system_prompt": self.DEFAULT_SYSTEM_PROMPT,
            "streaming_supported": False,
        }

    def chat(self, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        started = time.monotonic()
        settings = self._settings(payload)
        prompt = self._prompt(payload)
        finding = payload.get("finding") if isinstance(payload.get("finding"), dict) else {}
        content = self._local_chat(settings, prompt, finding)
        return {
            "role": "assistant",
            "content": content,
            "provider": settings.provider,
            "model": settings.model,
            "temperature": settings.temperature,
            "latency_ms": int((time.monotonic() - started) * 1000),
            "actor": actor,
            "safety_note": "Assistant output is advisory and requires human review before remediation or closure.",
        }

    def _settings(self, payload: dict[str, Any]) -> AssistantSettings:
        controls = payload.get("controls") if isinstance(payload.get("controls"), dict) else {}
        provider = str(controls.get("provider") or self.provider or "local").strip().lower()
        model = str(controls.get("model") or self.default_model).strip()
        if not model:
            raise ValueError("assistant model is required")
        if self.allowed_models and model not in self.allowed_models and provider == self.provider:
            raise ValueError(f"assistant model '{model}' is not allowed by server configuration")
        try:
            temperature = float(controls.get("temperature", 0.2))
        except (TypeError, ValueError) as exc:
            raise ValueError("temperature must be numeric") from exc
        if temperature < 0 or temperature > 1:
            raise ValueError("temperature must be between 0 and 1")
        system_prompt = str(controls.get("system_prompt") or self.DEFAULT_SYSTEM_PROMPT).strip()
        if len(system_prompt) > 2000:
            raise ValueError("system prompt exceeds 2000 characters")
        max_tokens = int(controls.get("max_tokens", 800) or 800)
        if max_tokens < 64 or max_tokens > 4096:
            raise ValueError("max_tokens must be between 64 and 4096")
        return AssistantSettings(provider, model, temperature, system_prompt, max_tokens)

    @staticmethod
    def _prompt(payload: dict[str, Any]) -> str:
        prompt = str(payload.get("message") or payload.get("prompt") or "").strip()
        if not prompt:
            raise ValueError("assistant message is required")
        if len(prompt) > 8000:
            raise ValueError("assistant message exceeds 8000 characters")
        return prompt

    @staticmethod
    def _finding_summary(finding: dict[str, Any]) -> str:
        if not finding:
            return "No finding context supplied."
        parts = [
            f"Title: {finding.get('title', 'unknown')}",
            f"Severity: {finding.get('severity', 'unknown')}",
            f"Status: {finding.get('status', 'unknown')}",
            f"Affected component: {finding.get('affectedPath') or finding.get('affected_component') or 'unknown'}",
        ]
        recommendation = finding.get("remediation") or finding.get("recommendation")
        if isinstance(recommendation, dict):
            parts.append(f"Recommendation: {recommendation.get('summary') or recommendation.get('rationale') or 'review required'}")
        elif recommendation:
            parts.append(f"Recommendation: {recommendation}")
        return "\n".join(str(part)[:1000] for part in parts)

    def _local_chat(self, settings: AssistantSettings, prompt: str, finding: dict[str, Any]) -> str:
        lower = prompt.lower()
        context = self._finding_summary(finding)
        if "test" in lower or "validate" in lower:
            guidance = "Validation approach:\n1. Re-run the relevant VulnoraIQ profile.\n2. Confirm the original evidence no longer reproduces.\n3. Add a regression check.\n4. Record reviewer sign-off in the finding history."
        elif "risk" in lower or "priority" in lower:
            guidance = "Risk review:\nPrioritise by exposure, trust boundary, data sensitivity, and governance category."
        elif "fix" in lower or "remed" in lower:
            guidance = "Remediation guidance:\nApply deterministic controls where possible, preserve evidence, and verify with a human reviewer."
        else:
            guidance = "Analysis guidance:\nReview the evidence, mapped governance context, and current remediation state before updating the finding."
        return f"{guidance}\n\nFinding context considered:\n{context}\n\nModel controls: {settings.model}, temperature={settings.temperature}."
