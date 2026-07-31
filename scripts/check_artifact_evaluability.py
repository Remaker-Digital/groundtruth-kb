#!/usr/bin/env python3
"""Read-only, fail-closed evaluation for change-controlled GT-KB artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PACKAGE_SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from groundtruth_kb.assertions import _VALID_ASSERTION_TYPES, run_single_assertion  # noqa: E402
from groundtruth_kb.db import KnowledgeDB  # noqa: E402

EVALUATOR_VERSION = 1
CHANGE_CONTROLLED_TYPES = {"architecture_decision", "design_constraint", "governance"}
EVIDENCE_STATES = {"current", "stale", "unavailable", "contradictory", "unverifiable"}
GOVERNED_GATES = {"implementation", "verification", "promotion", "closure"}
HISTORICAL_CLASSIFICATIONS = {"KEEP", "QUARANTINE"}

# Stable machine reasons are part of the evaluator's diagnostic contract.
_UNSUPPORTED_REQUIRED = "unsupported-required"
_ZERO_EXECUTABLE = "zero-executable"
_MIXED_REQUIRED = "mixed-required"
_NEVER_PASS = "never-pass"
_PROSE_STORED_RECONCILIATION = "prose-stored-reconciliation"
_CURRENT_GATE = "current-gate"
_HISTORICAL_FIXTURE = "historical-fixture"
_ACTIVE_LEAKAGE = "active-leakage"
_HARD_INVARIANT = "hard-invariant"
_FULLY_EXECUTABLE = "fully-executable"
_BASELINE_REGRESSION = "baseline-regression"
_LEGITIMATE_RESULTS = "legitimate-results"


class EvaluationError(RuntimeError):
    """Raised when requested evaluation cannot be performed safely."""


def _canonical_hash(value: Any) -> str:
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest().upper()


def evaluator_hash() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest().upper()


def _assertions(spec: dict[str, Any]) -> list[Any]:
    parsed = spec.get("_assertions_parsed")
    if parsed is None:
        parsed = spec.get("assertions_parsed")
    if isinstance(parsed, list):
        return parsed
    raw = spec.get("assertions")
    if not raw:
        return []
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise EvaluationError(f"{spec.get('id')}: assertions are malformed JSON: {exc}") from exc
    if not isinstance(raw, list):
        raise EvaluationError(f"{spec.get('id')}: assertions must be a list")
    return raw


def _assertion_id(assertion: Any, index: int) -> str:
    if isinstance(assertion, dict) and isinstance(assertion.get("id"), str) and assertion["id"].strip():
        return assertion["id"].strip()
    return f"INDEX-{index + 1}"


def _unsupported_types(assertion: Any, path: str) -> list[str]:
    if not isinstance(assertion, dict):
        return [f"{path}:text"]
    assertion_type = assertion.get("type")
    if assertion_type not in _VALID_ASSERTION_TYPES:
        return [f"{path}:{assertion_type or '<missing>'}"]
    unsupported: list[str] = []
    if assertion_type in {"all_of", "any_of"}:
        for index, child in enumerate(assertion.get("assertions") or []):
            unsupported.extend(_unsupported_types(child, f"{path}.{index + 1}"))
    return unsupported


def _required_prose_statements(description: object) -> list[str]:
    if not isinstance(description, str):
        return []
    match = re.search(
        r"^## Required Executable Assertions\s*$([\s\S]*?)(?=^##\s|\Z)",
        description,
        flags=re.MULTILINE,
    )
    if not match:
        return []
    return [item.group(1).strip() for item in re.finditer(r"^\s*\d+\.\s+(.+?)\s*$", match.group(1), flags=re.MULTILINE)]


def _statement_tokens(value: str) -> set[str]:
    stop_words = {"a", "an", "and", "are", "is", "of", "or", "the", "to"}
    return {token for token in re.findall(r"[a-z0-9]+", value.lower()) if token not in stop_words}


def _statements_correspond(left: str, right: str) -> bool:
    left_tokens = _statement_tokens(left)
    right_tokens = _statement_tokens(right)
    if not left_tokens or not right_tokens:
        return False
    similarity = len(left_tokens & right_tokens) / len(left_tokens | right_tokens)
    currentness_terms = {"contradictory", "currentness", "invalid", "stale", "unavailable", "unverifiable"}
    currentness_equivalent = (
        {"evidence", "current", "gate"} <= left_tokens | right_tokens
        and bool(left_tokens & currentness_terms)
        and bool(right_tokens & currentness_terms)
    )
    return similarity >= 0.45 or currentness_equivalent


def reconcile_prose_and_stored(spec: dict[str, Any], indexed: list[tuple[str, Any]]) -> dict[str, Any]:
    prose = _required_prose_statements(spec.get("description"))
    outer_ids = [assertion_id for assertion_id, _ in indexed]
    stored_descriptions = [
        str(assertion.get("description") or "") if isinstance(assertion, dict) else str(assertion)
        for _, assertion in indexed
    ]
    if not prose:
        return {
            "status": "NOT_APPLICABLE",
            "reason": _PROSE_STORED_RECONCILIATION,
            "outer_ids": outer_ids,
            "count": len(indexed),
            "order_matches": None,
        }
    order_matches = len(prose) == len(stored_descriptions) and all(
        _statements_correspond(prose_item, stored_item)
        for prose_item, stored_item in zip(prose, stored_descriptions, strict=True)
    )
    return {
        "status": "PASS" if order_matches else "FAIL",
        "reason": _PROSE_STORED_RECONCILIATION,
        "outer_ids": outer_ids,
        "count": {"prose": len(prose), "stored": len(indexed)},
        "order_matches": order_matches,
    }


def classify_historical_evidence(path: str, *, active_loading_paths: set[str]) -> dict[str, str]:
    normalized = Path(path).as_posix()
    if normalized in {Path(item).as_posix() for item in active_loading_paths}:
        return {"classification": "FAIL", "reason": _ACTIVE_LEAKAGE}
    if any(part in {"archive", "history", "fixtures"} for part in Path(normalized).parts):
        return {"classification": "KEEP", "reason": _HISTORICAL_FIXTURE}
    return {"classification": "QUARANTINE", "reason": _HISTORICAL_FIXTURE}


def satisfies_governed_gate(evaluation: dict[str, Any], gate: str, *, hard_invariant: bool = False) -> bool:
    if gate not in GOVERNED_GATES:
        raise EvaluationError(f"unsupported governed gate: {gate}")
    # Missing hard-invariant evidence blocks implementation, verification,
    # promotion, and closure; only a current full-carrier PASS satisfies them.
    if hard_invariant and evaluation.get("carrier_result") != "PASS":
        return False
    return evaluation.get("carrier_result") == "PASS"


def _aggregate_status(statuses: list[str]) -> str:
    if not statuses:
        return "NOT_APPLICABLE"
    if all(status == "PASS" for status in statuses):
        return "PASS"
    if any(status == "FAIL" for status in statuses):
        return "FAIL"
    if all(status == "UNASSESSED" for status in statuses):
        return "UNASSESSED"
    return "PARTIAL"


def evaluate_spec(
    spec: dict[str, Any],
    *,
    project_root: Path,
    assertion_ids: set[str] | None = None,
    evaluated_at: datetime | None = None,
    evidence_state: str = "current",
) -> dict[str, Any]:
    if evidence_state not in EVIDENCE_STATES:
        raise EvaluationError(f"unsupported evidence state: {evidence_state}")
    assertions = _assertions(spec)
    indexed = [(_assertion_id(assertion, index), assertion) for index, assertion in enumerate(assertions)]
    duplicate_ids = sorted(
        assertion_id
        for assertion_id in {item[0] for item in indexed}
        if sum(candidate_id == assertion_id for candidate_id, _ in indexed) > 1
    )
    if duplicate_ids:
        raise EvaluationError(f"{spec.get('id')}: duplicate assertion ids: {', '.join(duplicate_ids)}")

    available_ids = {assertion_id for assertion_id, _ in indexed}
    selected_ids = available_ids if assertion_ids is None else set(assertion_ids)
    unknown_ids = sorted(selected_ids - available_ids)
    if unknown_ids:
        raise EvaluationError(f"{spec.get('id')}: unknown scoped assertion ids: {', '.join(unknown_ids)}")
    selected = [(assertion_id, assertion) for assertion_id, assertion in indexed if assertion_id in selected_ids]
    deferred_ids = [assertion_id for assertion_id, _ in indexed if assertion_id not in selected_ids]
    unsupported = [item for assertion_id, assertion in selected for item in _unsupported_types(assertion, assertion_id)]

    results: list[dict[str, Any]] = []
    for assertion_id, assertion in selected:
        result = run_single_assertion(assertion, project_root)
        results.append({"assertion_id": assertion_id, **result})
    raw_scope_result = _aggregate_status([str(result.get("status") or "UNASSESSED") for result in results])
    reconciliation = reconcile_prose_and_stored(spec, indexed)
    if unsupported:
        scope_result = "FAIL"
        evaluation_reason = _UNSUPPORTED_REQUIRED
    elif not selected:
        scope_result = "UNASSESSED"
        evaluation_reason = _ZERO_EXECUTABLE
    elif evidence_state != "current":
        scope_result = "FAIL"
        evaluation_reason = f"{_CURRENT_GATE}:{evidence_state}"
    elif reconciliation["status"] == "FAIL":
        scope_result = "FAIL"
        evaluation_reason = _PROSE_STORED_RECONCILIATION
    else:
        scope_result = raw_scope_result
        evaluation_reason = (
            _FULLY_EXECUTABLE
            if scope_result == "PASS"
            else (_MIXED_REQUIRED if scope_result == "PARTIAL" else _NEVER_PASS)
        )
    carrier_result = "PARTIAL" if deferred_ids and scope_result == "PASS" else scope_result
    timestamp = evaluated_at or datetime.now(UTC)
    subject_payload = {
        "id": spec.get("id"),
        "version": spec.get("version"),
        "type": spec.get("type"),
        "assertions": assertions,
    }
    return {
        "subject_id": spec.get("id"),
        "subject_version": spec.get("version"),
        "subject_sha256": _canonical_hash(subject_payload),
        "evaluator_version": EVALUATOR_VERSION,
        "evaluator_sha256": evaluator_hash(),
        "evaluated_at": timestamp.isoformat(),
        "scope": "full" if assertion_ids is None else "scoped",
        "selected_assertion_ids": [assertion_id for assertion_id, _ in selected],
        "deferred_assertion_ids": deferred_ids,
        "scope_result": scope_result,
        "carrier_result": carrier_result,
        "evaluation_reason": evaluation_reason,
        "unsupported_required": unsupported,
        "prose_stored_reconciliation": reconciliation,
        "evidence_state": evidence_state,
        "currentness": {
            "subject_version": spec.get("version"),
            "state": evidence_state,
            "invalidated_by": ["subject_version_change", "assertion_definition_change", "evaluator_change"],
        },
        "gate_semantics": {
            "hard_invariant": _HARD_INVARIANT,
            "blocked_gates": sorted(GOVERNED_GATES),
            "historical_classifications": sorted(HISTORICAL_CLASSIFICATIONS),
            "non_regression": [_BASELINE_REGRESSION, _LEGITIMATE_RESULTS],
        },
        "results": results,
    }


def evaluate_specs(
    db: KnowledgeDB,
    *,
    project_root: Path,
    spec_ids: list[str] | None = None,
    assertion_ids: set[str] | None = None,
    evidence_state: str = "current",
) -> dict[str, Any]:
    if spec_ids:
        specs: list[dict[str, Any]] = []
        for spec_id in spec_ids:
            spec = db.get_spec(spec_id)
            if spec is None:
                raise EvaluationError(f"spec not found: {spec_id}")
            specs.append(spec)
    else:
        specs = [spec for spec in db.list_specs() if spec.get("type") in CHANGE_CONTROLLED_TYPES]
    if assertion_ids is not None and len(specs) != 1:
        raise EvaluationError("--assertion requires exactly one --spec")

    evaluations = [
        evaluate_spec(
            spec,
            project_root=project_root,
            assertion_ids=assertion_ids,
            evidence_state=evidence_state,
        )
        for spec in sorted(specs, key=lambda item: str(item.get("id") or ""))
    ]
    aggregate_result = _aggregate_status([item["scope_result"] for item in evaluations])
    return {
        "schema_version": 1,
        "aggregate_result": aggregate_result,
        "carrier_count": len(evaluations),
        "scope": "scoped" if assertion_ids is not None else "full",
        "evaluations": evaluations,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--database", type=Path, default=None)
    parser.add_argument("--spec", action="append", dest="spec_ids")
    parser.add_argument("--assertion", action="append", dest="assertion_ids")
    parser.add_argument("--evidence-state", choices=sorted(EVIDENCE_STATES), default="current")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    project_root = args.project_root.resolve()
    database = args.database or (project_root / "groundtruth.db")

    db = KnowledgeDB(database)
    try:
        report = evaluate_specs(
            db,
            project_root=project_root,
            spec_ids=args.spec_ids,
            assertion_ids=set(args.assertion_ids) if args.assertion_ids else None,
            evidence_state=args.evidence_state,
        )
    except EvaluationError as exc:
        print(f"ARTIFACT EVALUABILITY: FAIL - {exc}", file=sys.stderr)
        return 1
    finally:
        db.close()

    if args.as_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"ARTIFACT EVALUABILITY: {report['aggregate_result']} ({report['carrier_count']} carriers)")
        for evaluation in report["evaluations"]:
            print(
                f"- {evaluation['subject_id']} v{evaluation['subject_version']}: "
                f"scope={evaluation['scope_result']} carrier={evaluation['carrier_result']}"
            )
    return 0 if report["aggregate_result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
