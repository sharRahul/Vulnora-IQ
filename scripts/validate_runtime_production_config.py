#!/usr/bin/env python3
from __future__ import annotations

import json
import logging
import sys

from webui.production_checks import validate_all

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
LOGGER = logging.getLogger("validate_runtime")


def main() -> None:
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    results = validate_all(host=host)
    failed = [r for r in results if r["status"] != "pass"]
    passed_count = sum(1 for r in results if r["status"] == "pass")
    print(json.dumps({"checks": results, "passed": passed_count, "failed": len(failed)}, indent=2))
    if failed:
        LOGGER.error("Production configuration validation FAILED: %d check(s) failed.", len(failed))
        sys.exit(1)
    LOGGER.info("Production configuration validation PASSED (%d checks).", passed_count)


if __name__ == "__main__":
    main()
