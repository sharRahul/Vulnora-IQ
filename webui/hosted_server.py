from __future__ import annotations

import argparse
import json
import mimetypes
import threading
import time
from dataclasses import asdict
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

import yaml

from core.scanner import Scanner
from dashboards.generate_dashboard import DashboardGenerator
from dashboards.html_dashboard import HtmlDashboardGenerator
from reports.json_report_generator import JsonReportGenerator
from reports.report_generator import MarkdownReportGenerator
from reports.sarif_report_generator import SarifReportGenerator
from webui.auth import AuthPrincipal, WebAuthManager
from webui.persistent_jobs import PersistentJobStore, PersistedScanJob


STATIC_DIR = Path(__file__).parent / "static"
OUTPUT_ROOT = Path("reports/output/webui")
TERMINAL_STATES = {"completed", "failed"}
AUTH_MANAGER = WebAuthManager()
JOB_STORE = PersistentJobStore()


def load_config() -> dict[str, Any]:
    def read_yaml(path: str) -> dict[str, Any]:
        file_path = Path("config") / path
        if not file_path.exists():
            return {}
        return yaml.safe_load(file_path.read_text(encoding="utf-8")) or {}

    return {
        "targets": read_yaml("targets.yaml").get("targets", {}),
        "profiles": read_yaml("attack_profiles.yaml").get("profiles", {}),
        "web_auth_enabled": AUTH_MANAGER.enabled(),
    }


def validate_scan_request(payload: dict[str, Any]) -> tuple[str, str, bool]:
    config = load_config()
    target = str(payload.get("target") or "demo")
    profile = str(payload.get("profile") or "baseline")
    authorised = bool(payload.get("authorised", False))
    if target not in config["targets"]:
        raise ValueError(f"Unknown target: {target}")
    if profile not in config["profiles"]:
        raise ValueError(f"Unknown profile: {profile}")
    return target, profile, authorised


def run_scan_job(job_id: str) -> None:
    def mutate(fn) -> None:
        JOB_STORE.update(job_id, fn)

    try:
        mutate(lambda job: (setattr(job, "status", "running"), setattr(job, "started_at", datetime.now(timezone.utc).isoformat()), job.add_event("initialising", "Loading scanner configuration and selected profile.", 8)))
        job = JOB_STORE.get(job_id)
        if not job:
            return
        mutate(lambda item: item.add_event("scanning", f"Running {job.profile} profile against {job.target}.", 25))
        result = Scanner().scan(target_name=job.target, profile_name=job.profile, authorised=job.authorised)

        mutate(lambda item: item.add_event("policy", "Scan completed; evaluating policies and scoring findings.", 55))
        output_dir = OUTPUT_ROOT / job.id
        output_dir.mkdir(parents=True, exist_ok=True)
        markdown_path = MarkdownReportGenerator().generate(result, output_dir / "scan-report.md")
        json_path = JsonReportGenerator().generate(result, output_dir / "scan-report.json")
        sarif_path = SarifReportGenerator().generate(result, output_dir / "scan-report.sarif")

        mutate(lambda item: item.add_event("dashboard", "Rendering Markdown and HTML dashboards.", 75))
        report_data = json.loads(json_path.read_text(encoding="utf-8"))
        dashboard_path = DashboardGenerator().generate_from_report(report_data, output_dir / "dashboard.md")
        html_dashboard_path = HtmlDashboardGenerator().generate_from_report(report_data, output_dir / "dashboard.html")

        def complete(item: PersistedScanJob) -> None:
            item.status = "completed"
            item.completed_at = datetime.now(timezone.utc).isoformat()
            item.outputs = {
                "markdown": str(markdown_path),
                "json": str(json_path),
                "sarif": str(sarif_path),
                "dashboard_markdown": str(dashboard_path),
                "dashboard_html": str(html_dashboard_path),
            }
            item.summary = {
                "target": report_data.get("target"),
                "profile": report_data.get("profile"),
                "finding_count": report_data.get("finding_count"),
                "highest_severity": report_data.get("highest_severity"),
                "policy_status": report_data.get("policy_status"),
                "severity_counts": report_data.get("severity_counts", {}),
                "policy_results": report_data.get("policy_results", []),
                "findings": report_data.get("findings", []),
            }
            item.add_event("completed", "Scan completed and reports are ready.", 100)

        mutate(complete)
    except Exception as exc:  # pragma: no cover
        def fail(item: PersistedScanJob) -> None:
            item.status = "failed"
            item.error = str(exc)
            item.completed_at = datetime.now(timezone.utc).isoformat()
            item.add_event("failed", str(exc), 100, level="error")

        mutate(fail)


