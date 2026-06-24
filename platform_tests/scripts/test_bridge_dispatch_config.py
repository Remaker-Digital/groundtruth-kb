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

import groundtruth_kb.bridge_dispatch_config as bridge_dispatch_config  # noqa: E402
from groundtruth_kb.bridge_dispatch_config import (  # noqa: E402
    BENIGN_NONLAUNCH_LAUNCH_REASONS,
    _runtime_findings_for_recipient,
    collect_bridge_dispatch_status,
    load_bridge_dispatch_config,
    select_dispatch_candidates,
)
from groundtruth_kb.bridge_dispatch_report import build_bridge_dispatch_report  # noqa: E402
from groundtruth_kb.bridge_dispatch_rules import DispatchContext, context_from_bridge_text  # noqa: E402
from groundtruth_kb.bridge_dispatch_transactions import (  # noqa: E402
    DispatchConfigTransactionError,
    set_eligibility,
    set_rule,
    set_weights,
)
from groundtruth_kb.harness_projection import read_roles  # noqa: E402


@pytest.fixture(autouse=True)
def _no_registry_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GTKB_HARNESS_REGISTRY_PATH", raising=False)
    monkeypatch.delenv(bridge_dispatch_config.CROSS_HARNESS_TRIGGER_DISABLE_ENV_VAR, raising=False)
    monkeypatch.setattr(bridge_dispatch_config, "_read_windows_persistent_env_var", lambda _name, _scope: None)


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


