from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402

APP_REGISTRY = REPO_ROOT / "applications" / "Agent_Red" / ".gtkb-app-isolation.json"
CLOSEOUT_PROJECT_ID = "PROJECT-GTKB-ISOLATION-PROGRAM-CLOSEOUT"
READINESS_PROJECT_ID = "PROJECT-GTKB-AGENT-RED-READINESS"
BRIDGE_THREAD = "gtkb-ar-readiness-phase-1-0-status-reconciliation"


def _registry() -> dict:
    return json.loads(APP_REGISTRY.read_text(encoding="utf-8"))


def _artifact_entry(name: str) -> dict:
    entries = _registry().get("top_level_artifacts")
    assert isinstance(entries, list) and entries
    matches = [entry for entry in entries if entry.get("name") == name]
    assert len(matches) == 1
    return matches[0]


def test_claude_registry_entry_reconciles_fresh_content_claim() -> None:
    entry = _artifact_entry(".claude")
    justification = entry["justification"]

    assert entry["type"] == "DIR"
    assert entry["bucket"] == "B"
    assert entry["tool"] == "Claude Code"
    assert "minimal placeholder" not in justification
    assert "15 files / 596 freshly measured lines" in justification
    assert "code-reviewer and security-analyzer agents" in justification
    assert "deploy/run-tests/seed-tenant skills" in justification
    assert "no GT-KB platform content imported" in justification


def test_agent_red_registry_schema_and_bucket_b_contract_remain_valid() -> None:
    registry = _registry()

    assert registry["application"] == "Agent_Red"
    assert registry["schema_version"]
    assert registry["last_updated"] == "2026-06-19"

    entries = registry["top_level_artifacts"]
    for entry in entries:
        assert entry.get("name")
        assert entry.get("type")
        assert entry.get("bucket")
        if entry["bucket"] == "A":
            assert entry.get("purpose")
        elif entry["bucket"] == "B":
            assert entry.get("tool")
            assert entry.get("justification")
        else:
            raise AssertionError(f"unexpected app-root bucket {entry['bucket']!r}")


def test_codex_registry_entry_remains_minimal_and_unchanged() -> None:
    entry = _artifact_entry(".codex")

    assert entry == {
        "name": ".codex",
        "type": "DIR",
        "bucket": "B",
        "tool": "Codex CLI",
        "justification": (
            "CWD-rooted config discovery for Agent-Red-scoped Codex sessions; "
            "minimal placeholder per Codex GO sub-slice 1 condition 2 "
            "(no GT-KB platform content imported)"
        ),
    }


def test_closeout_project_records_unbuilt_slices_and_readiness_handoff() -> None:
    db = KnowledgeDB(REPO_ROOT / "groundtruth.db")
    try:
        project = db.get_project(CLOSEOUT_PROJECT_ID)
        links = db.list_project_artifact_links(CLOSEOUT_PROJECT_ID)
    finally:
        db.close()

    assert project is not None
    notes = project["notes"] or ""
    assert "GTKB-ISOLATION-019 closeout overclaimed completion" in notes
    assert "sub-slice 5 (app-root minimization validator) remains unbuilt" in notes
    assert "sub-slice 6 (ADR/DCL into MemBase) remains unbuilt" in notes
    assert READINESS_PROJECT_ID in notes
    for work_item_id in ("WI-4654", "WI-4655", "WI-4656", "WI-4657"):
        assert work_item_id in notes

    assert any(
        link["artifact_type"] == "bridge_thread"
        and link["artifact_ref"] == BRIDGE_THREAD
        and link["relationship"] == "reconciles"
        for link in links
    )
