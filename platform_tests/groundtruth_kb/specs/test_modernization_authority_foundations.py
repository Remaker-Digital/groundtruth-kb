"""Modernization authority-foundation carriers, read from the native authority.

The former frozen acceptance module required eight carriers to be current and fully evaluable from the retired local
store. The current corpus is read here with each carrier's expected status; the active carriers must carry stated
authority, unique outer assertion ids, live root-bound enforcement sources and a PASS from the artifact evaluator
wherever executable assertions exist. Carriers without executable assertions are named, not silently tolerated.
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
# Active carriers whose imported records carry no executable assertion; the evaluator reports them UNASSESSED.
# Adding executable assertions to them is formal work, not a test concern; removing a name here requires that work.
WITHOUT_EXECUTABLE_ASSERTIONS = {
    "DCL-ACTIVITY-CONTEXT-MANIFEST-001",
    "GOV-SOURCE-OF-TRUTH-FRESHNESS-001",
    "GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001",
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


def test_active_carriers_are_stated_and_uniquely_asserted(carriers):
    problems: list[str] = []
    for record_id, record in _active(carriers).items():
        if record.get("authority") != "stated":
            problems.append(f"{record_id}: authority is {record.get('authority')!r}, expected 'stated'")
        assertion_ids = [item.get("id") for item in record.get("assertions") or [] if isinstance(item, dict)]
        if any(not assertion_id for assertion_id in assertion_ids):
            problems.append(f"{record_id}: every outer assertion requires an id")
        if len(assertion_ids) != len(set(assertion_ids)):
            problems.append(f"{record_id}: duplicate outer assertion ids")
        if not assertion_ids and record_id not in WITHOUT_EXECUTABLE_ASSERTIONS:
            problems.append(f"{record_id}: no executable assertion and not named as such")
        if assertion_ids and record_id in WITHOUT_EXECUTABLE_ASSERTIONS:
            problems.append(f"{record_id}: now carries executable assertions; remove it from the named list")
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


def test_active_carriers_with_executable_assertions_evaluate_to_pass(evaluator, carriers):
    outcomes = {
        record_id: evaluator.evaluate_spec(record, project_root=REPO_ROOT)
        for record_id, record in _active(carriers).items()
    }
    failures = [
        f"{record_id}: {result['carrier_result']} ({result['evaluation_reason']})"
        for record_id, result in outcomes.items()
        if record_id not in WITHOUT_EXECUTABLE_ASSERTIONS and result["carrier_result"] != "PASS"
    ]
    assert not failures, "\n".join(failures)
    unassessed = {record_id for record_id, result in outcomes.items() if result["carrier_result"] == "UNASSESSED"}
    assert unassessed == WITHOUT_EXECUTABLE_ASSERTIONS, unassessed ^ WITHOUT_EXECUTABLE_ASSERTIONS
