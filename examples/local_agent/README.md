# Local mock AI agent

Run a deterministic loopback-only target for VulnoraIQ end-to-end testing:

```bash
python examples/local_agent/server.py --port 9090
vulnoraiq targets validate --target local_mock_agent
vulnoraiq scan --target local_mock_agent --profile ai_agent_foundation --authorised
```

Use `--mode vulnerable` to simulate unsafe responses and `--mode remediated`/`normal` for safe behavior.
