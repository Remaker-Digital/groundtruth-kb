"""Spec-derived tests for ``scripts/backfill_implements_links.py`` (WI-3462).

Bridge thread ``gtkb-implements-link-backfill-phase2-implementation`` (GO -002);
scoping GO ``gtkb-implements-link-backfill-phase2-scoping-002``. Covers the
spec-to-test mapping in the implementation proposal:

- discovery classification (CLEAN / AMBIGUOUS / UNADDRESSED);
- CLEAN auto-link inserts correct ``implements`` rows;
- D3 ambiguity resolution (``*-scoping`` drop + superseded-thread drop);
- residual ambiguity fails closed and is surfaced (no link);
- UNADDRESSED untouched;
- idempotent rerun (no duplicate active links);
- no cross-project leak (a thread is linked only to projects that gate its WI);
- v4 invariant: links alone do not complete a project whose gating WIs are not
  all VERIFIED (``GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`` v4).

Isolated ``tmp_path`` project roots; the only live-repo dependency is the
script import path.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
from groundtruth_kb.db import KnowledgeDB

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"
BACKFILL_PATH = SCRIPTS_DIR / "backfill_implements_links.py"


@pytest.fixture(scope="module")
def backfill():
    # The backfill module imports project_verified_completion_scanner at call
    # time, so scripts/ must be importable.
    if str(SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_DIR))
    spec = importlib.util.spec_from_file_location("backfill_implements_links", BACKFILL_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["backfill_implements_links"] = module
    spec.loader.exec_module(module)
    return module


def _write_thread(bridge_dir: Path, slug: str, versions: list[tuple[str, str]]) -> None:
    """Write a thread's version files. ``versions`` is a list of (status, body)
    in version order (-001, -002, ...). Returns nothing; the caller appends the
    INDEX entry separately so multi-thread INDEX ordering is explicit."""
    bridge_dir.mkdir(parents=True, exist_ok=True)
    for index, (_status, body) in enumerate(versions, start=1):
        (bridge_dir / f"{slug}-{index:03d}.md").write_text(body, encoding="utf-8")


def _build_index(bridge_dir: Path, threads: list[tuple[str, list[str]]]) -> None:
    """Write bridge/INDEX.md. ``threads`` is a list of (slug, [status lines top-first])."""
    lines = ["# Bridge Index", ""]
    for slug, status_lines in threads:
        lines.append(f"Document: {slug}")
        lines.extend(status_lines)
        lines.append("")
    bridge_dir.mkdir(parents=True, exist_ok=True)
    (bridge_dir / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _seed_db(
    project_root: Path,
    *,
    projects: dict[str, list[str]],
    pre_linked: dict[str, list[str]] | None = None,
) -> None:
    """Seed projects + one active authorization each + gating memberships.

    ``projects`` maps project_id -> [gating work item ids]. ``pre_linked`` maps
    project_id -> [thread slugs already implements-linked] (for idempotency).
    """
    db = KnowledgeDB(project_root / "groundtruth.db")
    try:
        db.insert_deliberation(
            "DELIB-SEED",
            "owner_conversation",
            "seed",
            "seed",
            "{}",
            "t",
            "s",
            outcome="owner_decision",
        )
        db.insert_spec(id="SPEC-SEED", title="Seed", status="verified", changed_by="t", change_reason="s")
        for project_id, wis in projects.items():
            db.insert_project(project_id, "t", "s", id=project_id, status="active")
            for wi in wis:
                if db.get_work_item(wi) is None:
                    db.insert_work_item(wi, f"WI {wi}", "new", "backlog", "open", "t", "s")
                db.link_project_work_item(project_id, wi, "t", "s")
            db.insert_project_authorization(
                project_id,
                f"auth {project_id}",
                "DELIB-SEED",
                "scope",
                "t",
                "s",
                id=f"PAUTH-{project_id}",
                status="active",
                included_work_item_ids=wis,
                included_spec_ids=["SPEC-SEED"],
            )
        for project_id, slugs in (pre_linked or {}).items():
            for slug in slugs:
                db.add_project_artifact_link(
                    project_id,
                    "bridge_thread",
                    slug,
                    "t",
                    "pre-seed",
                    relationship="implements",
                )
    finally:
        db.close()


def _impl_report(wi: str, *, supersedes: str | None = None) -> str:
    body = f"NEW\n\n# Implementation report\n\nWork Item: {wi}\n"
    if supersedes:
        body += f"\nSupersedes implementation thread: bridge/{supersedes}-001.md\n"
    return body


# --------------------------------------------------------------------------- #
# Discovery classification
# --------------------------------------------------------------------------- #


def test_classify_clean_ambiguous_unaddressed(backfill, tmp_path):
    bridge = tmp_path / "bridge"
    # CLEAN: WI-1 has exactly one addressing thread.
    _write_thread(bridge, "thread-clean", [("VERIFIED", _impl_report("WI-1"))])
    # AMBIGUOUS: WI-2 has two non-scoping, non-superseding threads.
    _write_thread(bridge, "thread-amb-a", [("VERIFIED", _impl_report("WI-2"))])
    _write_thread(bridge, "thread-amb-b", [("GO", _impl_report("WI-2"))])
    # UNADDRESSED: WI-3 has no addressing thread.
    _build_index(
        bridge,
        [
            ("thread-clean", ["VERIFIED: bridge/thread-clean-001.md"]),
            ("thread-amb-a", ["VERIFIED: bridge/thread-amb-a-001.md"]),
            ("thread-amb-b", ["GO: bridge/thread-amb-b-001.md"]),
        ],
    )
    _seed_db(
        tmp_path,
        projects={
            "PROJECT-CLEAN": ["WI-1"],
            "PROJECT-AMB": ["WI-2"],
            "PROJECT-UNADDR": ["WI-3"],
        },
    )

    by_id = {pc.project_id: pc for pc in backfill.discover(tmp_path)}
    assert by_id["PROJECT-CLEAN"].classification == "clean"
    assert by_id["PROJECT-CLEAN"].resolved_links == {"WI-1": "thread-clean"}
    assert by_id["PROJECT-AMB"].classification == "ambiguous"
    assert sorted(by_id["PROJECT-AMB"].ambiguous_work_items["WI-2"]) == ["thread-amb-a", "thread-amb-b"]
    assert by_id["PROJECT-UNADDR"].classification == "unaddressed"
    assert by_id["PROJECT-UNADDR"].unaddressed_work_items == ["WI-3"]


# --------------------------------------------------------------------------- #
# CLEAN auto-link
# --------------------------------------------------------------------------- #


def test_clean_auto_link(backfill, tmp_path):
    bridge = tmp_path / "bridge"
    _write_thread(bridge, "thread-clean", [("VERIFIED", _impl_report("WI-1"))])
    _build_index(bridge, [("thread-clean", ["VERIFIED: bridge/thread-clean-001.md"])])
    _seed_db(tmp_path, projects={"PROJECT-CLEAN": ["WI-1"]})

    result = backfill.apply_backfill(tmp_path)
    assert len(result["inserted"]) == 1
    assert result["inserted"][0]["project_id"] == "PROJECT-CLEAN"
    assert result["inserted"][0]["thread"] == "thread-clean"

    # Verify the row is a live active implements link.
    from project_verified_completion_scanner import _implements_links_by_project

    links = _implements_links_by_project(tmp_path)
    assert links.get("PROJECT-CLEAN") == {"thread-clean"}


# --------------------------------------------------------------------------- #
# D3 ambiguity resolution
# --------------------------------------------------------------------------- #


def test_d3_drops_scoping_when_nonscoping_sibling_exists(backfill, tmp_path):
    bridge = tmp_path / "bridge"
    # WI-1 cited by a -scoping thread AND a non-scoping impl thread.
    _write_thread(bridge, "feat-scoping", [("GO", _impl_report("WI-1"))])
    _write_thread(bridge, "feat-implementation", [("VERIFIED", _impl_report("WI-1"))])
    _build_index(
        bridge,
        [
            ("feat-scoping", ["GO: bridge/feat-scoping-001.md"]),
            ("feat-implementation", ["VERIFIED: bridge/feat-implementation-001.md"]),
        ],
    )
    _seed_db(tmp_path, projects={"PROJECT-X": ["WI-1"]})

    by_id = {pc.project_id: pc for pc in backfill.discover(tmp_path)}
    pc = by_id["PROJECT-X"]
    assert pc.classification == "clean"
    assert pc.resolved_links == {"WI-1": "feat-implementation"}


def test_d3_drops_superseded_thread(backfill, tmp_path):
    bridge = tmp_path / "bridge"
    # v3 thread cites WI-1; v4 superseder cites WI-1 and declares supersession.
    _write_thread(bridge, "feat-v3", [("GO", _impl_report("WI-1"))])
    _write_thread(bridge, "feat-v4", [("VERIFIED", _impl_report("WI-1", supersedes="feat-v3"))])
    _build_index(
        bridge,
        [
            ("feat-v3", ["GO: bridge/feat-v3-001.md"]),
            ("feat-v4", ["VERIFIED: bridge/feat-v4-001.md"]),
        ],
    )
    _seed_db(tmp_path, projects={"PROJECT-X": ["WI-1"]})

    by_id = {pc.project_id: pc for pc in backfill.discover(tmp_path)}
    pc = by_id["PROJECT-X"]
    assert pc.classification == "clean"
    assert pc.resolved_links == {"WI-1": "feat-v4"}


def test_residual_ambiguity_fails_closed_and_is_surfaced(backfill, tmp_path):
    bridge = tmp_path / "bridge"
    # Two non-scoping, non-superseding threads cite WI-1: genuinely ambiguous.
    _write_thread(bridge, "feat-a", [("VERIFIED", _impl_report("WI-1"))])
    _write_thread(bridge, "feat-b", [("VERIFIED", _impl_report("WI-1"))])
    _build_index(
        bridge,
        [
            ("feat-a", ["VERIFIED: bridge/feat-a-001.md"]),
            ("feat-b", ["VERIFIED: bridge/feat-b-001.md"]),
        ],
    )
    _seed_db(tmp_path, projects={"PROJECT-X": ["WI-1"]})

    result = backfill.apply_backfill(tmp_path)
    assert result["inserted"] == []
    assert "PROJECT-X" in result["ambiguous_projects"]
    assert len(result["needs_owner_auq"]) == 1
    # No link was written (fail closed).
    from project_verified_completion_scanner import _implements_links_by_project

    assert _implements_links_by_project(tmp_path).get("PROJECT-X", set()) == set()


# --------------------------------------------------------------------------- #
# UNADDRESSED untouched
# --------------------------------------------------------------------------- #


def test_unaddressed_untouched(backfill, tmp_path):
    bridge = tmp_path / "bridge"
    # No thread cites WI-1.
    _write_thread(bridge, "unrelated", [("VERIFIED", _impl_report("WI-99"))])
    _build_index(bridge, [("unrelated", ["VERIFIED: bridge/unrelated-001.md"])])
    _seed_db(tmp_path, projects={"PROJECT-X": ["WI-1"]})

    result = backfill.apply_backfill(tmp_path)
    assert result["inserted"] == []
    assert "PROJECT-X" in result["unaddressed_projects"]
    from project_verified_completion_scanner import _implements_links_by_project

    assert _implements_links_by_project(tmp_path).get("PROJECT-X", set()) == set()


# --------------------------------------------------------------------------- #
# Idempotency
# --------------------------------------------------------------------------- #


def test_idempotent_rerun_no_duplicate_links(backfill, tmp_path):
    bridge = tmp_path / "bridge"
    _write_thread(bridge, "thread-clean", [("VERIFIED", _impl_report("WI-1"))])
    _build_index(bridge, [("thread-clean", ["VERIFIED: bridge/thread-clean-001.md"])])
    _seed_db(tmp_path, projects={"PROJECT-CLEAN": ["WI-1"]})

    first = backfill.apply_backfill(tmp_path)
    assert len(first["inserted"]) == 1
    assert first["skipped"] == []

    second = backfill.apply_backfill(tmp_path)
    assert second["inserted"] == []
    assert len(second["skipped"]) == 1
    assert second["skipped"][0]["thread"] == "thread-clean"

    # Exactly one active link version-chain remains in the current view.
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        rows = (
            db._get_conn()
            .execute(
                "SELECT COUNT(*) FROM current_project_artifact_links "
                "WHERE project_id='PROJECT-CLEAN' AND artifact_type='bridge_thread' "
                "AND relationship='implements' AND status='active'"
            )
            .fetchone()[0]
        )
    finally:
        db.close()
    assert rows == 1


# --------------------------------------------------------------------------- #
# No cross-project leak
# --------------------------------------------------------------------------- #


def test_no_cross_project_leak(backfill, tmp_path):
    bridge = tmp_path / "bridge"
    # thread-a addresses WI-1. PROJECT-A gates WI-1; PROJECT-C does NOT gate WI-1.
    _write_thread(bridge, "thread-a", [("VERIFIED", _impl_report("WI-1"))])
    _build_index(bridge, [("thread-a", ["VERIFIED: bridge/thread-a-001.md"])])
    _seed_db(tmp_path, projects={"PROJECT-A": ["WI-1"], "PROJECT-C": ["WI-2"]})

    backfill.apply_backfill(tmp_path)
    from project_verified_completion_scanner import _implements_links_by_project

    links = _implements_links_by_project(tmp_path)
    assert links.get("PROJECT-A") == {"thread-a"}
    # thread-a must NOT be linked to PROJECT-C (which does not gate WI-1).
    assert "thread-a" not in links.get("PROJECT-C", set())


def test_shared_wi_links_thread_to_every_gating_project(backfill, tmp_path):
    bridge = tmp_path / "bridge"
    # WI-1 is a member of BOTH projects; thread-a addresses it. Both projects
    # legitimately get the link (the link is per-project, not leaked).
    _write_thread(bridge, "thread-a", [("VERIFIED", _impl_report("WI-1"))])
    _build_index(bridge, [("thread-a", ["VERIFIED: bridge/thread-a-001.md"])])
    _seed_db(tmp_path, projects={"PROJECT-A": ["WI-1"], "PROJECT-B": ["WI-1"]})

    backfill.apply_backfill(tmp_path)
    from project_verified_completion_scanner import _implements_links_by_project

    links = _implements_links_by_project(tmp_path)
    assert links.get("PROJECT-A") == {"thread-a"}
    assert links.get("PROJECT-B") == {"thread-a"}


# --------------------------------------------------------------------------- #
# v4 invariant: links alone do not complete an unfinished project
# --------------------------------------------------------------------------- #


def test_links_do_not_complete_unfinished_project(backfill, tmp_path):
    bridge = tmp_path / "bridge"
    # Two gating WIs. WI-1's thread is VERIFIED; WI-2's thread is only GO.
    _write_thread(bridge, "thread-done", [("VERIFIED", _impl_report("WI-1"))])
    _write_thread(bridge, "thread-wip", [("GO", _impl_report("WI-2"))])
    _build_index(
        bridge,
        [
            ("thread-done", ["VERIFIED: bridge/thread-done-001.md"]),
            ("thread-wip", ["GO: bridge/thread-wip-001.md"]),
        ],
    )
    _seed_db(tmp_path, projects={"PROJECT-X": ["WI-1", "WI-2"]})

    # Both gating WIs have an addressing thread -> CLEAN -> both linked.
    result = backfill.apply_backfill(tmp_path)
    assert "PROJECT-X" in result["clean_projects"]
    assert {ins["thread"] for ins in result["inserted"]} == {"thread-done", "thread-wip"}

    # v4 completion gate: PROJECT-X must NOT be completion-ready, because WI-2's
    # addressing thread is GO (not VERIFIED), so WI-2 is not VERIFIED-for-project.
    if str(SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_DIR))
    import project_verified_completion_scanner as scanner

    ready = scanner.completion_ready(tmp_path)
    assert all(r.project_id != "PROJECT-X" for r in ready), (
        "links alone must not complete a project whose gating WIs are not all VERIFIED"
    )
    # The verified-for-project set contains only WI-1 (the VERIFIED thread).
    by_project = scanner.verified_work_items_by_project(tmp_path)
    assert by_project.get("PROJECT-X") == {"WI-1"}


def test_report_mode_is_read_only(backfill, tmp_path):
    bridge = tmp_path / "bridge"
    _write_thread(bridge, "thread-clean", [("VERIFIED", _impl_report("WI-1"))])
    _build_index(bridge, [("thread-clean", ["VERIFIED: bridge/thread-clean-001.md"])])
    _seed_db(tmp_path, projects={"PROJECT-CLEAN": ["WI-1"]})

    backfill.discover(tmp_path)  # report path
    from project_verified_completion_scanner import _implements_links_by_project

    # discover() must not have written any link.
    assert _implements_links_by_project(tmp_path).get("PROJECT-CLEAN", set()) == set()
