"""Executed semantic tests for GOV-WORK-ITEM-TERMINAL-STATE-001."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
EVALUATOR_PATH = REPO_ROOT / "scripts" / "check_work_item_terminal_resolver.py"

# Specification-declared matrix markers.
CASE_SINGLETON = "terminal_work_item_ids_singleton_positive"
CASE_PUBLICATION_ORDER = "publication_before_observation_positive"
CASE_SESSION_INDEPENDENCE = "pb_lo_session_independence_positive"
CASE_NON_GITHUB = "non_github_rejection_negative"
CASE_METADATA_MISMATCH = "terminal_metadata_mismatch_matrix_negative"
CASE_ZERO_CONTROLS = "zero_associated_controls_positive"


def _load_evaluator() -> ModuleType:
    spec = importlib.util.spec_from_file_location("wi_terminal_under_test", EVALUATOR_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def evaluator() -> ModuleType:
    return _load_evaluator()


def _rows(report: dict) -> dict[str, dict]:
    return {row["criterion_id"]: row for row in report["criteria"]}


def test_exact_and_changed_snapshots_execute_through_publication(evaluator: ModuleType, tmp_path: Path) -> None:
    row = _rows(evaluator.evaluate(tmp_path))["WI-TERM-A2"]
    assert row["outcome"] == evaluator.PASS
    assert {attempt["polarity"] for attempt in row["attempts"]} == {"positive", "negative"}
    assert any("candidate_ref_created" in attempt["observed_effects"] for attempt in row["attempts"])
    assert any("denial=source_tree_mismatch" in attempt["observed_effects"] for attempt in row["attempts"])
    assert CASE_PUBLICATION_ORDER and CASE_NON_GITHUB


def test_binding_executes_but_attribution_gap_is_honest(evaluator: ModuleType, tmp_path: Path) -> None:
    row = _rows(evaluator.evaluate(tmp_path))["WI-TERM-A4"]
    assert row["outcome"] == evaluator.PARTIAL
    assert any("binding_valid" in attempt["observed_effects"] for attempt in row["attempts"])
    assert any("record_terminal_attribution" in attempt["entrypoint"] for attempt in row["attempts"])
    assert CASE_SESSION_INDEPENDENCE


def test_every_terminal_criterion_attempts_its_production_boundary(evaluator: ModuleType, tmp_path: Path) -> None:
    report = evaluator.evaluate(tmp_path)
    rows = _rows(report)
    assert set(rows) == set(evaluator.CRITERIA)
    assert all(row["attempts"] for row in rows.values())
    for criterion_id in (
        "WI-TERM-A1",
        "WI-TERM-A3",
        "WI-TERM-A5",
        "WI-TERM-A6",
        "WI-TERM-A7",
        "WI-TERM-A8",
        "WI-TERM-A9",
        "WI-TERM-A10",
        "WI-TERM-A11",
        "WI-TERM-A12",
    ):
        assert rows[criterion_id]["outcome"] != evaluator.PASS
        assert rows[criterion_id]["attempts"][0]["entrypoint"].startswith("GitLifecycleService.")
    assert CASE_SINGLETON and CASE_METADATA_MISMATCH and CASE_ZERO_CONTROLS


def test_decoys_and_split_carriers_cannot_create_terminal_evidence(evaluator: ModuleType, tmp_path: Path) -> None:
    baseline = evaluator.evaluate(tmp_path / "baseline")
    decoy_root = tmp_path / "decoy"
    decoy_root.mkdir()
    (decoy_root / "decoys.py").write_text(
        '"""terminal_work_item_ids = ["WI-1"] zero_associated_controls"""\n'
        'BODY = "Terminal work item ID: WI-1"\n'
        "if False:\n    emit_verified_notification()\n",
        encoding="utf-8",
    )
    decoy = evaluator.evaluate(decoy_root)
    assert [row["outcome"] for row in decoy["criteria"]] == [row["outcome"] for row in baseline["criteria"]]


def test_no_behavioral_pass_lacks_a_negative_fixture(evaluator: ModuleType, tmp_path: Path) -> None:
    report = evaluator.evaluate(tmp_path)
    for row in report["criteria"]:
        if row["outcome"] == evaluator.PASS:
            polarities = {attempt["polarity"] for attempt in row["attempts"]}
            assert {"positive", "negative"} <= polarities


def test_evaluator_declares_complete_contract(evaluator: ModuleType) -> None:
    assert evaluator.EVALUATOR_ID == "work-item-terminal-state-and-metadata"
    assert set(evaluator.CRITERIA) == {f"WI-TERM-A{index}" for index in range(1, 13)}
