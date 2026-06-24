# Safety model

VulnoraIQ is a controlled AI security assessment lab. Use it only against systems you own or are explicitly authorised to assess.

The current safety model has three layers:

1. **Scope controls** — no default target; all configured targets require explicit authorisation.
2. **Runtime controls** — Docker lab targets use private service names, bounded request limits, safety profiles, rate limits, timeouts, and response-size limits.
3. **Evidence controls** — reports and evidence are written to controlled paths with redaction and artifact path protection.

## Docker lab controls

The current safe lab uses Docker Compose:

- private internal `vulnoraiq-lab` network;
- no host networking;
- no privileged containers;
- no Docker socket mount;
- non-root application users;
- capability drop and `no-new-privileges`;
- Docker-only service-name targets in `config/targets.docker.yaml`;
- host allowlists through safety profiles;
- deterministic test-agent behaviour (behind test profile);
- bounded request count, concurrency, size, timeout, and rate limits;
- sanitized reports and evidence with secret redaction;
- reports, evidence, audit logs, and jobs under `/data`.

## Authorisation gate

All scans require one of these:

- CLI: pass `--authorised`.
- WebUI: confirm the authorisation checklist before scan launch.

Authorisation means the assessor owns the target or has written permission to assess it. VulnoraIQ is not intended for unapproved assessment of third-party systems.

## Fail-closed cases

The current safety posture blocks or fails closed for:

- missing authorisation on configured targets;
- unsupported URL schemes;
- public or external hosts when the selected safety profile does not allow them;
- oversized requests or responses;
- missing Docker lab configuration for Docker lab mode;
- malformed JSON/API requests;
- unsafe artifact path traversal;
- missing production auth configuration when `VULNORAIQ_ENV=production`;
- secrets detected in persisted artifacts or evidence paths where redaction should have applied.

## Evidence boundary

VulnoraIQ collects framework evidence for scanner/reporting purposes. Human review is required before sharing reports or treating a finding as confirmed.

Do not store real credentials, sensitive personal data, production prompts, or business-confidential responses in test fixtures. For real authorised targets, review generated evidence and reports before distribution.

## Not a permission or assurance grant

The safety model reduces accidental misuse and unsafe local testing paths. It does not provide legal authorisation, certified VAPT-grade assurance, or proof that every real-world vulnerability class is detectable.
