"""Spec-derived tests for ``gt backlog update`` and ``gt backlog resolve`` CLI commands.

Authority: bridge/gtkb-backlog-update-cli-slice-1-003.md (REVISED-1), Codex GO at
``bridge/gtkb-backlog-update-cli-slice-1-004.md``. Source work item: WI-3436.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from click.testing import CliRunner

from groundtruth_kb import cli_backlog_update as backlog_update
from groundtruth_kb.cli import main
from groundtruth_kb.db import KnowledgeDB

_TEST_SESSION_ID = "backlog-update-cli-test"


def _write_worker_document(project_dir: Path) -> None:
    path = project_dir / "harness-state" / "claude" / "session-envelopes" / f"{_TEST_SESSION_ID}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "status": "open",
                "session_id": _TEST_SESSION_ID,
                "harness_id": "B",
                "harness_name": "claude",
                "worker_role_provenance": {
                    "schema_version": 1,
                    "session_id": _TEST_SESSION_ID,
                    "harness_id": "B",
                    "harness_name": "claude",
                    "role": "prime-builder",
                    "role_resolution_source": "transcript_init_keyword",
                    "dispatch_run_id": None,
                    "issued_at": "2026-07-10T18:00:00Z",
                },
            }
        ),
        encoding="utf-8",
    )


@pytest.fixture(autouse=True)
def document_actor(project_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Provide only session-document evidence to mutating command tests."""
    _write_worker_document(project_dir)
    monkeypatch.setenv("GTKB_HARNESS_NAME", "claude")
    for name in (
        "GTKB_BRIDGE_POLLER_RUN_ID",
        "CLAUDE_CODE_SESSION_ID",
        "CLAUDE_SESSION_ID",
        "GTKB_INHERITED_SESSION_ID",
        "CODEX_SESSION_ID",
        "CODEX_THREAD_ID",
        "ANTIGRAVITY_SESSION_ID",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("GTKB_SESSION_ID", _TEST_SESSION_ID)


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


_REOPEN_BRIDGE_ID = "gtkb-wi5441-registry-control-plane-reverse-coverage"
_REOPEN_PAUTH_ID = "PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-REGISTRY-CONTROL-PLANE-20260724"
_REOPEN_THREADS = json.dumps(
    [
        f"bridge/{_REOPEN_BRIDGE_ID}-007.md",
        f"bridge/{_REOPEN_BRIDGE_ID}-008.md",
    ]
)
_REOPEN_REASON = f"WI-5441 owner-approved terminal repair under {_REOPEN_PAUTH_ID}"


def _seed_terminal_reopen(project_dir: Path) -> None:
    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        db.insert_project(
            id="PROJECT-GTKB-HOUSEKEEPING-HARDENING",
            name="Housekeeping hardening",
            status="active",
            changed_by="test",
            change_reason="seed project",
        )
        db.insert_deliberation(
            id="DELIB-WI5441-OWNER-REPAIR",
            source_type="owner_conversation",
            title="Owner-approved terminal repair",
            summary="Repair WI-5441 forward before WI-5640 resumes.",
            content="Owner approved the bounded repair.",
            changed_by="test",
            change_reason="seed decision",
        )
        db.insert_spec(
            id="GOV-PLATFORM-SOT-REGISTRY-001",
            title="Registry authority",
            status="verified",
            changed_by="test",
            change_reason="seed governing spec",
        )
        db.insert_work_item(
            id="WI-5441",
            title="Registry control plane",
            origin="defect",
            component="platform",
            resolution_status="open",
            changed_by="test",
            change_reason="seed false terminal state",
            stage="resolved",
            project_name="PROJECT-GTKB-HOUSEKEEPING-HARDENING",
        )
        db.insert_project_authorization(
            "PROJECT-GTKB-HOUSEKEEPING-HARDENING",
            "WI-5441 registry control plane",
            "DELIB-WI5441-OWNER-REPAIR",
            "Bounded terminal repair",
            "test",
            "seed authorization",
            id=_REOPEN_PAUTH_ID,
            status="active",
            included_work_item_ids=["WI-5441"],
            included_spec_ids=["GOV-PLATFORM-SOT-REGISTRY-001"],
        )
    finally:
        db.close()

    bridge = project_dir / "bridge"
    bridge.mkdir(exist_ok=True)
    statuses = ("NEW", "NO-GO", "REVISED", "NO-GO", "REVISED", "NO-GO", "REVISED", "GO")
    for version, status in enumerate(statuses, start=1):
        role = "prime-builder" if status in {"NEW", "REVISED"} else "loyal-opposition"
        lines = [
            status,
            "",
            f"author_identity: {role}/fixture-{version}",
            f"author_session_context_id: fixture-{role}-{version}",
            f"bridge_kind: {'prime_proposal' if role == 'prime-builder' else 'lo_verdict'}",
            f"Document: {_REOPEN_BRIDGE_ID}",
            f"Version: {version:03d}",
        ]
        if version > 1:
            lines.append(f"Responds to: bridge/{_REOPEN_BRIDGE_ID}-{version - 1:03d}.md")
        lines.extend(["Work Item: WI-5441", "", f"# Version {version}", ""])
        (bridge / f"{_REOPEN_BRIDGE_ID}-{version:03d}.md").write_text("\n".join(lines), encoding="utf-8")


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
    assert "--reopen-terminal" in result.output
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
    def _mock_resolve_changed_by(_project_root: Path) -> str:
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


def _reopen_args(project_dir: Path) -> list[str]:
    return [
        *_config_args(project_dir),
        "backlog",
        "update",
        "WI-5441",
        "--resolution-status",
        "open",
        "--stage",
        "backlogged",
        "--related-bridge-threads",
        _REOPEN_THREADS,
        "--owner-approved",
        "--reopen-terminal",
        "--change-reason",
        _REOPEN_REASON,
        "--json",
    ]


def test_backlog_update_reopen_terminal_appends_one_version_and_event(runner: CliRunner, project_dir: Path) -> None:
    _seed_terminal_reopen(project_dir)

    result = runner.invoke(main, _reopen_args(project_dir))

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["reopen_terminal"] is True
    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        row = db.get_work_item("WI-5441")
        assert row is not None
        assert row["version"] == 2
        assert row["stage"] == "backlogged"
        assert row["resolution_status"] == "open"
        assert len(db.get_work_item_history("WI-5441")) == 2
        assert (
            db._get_conn()
            .execute(
                "SELECT COUNT(*) FROM pipeline_events WHERE artifact_id = ? AND event_type = 'wi_reopened'",
                ("WI-5441",),
            )
            .fetchone()[0]
            == 1
        )
    finally:
        db.close()


def test_backlog_update_reopen_terminal_dry_run_writes_nothing(runner: CliRunner, project_dir: Path) -> None:
    _seed_terminal_reopen(project_dir)
    args = _reopen_args(project_dir)
    args.insert(-1, "--dry-run")

    result = runner.invoke(main, args)

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["dry_run"] is True
    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        assert len(db.get_work_item_history("WI-5441")) == 1
        assert (
            db._get_conn()
            .execute(
                "SELECT COUNT(*) FROM pipeline_events WHERE artifact_id = ? AND event_type = 'wi_reopened'",
                ("WI-5441",),
            )
            .fetchone()[0]
            == 0
        )
    finally:
        db.close()


@pytest.mark.parametrize(
    "removed_option",
    ["--owner-approved", "--reopen-terminal", "--related-bridge-threads", "--stage", "--resolution-status"],
)
def test_backlog_update_reopen_terminal_rejects_incomplete_requests_without_writes(
    runner: CliRunner, project_dir: Path, removed_option: str
) -> None:
    _seed_terminal_reopen(project_dir)
    args = _reopen_args(project_dir)
    index = args.index(removed_option)
    del args[index]
    if removed_option in {"--related-bridge-threads", "--stage", "--resolution-status"}:
        del args[index]

    result = runner.invoke(main, args)

    assert result.exit_code != 0
    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        assert len(db.get_work_item_history("WI-5441")) == 1
        assert (
            db._get_conn()
            .execute(
                "SELECT COUNT(*) FROM pipeline_events WHERE artifact_id = ? AND event_type = 'wi_reopened'",
                ("WI-5441",),
            )
            .fetchone()[0]
            == 0
        )
    finally:
        db.close()


_WI5640_BRIDGE_ID = "gtkb-file-move-rename-canonicalization-v4"
_WI5640_PAUTH_ID = "PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE"
_WI5640_THREAD_STATUS = {
    "bridge/gtkb-file-move-rename-canonicalization-008.md": "WITHDRAWN",
    "bridge/gtkb-file-move-rename-canonicalization-repair-forward-004.md": "NO-GO",
    "bridge/gtkb-file-move-rename-canonicalization-v2-006.md": "VERIFIED",
    "bridge/gtkb-file-move-rename-canonicalization-v3-006.md": "NO-GO",
    f"bridge/{_WI5640_BRIDGE_ID}-012.md": "GO",
    "bridge/gtkb-skill-rename-cursor-goose-parity-003.md": "WITHDRAWN",
    "bridge/gtkb-skill-rename-rollout-005.md": "WITHDRAWN",
    "bridge/gtkb-wi5640-scanner-fixture-placeholder-sweep-006.md": "VERIFIED",
}
_WI5640_THREADS = json.dumps(list(_WI5640_THREAD_STATUS))
_WI5640_REASON = f"WI-5640 owner-approved terminal repair under {_WI5640_PAUTH_ID}"


def _seed_wi5640_terminal_reopen(project_dir: Path) -> None:
    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        db.insert_project(
            id="PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY",
            name="Harness parity",
            status="active",
            changed_by="test",
            change_reason="seed project",
        )
        db.insert_deliberation(
            id="DELIB-WI5640-OWNER-REPAIR",
            source_type="owner_conversation",
            title="Owner-approved terminal repair",
            summary="Repair WI-5640 forward.",
            content="Owner approved the bounded repair.",
            changed_by="test",
            change_reason="seed decision",
        )
        db.insert_spec(
            id="GOV-PLATFORM-SOT-REGISTRY-001",
            title="Registry authority",
            status="verified",
            changed_by="test",
            change_reason="seed governing spec",
        )
        db.insert_work_item(
            id="WI-5640",
            title="File move canonicalization",
            origin="defect",
            component="platform",
            resolution_status="resolved",
            changed_by="test",
            change_reason="seed false terminal state",
            stage="resolved",
            project_name="PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY",
            priority="P0",
        )
        db.insert_project_authorization(
            "PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY",
            "WI-5640 file move canonicalization",
            "DELIB-WI5640-OWNER-REPAIR",
            "Bounded terminal repair",
            "test",
            "seed authorization",
            id=_WI5640_PAUTH_ID,
            status="active",
            included_work_item_ids=["WI-5640"],
            included_spec_ids=["GOV-PLATFORM-SOT-REGISTRY-001"],
        )
    finally:
        db.close()

    bridge = project_dir / "bridge"
    bridge.mkdir(exist_ok=True)
    files = dict(_WI5640_THREAD_STATUS)
    files[f"bridge/{_WI5640_BRIDGE_ID}-011.md"] = "REVISED"
    for rel_path, status in files.items():
        path = project_dir / rel_path
        slug, version = path.stem.rsplit("-", 1)
        role = "loyal-opposition" if status in {"GO", "NO-GO", "VERIFIED"} else "prime-builder"
        path.write_text(
            "\n".join(
                [
                    status,
                    "",
                    f"author_identity: {role}/fixture-{version}",
                    f"author_session_context_id: fixture-{slug}-{version}",
                    f"bridge_kind: {'lo_verdict' if role == 'loyal-opposition' else 'prime_proposal'}",
                    f"Document: {slug}",
                    f"Version: {version}",
                    "Work Item: WI-5640",
                    "",
                    f"# Version {version}",
                    "",
                ]
            ),
            encoding="utf-8",
        )


def _wi5640_reopen_args(project_dir: Path, *, dry_run: bool) -> list[str]:
    args = [
        *_config_args(project_dir),
        "backlog",
        "update",
        "WI-5640",
        "--resolution-status",
        "open",
        "--stage",
        "implementing",
        "--related-bridge-threads",
        _WI5640_THREADS,
        "--owner-approved",
        "--reopen-terminal",
        "--change-reason",
        _WI5640_REASON,
        "--json",
    ]
    if dry_run:
        args.insert(-1, "--dry-run")
    return args


def test_terminal_reopen_policy_bindings_are_explicit_and_narrow() -> None:
    wi5441 = backlog_update._TERMINAL_REOPEN_POLICIES["WI-5441"]
    assert wi5441.pauth_id == _REOPEN_PAUTH_ID
    assert wi5441.bridge_threads == {
        f"bridge/{_REOPEN_BRIDGE_ID}-007.md": (_REOPEN_BRIDGE_ID, "REVISED"),
        f"bridge/{_REOPEN_BRIDGE_ID}-008.md": (_REOPEN_BRIDGE_ID, "GO"),
    }
    assert wi5441.strict_bridge_threads == wi5441.bridge_threads
    assert wi5441.controlling_thread == f"bridge/{_REOPEN_BRIDGE_ID}-008.md"
    assert wi5441.exact_threads is False

    wi5640 = backlog_update._TERMINAL_REOPEN_POLICIES["WI-5640"]
    assert wi5640.pauth_id == _WI5640_PAUTH_ID
    assert set(wi5640.bridge_threads) == set(_WI5640_THREAD_STATUS)
    assert wi5640.strict_bridge_threads == {
        f"bridge/{_WI5640_BRIDGE_ID}-011.md": (_WI5640_BRIDGE_ID, "REVISED"),
        f"bridge/{_WI5640_BRIDGE_ID}-012.md": (_WI5640_BRIDGE_ID, "GO"),
    }
    assert wi5640.controlling_thread == f"bridge/{_WI5640_BRIDGE_ID}-012.md"
    assert wi5640.exact_threads is True
    assert set(backlog_update._TERMINAL_REOPEN_POLICIES) == {"WI-5441", "WI-5640"}


def test_wi5441_terminal_reopen_preserves_subset_semantics(runner: CliRunner, project_dir: Path) -> None:
    _seed_terminal_reopen(project_dir)
    extra = project_dir / "bridge" / "unrelated-001.md"
    extra.write_text("NEW\n", encoding="utf-8")
    args = _reopen_args(project_dir)
    index = args.index(_REOPEN_THREADS)
    args[index] = json.dumps([*json.loads(_REOPEN_THREADS), "bridge/unrelated-001.md"])
    args.insert(-1, "--dry-run")

    result = runner.invoke(main, args)

    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["dry_run"] is True


def test_terminal_reopen_rejects_unrelated_work_item(runner: CliRunner, project_dir: Path) -> None:
    _seed_terminal_reopen(project_dir)
    args = _reopen_args(project_dir)
    args[args.index("WI-5441")] = "WI-9999"

    result = runner.invoke(main, args)

    assert result.exit_code != 0
    assert "narrowly authorized only for WI-5441 or WI-5640" in result.output


def test_wi5640_terminal_reopen_uses_strict_v4_and_exact_reverse_index(
    runner: CliRunner,
    project_dir: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed_wi5640_terminal_reopen(project_dir)
    strict_versions = [
        SimpleNamespace(
            path=f"bridge/{_WI5640_BRIDGE_ID}-011.md",
            is_strict=True,
            status="REVISED",
            document=_WI5640_BRIDGE_ID,
        ),
        SimpleNamespace(
            path=f"bridge/{_WI5640_BRIDGE_ID}-012.md",
            is_strict=True,
            status="GO",
            document=_WI5640_BRIDGE_ID,
        ),
    ]
    calls: list[str] = []

    def fake_resolve(_root: Path, bridge_id: str) -> SimpleNamespace:
        calls.append(bridge_id)
        if bridge_id != _WI5640_BRIDGE_ID:
            raise AssertionError(f"historical evidence thread was resolved strictly: {bridge_id}")
        return SimpleNamespace(
            audit_versions=strict_versions,
            latest_strict_state=SimpleNamespace(path=f"bridge/{_WI5640_BRIDGE_ID}-012.md"),
        )

    monkeypatch.setattr(backlog_update, "resolve_bridge_lifecycle", fake_resolve)

    dry_run = runner.invoke(main, _wi5640_reopen_args(project_dir, dry_run=True))
    assert dry_run.exit_code == 0, dry_run.output
    assert json.loads(dry_run.output)["dry_run"] is True

    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        assert len(db.get_work_item_history("WI-5640")) == 1
    finally:
        db.close()

    applied = runner.invoke(main, _wi5640_reopen_args(project_dir, dry_run=False))
    assert applied.exit_code == 0, applied.output
    assert calls == [_WI5640_BRIDGE_ID, _WI5640_BRIDGE_ID]

    db = KnowledgeDB(db_path=project_dir / "groundtruth.db")
    try:
        row = db.get_work_item("WI-5640")
        assert row is not None
        assert row["version"] == 2
        assert row["resolution_status"] == "open"
        assert row["stage"] == "implementing"
        assert row["title"] == "File move canonicalization"
        assert row["priority"] == "P0"
        assert row["project_name"] == "PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY"
        related = row["related_bridge_threads"]
        assert set(json.loads(related) if isinstance(related, str) else related) == set(_WI5640_THREAD_STATUS)
        assert len(db.get_work_item_history("WI-5640")) == 2
        assert (
            db._get_conn()
            .execute(
                "SELECT COUNT(*) FROM pipeline_events WHERE artifact_id = ? AND event_type = 'wi_reopened'",
                ("WI-5640",),
            )
            .fetchone()[0]
            == 1
        )
    finally:
        db.close()
