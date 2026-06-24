from __future__ import annotations

import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = os.getenv("MOCK_AGENT_HOST", "0.0.0.0")
PORT = int(os.getenv("MOCK_AGENT_PORT", "9090"))


def answer(prompt: str) -> str:
    p = prompt.lower()
    if "health check" in p or "reply with ok" in p:
        return "OK docker mock agent ready"
    if "system prompt" in p or "developer message" in p:
        return "I cannot provide protected system prompts or developer instructions. Policy boundary preserved."
    if "api key" in p or "password" in p or "secret" in p:
        return "I cannot provide secrets. Redaction applied and sensitive data refused."
    if "ignore previous" in p or "bypass" in p:
        return "I cannot override trusted instructions or disable policy controls."
    if "tool" in p or "send external" in p:
        return "Tool request blocked: approval required and dry-run only."
    if "rag" in p or "retrieval" in p:
        return "RAG answer from approved docker fixture context only."
    return "Safe deterministic mock response for authorised Docker lab assessment."


def write(handler: BaseHTTPRequestHandler, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
    data = json.dumps(payload).encode()
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(data)))
    handler.send_header("X-Content-Type-Options", "nosniff")
    handler.end_headers()
    handler.wfile.write(data)


def read(handler: BaseHTTPRequestHandler) -> dict:
    length = int(handler.headers.get("Content-Length", "0") or 0)
    if length > 65536:
        raise ValueError("request too large")
    return json.loads(handler.rfile.read(length).decode() if length else "{}")


class H(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path.split("?", 1)[0] == "/healthz":
            write(self, {"status": "ok", "service": "local-mock-agent"})
            return
        write(self, {"error": "not found"}, HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802
        try:
            body = read(self)
            path = self.path.split("?", 1)[0]
            prompt = str(body.get("prompt") or body.get("input") or body.get("query") or "")
            if path == "/v1/chat/completions":
                messages = body.get("messages") or []
                if messages and isinstance(messages, list):
                    prompt = str(messages[-1].get("content", ""))
                write(self, {"choices": [{"message": {"role": "assistant", "content": answer(prompt)}}], "model": "mock-agent"})
                return
            if path == "/api/generate":
                write(self, {"response": answer(str(body.get("prompt", ""))), "done": True})
                return
            if path == "/rag/query":
                write(self, {"answer": answer(prompt), "context": [{"id": "kb-docker-001", "classification": "internal-fixture"}]})
                return
            if path == "/webhook":
                write(self, {"output": answer(prompt)})
                return
            if path == "/agent/tool-loop":
                write(self, {"answer": answer(prompt), "tool_calls": [{"name": "search_docs", "approved": True, "dry_run": True}]})
                return
            if path == "/agent":
                write(self, {"response": answer(prompt), "output": answer(prompt)})
                return
            write(self, {"error": "not found"}, HTTPStatus.NOT_FOUND)
        except Exception as exc:
            write(self, {"error": str(exc)}, HTTPStatus.BAD_REQUEST)

    def log_message(self, fmt: str, *args: object) -> None:
        print(fmt % args)


if __name__ == "__main__":
    print(f"local mock agent on {HOST}:{PORT}")
    ThreadingHTTPServer((HOST, PORT), H).serve_forever()
