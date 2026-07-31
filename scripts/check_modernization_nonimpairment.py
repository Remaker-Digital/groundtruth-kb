#!/usr/bin/env python3
"""Validate modernization activation evidence for intuitiveness and non-impairment."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

MEASUREMENT_DIRECTIONS = {"equal", "higher_or_equal", "lower_or_equal"}


class NonImpairmentError(RuntimeError):
    """Raised when the evidence artifact cannot be evaluated."""


def _measurement_passes(item: dict[str, Any]) -> bool:
    direction = item.get("direction")
    baseline = item.get("baseline")
    result = item.get("result")
    if direction not in MEASUREMENT_DIRECTIONS:
        return False
    if not isinstance(baseline, (int, float)) or not isinstance(result, (int, float)):
        return False
    if direction == "equal":
        return result == baseline
    if direction == "higher_or_equal":
        return result >= baseline
    return result <= baseline


def evaluate_evidence(evidence: dict[str, Any]) -> dict[str, Any]:
    findings: list[dict[str, str]] = []

    measurements = evidence.get("measurements")
    if not isinstance(measurements, list) or not measurements:
        findings.append({"id": "baseline-result", "severity": "P1", "reason": "missing measurements"})
    else:
        for index, item in enumerate(measurements):
            if not isinstance(item, dict) or not _measurement_passes(item):
                metric_id = item.get("id") if isinstance(item, dict) else None
                findings.append(
                    {
                        "id": str(metric_id or f"measurement-{index + 1}"),
                        "severity": "P1",
                        "reason": "result impairs baseline or measurement contract is invalid",
                    }
                )

    rollback = evidence.get("rollback")
    if (
        not isinstance(rollback, dict)
        or not isinstance(rollback.get("instructions"), str)
        or not rollback["instructions"].strip()
        or rollback.get("tested") is not True
        or not rollback.get("evidence")
    ):
        findings.append({"id": "rollback", "severity": "P1", "reason": "rollback is absent or untested"})

    hard_invariants = evidence.get("hard_invariants")
    if not isinstance(hard_invariants, list) or not hard_invariants:
        findings.append({"id": "hard-invariant", "severity": "P0", "reason": "hard-invariant evidence is missing"})
    else:
        for item in hard_invariants:
            if (
                not isinstance(item, dict)
                or item.get("status") != "PASS"
                or not item.get("id")
                or not item.get("evidence")
            ):
                invariant_id = item.get("id") if isinstance(item, dict) else None
                findings.append(
                    {
                        "id": str(invariant_id or "hard-invariant"),
                        "severity": "P0",
                        "reason": "hard-invariant does not have passing evidence",
                    }
                )

    active_paths = {
        Path(path).as_posix() for path in evidence.get("worker_loading_paths", []) if isinstance(path, str) and path
    }
    superseded = evidence.get("superseded_guidance")
    if not isinstance(superseded, list):
        findings.append({"id": "superseded", "severity": "P0", "reason": "superseded-guidance disposition is missing"})
    else:
        for item in superseded:
            if not isinstance(item, dict) or not item.get("path") or not item.get("disposition"):
                findings.append({"id": "superseded", "severity": "P1", "reason": "superseded guidance is undisposed"})
                continue
            path = Path(str(item["path"])).as_posix()
            if path in active_paths:
                findings.append(
                    {
                        "id": path,
                        "severity": "P0",
                        "reason": "superseded guidance remains on a worker-loading path",
                    }
                )

    required_routes = ("canonical_authority", "primary_read_route", "primary_mutation_route")
    for field in required_routes:
        if not isinstance(evidence.get(field), str) or not evidence[field].strip():
            findings.append({"id": field, "severity": "P1", "reason": f"missing {field}"})

    return {
        "schema_version": 1,
        "status": "PASS" if not findings else "FAIL",
        "activation_allowed": not findings,
        "blocked_gates": [] if not findings else ["implementation", "verification", "promotion", "closure"],
        "findings": findings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    try:
        payload = json.loads(args.evidence.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"MODERNIZATION NON-IMPAIRMENT: FAIL - {exc}", file=sys.stderr)
        return 1
    if not isinstance(payload, dict):
        print("MODERNIZATION NON-IMPAIRMENT: FAIL - evidence root must be an object", file=sys.stderr)
        return 1
    report = evaluate_evidence(payload)
    if args.as_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"MODERNIZATION NON-IMPAIRMENT: {report['status']}")
        for finding in report["findings"]:
            print(f"- {finding['severity']} {finding['id']}: {finding['reason']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
