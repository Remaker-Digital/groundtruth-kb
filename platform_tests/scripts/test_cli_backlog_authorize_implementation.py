"""Tests for the retired ``gt backlog authorize-implementation`` mutation path.

The command remains help-discoverable, but every operational invocation must
fail before owner-decision capture, project-authorization mutation, or dry-run
postimage construction. Project-scoped authorization uses ``gt projects
authorize`` instead.

Authority: WI-6066 and the independently approved source-bearing proposal
``gtkb-wi6066-retire-per-wi-authorize-implementation``.

Every test runs against a temporary ``groundtruth.db`` created from a temp
``groundtruth.toml``; no test mutates the production ``groundtruth.db``.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

from click.testing import CliRunner

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.cli import main  # noqa: E402
from groundtruth_kb.db import KnowledgeDB  # noqa: E402

_SEED_BY = "prime-builder/claude"
_PROJECT_ID = "PROJECT-TEST"
_WI_ID = "WI-TEST-1"
_SPEC_ID = "SPEC-TEST-1"
_OWNER_DELIB = "DELIB-OWNER-1"
_RETIRED_MESSAGE = "Per-work-item implementation authorization is retired"
_RECOVERY_COMMAND = "gt projects authorize"


def _project(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Create a temp project; return (root, config, db_path)."""
    root = tmp_path / "project"
    root.mkdir()
    db_path = root / "groundtruth.db"
    config = root / "groundtruth.toml"
    config.write_text(
        f'[groundtruth]\ndb_path = "{db_path.as_posix()}"\nproject_root = "{root.as_posix()}"\n',
        encoding="utf-8",
    )
    return root, config, db_path


def _seed_common(db_path: Path, *, with_membership: bool = True, extra_projects: tuple[str, ...] = ()) -> None:
    """Seed a project, a work item, an active membership, and an approved spec."""
    db = KnowledgeDB(db_path=db_path)
    db.insert_project(_PROJECT_ID, _SEED_BY, "seed project", id=_PROJECT_ID)
    for pid in extra_projects:
        db.insert_project(pid, _SEED_BY, "seed extra project", id=pid)
    db.insert_work_item(
        id=_WI_ID,
        title="Owner-selected work item",
        origin="improvement",
        component="cli",
        resolution_status="open",
        changed_by=_SEED_BY,
        change_reason="seed work item",
        stage="backlogged",
    )
    db.insert_spec(
        id=_SPEC_ID,
        title="Governing specification",
        status="specified",
        changed_by=_SEED_BY,
        change_reason="seed spec",
    )
    if with_membership:
        db.link_project_work_item(_PROJECT_ID, _WI_ID, _SEED_BY, "seed membership", status="active")
    for pid in extra_projects:
        db.link_project_work_item(pid, _WI_ID, _SEED_BY, "seed extra membership", status="active")
    db.close()


def _seed_owner_deliberation(db_path: Path) -> None:
    db = KnowledgeDB(db_path=db_path)
    db.insert_deliberation(
        id=_OWNER_DELIB,
        source_type="owner_conversation",
        title="Owner authorization decision",
        summary="Owner approved implementing the work item.",
        content="Owner approved this work item for implementation.",
        changed_by=_SEED_BY,
        change_reason="seed owner deliberation",
        outcome="owner_decision",
        work_item_id=_WI_ID,
    )
    db.close()


def _auth_rows(db_path: Path) -> list[sqlite3.Row]:
    if not db_path.exists():
        return []
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        return list(conn.execute("SELECT * FROM current_project_authorizations").fetchall())


def _delib_count(db_path: Path) -> int:
    with sqlite3.connect(db_path) as conn:
        return int(conn.execute("SELECT COUNT(*) FROM current_deliberations").fetchone()[0])


def _args(config: Path, *extra: str) -> list[str]:
    return ["--config", str(config), "backlog", "authorize-implementation", *extra]


def test_t1_command_registered_with_options(tmp_path: Path) -> None:
    _, config, _ = _project(tmp_path)
    result = CliRunner().invoke(main, _args(config, "--help"))
    assert result.exit_code == 0, result.output
    for option in (
        "--owner-decision",
        "--auq-id",
        "--include-spec",
        "--allowed-mutation",
        "--project",
        "--dry-run",
        "--json",
    ):
        assert option in result.output, f"missing {option} in help"


def _assert_retired_without_mutation(db_path: Path, result: object, *, delib_before: int) -> None:
    assert result.exit_code != 0
    assert _RETIRED_MESSAGE in result.output
    assert _RECOVERY_COMMAND in result.output
    assert _auth_rows(db_path) == []
    assert _delib_count(db_path) == delib_before
    assert "proposed_authorization" not in result.output
    assert "included_work_item_ids" not in result.output


def test_t2_existing_owner_decision_shape_is_retired_without_mutation(tmp_path: Path) -> None:
    _, config, db_path = _project(tmp_path)
    _seed_common(db_path)
    _seed_owner_deliberation(db_path)
    delib_before = _delib_count(db_path)
    result = CliRunner().invoke(
        main,
        _args(
            config,
            _WI_ID,
            "--owner-decision",
            _OWNER_DELIB,
            "--include-spec",
            _SPEC_ID,
            "--allowed-mutation",
            "source",
            "--change-reason",
            "retired existing-decision invocation",
            "--json",
        ),
    )
    _assert_retired_without_mutation(db_path, result, delib_before=delib_before)


def test_t3_fresh_auq_shape_is_retired_before_deliberation_write(tmp_path: Path) -> None:
    root, config, db_path = _project(tmp_path)
    _seed_common(db_path)
    content_file = root / "owner-decision.md"
    content_file.write_text("Owner approved this work item via AUQ.\n", encoding="utf-8")
    delib_before = _delib_count(db_path)
    result = CliRunner().invoke(
        main,
        _args(
            config,
            _WI_ID,
            "--auq-id",
            "AUQ-S999-1",
            "--auq-answer",
            "Yes, authorize it",
            "--decision-content-file",
            str(content_file),
            "--include-spec",
            _SPEC_ID,
            "--allowed-mutation",
            "source",
            "--change-reason",
            "retired fresh-AUQ invocation",
            "--json",
        ),
    )
    _assert_retired_without_mutation(db_path, result, delib_before=delib_before)


def test_t4_dry_run_is_retired_without_one_wi_postimage(tmp_path: Path) -> None:
    _, config, db_path = _project(tmp_path)
    _seed_common(db_path)
    _seed_owner_deliberation(db_path)
    delib_before = _delib_count(db_path)
    result = CliRunner().invoke(
        main,
        _args(
            config,
            _WI_ID,
            "--owner-decision",
            _OWNER_DELIB,
            "--include-spec",
            _SPEC_ID,
            "--allowed-mutation",
            "source",
            "--change-reason",
            "retired dry-run invocation",
            "--dry-run",
            "--json",
        ),
    )
    _assert_retired_without_mutation(db_path, result, delib_before=delib_before)


def test_t5_retirement_precedes_database_access(tmp_path: Path) -> None:
    _, config, db_path = _project(tmp_path)
    result = CliRunner().invoke(
        main,
        _args(
            config,
            "WI-DOES-NOT-EXIST",
            "--owner-decision",
            "DELIB-DOES-NOT-EXIST",
            "--include-spec",
            "SPEC-DOES-NOT-EXIST",
            "--allowed-mutation",
            "source",
            "--change-reason",
            "prove unconditional retirement",
        ),
    )
    assert result.exit_code != 0
    assert _RETIRED_MESSAGE in result.output
    assert _RECOVERY_COMMAND in result.output
    assert not db_path.exists()
