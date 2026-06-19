from __future__ import annotations

import importlib.util
import json
import sys
import tomllib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))
SCAN_HELPER_PATH = REPO_ROOT / ".claude" / "skills" / "bridge" / "helpers" / "scan_bridge.py"

from groundtruth_kb.bridge_dispatch_config import (  # noqa: E402
    collect_bridge_dispatch_status,
    load_bridge_dispatch_config,
    select_dispatch_candidates,
)
from groundtruth_kb.bridge_dispatch_rules import DispatchContext, context_from_bridge_text  # noqa: E402
from groundtruth_kb.harness_projection import read_roles  # noqa: E402


@pytest.fixture(autouse=True)
def _no_registry_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GTKB_HARNESS_REGISTRY_PATH", raising=False)


def _write_project(root: Path, *, rules: str = "", harnesses: list[dict] | None = None) -> None:
    (root / "config" / "dispatcher").mkdir(parents=True)
    (root / "config" / "dispatcher" / "rules.toml").write_text(
        rules
        or """
schema_version = 1
selection_order = ["reviewer_precedence", "harness_id"]
rules = []
""".lstrip(),
        encoding="utf-8",
    )
    (root / "harness-state").mkdir()
    (root / "harness-state" / "harness-registry.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source_of_truth": "test",
                "harnesses": harnesses or _default_harnesses(),
            }
        ),
        encoding="utf-8",
    )


def _default_harnesses() -> list[dict]:
    return [
        {
            "id": "A",
            "harness_name": "codex",
            "harness_type": "codex",
            "status": "active",
            "role": ["prime-builder"],
            "can_fire_events": True,
            "can_receive_dispatch": True,
            "event_driven_hooks": True,
            "reviewer_precedence": 20,
        },
        {
            "id": "B",
            "harness_name": "claude",
            "harness_type": "claude",
            "status": "active",
            "role": ["prime-builder"],
            "can_fire_events": True,
            "can_receive_dispatch": False,
            "event_driven_hooks": False,
            "reviewer_precedence": 10,
        },
        {
            "id": "D",
            "harness_name": "ollama",
            "harness_type": "ollama",
            "status": "active",
            "role": ["loyal-opposition"],
            "can_fire_events": False,
            "can_receive_dispatch": True,
            "event_driven_hooks": False,
            "reviewer_precedence": 10,
        },
        {
            "id": "F",
            "harness_name": "openrouter",
            "harness_type": "openrouter",
            "status": "active",
            "role": ["loyal-opposition"],
            "can_fire_events": False,
            "can_receive_dispatch": True,
            "event_driven_hooks": False,
            "reviewer_precedence": 20,
        },
    ]


def test_collect_status_keeps_role_and_dispatchability_orthogonal(tmp_path: Path) -> None:
    _write_project(tmp_path)

    status = collect_bridge_dispatch_status(tmp_path)

    assert status.health_status == "PASS"
    assert [row["id"] for row in status.selected_by_role["prime-builder"]] == ["A"]
    assert [row["id"] for row in status.selected_by_role["loyal-opposition"]] == ["D", "F"]
    claude = next(row for row in status.harnesses if row["id"] == "B")
    assert claude["role"] == ["prime-builder"]
    assert claude["can_receive_dispatch"] is False
    assert claude["can_fire_events"] is True


def test_collect_status_preserves_harness_registry_projection_bytes(tmp_path: Path) -> None:
    _write_project(tmp_path)
    registry_path = tmp_path / "harness-state" / "harness-registry.json"
    before = registry_path.read_bytes()

    status = collect_bridge_dispatch_status(tmp_path)

    assert status.selected_by_role["prime-builder"]
    assert registry_path.read_bytes() == before


def test_wi4661_live_harness_b_is_headless_dispatchable() -> None:
    rules = tomllib.loads((REPO_ROOT / "config" / "dispatcher" / "rules.toml").read_text(encoding="utf-8"))
    harness_b_rules = rules["harnesses"]["B"]

    assert harness_b_rules["can_receive_dispatch"] is True
    assert "interactive-only" not in harness_b_rules["tags"]

    projection = read_roles(REPO_ROOT)
    harness_b = next(row for row in projection["harnesses"] if row["id"] == "B")
    assert harness_b["role"] == ["prime-builder"]
    assert harness_b["status"] == "active"

    status_payload = collect_bridge_dispatch_status(REPO_ROOT).to_json_dict()
    harness_b_status = next(row for row in status_payload["harnesses"] if row["id"] == "B")
    assert harness_b_status["can_receive_dispatch"] is True
    prime_candidate_ids = [row["id"] for row in status_payload["selected_by_role"]["prime-builder"]]
    assert "B" in prime_candidate_ids


