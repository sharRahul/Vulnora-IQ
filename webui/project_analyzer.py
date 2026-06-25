from __future__ import annotations

import ast
import logging
import os
import re
from pathlib import Path
from typing import Any

PROJECTS_ROOT = Path(os.getenv("VULNORAIQ_PROJECTS_DIR", "/app/projects"))
LOGGER = logging.getLogger("vulnoraiq.webui.project_analyzer")

FRAMEWORK_PATTERNS: dict[str, list[str]] = {
    "flask": ["from flask", "import flask", "Flask("],
    "fastapi": ["from fastapi", "import fastapi", "FastAPI("],
    "django": ["from django", "import django", "DJANGO_SETTINGS_MODULE"],
    "gradio": ["import gradio", "from gradio", "gr.Blocks", "gr.Interface"],
    "streamlit": ["import streamlit", "from streamlit", "st."],
    "aiohttp": ["from aiohttp", "import aiohttp"],
}

ENDPOINT_PATTERNS: dict[str, list[re.Pattern]] = {
    "flask": [
        re.compile(r'@\w+\.route\([\'"]([^\'"]+)[\'"]', re.M),
        re.compile(r'@\w+\.(get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"]', re.M),
        re.compile(r'app\.add_url_rule\([\'"]([^\'"]+)[\'"]', re.M),
    ],
    "fastapi": [
        re.compile(r'@\w+\.(get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"]', re.M),
    ],
}


def list_projects() -> list[dict[str, Any]]:
    if not PROJECTS_ROOT.exists():
        return []
    projects = []
    for entry in sorted(PROJECTS_ROOT.iterdir()):
        if entry.is_dir() and not entry.name.startswith("."):
            projects.append(analyze_project(entry.name))
    return projects


