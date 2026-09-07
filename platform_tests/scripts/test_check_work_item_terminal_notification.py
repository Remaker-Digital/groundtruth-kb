"""Executed semantic tests for DCL-BRIDGE-CLAIM-LIFECYCLE-001.

Coverage markers: DCL-BRIDGE-CLAIM-LIFECYCLE-001:positive and
DCL-BRIDGE-CLAIM-LIFECYCLE-001:negative.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
EVALUATOR_PATH = REPO_ROOT / "scripts" / "check_work_item_terminal_notification.py"
POSITIVE_MARKER = "DCL-BRIDGE-CLAIM-LIFECYCLE-001:positive"
NEGATIVE_MARKER = "DCL-BRIDGE-CLAIM-LIFECYCLE-001:negative"


def _load_evaluator() -> ModuleType:
    spec = importlib.util.spec_from_file_location("terminal_notification_under_test", EVALUATOR_PATH)
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


def test_exact_and_modified_snapshots_execute(evaluator: ModuleType, tmp_path: Path) -> None:
    row = _rows(evaluator.evaluate(tmp_path))["CLAIM-LC-1"]
    assert row["outcome"] == evaluator.PASS
    assert {attempt["polarity"] for attempt in row["attempts"]} == {"positive", "negative"}
    assert any("source_tree_mismatch" in str(attempt["observed_effects"]) for attempt in row["attempts"])
    assert POSITIVE_MARKER and NEGATIVE_MARKER


def test_real_claim_acquire_release_and_foreign_fence_execute(evaluator: ModuleType, tmp_path: Path) -> None:
    row = _rows(evaluator.evaluate(tmp_path))["CLAIM-LC-4"]
    effects = [effect for attempt in row["attempts"] for effect in attempt["observed_effects"]]
    assert row["outcome"] == evaluator.PARTIAL
    assert "holder=semantic-session" in effects
    assert "remaining=None" in effects
    assert all(attempt["outcome"] == evaluator.PASS for attempt in row["attempts"])


def test_timing_input_is_observed_without_claiming_policy_authority(evaluator: ModuleType, tmp_path: Path) -> None:
    row = _rows(evaluator.evaluate(tmp_path))["CLAIM-LC-8"]
    assert row["outcome"] == evaluator.PARTIAL
    assert any("observed_ttl_seconds=73" in attempt["observed_effects"] for attempt in row["attempts"])
    assert any("registered_claim_timing_policy" in attempt["entrypoint"] for attempt in row["attempts"])


def test_all_nine_required_assertions_have_attempt_ledgers(evaluator: ModuleType, tmp_path: Path) -> None:
    rows = _rows(evaluator.evaluate(tmp_path))
    assert set(rows) == {f"CLAIM-LC-{index}" for index in range(1, 10)}
    assert all(row["attempts"] for row in rows.values())
    for row in rows.values():
        assert all(attempt["entrypoint"] and attempt["observed_effects"] for attempt in row["attempts"])


def test_decoy_order_and_notification_tokens_cannot_synthesize_pass(evaluator: ModuleType, tmp_path: Path) -> None:
    baseline = evaluator.evaluate(tmp_path / "baseline")
    decoy_root = tmp_path / "decoy"
    decoy_root.mkdir()
    (decoy_root / "decoy.py").write_text(
        '"""commit release zero_associated_controls write_bridge_file"""\n'
        "if False:\n    write_bridge_file()\n    commit()\n",
        encoding="utf-8",
    )
    decoy = evaluator.evaluate(decoy_root)
    assert [row["outcome"] for row in decoy["criteria"]] == [row["outcome"] for row in baseline["criteria"]]


def test_evaluator_declares_complete_contract(evaluator: ModuleType) -> None:
    assert evaluator.EVALUATOR_ID == "post-commit-notification-coordination-release"
    assert set(evaluator.CRITERIA) == {f"CLAIM-LC-{index}" for index in range(1, 10)}