def test_config_overlay_can_disable_dispatchability(tmp_path: Path) -> None:
    _write_project(
        tmp_path,
        rules="""
schema_version = 1
selection_order = ["reviewer_precedence", "harness_id"]

[harnesses.A]
can_receive_dispatch = false

rules = []
""".lstrip(),
    )

    status = collect_bridge_dispatch_status(tmp_path)

    assert status.health_status == "FAIL"
    assert status.selected_by_role["prime-builder"] == []
    assert any("prime-builder" in finding for finding in status.health_findings)


def test_context_from_bridge_text_extracts_rule_context() -> None:
    context = context_from_bridge_text(
        "loyal-opposition",
        "session_subject: Dispatch topology\n\n::open verify\n",
        status="NEW",
    )

    assert context == DispatchContext(
        required_role="loyal-opposition",
        status="NEW",
        session_subject="Dispatch topology",
        activity="verify",
    )


def test_rules_match_status_and_activity_without_role_only_fallback(tmp_path: Path) -> None:
    _write_project(
        tmp_path,
        rules="""
schema_version = 1

[[rules]]
id = "lo-verify-only"
required_roles = ["loyal-opposition"]
statuses = ["NEW"]
activities = ["verify"]
prefer = ["harness_id"]
""".lstrip(),
    )
    config = load_bridge_dispatch_config(tmp_path)
    records = _default_harnesses()

    matching = select_dispatch_candidates(
        records,
        config,
        DispatchContext(required_role="loyal-opposition", status="NEW", activity="verify"),
    )
    non_matching = select_dispatch_candidates(
        records,
        config,
        DispatchContext(required_role="loyal-opposition", status="GO", activity="verify"),
    )

    assert [row["id"] for row in matching] == ["D", "F"]
    assert non_matching == []


# WI-4658 — collect_bridge_dispatch_status quarantined-thread health-finding tests.
# bridge/gtkb-dispatch-malformed-status-token-quarantine-001.md (GO at -002).
#
# Cover the new finding emitted by ``_runtime_findings_for_recipient`` when a
# recipient state row carries ``quarantined_threads`` from the batch acquire's
# skip-and-continue path. Without this finding, ``gt bridge dispatch health``
# reports topology-only PASS while live quarantines exist (false-green).


def _write_dispatch_state(root: Path, recipients: dict[str, dict]) -> None:
    state_dir = root / ".gtkb-state" / "bridge-poller"
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "dispatch-state.json").write_text(
        json.dumps({"recipients": recipients, "schema_version": 1, "updated_at": "2026-06-18T17:00:00Z"}),
        encoding="utf-8",
    )