def analyze_project(name: str) -> dict[str, Any]:
    root = PROJECTS_ROOT / name
    result: dict[str, Any] = {
        "name": name,
        "exists": root.exists(),
        "framework": None,
        "ports": [],
        "endpoints": [],
        "env_vars": [],
        "has_dockerfile": (root / "Dockerfile").exists(),
        "has_requirements": (root / "requirements.txt").exists(),
        "has_pyproject": (root / "pyproject.toml").exists(),
        "readme": _read_file_preview(root / "README.md"),
        "file_count": 0,
        "errors": [],
    }
    if not root.exists():
        return result

    py_files = list(root.rglob("*.py"))
    result["file_count"] = len(py_files)

    source_map: dict[str, str] = {}
    for pyf in py_files:
        try:
            rel = str(pyf.relative_to(root))
            text = pyf.read_text(encoding="utf-8", errors="replace")
            source_map[rel] = text
        except Exception as exc:
            result["errors"].append(f"cannot read {pyf.name}: {exc}")

    all_source = "\n".join(source_map.values())

    # detect framework
    for fw, patterns in FRAMEWORK_PATTERNS.items():
        for pat in patterns:
            if pat in all_source:
                result["framework"] = fw
                break
        if result["framework"]:
            break

    # detect if it's a plain http.server
    if not result["framework"] and ("HTTPServer" in all_source or "BaseHTTPRequestHandler" in all_source):
        result["framework"] = "http.server"

    # detect ports
    port_patterns = [
        re.compile(r'(?:port|PORT)\s*[=:]\s*(\d{4,5})'),
        re.compile(r'app\.run\(.*port\s*=\s*(\d+)', re.DOTALL),
        re.compile(r'uvicorn\.run\(.*port\s*=\s*(\d+)', re.DOTALL),
        re.compile(r'\.listen\((\d+)\)'),
    ]
    seen_ports: set[int] = set()
    for pat in port_patterns:
        for m in pat.finditer(all_source):
            try:
                p = int(m.group(1))
                if 1024 <= p <= 65535 and p not in seen_ports:
                    seen_ports.add(p)
                    result["ports"].append(p)
            except ValueError:
                pass
    # default Flask port
    if result["framework"] == "flask" and not result["ports"]:
        result["ports"].append(5000)

    # detect environment variables
    env_pat = re.compile(r"(?:os\.getenv|os\.environ\.get|os\.environ\[)\s*['\"](\w+)['\"]")
    seen_env: set[str] = set()
    for m in env_pat.finditer(all_source):
        var = m.group(1)
        if var not in seen_env and var.isupper():
            seen_env.add(var)
            is_api_key = any(k in var.lower() for k in ("key", "token", "secret", "api", "password", "auth"))
            result["env_vars"].append({
                "name": var,
                "required": is_api_key,
                "suggested": "OPENAI_API_KEY" if "OPENAI" in var else "",
            })

    # detect endpoints
    fw_endpoint_patterns = ENDPOINT_PATTERNS.get(result.get("framework", ""), [])
    for pat in fw_endpoint_patterns:
        for m in pat.finditer(all_source):
            groups = m.groups()
            if len(groups) == 2:
                verb, path = groups
            else:
                verb, path = "GET", groups[0]
            endpoint = {
                "method": verb.upper(),
                "path": path,
                "param_style": "query" if "request.args" in all_source or "fastapi.Request" in all_source else "json",
            }
            # Check if it reads msg/query param
            if '["msg"]' in all_source or '.get("msg")' in all_source:
                endpoint["param_key"] = "msg"
            elif '["prompt"]' in all_source or '.get("prompt")' in all_source:
                endpoint["param_key"] = "prompt"
            elif '["input"]' in all_source or '.get("input")' in all_source:
                endpoint["param_key"] = "input"
            elif '["query"]' in all_source or '.get("query")' in all_source:
                endpoint["param_key"] = "query"
            elif "request.json" in all_source or "body" in all_source:
                endpoint["param_key"] = "prompt"
            result["endpoints"].append(endpoint)

    # if no endpoints detected via patterns, try AST analysis on each file
    if not result["endpoints"]:
        for _rel, source in source_map.items():
            try:
                tree = ast.parse(source)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        func = _call_name(node)
                        if func and ("add_url_rule" in func or "route" in func):
                            for arg in node.args:
                                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                                    result["endpoints"].append({
                                        "method": "GET",
                                        "path": arg.value,
                                        "param_style": "unknown",
                                    })
            except SyntaxError:
                pass

    return result


def _call_name(node: ast.Call) -> str | None:
    if isinstance(node.func, ast.Attribute):
        parts = []
        cur = node.func
        while isinstance(cur, ast.Attribute):
            parts.append(cur.attr)
            cur = cur.value
        if isinstance(cur, ast.Name):
            parts.append(cur.id)
        return ".".join(reversed(parts))
    if isinstance(node.func, ast.Name):
        return node.func.id
    return None


def _read_file_preview(path: Path, max_lines: int = 20) -> str:
    if not path.exists():
        return ""
    lines = path.read_text(encoding="utf-8", errors="replace").split("\n")
    return "\n".join(lines[:max_lines])


def generate_dockerfile(name: str) -> str | None:
    project = analyze_project(name)
    if not project["exists"]:
        return None

    root = PROJECTS_ROOT / name
    existing_df = root / "Dockerfile"
    if existing_df.exists():
        return existing_df.read_text(encoding="utf-8", errors="replace")

    base = "python:3.12-slim"
    install = "pip install -r requirements.txt" if project["has_requirements"] else "pip install ."
    entrypoint = "python app.py" if (root / "app.py").exists() else "python main.py"

    lines = [
        f"FROM {base}",
        "WORKDIR /app",
        "COPY . .",
        f"RUN {install}",
        f'CMD ["{entrypoint.split()[0]}", "{entrypoint.split()[1]}"]' if " " in entrypoint else f'CMD ["{entrypoint}"]',
    ]
    return "\n".join(lines) + "\n"
