from __future__ import annotations

import argparse
import ipaddress
import json
import logging
import mimetypes
import os
import secrets
import threading
import time
from collections.abc import Callable
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
from webui.persistent_jobs import JobStore, PersistedScanJob, create_job_store

LOGGER = logging.getLogger("vulnoraiq.webui")
AUDIT_LOG = logging.getLogger("vulnoraiq.audit")
STATIC_DIR = Path(__file__).parent / "static"
CONFIG_ROOT = Path(os.getenv("VULNORAIQ_CONFIG_DIR", "config"))
OUTPUT_ROOT = Path(os.getenv("VULNORAIQ_WEB_OUTPUT_ROOT", "reports/output/webui"))
TERMINAL_STATES = {"completed", "failed"}
AUTH_MANAGER = WebAuthManager(os.getenv("VULNORAIQ_WEB_USERS_PATH", str(CONFIG_ROOT / "web_users.yaml")))
JOB_STORE: JobStore = create_job_store()
STARTED_AT = datetime.now(timezone.utc)

# Security limits
MAX_REQUEST_BODY = int(os.getenv("VULNORAIQ_MAX_REQUEST_BODY", str(10 * 1024 * 1024)))
RATE_LIMIT_WINDOW = int(os.getenv("VULNORAIQ_RATE_LIMIT_WINDOW", "60"))
RATE_LIMIT_MAX = int(os.getenv("VULNORAIQ_RATE_LIMIT_MAX", "60"))

# Proxy trust settings
TRUST_PROXY_HEADERS = os.getenv("VULNORAIQ_TRUST_PROXY_HEADERS", "false").strip().lower() in ("1", "true", "yes")
_TRUSTED_PROXY_CIDRS_ENV = os.getenv("VULNORAIQ_TRUSTED_PROXY_CIDRS", "")
TRUSTED_PROXY_NETS: list[ipaddress.IPv4Network | ipaddress.IPv6Network] = []
if TRUST_PROXY_HEADERS and _TRUSTED_PROXY_CIDRS_ENV:
    for cidr in _TRUSTED_PROXY_CIDRS_ENV.split(","):
        cidr = cidr.strip()
        if cidr:
            TRUSTED_PROXY_NETS.append(ipaddress.ip_network(cidr, strict=False))

# Rate limiter state
_rate_limit_store: dict[str, list[float]] = {}
_rate_limit_lock = threading.Lock()

# CSRF token store
_csrf_tokens: dict[str, dict[str, Any]] = {}  # session_key -> {"token": str, "expires": float}
_csrf_token_lock = threading.Lock()
CSRF_TOKEN_TTL = int(os.getenv("VULNORAIQ_CSRF_TOKEN_TTL", "300"))  # 5 minutes


def _resolve_client_ip(handler: BaseHTTPRequestHandler) -> str:
    """Resolve client IP, respecting proxy trust settings."""
    direct_ip = handler.client_address[0]
    if not TRUST_PROXY_HEADERS:
        return direct_ip
    # Only trust proxy headers when request comes from a trusted proxy
    try:
        addr = ipaddress.ip_address(direct_ip)
    except ValueError:
        return direct_ip
    is_trusted = any(addr in net for net in TRUSTED_PROXY_NETS)
    if not is_trusted:
        return direct_ip
    forwarded = handler.headers.get("X-Forwarded-For", "").strip()
    if forwarded:
        # Use the leftmost address (original client)
        client = forwarded.split(",")[0].strip()
        try:
            ipaddress.ip_address(client)
            return client
        except ValueError:
            pass
    return direct_ip


def _audit(event: str, principal: AuthPrincipal, client_ip: str = "", detail: str = "") -> None:
    AUDIT_LOG.info(
        "event=%s user=%s role=%s authenticated=%s ip=%s detail=%s",
        event, principal.username, principal.role,
        str(principal.authenticated).lower(), client_ip, detail,
    )


def _rate_limit(client_ip: str) -> bool:
    now = time.monotonic()
    with _rate_limit_lock:
        timestamps = _rate_limit_store.get(client_ip, [])
        timestamps = [t for t in timestamps if now - t < RATE_LIMIT_WINDOW]
        if len(timestamps) >= RATE_LIMIT_MAX:
            return False
        timestamps.append(now)
        _rate_limit_store[client_ip] = timestamps
    return True


