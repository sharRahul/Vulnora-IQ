#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
echo "Starting VulnoraIQ WebUI — Docker containers will run in the background."
if command -v python3 >/dev/null 2>&1; then
  python3 scripts/bootstrap_launch.py "$@"
else
  python scripts/bootstrap_launch.py "$@"
fi
echo ""
echo "Docker containers are still running. To stop them later, run:"
echo "  docker compose down"
read -r -p "Press Enter to close this window..." _
