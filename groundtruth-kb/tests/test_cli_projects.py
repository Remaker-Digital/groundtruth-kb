"""CLI tests for `gt projects authorize` spec-linkage gate (WI-3312).

Covers the cli.py wiring of GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001:
a ProjectAuthorizationSpecLinkageError raised by the service layer must be
surfaced to the user as a click.UsageError (exit code 2) citing the source
spec.

New test surface per bridge/gtkb-project-authorize-spec-linkage-gate-005.md
REVISED-2 (Codex GO at -006).
"""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from groundtruth_kb.cli import main
from groundtruth_kb.db import KnowledgeDB

PROJECT_ID = "PROJECT-CLI-AUTH-TEST"
DELIB_ID = "DELIB-CLI-AUTH-TEST"


def _prepare_db(db_path: Path) -> None:
    """Create a DB with a project and an owner-decision deliberation so that
    `projects authorize` reaches the spec-linkage validator."""
    db = KnowledgeDB(db_path=str(db_path))
    try:
        db.insert_project("CLI Auth Test Project", "test", "test setup", id=PROJECT_ID)
        db.insert_deliberation(
            id=DELIB_ID,
            source_type="owner_conversation",
            title="CLI auth test owner decision",
            summary="owner decision summary",
            content="owner decision content",
            changed_by="test",
            change_reason="test setup",
        )
    finally:
        db.close()


def _invoke_authorize_without_specs(tmp_path: Path, monkeypatch):
    """Run `gt projects authorize` with no --include-spec against a fresh DB."""
    _prepare_db(tmp_path / "groundtruth.db")
    monkeypatch.chdir(tmp_path)
    return CliRunner().invoke(
        main,
        [
            "projects", "authorize", PROJECT_ID,
            "--owner-decision", DELIB_ID,
            "--name", "CLI Auth Test Authorization",
            "--scope", "bounded test authorization scope",
            "--change-reason", "test authorization",
        ],
    )


def test_cli_authorize_missing_specs_emits_usage_error(tmp_path, monkeypatch) -> None:
    result = _invoke_authorize_without_specs(tmp_path, monkeypatch)
    # click.UsageError exits with code 2 -- distinct from click.ClickException's
    # exit code 1 -- confirming the typed ProjectAuthorizationSpecLinkageError
    # path, not the generic ProjectLifecycleError path.
    assert result.exit_code == 2, result.output


def test_cli_error_cites_source_spec(tmp_path, monkeypatch) -> None:
    result = _invoke_authorize_without_specs(tmp_path, monkeypatch)
    assert result.exit_code != 0
    assert "GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001" in result.output
