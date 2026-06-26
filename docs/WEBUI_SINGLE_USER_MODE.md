# WebUI single-user/admin mode

VulnoraIQ Desktop Mode and Docker Lab Mode are local operator modes. They run the WebUI on loopback and resolve requests to a built-in local admin principal when `VULNORAIQ_AUTH_ENABLED=false`.

Use production auth for shared internal deployments:

```bash
export VULNORAIQ_ENV=production
export VULNORAIQ_AUTH_ENABLED=true
export VULNORAIQ_ADMIN_TOKEN="$(openssl rand -hex 32)"
```

Desktop Mode runs VulnoraIQ on the host. Docker Desktop is still required, but Docker containers are only created for sandboxed imported agents or local test runtimes.
