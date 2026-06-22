from __future__ import annotations

import hashlib
import hmac
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(slots=True)
class AuthPrincipal:
    username: str
    role: str
    permissions: set[str]
    authenticated: bool


_ENV_AUTH_ENABLED = "VULNORAIQ_AUTH_ENABLED"
_ENV_ADMIN_TOKEN = "VULNORAIQ_ADMIN_TOKEN"
_ENV_ANALYST_TOKEN = "VULNORAIQ_ANALYST_TOKEN"
_ENV_VIEWER_TOKEN = "VULNORAIQ_VIEWER_TOKEN"
_ENV_PRODUCTION = "VULNORAIQ_ENV"

_DEFAULT_PERMISSIONS: dict[str, set[str]] = {
    "viewer": {"view_scans", "download_artifacts"},
    "analyst": {"view_scans", "download_artifacts", "start_demo_scan"},
    "admin": {"view_scans", "download_artifacts", "start_demo_scan", "start_configured_scan", "manage_runtime"},
}

_INTERNAL_ADMIN_TOKEN = "vulnoraiq-internal-admin-token"

# Minimum token length for production mode
_MIN_TOKEN_LENGTH = 20


class WebAuthManager:
    """Role-aware auth manager driven by environment variables.

    Auth is enabled by default (VULNORAIQ_AUTH_ENABLED=true).
    Set VULNORAIQ_AUTH_ENABLED=false to disable (not recommended for production).

    Token env vars (mutually exclusive with file config):
      VULNORAIQ_ADMIN_TOKEN  - full access
      VULNORAIQ_ANALYST_TOKEN - demo-scan + view access
      VULNORAIQ_VIEWER_TOKEN  - view-only access

    Falls back to config/web_users.yaml if no token env vars are set.
    The file-based fallback is NOT allowed in production mode.

    Production mode (VULNORAIQ_ENV=production):
      - Auth must be enabled
      - At least VULNORAIQ_ADMIN_TOKEN must be set and meet minimum length
      - File-based demo users are rejected
      - Internal admin token is disabled
    """

    def __init__(self, path: str | Path = "config/web_users.yaml") -> None:
        self.path = Path(path)
        self._config: dict[str, Any] | None = None
        self._env_tokens: dict[str, str] | None = None

    def is_production(self) -> bool:
        return os.getenv(_ENV_PRODUCTION, "").strip().lower() == "production"

    def _validate_production(self) -> None:
        if not self.is_production():
            return
        if not self.enabled():
            raise RuntimeError(
                "Production mode requires VULNORAIQ_AUTH_ENABLED=true. "
                "Set VULNORAIQ_ENV=development to run with auth disabled."
            )
        env_tokens = self._load_env_tokens()
        if not env_tokens or "admin" not in env_tokens.values():
            raise RuntimeError(
                "Production mode requires at least VULNORAIQ_ADMIN_TOKEN to be set "
                "with a value of 20 characters or more."
            )
        for token, role in env_tokens.items():
            if role == "admin" and len(token) < _MIN_TOKEN_LENGTH:
                raise RuntimeError(
                    f"VULNORAIQ_ADMIN_TOKEN must be at least {_MIN_TOKEN_LENGTH} characters "
                    f"in production mode (got {len(token)})."
                )

    def _load_env_tokens(self) -> dict[str, str]:
        if self._env_tokens is None:
            tokens: dict[str, str] = {}
            for key, role in [
                (_ENV_ADMIN_TOKEN, "admin"),
                (_ENV_ANALYST_TOKEN, "analyst"),
                (_ENV_VIEWER_TOKEN, "viewer"),
            ]:
                val = os.getenv(key, "").strip()
                if val:
                    tokens[val] = role
            self._env_tokens = tokens
        return self._env_tokens

    def has_file_auth(self) -> bool:
        """Return True if the file-based auth config exists and has any active users."""
        if not self.path.exists():
            return False
        users = self.load().get("users", [])
        return any(u.get("status") == "active" for u in users)

    def load(self) -> dict[str, Any]:
        if self._config is None:
            if self.path.exists():
                self._config = yaml.safe_load(self.path.read_text(encoding="utf-8")) or {}
            else:
                self._config = {}
        return self._config

    def enabled(self) -> bool:
        env_val = os.getenv(_ENV_AUTH_ENABLED)
        if env_val is not None:
            return env_val.lower() in ("1", "true", "yes")
        # In production mode, default to enabled
        if self.is_production():
            return True
        cfg = self.load()
        return cfg.get("auth", {}).get("enabled", True) if cfg else True

    def header_name(self) -> str:
        return str(self.load().get("auth", {}).get("header_name", "X-VulnoraIQ-Token"))

    def anonymous(self) -> AuthPrincipal:
        return AuthPrincipal("anonymous", "viewer", _DEFAULT_PERMISSIONS["viewer"], authenticated=False)

    def authenticate_token(self, token: str | None) -> AuthPrincipal | None:
        if not self.enabled():
            return AuthPrincipal("anonymous", "analyst", _DEFAULT_PERMISSIONS["analyst"], authenticated=False)

        if not token:
            return None

        # Internal admin token is disabled in production
        if not self.is_production() and token == _INTERNAL_ADMIN_TOKEN:
            return AuthPrincipal("internal", "admin", _DEFAULT_PERMISSIONS["admin"], authenticated=True)

        env_tokens = self._load_env_tokens()
        if env_tokens:
            # Constant-time comparison
            for candidate, role in env_tokens.items():
                if hmac.compare_digest(candidate, token):
                    return AuthPrincipal(
                        f"env-{role}", role, _DEFAULT_PERMISSIONS[role], authenticated=True
                    )
            return None

        # File-based fallback (not allowed in production)
        if self.is_production():
            return None

        digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
        for user in self.load().get("users", []):
            if user.get("status") != "active":
                continue
            if str(user.get("token_hash")) == digest:
                role = str(user.get("role", "viewer"))
                return AuthPrincipal(
                    str(user.get("username")), role, self.permissions_for_role(role), authenticated=True
                )
        return None

    def permissions_for_role(self, role: str) -> set[str]:
        if role in _DEFAULT_PERMISSIONS:
            return _DEFAULT_PERMISSIONS[role]
        roles = self.load().get("roles", {})
        visited: set[str] = set()

        def collect(current_role: str) -> set[str]:
            if current_role in visited:
                return set()
            visited.add(current_role)
            spec = roles.get(current_role, {})
            permissions = set(spec.get("permissions", []))
            for parent in spec.get("inherits", []) or []:
                permissions |= collect(str(parent))
            return permissions

        return collect(role)

    @staticmethod
    def can(principal: AuthPrincipal, permission: str) -> bool:
        return permission in principal.permissions
