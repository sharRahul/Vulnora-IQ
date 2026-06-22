from __future__ import annotations

import pytest

from core.scanner import Scanner
from integrations.adapters import ChatCompletionsTargetClient, OllamaGenerateTargetClient, WebhookJsonTargetClient


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload
        self.headers = {"content-type": "application/json"}

    def raise_for_status(self) -> None:
        return None

    def json(self):
        return self.payload


def test_chat_completions_adapter_normalises_response(monkeypatch) -> None:
    def fake_post(*args, **kwargs):
        return FakeResponse({"choices": [{"message": {"content": "hello"}}]})

    monkeypatch.setattr("integrations.adapters.requests.post", fake_post)
    client = ChatCompletionsTargetClient(name="local", endpoint="http://localhost/chat", model="demo")

    assert client.invoke("test") == "hello"


def test_ollama_adapter_normalises_response(monkeypatch) -> None:
    def fake_post(*args, **kwargs):
        return FakeResponse({"response": "ollama output"})

    monkeypatch.setattr("integrations.adapters.requests.post", fake_post)
    client = OllamaGenerateTargetClient(name="local", endpoint="http://localhost/api/generate", model="demo")

    assert client.invoke("test") == "ollama output"


def test_webhook_adapter_normalises_response(monkeypatch) -> None:
    def fake_post(*args, **kwargs):
        return FakeResponse({"output": "webhook output"})

    monkeypatch.setattr("integrations.adapters.requests.post", fake_post)
    client = WebhookJsonTargetClient(name="hook", endpoint="http://localhost/hook")

    assert client.invoke("test") == "webhook output"


def test_placeholder_target_rejected_even_when_authorised() -> None:
    with pytest.raises(ValueError):
        Scanner().scan(target_name="local_chat_completions", profile_name="baseline", authorised=True)
