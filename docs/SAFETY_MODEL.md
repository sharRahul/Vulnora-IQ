# Safety model

VulnoraIQ is for systems you own or are explicitly authorised to assess. Non-demo targets require the `--authorised` flag or WebUI authorisation confirmation.

Docker lab controls:

- private Docker network; no host networking
- no privileged containers
- no Docker socket mount
- non-root application users
- allowlisted Docker service hosts in `docker_lab`
- external/public hosts blocked by default
- safe, non-destructive deterministic payloads
- bounded request count, concurrency, size, timeout, and rate limits
- sanitized evidence and reports with secret redaction
- reports/evidence/audit/job data stored under `/data`

Blocked by default: arbitrary internet targets, unsupported schemes, missing authorisation, oversized requests/responses, missing Docker lab configuration, and secrets in persisted artifacts.
