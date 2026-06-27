"""Spec-derived tests for ``gt backlog update`` and ``gt backlog resolve`` CLI commands.

Authority: bridge/gtkb-backlog-update-cli-slice-1-003.md (REVISED-1), Codex GO at
``bridge/gtkb-backlog-update-cli-slice-1-004.md``. Source work item: WI-3436.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from groundtruth_kb.cli import main
from groundtruth_kb.db import KnowledgeDB


def _seed_db(project_dir: Path) -> None:
    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        db.insert_project(
            id="PROJECT-TEST",
            name="Test Project",
            status="active",
            changed_by="test",
            change_reason="seed project",
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
    finally:
        db.close()


def _config_args(project_dir: Path) -> list[str]:
    return ["--config", str(project_dir / "groundtruth.toml")]


def test_backlog_update_help(runner: CliRunner, project_dir: Path) -> None:
    """T1: gt backlog update --help lists expected options."""
    result = runner.invoke(main, [*_config_args(project_dir), "backlog", "update", "--help"])
    assert result.exit_code == 0
    assert "--resolution-status" in result.output
    assert "--stage" in result.output
    assert "--owner-approved" in result.output
    assert "--change-reason" in result.output
    assert "--dry-run" in result.output
    assert "--json" in result.output


def test_backlog_resolve_help(runner: CliRunner, project_dir: Path) -> None:
    """T2: gt backlog resolve --help lists resolve convenience usage."""
    result = runner.invoke(main, [*_config_args(project_dir), "backlog", "resolve", "--help"])
    assert result.exit_code == 0
    assert "Resolve a work item" in result.output
    assert "--owner-approved" in result.output
    assert "--change-reason" in result.output


def test_backlog_update_writes_new_version(runner: CliRunner, project_dir: Path) -> None:
    """T3: Update writes an append-only new version."""
    _seed_db(project_dir)

    result = runner.invoke(
        main,
        [
            *_config_args(project_dir),
            "backlog",
            "update",
            "WI-IMPROVEMENT",
            "--resolution-status",
            "in_progress",
            "--change-reason",
            "update progress",
        ],
    )
    assert result.exit_code == 0
    assert "Updated work item WI-IMPROVEMENT." in result.output

    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        history = db.get_work_item_history("WI-IMPROVEMENT")
        assert len(history) == 2
        # Verify append-only versioning is correct
        assert history[0]["version"] == 2
        assert history[0]["resolution_status"] == "in_progress"
        assert history[0]["change_reason"] == "update progress"

        assert history[1]["version"] == 1
        assert history[1]["resolution_status"] == "open"
    finally:
        db.close()


def test_backlog_update_unsupplied_fields_carry_forward(runner: CliRunner, project_dir: Path) -> None:
    """T4: Unsupplied fields carry forward from previous version."""
    _seed_db(project_dir)

    result = runner.invoke(
        main,
        [
            *_config_args(project_dir),
            "backlog",
            "update",
            "WI-IMPROVEMENT",
            "--priority",
            "P1",
            "--change-reason",
            "update priority",
        ],
    )
    assert result.exit_code == 0

    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        latest = db.get_work_item("WI-IMPROVEMENT")
        assert latest is not None
        assert latest["priority"] == "P1"
        assert latest["title"] == "Improvement work item"
        assert latest["resolution_status"] == "open"
    finally:
        db.close()


def test_backlog_update_related_bridge_threads(runner: CliRunner, project_dir: Path) -> None:
    """T5: related_bridge_threads is updatable."""
    _seed_db(project_dir)
    threads_json = '["bridge/example-001.md"]'

    result = runner.invoke(
        main,
        [
            *_config_args(project_dir),
            "backlog",
            "update",
            "WI-IMPROVEMENT",
            "--related-bridge-threads",
            threads_json,
            "--change-reason",
            "update bridge threads",
        ],
    )
    assert result.exit_code == 0

    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        latest = db.get_work_item("WI-IMPROVEMENT")
        assert latest is not None
        assert latest["related_bridge_threads"] == threads_json
    finally:
        db.close()


@pytest.mark.parametrize(
    "bad_value",
    [
        "[bridge/example-001.md,bridge/example-002.md]",
        '{"not": "an array"}',
        '"bridge/example-001.md"',
    ],
)
def test_backlog_update_rejects_malformed_related_bridge_threads(
    runner: CliRunner,
    project_dir: Path,
    bad_value: str,
) -> None:
    _seed_db(project_dir)

    result = runner.invoke(
        main,
        [
            *_config_args(project_dir),
            "backlog",
            "update",
            "WI-IMPROVEMENT",
            "--related-bridge-threads",
            bad_value,
            "--change-reason",
            "try malformed bridge threads",
        ],
    )
    assert result.exit_code != 0
    assert "--related-bridge-threads" in result.output
    assert "expected a JSON array of strings" in result.output

    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        latest = db.get_work_item("WI-IMPROVEMENT")
        assert latest is not None
        assert latest["related_bridge_threads"] is None
        assert len(db.get_work_item_history("WI-IMPROVEMENT")) == 1
    finally:
        db.close()


def test_backlog_resolve_preserves_valid_related_bridge_threads(runner: CliRunner, project_dir: Path) -> None:
    _seed_db(project_dir)
    threads_json = '["bridge/example-001.md","bridge/example-002.md"]'

    result = runner.invoke(
        main,
        [
            *_config_args(project_dir),
            "backlog",
            "resolve",
            "WI-IMPROVEMENT",
            "--related-bridge-threads",
            threads_json,
            "--change-reason",
            "resolve with bridge evidence",
        ],
    )
    assert result.exit_code == 0
    assert "Resolved work item WI-IMPROVEMENT." in result.output

    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        latest = db.get_work_item("WI-IMPROVEMENT")
        assert latest is not None
        assert latest["resolution_status"] == "resolved"
        assert latest["stage"] == "resolved"
        assert latest["related_bridge_threads"] == threads_json
    finally:
        db.close()


def test_backlog_resolve_rejects_malformed_related_bridge_threads(runner: CliRunner, project_dir: Path) -> None:
    _seed_db(project_dir)

    result = runner.invoke(
        main,
        [
            *_config_args(project_dir),
            "backlog",
            "resolve",
            "WI-IMPROVEMENT",
            "--related-bridge-threads",
            '"bridge/example-001.md"',
            "--change-reason",
            "try malformed bridge evidence",
        ],
    )
    assert result.exit_code != 0
    assert "--related-bridge-threads" in result.output
    assert "expected a JSON array of strings" in result.output

    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        latest = db.get_work_item("WI-IMPROVEMENT")
        assert latest is not None
        assert latest["resolution_status"] == "open"
        assert latest["stage"] == "created"
        assert latest["related_bridge_threads"] is None
    finally:
        db.close()


def test_backlog_update_gov15_status_only_bypass_closed(runner: CliRunner, project_dir: Path) -> None:
    """T6a: GOV-15 status-only bypass CLOSED (negative test)."""
    _seed_db(project_dir)

    result = runner.invoke(
        main,
        [
            *_config_args(project_dir),
            "backlog",
            "update",
            "WI-DEFECT",
            "--resolution-status",
            "resolved",
            "--change-reason",
            "try bypass",
        ],
    )
    # Must fail closed with non-zero exit code
    assert result.exit_code != 0
    assert "without explicit owner approval" in result.output

    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        latest = db.get_work_item("WI-DEFECT")
        assert latest is not None
        assert latest["resolution_status"] == "open"  # resolution status must not change
    finally:
        db.close()


def test_backlog_update_gov15_owner_approved_positive(runner: CliRunner, project_dir: Path) -> None:
    """T6b: GOV-15 positive: owner-approved coherent terminal state."""
    _seed_db(project_dir)

    result = runner.invoke(
        main,
        [
            *_config_args(project_dir),
            "backlog",
            "resolve",
            "WI-DEFECT",
            "--owner-approved",
            "--change-reason",
            "owner approved resolution",
        ],
    )
    assert result.exit_code == 0
    assert "Resolved work item WI-DEFECT." in result.output

    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        latest = db.get_work_item("WI-DEFECT")
        assert latest is not None
        assert latest["resolution_status"] == "resolved"
        assert latest["stage"] == "resolved"
    finally:
        db.close()


def test_backlog_update_gov15_not_overapplied_to_improvement(runner: CliRunner, project_dir: Path) -> None:
    """T6c: GOV-15 not over-applied to non-defect work items."""
    _seed_db(project_dir)

    result = runner.invoke(
        main,
        [
            *_config_args(project_dir),
            "backlog",
            "resolve",
            "WI-IMPROVEMENT",
            "--change-reason",
            "resolve improvement",
        ],
    )
    assert result.exit_code == 0
    assert "Resolved work item WI-IMPROVEMENT." in result.output

    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        latest = db.get_work_item("WI-IMPROVEMENT")
        assert latest is not None
        assert latest["resolution_status"] == "resolved"
    finally:
        db.close()


def test_backlog_update_fail_closed_attribution(
    runner: CliRunner,
    project_dir: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """T7: Fail-closed attribution: non-zero exit and no writes when unresolvable."""
    _seed_db(project_dir)

    from groundtruth_kb import cli_backlog_update

    # Mock attribution resolver to raise RuntimeError
    def _mock_resolve_changed_by() -> str:
        raise RuntimeError("No harness resolved")

    monkeypatch.setattr(cli_backlog_update, "_resolve_changed_by", _mock_resolve_changed_by)

    result = runner.invoke(
        main,
        [
            *_config_args(project_dir),
            "backlog",
            "update",
            "WI-IMPROVEMENT",
            "--priority",
            "P1",
            "--change-reason",
            "test attribution",
        ],
    )
    assert result.exit_code != 0
    assert "No harness resolved" in result.output

    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        latest = db.get_work_item("WI-IMPROVEMENT")
        assert latest is not None
        assert latest["priority"] == "P3"  # must not have updated
    finally:
        db.close()


def test_backlog_update_dry_run(runner: CliRunner, project_dir: Path) -> None:
    """T8: --dry-run reports changes but does not write to database."""
    _seed_db(project_dir)

    result = runner.invoke(
        main,
        [
            *_config_args(project_dir),
            "backlog",
            "update",
            "WI-IMPROVEMENT",
            "--priority",
            "P1",
            "--change-reason",
            "dry run update",
            "--dry-run",
        ],
    )
    assert result.exit_code == 0
    assert "Would update work item WI-IMPROVEMENT." in result.output

    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        history = db.get_work_item_history("WI-IMPROVEMENT")
        assert len(history) == 1  # no new version created
        assert history[0]["priority"] == "P3"
    finally:
        db.close()


def test_backlog_update_invalid_stage_transition(runner: CliRunner, project_dir: Path) -> None:
    """T9: Invalid stage transition is rejected."""
    _seed_db(project_dir)

    result = runner.invoke(
        main,
        [
            *_config_args(project_dir),
            "backlog",
            "update",
            "WI-IMPROVEMENT",
            "--stage",
            "implementing",  # Invalid from 'created' per transitions dictionary
            "--change-reason",
            "invalid transition",
        ],
    )
    assert result.exit_code != 0
    assert "Invalid stage transition" in result.output


def test_update_description_file_with_embedded_quotes(runner: CliRunner, project_dir: Path) -> None:
    """WI-4727 / GOV-STANDING-BACKLOG-001: --description-file sets a description
    containing embedded double-quotes correctly. The file content never transits
    argv, so PowerShell native-exe arg-split cannot corrupt the embedded quotes."""
    _seed_db(project_dir)
    description_text = 'Realign the "foo" widget and the "bar" gadget per owner note.'
    desc_path = project_dir / "wi4727_desc.txt"
    desc_path.write_text(description_text, encoding="utf-8")

    result = runner.invoke(
        main,
        [
            *_config_args(project_dir),
            "backlog",
            "update",
            "WI-IMPROVEMENT",
            "--description-file",
            str(desc_path),
            "--owner-approved",
            "--change-reason",
            "set description from file (WI-4727)",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "Updated work item WI-IMPROVEMENT." in result.output

    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        latest = db.get_work_item("WI-IMPROVEMENT")
        assert latest is not None
        assert latest["description"] == description_text
    finally:
        db.close()


def test_update_description_inline_still_works(runner: CliRunner, project_dir: Path) -> None:
    """WI-4727 / GOV-STANDING-BACKLOG-001: the existing --description TEXT path is
    unchanged (backward compatibility)."""
    _seed_db(project_dir)
    description_text = "Inline description unchanged by the new option."

    result = runner.invoke(
        main,
        [
            *_config_args(project_dir),
            "backlog",
            "update",
            "WI-IMPROVEMENT",
            "--description",
            description_text,
            "--owner-approved",
            "--change-reason",
            "set description inline",
        ],
    )
    assert result.exit_code == 0, result.output

    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        latest = db.get_work_item("WI-IMPROVEMENT")
        assert latest is not None
        assert latest["description"] == description_text
    finally:
        db.close()


def test_update_description_and_file_mutually_exclusive(runner: CliRunner, project_dir: Path) -> None:
    """DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001: supplying both
    --description and --description-file is a usage error (no traceback) and writes
    nothing."""
    _seed_db(project_dir)
    desc_path = project_dir / "wi4727_both.txt"
    desc_path.write_text("file content", encoding="utf-8")

    result = runner.invoke(
        main,
        [
            *_config_args(project_dir),
            "backlog",
            "update",
            "WI-IMPROVEMENT",
            "--description",
            "inline content",
            "--description-file",
            str(desc_path),
            "--owner-approved",
            "--change-reason",
            "both inputs supplied",
        ],
    )
    assert result.exit_code != 0
    assert "Cannot specify both --description and --description-file" in result.output
    assert "Traceback" not in result.output

    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        assert len(db.get_work_item_history("WI-IMPROVEMENT")) == 1
    finally:
        db.close()


def test_update_description_file_missing_path_errors(runner: CliRunner, project_dir: Path) -> None:
    """DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001: a missing --description-file
    path is rejected by Click's exists=True validation with a clear usage error and
    no traceback, writing nothing."""
    _seed_db(project_dir)
    missing_path = project_dir / "wi4727_missing.txt"

    result = runner.invoke(
        main,
        [
            *_config_args(project_dir),
            "backlog",
            "update",
            "WI-IMPROVEMENT",
            "--description-file",
            str(missing_path),
            "--owner-approved",
            "--change-reason",
            "missing description file",
        ],
    )
    assert result.exit_code != 0
    assert "--description-file" in result.output
    assert "does not exist" in result.output
    assert "Traceback" not in result.output

    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        assert len(db.get_work_item_history("WI-IMPROVEMENT")) == 1
    finally:
        db.close()
