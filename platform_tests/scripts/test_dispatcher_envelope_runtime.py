"""Focused tests for dispatch-envelope rules and scheduler behavior."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.dispatcher.rules_loader import DispatchRuleError, load_rules, validate_rules
from groundtruth_kb.dispatcher.scheduler import tick


def test_empty_dispatcher_registry_loads() -> None:
    registry = Path("config/dispatcher/rules.toml")
    rules = load_rules(registry)
    assert rules == []


def test_dispatch_rules_require_activity_gate() -> None:
    with pytest.raises(DispatchRuleError, match="activity_gate"):
        validate_rules(
            {
                "rules": [
                    {
                        "id": "rule-1",
                        "trigger": "manual",
                        "target": "codex",
                        "payload": {},
                    }
                ]
            }
        )
    with pytest.raises(DispatchRuleError, match="non-empty"):
        validate_rules(
            {
                "rules": [
                    {
                        "id": "rule-1",
                        "trigger": "manual",
                        "target": "codex",
                        "activity_gate": "  ",
                        "payload": {},
                    }
                ]
            }
        )


def test_dispatch_rules_require_unique_ids_and_warn_on_bare_envelope() -> None:
    with pytest.raises(DispatchRuleError, match="duplicates"):
        validate_rules(
            {
                "rules": [
                    {
                        "id": "rule-1",
                        "trigger": "manual",
                        "target": "codex",
                        "activity_gate": "working_tree_dirty",
                        "payload": {},
                    },
                    {
                        "id": "rule-1",
                        "trigger": "manual",
                        "target": "codex",
                        "activity_gate": "working_tree_dirty",
                        "payload": {},
                    },
                ]
            }
        )

    with pytest.warns(UserWarning, match="bare 'envelope'"):
        rules = validate_rules(
            {
                "rules": [
                    {
                        "id": "legacy-name",
                        "trigger": "manual",
                        "target": "codex",
                        "activity_gate": "working_tree_dirty",
                        "payload": {"template": "legacy envelope wording"},
                    }
                ]
            }
        )
    assert rules[0].id == "legacy-name"


def test_dispatch_scheduler_logs_dry_run_event(tmp_path: Path) -> None:
    rules_path = tmp_path / "rules.toml"
    rules_path.write_text(
        """
[[rules]]
id = "bridge-actionable"
trigger = "bridge"
target = "codex"
activity_gate = "bridge_actionable_count > 0"
persist = true

[rules.payload]
kind = "review"
""".lstrip(),
        encoding="utf-8",
    )
    bridge = tmp_path / "bridge"
    bridge.mkdir()
    (bridge / "INDEX.md").write_text("Document: demo\nNEW: bridge/demo-001.md\n", encoding="utf-8")
    (bridge / "demo-001.md").write_text("NEW\n", encoding="utf-8")

    state = tick(tmp_path, rules_path=rules_path, dry_run=True)

    assert state["eligible_count"] == 1
    state_file = tmp_path / ".gtkb-state" / "dispatcher" / "state.json"
    log_file = tmp_path / ".gtkb-state" / "dispatcher" / "log.jsonl"
    assert json.loads(state_file.read_text(encoding="utf-8"))["rule_count"] == 1
    assert json.loads(log_file.read_text(encoding="utf-8").splitlines()[0])["gate_passed"] is True
    assert not (tmp_path / "groundtruth.db").exists()


def test_dispatch_scheduler_persists_execute_mode_event(tmp_path: Path) -> None:
    rules_path = tmp_path / "rules.toml"
    rules_path.write_text(
        """
[[rules]]
id = "bridge-actionable"
trigger = "bridge"
target = "codex"
activity_gate = "bridge_actionable_count > 0"
persist = true

[rules.payload]
kind = "review"
""".lstrip(),
        encoding="utf-8",
    )
    bridge = tmp_path / "bridge"
    bridge.mkdir()
    (bridge / "INDEX.md").write_text("Document: demo\nNEW: bridge/demo-001.md\n", encoding="utf-8")
    (bridge / "demo-001.md").write_text("NEW\n", encoding="utf-8")

    state = tick(tmp_path, rules_path=rules_path, dry_run=False)

    assert state["persisted_count"] == 1
    assert state["events"][0]["dispatch_event_id"].startswith("dispatch-bridge-actionable-")
    conn = sqlite3.connect(tmp_path / "groundtruth.db")
    try:
        row = conn.execute(
            "SELECT rule_id, target_kind, target_value, gate_result, spawn_outcome FROM dispatch_events"
        ).fetchone()
    finally:
        conn.close()
    assert row == ("bridge-actionable", "rule_target", "codex", "pass", "eligible")


def test_dispatch_scheduler_path_gate_runs_in_subprocess(tmp_path: Path) -> None:
    module_dir = tmp_path / "groundtruth-kb" / "src"
    module_dir.mkdir(parents=True)
    (module_dir / "demo_predicate.py").write_text(
        "from pathlib import Path\n\ndef has_marker(root: Path) -> bool:\n    return (root / 'marker.txt').is_file()\n",
        encoding="utf-8",
    )
    (tmp_path / "marker.txt").write_text("ready", encoding="utf-8")
    rules_path = tmp_path / "rules.toml"
    rules_path.write_text(
        """
[[rules]]
id = "path-gate"
trigger = "manual"
target = "codex"
activity_gate = "path:demo_predicate:has_marker"

[rules.payload]
kind = "demo"
""".lstrip(),
        encoding="utf-8",
    )

    state = tick(tmp_path, rules_path=rules_path, dry_run=True)

    assert state["eligible_count"] == 1


def test_dispatch_events_schema_is_created(tmp_path: Path) -> None:
    db = KnowledgeDB(db_path=tmp_path / "groundtruth.db")
    db.insert_dispatch_event(
        event_id="event-1",
        rule_id="rule-1",
        trigger="manual",
        target="codex",
        activity_gate="working_tree_dirty",
        gate_passed=False,
        payload={"hello": "world"},
    )
    conn = sqlite3.connect(tmp_path / "groundtruth.db")
    try:
        row = conn.execute("SELECT name FROM sqlite_master WHERE name = 'dispatch_events'").fetchone()
        columns = {item[1] for item in conn.execute("PRAGMA table_info(dispatch_events)").fetchall()}
        count = conn.execute("SELECT COUNT(*) FROM dispatch_events").fetchone()[0]
    finally:
        conn.close()
    assert row is not None
    assert {
        "id",
        "version",
        "rule_id",
        "target_kind",
        "target_value",
        "trigger_at",
        "gate_result",
        "payload_template_id",
        "spawn_outcome",
        "spawn_pid",
        "spawn_exit_status",
        "changed_by",
        "changed_at",
        "change_reason",
    } <= columns
    assert count == 1
