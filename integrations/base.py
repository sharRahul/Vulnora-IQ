from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class DemoEchoClient:
    """Safe in-memory target used for local demo scans."""

    name: str = "demo-echo"

    def invoke(self, prompt: str, **kwargs: Any) -> str:
        lowered = prompt.lower()
        if "system prompt" in lowered or "developer message" in lowered:
            return "I can't disclose hidden instructions or protected system content."
        if "api key" in lowered or "password" in lowered or "private key" in lowered:
            return "I can't provide secrets."
        return f"Demo response received for assessment input: {prompt[:120]}"
