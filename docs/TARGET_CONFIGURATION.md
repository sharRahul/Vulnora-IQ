# Target configuration

Docker lab targets are defined in `config/targets.docker.yaml` and use Docker service names such as `http://local-mock-agent:9090`, never host `localhost`. Each non-demo target requires explicit authorisation and a safety profile.

The `docker_lab` safety profile in `config/safety_profiles.yaml` allows only HTTP traffic to approved Docker service names, bounds request/response sizes, enforces timeouts and rate limits, requires authorisation, and blocks external/public hosts fail-closed.

Secrets must be referenced through environment variables only. Headers, request bodies, responses, evidence, and reports are passed through redaction before persistence.
