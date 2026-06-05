"""Activity-gated dispatch-envelope scheduler."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from groundtruth_kb.dispatcher.rules_loader import DispatchRule, default_rules_path, load_rules


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _bridge_actionable_count(project_root: Path) -> int:
    index = project_root / "bridge" / "INDEX.md"
    try:
        text = index.read_text(encoding="utf-8")
    except OSError:
        return 0
    return sum(1 for line in text.splitlines() if line.startswith(("NEW:", "REVISED:")))


def _working_tree_dirty(project_root: Path) -> bool:
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return False
    return bool(result.stdout.strip())


def _path_gate(project_root: Path, dotted: str) -> bool:
    module_name, _, attr = dotted.partition(":")
    if not module_name or not attr:
        return False
    env = os.environ.copy()
    src_path = str(project_root / "groundtruth-kb" / "src")
    env["PYTHONPATH"] = src_path + os.pathsep + env.get("PYTHONPATH", "")
    code = (
        "import importlib, pathlib, sys; "
        "module_name, attr, root = sys.argv[1:4]; "
        "candidate = getattr(importlib.import_module(module_name), attr); "
        "raise SystemExit(0 if bool(candidate(pathlib.Path(root))) else 1)"
    )
    try:
        result = subprocess.run(
            [sys.executable, "-c", code, module_name, attr, str(project_root)],
            cwd=project_root,
            env=env,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


def activity_gate_passes(project_root: Path, gate: str) -> bool:
    gate = gate.strip()
    if gate == "bridge_actionable_count > 0":
        return _bridge_actionable_count(project_root) > 0
    if gate == "working_tree_dirty":
        return _working_tree_dirty(project_root)
    if gate.startswith("path:"):
        return _path_gate(project_root, gate.removeprefix("path:"))
    return False


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _append_jsonl(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(data, sort_keys=True) + "\n")


def _dispatch_event_id(rule: DispatchRule, trigger_at: str) -> str:
    safe_time = trigger_at.replace(":", "-")
    return f"dispatch-{rule.id}-{safe_time}"


def _event_for_rule(rule: DispatchRule, *, gate_passed: bool, dry_run: bool, trigger_at: str) -> dict[str, Any]:
    gate_result = "pass" if gate_passed else "skip"
    return {
        "rule_id": rule.id,
        "trigger": rule.trigger,
        "target": rule.target,
        "target_kind": "rule_target",
        "activity_gate": rule.activity_gate,
        "gate_passed": gate_passed,
        "gate_result": gate_result,
        "trigger_at": trigger_at,
        "spawn_outcome": "dry_run" if dry_run else ("eligible" if gate_passed else "gate_skip"),
        "dry_run": dry_run,
        "persist": rule.persist,
        "payload": rule.payload,
    }


def _persist_events(project_root: Path, events: list[dict[str, Any]]) -> None:
    from groundtruth_kb.db import KnowledgeDB

    db = KnowledgeDB(project_root / "groundtruth.db")
    try:
        for event in events:
            if event["dry_run"] or not event["persist"] or not event["gate_passed"]:
                continue
            event_id = _dispatch_event_id(
                DispatchRule(
                    id=str(event["rule_id"]),
                    trigger=str(event["trigger"]),
                    target=str(event["target"]),
                    activity_gate=str(event["activity_gate"]),
                    payload=dict(event["payload"]),
                    persist=bool(event["persist"]),
                ),
                str(event["trigger_at"]),
            )
            row = db.insert_dispatch_event(
                event_id=event_id,
                rule_id=str(event["rule_id"]),
                target_kind=str(event["target_kind"]),
                target_value=str(event["target"]),
                trigger_at=str(event["trigger_at"]),
                gate_result=str(event["gate_result"]),
                payload_template_id=str(event["trigger"]),
                spawn_outcome=str(event["spawn_outcome"]),
                activity_gate=str(event["activity_gate"]),
                dry_run=False,
                payload=dict(event["payload"]),
            )
            if row:
                event["dispatch_event_id"] = row["id"]
                event["dispatch_event_version"] = row["version"]
    finally:
        db.close()


def tick(project_root: Path, *, rules_path: Path | None = None, dry_run: bool = True) -> dict[str, Any]:
    rules = load_rules(rules_path or default_rules_path(project_root))
    trigger_at = _now()
    events = [
        _event_for_rule(
            rule,
            gate_passed=activity_gate_passes(project_root, rule.activity_gate),
            dry_run=dry_run,
            trigger_at=trigger_at,
        )
        for rule in rules
    ]
    if not dry_run:
        _persist_events(project_root, events)
    state = {
        "dry_run": dry_run,
        "rule_count": len(rules),
        "eligible_count": sum(1 for event in events if event["gate_passed"]),
        "persisted_count": sum(1 for event in events if "dispatch_event_id" in event),
        "events": events,
    }
    state_path = project_root / ".gtkb-state" / "dispatcher" / "state.json"
    log_path = project_root / ".gtkb-state" / "dispatcher" / "log.jsonl"
    _write_json(state_path, state)
    for event in events:
        _append_jsonl(log_path, event)
    return state