def test_wi4760_health_warns_when_process_kill_switch_active(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_project(tmp_path)
    monkeypatch.setenv(bridge_dispatch_config.CROSS_HARNESS_TRIGGER_DISABLE_ENV_VAR, "1")

    status = collect_bridge_dispatch_status(tmp_path)

    assert status.health_status == "WARN"
    finding = "\n".join(status.health_findings)
    assert bridge_dispatch_config.CROSS_HARNESS_TRIGGER_DISABLE_ENV_VAR in finding
    assert "Process" in finding
    assert "no-op" in finding


def test_wi4760_health_warns_when_user_scope_kill_switch_active(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_project(tmp_path)

    def _persistent_reader(_name: str, scope: str) -> str | None:
        return "1" if scope == "User" else None

    monkeypatch.setattr(bridge_dispatch_config, "_read_windows_persistent_env_var", _persistent_reader)

    status = collect_bridge_dispatch_status(tmp_path)

    assert status.health_status == "WARN"
    finding = "\n".join(status.health_findings)
    assert bridge_dispatch_config.CROSS_HARNESS_TRIGGER_DISABLE_ENV_VAR in finding
    assert "User" in finding
    assert "no-op" in finding


def test_wi4768_live_dispatch_config_projection_drift_is_visible() -> None:
    rules = tomllib.loads((REPO_ROOT / "config" / "dispatcher" / "rules.toml").read_text(encoding="utf-8"))
    harness_b_rules = rules["harnesses"]["B"]

    assert harness_b_rules["can_receive_dispatch"] is True
    assert "interactive-only" not in harness_b_rules["tags"]

    projection = read_roles(REPO_ROOT)
    harness_b = next(row for row in projection["harnesses"] if row["id"] == "B")

    status_payload = collect_bridge_dispatch_status(REPO_ROOT).to_json_dict()
    harness_b_status = next(row for row in status_payload["harnesses"] if row["id"] == "B")
    assert harness_b_status["can_receive_dispatch"] is True
    assert harness_b_status["status"] == harness_b["status"]
    if harness_b["status"] == "active":
        candidate_ids = [row["id"] for row in status_payload["selected_by_role"]["prime-builder"]]
        assert "B" in candidate_ids
    else:
        assert any(
            "harness B can_receive_dispatch" in finding and f"status={harness_b['status']}" in finding
            for finding in status_payload["consistency_findings"]
        )


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


def test_quality_first_selection_breaks_ties_by_cost_then_availability(tmp_path: Path) -> None:
    _write_project(
        tmp_path,
        rules="""
schema_version = 1
selection_order = ["quality", "cost", "availability", "harness_id"]
rules = []
""".lstrip(),
    )
    records = [
        {
            "id": "A",
            "harness_name": "codex",
            "status": "active",
            "role": ["prime-builder"],
            "can_receive_dispatch": True,
            "dispatch_quality": 90,
            "dispatch_cost": 20,
            "dispatch_availability": 99,
        },
        {
            "id": "B",
            "harness_name": "claude",
            "status": "active",
            "role": ["prime-builder"],
            "can_receive_dispatch": True,
            "dispatch_quality": 95,
            "dispatch_cost": 70,
            "dispatch_availability": 75,
        },
        {
            "id": "C",
            "harness_name": "antigravity",
            "status": "active",
            "role": ["prime-builder"],
            "can_receive_dispatch": True,
            "dispatch_quality": 95,
            "dispatch_cost": 60,
            "dispatch_availability": 80,
        },
        {
            "id": "D",
            "harness_name": "ollama",
            "status": "active",
            "role": ["prime-builder"],
            "can_receive_dispatch": True,
            "dispatch_quality": 95,
            "dispatch_cost": 60,
            "dispatch_availability": 95,
        },
    ]

    selected = select_dispatch_candidates(
        records,
        load_bridge_dispatch_config(tmp_path),
        DispatchContext(required_role="prime-builder"),
    )

    assert [row["id"] for row in selected] == ["D", "C", "B", "A"]


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


# WI-4718 — benign concurrency_cap_reached must not be misclassified as a runtime FAIL.
# bridge/gtkb-wi4718-dispatch-health-benign-cap-false-fail-001.md (GO at -002).
#
# The trigger collapses all non-launch spawn results to last_result="launch_failed";
# only last_launch.reason distinguishes saturation (benign) from genuine failure.
# Before this fix the generic last_result check at _runtime_findings_for_recipient
# emitted a dispatch runtime failure finding for concurrency_cap_reached, causing
# gt bridge dispatch health to report FAIL for a merely saturated dispatcher.


def test_wi4718_saturation_emits_warn_not_fail(tmp_path: Path) -> None:
    """A concurrency_cap_reached row with pending work emits WARN, never FAIL."""
    _write_project(tmp_path)
    _write_dispatch_state(
        tmp_path,
        {
            "loyal-opposition:D": {
                "pending_count": 3,
                "selected_count": 2,
                "last_result": "launch_failed",
                "last_launch": {
                    "reason": "concurrency_cap_reached",
                    "live_count": 2,
                    "cap": 2,
                },
            }
        },
    )

    status = collect_bridge_dispatch_status(tmp_path)

    failure_findings = [f for f in status.health_findings if "dispatch runtime failure" in f]
    warn_findings = [f for f in status.health_findings if "saturated" in f]
    assert failure_findings == [], f"Expected no failure findings, got: {failure_findings}"
    assert len(warn_findings) == 1
    assert "loyal-opposition:D" in warn_findings[0]
    assert "live_count=2/cap=2" in warn_findings[0]
    assert "pending_count=3" in warn_findings[0]
    assert status.health_status != "FAIL"


def test_wi4718_saturation_with_live_count_cap_in_finding(tmp_path: Path) -> None:
    """The saturation WARN finding includes live_count and cap from last_launch."""
    row: dict = {
        "pending_count": 5,
        "selected_count": 1,
        "last_result": "launch_failed",
        "last_launch": {"reason": "concurrency_cap_reached", "live_count": 4, "cap": 4},
    }

    findings = _runtime_findings_for_recipient("prime-builder:B", row)

    failure = [f for f in findings if "dispatch runtime failure" in f]
    warn = [f for f in findings if "saturated" in f]
    assert failure == []
    assert len(warn) == 1
    assert "live_count=4/cap=4" in warn[0]


def test_wi4718_no_findings_when_no_pending_work(tmp_path: Path) -> None:
    """Saturation with no pending work emits no findings at all."""
    row: dict = {
        "pending_count": 0,
        "selected_count": 0,
        "last_result": "launch_failed",
        "last_launch": {"reason": "concurrency_cap_reached", "live_count": 2, "cap": 2},
    }

    findings = _runtime_findings_for_recipient("loyal-opposition:A", row)

    assert findings == []


def test_wi4718_genuine_launch_reason_still_fails(tmp_path: Path) -> None:
    """A genuine failure reason (spawn_rate_limited) still produces a runtime failure."""
    _write_project(tmp_path)
    _write_dispatch_state(
        tmp_path,
        {
            "loyal-opposition:D": {
                "pending_count": 2,
                "selected_count": 1,
                "last_result": "launch_failed",
                "last_launch": {"reason": "spawn_rate_limited"},
            }
        },
    )

    status = collect_bridge_dispatch_status(tmp_path)

    assert status.health_status == "FAIL"
    assert any("last_result=launch_failed" in f for f in status.health_findings)


def test_wi4718_absent_launch_reason_still_fails() -> None:
    """launch_failed with no reason field is treated as a genuine failure (fail-closed)."""
    row: dict = {
        "pending_count": 1,
        "selected_count": 1,
        "last_result": "launch_failed",
        "last_launch": {},
    }

    findings = _runtime_findings_for_recipient("prime-builder:B", row)

    assert any("dispatch runtime failure" in f and "last_result=launch_failed" in f for f in findings)


def test_wi4718_benign_constant_contains_expected_reasons() -> None:
    """BENIGN_NONLAUNCH_LAUNCH_REASONS contains concurrency_cap_reached and is frozen."""
    assert "concurrency_cap_reached" in BENIGN_NONLAUNCH_LAUNCH_REASONS
    assert "per_role_concurrency_cap_reached" in BENIGN_NONLAUNCH_LAUNCH_REASONS
    assert isinstance(BENIGN_NONLAUNCH_LAUNCH_REASONS, frozenset)


def test_wi4768_per_role_saturation_emits_warn_not_fail(tmp_path: Path) -> None:
    """Per-role worker saturation is live backpressure, not dispatcher failure."""
    _write_project(tmp_path)
    _write_dispatch_state(
        tmp_path,
        {
            "loyal-opposition:D": {
                "pending_count": 3,
                "selected_count": 1,
                "last_result": "launch_failed",
                "last_launch": {
                    "reason": "per_role_concurrency_cap_reached",
                    "per_role_live": 8,
                    "per_role_cap": 8,
                },
            }
        },
    )

    status = collect_bridge_dispatch_status(tmp_path)

    failure_findings = [f for f in status.health_findings if "dispatch runtime failure" in f]
    warn_findings = [f for f in status.health_findings if "per_role_concurrency_cap_reached" in f]
    assert failure_findings == []
    assert len(warn_findings) == 1
    assert "live_count=8/cap=8" in warn_findings[0]
    assert status.health_status == "WARN"


def test_wi4768_orphaned_failure_evidence_warns_not_fails(tmp_path: Path) -> None:
    """A recipient row whose failure evidence points at another recipient is stale."""
    _write_project(tmp_path)
    _write_dispatch_state(
        tmp_path,
        {
            "loyal-opposition:F": {
                "pending_count": 2,
                "selected_count": 1,
                "last_result": "subprocess_execution_failed",
                "failure_class": "subprocess_execution_failed",
                "selected_candidate": {"recipient": "loyal-opposition:D"},
                "last_launch": {
                    "recipient": "loyal-opposition:D",
                    "selected_candidate": {"recipient": "loyal-opposition:D"},
                    "exit_failure_reason": "subprocess_execution_failed",
                },
            }
        },
    )

    status = collect_bridge_dispatch_status(tmp_path)

    findings = "\n".join(status.health_findings)
    assert "dispatch runtime failure: loyal-opposition:F" not in findings
    assert "loyal-opposition:F stale failure evidence ignored" in findings
    classification = next(row for row in status.runtime_classifications if row["recipient"] == "loyal-opposition:F")
    assert classification["severity"] == "WARN"
    assert classification["stale_failure_evidence"] is True
    assert classification["stale_failure_reason"] == "recipient evidence points to loyal-opposition:D"


def test_wi4768_status_surfaces_config_projection_drift(tmp_path: Path) -> None:
    """Status keeps overlay behavior visible by reporting raw projection drift."""
    harnesses = _default_harnesses()
    for harness in harnesses:
        if harness["id"] == "F":
            harness["can_receive_dispatch"] = False
    _write_project(
        tmp_path,
        harnesses=harnesses,
        rules="""
schema_version = 1

[harnesses.F]
can_receive_dispatch = true
dispatch_quality = 80

rules = []
""".lstrip(),
    )

    status = collect_bridge_dispatch_status(tmp_path)

    assert status.health_status == "WARN"
    assert any(
        "harness F can_receive_dispatch rules.toml=True harness-registry=False" in finding
        for finding in status.consistency_findings
    )
    assert any(row["id"] == "F" for row in status.selected_by_role["loyal-opposition"])


def test_wi4765_report_builder_preserves_dispatch_runtime_failure_causes(tmp_path: Path) -> None:
    """The read-only report exposes distinct runtime cause fields for operators."""
    _write_project(tmp_path)
    _write_dispatch_state(
        tmp_path,
        {
            "loyal-opposition:D": {
                "pending_count": 1,
                "selected_count": 1,
                "last_result": "launch_failed",
                "failure_class": "provider_failure",
                "last_launch": {
                    "reason": "spawn_rate_limited",
                    "exit_failure_reason": "no_verdict_produced",
                },
            }
        },
    )

    report = build_bridge_dispatch_report(tmp_path)
    taxonomy = report["reliability"]["failure_taxonomy"]

    assert taxonomy["last_result"]["launch_failed"] == 1
    assert taxonomy["failure_class"]["provider_failure"] == 1
    assert taxonomy["last_launch.reason"]["spawn_rate_limited"] == 1
    assert taxonomy["last_launch.exit_failure_reason"]["no_verdict_produced"] == 1


def test_wi4766_transactions_round_trip_through_dispatch_config_loader(tmp_path: Path) -> None:
    _write_project(
        tmp_path,
        rules="""
schema_version = 1
selection_order = ["quality", "cost", "availability", "harness_id"]

[harnesses.A]
can_receive_dispatch = true
can_fire_events = true
dispatch_cost = 60
dispatch_quality = 90
dispatch_availability = 90

[[rules]]
id = "bridge-prime-builder-default"
required_roles = ["prime-builder"]
statuses = ["GO"]
prefer = ["quality", "cost", "availability", "harness_id"]
""".lstrip(),
    )

    set_eligibility(tmp_path, "A", can_receive_dispatch=False, can_fire_events=None)
    set_weights(tmp_path, "A", dispatch_quality=75, dispatch_cost=20, dispatch_availability=None)
    set_rule(tmp_path, "bridge-prime-builder-default", statuses=("GO", "NO-GO"), prefer=("cost", "harness_id"))

    dispatch_config = load_bridge_dispatch_config(tmp_path)
    overlay = dispatch_config.overlay_for("A")
    assert overlay is not None
    assert overlay.can_receive_dispatch is False
    assert overlay.dispatch_quality == 75
    assert overlay.dispatch_cost == 20
    assert dispatch_config.rules[0].statuses == ("GO", "NO-GO")
    assert dispatch_config.selection_order_for(DispatchContext(required_role="prime-builder", status="GO")) == (
        "cost",
        "harness_id",
    )


def test_wi4766_transactions_reject_unknown_rule_without_config_write(tmp_path: Path) -> None:
    _write_project(tmp_path)
    rules_path = tmp_path / "config" / "dispatcher" / "rules.toml"
    before = rules_path.read_bytes()

    with pytest.raises(DispatchConfigTransactionError, match="does not exist"):
        set_rule(tmp_path, "missing-rule", statuses=("NEW",))

    assert rules_path.read_bytes() == before


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
