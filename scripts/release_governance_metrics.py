#!/usr/bin/env python3
"""Release-gate enforcement of AUQ governance metrics.

Enforces: Sub-slice F of GTKB-GOV-AUQ-ENFORCEMENT-STACK.
See bridge/gtkb-gov-auq-enforcement-stack-slice-f-release-metrics-2026-05-04 for approved scope.

Invokes 3 release-metric doctor checks:
  - _check_untriaged_prose_decisions
  - _check_auq_coverage
  - _check_uncited_owner_input_bridges

Exits 0 when all 3 pass; exits 1 when any fail. Status output emitted to
stdout for CI log capture; offending findings to stderr.

Usage:
    python scripts/release_governance_metrics.py [--target <path>]

Configuration:
    GTKB_AUQ_METRICS_CUTOFF_DATE: ISO date excluding pre-cutoff history
    from rolling-window metrics (default 2026-05-04, the Sub-slice A -014
    VERIFIED date).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Target project root (defaults to repo root containing this script).",
    )
    args = parser.parse_args()

    target: Path = args.target.resolve()

    # Import doctor checks (deferred so --help works without doctor module loadable).
    sys.path.insert(0, str(target / "groundtruth-kb" / "src"))
    from groundtruth_kb.project.doctor import (
        _check_untriaged_prose_decisions,
        _check_auq_coverage,
        _check_uncited_owner_input_bridges,
    )

    checks = [
        _check_untriaged_prose_decisions(target),
        _check_auq_coverage(target),
        _check_uncited_owner_input_bridges(target),
    ]

    # Block on anything other than status == "pass". Required release-gate
    # metrics whose configuration or helper dependency is invalid (warning) or
    # which fail outright (fail) are NOT clean — they are unverified. Treating
    # warnings as PASS would let misconfigured cutoffs / missing helpers
    # silently bypass the gate. Per Codex -004 F2.
    blocking = [c for c in checks if c.status != "pass"]
    print("=== AUQ Release Governance Metrics ===")
    for c in checks:
        marker = "PASS" if c.status == "pass" else c.status.upper()
        print(f"[{marker}] {c.name}: {c.message}")

    if blocking:
        print("", file=sys.stderr)
        print(
            f"BLOCK: {len(blocking)} of {len(checks)} release governance metrics not clean (status != pass).",
            file=sys.stderr,
        )
        for c in blocking:
            print(f"  - [{c.status.upper()}] {c.name}: {c.message}", file=sys.stderr)
        return 1

    print("")
    print(f"PASS: all {len(checks)} release governance metrics clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
