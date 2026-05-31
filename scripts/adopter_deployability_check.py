#!/usr/bin/env python3
"""Root script wrapper for the partial Slice 1 adopter deployability gate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
GROUNDTRUTH_SRC = REPO_ROOT / "groundtruth-kb" / "src"
if str(GROUNDTRUTH_SRC) not in sys.path:
    sys.path.insert(0, str(GROUNDTRUTH_SRC))

from groundtruth_kb.adoption.deployability_preservation_gate import (  # noqa: E402
    DEFERRED_PROOFS,
    PARTIAL_CLEARANCE_WARNING,
    check_adopter_deployability,
)


def build_parser() -> argparse.ArgumentParser:
    deferred = "\n".join(f"  - {spec}: {thread}" for spec, thread in DEFERRED_PROOFS.items())
    return argparse.ArgumentParser(
        description=(
            "Run the partial Slice 1 adopter deployability preservation gate. "
            "A PASS is not full deployability clearance."
        ),
        epilog=(
            "Partial Slice 1 coverage only. Deferred proofs that must pass before irreversible adopter work:\n"
            f"{deferred}"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )


def _status_symbol(status: str) -> str:
    return {"PASS": "PASS", "FAIL": "FAIL", "SKIP": "SKIP", "WARN": "WARN"}.get(status, status)


def _print_text(report: object) -> None:
    data = report.as_dict()
    print(f"Adopter deployability preservation gate: {data['summary_status']} (coverage: {data['coverage']})")
    print(PARTIAL_CLEARANCE_WARNING)
    print("Covered specs:")
    for spec in data["covered_specs"]:
        print(f"  - {spec}")
    print("Deferred specs:")
    for spec in data["deferred_specs"]:
        print(f"  - {spec}: {data['deferred_proofs'][spec]}")
    print("Results:")
    for result in data["results"]:
        print(f"  - {_status_symbol(result['status'])} {result['name']}: {result['detail']}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    parser.add_argument("--adopter-root", required=True, type=Path, help="Path to the adopter root to check.")
    parser.add_argument("--json", action="store_true", help="Emit the machine-readable report JSON.")
    args = parser.parse_args(argv)

    report = check_adopter_deployability(args.adopter_root)
    if args.json:
        print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    else:
        _print_text(report)
    return 1 if report.has_failures() else 0


if __name__ == "__main__":
    raise SystemExit(main())
