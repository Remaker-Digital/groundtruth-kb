"""Tests for objective modernization non-impairment evidence."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "check_modernization_nonimpairment.py"


@pytest.fixture
def checker():
    spec = importlib.util.spec_from_file_location("check_modernization_nonimpairment", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _passing_evidence() -> dict:
    return {
        "canonical_authority": "DCL-EXAMPLE-001",
        "primary_read_route": "gt example show",
        "primary_mutation_route": "gt example update",
        "measurements": [
            {"id": "latency", "baseline": 5, "result": 4, "direction": "lower_or_equal"},
            {"id": "coverage", "baseline": 10, "result": 10, "direction": "higher_or_equal"},
        ],
        "rollback": {"instructions": "restore prior config", "tested": True, "evidence": "TEST-ROLLBACK"},
        "hard_invariants": [{"id": "INV-1", "status": "PASS", "evidence": "TEST-INV-1"}],
        "worker_loading_paths": ["rules/current.md"],
        "superseded_guidance": [{"path": "archive/old.md", "disposition": "quarantined"}],
    }


def test_complete_nonimpairing_evidence_passes(checker):
    report = checker.evaluate_evidence(_passing_evidence())

    assert report["status"] == "PASS"
    assert report["activation_allowed"] is True
    assert report["blocked_gates"] == []


def test_regressed_measurement_blocks_activation(checker):
    evidence = _passing_evidence()
    evidence["measurements"][0]["result"] = 6

    report = checker.evaluate_evidence(evidence)

    assert report["status"] == "FAIL"
    assert any(item["id"] == "latency" for item in report["findings"])


def test_missing_hard_invariant_blocks_verification_promotion_and_closure(checker):
    evidence = _passing_evidence()
    evidence["hard_invariants"] = []

    report = checker.evaluate_evidence(evidence)

    assert any(item["severity"] == "P0" and item["id"] == "hard-invariant" for item in report["findings"])
    assert report["blocked_gates"] == ["implementation", "verification", "promotion", "closure"]


def test_untested_rollback_blocks_activation(checker):
    evidence = _passing_evidence()
    evidence["rollback"]["tested"] = False

    report = checker.evaluate_evidence(evidence)

    assert any(item["id"] == "rollback" for item in report["findings"])


def test_superseded_guidance_on_worker_loading_path_is_p0(checker):
    evidence = _passing_evidence()
    evidence["superseded_guidance"] = [{"path": "rules/current.md", "disposition": "superseded"}]

    report = checker.evaluate_evidence(evidence)

    assert any(item["id"] == "rules/current.md" and item["severity"] == "P0" for item in report["findings"])


@pytest.mark.parametrize("field", ["canonical_authority", "primary_read_route", "primary_mutation_route"])
def test_missing_canonical_route_blocks_activation(checker, field):
    evidence = _passing_evidence()
    evidence.pop(field)

    report = checker.evaluate_evidence(evidence)

    assert any(item["id"] == field for item in report["findings"])
