# WebUI guide

Start Docker Compose and open <http://localhost:8787>. The WebUI loads configured Docker lab targets from the same backend scanner used by the CLI. Use target validation to confirm connectivity and response extraction, confirm authorisation, start a scan, watch job events, inspect findings/evidence, and download reports.

Docker lab targets are labelled with `environment: docker_lab` and tags including `docker` and `mock`. Non-demo scans remain gated by explicit authorisation.
