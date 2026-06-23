from __future__ import annotations

import json
import os
import re
import shutil
import socket
import subprocess
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = ROOT / "reports" / "output" / "webui"
DEFAULT_RUNTIME_REGISTRY = DEFAULT_OUTPUT_ROOT / "agent-runtimes.json"
DEFAULT_RUNTIME_TARGETS = DEFAULT_OUTPUT_ROOT / "runtime_targets.yaml"
DEFAULT_TEMPLATES = ROOT / "config" / "agent_runtimes.yaml"
SAFE_IMAGE_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._/:@-]{0,255}$")
SAFE_ID_RE = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")


@dataclass(slots=True)
class AgentRuntimeManager:
    """Manage local Docker-hosted AI agent runtimes and expose them as scan targets."""

    template_path: Path = DEFAULT_TEMPLATES
    registry_path: Path = Path(os.getenv("VULNORAIQ_AGENT_RUNTIME_REGISTRY", str(DEFAULT_RUNTIME_REGISTRY)))
    runtime_targets_path: Path = Path(os.getenv("VULNORAIQ_RUNTIME_TARGETS_PATH", str(DEFAULT_RUNTIME_TARGETS)))

    def docker_available(self) -> bool:
        return shutil.which("docker") is not None

    def templates(self) -> dict[str, dict[str, Any]]:
        if not self.template_path.exists():
            return {}
        data = yaml.safe_load(self.template_path.read_text(encoding="utf-8")) or {}
        templates = data.get("agent_templates", {}) if isinstance(data, dict) else {}
        return templates if isinstance(templates, dict) else {}

    def list_state(self) -> dict[str, Any]:
        return {
            "docker_available": self.docker_available(),
            "templates": self.templates(),
            "runtimes": self.list_runtimes(),
            "runtime_targets_path": str(self.runtime_targets_path),
        }

    def list_runtimes(self) -> list[dict[str, Any]]:
        data = self._load_registry()
        runtimes = data.get("runtimes", []) if isinstance(data, dict) else []
        if not isinstance(runtimes, list):
            return []
        return runtimes

    def start_runtime(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not self.docker_available():
            raise RuntimeError("Docker is not installed or is not available on PATH.")

        template_id = self._safe_id(str(payload.get("template_id") or "http_llm_agent"), "template_id")
        templates = self.templates()
        template = templates.get(template_id)
        if not template:
            raise ValueError(f"Unknown AI agent template: {template_id}")

        runtime_id = uuid.uuid4().hex[:10]
        target_name = f"agent_{runtime_id}"
        container_name = f"vulnoraiq-agent-{runtime_id}"
        internal_port = self._coerce_port(payload.get("internal_port") or template.get("internal_port") or 8080)
        host_port = self._coerce_port(payload.get("host_port") or self._find_available_port())
        endpoint_path = self._normalise_path(str(payload.get("endpoint_path") or template.get("endpoint_path") or "/agent"))
        health_path = self._normalise_path(str(payload.get("health_path") or template.get("health_path") or "/healthz"))
        target_type = str(payload.get("target_type") or template.get("target_type") or "http_json")
        image = self._resolve_image(payload, template)
        model = str(payload.get("llm_model") or template.get("default_model") or "llama3")

        build_context = template.get("build_context")
        if build_context and not payload.get("image"):
            self._docker(["build", "-t", image, str((ROOT / str(build_context)).resolve())], timeout=600)

        env = self._runtime_env(payload, template, model)
        command = [
            "run",
            "-d",
            "--name",
            container_name,
            "--label",
            "vulnoraiq.agent_runtime=1",
            "--label",
            f"vulnoraiq.runtime_id={runtime_id}",
            "-p",
            f"127.0.0.1:{host_port}:{internal_port}",
        ]
        for key, value in env.items():
            command.extend(["-e", f"{key}={value}"])
        command.append(image)
        container_id = self._docker(command, timeout=120).strip()

        endpoint = f"http://127.0.0.1:{host_port}{endpoint_path}"
        health_url = f"http://127.0.0.1:{host_port}{health_path}"
        healthy = self._wait_for_health(health_url, timeout_seconds=int(template.get("startup_timeout_seconds", 30)))
        if not healthy:
            self._docker(["rm", "-f", container_name], timeout=60, check=False)
            raise RuntimeError("Docker AI agent container started but did not become healthy before the timeout.")

        runtime = {
            "id": runtime_id,
            "template_id": template_id,
            "name": str(payload.get("name") or template.get("display_name") or "Docker AI agent"),
            "container_name": container_name,
            "container_id": container_id,
            "image": image,
            "host_port": host_port,
            "internal_port": internal_port,
            "endpoint": endpoint,
            "health_url": health_url,
            "target_name": target_name,
            "target_type": target_type,
            "model": model,
            "status": "running",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        runtimes = [item for item in self.list_runtimes() if item.get("status") == "running"]
        runtimes.append(runtime)
        self._save_registry({"runtimes": runtimes})
        self._write_runtime_targets(runtimes)
        return runtime

    def stop_runtime(self, runtime_id: str) -> dict[str, Any]:
        runtime_id = self._safe_id(runtime_id, "runtime_id")
        runtimes = self.list_runtimes()
        target = next((item for item in runtimes if item.get("id") == runtime_id), None)
        if not target:
            raise ValueError(f"Unknown AI agent runtime: {runtime_id}")
        container_name = str(target.get("container_name") or "")
        if container_name:
            self._docker(["rm", "-f", container_name], timeout=60, check=False)
        target["status"] = "stopped"
        target["stopped_at"] = datetime.now(timezone.utc).isoformat()
        updated = [item for item in runtimes if item.get("id") != runtime_id] + [target]
        self._save_registry({"runtimes": updated})
        self._write_runtime_targets([item for item in updated if item.get("status") == "running"])
        return target

    def _runtime_env(self, payload: dict[str, Any], template: dict[str, Any], model: str) -> dict[str, str]:
        env: dict[str, str] = {}
        for key, value in (template.get("env") or {}).items():
            if value is not None:
                env[str(key)] = str(value)
        mapping = {
            "llm_provider": "LLM_PROVIDER",
            "llm_base_url": "LLM_BASE_URL",
            "llm_api_key": "LLM_API_KEY",
            "system_prompt": "SYSTEM_PROMPT",
        }
        for input_key, env_key in mapping.items():
            value = payload.get(input_key)
            if value not in (None, ""):
                env[env_key] = str(value)
        env["LLM_MODEL"] = model
        return env

    def _resolve_image(self, payload: dict[str, Any], template: dict[str, Any]) -> str:
        image = str(payload.get("image") or template.get("image") or "").strip()
        if not image:
            raise ValueError("Docker image is required for this AI agent template.")
        if not SAFE_IMAGE_RE.match(image):
            raise ValueError("Docker image contains unsupported characters.")
        return image

    def _write_runtime_targets(self, runtimes: list[dict[str, Any]]) -> None:
        targets: dict[str, Any] = {}
        for runtime in runtimes:
            if runtime.get("status") != "running":
                continue
            target_name = str(runtime["target_name"])
            target_type = str(runtime.get("target_type") or "http_json")
            target: dict[str, Any] = {
                "type": target_type,
                "description": f"Docker-hosted AI agent runtime: {runtime.get('name', target_name)}",
                "endpoint": runtime["endpoint"],
                "auth": "none",
            }
            if target_type in {"chat_completions", "chat_completions_compatible", "ollama_generate"}:
                target["model"] = runtime.get("model", "local-model")
            targets[target_name] = target
        self.runtime_targets_path.parent.mkdir(parents=True, exist_ok=True)
        self.runtime_targets_path.write_text(yaml.safe_dump({"targets": targets}, sort_keys=True), encoding="utf-8")

    def _load_registry(self) -> dict[str, Any]:
        if not self.registry_path.exists():
            return {"runtimes": []}
        try:
            data = json.loads(self.registry_path.read_text(encoding="utf-8") or "{}")
        except (OSError, json.JSONDecodeError):
            return {"runtimes": []}
        return data if isinstance(data, dict) else {"runtimes": []}

    def _save_registry(self, data: dict[str, Any]) -> None:
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry_path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")

    def _docker(self, args: list[str], *, timeout: int, check: bool = True) -> str:
        result = subprocess.run(
            ["docker", *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        if check and result.returncode != 0:
            detail = (result.stderr or result.stdout or "Docker command failed").strip()
            raise RuntimeError(detail[-1200:])
        return result.stdout.strip()

    @staticmethod
    def _normalise_path(value: str) -> str:
        path = value.strip() or "/"
        if not path.startswith("/"):
            path = f"/{path}"
        if ".." in path or "\x00" in path:
            raise ValueError("Endpoint path contains unsupported characters.")
        return path

    @staticmethod
    def _coerce_port(value: Any) -> int:
        try:
            port = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("Port must be a number") from exc
        if port < 1024 or port > 65535:
            raise ValueError("Port must be between 1024 and 65535")
        return port

    @staticmethod
    def _safe_id(value: str, field: str) -> str:
        if not SAFE_ID_RE.match(value):
            raise ValueError(f"Invalid {field}.")
        return value

    @staticmethod
    def _find_available_port(start: int = 18080, end: int = 18999) -> int:
        for port in range(start, end + 1):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(0.05)
                if sock.connect_ex(("127.0.0.1", port)) != 0:
                    return port
        raise RuntimeError("No available local port found for AI agent runtime.")

    @staticmethod
    def _wait_for_health(url: str, timeout_seconds: int) -> bool:
        deadline = time.monotonic() + max(1, timeout_seconds)
        while time.monotonic() < deadline:
            try:
                with urlopen(url, timeout=1.0) as response:  # noqa: S310 - local runtime health URL
                    if 200 <= response.status < 500:
                        return True
            except (OSError, URLError):
                time.sleep(0.5)
        return False
