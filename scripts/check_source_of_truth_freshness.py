#!/usr/bin/env python3
"""Evaluate whether a derived source-of-truth extract is safe to use as current.

Contract vocabulary retained for the formal carrier:
- retired-authority: bridge/INDEX.md and harness-state/role-assignments.json
- high-churn sources are live-query-only
- low-churn metadata includes source_id, authority_class, churn_class,
  generated_at, live_query_route, and recovery_route
- expired or conflict evidence routes to recovery
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PACKAGE_SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from groundtruth_kb.context.freshness import (  # noqa: E402,F401
    HIGH_CHURN_CLASSES,
    LOW_CHURN_REQUIRED_FIELDS,
    RETIRED_AUTHORITY_PATHS,
    evaluate_extract,
    run_contract_fixtures,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    report = run_contract_fixtures()
    if args.as_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"SOURCE-OF-TRUTH FRESHNESS: {report['status']}")
        for assertion in report["assertions"]:
            print(f"- {assertion['id']}: {assertion['status']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
