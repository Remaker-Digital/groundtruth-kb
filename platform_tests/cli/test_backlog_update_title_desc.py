"""Spec-derived tests for ``gt backlog update --title/--description`` (WI-4357).

Authority: bridge/gtkb-backlog-update-title-desc-cli-001-003.md (REVISED-1),
Codex GO at bridge/gtkb-backlog-update-title-desc-cli-001-004.md. Source work
item: WI-4357. Owner decisions: DELIB-20260870 (design), DELIB-20260871 (PAUTH
strategy). PAUTH: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-BACKLOG-UPDATE-TITLE-DESC-CLI-WI-4357.

Each test seeds a fresh project with a deliberation row that backs a PAUTH
authorization, a defect WI (for GOV-15 composition), and an improvement WI
with bridge_authorized approval_state. The CLI is invoked via Click's
``CliRunner`` against the in-tree ``gt`` entry point.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.cli import main  # noqa: E402
from groundtruth_kb.db import KnowledgeDB  # noqa: E402

SEED_DELIB_ID = "DELIB-WI4357-TEST-DESIGN"
SEED_PAUTH_ID = "PAUTH-PROJECT-TEST-BACKLOG-TEXT-EDIT-WI-IMPROVEMENT"


@pytest.fixture(autouse=True)
def set_harness_name(monkeypatch) -> None:
    """Ensure a deterministic active prime builder is resolved by default in these tests."""
    monkeypatch.setenv("GTKB_HARNESS_NAME", "antigravity")


def _project(tmp_path: Path) -> tuple[Path, Path]:
    """Create a project directory with groundtruth.toml + seeded db."""
    root = tmp_path / "project"
    root.mkdir()
    config = root / "groundtruth.toml"
    config.write_text(
        '[groundtruth]\ndb_path = "./groundtruth.db"\nproject_root = "."\n',
        encoding="utf-8",
    )

    db = KnowledgeDB(db_path=root / "groundtruth.db")
    try:
        db.insert_project(
            id="PROJECT-TEST",
            name="Test Project",
            status="active",
            changed_by="test",
            change_reason="seed project",
        )
        # GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001: active PAUTH must
        # cite at least one specified+ spec. Seed a trivial requirement so
        # the seeded PAUTH below is acceptable.
        db.insert_spec(
            id="SPEC-WI4357-TEST-SEED",
            title="Test seed requirement for WI-4357 disjunctive-gate tests",
            status="specified",
            changed_by="test",
            change_reason="seed spec",
        )
        db.insert_deliberation(
            id=SEED_DELIB_ID,
            source_type="owner_conversation",
            title="Owner-approved test design",
            summary="Owner approved seeded design for WI-4357 tests.",
            content="Owner-decision content for WI-4357 disjunctive-gate tests.",
            changed_by="test",
            change_reason="seed deliberation",
            outcome="owner_decision",
        )
        db.insert_project_authorization(
            project_id="PROJECT-TEST",
            authorization_name="Backlog text-edit authorization",
            owner_decision_deliberation_id=SEED_DELIB_ID,
            scope_summary="Authorize text edits to WI-IMPROVEMENT for tests.",
            changed_by="test",
            change_reason="seed authorization",
            id=SEED_PAUTH_ID,
            status="active",
            allowed_mutation_classes=["cli_extension", "source", "test_addition"],
            included_work_item_ids=["WI-IMPROVEMENT", "WI-DEFECT"],
            included_spec_ids=["SPEC-WI4357-TEST-SEED"],
        )
        db.insert_work_item(
            id="WI-DEFECT",
            title="Defect work item",
            origin="defect",
            component="platform",
            resolution_status="open",
            changed_by="test",
            change_reason="seed defect",
            stage="created",
            project_name="PROJECT-TEST",
            priority="P3",
        )
        db.insert_work_item(
            id="WI-IMPROVEMENT",
            title="Improvement work item",
            origin="improvement",
            component="platform",
            resolution_status="open",
            changed_by="test",
            change_reason="seed improvement",
            stage="created",
            project_name="PROJECT-TEST",
            priority="P3",
        )
        # WI seeded at stage='tested' so T8 can exercise a non-terminal
        # transition ('tested' -> 'backlogged') that does not trip GOV-12 or
        # the backlog-snapshot guard.
        db.insert_work_item(
            id="WI-TESTED",
            title="Tested-stage work item",
            origin="improvement",
            component="platform",
            resolution_status="open",
            changed_by="test",
            change_reason="seed tested-stage",
            stage="tested",
            project_name="PROJECT-TEST",
            priority="P3",
        )
        db.insert_work_item(
            id="WI-BRIDGE",
            title="Bridge-authorized work item",
            origin="improvement",
            component="platform",
            resolution_status="open",
            changed_by="test",
            change_reason="seed bridge_authorized",
            stage="created",
            approval_state="bridge_authorized",
            project_name="PROJECT-TEST",
            priority="P3",
        )
    finally:
        db.close()

    return root, config


def _config_args(config: Path) -> list[str]:
    return ["--config", str(config)]


def _current_title(db_path: Path, wi_id: str) -> str:
    with sqlite3.connect(db_path) as conn:
        row = conn.execute("SELECT title FROM current_work_items WHERE id = ?", (wi_id,)).fetchone()
    assert row is not None, f"WI {wi_id} missing"
    return str(row[0])


def _current_description(db_path: Path, wi_id: str) -> str | None:
    with sqlite3.connect(db_path) as conn:
        row = conn.execute("SELECT description FROM current_work_items WHERE id = ?", (wi_id,)).fetchone()
    assert row is not None
    return None if row[0] is None else str(row[0])


def _version_count(db_path: Path, wi_id: str) -> int:
    with sqlite3.connect(db_path) as conn:
        row = conn.execute("SELECT COUNT(*) FROM work_items WHERE id = ?", (wi_id,)).fetchone()
    return int(row[0])


# ---------------------------------------------------------------------------
# T1: Gate rejects when no evidence arm is satisfied.
# Spec: GOV-STANDING-BACKLOG-001 + GOV-15 (disjunctive gate enforcement).
# ---------------------------------------------------------------------------
def test_gate_rejects_without_evidence(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    result = CliRunner().invoke(
        main,
        [
            *_config_args(config),
            "backlog",
            "update",
            "WI-IMPROVEMENT",
            "--title",
            "Improved title",
            "--change-reason",
            "ordinary edit without any authorization token",
        ],
    )
    assert result.exit_code != 0, result.output
    assert "without text-edit authorization" in result.output
    # Verify no new version was persisted.
    assert _version_count(root / "groundtruth.db", "WI-IMPROVEMENT") == 1
    assert _current_title(root / "groundtruth.db", "WI-IMPROVEMENT") == "Improvement work item"


# ---------------------------------------------------------------------------
# T2: --owner-approved admits a title edit (arm 2).
# Spec: GOV-STANDING-BACKLOG-001 (owner-approved disjunctive arm).
# ---------------------------------------------------------------------------
def test_owner_approved_admits_title_edit(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    result = CliRunner().invoke(
        main,
        [
            *_config_args(config),
            "backlog",
            "update",
            "WI-IMPROVEMENT",
            "--title",
            "Owner-approved new title",
            "--owner-approved",
            "--change-reason",
            "owner-approved title edit",
        ],
    )
    assert result.exit_code == 0, result.output
    assert _current_title(root / "groundtruth.db", "WI-IMPROVEMENT") == "Owner-approved new title"
    assert _version_count(root / "groundtruth.db", "WI-IMPROVEMENT") == 2


# ---------------------------------------------------------------------------
# T3: PAUTH citation in --change-reason admits a description edit (arm 3a).
# Spec: GOV-STANDING-BACKLOG-001 + GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001.
# ---------------------------------------------------------------------------
def test_pauth_citation_admits_description_edit(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    result = CliRunner().invoke(
        main,
        [
            *_config_args(config),
            "backlog",
            "update",
            "WI-IMPROVEMENT",
            "--description",
            "New description authorized by PAUTH",
            "--change-reason",
            f"text edit under {SEED_PAUTH_ID}",
        ],
    )
    assert result.exit_code == 0, result.output
    assert _current_description(root / "groundtruth.db", "WI-IMPROVEMENT") == "New description authorized by PAUTH"


# ---------------------------------------------------------------------------
# T4: DELIB citation in --change-reason admits a title edit (arm 3b positive).
# Spec: GOV-STANDING-BACKLOG-001 + Deliberation Archive citation.
# ---------------------------------------------------------------------------
def test_delib_citation_admits_text_edit(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    result = CliRunner().invoke(
        main,
        [
            *_config_args(config),
            "backlog",
            "update",
            "WI-IMPROVEMENT",
            "--title",
            "Title authorized by DELIB",
            "--change-reason",
            f"text edit under owner decision {SEED_DELIB_ID}",
        ],
    )
    assert result.exit_code == 0, result.output
    assert _current_title(root / "groundtruth.db", "WI-IMPROVEMENT") == "Title authorized by DELIB"


# ---------------------------------------------------------------------------
# T5: NEGATIVE — nonexistent DELIB-shaped token does NOT satisfy the gate.
# Spec: Residual-Risk mitigation (Codex GO -004): real DB existence lookup.
# ---------------------------------------------------------------------------
def test_nonexistent_delib_citation_rejected(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    result = CliRunner().invoke(
        main,
        [
            *_config_args(config),
            "backlog",
            "update",
            "WI-IMPROVEMENT",
            "--title",
            "Attempt to bypass gate",
            "--change-reason",
            "text edit citing DELIB-99999999 which does not exist in the DB",
        ],
    )
    assert result.exit_code != 0, result.output
    assert "without text-edit authorization" in result.output
    assert _version_count(root / "groundtruth.db", "WI-IMPROVEMENT") == 1


# ---------------------------------------------------------------------------
# T6: bridge_authorized approval_state admits a text edit (arm 1).
# Spec: GOV-STANDING-BACKLOG-001 (approval_state disjunctive arm).
# ---------------------------------------------------------------------------
def test_bridge_authorized_admits_text_edit(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    result = CliRunner().invoke(
        main,
        [
            *_config_args(config),
            "backlog",
            "update",
            "WI-BRIDGE",
            "--title",
            "Edit under bridge_authorized state",
            "--change-reason",
            "text edit; approval_state arm satisfied",
        ],
    )
    assert result.exit_code == 0, result.output
    assert _current_title(root / "groundtruth.db", "WI-BRIDGE") == "Edit under bridge_authorized state"


# ---------------------------------------------------------------------------
# T7: Mixed --title + terminal --resolution-status: BOTH gates required.
# Spec: GOV-15 + GOV-STANDING-BACKLOG-001 (gate composition).
# ---------------------------------------------------------------------------
def test_mixed_title_and_resolution_status_requires_both_gates(tmp_path: Path) -> None:
    root, config = _project(tmp_path)

    # Without --owner-approved, GOV-15 blocks the defect → resolved transition
    # even though the text-edit gate could be satisfied via the PAUTH arm.
    result_no_owner = CliRunner().invoke(
        main,
        [
            *_config_args(config),
            "backlog",
            "update",
            "WI-DEFECT",
            "--title",
            "Resolved with new title",
            "--resolution-status",
            "resolved",
            "--change-reason",
            f"defect resolution under {SEED_PAUTH_ID}",
        ],
    )
    assert result_no_owner.exit_code != 0, result_no_owner.output
    assert "GOV-15" in result_no_owner.output
    assert _version_count(root / "groundtruth.db", "WI-DEFECT") == 1

    # With --owner-approved + non-empty change_reason, both gates pass.
    result_ok = CliRunner().invoke(
        main,
        [
            *_config_args(config),
            "backlog",
            "update",
            "WI-DEFECT",
            "--title",
            "Resolved with new title",
            "--resolution-status",
            "resolved",
            "--owner-approved",
            "--change-reason",
            "defect resolution with owner approval",
        ],
    )
    assert result_ok.exit_code == 0, result_ok.output
    assert _current_title(root / "groundtruth.db", "WI-DEFECT") == "Resolved with new title"


# ---------------------------------------------------------------------------
# T8: Mixed --title + non-terminal --stage: only text-edit gate applies.
# Spec: gate composition (text edits + non-terminal stage transitions).
# ---------------------------------------------------------------------------
def test_mixed_title_and_non_terminal_stage_text_gate_only(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    # Also include WI-TESTED in the PAUTH scope by extending the seeded
    # authorization implicitly: WI-TESTED is project-scoped via
    # PROJECT-TEST membership, and the gate's PAUTH arm matches when the
    # cited PAUTH is active. Even if the PAUTH did not include this WI,
    # the gate cares only about active-status existence of the cited token.
    result = CliRunner().invoke(
        main,
        [
            *_config_args(config),
            "backlog",
            "update",
            "WI-TESTED",
            "--title",
            "Title with stage advance",
            "--stage",
            "backlogged",
            "--change-reason",
            f"text edit and non-terminal stage transition under {SEED_PAUTH_ID}",
        ],
    )
    assert result.exit_code == 0, result.output
    assert _current_title(root / "groundtruth.db", "WI-TESTED") == "Title with stage advance"


# ---------------------------------------------------------------------------
# T9: --dry-run validates and reports the would-be edit without writing.
# Spec: DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (dry-run discipline).
# ---------------------------------------------------------------------------
def test_dry_run_validates_and_reports_no_write(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    result = CliRunner().invoke(
        main,
        [
            *_config_args(config),
            "backlog",
            "update",
            "WI-IMPROVEMENT",
            "--title",
            "Dry-run title proposal",
            "--owner-approved",
            "--change-reason",
            "dry-run preview",
            "--dry-run",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["dry_run"] is True
    assert payload["updated"] is False
    assert payload["fields"]["title"] == "Dry-run title proposal"
    # Verify no new version was persisted.
    assert _version_count(root / "groundtruth.db", "WI-IMPROVEMENT") == 1
    assert _current_title(root / "groundtruth.db", "WI-IMPROVEMENT") == "Improvement work item"


# ---------------------------------------------------------------------------
# T10: Empty --change-reason combined with --title rejected before the gate.
# Spec: DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 (change_reason
# validation precedes the disjunctive gate).
# ---------------------------------------------------------------------------
def test_empty_change_reason_rejected_with_title_edit(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    result = CliRunner().invoke(
        main,
        [
            *_config_args(config),
            "backlog",
            "update",
            "WI-IMPROVEMENT",
            "--title",
            "Title with empty reason",
            "--owner-approved",
            "--change-reason",
            "   ",
        ],
    )
    assert result.exit_code != 0, result.output
    assert "change-reason" in result.output
    assert _version_count(root / "groundtruth.db", "WI-IMPROVEMENT") == 1
