"""Tests for the governed ``gt backlog status`` CLI service.

Authority: bridge/gtkb-discoverability-cli-slice-2-implementation-003.md
(REVISED-1), Codex GO at -004. Source work item: WI-3262.

Covers the 10-test Specification-Derived Verification Plan (T1-T10):

* T1 base lists projects with resolution_status_breakdown.
* T2 ``--project <PID>`` filters to one project.
* T3 ``--json`` output is parseable and schema-stable.
* T4 ``--with-orphans`` surfaces a membership-less work item.
* T5 ``--with-retire-ready`` surfaces a completion-ready authorization
  (via the canonical scanner module's ``completion_ready``).
* T6 ``--with-verified-coverage`` annotates per-WI coverage (via the
  canonical scanner module's ``verified_work_items_by_project``).
* T7 retire-ready / verified-coverage output carries ``scanner_caveat``
  naming the canonical thread
  ``gtkb-project-completion-scanner-addressing-thread-fix`` AND not the
  withdrawn ``-implementation`` slug.
* T8 read-only: the db file is byte-identical before and after.
* T9 ``doubled_prefix_flag`` set for a ``PROJECT-PROJECT-*`` project.
* T10 base output (no scanner flags) imports no scanner module: the test
  injects a sentinel module that raises ``ImportError`` if the base path
  ever reaches ``scripts.project_verified_completion_scanner``.

Every test runs against a temporary ``groundtruth.db`` created from a temp
``groundtruth.toml``; no test mutates the canonical ``groundtruth.db``
or ``memory/MEMORY.md``.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.cli import main  # noqa: E402
from groundtruth_kb.cli_backlog_status import (  # noqa: E402
    BacklogStatusRequest,
    build_backlog_status,
)
from groundtruth_kb.config import GTConfig  # noqa: E402
from groundtruth_kb.db import KnowledgeDB  # noqa: E402


def _project(tmp_path: Path) -> tuple[Path, Path]:
    """Create a temp project with a groundtruth.toml; return (root, config-file)."""
    root = tmp_path / "project"
    root.mkdir()
    config = root / "groundtruth.toml"
    config.write_text(
        '[groundtruth]\ndb_path = "./groundtruth.db"\nproject_root = "."\n',
        encoding="utf-8",
    )
    return root, config


def _seed_basic_project(db_path: Path) -> None:
    """Seed two projects + three work items + memberships.

    * PROJECT-GTKB-X (canonical id; one work item via backfill from
      ``project_name="GTKB-X"``).
    * PROJECT-PROJECT-GTKB-Y (phantom doubled-prefix id seeded directly via
      ``insert_project(id=...)`` so the seed is independent of whether the
      idempotent fix in ``_project_id_from_names`` is active in the running
      process). The doubled-prefix pattern is a phantom artifact of the
      pre-fix derivation; existing instances persist after the fix and must
      still surface in the status report.
    * WI-ORPHAN exists with no membership (used by T4).
    """
    db = KnowledgeDB(db_path=db_path)
    try:
        # Canonical-id project, created indirectly through the backfill.
        db.insert_work_item(
            id="WI-9001",
            title="Canonical project member",
            origin="defect",
            component="backlog",
            resolution_status="open",
            changed_by="test",
            change_reason="seed canonical project member",
            project_name="GTKB-X",
        )
        # Phantom doubled-prefix project, created with an explicit id so the
        # seed is independent of the idempotent fix state.
        db.insert_project(
            name="GTKB-Y",
            id="PROJECT-PROJECT-GTKB-Y",
            changed_by="test",
            change_reason="seed phantom doubled-prefix project for status flag test",
        )
        db.insert_work_item(
            id="WI-9002",
            title="Doubled-prefix project member",
            origin="defect",
            component="backlog",
            resolution_status="resolved",
            changed_by="test",
            change_reason="seed doubled-prefix project member",
        )
        db.link_project_work_item(
            project_id="PROJECT-PROJECT-GTKB-Y",
            work_item_id="WI-9002",
            changed_by="test",
            change_reason="seed phantom membership for doubled-prefix flag test",
        )
        # Orphan work item: deliberately no project_name and no membership.
        db.insert_work_item(
            id="WI-ORPHAN",
            title="Orphan work item (no membership)",
            origin="defect",
            component="backlog",
            resolution_status="open",
            changed_by="test",
            change_reason="seed orphan",
        )
        # Run the backfill so PROJECT-GTKB-X is created from WI-9001's
        # project_name compatibility field. Under the idempotent fix this
        # produces the canonical id (not the doubled-prefix form).
        db._backfill_project_artifacts_from_work_items()
    finally:
        db.close()


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# T1 — base lists projects with resolution_status_breakdown
# ---------------------------------------------------------------------------


def test_status_base_lists_projects_with_breakdown(tmp_path: Path) -> None:
    root, config_file = _project(tmp_path)
    _seed_basic_project(root / "groundtruth.db")

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--config", str(config_file), "backlog", "status", "--json"],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    project_ids = {p["id"] for p in payload["projects"]}
    assert "PROJECT-GTKB-X" in project_ids
    canonical = next(p for p in payload["projects"] if p["id"] == "PROJECT-GTKB-X")
    assert canonical["resolution_status_breakdown"] == {"open": 1}
    assert canonical["work_item_count"] == 1


# ---------------------------------------------------------------------------
# T2 — --project <PID> filters to one project
# ---------------------------------------------------------------------------


def test_status_project_filter(tmp_path: Path) -> None:
    root, config_file = _project(tmp_path)
    _seed_basic_project(root / "groundtruth.db")

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--config",
            str(config_file),
            "backlog",
            "status",
            "--project",
            "PROJECT-GTKB-X",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert [p["id"] for p in payload["projects"]] == ["PROJECT-GTKB-X"]


# ---------------------------------------------------------------------------
# T3 — --json output is parseable and schema-stable
# ---------------------------------------------------------------------------


def test_status_json_parseable_and_keys(tmp_path: Path) -> None:
    root, config_file = _project(tmp_path)
    _seed_basic_project(root / "groundtruth.db")

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--config", str(config_file), "backlog", "status", "--json"],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)

    assert set(payload.keys()) >= {"projects", "summary"}
    assert set(payload["summary"].keys()) >= {
        "project_count",
        "doubled_prefix_project_count",
        "total_active_memberships",
    }
    project_row_keys = {
        "id",
        "name",
        "status",
        "work_item_count",
        "resolution_status_breakdown",
        "doubled_prefix_flag",
    }
    for project_row in payload["projects"]:
        assert project_row_keys <= set(project_row.keys())


# ---------------------------------------------------------------------------
# T4 — --with-orphans surfaces a membership-less work item
# ---------------------------------------------------------------------------


def test_status_orphans_surfaced(tmp_path: Path) -> None:
    root, config_file = _project(tmp_path)
    _seed_basic_project(root / "groundtruth.db")

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--config",
            str(config_file),
            "backlog",
            "status",
            "--with-orphans",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    orphan_ids = {wi["id"] for wi in payload["orphan_work_items"]}
    assert "WI-ORPHAN" in orphan_ids


# ---------------------------------------------------------------------------
# T5 — --with-retire-ready uses the scanner module
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _FakeReadiness:
    """Stand-in for ``project_verified_completion_scanner.AuthorizationReadiness``."""

    authorization_id: str
    project_id: str
    authorization_name: str
    included_work_item_ids: list[str]
    verified_work_item_ids: list[str]
    unverified_work_item_ids: list[str]
    completion_ready: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "authorization_id": self.authorization_id,
            "project_id": self.project_id,
            "authorization_name": self.authorization_name,
            "included_work_item_ids": self.included_work_item_ids,
            "verified_work_item_ids": self.verified_work_item_ids,
            "unverified_work_item_ids": self.unverified_work_item_ids,
            "completion_ready": self.completion_ready,
        }


def test_status_retire_ready_uses_scanner(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root, config_file = _project(tmp_path)
    _seed_basic_project(root / "groundtruth.db")

    sentinel = _FakeReadiness(
        authorization_id="PAUTH-FAKE-001",
        project_id="PROJECT-GTKB-X",
        authorization_name="Fake completion-ready authorization",
        included_work_item_ids=["WI-9001"],
        verified_work_item_ids=["WI-9001"],
        unverified_work_item_ids=[],
        completion_ready=True,
    )

    scanner_mod = importlib.import_module("scripts.project_verified_completion_scanner")
    monkeypatch.setattr(scanner_mod, "completion_ready", lambda *_a, **_kw: [sentinel])
    monkeypatch.setattr(scanner_mod, "verified_work_items_by_project", lambda *_a, **_kw: {})

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--config",
            str(config_file),
            "backlog",
            "status",
            "--with-retire-ready",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert "retire_ready" in payload
    assert payload["retire_ready"] == [sentinel.as_dict()]


# ---------------------------------------------------------------------------
# T6 — --with-verified-coverage annotates per-WI coverage
# ---------------------------------------------------------------------------


def test_status_verified_coverage_annotation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root, config_file = _project(tmp_path)
    _seed_basic_project(root / "groundtruth.db")

    scanner_mod = importlib.import_module("scripts.project_verified_completion_scanner")
    monkeypatch.setattr(
        scanner_mod,
        "verified_work_items_by_project",
        lambda *_a, **_kw: {"PROJECT-GTKB-X": {"WI-9001"}},
    )
    monkeypatch.setattr(scanner_mod, "completion_ready", lambda *_a, **_kw: [])

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--config",
            str(config_file),
            "backlog",
            "status",
            "--with-verified-coverage",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    canonical = next(p for p in payload["projects"] if p["id"] == "PROJECT-GTKB-X")
    assert canonical["verified_bridge_covered"] == {"WI-9001": True}
    doubled = next(p for p in payload["projects"] if p["id"] == "PROJECT-PROJECT-GTKB-Y")
    assert doubled["verified_bridge_covered"] == {"WI-9002": False}


# ---------------------------------------------------------------------------
# T7 — scanner_caveat names canonical thread (not -implementation)
# ---------------------------------------------------------------------------


def test_status_scanner_caveat_present_when_flags_set(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root, config_file = _project(tmp_path)
    _seed_basic_project(root / "groundtruth.db")

    scanner_mod = importlib.import_module("scripts.project_verified_completion_scanner")
    monkeypatch.setattr(scanner_mod, "verified_work_items_by_project", lambda *_a, **_kw: {})
    monkeypatch.setattr(scanner_mod, "completion_ready", lambda *_a, **_kw: [])

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--config",
            str(config_file),
            "backlog",
            "status",
            "--with-retire-ready",
            "--with-verified-coverage",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    caveat = payload["scanner_caveat"]
    assert "gtkb-project-completion-scanner-addressing-thread-fix" in caveat, (
        f"canonical scanner-fix slug missing; caveat={caveat!r}"
    )
    # The withdrawn duplicate must NOT appear (proposal F1 correction). We
    # detect it by looking for the disambiguating ``-implementation.md``
    # filename fragment so the substring check does not false-positive on the
    # canonical slug above.
    assert "addressing-thread-fix-implementation" not in caveat, (
        f"withdrawn `-implementation` duplicate slug present; caveat={caveat!r}"
    )
    assert "VERIFIED at bridge thread" in caveat
    assert "in flight" not in caveat


# ---------------------------------------------------------------------------
# T8 — read-only: db file byte-identical before/after
# ---------------------------------------------------------------------------


def test_status_makes_no_db_writes(tmp_path: Path) -> None:
    root, config_file = _project(tmp_path)
    db_path = root / "groundtruth.db"
    _seed_basic_project(db_path)
    hash_before = _file_hash(db_path)

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--config",
            str(config_file),
            "backlog",
            "status",
            "--with-orphans",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.output

    hash_after = _file_hash(db_path)
    assert hash_before == hash_after, "gt backlog status mutated the database; this command must be read-only"


# ---------------------------------------------------------------------------
# T9 — doubled_prefix_flag set for a PROJECT-PROJECT-* project
# ---------------------------------------------------------------------------


def test_status_flags_doubled_prefix_project(tmp_path: Path) -> None:
    root, config_file = _project(tmp_path)
    _seed_basic_project(root / "groundtruth.db")

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--config", str(config_file), "backlog", "status", "--json"],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    flagged = [p for p in payload["projects"] if p["doubled_prefix_flag"]]
    flagged_ids = {p["id"] for p in flagged}
    assert "PROJECT-PROJECT-GTKB-Y" in flagged_ids, (
        f"doubled-prefix project not flagged; project_ids in flagged={flagged_ids!r}"
    )
    # And the canonical project is NOT flagged.
    canonical = next(p for p in payload["projects"] if p["id"] == "PROJECT-GTKB-X")
    assert canonical["doubled_prefix_flag"] is False


# ---------------------------------------------------------------------------
# T10 — base output (no flags) imports no scanner module
# ---------------------------------------------------------------------------


def test_status_base_has_no_scanner_dependency(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root, config_file = _project(tmp_path)
    _seed_basic_project(root / "groundtruth.db")

    # Replace the scanner module in sys.modules with a sentinel that raises
    # AttributeError on any attribute access. If the base command path
    # reaches the scanner, calling completion_ready /
    # verified_work_items_by_project will surface immediately and fail the test.
    class _Sentinel:
        def __getattr__(self, name: str) -> Any:
            raise AssertionError(
                f"base `gt backlog status` accessed scripts.project_verified_completion_scanner.{name!r};"
                " the base path must not import or use the scanner module"
            )

    sentinel = _Sentinel()
    monkeypatch.setitem(
        sys.modules,
        "scripts.project_verified_completion_scanner",
        sentinel,
    )

    # Service-level invocation: build_backlog_status with no scanner flags.
    config = GTConfig.load(config_file)
    request = BacklogStatusRequest(
        with_orphans=False,
        with_retire_ready=False,
        with_verified_coverage=False,
    )
    result = build_backlog_status(config, request)
    assert "scanner_caveat" not in result
    assert "retire_ready" not in result
    for project_row in result["projects"]:
        assert "verified_bridge_covered" not in project_row