def _clean_rate_limit_store() -> None:
    now = time.monotonic()
    with _rate_limit_lock:
        expired: list[str] = []
        for ip, timestamps in _rate_limit_store.items():
            _rate_limit_store[ip] = [t for t in timestamps if now - t < RATE_LIMIT_WINDOW]
            if not _rate_limit_store[ip]:
                expired.append(ip)
        for ip in expired:
            del _rate_limit_store[ip]


def _csrf_session_key(principal: AuthPrincipal, client_ip: str) -> str:
    """Bind CSRF token to authenticated principal or client IP."""
    if principal.authenticated:
        return f"user:{principal.username}"
    return f"ip:{client_ip}"


def _csrf_token_for(session_key: str) -> str:
    now = time.monotonic()
    with _csrf_token_lock:
        entry = _csrf_tokens.get(session_key)
        if entry and entry["expires"] > now:
            return entry["token"]
        token = secrets.token_urlsafe(32)
        _csrf_tokens[session_key] = {"token": token, "expires": now + CSRF_TOKEN_TTL}
        return token


def _validate_csrf(session_key: str, provided_token: str | None) -> bool:
    if not provided_token:
        return False
    now = time.monotonic()
    with _csrf_token_lock:
        entry = _csrf_tokens.get(session_key)
        if not entry:
            return False
        if entry["expires"] <= now:
            _csrf_tokens.pop(session_key, None)
            return False
        return secrets.compare_digest(entry["token"], provided_token)


def _clean_csrf_store() -> None:
    now = time.monotonic()
    with _csrf_token_lock:
        expired = [k for k, v in _csrf_tokens.items() if v["expires"] <= now]
        for k in expired:
            del _csrf_tokens[k]


def load_config() -> dict[str, Any]:
    def read_yaml(path: str) -> dict[str, Any]:
        file_path = CONFIG_ROOT / path
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
    def mutate(fn: Callable[[PersistedScanJob], None]) -> None:
        JOB_STORE.update(job_id, fn)

    try:
        def start_job(job: PersistedScanJob) -> None:
            job.status = "running"
            job.started_at = datetime.now(timezone.utc).isoformat()
            job.add_event("initialising", "Loading scanner configuration and selected profile.", 8)
        mutate(start_job)
        job = JOB_STORE.get(job_id)
        if not job:
            LOGGER.warning("scan_job_missing job_id=%s", job_id)
            return
        LOGGER.info("scan_job_started job_id=%s target=%s profile=%s", job.id, job.target, job.profile)
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
        LOGGER.info("scan_job_completed job_id=%s target=%s profile=%s", job.id, job.target, job.profile)
    except Exception:  # pragma: no cover
        LOGGER.exception("scan_job_failed job_id=%s", job_id)
        err_msg = "internal scan error"

        def fail(item: PersistedScanJob) -> None:
            item.status = "failed"
            item.error = err_msg
            item.completed_at = datetime.now(timezone.utc).isoformat()
            item.add_event("failed", err_msg, 100, level="error")

        mutate(fail)


