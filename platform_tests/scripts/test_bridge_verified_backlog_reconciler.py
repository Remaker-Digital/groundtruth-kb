"""Tests for scripts/bridge_verified_backlog_reconciler.py."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

from groundtruth_kb.db import KnowledgeDB

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "bridge_verified_backlog_reconciler.py"


def _load_module() -> ModuleType:
    name = "bridge_verified_backlog_reconciler_for_test"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _write_index(root: Path, statuses: dict[str, str]) -> Path:
    bridge_dir = root / "bridge"
    bridge_dir.mkdir(parents=True, exist_ok=True)
    lines = ["# Bridge Index", ""]
    for slug, status in statuses.items():
        version = "002" if status == "VERIFIED" else "001"
        (bridge_dir / f"{slug}-{version}.md").write_text(
            f"{status}\n\n# {slug}\n\nContext only.\n",
            encoding="utf-8",
        )
        lines.extend(
            [
                f"Document: {slug}",
                f"{status}: bridge/{slug}-{version}.md",
                "",
            ]
        )
    path = bridge_dir / "INDEX.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _write_parent_evidence(root: Path, slug: str, item_id: str, *, version: str = "002") -> None:
    path = root / "bridge" / f"{slug}-{version}.md"
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    path.write_text(f"{existing}\nParent work item: {item_id}\n", encoding="utf-8")


def _write_work_item_metadata(root: Path, slug: str, item_id: str, *, version: str = "002") -> None:
    """Append a canonical ``Work Item: WI-XXXX`` metadata line to a bridge file."""

    path = root / "bridge" / f"{slug}-{version}.md"
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    path.write_text(f"{existing}\nWork Item: {item_id}\n", encoding="utf-8")


def _db(root: Path) -> KnowledgeDB:
    return KnowledgeDB(root / "groundtruth.db")


def _insert_work_item(
    db: KnowledgeDB,
    item_id: str,
    related: object,
    *,
    resolution_status: str = "open",
    stage: str = "backlogged",
) -> None:
    db.insert_work_item(
        item_id,
        f"{item_id} title",
        "new",
        "platform",
        resolution_status,
        "test",
        "seed",
        stage=stage,
        related_bridge_threads=json.dumps(related) if not isinstance(related, str) else related,
    )


def test_single_linked_parent_resolves_when_bridge_verified(tmp_path: Path) -> None:
    module = _load_module()
    _write_index(tmp_path, {"thread-a": "VERIFIED"})
    _write_parent_evidence(tmp_path, "thread-a", "WI-0001")
    db = _db(tmp_path)
    try:
        _insert_work_item(db, "WI-0001", ["thread-a"])
    finally:
        db.close()

    summary = module.reconcile(project_root=tmp_path, apply=True)

    db = _db(tmp_path)
    try:
        row = db.get_work_item("WI-0001")
        assert row is not None
        assert row["resolution_status"] == "resolved"
        assert row["stage"] == "resolved"
        assert "thread-a" in row["completion_evidence"]
        assert summary["resolved_ids"] == ["WI-0001"]
    finally:
        db.close()


def test_shared_parent_remains_active_when_any_link_is_not_verified(tmp_path: Path) -> None:
    module = _load_module()
    _write_index(tmp_path, {"thread-a": "VERIFIED", "thread-b": "GO"})
    _write_parent_evidence(tmp_path, "thread-a", "WI-0002")
    db = _db(tmp_path)
    try:
        _insert_work_item(db, "WI-0002", ["thread-a", "thread-b"])
    finally:
        db.close()

    summary = module.reconcile(project_root=tmp_path, apply=True)

    db = _db(tmp_path)
    try:
        row = db.get_work_item("WI-0002")
        assert row is not None
        assert row["resolution_status"] == "open"
        assert summary["resolved_ids"] == []
        assert summary["candidates"][0]["reason"] == "linked_bridge_not_verified"
    finally:
        db.close()


def test_shared_parent_resolves_when_all_links_are_verified(tmp_path: Path) -> None:
    module = _load_module()
    _write_index(tmp_path, {"thread-a": "VERIFIED", "thread-b": "VERIFIED"})
    _write_parent_evidence(tmp_path, "thread-a", "WI-0003")
    _write_parent_evidence(tmp_path, "thread-b", "WI-0003")
    db = _db(tmp_path)
    try:
        _insert_work_item(db, "WI-0003", ["thread-a", "thread-b"])
    finally:
        db.close()

    summary = module.reconcile(project_root=tmp_path, apply=True)

    db = _db(tmp_path)
    try:
        row = db.get_work_item("WI-0003")
        assert row is not None
        assert row["resolution_status"] == "resolved"
        assert summary["resolved_ids"] == ["WI-0003"]
    finally:
        db.close()


def test_unrecognized_only_references_are_skipped(tmp_path: Path) -> None:
    module = _load_module()
    _write_index(tmp_path, {"thread-a": "VERIFIED"})
    db = _db(tmp_path)
    try:
        _insert_work_item(db, "WI-0004", ["missing-thread"])
    finally:
        db.close()

    summary = module.reconcile(project_root=tmp_path, apply=True)

    assert summary["resolved_ids"] == []
    assert summary["candidates"][0]["reason"] == "missing_bridge_document"


def test_terminal_work_items_are_skipped_without_new_version(tmp_path: Path) -> None:
    module = _load_module()
    _write_index(tmp_path, {"thread-a": "VERIFIED"})
    db = _db(tmp_path)
    try:
        _insert_work_item(db, "WI-0005", ["thread-a"], resolution_status="resolved", stage="resolved")
        before_history = db.get_work_item_history("WI-0005")
    finally:
        db.close()

    summary = module.reconcile(project_root=tmp_path, apply=True)

    db = _db(tmp_path)
    try:
        after_history = db.get_work_item_history("WI-0005")
        assert len(after_history) == len(before_history)
        assert summary["candidate_count"] == 0
    finally:
        db.close()


def test_path_and_plain_slug_references_normalize_to_one_document(tmp_path: Path) -> None:
    module = _load_module()
    _write_index(tmp_path, {"thread-a": "VERIFIED"})
    _write_parent_evidence(tmp_path, "thread-a", "WI-0006")
    db = _db(tmp_path)
    try:
        _insert_work_item(db, "WI-0006", ["bridge/thread-a-001.md", "thread-a"])
    finally:
        db.close()

    summary = module.reconcile(project_root=tmp_path, apply=False)

    assert summary["would_resolve_ids"] == ["WI-0006"]
    assert summary["candidates"][0]["recognized_bridge_threads"] == ["thread-a"]


def test_dry_run_reports_candidates_without_mutating_database(tmp_path: Path) -> None:
    module = _load_module()
    _write_index(tmp_path, {"thread-a": "VERIFIED"})
    _write_parent_evidence(tmp_path, "thread-a", "WI-0007")
    db = _db(tmp_path)
    try:
        _insert_work_item(db, "WI-0007", ["thread-a"])
    finally:
        db.close()

    summary = module.reconcile(project_root=tmp_path, apply=False)

    db = _db(tmp_path)
    try:
        row = db.get_work_item("WI-0007")
        assert row is not None
        assert row["resolution_status"] == "open"
        assert summary["would_resolve_ids"] == ["WI-0007"]
        assert summary["resolved_ids"] == []
    finally:
        db.close()


def test_contextual_verified_bridge_reference_without_parent_evidence_is_skipped(tmp_path: Path) -> None:
    module = _load_module()
    _write_index(tmp_path, {"thread-a": "VERIFIED"})
    db = _db(tmp_path)
    try:
        _insert_work_item(db, "WI-0008", ["thread-a"])
    finally:
        db.close()

    summary = module.reconcile(project_root=tmp_path, apply=True)

    db = _db(tmp_path)
    try:
        row = db.get_work_item("WI-0008")
        assert row is not None
        assert row["resolution_status"] == "open"
        assert summary["resolved_ids"] == []
        assert summary["candidates"][0]["reason"] == "missing_parent_evidence"
        assert summary["candidates"][0]["missing_parent_evidence"] == ["thread-a"]
    finally:
        db.close()


def test_repair_overbroad_resolution_reopens_previous_nonterminal_version(tmp_path: Path) -> None:
    module = _load_module()
    _write_index(tmp_path, {"thread-a": "VERIFIED"})
    db = _db(tmp_path)
    try:
        _insert_work_item(db, "WI-0009", ["thread-a"])
        db.update_work_item(
            "WI-0009",
            module.CHANGED_BY,
            module.CHANGE_REASON,
            owner_approved=True,
            resolution_status="resolved",
            stage="resolved",
            completion_evidence="Resolved by broad predicate.",
        )
    finally:
        db.close()

    summary = module.reconcile(project_root=tmp_path, apply=True, repair_overbroad=True)

    db = _db(tmp_path)
    try:
        row = db.get_work_item("WI-0009")
        assert row is not None
        assert row["resolution_status"] == "open"
        assert row["stage"] == "backlogged"
        assert row["changed_by"] == module.REPAIR_CHANGED_BY
        assert summary["reopened_ids"] == ["WI-0009"]
        assert summary["would_reopen_ids"] == ["WI-0009"]
    finally:
        db.close()


def test_repair_overbroad_keeps_strict_evidence_resolution_closed(tmp_path: Path) -> None:
    module = _load_module()
    _write_index(tmp_path, {"thread-a": "VERIFIED"})
    _write_parent_evidence(tmp_path, "thread-a", "WI-0010")
    db = _db(tmp_path)
    try:
        _insert_work_item(db, "WI-0010", ["thread-a"])
        db.update_work_item(
            "WI-0010",
            module.CHANGED_BY,
            module.CHANGE_REASON,
            owner_approved=True,
            resolution_status="resolved",
            stage="resolved",
            completion_evidence="Resolved by strict predicate.",
        )
    finally:
        db.close()

    summary = module.reconcile(project_root=tmp_path, apply=True, repair_overbroad=True)

    db = _db(tmp_path)
    try:
        row = db.get_work_item("WI-0010")
        assert row is not None
        assert row["resolution_status"] == "resolved"
        assert row["changed_by"] == module.CHANGED_BY
        assert summary["reopened_ids"] == []
        assert summary["would_reopen_ids"] == []
        assert summary["repair_candidates"][0]["reason"] == "strict_parent_evidence_satisfied"
    finally:
        db.close()


def test_build_work_item_bridge_index_parses_metadata_line_only(tmp_path: Path) -> None:
    module = _load_module()
    _write_index(tmp_path, {"thread-a": "VERIFIED"})
    # Canonical metadata line for WI-0100; a prose mention of WI-0200 must not link.
    _write_work_item_metadata(tmp_path, "thread-a", "WI-0100")
    path = tmp_path / "bridge" / "thread-a-002.md"
    path.write_text(path.read_text(encoding="utf-8") + "\nSee WI-0200 for related context.\n", encoding="utf-8")

    bridge_statuses = module.parse_latest_bridge_statuses(
        (tmp_path / "bridge" / "INDEX.md").read_text(encoding="utf-8")
    )
    index = module.build_work_item_bridge_index(tmp_path, bridge_statuses)

    assert index == {"WI-0100": ["thread-a"]}
    assert "WI-0200" not in index


def test_derives_link_from_bridge_work_item_metadata_resolves_unlinked_wi(tmp_path: Path) -> None:
    module = _load_module()
    _write_index(tmp_path, {"thread-a": "VERIFIED"})
    _write_work_item_metadata(tmp_path, "thread-a", "WI-0011")
    db = _db(tmp_path)
    try:
        # related_bridge_threads=None mirrors a WI created via `gt backlog add`:
        # truly unlinked, so the pre-fix candidate filter would have excluded it.
        db.insert_work_item(
            "WI-0011",
            "WI-0011 title",
            "new",
            "platform",
            "open",
            "test",
            "seed",
            stage="backlogged",
            related_bridge_threads=None,
        )
    finally:
        db.close()

    summary = module.reconcile(project_root=tmp_path, apply=True)

    db = _db(tmp_path)
    try:
        row = db.get_work_item("WI-0011")
        assert row is not None
        assert row["resolution_status"] == "resolved"
        assert row["stage"] == "resolved"
        assert "thread-a" in row["completion_evidence"]
        assert summary["resolved_ids"] == ["WI-0011"]
        assert summary["candidates"][0]["recognized_bridge_threads"] == ["thread-a"]
    finally:
        db.close()


def test_derivation_ignores_prose_work_item_mentions(tmp_path: Path) -> None:
    module = _load_module()
    _write_index(tmp_path, {"thread-a": "VERIFIED"})
    # WI-0012 appears only in prose, never as a `Work Item:` metadata line.
    path = tmp_path / "bridge" / "thread-a-002.md"
    path.write_text(path.read_text(encoding="utf-8") + "\nThis work supports WI-0012 indirectly.\n", encoding="utf-8")
    db = _db(tmp_path)
    try:
        db.insert_work_item(
            "WI-0012",
            "WI-0012 title",
            "new",
            "platform",
            "open",
            "test",
            "seed",
            stage="backlogged",
            related_bridge_threads=None,
        )
    finally:
        db.close()

    summary = module.reconcile(project_root=tmp_path, apply=True)

    db = _db(tmp_path)
    try:
        row = db.get_work_item("WI-0012")
        assert row is not None
        assert row["resolution_status"] == "open"
        assert summary["resolved_ids"] == []
        # No derived link, no own link -> WI is not even a candidate.
        assert "WI-0012" not in [row["id"] for row in summary["candidates"]]
    finally:
        db.close()


def test_derived_link_with_unverified_sibling_thread_not_resolved(tmp_path: Path) -> None:
    module = _load_module()
    _write_index(tmp_path, {"thread-a": "VERIFIED", "thread-b": "GO"})
    # The WI's own link is the unverified sibling; the derivation adds the VERIFIED thread.
    _write_work_item_metadata(tmp_path, "thread-a", "WI-0013")
    db = _db(tmp_path)
    try:
        _insert_work_item(db, "WI-0013", ["thread-b"])
    finally:
        db.close()

    summary = module.reconcile(project_root=tmp_path, apply=True)

    db = _db(tmp_path)
    try:
        row = db.get_work_item("WI-0013")
        assert row is not None
        assert row["resolution_status"] == "open"
        assert summary["resolved_ids"] == []
        candidate = summary["candidates"][0]
        assert candidate["reason"] == "linked_bridge_not_verified"
        # Derivation supplemented the links: both the own (GO) and derived (VERIFIED) slug present.
        assert set(candidate["recognized_bridge_threads"]) == {"thread-a", "thread-b"}
    finally:
        db.close()


def test_classify_work_item_without_derived_links_is_byte_identical(tmp_path: Path) -> None:
    module = _load_module()
    _write_index(tmp_path, {"thread-a": "VERIFIED"})
    _write_parent_evidence(tmp_path, "thread-a", "WI-0014")
    bridge_statuses = module.parse_latest_bridge_statuses(
        (tmp_path / "bridge" / "INDEX.md").read_text(encoding="utf-8")
    )
    item = {
        "id": "WI-0014",
        "title": "WI-0014 title",
        "resolution_status": "open",
        "stage": "backlogged",
        "related_bridge_threads": json.dumps(["thread-a"]),
    }

    baseline = module.classify_work_item(item, bridge_statuses, project_root=tmp_path)
    with_none = module.classify_work_item(item, bridge_statuses, project_root=tmp_path, derived_links=None)
    with_empty = module.classify_work_item(item, bridge_statuses, project_root=tmp_path, derived_links={})

    assert baseline == with_none == with_empty
    assert baseline["action"] == "resolve"


def test_claude_and_codex_hooks_register_reconciler_command() -> None:
    claude = json.loads((REPO_ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
    codex = json.loads((REPO_ROOT / ".codex" / "hooks.json").read_text(encoding="utf-8"))

    claude_text = json.dumps(claude)
    codex_text = json.dumps(codex)

    assert "scripts/bridge_verified_backlog_reconciler.py" in claude_text
    assert "bridge_verified_backlog_reconciler.py" in codex_text
    assert "--apply --quiet" in claude_text
    assert "--apply --quiet" in codex_text
