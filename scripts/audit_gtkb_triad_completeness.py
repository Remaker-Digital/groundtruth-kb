#!/usr/bin/env python3
"""Inspect current native specification, test and implementation associations.

This read-only diagnostic uses the selected project's authority configuration.
It never opens a local authority store, parses historical bridge payloads,
executes an adopter suite or mutates canonical records. Owner origin is assessed
during review of the current canonical specification, with unclear cases referred
to the owner. This diagnostic checks mechanical triad relationships only.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

from groundtruth_kb.authority_client import (
    AuthorityClient,
    AuthorityClientError,
    configured_authority_client,
    page_records,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOMAINS = ("specifications", "tests", "test-plans", "test-phases")


@dataclass(frozen=True)
class Gap:
    kind: str
    severity: str
    artifact_id: str
    artifact_path: str | None
    detail: str


def _current_records(client: AuthorityClient) -> dict[str, dict[str, dict[str, Any]]]:
    result = {}
    for domain in DOMAINS:
        records = page_records(client, "/v1/" + domain)
        keyed = {}
        for row in records:
            if row["id"] in keyed or type(row.get("version")) is not int or row["version"] < 1:
                raise AuthorityClientError(
                    "invalid_response",
                    f"{domain} current identities are invalid or duplicated",
                )
            keyed[row["id"]] = row
        result[domain] = keyed
    return result


def _implementation_associations(spec: dict[str, Any]) -> bool:
    constraints = spec.get("constraints")
    return bool(
        spec.get("assertions")
        or spec.get("source_paths")
        or (isinstance(constraints, dict) and constraints.get("implementation_evidence"))
    )


def _dated_passing_result(test: dict[str, Any]) -> bool:
    """A recorded dated PASS is evidence, not execution by this diagnostic."""
    if test.get("last_result") != "pass":
        return False
    timestamp, day = test.get("last_executed_at"), test.get("last_executed_on")
    if bool(timestamp) == bool(day):
        return False
    try:
        if timestamp:
            return (
                isinstance(timestamp, str)
                and datetime.fromisoformat(timestamp.replace("Z", "+00:00")).tzinfo is not None
            )
        return isinstance(day, str) and len(day) == 10 and date.fromisoformat(day).isoformat() == day
    except ValueError:
        return False


def _active_test_ids(records: dict[str, dict[str, dict[str, Any]]]) -> set[str]:
    plans = {row["id"] for row in records["test-plans"].values() if row.get("status") == "active"}
    return {
        test_id
        for phase in records["test-phases"].values()
        if phase.get("plan_id") in plans
        for test_id in (phase.get("test_ids") or [])
    }


def _adopter_review_candidate(spec: dict[str, Any]) -> bool:
    scope = spec.get("application_scope")
    if scope is not None:
        return scope == "application:Agent_Red"
    text = " ".join(
        str(spec.get(key) or "") for key in ("title", "description", "scope", "section", "tags", "source_paths")
    ).lower()
    return any(term in text for term in ("agent red", "agent_red", "agent-red"))


def audit_spec_triad(
    records: dict[str, dict[str, dict[str, Any]]],
) -> tuple[list[Gap], int]:
    """Inspect native completion claims; do not infer verification from status."""
    gaps: list[Gap] = []
    implementation_claims = 0
    active_tests = _active_test_ids(records)
    tests = list(records["tests"].values())
    for spec in sorted(records["specifications"].values(), key=lambda row: row["id"]):
        spec_id, status = spec["id"], spec.get("status")
        if status in {"retired", "superseded"}:
            continue
        if status != "active":
            gaps.append(
                Gap(
                    "noncanonical_spec_status",
                    "high",
                    spec_id,
                    None,
                    "Current native formal status is not active, superseded or retired; reconcile the record without treating a legacy label as verification.",
                )
            )
            continue
        if _adopter_review_candidate(spec):
            gaps.append(
                Gap(
                    "agent_red_scoped_spec_candidate_for_gtkb_reclassification",
                    "medium",
                    spec_id,
                    None,
                    "Review current platform-versus-adopter applicability explicitly; no reclassification is applied by this diagnostic.",
                )
            )
        if not spec.get("implementation_verified_at"):
            continue
        implementation_claims += 1
        paths = spec.get("source_paths") or []
        artifact_path = ", ".join(paths[:3]) or None
        if not _implementation_associations(spec):
            gaps.append(
                Gap(
                    "verified_implementation_without_implementation_evidence",
                    "high",
                    spec_id,
                    artifact_path,
                    "The current implementation verification marker has no assertions, source associations or implementation_evidence constraint. Associations alone do not prove execution.",
                )
            )
        linked = [test for test in tests if test.get("spec_id") == spec_id]
        executable = [test for test in linked if test.get("test_file") and test["id"] in active_tests]
        if not executable:
            gaps.append(
                Gap(
                    "verified_implementation_without_active_test_binding",
                    "critical",
                    spec_id,
                    artifact_path,
                    "No current TEST for this specification declares a test_file and belongs to a phase of an active test plan, as required by the native verification evidence rule.",
                )
            )
        elif not any(_dated_passing_result(test) for test in executable):
            gaps.append(
                Gap(
                    "verified_implementation_without_passing_test_execution",
                    "high",
                    spec_id,
                    artifact_path,
                    "Active declared TEST bindings contain no recorded pass with exactly one valid execution timestamp or date. Definition, coverage mapping and historical adopter labels are not passing execution evidence.",
                )
            )
    return gaps, implementation_claims


def run_audit(project_root: Path, *, client: AuthorityClient | None = None) -> dict[str, Any]:
    """Read all four native collections twice; refuse observed concurrent drift."""
    authority = client if client is not None else configured_authority_client(project_root)
    records = _current_records(authority)
    gaps, claims = audit_spec_triad(records)
    if _current_records(authority) != records:
        raise AuthorityClientError(
            "source_changed",
            "Native audit inputs changed during inspection; read current state and retry. No complete result is available.",
        )
    return {
        "authority_url": authority.url,
        "source": "native_current_records",
        "records_read": {domain: len(rows) for domain, rows in records.items()},
        "implementation_claims": claims,
        "gap_count": len(gaps),
        "by_kind": dict(sorted(Counter(gap.kind for gap in gaps).items())),
        "by_severity": dict(sorted(Counter(gap.severity for gap in gaps).items())),
        "gaps": [asdict(gap) for gap in gaps],
        "assessment_complete": not gaps,
        "limitations": [
            "Native declaration rule only: test_file plus a phase of an active plan. Source/function existence and current byte qualification are separate checks.",
            "Recorded dated test results are not a new execution or independent verification by this audit.",
            "Owner origin is assessed during review of the current canonical specification; unclear cases go to the owner. Mechanical triad completion neither approves nor rejects owner origin.",
            "Repeated reads detect observed drift; this report is an inspection, not a durable authority snapshot.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--json", action="store_true", help="Emit the diagnostic as JSON.")
    parser.add_argument(
        "--fail-on-gaps",
        action="store_true",
        help="Exit 1 for mechanical triad findings.",
    )
    args = parser.parse_args(argv)
    try:
        report = run_audit(args.project_root)
    except AuthorityClientError as error:
        print(
            json.dumps({"error": {"code": error.code, "message": str(error)}}, sort_keys=True),
            file=sys.stderr,
        )
        return 2
    except (OSError, ValueError):
        print(
            json.dumps(
                {
                    "error": {
                        "code": "invalid_configuration",
                        "message": "Unable to load the selected project authority configuration.",
                    }
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("GT-KB native triad inspection")
        print(f"Authority: {report['authority_url']}")
        print(f"Findings: {report['gap_count']}")
        print(f"Mechanical triad checks complete: {report['assessment_complete']}")
        for gap in report["gaps"][:50]:
            print(f"- [{gap['severity']}] {gap['kind']} {gap['artifact_id']}: {gap['detail']}")
        print(report["limitations"][2])
        if report["gap_count"] > 50:
            print("Additional findings are retained in --json output.")
    return 1 if args.fail_on_gaps and not report["assessment_complete"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
