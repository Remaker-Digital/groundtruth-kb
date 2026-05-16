"""Tests for the governed ``gt backlog add`` CLI service.

Authority: bridge/gtkb-backlog-add-cli-slice-1-003.md (REVISED-1), Codex GO at
``bridge/gtkb-backlog-add-cli-slice-1-004.md``. Source work item: WI-3270.

Covers the 14-test Specification-Derived Verification Plan (T1-T14):
required-field + enum validation, dry-run no-mutation, no MEMORY.md /
work_list.md write, monotonic WI-NNNN allocation, link preservation,
``backlog list`` round-trip, duplicate-id guard, fail-closed harness
attribution, fallback-author absence, and ``--json`` machine readability.

Every test runs against a temporary ``groundtruth.db`` created from a temp
``groundtruth.toml``; no test mutates the production ``groundtruth.db``,
``memory/MEMORY.md``, or ``memory/work_list.md``.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path
from unittest import mock

import pytest
from click.testing import CliRunner

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.cli import main  # noqa: E402

_FORBIDDEN_CHANGED_BY = ("gt-backlog-add", "unknown", "prime-builder/unknown")


def _project(tmp_path: Path) -> tuple[Path, Path]:
    """Create a temp project with a groundtruth.toml; return (root, config)."""
    root = tmp_path / "project"
    root.mkdir()
    config = root / "groundtruth.toml"
    config.write_text(
        '[groundtruth]\ndb_path = "./groundtruth.db"\nproject_root = "."\n',
        encoding="utf-8",
    )
    return root, config


def _add_args(config: Path, *extra: str) -> list[str]:
    """Minimal-valid ``gt backlog add`` argv with optional extra flags."""
    return [
        "--config",
        str(config),
        "backlog",
        "add",
        "--title",
        "Capture noticed defect",
        "--origin",
        "defect",
        "--component",
        "backlog",
        "--change-reason",
        "capture candidate during normal work",
        *extra,
    ]


def _wi_count(db_path: Path) -> int:
    if not db_path.exists():
        return 0
    with sqlite3.connect(db_path) as conn:
        row = conn.execute("SELECT COUNT(*) FROM current_work_items").fetchone()
    return int(row[0])


def _wi_rows(db_path: Path) -> list[sqlite3.Row]:
    if not db_path.exists():
        return []
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        return list(conn.execute("SELECT * FROM current_work_items ORDER BY id").fetchall())


def _wi_row(db_path: Path, wi_id: str) -> sqlite3.Row | None:
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute("SELECT * FROM current_work_items WHERE id = ?", (wi_id,)).fetchone()


# ---------------------------------------------------------------------------
# T1 - minimal valid inputs create exactly one row with candidate defaults
# ---------------------------------------------------------------------------


def test_add_minimal_valid_inputs_creates_row(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    db_path = root / "groundtruth.db"
    with mock.patch.dict("os.environ", {"GTKB_HARNESS_NAME": "claude"}):
        result = CliRunner().invoke(main, _add_args(config))
    assert result.exit_code == 0, result.output
    assert "Created WI-" in result.output
    assert _wi_count(db_path) == 1
    row = _wi_rows(db_path)[0]
    assert row["origin"] == "defect"
    assert row["component"] == "backlog"
    assert row["resolution_status"] == "open"
    assert row["stage"] == "backlogged"
    assert row["priority"] == "P3"


# ---------------------------------------------------------------------------
# T2 - missing required --title fails with non-zero exit and no row
# ---------------------------------------------------------------------------


def test_add_missing_required_title_fails(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    args = [
        "--config",
        str(config),
        "backlog",
        "add",
        "--origin",
        "defect",
        "--component",
        "backlog",
        "--change-reason",
        "missing title",
    ]
    with mock.patch.dict("os.environ", {"GTKB_HARNESS_NAME": "claude"}):
        result = CliRunner().invoke(main, args)
    assert result.exit_code != 0
    assert "--title" in result.output
    assert _wi_count(root / "groundtruth.db") == 0


# ---------------------------------------------------------------------------
# T3 - invalid --origin fails (enum validation)
# ---------------------------------------------------------------------------


def test_add_invalid_origin_fails(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    args = [
        "--config",
        str(config),
        "backlog",
        "add",
        "--title",
        "Bad origin",
        "--origin",
        "bogus-origin",
        "--component",
        "backlog",
        "--change-reason",
        "invalid origin",
    ]
    with mock.patch.dict("os.environ", {"GTKB_HARNESS_NAME": "claude"}):
        result = CliRunner().invoke(main, args)
    assert result.exit_code != 0
    assert _wi_count(root / "groundtruth.db") == 0


# ---------------------------------------------------------------------------
# T4 - invalid --priority fails (enum validation)
# ---------------------------------------------------------------------------


def test_add_invalid_priority_fails(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    with mock.patch.dict("os.environ", {"GTKB_HARNESS_NAME": "claude"}):
        result = CliRunner().invoke(main, _add_args(config, "--priority", "P9"))
    assert result.exit_code != 0
    assert _wi_count(root / "groundtruth.db") == 0


# ---------------------------------------------------------------------------
# T5 - dry-run reports the allocated id but does not mutate the DB
# ---------------------------------------------------------------------------


def test_add_dry_run_does_not_mutate(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    db_path = root / "groundtruth.db"
    before = _wi_count(db_path)
    with mock.patch.dict("os.environ", {"GTKB_HARNESS_NAME": "claude"}):
        result = CliRunner().invoke(main, _add_args(config, "--dry-run"))
    assert result.exit_code == 0, result.output
    assert "Would create WI-" in result.output
    assert _wi_count(db_path) == before


# ---------------------------------------------------------------------------
# T6 - command never writes memory/MEMORY.md or memory/work_list.md
# ---------------------------------------------------------------------------


def test_add_does_not_write_memory_md(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    memory_dir = root / "memory"
    memory_dir.mkdir()
    memory_md = memory_dir / "MEMORY.md"
    work_list = memory_dir / "work_list.md"
    memory_md.write_text("# memory\n", encoding="utf-8")
    work_list.write_text("# work list\n", encoding="utf-8")
    memory_before = memory_md.stat().st_mtime_ns
    work_list_before = work_list.stat().st_mtime_ns

    with mock.patch.dict("os.environ", {"GTKB_HARNESS_NAME": "claude"}):
        result = CliRunner().invoke(main, _add_args(config))
    assert result.exit_code == 0, result.output

    assert memory_md.stat().st_mtime_ns == memory_before
    assert work_list.stat().st_mtime_ns == work_list_before
    assert memory_md.read_text(encoding="utf-8") == "# memory\n"
    assert work_list.read_text(encoding="utf-8") == "# work list\n"


# ---------------------------------------------------------------------------
# T7 - sequential adds allocate monotonically increasing WI-NNNN ids
# ---------------------------------------------------------------------------


def test_add_allocates_monotonically_increasing_wi_id(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    runner = CliRunner()
    with mock.patch.dict("os.environ", {"GTKB_HARNESS_NAME": "claude"}):
        first = runner.invoke(main, _add_args(config, "--json"))
        second = runner.invoke(main, _add_args(config, "--json"))
    assert first.exit_code == 0, first.output
    assert second.exit_code == 0, second.output
    first_id = json.loads(first.output)["id"]
    second_id = json.loads(second.output)["id"]
    first_n = int(first_id[3:])
    second_n = int(second_id[3:])
    assert second_n == first_n + 1


# ---------------------------------------------------------------------------
# T8 - source_owner_directive and related-link fields are preserved
# ---------------------------------------------------------------------------


def test_add_preserves_source_owner_directive_and_links(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    db_path = root / "groundtruth.db"
    related_specs = '["SPEC-1000", "SPEC-1001"]'
    related_delibs = '["DELIB-2000"]'
    related_bridges = '["bridge/gtkb-example-001.md"]'
    depends = '["WI-9000"]'
    with mock.patch.dict("os.environ", {"GTKB_HARNESS_NAME": "claude"}):
        result = CliRunner().invoke(
            main,
            _add_args(
                config,
                "--source-owner-directive",
                "owner directive 2026-05-14",
                "--related-spec-ids",
                related_specs,
                "--related-deliberation-ids",
                related_delibs,
                "--related-bridge-threads",
                related_bridges,
                "--depends-on-work-items",
                depends,
            ),
        )
    assert result.exit_code == 0, result.output
    row = _wi_rows(db_path)[0]
    assert row["source_owner_directive"] == "owner directive 2026-05-14"
    assert json.loads(row["related_spec_ids_at_creation"]) == ["SPEC-1000", "SPEC-1001"]
    assert json.loads(row["related_deliberation_ids"]) == ["DELIB-2000"]
    assert json.loads(row["related_bridge_threads"]) == ["bridge/gtkb-example-001.md"]
    assert json.loads(row["depends_on_work_items"]) == ["WI-9000"]


# ---------------------------------------------------------------------------
# T9 - the created row round-trips through ``backlog list``
# ---------------------------------------------------------------------------


def test_add_round_trips_through_backlog_list(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    runner = CliRunner()
    with mock.patch.dict("os.environ", {"GTKB_HARNESS_NAME": "claude"}):
        created = runner.invoke(main, _add_args(config, "--json"))
        assert created.exit_code == 0, created.output
        new_id = json.loads(created.output)["id"]
        listed = runner.invoke(main, ["--config", str(config), "backlog", "list", "--json"])
    assert listed.exit_code == 0, listed.output
    items = json.loads(listed.output)
    assert any(item["id"] == new_id for item in items)


# ---------------------------------------------------------------------------
# T10 - duplicate-id guard refuses to overwrite an existing row
# ---------------------------------------------------------------------------


def test_add_duplicate_id_guard_refuses_overwrite(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    db_path = root / "groundtruth.db"

    # Pre-create the row that ``backlog add`` would allocate next (WI-0001 in
    # an empty DB) so the allocation collides.
    from groundtruth_kb.db import KnowledgeDB

    db = KnowledgeDB(db_path=db_path)
    db.insert_work_item(
        id="WI-0001",
        title="Pre-existing",
        origin="new",
        component="backlog",
        resolution_status="open",
        changed_by="prime-builder/claude",
        change_reason="pre-seed for duplicate-id guard test",
        stage="backlogged",
    )
    db.close()
    assert _wi_count(db_path) == 1

    with mock.patch.dict("os.environ", {"GTKB_HARNESS_NAME": "claude"}):
        result = CliRunner().invoke(main, _add_args(config))
    # An empty-DB allocation picks WI-0002 once WI-0001 exists, so the command
    # actually succeeds; force the collision by stubbing the allocator instead.
    # (Defensive guard is exercised directly below.)
    assert result.exit_code == 0, result.output

    # Directly exercise the duplicate-id guard: stub the allocator to return an
    # already-taken id and confirm ``add_backlog_item`` raises rather than
    # versioning over the existing row.
    from groundtruth_kb.cli_backlog_add import BacklogAddError, BacklogAddRequest, add_backlog_item
    from groundtruth_kb.config import GTConfig

    cfg = GTConfig.load(config_path=config)
    request = BacklogAddRequest(
        title="Collision",
        origin="defect",
        component="backlog",
        priority="P3",
        project_name=None,
        subproject_name=None,
        description=None,
        source_owner_directive=None,
        source_spec_id=None,
        source_deliberation_query=None,
        related_spec_ids_at_creation=None,
        related_deliberation_ids=None,
        related_bridge_threads=None,
        depends_on_work_items=None,
        acceptance_summary=None,
        regression_visibility=None,
        change_reason="duplicate-id guard",
        dry_run=False,
    )
    count_before = _wi_count(db_path)
    with (
        mock.patch.dict("os.environ", {"GTKB_HARNESS_NAME": "claude"}),
        mock.patch(
            "groundtruth_kb.cli_backlog_add._allocate_next_work_item_id",
            return_value="WI-0001",
        ),
        pytest.raises(BacklogAddError, match="already exists"),
    ):
        add_backlog_item(cfg, request)
    assert _wi_count(db_path) == count_before


# ---------------------------------------------------------------------------
# T11 - the created row's changed_by is resolved via the harness resolver
# ---------------------------------------------------------------------------


def test_add_attributes_changed_by_via_resolver(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    db_path = root / "groundtruth.db"
    with mock.patch.dict("os.environ", {"GTKB_HARNESS_NAME": "claude"}):
        result = CliRunner().invoke(main, _add_args(config, "--json"))
    assert result.exit_code == 0, result.output
    new_id = json.loads(result.output)["id"]
    row = _wi_row(db_path, new_id)
    assert row is not None
    assert row["changed_by"] == "prime-builder/claude"


# ---------------------------------------------------------------------------
# T12 - the command fails closed when no harness can be resolved
# ---------------------------------------------------------------------------


def test_add_fails_closed_without_harness_resolution(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    db_path = root / "groundtruth.db"
    count_before = _wi_count(db_path)

    # Clear GTKB_HARNESS_NAME and force the resolver's three-source resolution
    # to find no harness (no kwarg, no env, no sole Prime). Patching the
    # internal name resolver to return None makes resolve_changed_by() raise
    # RuntimeError authentically.
    with (
        mock.patch.dict("os.environ", {}, clear=True),
        mock.patch("scripts._kb_attribution._resolve_harness_name", return_value=None),
    ):
        result = CliRunner().invoke(main, _add_args(config))
    assert result.exit_code != 0
    assert _wi_count(db_path) == count_before


# ---------------------------------------------------------------------------
# T13 - no fallback-author row is ever written (audit-trail regression)
# ---------------------------------------------------------------------------


def test_add_does_not_emit_fallback_changed_by(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    db_path = root / "groundtruth.db"

    # Run the fail-closed scenario from T12, then assert no row exists with a
    # forbidden fallback ``changed_by`` literal.
    with (
        mock.patch.dict("os.environ", {}, clear=True),
        mock.patch("scripts._kb_attribution._resolve_harness_name", return_value=None),
    ):
        result = CliRunner().invoke(main, _add_args(config))
    assert result.exit_code != 0

    for row in _wi_rows(db_path):
        assert row["changed_by"] not in _FORBIDDEN_CHANGED_BY


# ---------------------------------------------------------------------------
# T14 - ``--json`` emits parseable JSON with id / created / dry_run keys
# ---------------------------------------------------------------------------


def test_add_emits_machine_readable_json(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    with mock.patch.dict("os.environ", {"GTKB_HARNESS_NAME": "claude"}):
        result = CliRunner().invoke(main, _add_args(config, "--json"))
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["id"].startswith("WI-")
    assert payload["created"] is True
    assert payload["dry_run"] is False
