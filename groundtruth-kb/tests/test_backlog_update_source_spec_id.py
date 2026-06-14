"""Spec-derived tests for the ``gt backlog update --source-spec-id`` flag (WI-4521).

Authority: bridge/gtkb-wi4521-backlog-update-source-spec-id-001.md (NEW), Codex GO
at ``bridge/gtkb-wi4521-backlog-update-source-spec-id-002.md``. Source work item:
WI-4521. Project authorization:
``PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-2``.

The flag exposes the already-supported ``source_spec_id`` work-item field
(carried forward by ``db.update_work_item`` at db.py:4367) through the
``gt backlog update`` CLI surface, mirroring the ``gt backlog add`` precedent
(cli.py:2112). Coverage maps each WI-4521 acceptance criterion to one test:

- set/backfill (blank -> value)         : ``test_update_sets_source_spec_id``,
                                          ``test_backfill_blank_source_spec_id``
- correction (existing -> new value)    : ``test_correct_existing_source_spec_id``
- no-flag carry-forward preserved       : ``test_no_flag_preserves_source_spec_id``
- dry-run reports the would-be update   : ``test_dry_run_reports_source_spec_id``
- other gates unaffected (text-edit,    : ``test_text_edit_gate_unchanged_with_source_spec_id``,
  GOV-15)                                 ``test_gov15_gate_unchanged_with_source_spec_id``
- help surface lists the flag           : ``test_update_help_lists_source_spec_id``
"""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from groundtruth_kb.cli import main
from groundtruth_kb.db import KnowledgeDB


def _seed_work_item(
    project_dir: Path,
    *,
    work_item_id: str,
    origin: str = "improvement",
    source_spec_id: str | None = None,
) -> None:
    """Seed a single work item with an explicit ``source_spec_id`` value."""
    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        db.insert_work_item(
            id=work_item_id,
            title=f"{work_item_id} title",
            origin=origin,
            component="platform",
            resolution_status="open",
            changed_by="test",
            change_reason="seed work item",
            stage="created",
            priority="P3",
            source_spec_id=source_spec_id,
        )
    finally:
        db.close()


def _config_args(project_dir: Path) -> list[str]:
    return ["--config", str(project_dir / "groundtruth.toml")]


def test_update_help_lists_source_spec_id(runner: CliRunner, project_dir: Path) -> None:
    """The new flag is discoverable on ``gt backlog update --help``."""
    result = runner.invoke(main, [*_config_args(project_dir), "backlog", "update", "--help"])
    assert result.exit_code == 0
    assert "--source-spec-id" in result.output


def test_update_sets_source_spec_id(runner: CliRunner, project_dir: Path) -> None:
    """WI-4521 root: ``--source-spec-id`` is accepted and persisted on update."""
    _seed_work_item(project_dir, work_item_id="WI-SET", source_spec_id=None)

    result = runner.invoke(
        main,
        [
            *_config_args(project_dir),
            "backlog",
            "update",
            "WI-SET",
            "--source-spec-id",
            "GOV-FOO-001",
            "--change-reason",
            "set source spec id",
        ],
    )
    assert result.exit_code == 0
    assert "Updated work item WI-SET." in result.output

    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        latest = db.get_work_item("WI-SET")
        assert latest is not None
        assert latest["source_spec_id"] == "GOV-FOO-001"
    finally:
        db.close()


def test_backfill_blank_source_spec_id(runner: CliRunner, project_dir: Path) -> None:
    """WI-4517 (b) use case: backfill a blank ``source_spec_id`` to a value."""
    _seed_work_item(project_dir, work_item_id="WI-BACKFILL", source_spec_id=None)

    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        seeded = db.get_work_item("WI-BACKFILL")
        assert seeded is not None
        assert seeded["source_spec_id"] is None
    finally:
        db.close()

    result = runner.invoke(
        main,
        [
            *_config_args(project_dir),
            "backlog",
            "update",
            "WI-BACKFILL",
            "--source-spec-id",
            "GOV-CODE-QUALITY-BASELINE-001",
            "--change-reason",
            "backfill source spec id",
        ],
    )
    assert result.exit_code == 0

    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        latest = db.get_work_item("WI-BACKFILL")
        assert latest is not None
        assert latest["source_spec_id"] == "GOV-CODE-QUALITY-BASELINE-001"
    finally:
        db.close()


