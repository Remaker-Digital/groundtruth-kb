"""Tests for the report-only API harness stewardship monitor (WI-4558).

Covers the GO-required evidence (bridge/gtkb-api-harness-stewardship-monitor-002):
all six read surfaces (incl. dispatch JSONL rotation), stuck-work risk scoring
with cited evidence, material-change detection, end-to-end run emitting only
under .gtkb-state/api-harness-stewardship/, and an AST/structural proof that the
module is report-only (no network imports, no mutating MemBase/dispatch calls).
"""

from __future__ import annotations

import ast
import importlib.util
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

_MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "api_harness_stewardship_monitor.py"

_spec = importlib.util.spec_from_file_location("api_harness_stewardship_monitor", _MODULE_PATH)
assert _spec and _spec.loader
mon = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mon)


class _FakeDB:
    def __init__(self, items):
        self._items = items

    def list_work_items(self):
        return list(self._items)


def _fake_db_factory(_items):
    def factory(_project_root):
        return _FakeDB(_items)

    return factory


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    poller = tmp_path / ".gtkb-state" / "bridge-poller"
    poller.mkdir(parents=True)
    (poller / "dispatch-state.json").write_text(
        json.dumps(
            {
                "recipients": {
                    "loyal-opposition:D": {
                        "last_result": "provider_failure_backoff_active",
                        "circuit_breaker_tripped": True,
                        "failure_count": 5,
                        "updated_at": "2026-06-18T21:00:00Z",
                    },
                    "loyal-opposition:F": {
                        "last_result": "unchanged",
                        "circuit_breaker_tripped": False,
                        "failure_count": 0,
                        "updated_at": "2026-06-18T21:00:00Z",
                    },
                }
            }
        ),
        encoding="utf-8",
    )
    # Main failures file + a rotated sibling (both must be read).
    (poller / "dispatch-failures.jsonl").write_text(
        json.dumps({"recipient": "loyal-opposition:D", "reason": "max_turn_exhaustion"}) + "\n",
        encoding="utf-8",
    )
    (poller / "dispatch-failures.jsonl.1").write_text(
        json.dumps({"recipient": "loyal-opposition:D", "reason": "max_turn_exhaustion"})
        + "\n"
        + json.dumps({"recipient": "loyal-opposition:F", "reason": "spawn_rate_limited"})
        + "\n",
        encoding="utf-8",
    )

    hstate = tmp_path / "harness-state"
    hstate.mkdir()
    (hstate / "harness-registry.json").write_text(
        json.dumps(
            {
                "harnesses": [
                    {"id": "D", "role": ["loyal-opposition"], "status": "active"},
                    {"id": "F", "role": ["loyal-opposition"], "status": "active"},
                ]
            }
        ),
        encoding="utf-8",
    )
    (hstate / "harness-identities.json").write_text(json.dumps({"B": "claude"}), encoding="utf-8")

    api = tmp_path / ".api-harness"
    api.mkdir()
    (api / "routing.toml").write_text(
        "schema_version = 1\n\n"
        '[models.qwen-local]\nmodel_id = "qwen"\nprovider = "ollama"\n\n'
        '[models.deepseek]\nmodel_id = "deepseek"\nprovider = "openrouter"\n\n'
        '[routing]\ndefault_model = "qwen-local"\n',
        encoding="utf-8",
    )

    rules = tmp_path / "config" / "dispatcher"
    rules.mkdir(parents=True)
    (rules / "rules.toml").write_text(
        "[harnesses.D]\ndispatch_cost = 5\ndispatch_quality = 62\n"
        "dispatch_availability = 95\ncan_receive_dispatch = true\n\n"
        "[harnesses.F]\ndispatch_cost = 20\ndispatch_quality = 72\n"
        "dispatch_availability = 90\ncan_receive_dispatch = true\n",
        encoding="utf-8",
    )

    bridge = tmp_path / "bridge"
    bridge.mkdir()
    (bridge / "some-thread-001.md").write_text("NEW\n\n# proposal\n", encoding="utf-8")
    return tmp_path


# --- surface readers ------------------------------------------------------


