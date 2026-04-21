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
    module = _load_module()

    audit = module.build_audit(REPO_ROOT)
    actionable = {
        (entry["document"], entry["status"])
        for entry in audit["bridge"]["actionable"]
    }

    assert ("gtkb-azure-cicd-gates", "GO") in actionable
    assert ("agent-red-bridge-dispatcher-deferral-enforcement", "GO") in actionable
    assert ("commercial-readiness-spec-1833-ready-propagation", "NO-GO") in actionable
    assert ("commercial-readiness-spec-1831-startup-wiring", "NO-GO") in actionable
    assert ("commercial-readiness-spec-verification", "NO-GO") in actionable
    assert ("agent-red-bridge-dispatcher-deferral-enforcement-implementation", "NO-GO") in actionable


def test_standing_backlog_audit_summarizes_membase_work_items_and_release_blockers() -> None:
    module = _load_module()

    audit = module.build_audit(REPO_ROOT)

    assert audit["work_items"]["status_counts"]["open"] >= 1900
    assert audit["work_items"]["status_counts"]["blocked"] >= 1
    assert any(item["priority"] == "P0" for item in audit["work_items"]["top_non_terminal"])
    assert "Production credentials exposed in the deleted generated manifest must be rotated." in audit["release_blockers"]
    assert not any("required CI evidence must be obtained" in blocker for blocker in audit["release_blockers"])
    assert (
        "Owner/project must decide the release-branch provenance policy for "
        "`main`/`develop`."
    ) in audit["release_blockers"]


def test_standing_backlog_contains_harvested_source_items() -> None:
    work_list = (REPO_ROOT / "memory" / "work_list.md").read_text(encoding="utf-8")
    disposition_report = (
        REPO_ROOT
        / "independent-progress-assessments"
        / "CODEX-INSIGHT-DROPBOX"
        / "STANDING-BACKLOG-BRIDGE-DISPOSITIONS-2026-04-20.md"
    ).read_text(encoding="utf-8")

    for item_id in (
        "GTKB-GOV-004",
        "GTKB-GOV-005",
        "GTKB-GOV-006",
        "GTKB-GOV-007",
        "GTKB-GOV-008",
        "GTKB-GOV-009",
        "GTKB-GOV-010",
    ):
        assert item_id in work_list

    assert "audit_standing_backlog_sources.py" in work_list
    assert "STANDING-BACKLOG-HARVEST-2026-04-20.md" in work_list
    assert "STANDING-BACKLOG-BRIDGE-DISPOSITIONS-2026-04-20.md" in work_list
    assert "GTKB-GOV-005 - DONE" in work_list
    assert "gtkb-azure-cicd-gates" in work_list
    assert "commercial-readiness-spec-1833-ready-propagation" in work_list
    assert "`gtkb-azure-cicd-gates` `GO`" in disposition_report
    assert "It is assigned to `GTKB-GOV-009`" in disposition_report
    assert "`agent-red-bridge-dispatcher-deferral-enforcement-implementation` `NO-GO`" in disposition_report
    assert "`commercial-readiness-spec-1831-startup-wiring` `NO-GO`" in disposition_report
    assert "`commercial-readiness-spec-verification` `NO-GO`" in disposition_report
    assert "`commercial-readiness-spec-1833-ready-propagation` `NO-GO`" in disposition_report
    assert "1994 open" in work_list


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