def test_correct_existing_source_spec_id(runner: CliRunner, project_dir: Path) -> None:
    """Correction: an existing ``source_spec_id`` is overwritten with the new value."""
    _seed_work_item(project_dir, work_item_id="WI-CORRECT", source_spec_id="GOV-OLD-001")

    result = runner.invoke(
        main,
        [
            *_config_args(project_dir),
            "backlog",
            "update",
            "WI-CORRECT",
            "--source-spec-id",
            "GOV-NEW-001",
            "--change-reason",
            "correct source spec id",
        ],
    )
    assert result.exit_code == 0

    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        latest = db.get_work_item("WI-CORRECT")
        assert latest is not None
        assert latest["source_spec_id"] == "GOV-NEW-001"
    finally:
        db.close()


def test_no_flag_preserves_source_spec_id(runner: CliRunner, project_dir: Path) -> None:
    """Carry-forward preserved: updating another field WITHOUT the flag keeps the value."""
    _seed_work_item(project_dir, work_item_id="WI-PRESERVE", source_spec_id="GOV-KEEP-001")

    result = runner.invoke(
        main,
        [
            *_config_args(project_dir),
            "backlog",
            "update",
            "WI-PRESERVE",
            "--priority",
            "P1",
            "--change-reason",
            "update priority only",
        ],
    )
    assert result.exit_code == 0

    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        latest = db.get_work_item("WI-PRESERVE")
        assert latest is not None
        assert latest["priority"] == "P1"
        assert latest["source_spec_id"] == "GOV-KEEP-001"
    finally:
        db.close()


def test_dry_run_reports_source_spec_id(runner: CliRunner, project_dir: Path) -> None:
    """``--dry-run`` reports the would-be ``source_spec_id`` and writes no new version."""
    _seed_work_item(project_dir, work_item_id="WI-DRYRUN", source_spec_id=None)

    result = runner.invoke(
        main,
        [
            *_config_args(project_dir),
            "backlog",
            "update",
            "WI-DRYRUN",
            "--source-spec-id",
            "GOV-DRY-001",
            "--change-reason",
            "dry run source spec id",
            "--dry-run",
            "--json",
        ],
    )
    assert result.exit_code == 0
    assert "source_spec_id" in result.output
    assert "GOV-DRY-001" in result.output

    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        history = db.get_work_item_history("WI-DRYRUN")
        assert len(history) == 1  # no new version written
        assert history[0]["source_spec_id"] is None
    finally:
        db.close()


def test_text_edit_gate_unchanged_with_source_spec_id(runner: CliRunner, project_dir: Path) -> None:
    """The text-edit gate still fires for ``--title`` even when ``--source-spec-id`` is also passed.

    The new flag must not become a bypass: combining it with ``--title`` on a
    work item lacking text-edit authorization (no bridge_authorized state, no
    ``--owner-approved``, no PAUTH/DELIB token in the reason) must still fail
    closed, and no new version may be written.
    """
    _seed_work_item(project_dir, work_item_id="WI-TEXTGATE", source_spec_id=None)

    result = runner.invoke(
        main,
        [
            *_config_args(project_dir),
            "backlog",
            "update",
            "WI-TEXTGATE",
            "--source-spec-id",
            "GOV-BAR-001",
            "--title",
            "Rewritten title",
            "--change-reason",
            "attempt title edit without authorization",
        ],
    )
    assert result.exit_code != 0
    assert "without text-edit authorization" in result.output

    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        history = db.get_work_item_history("WI-TEXTGATE")
        assert len(history) == 1  # gate fired before any write
        assert history[0]["title"] == "WI-TEXTGATE title"
        assert history[0]["source_spec_id"] is None
    finally:
        db.close()


def test_gov15_gate_unchanged_with_source_spec_id(runner: CliRunner, project_dir: Path) -> None:
    """GOV-15 still fires for a defect terminal transition even with ``--source-spec-id``.

    Resolving a defect work item without ``--owner-approved`` must fail closed
    under GOV-15 regardless of whether ``--source-spec-id`` is supplied; no new
    version may be written.
    """
    _seed_work_item(
        project_dir,
        work_item_id="WI-GOV15",
        origin="defect",
        source_spec_id=None,
    )

    result = runner.invoke(
        main,
        [
            *_config_args(project_dir),
            "backlog",
            "update",
            "WI-GOV15",
            "--resolution-status",
            "resolved",
            "--source-spec-id",
            "GOV-BAZ-001",
            "--change-reason",
            "attempt resolve without owner approval",
        ],
    )
    assert result.exit_code != 0
    assert "without explicit owner approval" in result.output

    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        latest = db.get_work_item("WI-GOV15")
        assert latest is not None
        assert latest["resolution_status"] == "open"  # unchanged
        assert latest["source_spec_id"] is None  # unchanged
    finally:
        db.close()
