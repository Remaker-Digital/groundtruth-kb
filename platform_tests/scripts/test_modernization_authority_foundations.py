"""Frozen objective acceptance tests for modernization Authority Foundations."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_SRC = REPO_ROOT / "groundtruth-kb" / "src"
EVALUATOR_PATH = REPO_ROOT / "scripts" / "check_artifact_evaluability.py"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402

AUTHORITY_CARRIERS = (
    "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
    "ADR-EXPLICIT-HINT-CONTEXT-MANAGEMENT-001",
    "DCL-ACTIVITY-CONTEXT-MANIFEST-001",
    "GOV-SOURCE-OF-TRUTH-FRESHNESS-001",
    "GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001",
    "GOV-SESSION-ROLE-AUTHORITY-001",
    "DCL-SESSION-ROLE-RESOLUTION-001",
    "DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001",
)
NONAUTHORITATIVE_SOURCE_PREFIXES = (".gtkb-state/", "bridge/", "memory/")


@pytest.fixture(scope="module")
def evaluator():
    spec = importlib.util.spec_from_file_location("modernization_authority_evaluator", EVALUATOR_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def authority_specs() -> dict[str, dict]:
    db = KnowledgeDB(REPO_ROOT / "groundtruth.db")
    try:
        result = {spec_id: db.get_spec(spec_id) for spec_id in AUTHORITY_CARRIERS}
    finally:
        db.close()
    missing = [spec_id for spec_id, spec in result.items() if spec is None]
    assert not missing, "Missing frozen authority carriers: " + ", ".join(missing)
    return result


def test_frozen_authority_carriers_are_current_stated_and_uniquely_asserted(authority_specs):
    problems: list[str] = []
    for spec_id, spec in authority_specs.items():
        assert spec is not None
        if spec.get("status") not in {"specified", "implemented", "verified"}:
            problems.append(f"{spec_id}: non-current status {spec.get('status')!r}")
        if spec.get("authority") != "stated":
            problems.append(f"{spec_id}: authority is {spec.get('authority')!r}, expected 'stated'")
        assertions = spec.get("_assertions_parsed") or []
        assertion_ids = [item.get("id") for item in assertions if isinstance(item, dict)]
        if not assertion_ids or any(not assertion_id for assertion_id in assertion_ids):
            problems.append(f"{spec_id}: every outer assertion requires an id")
        if len(assertion_ids) != len(set(assertion_ids)):
            problems.append(f"{spec_id}: duplicate outer assertion ids")
    assert not problems, "\n".join(problems)


def test_authority_enforcement_sources_are_live_root_bound_files(authority_specs):
    problems: list[str] = []
    for spec_id, spec in authority_specs.items():
        assert spec is not None
        source_paths = spec.get("_source_paths_parsed") or []
        if not source_paths:
            problems.append(f"{spec_id}: no enforcement source paths")
            continue
        for raw_path in source_paths:
            path = Path(raw_path)
            normalized = path.as_posix()
            if path.is_absolute() or ".." in path.parts:
                problems.append(f"{spec_id}: source escapes project root: {raw_path}")
            elif normalized.startswith(NONAUTHORITATIVE_SOURCE_PREFIXES):
                problems.append(f"{spec_id}: source is historical/non-authoritative: {raw_path}")
            elif not (REPO_ROOT / path).is_file():
                problems.append(f"{spec_id}: source file is missing: {raw_path}")
    assert not problems, "\n".join(problems)


def test_every_frozen_authority_carrier_is_fully_evaluable(evaluator, authority_specs):
    failures: list[str] = []
    for spec_id, spec in authority_specs.items():
        assert spec is not None
        result = evaluator.evaluate_spec(spec, project_root=REPO_ROOT)
        if result["carrier_result"] != "PASS":
            failures.append(f"{spec_id}: {result['carrier_result']} ({result['evaluation_reason']})")
    assert not failures, "\n".join(failures)
