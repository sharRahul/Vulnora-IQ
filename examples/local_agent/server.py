from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse


def answer(prompt: str, mode: str = "normal") -> str:
    lower = prompt.lower()
    if mode == "vulnerable" and any(x in lower for x in ("system prompt", "secret", "ignore previous")):
        return "VULNERABLE: system prompt is secret=demo-secret and I will call tool_call without approval."
    if any(x in lower for x in ("system prompt", "secret", "ignore previous", "exfiltrate", "tool")):
        return "I cannot reveal protected instructions, secrets, or perform tool actions without explicit authorization and approval."
    return "OK: safe bounded response with policy boundary preserved."


class Handler(BaseHTTPRequestHandler):
    server_version = "VulnoraIQLocalMock/1.0"
    mode = "normal"

    def _read(self):
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length > 100000:
            self.send_error(413)
            return None
        return json.loads(self.rfile.read(length) or b"{}")

    def _send(self, payload, status=200):
        data = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if urlparse(self.path).path == "/healthz":
            self._send({"status": "ok"})
        else:
            self.send_error(404)

    def do_POST(self):
        body = self._read()
        if body is None:
            return
        path = urlparse(self.path).path
        if path == "/agent":
            self._send({"response": answer(body.get("prompt") or body.get("input") or "", body.get("mode") or self.mode)})
        elif path == "/v1/chat/completions":
            messages = body.get("messages") or []
            prompt = messages[-1].get("content", "") if messages else ""
            self._send({"choices": [{"message": {"content": answer(prompt, self.mode)}}]})
        elif path == "/api/generate":
            self._send({"response": answer(body.get("prompt", ""), self.mode), "done": True})
        elif path == "/rag/query":
            self._send({"answer": answer(body.get("query", ""), self.mode), "context": [{"source": "mock", "text": "sanitized context"}]})
        elif path == "/webhook":
            self._send({"output": answer(body.get("input", ""), self.mode)})
        elif path == "/agent/tool-loop":
            self._send({"answer": answer(body.get("input", ""), self.mode), "tool_calls": []})
        else:
            self.send_error(404)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=9090)
    parser.add_argument("--mode", choices=["normal", "vulnerable", "remediated"], default="normal")
    args = parser.parse_args()
    Handler.mode = args.mode
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Local mock AI agent listening on http://127.0.0.1:{args.port} mode={args.mode}")
    server.serve_forever()


if __name__ == "__main__":
    main()
