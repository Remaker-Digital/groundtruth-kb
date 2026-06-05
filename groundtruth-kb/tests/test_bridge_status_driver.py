"""Tests for the read-only bridge status driver."""

from __future__ import annotations

import inspect
import json
from pathlib import Path


def _write_bridge_file(root: Path, name: str, version: int, content: str) -> None:
    (root / "bridge" / f"{name}-{version:03d}.md").write_text(content, encoding="utf-8")


def test_bridge_status_driver_reports_role_actionability_without_verified(project_dir: Path) -> None:
    bridge_dir = project_dir / "bridge"
    bridge_dir.mkdir()
    index_lines = [
        "Document: impl-go",
        "GO: bridge/impl-go-002.md",
        "NEW: bridge/impl-go-001.md",
        "",
        "Document: scoping-go",
        "GO: bridge/scoping-go-002.md",
        "NEW: bridge/scoping-go-001.md",
        "",
        "Document: revise-me",
        "NO-GO: bridge/revise-me-002.md",
        "NEW: bridge/revise-me-001.md",
        "",
        "Document: review-new",
        "NEW: bridge/review-new-001.md",
        "",
        "Document: review-revised",
        "REVISED: bridge/review-revised-003.md",
        "NO-GO: bridge/review-revised-002.md",
        "NEW: bridge/review-revised-001.md",
        "",
        "Document: closed",
        "VERIFIED: bridge/closed-002.md",
        "NEW: bridge/closed-001.md",
        "",
        "Document: withdrawn",
        "WITHDRAWN: bridge/withdrawn-002.md",
        "NEW: bridge/withdrawn-001.md",
        "",
        "Document: advisory",
        "ADVISORY: bridge/advisory-001.md",
    ]
    (bridge_dir / "INDEX.md").write_text("\n".join(index_lines), encoding="utf-8")

    _write_bridge_file(project_dir, "impl-go", 1, "bridge_kind: implementation_proposal\n")
    _write_bridge_file(project_dir, "impl-go", 2, "GO\n")
    _write_bridge_file(project_dir, "scoping-go", 1, "bridge_kind: implementation_scoping\n")
    _write_bridge_file(project_dir, "scoping-go", 2, "GO\n")
    _write_bridge_file(project_dir, "revise-me", 1, "bridge_kind: implementation_proposal\n")
    _write_bridge_file(project_dir, "revise-me", 2, "NO-GO\n")
    _write_bridge_file(project_dir, "review-new", 1, "bridge_kind: implementation_proposal\n")
    _write_bridge_file(project_dir, "review-revised", 1, "bridge_kind: implementation_proposal\n")
    _write_bridge_file(project_dir, "review-revised", 2, "NO-GO\n")
    _write_bridge_file(project_dir, "review-revised", 3, "bridge_kind: implementation_proposal\n")
    _write_bridge_file(project_dir, "closed", 1, "bridge_kind: post_implementation_report\n")
    _write_bridge_file(project_dir, "closed", 2, "VERIFIED\n")
    _write_bridge_file(project_dir, "withdrawn", 1, "bridge_kind: implementation_proposal\n")
    _write_bridge_file(project_dir, "withdrawn", 2, "WITHDRAWN\n")
    _write_bridge_file(project_dir, "advisory", 1, "bridge_kind: advisory_report\n")

    from groundtruth_kb.bridge.status_driver import collect_bridge_status

    snapshot = collect_bridge_status(project_dir)
    queue = snapshot.queue

    assert queue.status_counts["VERIFIED"] == 1
    assert queue.status_counts["WITHDRAWN"] == 1
    assert [item.document_name for item in queue.prime_actionable] == [
        "impl-go",
        "scoping-go",
        "revise-me",
    ]
    assert {item.top_status for item in queue.prime_actionable} == {"GO", "NO-GO"}
    assert "closed" not in {item.document_name for item in queue.prime_actionable}
    assert [item.document_name for item in queue.loyal_opposition_actionable] == [
        "review-new",
        "review-revised",
    ]
    assert queue.dispatchable_counts["prime_dispatchable"] == 2
    assert queue.dispatchable_counts["prime_interactive"] == 1
    assert queue.dispatchable_counts["terminal_or_non_actionable"] == 3