def test_dispatch_surface_reads_state_and_rotated_failures(project_root: Path):
    surface = mon.read_dispatch_surface(project_root)
    assert surface["status"] == "ok"
    d = surface["per_harness"]["D"]
    assert d["present"] and d["circuit_breaker_tripped"] and d["failure_count"] == 5
    # max_turn_exhaustion counted across the main file AND the rotated sibling.
    assert d["failure_reasons"].get("max_turn_exhaustion") == 2
    assert surface["per_harness"]["F"]["failure_reasons"].get("spawn_rate_limited") == 1


def test_harness_surface_normalizes_registry(project_root: Path):
    surface = mon.read_harness_surface(project_root)
    assert surface["status"] == "ok" and surface["identities_present"]
    assert surface["per_harness"]["D"]["present"]
    assert surface["per_harness"]["D"]["role"] == ["loyal-opposition"]


def test_routing_surface_groups_by_provider(project_root: Path):
    surface = mon.read_routing_surface(project_root)
    assert surface["status"] == "ok"
    assert "qwen-local" in surface["per_provider"]["ollama"]
    assert "deepseek" in surface["per_provider"]["openrouter"]
    assert surface["default_model"] == "qwen-local"


def test_cost_quality_surface_reads_static_rules(project_root: Path):
    surface = mon.read_cost_quality_surface(project_root)
    assert surface["per_harness"]["D"]["dispatch_quality"] == 62
    assert surface["per_harness"]["F"]["dispatch_cost"] == 20


def test_bridge_surface_counts_actionable_latest(project_root: Path):
    surface = mon.read_bridge_surface(project_root)
    assert surface["status"] == "ok"
    assert surface["actionable_pending"] == 1


def test_readiness_surface_uses_injected_probe(project_root: Path):
    calls: list[str] = []

    def probe(harness_id: str):
        calls.append(harness_id)
        return {"probed": True, "status": "reachable"}

    surface = mon.read_readiness_surface(probe)
    assert sorted(calls) == ["D", "F"]
    assert surface["per_harness"]["D"]["status"] == "reachable"


def test_membase_surface_uses_injected_factory(project_root: Path):
    items = [
        {"title": "Ollama worker crash", "stage": "backlogged"},
        {"title": "OpenRouter timeout", "stage": "verified"},  # terminal -> excluded
        {"title": "unrelated", "stage": "backlogged"},
    ]
    surface = mon.read_membase_surface(project_root, db_factory=_fake_db_factory(items))
    assert surface["status"] == "ok"
    assert surface["per_harness"]["D"]["open_related_work_items"] == 1  # ollama, non-terminal
    assert surface["per_harness"]["F"]["open_related_work_items"] == 0  # openrouter only terminal


def test_surface_readers_defensive_on_missing(tmp_path: Path):
    # Empty project root: every reader degrades to "unknown" rather than raising.
    assert mon.read_dispatch_surface(tmp_path)["status"] == "unknown"
    assert mon.read_harness_surface(tmp_path)["status"] == "unknown"
    assert mon.read_routing_surface(tmp_path)["status"] == "unknown"
    assert mon.read_bridge_surface(tmp_path)["status"] == "unknown"
    assert mon.read_membase_surface(tmp_path, db_factory=_fake_db_factory([]))["status"] == "unknown"


# --- risk scoring ---------------------------------------------------------


def test_risk_scoring_elevated_with_cited_evidence(project_root: Path):
    dispatch = mon.read_dispatch_surface(project_root)
    bridge = mon.read_bridge_surface(project_root)
    risk = mon.score_stuck_work_risk("D", dispatch, bridge)
    assert risk["risk"] == "elevated"
    text = " ".join(risk["evidence"])
    assert "circuit_breaker_tripped" in text
    assert "provider_failure_backoff_active" in text
    assert "fatal dispatch-failure" in text


def test_risk_scoring_healthy_is_none():
    dispatch = {
        "per_harness": {
            "F": {
                "recipient_key": "loyal-opposition:F",
                "last_result": "unchanged",
                "circuit_breaker_tripped": False,
                "failure_count": 0,
                "failure_reasons": {},
            }
        }
    }
    risk = mon.score_stuck_work_risk("F", dispatch, {"actionable_pending": 0})
    assert risk["risk"] == "none"
    assert risk["evidence"] == []


