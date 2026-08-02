"""Disclosure-shape tests for the open session-startup disclosure.

Per SPEC-ENVELOPE-DISCLOSURE-UI-001 and bridge thread
``gtkb-envelope-disclosure-ui-impl`` GO at ``-009``: the open disclosure
renders only the canonical envelope-program sections. These tests pin
section presence/absence + the backlog-pipeline filters that feed the
top-3 priority surface.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "session_self_initialization.py"


@pytest.fixture(autouse=True)
def _isolate_lifecycle_guard_env(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("GTKB_LIFECYCLE_GUARD_PATH", str(tmp_path / "session-lifecycle-guard.json"))


def _load_module():
    spec = importlib.util.spec_from_file_location("session_self_initialization_for_disclosure", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["session_self_initialization_for_disclosure"] = module
    spec.loader.exec_module(module)
    return module


def _render_prime_open_report(module) -> str:
    model = module.build_startup_model(REPO_ROOT, role_profile="prime-builder", fast_hook=True)
    return module.render_report(model, "http://localhost:3000/d/gtkb/groundtruth-kb-dashboard", REPO_ROOT)


def _startup_service_result(module, model: dict, report_text: str) -> dict:
    dashboard_dir = REPO_ROOT / "docs" / "gtkb-dashboard"
    return {
        "project_root": REPO_ROOT,
        "model": model,
        "dashboard_path": REPO_ROOT / "docs" / "gtkb-dashboard" / "grafana" / "dashboards" / "gtkb-dashboard.json",
        "dashboard_url": module.GRAFANA_DASHBOARD_URL,
        "data_path": dashboard_dir / "dashboard-data.json",
        "report_path": dashboard_dir / "session-startup-report.md",
        "report_text": report_text,
        "wrapup_path": dashboard_dir / "session-wrapup-report.md",
        "wrapup_text": "",
    }


# ---- Section absence tests (4 dropped sections per SPEC) -------------------


def test_open_disclosure_omits_work_state_section() -> None:
    module = _load_module()
    report = _render_prime_open_report(module)
    assert "### Work State" not in report


def test_open_disclosure_omits_recommended_session_focus_section() -> None:
    module = _load_module()
    report = _render_prime_open_report(module)
    assert "### Recommended Session Focus" not in report
    assert "Reply with A, B, C, D" not in report
    assert "Or provide a prompt for something else." not in report


def test_open_disclosure_omits_inline_glossary_section() -> None:
    module = _load_module()
    report = _render_prime_open_report(module)
    # The startup glossary helper rendered "### Glossary" at the
    # Startup Disclosure level; the inline section is dropped.
    assert "### Glossary" not in report


def test_open_disclosure_omits_wrap_up_trigger_commands_section() -> None:
    module = _load_module()
    report = _render_prime_open_report(module)
    assert "### Wrap-Up Trigger Commands" not in report
    assert "Accepted wrap-up commands:" not in report


# ---- Section presence tests (kept surfaces) --------------------------------


def test_open_disclosure_includes_role_declaration() -> None:
    module = _load_module()
    report = _render_prime_open_report(module)
    assert "### Role And Governance Stance" in report
    assert "Role being assumed: Prime Builder" in report
    assert "Interactive resolved role: Prime Builder" in report
    assert "Interactive role source:" in report
    # DCL-SESSION-ROLE-RESOLUTION-001 v7: worker disclosure MUST NOT surface the durable registry role.
    assert "Durable registry role" not in report


def test_open_disclosure_includes_bridge_actionable_summary() -> None:
    module = _load_module()
    report = _render_prime_open_report(module)
    # The Current Project State section retains the bridge-actionable rollup.
    assert "### Current Project State" in report
    assert "dashboard-scoped bridge/contention entries" in report


def test_open_disclosure_includes_top_3_priorities_surface() -> None:
    module = _load_module()
    model = module.build_startup_model(REPO_ROOT, role_profile="prime-builder", fast_hook=True)
    report = module.render_report(model, "http://localhost:3000/d/gtkb/groundtruth-kb-dashboard", REPO_ROOT)
    # The canonical top-3 priorities surface MUST appear in the open disclosure.
    assert "### Top Priority Actions" in report
    top_actions = model.get("top_priority_actions") or []
    for entry in top_actions:
        assert entry["id"] in report


def test_open_disclosure_includes_dashboard_link() -> None:
    module = _load_module()
    report = _render_prime_open_report(module)
    assert "GroundTruth-KB Project Dashboard" in report
    assert "http://localhost:3000/d/gtkb/groundtruth-kb-dashboard" in report


def test_init_disclosure_is_minimized_for_routing_only() -> None:
    module = _load_module()
    model = module.build_startup_model(REPO_ROOT, role_profile="prime-builder", fast_hook=True)
    report = module.render_report(model, module.GRAFANA_DASHBOARD_URL, REPO_ROOT)
    disclosure = module._startup_disclosure(_startup_service_result(module, model, report))

    assert "## Startup Disclosure" in disclosure
    assert "### Role And Routing" in disclosure
    assert "### Compact Project State" in disclosure
    assert "### Init Scope" in disclosure
    assert "`::open <activity>`" in disclosure
    assert "### Top Priority Actions" not in disclosure
    assert "## Session Startup" not in disclosure
    assert "### Active Work Subject" not in disclosure


# ---- Backlog projection / pipeline tests -----------------------------------


def test_backlog_items_preserve_status_priority_shape() -> None:
    module = _load_module()
    items = module._backlog_items_from_membase(REPO_ROOT)
    assert items, "expected a non-empty backlog projection from MemBase"
    sample = items[0]
    assert "resolution_status" in sample
    assert "stage" in sample
    assert "priority" in sample


def test_top_3_does_not_filter_by_legacy_approval_metadata(monkeypatch) -> None:
    """Top-3 must not derive priority eligibility from legacy approval metadata."""
    module = _load_module()
    synthetic = [
        {
            "id": "WI-9001",
            "title": "Open item A",
            "body": "",
            "resolution_status": "open",
            "priority": "P1",
        },
        {
            "id": "WI-9002",
            "title": "Open item B",
            "body": "",
            "resolution_status": "open",
            "priority": "P1",
        },
        {
            "id": "WI-9003",
            "title": "Open item C",
            "body": "",
            "resolution_status": "open",
            "priority": "P1",
        },
        {
            "id": "WI-9004",
            "title": "Lower-priority open item",
            "body": "",
            "resolution_status": "open",
            "priority": "P2",
        },
    ]
    monkeypatch.setattr(module, "_backlog_items_from_membase", lambda root: synthetic)
    monkeypatch.setattr(module, "_bridge_latest_status", lambda root: {})
    # Synthetic WI ids have no scope-classifier signal; pin to a primary-included
    # scope so the visible-items filter does not drop them.
    monkeypatch.setattr(module, "classify_dashboard_scope", lambda row: "agent_red_product")
    metrics, top = module._backlog_metrics(REPO_ROOT)
    top_ids = [item["id"] for item in top]
    assert top_ids == ["WI-9001", "WI-9002", "WI-9003"]
    # Same list at both consumption sites
    assert metrics["top_priority_actions"] == top


def test_top_3_excludes_resolved_and_verified_wis(monkeypatch) -> None:
    """Top-3 must drop items whose resolution_status is terminal."""
    module = _load_module()
    synthetic = [
        {
            "id": "WI-9100",
            "title": "Open item",
            "body": "",
            "resolution_status": "open",
            "priority": "P1",
        },
        {
            "id": "WI-9101",
            "title": "Resolved item",
            "body": "",
            "resolution_status": "resolved",
            "priority": "P1",
        },
        {
            "id": "WI-9102",
            "title": "Verified item",
            "body": "",
            "resolution_status": "verified",
            "priority": "P1",
        },
    ]
    monkeypatch.setattr(module, "_backlog_items_from_membase", lambda root: synthetic)
    monkeypatch.setattr(module, "_bridge_latest_status", lambda root: {})
    # Synthetic WI ids have no scope-classifier signal; pin to a primary-included
    # scope so the visible-items filter does not drop them.
    monkeypatch.setattr(module, "classify_dashboard_scope", lambda row: "agent_red_product")
    metrics, top = module._backlog_metrics(REPO_ROOT)
    top_ids = [item["id"] for item in top]
    assert "WI-9100" in top_ids
    assert "WI-9101" not in top_ids
    assert "WI-9102" not in top_ids


def test_top_priority_dict_and_tuple_are_identical(monkeypatch) -> None:
    """``top_priority_actions`` in the metrics dict must equal the tuple return."""
    module = _load_module()
    monkeypatch.setattr(
        module,
        "_backlog_items_from_membase",
        lambda root: [
            {
                "id": "WI-9200",
                "title": "Item",
                "body": "",
                "resolution_status": "open",
                "priority": "P1",
            }
        ],
    )
    monkeypatch.setattr(module, "_bridge_latest_status", lambda root: {})
    metrics, top = module._backlog_metrics(REPO_ROOT)
    assert metrics["top_priority_actions"] == top
    # Identical sequence, not just equal lengths.
    assert [item["id"] for item in metrics["top_priority_actions"]] == [item["id"] for item in top]


def test_top_3_selection_is_deterministic(monkeypatch) -> None:
    module = _load_module()
    synthetic = [
        {
            "id": f"WI-9{i:03d}",
            "title": f"Item {i}",
            "body": "",
            "resolution_status": "open",
            "priority": "P1",
        }
        for i in range(300, 310)
    ]
    monkeypatch.setattr(module, "_backlog_items_from_membase", lambda root: synthetic)
    monkeypatch.setattr(module, "_bridge_latest_status", lambda root: {})
    # Synthetic WI ids have no scope-classifier signal; pin to a primary-included
    # scope so the visible-items filter does not drop them.
    monkeypatch.setattr(module, "classify_dashboard_scope", lambda row: "agent_red_product")
    first_metrics, first_top = module._backlog_metrics(REPO_ROOT)
    second_metrics, second_top = module._backlog_metrics(REPO_ROOT)
    assert [item["id"] for item in first_top] == [item["id"] for item in second_top]
    assert first_metrics["top_priority_actions"] == second_metrics["top_priority_actions"]


def test_top_3_selection_priority_then_wi_id(monkeypatch) -> None:
    """Top-3 sorts eligible items by priority, then stable work-item id.

    Given open items, the first three highest-priority stable ids are selected.
    """
    module = _load_module()
    synthetic = [
        {
            "id": "WI-9400",
            "title": "First",
            "body": "",
            "resolution_status": "open",
            "priority": "P1",
        },
        {
            "id": "WI-9401",
            "title": "Second",
            "body": "",
            "resolution_status": "open",
            "priority": "P1",
        },
        {
            "id": "WI-9402",
            "title": "Third",
            "body": "",
            "resolution_status": "open",
            "priority": "P1",
        },
        {
            "id": "WI-9403",
            "title": "Fourth (excluded)",
            "body": "",
            "resolution_status": "open",
            "priority": "P2",
        },
    ]
    monkeypatch.setattr(module, "_backlog_items_from_membase", lambda root: synthetic)
    monkeypatch.setattr(module, "_bridge_latest_status", lambda root: {})
    # Synthetic WI ids have no scope-classifier signal; pin to a primary-included
    # scope so the visible-items filter does not drop them.
    monkeypatch.setattr(module, "classify_dashboard_scope", lambda row: "agent_red_product")
    _, top = module._backlog_metrics(REPO_ROOT)
    assert [item["id"] for item in top] == ["WI-9400", "WI-9401", "WI-9402"]


def test_wrap_trigger_helper_preserved_for_capstone_reuse() -> None:
    """``WRAPUP_TRIGGER_COMMANDS`` and ``_render_wrapup_trigger_commands`` must
    remain importable from the module so the WI-4301 capstone can reuse them."""
    module = _load_module()
    assert hasattr(module, "WRAPUP_TRIGGER_COMMANDS")
    assert isinstance(module.WRAPUP_TRIGGER_COMMANDS, tuple)
    assert "wrap up" in module.WRAPUP_TRIGGER_COMMANDS
    assert hasattr(module, "_render_wrapup_trigger_commands")
    rendered = module._render_wrapup_trigger_commands()
    assert "Accepted wrap-up commands:" in rendered
    assert "`wrap up`" in rendered


# ---- TEST-11254: initial skill/knowledge shard migration (WI-4949) ---------


def test_test11254_startup_glossary_loads_core_subset_not_full_corpus() -> None:
    """SPEC-INTAKE-46594e: base startup uses bounded core primer, not full glossary."""
    from scripts.startup_glossary_load import load_glossary_for_startup

    result = load_glossary_for_startup(REPO_ROOT)
    assert result["status"] == "loaded"
    assert result["scope"] == "core_startup"
    assert int(result["term_count"]) <= int(result["full_term_count"])
    assert int(result["full_term_count"]) > int(result["term_count"])


def test_test11254_global_baseline_excludes_activity_only_codex_surfaces() -> None:
    """Deferred Codex LO surfaces must not appear in global_baseline allowed_surfaces."""
    import tomllib

    sharding_path = REPO_ROOT / "config" / "agent-control" / "activity-envelope-sharding.toml"
    sharding = tomllib.loads(sharding_path.read_text(encoding="utf-8"))
    global_surfaces = set(sharding["classes"]["global_baseline"]["allowed_surfaces"])
    deferred = set(sharding["classes"]["activity_only"]["deferred_surfaces"])
    assert deferred, "activity_only deferred_surfaces must be declared"
    assert not global_surfaces.intersection(deferred)


def test_test11254_readiness_both_roles_build_startup_model() -> None:
    """Readiness: Prime Builder and LO startup models build without activity shards."""
    module = _load_module()
    for role in ("prime-builder", "loyal-opposition"):
        model = module.build_startup_model(REPO_ROOT, role_profile=role, fast_hook=True)
        assert isinstance(model, dict)
        assert model.get("role_profile") == role


def test_test11254_init_disclosure_points_to_open_activity() -> None:
    """Minimized init disclosure routes activity context to ::open <activity>."""
    module = _load_module()
    model = module.build_startup_model(REPO_ROOT, role_profile="prime-builder", fast_hook=True)
    report = module.render_report(model, module.GRAFANA_DASHBOARD_URL, REPO_ROOT)
    disclosure = module._startup_disclosure(_startup_service_result(module, model, report))
    assert "`::open <activity>`" in disclosure
    assert "### Init Scope" in disclosure
