# Target configuration

VulnoraIQ now has two supported target-configuration paths:

| Path | File | Use |
| --- | --- | --- |
| Docker-first safe lab | `config/targets.docker.yaml` | Recommended for real local AI-agent/RAG/tool-loop testing through Docker Compose. |
| Host-native development/demo | `config/targets.yaml` | Local development, loopback demos, and placeholder internal examples. |

## Docker lab targets

Docker lab targets use service names on the private Compose network, for example `http://local-mock-agent:9090`.

Current Docker lab target shapes include:

| Target | Type | Purpose |
| --- | --- | --- |
| `local_mock_agent` | `chat_completions` | OpenAI-compatible chat-completions mock agent. |
| `local_rag_app` | `rag_query` | Mock RAG query target with answer/context extraction. |
| `local_mock_ollama` | `ollama_generate` | Ollama-style generate endpoint. |
| `local_webhook_agent` | `webhook_json` | Generic webhook-style JSON target. |
| `local_agent_tool_loop` | `agent_tool_loop` | Dry-run tool-loop mock target. |

Docker lab targets are marked with `environment: docker_lab`, `authorisation_required: true`, and `safety_profile: docker_lab`.

## Host-native targets

`config/targets.yaml` keeps the safe `demo` target and loopback/internal templates for local development. Current examples include HTTP JSON, chat-completions, Ollama-generate, RAG query, webhook JSON, and tool-loop shapes.

When testing outside Docker, keep targets on loopback unless you have written permission and a safety profile designed for the environment.

## Required target fields

A configured target should state:

- target name and type;
- `base_url` plus `endpoint_path`, or a full `endpoint`;
- method and request template/body template;
- response extraction path;
- timeout and rate limit;
- environment label;
- owner/contact where applicable;
- `authorisation_required: true` for non-demo targets;
- safety profile;
- tags that describe the target shape and environment.

## Runtime target management

The React WebUI target workspace currently calls backend APIs for:

- `GET /api/targets` — configured and runtime target inventory;
- `POST /api/targets/save` — save a runtime target;
- `POST /api/targets/delete` — delete a runtime target;
- `POST /api/targets/{id}/validate` — validate connectivity and response extraction;
- `GET /api/scans` and `POST /api/scans` — show recent jobs and launch authorised scans.

## Safety rules

- Non-demo targets require explicit authorisation.
- Secrets must be referenced through environment variables, not committed config values.
- Public or external hosts must be disallowed unless the safety profile explicitly permits them for an approved environment.
- Headers, request bodies, responses, evidence, and reports are passed through redaction before persistence.
- Docker lab targets should use Docker service names, not host `localhost`.