class HostedWebUiHandler(BaseHTTPRequestHandler):
    server_version = "VulnoraIQWebUI/0.0.1.5"

    def _client_ip(self) -> str:
        return _resolve_client_ip(self)

    def _session_key(self, principal: AuthPrincipal) -> str:
        client_ip = self._client_ip()
        return _csrf_session_key(principal, client_ip)

    def _security_headers(self, suppress_hsts: bool = False) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("X-XSS-Protection", "0")
        # Only emit HSTS when we can be confident we're behind TLS
        if not suppress_hsts:
            forwarded_proto = self.headers.get("X-Forwarded-Proto", "").strip().lower()
            if TRUST_PROXY_HEADERS and forwarded_proto == "https":
                self.send_header("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
            elif not TRUST_PROXY_HEADERS and self._client_ip() == "127.0.0.1":
                # Localhost development - skip HSTS
                pass
            else:
                self.send_header("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; form-action 'self'; base-uri 'self'; frame-ancestors 'none'",
        )
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")

    def _check_rate_limit(self, principal: AuthPrincipal, client_ip: str) -> bool:
        if not _rate_limit(client_ip):
            LOGGER.warning("rate_limit_exceeded ip=%s user=%s", client_ip, principal.username)
            _audit("rate_limit_exceeded", principal, client_ip)
            self._send_json({"error": "rate limit exceeded"}, status=HTTPStatus.TOO_MANY_REQUESTS)
            return False
        return True

    def _send_error_response(self, status: HTTPStatus, message: str) -> None:
        self._send_json({"error": message}, status=status)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        client_ip = self._client_ip()

        if path == "/healthz":
            self._send_json({"status": "ok", "service": "vulnoraiq-web", "started_at": STARTED_AT.isoformat()})
            return
        if path == "/readyz":
            config = load_config()
            ready = bool(config.get("targets")) and bool(config.get("profiles"))
            self._send_json(
                {
                    "status": "ready" if ready else "not_ready",
                    "targets_loaded": len(config.get("targets", {})),
                    "profiles_loaded": len(config.get("profiles", {})),
                    "auth_enabled": config.get("web_auth_enabled", False),
                },
                status=HTTPStatus.OK if ready else HTTPStatus.SERVICE_UNAVAILABLE,
            )
            return

        principal = self._principal(client_ip)
        if not principal:
            _audit("auth_failure", AUTH_MANAGER.anonymous(), client_ip, "no token provided")
            self._send_error_response(HTTPStatus.UNAUTHORIZED, "authentication required")
            return

        if not self._check_rate_limit(principal, client_ip):
            return

        if path == "/api/csrf-token":
            session_key = self._session_key(principal)
            token = _csrf_token_for(session_key)
            self._send_json({"csrf_token": token})
            return
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
                _audit("authz_failure", principal, client_ip, "view_scans")
                self._forbidden()
                return
            self._send_json({"jobs": [job.to_dict(include_events=False) for job in JOB_STORE.list()]})
            return
        if path.startswith("/api/scans/"):
            self._handle_scan_get(path, principal, client_ip)
            return
        self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        client_ip = self._client_ip()

        principal = self._principal(client_ip)
        if not principal:
            _audit("auth_failure", AUTH_MANAGER.anonymous(), client_ip, "no token provided")
            self._send_error_response(HTTPStatus.UNAUTHORIZED, "authentication required")
            return

        if not self._check_rate_limit(principal, client_ip):
            return

        if path == "/api/scans":
            session_key = self._session_key(principal)
            csrf_token = self.headers.get("X-CSRF-Token")
            if not _validate_csrf(session_key, csrf_token):
                _audit("csrf_failure", principal, client_ip, "invalid or missing CSRF token")
                self._send_error_response(HTTPStatus.FORBIDDEN, "invalid or missing CSRF token")
                return
            try:
                payload = self._read_json()
                target, profile, authorised = validate_scan_request(payload)
                required_permission = "start_demo_scan" if target == "demo" else "start_configured_scan"
                if not AUTH_MANAGER.can(principal, required_permission):
                    _audit("authz_failure", principal, client_ip, f"missing {required_permission}")
                    self._forbidden()
                    return
                job = JOB_STORE.create(target, profile, authorised, created_by=principal.username)
                _audit("scan_created", principal, client_ip, f"target={target} profile={profile} job_id={job.id}")
                LOGGER.info("scan_job_accepted job_id=%s target=%s profile=%s user=%s",
                            job.id, target, profile, principal.username)
                threading.Thread(target=run_scan_job, args=(job.id,), daemon=True).start()
                self._send_json(job.to_dict(), status=HTTPStatus.ACCEPTED)
            except ValueError as exc:
                self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def _handle_scan_get(self, path: str, principal: AuthPrincipal, client_ip: str) -> None:
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
                _audit("authz_failure", principal, client_ip, "view_scans")
                self._forbidden()
                return
            self._send_json(job.to_dict())
            return
        action = parts[3]
        if action == "events":
            if not AUTH_MANAGER.can(principal, "view_scans"):
                _audit("authz_failure", principal, client_ip, "view_scans")
                self._forbidden()
                return
            self._send_events(job_id)
            return
        if action == "artifact" and len(parts) == 5:
            if not AUTH_MANAGER.can(principal, "download_artifacts"):
                _audit("authz_failure", principal, client_ip, "download_artifacts")
                self._forbidden()
                return
            self._send_artifact(job, parts[4], client_ip)
            return
        self.send_error(HTTPStatus.NOT_FOUND, "Scan resource not found")

    def _principal(self, client_ip: str) -> AuthPrincipal | None:
        token = self.headers.get(AUTH_MANAGER.header_name())
        return AUTH_MANAGER.authenticate_token(token)

    def _send_artifact(self, job: PersistedScanJob, artifact_name: str, client_ip: str) -> None:
        path = job.outputs.get(artifact_name)
        if not path:
            self.send_error(HTTPStatus.NOT_FOUND, "Artifact not found")
            return
        file_path = Path(path)
        if not file_path.exists():
            self.send_error(HTTPStatus.NOT_FOUND, "Artifact file not found")
            return
        data = file_path.read_bytes()
        _audit("artifact_download", self._principal(client_ip) or AUTH_MANAGER.anonymous(),
               client_ip, f"artifact={artifact_name} job={job.id}")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", mimetypes.guess_type(file_path.name)[0] or "application/octet-stream")
        self.send_header("Content-Disposition", f'attachment; filename="{file_path.name}"')
        self.send_header("Content-Length", str(len(data)))
        self._security_headers()
        self.end_headers()
        self.wfile.write(data)

    def _send_events(self, job_id: str) -> None:
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self._security_headers()
        self.end_headers()
        sent = 0
        while True:
            job = JOB_STORE.get(job_id)
            if not job:
                return
            for event in job.events[sent:]:
                self.wfile.write(f"data: {json.dumps(asdict(event), default=str)}\n\n".encode())
                self.wfile.flush()
                sent += 1
            if job.status in TERMINAL_STATES:
                self.wfile.write(f"event: done\ndata: {json.dumps(job.to_dict(), default=str)}\n\n".encode())
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
        self._security_headers()
        self.end_headers()
        self.wfile.write(data)

    def _read_json(self) -> dict[str, Any]:
        raw_length = self.headers.get("Content-Length", "0")
        if not raw_length.isdigit():
            raise ValueError("invalid Content-Length")
        length = int(raw_length)
        if length <= 0:
            return {}
        if length > MAX_REQUEST_BODY:
            raise ValueError(f"Request body exceeds maximum allowed size ({MAX_REQUEST_BODY} bytes)")
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ValueError(f"invalid JSON: {exc}") from exc

    def _send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        data = json.dumps(payload, indent=2, sort_keys=True, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self._security_headers()
        self.end_headers()
        self.wfile.write(data)

    def _forbidden(self) -> None:
        self._send_json({"error": "forbidden"}, status=HTTPStatus.FORBIDDEN)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        LOGGER.info("http_request client=%s message=%s", self.address_string(), format % args)

    def send_error(self, code: int, message: str | None = None, explain: str | None = None) -> None:
        """Override to add security headers to error responses."""
        try:
            self.send_response(code)
            self._security_headers()
            self.end_headers()
            if message:
                self.wfile.write(message.encode("utf-8"))
        except OSError:
            pass


def create_server(host: str = "127.0.0.1", port: int = 8787) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), HostedWebUiHandler)


