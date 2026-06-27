from __future__ import annotations

from webui import assistant_knowledge, assistant_tools
from webui.assistant import AssistantOrchestrator


def test_knowledge_search_finds_relevant_owasp_snippet():
    hits = assistant_knowledge.search("prompt injection instruction boundary", limit=3)
    assert hits, "expected at least one bundled OWASP snippet"
    blob = " ".join(h.text.lower() + " " + h.source.lower() for h in hits)
    assert "inject" in blob or "llm01" in blob


def test_web_fetch_blocks_loopback_and_private():
    assert "refusing" in assistant_tools.web_fetch("http://127.0.0.1:8787/").lower()
    assert "refusing" in assistant_tools.web_fetch("http://169.254.169.254/latest/meta-data/").lower()
    assert "only http" in assistant_tools.web_fetch("file:///etc/passwd").lower()


def test_read_text_file_is_allowlisted():
    # Traversal outside the docs root is refused.
    assert "outside" in assistant_tools.read_text_file("../pyproject.toml").lower()
    # A real docs file reads back.
    content = assistant_tools.read_text_file("ASSESSMENT_ASSURANCE.md")
    assert "assurance" in content.lower()


def test_extract_url():
    assert assistant_tools.extract_url("see https://example.com/x for more") == "https://example.com/x"
    assert assistant_tools.extract_url("no url here") is None


def _force_templated(monkeypatch):
    # No autodownload + a model path that does not exist -> model.available() is False.
    monkeypatch.setenv("VULNORAIQ_ASSISTANT_AUTODOWNLOAD", "false")
    monkeypatch.setenv("VULNORAIQ_ASSISTANT_MODEL_PATH", "/nonexistent/vulnoraiq-assistant.gguf")


def test_chat_falls_back_to_templated_without_model(monkeypatch):
    _force_templated(monkeypatch)
    orch = AssistantOrchestrator()
    result = orch.chat({"message": "How should I mitigate this prompt injection weakness?"}, actor="tester")
    assert result["backend"] == "templated"
    assert "Mitigation guidance" in result["content"]
    assert result["role"] == "assistant"


def test_chat_uses_web_fetch_tool_when_url_present(monkeypatch):
    _force_templated(monkeypatch)
    monkeypatch.setattr(assistant_tools, "web_fetch", lambda url, **_: "FETCHED-OK")
    orch = AssistantOrchestrator()
    result = orch.chat({"message": "summarise https://example.com/article"}, actor="tester")
    assert "web_fetch" in result["tools_used"]
    assert "FETCHED-OK" in result["content"]


def test_explain_finding_templated_fallback(monkeypatch):
    _force_templated(monkeypatch)
    orch = AssistantOrchestrator()
    out = orch.explain_finding({"title": "Prompt injection boundary", "severity": "info"})
    assert out["backend"].startswith("templated")
    assert "Prompt injection boundary" in out["explanation"]


def test_available_config_reports_local_model_status():
    cfg = AssistantOrchestrator().available_config()
    assert "local_model" in cfg
    assert "runtime_installed" in cfg["local_model"]
    assert "web_fetch" in cfg["tools"]
