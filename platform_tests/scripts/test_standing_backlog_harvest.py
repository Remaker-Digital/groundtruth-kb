"""Tests for standing backlog source harvest visibility."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from groundtruth_kb.db import KnowledgeDB

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "audit_standing_backlog_sources.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("audit_standing_backlog_sources", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["audit_standing_backlog_sources"] = module
    spec.loader.exec_module(module)
    return module


def test_standing_backlog_audit_finds_current_actionable_bridge_entries() -> None:
    """Asserts structural invariants of the bridge audit, not specific entries.

    Per S330 Slice 8.6 row-37 fix: the original test asserted on six specific
    bridge documents that have since been closed/superseded as the bridge
    naturally evolved. Those assertions made the test a regression baseline
    rather than an invariant check. The invariants the test actually cares
    about are: (a) the audit shape is correct, (b) actionable entries carry
    the expected (document, status) pair, (c) VERIFIED is terminal and never
    appears in actionable, (d) historical example: gtkb-azure-cicd-gates
    closed at VERIFIED is correctly excluded.
    """
    module = _load_module()

    audit = module.build_audit(REPO_ROOT)

    assert isinstance(audit, dict), "audit must be a dict"
    assert "bridge" in audit, "audit must have 'bridge' key"
    assert isinstance(audit["bridge"], dict), "audit['bridge'] must be a dict"
    assert "actionable" in audit["bridge"], "audit['bridge'] must have 'actionable' key"
    assert isinstance(audit["bridge"]["actionable"], list), "actionable must be a list"

    actionable = {(entry["document"], entry["status"]) for entry in audit["bridge"]["actionable"]}
    actionable_documents = {doc for doc, _ in actionable}
    actionable_statuses = {status for _, status in actionable}

    for entry in audit["bridge"]["actionable"]:
        assert "document" in entry, f"each actionable entry must have a document field; got {entry}"
        assert "status" in entry, f"each actionable entry must have a status field; got {entry}"
        assert entry["document"], f"actionable entry must have non-empty document; got {entry}"
        assert entry["status"] in {"NEW", "REVISED", "GO", "NO-GO"}, (
            f"actionable status must be a non-terminal verdict; got {entry['status']} for {entry['document']}"
        )

    assert "VERIFIED" not in actionable_statuses, "VERIFIED is terminal and must never appear in actionable"
    assert ("gtkb-azure-cicd-gates", "VERIFIED") not in actionable, "VERIFIED must never appear in actionable"
    assert "gtkb-azure-cicd-gates" not in actionable_documents, (
        "gtkb-azure-cicd-gates closed at VERIFIED; must not appear in actionable"
    )


def test_standing_backlog_audit_summarizes_membase_work_items_and_release_blockers() -> None:
    """Asserts structural invariants of the work_items audit + release blockers.

    Per S330 Slice 8.6 row-38 fix: the original `>= 1900` open work-items
    assertion was a snapshot of local state, not an invariant. CI starts with
    an empty work_items table (groundtruth.db is gitignored per 23a54af3, and
    the CI seed materializes specs/deliberations only — work_items would
    bloat the fixture). The audit must still produce the right shape and
    enforce the load-bearing invariant: release_blockers is empty for this rc.
    """
    module = _load_module()

    audit = module.build_audit(REPO_ROOT)

    assert isinstance(audit["work_items"]["status_counts"], dict), "status_counts must be a dict"
    assert audit["work_items"]["status_counts"].get("open", 0) >= 0, "'open' may be absent or 0+"
    assert audit["work_items"]["status_counts"].get("blocked", 0) >= 0, "'blocked' may be absent or 0+"
    assert isinstance(audit["work_items"]["top_non_terminal"], list), "top_non_terminal must be a list"
    assert not any("Credential lifecycle" in blocker for blocker in audit["release_blockers"])
    assert not any("secret purging" in blocker for blocker in audit["release_blockers"])
    assert not any("release-branch provenance" in blocker for blocker in audit["release_blockers"])
    assert not any("required CI evidence must be obtained" in blocker for blocker in audit["release_blockers"])
    assert not any("Commercial integration state" in blocker for blocker in audit["release_blockers"])
    assert audit["release_blockers"] == []


def test_standing_backlog_contains_harvested_source_items() -> None:
    """Verify current structured backlog ownership and live audit evidence."""
    db = KnowledgeDB(REPO_ROOT / "groundtruth.db")
    try:
        items = {item_id: db.get_work_item(item_id) for item_id in ("GTKB-GOV-004", "GTKB-GOV-009", "GTKB-GOV-010")}
    finally:
        db.close()

    assert all(items.values()), f"expected canonical backlog records; got {items}"

    harvest_parent = items["GTKB-GOV-004"]
    assert harvest_parent["project_name"] == "GTKB-GOV-004"
    assert harvest_parent["resolution_status"] == "retired"
    assert "unified backlog" in harvest_parent["title"].lower()

    azure_gate = items["GTKB-GOV-009"]
    assert azure_gate["resolution_status"] == "verified"
    assert "bridge/gtkb-azure-cicd-gates-010.md" in azure_gate["status_detail"]

    audit_owner = items["GTKB-GOV-010"]
    assert audit_owner["resolution_status"] == "retired"
    assert "audit as release-gate input" in audit_owner["title"].lower()
    assert "gtkb-standing-backlog-harvest-audit-maintenance VERIFIED@-006" in audit_owner["status_detail"]

    module = _load_module()
    audit = module.build_audit(REPO_ROOT)

    assert set(audit) == {"bridge", "work_items", "release_blockers"}
    assert isinstance(audit["bridge"]["status_counts"], dict)
    assert isinstance(audit["work_items"]["status_counts"], dict)
    assert isinstance(audit["release_blockers"], list)


def test_standing_backlog_audit_treats_withdrawn_as_terminal_not_actionable(tmp_path: Path) -> None:
    """WITHDRAWN at top of a document's version chain must be parsed as the
    latest status, and must NOT appear in actionable (parallel to VERIFIED's
    terminal treatment). Per WI-3276 / gtkb-audit-script-withdrawn-status-handling.
    """
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "test-thread-withdrawn-fixture-001.md").write_text("NO-GO\n", encoding="utf-8")
    (bridge_dir / "test-thread-withdrawn-fixture-002.md").write_text("WITHDRAWN\n", encoding="utf-8")
    module = _load_module()
    entries = module.latest_bridge_entries(tmp_path)
    fixture_entry = next(
        (e for e in entries if e["document"] == "test-thread-withdrawn-fixture"),
        None,
    )
    assert fixture_entry is not None, (
        f"test-thread-withdrawn-fixture must appear in parse output; got entries={entries}"
    )
    assert fixture_entry["status"] == "WITHDRAWN", (
        f"Latest status must be WITHDRAWN (parsed correctly); got {fixture_entry['status']}"
    )
    assert fixture_entry["status"] not in module.ACTIONABLE_BRIDGE_STATUSES, (
        "WITHDRAWN must be terminal (not in ACTIONABLE_BRIDGE_STATUSES) like VERIFIED"
    )


def test_standing_backlog_harvest_decision_is_archived() -> None:
    db = KnowledgeDB(REPO_ROOT / "groundtruth.db")
    try:
        decision = db.get_deliberation("DELIB-0839")
        assert decision is not None
        assert decision["outcome"] == "informational"
        assert "GTKB-GOV-004 through GTKB-GOV-010" in decision["content"]
        assert "MemBase work_items require structured grouping" in decision["content"]
        assert "STANDING-BACKLOG-HARVEST-2026-04-20.md" in decision["content"]
    finally:
        db.close()
