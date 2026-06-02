"""Tests for scripts/bridge_reconciliation_correction_packet.py."""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path
from types import ModuleType

from click.testing import CliRunner
from groundtruth_kb.cli import main as cli_main

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "bridge_reconciliation_correction_packet.py"


def _load_module(
    path: Path = SCRIPT_PATH, name: str = "bridge_reconciliation_correction_packet_for_test"
) -> ModuleType:
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _write_config(root: Path) -> Path:
    scripts_dir = root / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(SCRIPT_PATH, scripts_dir / "bridge_reconciliation_correction_packet.py")
    config = root / "groundtruth.toml"
    config.write_text(
        "\n".join(
            [
                "[groundtruth]",
                'db_path = "./groundtruth.db"',
                'project_root = "."',
                'app_title = "test"',
                'brand_mark = "GT"',
                'brand_color = "#2563eb"',
            ]
        ),
        encoding="utf-8",
    )
    return config


def _audit_payload() -> dict[str, object]:
    return {
        "generated_at": "2026-06-02T00:00:00Z",
        "bridge_index": "E:/GT-KB/bridge/INDEX.md",
        "db_path": "E:/GT-KB/groundtruth.db",
        "issue_count": 3,
        "issues": [
            {
                "class": "stale_backlog_status",
                "type": "nonterminal_work_item_all_related_threads_verified",
                "subject": "WI-2002",
                "severity": "P2",
                "evidence": {
                    "priority": "P3",
                    "resolution_status": "open",
                    "stage": "backlogged",
                    "related_bridge_threads": ["gtkb-low-priority-thread"],
                    "related_bridge_statuses": {"gtkb-low-priority-thread": "VERIFIED"},
                },
                "recommended_action": "Review for terminal backlog update.",
            },
            {
                "class": "stale_backlog_status",
                "type": "nonterminal_work_item_all_related_threads_verified",
                "subject": "WI-1001",
                "severity": "P1",
                "evidence": {
                    "priority": "P1",
                    "resolution_status": "open",
                    "stage": "in_progress",
                    "related_bridge_threads": ["gtkb-high-priority-thread"],
                    "related_bridge_statuses": {"gtkb-high-priority-thread": "VERIFIED"},
                },
                "recommended_action": "Review for terminal backlog update.",
            },
            {
                "class": "bridge_index_drift",
                "type": "versioned_bridge_file_unindexed",
                "subject": "gtkb-other",
                "severity": "P3",
                "evidence": {"path": "bridge/gtkb-other-001.md"},
                "recommended_action": "Classify separately.",
            },
        ],
    }


def test_packet_refuses_combined_triage_classes() -> None:
    module = _load_module()

    try:
        module.build_packet(_audit_payload(), triage_class="stale_backlog_status,bridge_index_drift")
    except ValueError as exc:
        assert "exactly one triage class" in str(exc)
    else:
        raise AssertionError("combined classes should be refused")


def test_packet_sorts_high_priority_nonterminal_verified_candidates_first() -> None:
    module = _load_module()

    packet = module.build_packet(_audit_payload(), triage_class="stale_backlog_status")

    assert packet["dry_run"] is True
    assert packet["candidate_count"] == 2
    assert packet["candidates"][0]["subject"] == "WI-1001"
    assert packet["candidates"][0]["confidence"] == "high"
    assert packet["owner_decision_slots"][0]["required"] is True
    assert len(packet["owner_decision_slots"]) == 1
    assert packet["candidates"][0]["proposed_mutation_type"] == "backlog_terminal_status_update"
    assert packet["exclusions"]["excluded_count"] == 1


def test_packet_generator_is_read_only_against_input_file(tmp_path: Path) -> None:
    module = _load_module()
    audit_path = tmp_path / "audit.json"
    audit_path.write_text(json.dumps(_audit_payload()), encoding="utf-8")
    before = audit_path.read_text(encoding="utf-8")

    packet = module.build_packet(module.load_audit_input(audit_path), triage_class="stale_backlog_status")

    assert packet["forbidden_actions"]
    assert audit_path.read_text(encoding="utf-8") == before


def test_gt_bridge_reconcile_packet_json_cli(tmp_path: Path) -> None:
    config = _write_config(tmp_path)
    audit_path = tmp_path / "audit.json"
    audit_path.write_text(json.dumps(_audit_payload()), encoding="utf-8")

    result = CliRunner().invoke(
        cli_main,
        [
            "--config",
            str(config),
            "bridge",
            "reconcile",
            "packet",
            "--class",
            "stale_backlog_status",
            "--input",
            str(audit_path),
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    packet = json.loads(result.output)
    assert packet["dry_run"] is True
    assert packet["triage_class"] == "stale_backlog_status"
    assert packet["candidates"][0]["subject"] == "WI-1001"