# --- material-change detection -------------------------------------------


def test_material_change_detection_baseline_unchanged_changed():
    cur = {"D": {"risk": "elevated", "dispatch_last_result": "previous_launch_failed"}}
    baseline = mon.detect_material_changes(None, cur)
    assert baseline == [{"harness": "D", "kind": "baseline", "fields": {}}]

    unchanged = mon.detect_material_changes(cur, cur)
    assert unchanged == []

    changed = mon.detect_material_changes(
        {"D": {"risk": "none", "dispatch_last_result": "previous_launch_failed"}}, cur
    )
    assert changed[0]["kind"] == "changed"
    assert changed[0]["fields"]["risk"] == {"from": "none", "to": "elevated"}


# --- end-to-end run -------------------------------------------------------


def test_run_emits_reports_only_under_state_subdir(project_root: Path):
    before = {p.relative_to(project_root) for p in project_root.rglob("*") if p.is_file()}
    dispatch_before = (project_root / ".gtkb-state" / "bridge-poller" / "dispatch-state.json").read_bytes()

    report = mon.run(
        project_root,
        readiness_probe=lambda hid: {"probed": False, "status": "not_probed"},
        db_factory=_fake_db_factory([{"title": "Ollama work", "stage": "backlogged"}]),
        now=datetime(2026, 6, 18, 22, 0, 0, tzinfo=UTC),
        run_id="20260618T220000Z",
    )

    assert report["report_only"] is True
    state_root = project_root / ".gtkb-state" / "api-harness-stewardship"
    assert (state_root / "20260618T220000Z" / "report.json").is_file()
    assert (state_root / "20260618T220000Z" / "report.md").is_file()

    # Every newly written file is inside the stewardship state subdir (no mutation elsewhere).
    after = {p.relative_to(project_root) for p in project_root.rglob("*") if p.is_file()}
    new_files = after - before
    assert new_files, "run() should have written report artifacts"
    for rel in new_files:
        assert rel.parts[:2] == (".gtkb-state", "api-harness-stewardship"), rel

    # Read surfaces are untouched (read-only proof).
    dispatch_after = (project_root / ".gtkb-state" / "bridge-poller" / "dispatch-state.json").read_bytes()
    assert dispatch_after == dispatch_before


def test_run_second_pass_reports_no_material_change(project_root: Path):
    kwargs = dict(
        readiness_probe=lambda hid: {"probed": False, "status": "not_probed"},
        db_factory=_fake_db_factory([]),
    )
    mon.run(project_root, run_id="r1", now=datetime(2026, 6, 18, 22, 0, tzinfo=UTC), **kwargs)
    second = mon.run(project_root, run_id="r2", now=datetime(2026, 6, 18, 22, 5, tzinfo=UTC), **kwargs)
    # Same underlying state -> no material change on the second pass.
    assert second["material_changes"] == []


def test_default_readiness_probe_makes_no_network_call():
    result = mon.mock_readiness_probe("D")
    assert result["probed"] is False
    assert result["status"] == "not_probed"


# --- report-only structural proof (AST) ----------------------------------

_NETWORK_FORBIDDEN = {
    "requests",
    "urllib",
    "http",
    "socket",
    "aiohttp",
    "httpx",
    "ftplib",
    "smtplib",
    "subprocess",
}
_MUTATION_FORBIDDEN_SUBSTRINGS = (
    "insert_",
    "update_",
    "resolve_work_item",
    "delete_",
    "promote_",
    "retire_",
)


def test_module_is_report_only_no_network_no_mutation():
    tree = ast.parse(_MODULE_PATH.read_text(encoding="utf-8"))

    imported_roots: set[str] = set()
    mutating_calls: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported_roots.add(node.module.split(".")[0])
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            attr = node.func.attr
            if any(attr.startswith(s) or attr == s.rstrip("_") for s in _MUTATION_FORBIDDEN_SUBSTRINGS):
                mutating_calls.append(attr)

    assert not (imported_roots & _NETWORK_FORBIDDEN), (
        f"network/process import found: {imported_roots & _NETWORK_FORBIDDEN}"
    )
    assert not mutating_calls, f"mutating call(s) found: {mutating_calls}"
