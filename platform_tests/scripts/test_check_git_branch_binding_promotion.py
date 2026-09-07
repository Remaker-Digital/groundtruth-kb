"""Behavioral and decoy checks for the branch-binding semantic evaluator.

Coverage markers: DCL-GIT-BRANCH-BINDING-PROMOTION-001:positive and
DCL-GIT-BRANCH-BINDING-PROMOTION-001:negative.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
EVALUATOR_PATH = REPO_ROOT / "scripts" / "check_git_branch_binding_promotion.py"
POSITIVE_MARKER = "DCL-GIT-BRANCH-BINDING-PROMOTION-001:positive"
NEGATIVE_MARKER = "DCL-GIT-BRANCH-BINDING-PROMOTION-001:negative"


def _load_evaluator() -> ModuleType:
    spec = importlib.util.spec_from_file_location("branch_binding_under_test", EVALUATOR_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def evaluator() -> ModuleType:
    return _load_evaluator()


def _by_id(report: dict) -> dict[str, dict]:
    return {row["criterion_id"]: row for row in report["criteria"]}


def test_executes_supported_positive_and_negative_boundaries(evaluator: ModuleType, tmp_path: Path) -> None:
    report = evaluator.evaluate(tmp_path)
    rows = _by_id(report)
    for criterion_id in ("BRANCH-BIND-A2", "BRANCH-BIND-A4", "BRANCH-BIND-A8"):
        row = rows[criterion_id]
        assert row["outcome"] == evaluator.PASS
        assert {attempt["polarity"] for attempt in row["attempts"]} >= {"positive", "negative"}
        assert all(attempt["entrypoint"] for attempt in row["attempts"])
        assert all(attempt["observed_effects"] for attempt in row["attempts"])
    assert POSITIVE_MARKER and NEGATIVE_MARKER


def test_missing_terminal_boundaries_are_attempted_and_never_pass(evaluator: ModuleType, tmp_path: Path) -> None:
    rows = _by_id(evaluator.evaluate(tmp_path))
    for criterion_id in ("BRANCH-BIND-A1", "BRANCH-BIND-A5", "BRANCH-BIND-A7", "BRANCH-BIND-A9"):
        row = rows[criterion_id]
        assert row["outcome"] != evaluator.PASS
        assert row["attempts"]
        assert any(
            "unavailable" in attempt["reason"] or "incomplete" in attempt["reason"] for attempt in row["attempts"]
        )


def test_every_criterion_and_published_assertion_has_an_attempt(evaluator: ModuleType, tmp_path: Path) -> None:
    report = evaluator.evaluate(tmp_path)
    assert {row["criterion_id"] for row in report["criteria"]} == set(evaluator.CRITERIA)
    assert all(row["attempts"] for row in report["criteria"])
    supplemental = report["supplemental_assertions"]
    assert {row["assertion_id"] for row in supplemental} == {f"PUBLISHED-{index}" for index in range(1, 9)}
    assert all(row["outcome"] != evaluator.PASS for row in supplemental)
    assert all(row["entrypoint"] and row["observed_effects"] for row in supplemental)


def test_decoy_text_cannot_synthesize_pass(evaluator: ModuleType, tmp_path: Path) -> None:
    baseline = evaluator.evaluate(tmp_path / "baseline")
    decoy_root = tmp_path / "decoy"
    decoy_root.mkdir()
    (decoy_root / "decoys.py").write_text(
        '"""terminal_attribution promote zero_associated_controls --force"""\n'
        "if False:\n    publish_candidate_branch()\n",
        encoding="utf-8",
    )
    decoy = evaluator.evaluate(decoy_root)
    baseline_outcomes = {row["criterion_id"]: row["outcome"] for row in baseline["criteria"]}
    decoy_outcomes = {row["criterion_id"]: row["outcome"] for row in decoy["criteria"]}
    assert decoy_outcomes == baseline_outcomes


def test_evaluator_declares_complete_contract(evaluator: ModuleType) -> None:
    assert evaluator.EVALUATOR_ID == "git-branch-binding-promotion"
    assert set(evaluator.CRITERIA) == {f"BRANCH-BIND-A{index}" for index in range(1, 10)}
