# AI agent testing

The default AI-agent target is the containerised `local-mock-agent`. It never calls external LLM providers, never executes shell commands, never reads host files, and returns deterministic safe/vulnerable simulation responses for authorised testing.

Run the foundation profile from inside Docker:

```bash
docker compose exec vulnoraiq-web vulnoraiq scan --target local_mock_agent --profile ai_agent_foundation --authorised
```

The profile exercises prompt-injection resistance, system prompt leakage boundaries, tool misuse resistance, RAG context handling, policy bypass attempts, output handling, sensitive-data disclosure checks, agency limits, and audit/report generation.
