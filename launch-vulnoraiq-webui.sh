#!/usr/bin/env bash
set -euo pipefail

# VulnoraIQ Desktop Mode launcher for Linux.
# Source checkouts require Python 3.10+ on PATH.
# Docker Desktop or Docker Engine is required for Docker-based runtime features.

cd "$(dirname "$0")"
echo "============================================================"
echo " VulnoraIQ Desktop Mode"
echo "============================================================"
echo ""
echo "VulnoraIQ will run on this machine and store output in scan-reports/."
echo "Advanced Docker Lab mode is available through ./launch-vulnoraiq-docker-lab.sh."
echo ""

if command -v python3 >/dev/null 2>&1; then
  python3 scripts/desktop_launch.py "$@"
elif command -v python >/dev/null 2>&1; then
  python scripts/desktop_launch.py "$@"
else
  echo "Python was not found on PATH."
  echo "For source checkouts, install Python 3.10+ or use:"
  echo "  ./launch-vulnoraiq-docker-lab.sh"
  exit 1
fi
