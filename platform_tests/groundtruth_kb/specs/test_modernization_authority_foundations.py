"""Modernization authority-foundation carriers, read from the native authority.

The former frozen acceptance module required eight carriers to be current and fully evaluable from the retired local
store. The current corpus is read here with each carrier's expected status; the active carriers must carry stated
authority, unique outer assertion ids, live root-bound enforcement sources, a PASS from the artifact evaluator
wherever inline assertions exist and, wherever the evaluator reports UNASSESSED, at least one TEST row of the carrier
that names an executable test module of this repository (read from /v1/tests, function verified when named). A
carrier's required test artifacts must each exist and be bound that way. Every active carrier proves an executable
binding natively; nothing is named.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
EVALUATOR_PATH = REPO_ROOT / "scripts" / "check_artifact_evaluability.py"
NONAUTHORITATIVE_SOURCE_PREFIXES = (".gtkb-state/", "bridge/", "memory/")

# Carrier -> expected current status. The superseded and retired entries record owner-directed changes of the corpus.
AUTHORITY_CARRIERS = {
    "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001": "active",
    "ADR-EXPLICIT-HINT-CONTEXT-MANAGEMENT-001": "superseded",
    "DCL-ACTIVITY-CONTEXT-MANIFEST-001": "active",
    "GOV-SOURCE-OF-TRUTH-FRESHNESS-001": "active",
    "GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001": "active",
    "GOV-SESSION-ROLE-AUTHORITY-001": "retired",
    "DCL-SESSION-ROLE-RESOLUTION-001": "active",
    "DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001": "active",
}


@pytest.fixture(scope="module")
def evaluator():
    spec = importlib.util.spec_from_file_location("modernization_authority_evaluator", EVALUATOR_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def carriers(formal_record) -> dict[str, dict]:
    return {
        record_id: formal_record(record_id, expected_status=status) for record_id, status in AUTHORITY_CARRIERS.items()
    }


def _active(carriers: dict[str, dict]) -> dict[str, dict]:
    return {record_id: record for record_id, record in carriers.items() if record["status"] == "active"}


@pytest.fixture(scope="module")
def bindings(executable_test_bindings, carriers) -> dict[str, list[dict]]:
    """Executable TEST rows per active carrier, read natively (the conftest fixture states the executable rule)."""
    return {record_id: executable_test_bindings(record_id) for record_id in _active(carriers)}


def _inline_assertion_ids(record: dict) -> list:
    return [item.get("id") for item in record.get("assertions") or [] if isinstance(item, dict)]


def test_active_carriers_are_stated_and_uniquely_asserted(carriers, bindings):
    problems: list[str] = []
    for record_id, record in _active(carriers).items():
        if record.get("authority") != "stated":
            problems.append(f"{record_id}: authority is {record.get('authority')!r}, expected 'stated'")
        assertion_ids = _inline_assertion_ids(record)
        if any(not assertion_id for assertion_id in assertion_ids):
            problems.append(f"{record_id}: every outer assertion requires an id")
        if len(assertion_ids) != len(set(assertion_ids)):
            problems.append(f"{record_id}: duplicate outer assertion ids")
        if not assertion_ids and not bindings[record_id]:
            problems.append(f"{record_id}: no inline assertion and no executable TEST binding")
    assert not problems, "\n".join(problems)


def test_active_carrier_enforcement_sources_are_live_root_bound_files(carriers):
    problems: list[str] = []
    for record_id, record in _active(carriers).items():
        source_paths = record.get("source_paths") or []
        if not source_paths:
            problems.append(f"{record_id}: no enforcement source paths")
            continue
        for raw_path in source_paths:
            path = Path(raw_path)
            normalized = path.as_posix()
            if path.is_absolute() or ".." in path.parts:
                problems.append(f"{record_id}: source escapes project root: {raw_path}")
            elif normalized.startswith(NONAUTHORITATIVE_SOURCE_PREFIXES):
                problems.append(f"{record_id}: source is historical/non-authoritative: {raw_path}")
            elif not (REPO_ROOT / path).is_file():
                problems.append(f"{record_id}: source file is missing: {raw_path}")
    assert not problems, "\n".join(problems)


def test_active_carriers_with_executable_assertions_evaluate_to_pass(evaluator, carriers, bindings):
    outcomes = {
        record_id: evaluator.evaluate_spec(record, project_root=REPO_ROOT)
        for record_id, record in _active(carriers).items()
    }
    failures = [
        f"{record_id}: {result['carrier_result']} ({result['evaluation_reason']})"
        for record_id, result in outcomes.items()
        if _inline_assertion_ids(carriers[record_id]) and result["carrier_result"] != "PASS"
    ]
    failures += [
        f"{record_id}: UNASSESSED ({result['evaluation_reason']}) and no executable TEST binding"
        for record_id, result in outcomes.items()
        if result["carrier_result"] == "UNASSESSED" and not bindings[record_id]
    ]
    assert not failures, "\n".join(failures)


def test_required_test_artifacts_have_executable_bindings(carriers, bindings):
    problems: list[str] = []
    for record_id, record in _active(carriers).items():
        constraints = record.get("constraints")
        required = constraints.get("required_test_artifacts") if isinstance(constraints, dict) else None
        bound_files = {Path(row["test_file"]).as_posix() for row in bindings[record_id]}
        for raw_path in required or []:
            module = Path(raw_path).as_posix()
            if not (REPO_ROOT / module).is_file():
                problems.append(f"{record_id}: required test artifact is missing: {raw_path}")
            elif module not in bound_files:
                problems.append(f"{record_id}: required test artifact has no executable TEST binding: {raw_path}")
    assert not problems, "\n".join(problems)