def test_bridge_status_driver_accepts_multiline_index_header_comments(project_dir: Path) -> None:
    bridge_dir = project_dir / "bridge"
    bridge_dir.mkdir()
    index_lines = [
        "# Bridge Index",
        "",
        "<!-- Prime inserts new document entries at the top of the list below. -->",
        "<!-- Umbrella naming note (per gtkb-governance-hygiene-bundle Change G):",
        "     The AUQ-enforcement-stack umbrella uses two prefixes for the same family:",
        "       - gtkb-gov-askuserquestion-enforcement-stack-slice-{a,b,c,d}-*",
        "       - gtkb-gov-auq-enforcement-stack-slice-{e,f,a-followup}-*",
        "     They are the same governance umbrella; search both prefixes when investigating. -->",
        "<!-- Audit-trail clarification (2026-05-11, S342):",
        "     Bridge thread: gtkb-s341-backlog-candidates-membase-insert VERIFIED at -011. -->",
        "",
        "Document: review-new",
        "NEW: bridge/review-new-001.md",
    ]
    (bridge_dir / "INDEX.md").write_text("\n".join(index_lines), encoding="utf-8")
    _write_bridge_file(project_dir, "review-new", 1, "bridge_kind: implementation_proposal\n")

    from groundtruth_kb.bridge.status_driver import collect_bridge_status

    queue = collect_bridge_status(project_dir).queue

    assert queue.parse_error_count == 0
    assert queue.parse_errors == ()
    assert queue.status_counts["NEW"] == 1


def test_bridge_status_driver_reports_local_automation_health(project_dir: Path) -> None:
    (project_dir / "bridge").mkdir()
    (project_dir / "bridge" / "INDEX.md").write_text("", encoding="utf-8")
    (project_dir / "scripts").mkdir()
    (project_dir / "scripts" / "cross_harness_bridge_trigger.py").write_text("# trigger\n", encoding="utf-8")
    (project_dir / ".claude").mkdir()
    (project_dir / ".codex").mkdir()
    hook_payload = {
        "hooks": {
            "Stop": [
                {
                    "hooks": [
                        {"command": "python scripts/cross_harness_bridge_trigger.py"},
                        {"command": "python scripts/active_session_heartbeat.py"},
                        {"command": "python scripts/single_harness_bridge_automation.py --ensure"},
                    ]
                }
            ]
        }
    }
    (project_dir / ".claude" / "settings.json").write_text(json.dumps(hook_payload), encoding="utf-8")
    (project_dir / ".codex" / "hooks.json").write_text(json.dumps(hook_payload), encoding="utf-8")
    state_dir = project_dir / ".gtkb-state" / "bridge-poller"
    state_dir.mkdir(parents=True)
    (state_dir / "dispatch-state.json").write_text(
        json.dumps({"recipients": {"prime-builder": {}, "loyal-opposition": {}}, "updated_at": "2026-05-12T00:00:00Z"}),
        encoding="utf-8",
    )
    (state_dir / "active-codex-session.lock").write_text(json.dumps({"role": "codex"}), encoding="utf-8")
    map_path = project_dir / "config" / "agent-control" / "system-interface-map.toml"
    map_path.parent.mkdir(parents=True)
    map_path.write_text(
        "\n".join(
            [
                "[[systems]]",
                'id = "bridge-dispatch"',
                'canonical_name = "bridge dispatch"',
                'lifecycle_state = "active"',
                "",
                "[[systems]]",
                'id = "smart-poller"',
                'canonical_name = "retired smart poller"',
                'lifecycle_state = "retired"',
                "",
                "[[systems]]",
                'id = "monitor-gt-kb-bridge-codex-thread"',
                'canonical_name = "monitor-gt-kb-bridge (Codex app thread automation)"',
                'generated_or_authoritative = "external"',
            ]
        ),
        encoding="utf-8",
    )

    from groundtruth_kb.bridge.status_driver import collect_bridge_status

    automation = collect_bridge_status(project_dir).automation

    assert automation.trigger_script_exists is True
    assert automation.dispatch_state["recipient_count"] == 2
    assert automation.hook_registrations[".claude/settings.json"]["cross_harness_trigger_registered"] is True
    assert automation.hook_registrations[".codex/hooks.json"]["single_harness_automation_registered"] is True
    assert len(automation.active_session_locks) == 1
    assert automation.system_inventory["retired_systems"][0]["id"] == "smart-poller"
    assert automation.system_inventory["external_thread_automations"][0]["id"] == "monitor-gt-kb-bridge-codex-thread"


def test_bridge_status_driver_has_no_runtime_dispatch_side_effects() -> None:
    import groundtruth_kb.bridge.status_driver as status_driver

    source = inspect.getsource(status_driver)

    assert "subprocess" not in source
    assert ".write_text(" not in source
    assert ".replace(" not in source
