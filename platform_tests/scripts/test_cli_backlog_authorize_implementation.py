"""Tests for the governed ``gt backlog authorize-implementation`` CLI service.

Authority: bridge/gtkb-backlog-authorize-implementation-cli-slice-1-003.md
(REVISED), Codex GO at
``bridge/gtkb-backlog-authorize-implementation-cli-slice-1-004.md``.
Source work item: WI-3494. Owner decision: DELIB-2547.

Covers the spec-derived verification plan T1-T12: command registration, the
create path from an existing owner-authority deliberation, the fresh-AUQ
record path, fail-closed behavior without owner evidence, required spec
linkage, project auto-resolution and ambiguity guards, the no-gate-bypass
property, ``--dry-run`` no-mutation, the owner-authority predicate (NO-GO -002
F2), and the mutually-exclusive authority-input guard.

Every test runs against a temporary ``groundtruth.db`` created from a temp
``groundtruth.toml``; no test mutates the production ``groundtruth.db``.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import json
import re
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
_NONOWNER_DELIB = "DELIB-NONOWNER-1"


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


def _seed_nonowner_deliberation(db_path: Path) -> None:
    db = KnowledgeDB(db_path=db_path)
    db.insert_deliberation(
        id=_NONOWNER_DELIB,
        source_type="lo_review",
        title="Loyal Opposition review note",
        summary="A review record, not owner authority.",
        content="This is an LO review, not an owner decision.",
        changed_by=_SEED_BY,
        change_reason="seed non-owner deliberation",
        outcome="informational",
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


# ---------------------------------------------------------------------------
# T1 - command exists + is registered with the documented options
# ---------------------------------------------------------------------------


def test_t1_command_registered_with_options(tmp_path: Path) -> None:
    root, config, _ = _project(tmp_path)
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


# ---------------------------------------------------------------------------
# T2 - create path from an existing owner-authority deliberation
# ---------------------------------------------------------------------------


def test_t2_create_from_existing_owner_deliberation(tmp_path: Path) -> None:
    root, config, db_path = _project(tmp_path)
    _seed_common(db_path)
    _seed_owner_deliberation(db_path)
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
            "cli_extension",
            "--change-reason",
            "authorize WI for implementation",
            "--json",
        ),
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["created"] is True
    assert payload["owner_decision"] == _OWNER_DELIB
    assert payload["project_id"] == _PROJECT_ID
    rows = _auth_rows(db_path)
    assert len(rows) == 1
    row = rows[0]
    assert json.loads(row["included_work_item_ids"]) == [_WI_ID]
    assert row["owner_decision_deliberation_id"] == _OWNER_DELIB
    assert row["status"] == "active"
    assert json.loads(row["allowed_mutation_classes"]) == ["cli_extension"]


# ---------------------------------------------------------------------------
# T3 - fresh-AUQ path records an owner deliberation and cites it
# ---------------------------------------------------------------------------


def test_t3_fresh_auq_records_deliberation_and_cites_it(tmp_path: Path) -> None:
    root, config, db_path = _project(tmp_path)
    _seed_common(db_path)
    delib_before = _delib_count(db_path)
    content_file = root / "owner-decision.md"
    content_file.write_text("Owner approved this work item via AUQ.\n", encoding="utf-8")
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
            "cli_extension",
            "--change-reason",
            "authorize via fresh AUQ",
            "--json",
        ),
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["created"] is True
    assert _delib_count(db_path) == delib_before + 1
    new_delib_id = payload["owner_decision"]
    rows = _auth_rows(db_path)
    assert len(rows) == 1
    assert rows[0]["owner_decision_deliberation_id"] == new_delib_id
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        delib = conn.execute(
            "SELECT source_type, outcome FROM current_deliberations WHERE id = ?", (new_delib_id,)
        ).fetchone()
    assert delib["source_type"] == "owner_conversation"
    assert delib["outcome"] == "owner_decision"


# ---------------------------------------------------------------------------
# T4 - refuses (fail closed) when no owner-decision evidence is supplied
# ---------------------------------------------------------------------------


def test_t4_refuses_without_owner_evidence(tmp_path: Path) -> None:
    root, config, db_path = _project(tmp_path)
    _seed_common(db_path)
    result = CliRunner().invoke(
        main,
        _args(
            config,
            _WI_ID,
            "--include-spec",
            _SPEC_ID,
            "--allowed-mutation",
            "cli_extension",
            "--change-reason",
            "no owner evidence",
        ),
    )
    assert result.exit_code != 0
    assert _auth_rows(db_path) == []


# ---------------------------------------------------------------------------
# T5 - requires at least one --include-spec (fail closed)
# ---------------------------------------------------------------------------


def test_t5_requires_include_spec(tmp_path: Path) -> None:
    root, config, db_path = _project(tmp_path)
    _seed_common(db_path)
    _seed_owner_deliberation(db_path)
    result = CliRunner().invoke(
        main,
        _args(
            config,
            _WI_ID,
            "--owner-decision",
            _OWNER_DELIB,
            "--allowed-mutation",
            "cli_extension",
            "--change-reason",
            "no spec linkage",
        ),
    )
    assert result.exit_code != 0
    assert _auth_rows(db_path) == []


# ---------------------------------------------------------------------------
# T6 - project auto-resolution and ambiguity guards
# ---------------------------------------------------------------------------


def test_t6a_resolves_sole_membership(tmp_path: Path) -> None:
    root, config, db_path = _project(tmp_path)
    _seed_common(db_path)
    _seed_owner_deliberation(db_path)
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
            "cli_extension",
            "--change-reason",
            "auto-resolve project",
            "--json",
        ),
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["project_id"] == _PROJECT_ID


def test_t6b_zero_membership_errors(tmp_path: Path) -> None:
    root, config, db_path = _project(tmp_path)
    _seed_common(db_path, with_membership=False)
    _seed_owner_deliberation(db_path)
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
            "cli_extension",
            "--change-reason",
            "no membership",
        ),
    )
    assert result.exit_code != 0
    assert _auth_rows(db_path) == []


def test_t6c_multiple_membership_requires_project(tmp_path: Path) -> None:
    root, config, db_path = _project(tmp_path)
    _seed_common(db_path, extra_projects=("PROJECT-TEST-2",))
    _seed_owner_deliberation(db_path)
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
            "cli_extension",
            "--change-reason",
            "ambiguous membership",
        ),
    )
    assert result.exit_code != 0
    assert _auth_rows(db_path) == []


# ---------------------------------------------------------------------------
# T7 - the produced authorization is a normal envelope; no gate is bypassed
# ---------------------------------------------------------------------------


def test_t7_no_gate_bypass(tmp_path: Path) -> None:
    root, config, db_path = _project(tmp_path)
    _seed_common(db_path)
    _seed_owner_deliberation(db_path)
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
            "cli_extension",
            "--change-reason",
            "normal envelope",
            "--json",
        ),
    )
    assert result.exit_code == 0, result.output
    row = _auth_rows(db_path)[0]
    # A standard project-authorization envelope row -- no special bypass column.
    assert row["status"] == "active"
    assert row["owner_decision_deliberation_id"] == _OWNER_DELIB
    # The implementation module imports no gate module (it cannot weaken gates).
    import groundtruth_kb.cli_backlog_authorize_implementation as module

    source = Path(module.__file__).read_text(encoding="utf-8")
    gate_imports = re.findall(r"^\s*(?:from|import)\s+\S*gate\S*", source, re.MULTILINE)
    assert gate_imports == [], f"unexpected gate import(s): {gate_imports}"


# ---------------------------------------------------------------------------
# T8 - --dry-run resolves + validates but writes nothing
# ---------------------------------------------------------------------------


def test_t8_dry_run_writes_nothing(tmp_path: Path) -> None:
    root, config, db_path = _project(tmp_path)
    _seed_common(db_path)
    _seed_owner_deliberation(db_path)
    auth_before = len(_auth_rows(db_path))
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
            "cli_extension",
            "--change-reason",
            "dry run",
            "--dry-run",
            "--json",
        ),
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["created"] is False
    assert payload["dry_run"] is True
    assert len(_auth_rows(db_path)) == auth_before
    assert _delib_count(db_path) == delib_before


# ---------------------------------------------------------------------------
# T11 - a non-owner deliberation is rejected fail-closed (NO-GO -002 F2)
# ---------------------------------------------------------------------------


def test_t11_non_owner_deliberation_rejected(tmp_path: Path) -> None:
    root, config, db_path = _project(tmp_path)
    _seed_common(db_path)
    _seed_nonowner_deliberation(db_path)
    result = CliRunner().invoke(
        main,
        _args(
            config,
            _WI_ID,
            "--owner-decision",
            _NONOWNER_DELIB,
            "--include-spec",
            _SPEC_ID,
            "--allowed-mutation",
            "cli_extension",
            "--change-reason",
            "non-owner deliberation",
        ),
    )
    assert result.exit_code != 0
    assert "not owner authority" in result.output
    assert _auth_rows(db_path) == []


# ---------------------------------------------------------------------------
# T12 - mutually-exclusive authority inputs rejected (NO-GO -002 F2)
# ---------------------------------------------------------------------------


def test_t12_conflicting_authority_inputs_rejected(tmp_path: Path) -> None:
    root, config, db_path = _project(tmp_path)
    _seed_common(db_path)
    _seed_owner_deliberation(db_path)
    content_file = root / "owner-decision.md"
    content_file.write_text("conflicting evidence\n", encoding="utf-8")
    delib_before = _delib_count(db_path)
    result = CliRunner().invoke(
        main,
        _args(
            config,
            _WI_ID,
            "--owner-decision",
            _OWNER_DELIB,
            "--auq-id",
            "AUQ-CONFLICT",
            "--auq-answer",
            "yes",
            "--decision-content-file",
            str(content_file),
            "--include-spec",
            _SPEC_ID,
            "--allowed-mutation",
            "cli_extension",
            "--change-reason",
            "conflicting authority inputs",
        ),
    )
    assert result.exit_code != 0
    assert _auth_rows(db_path) == []
    assert _delib_count(db_path) == delib_before