def _rate_limit_cleanup_loop() -> None:
    while True:
        time.sleep(RATE_LIMIT_WINDOW)
        _clean_rate_limit_store()
        _clean_csrf_store()


def main() -> None:
    # Validate production mode on startup
    if AUTH_MANAGER.is_production():
        try:
            AUTH_MANAGER._validate_production()
        except RuntimeError as exc:
            LOGGER.error("production_mode_validation_failed: %s", exc)
            raise SystemExit(1) from exc

    logging.basicConfig(
        level=os.getenv("VULNORAIQ_LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    audit_handler = logging.StreamHandler()
    audit_handler.setLevel(logging.INFO)
    audit_handler.setFormatter(logging.Formatter("%(asctime)s AUDIT %(message)s"))
    AUDIT_LOG.addHandler(audit_handler)
    AUDIT_LOG.propagate = False

    parser = argparse.ArgumentParser(description="Run the VulnoraIQ hosted web UI.")
    parser.add_argument("--host", default=os.getenv("VULNORAIQ_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("VULNORAIQ_PORT", "8787")))
    parser.add_argument("--production", action="store_true", help="Enable production mode validation")
    args = parser.parse_args()

    if args.production or AUTH_MANAGER.is_production():
        try:
            AUTH_MANAGER._validate_production()
        except RuntimeError as exc:
            LOGGER.error("production_mode_validation_failed: %s", exc)
            raise SystemExit(1) from exc

    threading.Thread(target=_rate_limit_cleanup_loop, daemon=True).start()
    server = create_server(args.host, args.port)
    env_label = "production" if AUTH_MANAGER.is_production() else "development"
    LOGGER.info("web_ui_started env=%s url=http://%s:%s auth_enabled=%s backend=%s",
                env_label, args.host, args.port, AUTH_MANAGER.enabled(),
                os.getenv("VULNORAIQ_JOB_STORE_BACKEND", "sqlite"))
    _audit("server_start", AUTH_MANAGER.anonymous(), "",
           f"env={env_label} host={args.host} port={args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