def _load_scan_helper():
    spec = importlib.util.spec_from_file_location("scan_bridge_wi4578_regression", SCAN_HELPER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["scan_bridge_wi4578_regression"] = module
    spec.loader.exec_module(module)
    return module


def test_wi4658_health_warns_when_quarantined_threads_present(tmp_path: Path) -> None:
    """A recipient state row carrying quarantined_threads emits a WARN-level
    finding so health is no longer topology-only PASS."""
    _write_project(tmp_path)
    _write_dispatch_state(
        tmp_path,
        {
            "prime-builder:A": {
                "pending_count": 5,
                "selected_count": 3,
                "last_result": "launched",
                "last_launch": {"reason": None},
                "quarantined_threads": [
                    {"slug": "gtkb-wi4232-bridge-index-drift-pb-classification", "offending_line": "GO test"},
                    {"slug": "gtkb-other-broken", "offending_line": ""},
                ],
            }
        },
    )

    status = collect_bridge_dispatch_status(tmp_path)

    quarantine_findings = [f for f in status.health_findings if "quarantined for malformed status token" in f]
    assert len(quarantine_findings) == 1
    finding = quarantine_findings[0]
    assert "prime-builder:A" in finding
    assert "2 bridge thread(s)" in finding
    assert "gtkb-wi4232-bridge-index-drift-pb-classification" in finding
    assert status.health_status == "WARN"


def test_wi4658_health_silent_when_no_quarantined_threads(tmp_path: Path) -> None:
    """Non-regression: an empty quarantined_threads list emits no finding."""
    _write_project(tmp_path)
    _write_dispatch_state(
        tmp_path,
        {
            "prime-builder:A": {
                "pending_count": 5,
                "selected_count": 3,
                "last_result": "launched",
                "last_launch": {"reason": None},
                "quarantined_threads": [],
            }
        },
    )

    status = collect_bridge_dispatch_status(tmp_path)
    quarantine_findings = [f for f in status.health_findings if "quarantined for malformed status token" in f]
    assert quarantine_findings == []


def test_wi4658_health_dedupes_quarantined_slugs_in_finding(tmp_path: Path) -> None:
    """The finding sorts and de-duplicates slugs to keep the message deterministic
    when the dispatcher records repeated quarantine attempts across cycles."""
    _write_project(tmp_path)
    _write_dispatch_state(
        tmp_path,
        {
            "prime-builder:A": {
                "pending_count": 5,
                "selected_count": 3,
                "last_result": "launched",
                "last_launch": {"reason": None},
                "quarantined_threads": [
                    {"slug": "beta"},
                    {"slug": "alpha"},
                    {"slug": "beta"},
                    {"slug": "alpha"},
                ],
            }
        },
    )

    status = collect_bridge_dispatch_status(tmp_path)
    quarantine_findings = [f for f in status.health_findings if "quarantined for malformed status token" in f]
    assert len(quarantine_findings) == 1
    # 2 distinct slugs, listed in sorted order.
    assert "2 bridge thread(s)" in quarantine_findings[0]
    assert "['alpha', 'beta']" in quarantine_findings[0]


def test_wi4658_health_ignores_non_dict_quarantine_entries(tmp_path: Path) -> None:
    """Defensive: malformed entries in the quarantined_threads list (non-dict
    or missing 'slug') are skipped without raising."""
    _write_project(tmp_path)
    _write_dispatch_state(
        tmp_path,
        {
            "prime-builder:A": {
                "pending_count": 5,
                "selected_count": 3,
                "last_result": "launched",
                "last_launch": {"reason": None},
                "quarantined_threads": ["not-a-dict", {"slug": "good"}, {"no_slug_key": "x"}],
            }
        },
    )

    status = collect_bridge_dispatch_status(tmp_path)
    quarantine_findings = [f for f in status.health_findings if "quarantined for malformed status token" in f]
    assert len(quarantine_findings) == 1
    assert "1 bridge thread(s)" in quarantine_findings[0]
    assert "['good']" in quarantine_findings[0]


def test_wi4578_health_fails_for_blocked_runtime_candidates(tmp_path: Path) -> None:
    """Pending LO work plus readiness/backoff/spawn blockers is a runtime FAIL."""
    _write_project(tmp_path)
    _write_dispatch_state(
        tmp_path,
        {
            "loyal-opposition": {
                "pending_count": 2,
                "selected_count": 2,
                "last_result": "unchanged",
                "last_launch": {"reason": "spawn_rate_limited"},
                "fallback_skipped_candidates": [
                    {"recipient": "loyal-opposition:D", "reason": "ollama_dispatch_not_ready"},
                    {
                        "recipient": "loyal-opposition:F",
                        "reason": "provider_failure_backoff_active",
                        "failure_class": "process_terminated_abruptly",
                    },
                ],
            },
            "loyal-opposition:D": {
                "pending_count": 2,
                "selected_count": 1,
                "last_result": "ollama_dispatch_not_ready",
            },
            "loyal-opposition:F": {
                "pending_count": 2,
                "selected_count": 2,
                "last_result": "provider_failure_backoff_active",
                "failure_class": "process_terminated_abruptly",
            },
        },
    )

    status = collect_bridge_dispatch_status(tmp_path)

    assert status.health_status == "FAIL"
    findings = "\n".join(status.health_findings)
    assert "last_launch.reason=spawn_rate_limited" in findings
    assert "reason=ollama_dispatch_not_ready" in findings
    assert "reason=provider_failure_backoff_active" in findings
    assert "failure_class=process_terminated_abruptly" in findings


def test_wi4578_health_fails_for_exit_zero_no_verdict_evidence(tmp_path: Path) -> None:
    """Exit-zero LO completion without a verdict is runtime failure evidence."""
    _write_project(tmp_path)
    _write_dispatch_state(
        tmp_path,
        {
            "loyal-opposition:D": {
                "pending_count": 1,
                "selected_count": 1,
                "last_result": "launched",
                "last_launch": {"exit_failure_reason": "no_verdict_produced"},
            }
        },
    )

    status = collect_bridge_dispatch_status(tmp_path)

    assert status.health_status == "FAIL"
    assert any("last_launch.exit_failure_reason=no_verdict_produced" in f for f in status.health_findings)


def test_wi4578_manual_scan_excludes_acknowledged_archived_nonterminal(tmp_path: Path) -> None:
    """Manual scan uses the archive-aware bridge state for live actionable rows."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir(parents=True)
    (tmp_path / "config" / "governance").mkdir(parents=True)
    (tmp_path / "config" / "governance" / "tafe-acknowledged-archived-bridges.toml").write_text(
        """
[[acknowledged]]
slug = "archived-new"
""".lstrip(),
        encoding="utf-8",
    )
    (bridge_dir / "archived-new-001.md").write_text("NEW\n\n# Archived thread\n", encoding="utf-8")
    (bridge_dir / "live-new-001.md").write_text("NEW\n\n# Live thread\n", encoding="utf-8")
    index_path = bridge_dir / "INDEX.md"
    index_path.write_text("", encoding="utf-8")

    helper = _load_scan_helper()
    result = helper.scan(role="loyal-opposition", index_path=index_path)

    assert [thread["document"] for thread in result["actionable"]] == ["live-new"]
    assert [thread["document"] for thread in result["excluded_archived"]] == ["archived-new"]
    assert result["summary"] == {"NEW": 1}