class HostedWebUiHandler(BaseHTTPRequestHandler):
    server_version = "VulnoraIQWebUI/0.0.1.2"

    def do_GET(self) -> None:  # noqa: N802
        principal = self._principal()
        if not principal:
            self._send_json({"error": "authentication required"}, status=HTTPStatus.UNAUTHORIZED)
            return
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/":
            self._serve_static("index.html")
            return
        if path.startswith("/static/"):
            self._serve_static(path.removeprefix("/static/"))
            return
        if path == "/api/config":
            self._send_json(load_config())
            return
        if path == "/api/scans":
            if not AUTH_MANAGER.can(principal, "view_scans"):
                self._forbidden()
                return
            self._send_json({"jobs": [job.to_dict(include_events=False) for job in JOB_STORE.list()]})
            return
        if path.startswith("/api/scans/"):
            self._handle_scan_get(path, principal)
            return
        self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def do_POST(self) -> None:  # noqa: N802
        principal = self._principal()
        if not principal:
            self._send_json({"error": "authentication required"}, status=HTTPStatus.UNAUTHORIZED)
            return
        if urlparse(self.path).path != "/api/scans":
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            return
        try:
            payload = self._read_json()
            target, profile, authorised = validate_scan_request(payload)
            required_permission = "start_demo_scan" if target == "demo" else "start_configured_scan"
            if not AUTH_MANAGER.can(principal, required_permission):
                self._forbidden()
                return
            job = JOB_STORE.create(target, profile, authorised, created_by=principal.username)
            threading.Thread(target=run_scan_job, args=(job.id,), daemon=True).start()
            self._send_json(job.to_dict(), status=HTTPStatus.ACCEPTED)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)

    def _handle_scan_get(self, path: str, principal: AuthPrincipal) -> None:
        parts = [unquote(item) for item in path.split("/") if item]
        if len(parts) < 3:
            self.send_error(HTTPStatus.NOT_FOUND, "Scan not found")
            return
        job_id = parts[2]
        job = JOB_STORE.get(job_id)
        if not job:
            self.send_error(HTTPStatus.NOT_FOUND, "Scan not found")
            return
        if len(parts) == 3:
            if not AUTH_MANAGER.can(principal, "view_scans"):
                self._forbidden()
                return
            self._send_json(job.to_dict())
            return
        action = parts[3]
        if action == "events":
            if not AUTH_MANAGER.can(principal, "view_scans"):
                self._forbidden()
                return
            self._send_events(job_id)
            return
        if action == "artifact" and len(parts) == 5:
            if not AUTH_MANAGER.can(principal, "download_artifacts"):
                self._forbidden()
                return
            self._send_artifact(job, parts[4])
            return
        self.send_error(HTTPStatus.NOT_FOUND, "Scan resource not found")

    def _principal(self) -> AuthPrincipal | None:
        token = self.headers.get(AUTH_MANAGER.header_name())
        return AUTH_MANAGER.authenticate_token(token)

    def _send_artifact(self, job: PersistedScanJob, artifact_name: str) -> None:
        path = job.outputs.get(artifact_name)
        if not path:
            self.send_error(HTTPStatus.NOT_FOUND, "Artifact not found")
            return
        file_path = Path(path)
        if not file_path.exists():
            self.send_error(HTTPStatus.NOT_FOUND, "Artifact file not found")
            return
        data = file_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", mimetypes.guess_type(file_path.name)[0] or "application/octet-stream")
        self.send_header("Content-Disposition", f'attachment; filename="{file_path.name}"')
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_events(self, job_id: str) -> None:
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        sent = 0
        while True:
            job = JOB_STORE.get(job_id)
            if not job:
                return
            for event in job.events[sent:]:
                self.wfile.write(f"data: {json.dumps(asdict(event), default=str)}\n\n".encode("utf-8"))
                self.wfile.flush()
                sent += 1
            if job.status in TERMINAL_STATES:
                self.wfile.write(f"event: done\ndata: {json.dumps(job.to_dict(), default=str)}\n\n".encode("utf-8"))
                self.wfile.flush()
                return
            time.sleep(0.4)

    def _serve_static(self, relative_path: str) -> None:
        safe_relative = Path(relative_path)
        if safe_relative.is_absolute() or ".." in safe_relative.parts:
            self.send_error(HTTPStatus.BAD_REQUEST, "Invalid path")
            return
        file_path = STATIC_DIR / safe_relative
        if not file_path.exists() or not file_path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "Static file not found")
            return
        data = file_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", mimetypes.guess_type(file_path.name)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        data = json.dumps(payload, indent=2, sort_keys=True, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _forbidden(self) -> None:
        self._send_json({"error": "forbidden"}, status=HTTPStatus.FORBIDDEN)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        return


def create_server(host: str = "127.0.0.1", port: int = 8787) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), HostedWebUiHandler)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the VulnoraIQ hosted web UI.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args()
    server = create_server(args.host, args.port)
    print(f"VulnoraIQ Web UI running at http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
