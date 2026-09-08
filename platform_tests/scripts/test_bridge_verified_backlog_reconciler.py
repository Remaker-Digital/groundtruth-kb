"""Tests for scripts/bridge_verified_backlog_reconciler.py."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest
from groundtruth_kb.db import KnowledgeDB

from scripts.windows_subprocess import no_window_subprocess_kwargs

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


def _write_bridge_kind(root: Path, slug: str, bridge_kind: str, *, version: str = "001") -> None:
    path = root / "bridge" / f"{slug}-{version}.md"
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    path.write_text(f"{existing}\nbridge_kind: {bridge_kind}\n", encoding="utf-8")


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


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        **no_window_subprocess_kwargs(),
    )
    assert result.returncode == 0, result.stderr or result.stdout
    return result


def _init_git(root: Path) -> None:
    _git(root, "init", "-q")
    _git(root, "config", "user.email", "test@example.invalid")
    _git(root, "config", "user.name", "GT-KB Test")


def _write_strict_thread(
    root: Path,
    item_id: str,
    *,
    target_paths: list[str] | str,
    slug: str = "strict-thread",
    response_status: str = "NEW",
    waiver: bool = False,
    include_verdict: bool = True,
) -> dict[str, Path]:
    bridge_dir = root / "bridge"
    bridge_dir.mkdir(parents=True, exist_ok=True)
    target_value = json.dumps(target_paths) if isinstance(target_paths, list) else target_paths
    paths = {
        "proposal": bridge_dir / f"{slug}-001.md",
        "go": bridge_dir / f"{slug}-002.md",
        "report": bridge_dir / f"{slug}-003.md",
        "verdict": bridge_dir / f"{slug}-004.md",
    }
    paths["proposal"].write_text(
        "\n".join(
            [
                "NEW",
                "bridge_kind: prime_proposal",
                f"Work Item: {item_id}",
                f"target_paths: {target_value}",
                "",
                "# Implementation Proposal - strict closure fixture",
            ]
        ),
        encoding="utf-8",
    )
    paths["go"].write_text(
        "\n".join(
            [
                "GO",
                f"Responds to: bridge/{slug}-001.md",
                f"Work Item: {item_id}",
            ]
        ),
        encoding="utf-8",
    )
    report_lines = [
        response_status,
        "bridge_kind: implementation_report"
        if response_status != "NO-ACTION"
        else "bridge_kind: operational_state_change",
        f"Approved proposal: bridge/{slug}-001.md",
        f"Work Item: {item_id}",
    ]
    if waiver:
        report_lines.extend(
            [
                "",
                "## By-Reference Finalization Waiver",
                "Owner-approved by-reference waiver: DELIB-TEST-BY-REFERENCE-001.",
            ]
        )
    paths["report"].write_text("\n".join(report_lines), encoding="utf-8")
    if include_verdict:
        paths["verdict"].write_text(
            "\n".join(
                [
                    "VERIFIED",
                    f"Responds to: bridge/{slug}-003.md",
                    f"Work Item: {item_id}",
                ]
            ),
            encoding="utf-8",
        )
    return paths


def _classify_strict_thread(root: Path, item_id: str) -> dict[str, object]:
    module = _load_module()
    statuses = module.collect_latest_bridge_statuses(root)
    return module.classify_work_item(
        {
            "id": item_id,
            "title": "strict closure fixture",
            "resolution_status": "open",
            "stage": "backlogged",
            "related_bridge_threads": '["strict-thread"]',
        },
        statuses,
        project_root=root,
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


def test_shared_parent_remains_active_when_any_link_is_not_verified(
    tmp_path: Path,
) -> None:
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


@pytest.mark.parametrize("status", ["ADVISORY", "WITHDRAWN"])
def test_non_implementation_terminal_link_does_not_block_verified_implementation(tmp_path: Path, status: str) -> None:
    module = _load_module()
    _write_index(tmp_path, {"impl-thread": "VERIFIED", "traceability-thread": status})
    _write_parent_evidence(tmp_path, "impl-thread", "WI-0201")
    db = _db(tmp_path)
    try:
        _insert_work_item(db, "WI-0201", ["impl-thread", "traceability-thread"])
    finally:
        db.close()

    summary = module.reconcile(project_root=tmp_path, apply=True)

    db = _db(tmp_path)
    try:
        row = db.get_work_item("WI-0201")
        assert row is not None
        assert row["resolution_status"] == "resolved"
        assert summary["resolved_ids"] == ["WI-0201"]
        candidate = summary["candidates"][0]
        assert candidate["reason"] == "non_implementation_links_ignored"
        assert candidate["satisfied_implementation_bridge_threads"] == ["impl-thread"]
        assert candidate["non_blocking_bridge_threads"] == ["traceability-thread"]
        assert "traceability-thread" in row["completion_evidence"]
    finally:
        db.close()


def test_advisory_kind_go_link_does_not_block_verified_implementation(
    tmp_path: Path,
) -> None:
    module = _load_module()
    _write_index(tmp_path, {"impl-thread": "VERIFIED", "advisory-go": "GO"})
    _write_parent_evidence(tmp_path, "impl-thread", "WI-0202")
    _write_bridge_kind(tmp_path, "advisory-go", "governance_advisory_revision")
    db = _db(tmp_path)
    try:
        _insert_work_item(db, "WI-0202", ["impl-thread", "advisory-go"])
    finally:
        db.close()

    summary = module.reconcile(project_root=tmp_path, apply=True)

    db = _db(tmp_path)
    try:
        row = db.get_work_item("WI-0202")
        assert row is not None
        assert row["resolution_status"] == "resolved"
        assert summary["resolved_ids"] == ["WI-0202"]
        candidate = summary["candidates"][0]
        assert candidate["reason"] == "non_implementation_links_ignored"
        assert candidate["non_blocking_bridge_threads"] == ["advisory-go"]
    finally:
        db.close()


def test_advisory_link_alone_does_not_resolve_without_verified_implementation(
    tmp_path: Path,
) -> None:
    module = _load_module()
    _write_index(tmp_path, {"advisory": "ADVISORY"})
    db = _db(tmp_path)
    try:
        _insert_work_item(db, "WI-0203", ["advisory"])
    finally:
        db.close()

    summary = module.reconcile(project_root=tmp_path, apply=True)

    db = _db(tmp_path)
    try:
        row = db.get_work_item("WI-0203")
        assert row is not None
        assert row["resolution_status"] == "open"
        assert summary["resolved_ids"] == []
        assert summary["candidates"][0]["reason"] == "linked_bridge_not_verified"
    finally:
        db.close()


@pytest.mark.parametrize("blocking_status", ["NEW", "REVISED", "NO-ACTION", "NO-GO", "DEFERRED"])
def test_implementation_like_non_verified_links_still_block_resolution(tmp_path: Path, blocking_status: str) -> None:
    module = _load_module()
    _write_index(tmp_path, {"impl-thread": "VERIFIED", "blocking-thread": blocking_status})
    _write_parent_evidence(tmp_path, "impl-thread", "WI-0204")
    db = _db(tmp_path)
    try:
        _insert_work_item(db, "WI-0204", ["impl-thread", "blocking-thread"])
    finally:
        db.close()

    summary = module.reconcile(project_root=tmp_path, apply=True)

    db = _db(tmp_path)
    try:
        row = db.get_work_item("WI-0204")
        assert row is not None
        assert row["resolution_status"] == "open"
        assert summary["resolved_ids"] == []
        assert summary["candidates"][0]["reason"] == "linked_bridge_not_verified"
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


def test_path_and_plain_slug_references_normalize_to_one_document(
    tmp_path: Path,
) -> None:
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


def test_apply_revalidates_latest_bridge_status_before_resolution(tmp_path: Path, monkeypatch) -> None:
    module = _load_module()
    _write_index(tmp_path, {"thread-a": "VERIFIED"})
    _write_parent_evidence(tmp_path, "thread-a", "WI-0015")
    db = _db(tmp_path)
    try:
        _insert_work_item(db, "WI-0015", ["thread-a"])
    finally:
        db.close()

    original_classify_work_item = module.classify_work_item
    classify_calls = {"count": 0}

    def classify_and_drift(*args, **kwargs):  # type: ignore[no-untyped-def]
        result = original_classify_work_item(*args, **kwargs)
        classify_calls["count"] += 1
        if classify_calls["count"] == 1:
            (tmp_path / "bridge" / "thread-a-003.md").write_text(
                "DEFERRED\n\n# thread-a\n\nOwner parked the thread after prior VERIFIED evidence.\n",
                encoding="utf-8",
            )
        return result

    monkeypatch.setattr(module, "classify_work_item", classify_and_drift)

    summary = module.reconcile(project_root=tmp_path, apply=True)

    db = _db(tmp_path)
    try:
        row = db.get_work_item("WI-0015")
        assert row is not None
        assert row["resolution_status"] == "open"
        assert row["stage"] == "backlogged"
        assert classify_calls["count"] >= 2
        assert summary["resolved_ids"] == []
        assert summary["would_resolve_ids"] == []
        candidate = summary["candidates"][0]
        assert candidate["action"] == "skip"
        assert candidate["reason"] == "linked_bridge_not_verified"
        assert candidate["bridge_statuses"] == {"thread-a": "DEFERRED"}
    finally:
        db.close()


def test_contextual_verified_bridge_reference_without_parent_evidence_is_skipped(
    tmp_path: Path,
) -> None:
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


def test_related_deliberation_bridge_provenance_is_not_an_implementation_link(
    tmp_path: Path,
) -> None:
    module = _load_module()
    _write_index(tmp_path, {"thread-a": "VERIFIED"})
    db = _db(tmp_path)
    try:
        db.insert_work_item(
            "WI-0016",
            "WI-0016 title",
            "hygiene",
            "backlog",
            "open",
            "test",
            "seed bridge advisory provenance",
            stage="backlogged",
            related_deliberation_ids="thread-a",
            related_bridge_threads=None,
        )
    finally:
        db.close()

    summary = module.reconcile(project_root=tmp_path, apply=True)

    db = _db(tmp_path)
    try:
        row = db.get_work_item("WI-0016")
        assert row is not None
        assert row["resolution_status"] == "open"
        assert summary["resolved_ids"] == []
        assert summary["candidate_count"] == 0
    finally:
        db.close()


def test_repair_overbroad_resolution_reopens_previous_nonterminal_version(
    tmp_path: Path,
) -> None:
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


def test_repair_overbroad_keeps_strict_evidence_resolution_closed(
    tmp_path: Path,
) -> None:
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
    path.write_text(
        path.read_text(encoding="utf-8") + "\nSee WI-0200 for related context.\n",
        encoding="utf-8",
    )

    bridge_statuses = module.collect_latest_bridge_statuses(tmp_path)
    index = module.build_work_item_bridge_links(tmp_path, bridge_statuses)

    assert index == {"WI-0100": ["thread-a"]}
    assert "WI-0200" not in index


def test_derives_link_from_bridge_work_item_metadata_resolves_unlinked_wi(
    tmp_path: Path,
) -> None:
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
    path.write_text(
        path.read_text(encoding="utf-8") + "\nThis work supports WI-0012 indirectly.\n",
        encoding="utf-8",
    )
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


def test_derived_link_with_unverified_sibling_thread_not_resolved(
    tmp_path: Path,
) -> None:
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


def test_classify_work_item_without_derived_links_is_byte_identical(
    tmp_path: Path,
) -> None:
    module = _load_module()
    _write_index(tmp_path, {"thread-a": "VERIFIED"})
    _write_parent_evidence(tmp_path, "thread-a", "WI-0014")
    bridge_statuses = module.collect_latest_bridge_statuses(tmp_path)
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
    codex_runner = (REPO_ROOT / ".codex" / "gtkb-hooks" / "run_py_no_window.py").read_text(encoding="utf-8")

    claude_text = json.dumps(claude)
    codex_text = json.dumps(codex)

    assert "scripts/bridge_verified_backlog_reconciler.py" in claude_text
    assert "--batch stop" in codex_text
    assert "scripts/bridge_verified_backlog_reconciler.py" in codex_runner
    assert "--apply --quiet" in claude_text
    assert '"--apply"' in codex_runner
    assert '"--quiet"' in codex_runner


# --- WI-4704: umbrella auto-closure + parent-evidence relaxation -------------


def test_bridge_thread_files_excludes_child_and_prefix_sibling_files(
    tmp_path: Path,
) -> None:
    """WI-4704 GO Condition 1: parent enumeration matches only ``<slug>-NNN.md``."""

    module = _load_module()
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir(parents=True, exist_ok=True)
    (bridge_dir / "thread-001.md").write_text("NEW\n", encoding="utf-8")
    (bridge_dir / "thread-002.md").write_text("VERIFIED\n", encoding="utf-8")
    (bridge_dir / "thread-child-001.md").write_text("NEW\n", encoding="utf-8")
    (bridge_dir / "thread-extra-suffix.md").write_text("NEW\n", encoding="utf-8")

    files = module._bridge_thread_files(tmp_path, "thread")

    assert sorted(p.name for p in files) == ["thread-001.md", "thread-002.md"]


def test_umbrella_parent_go_resolves_when_all_children_verified_and_declare_wi(
    tmp_path: Path,
) -> None:
    """WI-4704 Class 1 positive: GO umbrella with all children VERIFIED + declaring child."""

    module = _load_module()
    _write_index(
        tmp_path,
        {
            "umbrella": "GO",
            "umbrella-slice-1": "VERIFIED",
            "umbrella-slice-2": "VERIFIED",
        },
    )
    _write_work_item_metadata(tmp_path, "umbrella-slice-1", "WI-0101")
    db = _db(tmp_path)
    try:
        _insert_work_item(db, "WI-0101", ["umbrella"])
    finally:
        db.close()

    summary = module.reconcile(project_root=tmp_path, apply=True)

    db = _db(tmp_path)
    try:
        row = db.get_work_item("WI-0101")
        assert row is not None
        assert row["resolution_status"] == "resolved"
        assert summary["resolved_ids"] == ["WI-0101"]
        candidate = summary["candidates"][0]
        assert candidate["reason"] == "umbrella_children_all_verified"
        # The umbrella parent's own status is NOT rewritten to VERIFIED.
        assert candidate["bridge_statuses"]["umbrella"] == "GO"
    finally:
        db.close()


def test_umbrella_not_resolved_when_a_child_is_not_verified(tmp_path: Path) -> None:
    """WI-4704 Class 1 negative: a non-VERIFIED child blocks umbrella closure."""

    module = _load_module()
    _write_index(
        tmp_path,
        {"umbrella": "GO", "umbrella-slice-1": "VERIFIED", "umbrella-slice-2": "GO"},
    )
    _write_work_item_metadata(tmp_path, "umbrella-slice-1", "WI-0102")
    db = _db(tmp_path)
    try:
        _insert_work_item(db, "WI-0102", ["umbrella"])
    finally:
        db.close()

    summary = module.reconcile(project_root=tmp_path, apply=True)

    db = _db(tmp_path)
    try:
        row = db.get_work_item("WI-0102")
        assert row is not None
        assert row["resolution_status"] == "open"
        assert summary["resolved_ids"] == []
        assert summary["candidates"][0]["reason"] == "linked_bridge_not_verified"
    finally:
        db.close()


def test_umbrella_not_resolved_when_no_child_declares_work_item(tmp_path: Path) -> None:
    """WI-4704 Class 1 negative: all-VERIFIED children that never declare the WI do not satisfy."""

    module = _load_module()
    _write_index(
        tmp_path,
        {
            "umbrella": "GO",
            "umbrella-slice-1": "VERIFIED",
            "umbrella-slice-2": "VERIFIED",
        },
    )
    db = _db(tmp_path)
    try:
        _insert_work_item(db, "WI-0103", ["umbrella"])
    finally:
        db.close()

    summary = module.reconcile(project_root=tmp_path, apply=True)

    db = _db(tmp_path)
    try:
        row = db.get_work_item("WI-0103")
        assert row is not None
        assert row["resolution_status"] == "open"
        assert summary["resolved_ids"] == []
        assert summary["candidates"][0]["reason"] == "linked_bridge_not_verified"
    finally:
        db.close()


def test_parent_evidence_relaxation_resolves_when_one_verified_link_declares_wi(
    tmp_path: Path,
) -> None:
    """WI-4704 Class 2 positive: a canonical declaration on one VERIFIED link resolves."""

    module = _load_module()
    _write_index(tmp_path, {"thread-a": "VERIFIED", "thread-b": "VERIFIED"})
    _write_work_item_metadata(tmp_path, "thread-a", "WI-0104")
    db = _db(tmp_path)
    try:
        _insert_work_item(db, "WI-0104", ["thread-a", "thread-b"])
    finally:
        db.close()

    summary = module.reconcile(project_root=tmp_path, apply=True)

    db = _db(tmp_path)
    try:
        row = db.get_work_item("WI-0104")
        assert row is not None
        assert row["resolution_status"] == "resolved"
        assert summary["resolved_ids"] == ["WI-0104"]
        assert summary["candidates"][0]["reason"] == "parent_evidence_canonical_relaxed"
    finally:
        db.close()


def test_parent_evidence_relaxation_rejects_prose_only_declaration(
    tmp_path: Path,
) -> None:
    """WI-4704 Class 2 negative: a prose WI mention never satisfies the canonical floor."""

    module = _load_module()
    _write_index(tmp_path, {"thread-a": "VERIFIED", "thread-b": "VERIFIED"})
    path_a = tmp_path / "bridge" / "thread-a-002.md"
    path_a.write_text(
        path_a.read_text(encoding="utf-8") + "\nThis thread supports WI-0105 broadly.\n",
        encoding="utf-8",
    )
    db = _db(tmp_path)
    try:
        _insert_work_item(db, "WI-0105", ["thread-a", "thread-b"])
    finally:
        db.close()

    summary = module.reconcile(project_root=tmp_path, apply=True)

    db = _db(tmp_path)
    try:
        row = db.get_work_item("WI-0105")
        assert row is not None
        assert row["resolution_status"] == "open"
        assert summary["resolved_ids"] == []
        assert summary["candidates"][0]["reason"] == "missing_parent_evidence"
    finally:
        db.close()


def test_reverse_link_construction_scans_bridge_dir_once_at_scale(tmp_path: Path, monkeypatch) -> None:
    """WI-4704 F1 scale guard: reverse-link construction must not glob the bridge dir per slug.

    Per-slug ``glob`` made the live dry-run O(slugs x dir) and time out at ~1099
    bridge docs. The one-pass file index scans the bridge directory a bounded
    number of times regardless of slug count; this test fails on the old shape.
    """

    module = _load_module()
    statuses = {f"thread-{i:03d}": "VERIFIED" for i in range(25)}
    _write_index(tmp_path, statuses)
    for i in range(25):
        _write_work_item_metadata(tmp_path, f"thread-{i:03d}", f"WI-95{i:02d}")
    bridge_statuses = module.collect_latest_bridge_statuses(tmp_path)

    bridge_dir = tmp_path / "bridge"
    real_glob = Path.glob
    scan_count = {"n": 0}

    def counting_glob(self, pattern):  # type: ignore[no-untyped-def]
        if self == bridge_dir:
            scan_count["n"] += 1
        return real_glob(self, pattern)

    monkeypatch.setattr(Path, "glob", counting_glob)
    derived = module.build_work_item_bridge_links(tmp_path, bridge_statuses)

    assert scan_count["n"] <= 2, f"bridge dir scanned {scan_count['n']}x; expected one-pass (<=2), not per-slug"
    assert len(derived) == 25


def test_verified_on_no_action_is_not_implementation_closure(tmp_path: Path) -> None:
    target = tmp_path / "scripts" / "impl.py"
    target.parent.mkdir(parents=True)
    target.write_text("VALUE = 1\n", encoding="utf-8")
    _write_strict_thread(
        tmp_path,
        "WI-11498-A",
        target_paths=["scripts/impl.py"],
        response_status="NO-ACTION",
    )

    row = _classify_strict_thread(tmp_path, "WI-11498-A")

    assert row["action"] == "skip"
    assert row["reason"] == "no_action_verified"
    assert row["closure_reason"] == "no_action_verified"


def test_malformed_approved_target_metadata_fails_closed(tmp_path: Path) -> None:
    _write_strict_thread(
        tmp_path,
        "WI-11498-B",
        target_paths='["scripts/impl.py"',
    )

    row = _classify_strict_thread(tmp_path, "WI-11498-B")

    assert row["action"] == "skip"
    assert row["reason"] == "malformed_target_metadata"
    evidence = row["verified_closure_evidence"]["strict-thread"]
    assert evidence["detail"] == "target_paths_not_json"


def test_untracked_terminal_verdict_lacks_commit_coverage(tmp_path: Path) -> None:
    _init_git(tmp_path)
    target = tmp_path / "scripts" / "impl.py"
    target.parent.mkdir(parents=True)
    target.write_text("VALUE = 1\n", encoding="utf-8")
    _write_strict_thread(
        tmp_path,
        "WI-11498-C",
        target_paths=["scripts/impl.py"],
        include_verdict=False,
    )
    _git(tmp_path, "add", "scripts/impl.py", "bridge")
    _git(tmp_path, "commit", "-q", "-m", "implementation without verdict")
    _write_strict_thread(tmp_path, "WI-11498-C", target_paths=["scripts/impl.py"])

    row = _classify_strict_thread(tmp_path, "WI-11498-C")

    assert row["action"] == "skip"
    assert row["reason"] == "missing_implementation_commit_coverage"
    evidence = row["verified_closure_evidence"]["strict-thread"]
    assert evidence["commit_coverage"]["verdict_state"] == "uncommitted_or_untracked"


def test_terminal_commit_with_ancestor_committed_target_closes(tmp_path: Path) -> None:
    """Implementation in an earlier commit than the verdict now closes (WI-6280).

    This test previously asserted the same-commit rule (skip +
    missing_implementation_commit_coverage). That rule was superseded by owner
    decision 2026-08-14 "Coverage rule", which settled a conflict between the
    file-bridge-protocol VERIFIED commit-finalization gate (same commit) and the
    owner-authorized auto-finalization sweep (verdict-only, implementation
    committed separately). The split-commit shape below is exactly what the
    sweep produces, and it must close.

    Landed by bridge/gtkb-wi6280-verified-closure-ancestor-coverage (GO at -004).
    """
    _init_git(tmp_path)
    target = tmp_path / "scripts" / "impl.py"
    target.parent.mkdir(parents=True)
    target.write_text("VALUE = 1\n", encoding="utf-8")
    _git(tmp_path, "add", "scripts/impl.py")
    _git(tmp_path, "commit", "-q", "-m", "implementation only")
    _write_strict_thread(tmp_path, "WI-11498-D", target_paths=["scripts/impl.py"])
    _git(tmp_path, "add", "bridge")
    _git(tmp_path, "commit", "-q", "-m", "terminal bridge only")

    row = _classify_strict_thread(tmp_path, "WI-11498-D")

    assert row["action"] == "resolve"
    assert row["closure_reason"] == "genuinely_closable"
    evidence = row["verified_closure_evidence"]["strict-thread"]
    assert evidence["commit_coverage"]["missing_paths"] == []


def test_focused_commit_with_verdict_and_all_targets_is_genuinely_closable(
    tmp_path: Path,
) -> None:
    _init_git(tmp_path)
    target = tmp_path / "scripts" / "impl.py"
    target.parent.mkdir(parents=True)
    target.write_text("VALUE = 1\n", encoding="utf-8")
    _write_strict_thread(tmp_path, "WI-11498-E", target_paths=["scripts/impl.py"])
    _git(tmp_path, "add", "scripts/impl.py", "bridge")
    _git(tmp_path, "commit", "-q", "-m", "focused implementation and verdict")

    row = _classify_strict_thread(tmp_path, "WI-11498-E")

    assert row["action"] == "resolve"
    assert row["closure_reason"] == "genuinely_closable"
    evidence = row["verified_closure_evidence"]["strict-thread"]
    assert evidence["mode"] == "focused_commit"
    assert evidence["commit_coverage"]["missing_paths"] == []


def test_reconcile_reuses_batched_git_provenance_for_many_verified_threads(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = _load_module()
    _init_git(tmp_path)
    expected_ids: list[str] = []
    db = _db(tmp_path)
    try:
        for index in range(8):
            item_id = f"WI-5397-{index:02d}"
            slug = f"strict-thread-{index:02d}"
            target_rel_path = f"scripts/impl_{index}.py"
            target = tmp_path / target_rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(f"VALUE = {index}\n", encoding="utf-8")
            _write_strict_thread(tmp_path, item_id, target_paths=[target_rel_path], slug=slug)
            _insert_work_item(db, item_id, [slug])
            expected_ids.append(item_id)
    finally:
        db.close()
    _git(tmp_path, "add", "scripts", "bridge")
    _git(tmp_path, "commit", "-q", "-m", "focused implementations and verdicts")

    calls: list[tuple[str, ...]] = []
    original_run_git = module._run_git

    def counting_run_git(project_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        calls.append(args)
        return original_run_git(project_root, *args)

    monkeypatch.setattr(module, "_run_git", counting_run_git)

    summary = module.reconcile(project_root=tmp_path, apply=False)

    assert sorted(summary["would_resolve_ids"]) == expected_ids
    assert [args for args in calls if args[:1] == ("status",)] == [
        ("status", "--porcelain=v1", "-z", "--untracked-files=all", "--")
    ]
    assert [args for args in calls if args[:1] == ("ls-files",)] == [("ls-files", "-z", "--")]
    assert [args for args in calls if args[:1] == ("log",)] == [("log", "--format=commit:%H", "--name-only", "--")]
    assert [args for args in calls if args[:1] == ("diff-tree",)] == []


def test_owner_by_reference_waiver_preserves_committed_verdict_closure(
    tmp_path: Path,
) -> None:
    _init_git(tmp_path)
    target = tmp_path / "scripts" / "impl.py"
    target.parent.mkdir(parents=True)
    target.write_text("VALUE = 1\n", encoding="utf-8")
    _git(tmp_path, "add", "scripts/impl.py")
    _git(tmp_path, "commit", "-q", "-m", "implementation by reference")
    _write_strict_thread(
        tmp_path,
        "WI-11498-F",
        target_paths=["scripts/impl.py"],
        waiver=True,
    )
    _git(tmp_path, "add", "bridge")
    _git(tmp_path, "commit", "-q", "-m", "waived terminal bridge")

    row = _classify_strict_thread(tmp_path, "WI-11498-F")

    assert row["action"] == "resolve"
    assert row["closure_reason"] == "genuinely_closable"
    evidence = row["verified_closure_evidence"]["strict-thread"]
    assert evidence["mode"] == "by_reference_waiver"


def test_waiver_reference_outside_report_does_not_bypass_commit_coverage(
    tmp_path: Path,
) -> None:
    _init_git(tmp_path)
    # Vehicle changed by WI-6280: this test's subject is waiver SCOPING, not the
    # same-commit rule. It previously induced a coverage failure by committing
    # the implementation before the verdict -- a shape that now legitimately
    # closes. The target below is never committed at all, so coverage still
    # fails for an unrelated reason and the waiver-scoping property is asserted
    # exactly as before.
    paths = _write_strict_thread(tmp_path, "WI-11498-G", target_paths=["scripts/never_committed.py"])
    with paths["proposal"].open("a", encoding="utf-8") as handle:
        handle.write(
            "\n\n## Owner Decisions / Input\nA DELIB-TEST-BY-REFERENCE-WAIVER exists for an unrelated sibling thread.\n"
        )
    _git(tmp_path, "add", "bridge")
    _git(tmp_path, "commit", "-q", "-m", "terminal bridge without report waiver")

    row = _classify_strict_thread(tmp_path, "WI-11498-G")

    assert row["action"] == "skip"
    assert row["reason"] == "missing_implementation_commit_coverage"
    evidence = row["verified_closure_evidence"]["strict-thread"]
    assert "mode" not in evidence


def _append_report_section(report_path: Path, section: str) -> None:
    report_path.write_text(report_path.read_text(encoding="utf-8") + section, encoding="utf-8")


def test_owner_decisions_heading_does_not_activate_by_reference_waiver(
    tmp_path: Path,
) -> None:
    """WI-5426: Owner Decisions / Input prose is not a by-reference waiver heading."""
    _init_git(tmp_path)
    paths = _write_strict_thread(tmp_path, "WI-5426-OD", target_paths=["scripts/never_committed.py"])
    _append_report_section(
        paths["report"],
        "\n\n## Owner Decisions / Input\nOwner-approved by-reference waiver: DELIB-TEST-BY-REFERENCE-001.\n",
    )
    _git(tmp_path, "add", "bridge")
    _git(tmp_path, "commit", "-q", "-m", "owner-decisions heading is not a waiver")

    row = _classify_strict_thread(tmp_path, "WI-5426-OD")

    assert row["action"] == "skip"
    evidence = row["verified_closure_evidence"]["strict-thread"]
    assert evidence.get("mode") != "by_reference_waiver"


def test_negated_by_reference_waiver_is_rejected(tmp_path: Path) -> None:
    """WI-5426: negated waiver prose under the dedicated heading does not close."""
    _init_git(tmp_path)
    paths = _write_strict_thread(tmp_path, "WI-5426-NEG", target_paths=["scripts/never_committed.py"])
    _append_report_section(
        paths["report"],
        "\n\n## By-Reference Finalization Waiver\nDo not grant a by-reference waiver. Missing DELIB reference.\n",
    )
    _git(tmp_path, "add", "bridge")
    _git(tmp_path, "commit", "-q", "-m", "negated waiver")

    row = _classify_strict_thread(tmp_path, "WI-5426-NEG")

    assert row["action"] == "skip"
    evidence = row["verified_closure_evidence"]["strict-thread"]
    assert evidence.get("mode") != "by_reference_waiver"


def test_duplicate_by_reference_waiver_declarations_are_rejected(
    tmp_path: Path,
) -> None:
    """WI-5426: duplicate affirmative declarations fail closed."""
    _init_git(tmp_path)
    paths = _write_strict_thread(tmp_path, "WI-5426-DUP", target_paths=["scripts/never_committed.py"])
    _append_report_section(
        paths["report"],
        "\n\n## By-Reference Finalization Waiver\n"
        "Owner-approved by-reference waiver: DELIB-TEST-BY-REFERENCE-001.\n"
        "Owner-approved by-reference waiver: DELIB-TEST-BY-REFERENCE-002.\n",
    )
    _git(tmp_path, "add", "bridge")
    _git(tmp_path, "commit", "-q", "-m", "duplicate waiver declarations")

    row = _classify_strict_thread(tmp_path, "WI-5426-DUP")

    assert row["action"] == "skip"
    evidence = row["verified_closure_evidence"]["strict-thread"]
    assert evidence.get("mode") != "by_reference_waiver"


def test_malformed_by_reference_waiver_declaration_is_rejected(tmp_path: Path) -> None:
    """WI-5426: a dedicated heading without the anchored DELIB line fails closed."""
    _init_git(tmp_path)
    paths = _write_strict_thread(tmp_path, "WI-5426-MAL", target_paths=["scripts/never_committed.py"])
    _append_report_section(
        paths["report"],
        "\n\n## By-Reference Finalization Waiver\nOwner approved a by-reference waiver DELIB-TEST-BY-REFERENCE-001\n",
    )
    _git(tmp_path, "add", "bridge")
    _git(tmp_path, "commit", "-q", "-m", "malformed waiver")

    row = _classify_strict_thread(tmp_path, "WI-5426-MAL")

    assert row["action"] == "skip"
    evidence = row["verified_closure_evidence"]["strict-thread"]
    assert evidence.get("mode") != "by_reference_waiver"
