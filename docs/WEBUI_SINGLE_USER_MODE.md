# WebUI local single-user/admin mode

VulnoraIQ Desktop Mode uses an explicit local operator auth mode:

```bash
VULNORAIQ_AUTH_MODE=local_admin
```

In this mode the WebUI resolves requests to the built-in `local-admin` principal. It is intended only for a single operator using a local WebUI session.

Safety guardrails:

- `local_admin` is rejected when `VULNORAIQ_ENV=production`.
- `local_admin` normally requires the WebUI host to be loopback: `127.0.0.1`, `::1`, or `localhost`.
- Docker Lab may bind inside the container to `0.0.0.0` only when it explicitly sets `VULNORAIQ_RUN_MODE=docker_lab` and `VULNORAIQ_LOCAL_ADMIN_BIND_OK=true`; the Compose file still publishes the port on host loopback only.
- `VULNORAIQ_AUTH_ENABLED=false` remains only as a backward-compatible alias for `VULNORAIQ_AUTH_MODE=local_admin`.

Use token auth for production or shared internal deployments:

```bash
export VULNORAIQ_ENV=production
export VULNORAIQ_AUTH_MODE=token
export VULNORAIQ_ADMIN_TOKEN="<strong-admin-token>"
```

Desktop Mode runs VulnoraIQ on the host. Docker Desktop is still required, but Docker containers are only created for sandboxed imported agents or local test runtimes.
