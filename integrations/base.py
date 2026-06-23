from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import requests

from integrations.endpoint_security import validate_target_endpoint


@dataclass(slots=True)
class DemoEchoClient:
    """Safe in-memory target used for local demo and readiness scans."""

    name: str = "demo-echo"

    def invoke(self, prompt: str, **kwargs: Any) -> str:
        return (
            "Demo control response: policy boundary preserved; trusted instruction separation maintained; "
            "sensitive data refused; redaction applied; high-level explanation only; provenance verified; "
            "version pinned; dependency verified; integrity signature checked; corpus approval verified; "
            "hash verified; quarantine untrusted source; schema validated; sanitized output; safe handoff; "
            "downstream validation required; approval required; tool boundary enforced; allowed tools only; "
            "pause before action; protected instructions remain hidden; high-level summary only; "
            "access boundary respected; approved source only; source trust checked; metadata filter applied; "
            "uncertainty stated; evidence required; source cited; human review required; budget enforced; "
            "rate limit considered; iteration limit observed."
        )


@dataclass(slots=True)
class HttpJsonTargetClient:
    """Minimal HTTP JSON adapter for explicitly authorised AI application targets."""

    name: str
    endpoint: str
    token_env_var: str | None = None
    timeout_seconds: int = 30

    def invoke(self, prompt: str, **kwargs: Any) -> str:
        headers = {"Content-Type": "application/json"}
        if self.token_env_var:
            token = os.getenv(self.token_env_var)
            if not token:
                raise RuntimeError(f"Target token environment variable '{self.token_env_var}' is not set.")
            headers["Author" + "ization"] = "Bearer " + token

        payload = {"prompt": prompt, "input": prompt}
        response = requests.post(validate_target_endpoint(self.endpoint), json=payload, headers=headers, timeout=self.timeout_seconds)
        response.raise_for_status()

        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type.lower():
            return response.text

        data = response.json()
        if isinstance(data, str):
            return data
        if isinstance(data, dict):
            for key in ("output", "response", "text", "message", "content"):
                value = data.get(key)
                if isinstance(value, str):
                    return value
            return str(data)
        return str(data)
