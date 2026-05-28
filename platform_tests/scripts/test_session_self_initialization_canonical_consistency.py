"""Tests for the canonical-state derivation in the startup-payload render path.

Per the GO of ``bridge/gtkb-startup-payload-canonical-state-drift-004.md`` IP-1
scope. Each test maps to a Specification Link cited in
``bridge/gtkb-startup-payload-canonical-state-drift-003.md`` Specification-Derived
Verification Plan. Verifies that ``_render_current_project_state`` derives
``role_slot`` and ``topology_mode`` from live ``harness-state/role-assignments.json``
rather than from a stale persisted ``workstream_focus`` snapshot.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from typing import Any

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS_DIR = _PROJECT_ROOT / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

ssi = importlib.import_module("session_self_initialization")


def _write_role_map(root: Path, role_map: dict[str, Any]) -> None:
    """Seed the harness registry projection (WI-3342 IP-3/IP-4).

    ``_render_current_project_state`` resolves the role map through
    ``load_role_assignments``, migrated to read the DB-backed registry
    projection ``harness-state/harness-registry.json`` (``harnesses`` is a LIST
    of unified records each carrying ``id`` + ``role``). This helper accepts
    the legacy ``{"harnesses": {harness_id: record}}`` dict input and writes
    the equivalent projection LIST so each test's verification intent — the
    rendered role-slot / topology line — is preserved.
    """
    harnesses_in = role_map.get("harnesses", {})
    records = [{"id": harness_id, **record} for harness_id, record in harnesses_in.items()]
    registry_path = root / "harness-state" / "harness-registry.json"
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(json.dumps({"harnesses": records}, indent=2) + "\n", encoding="utf-8")


def _make_model(
    *,
    workstream_focus: dict[str, Any] | None = None,
    role: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the minimum model dict ``_render_current_project_state`` reads.

    Sets ``app_green=False`` and ``gtkb_green=False`` so the readiness
    subject-scope assertion does not fire.
    """
    return {
        "metrics": {
            "backlog": {"active_item_count": 0},
            "membase": {"open_work_items": 0},
            "contention": {"actionable_count": 0},
            "drift": {"changed_path_count": 0},
            "regression": {"release_blocker_count": 0},
        },
        "dashboard_intelligence": {
            "release_readiness": {"blocker_count": 0},
            "quality_rollup": {"failing": 0, "manual": 0, "ready_or_passing": 0},
            "dual_scope_declared": False,
            "subject_readiness": {
                "application_green": False,
                "gtkb_green": False,
            },
        },
        "infrastructure": {
            "gtkb_upgrade_posture": {},
            "dev_environment_inventory": {},
            "harness_parity": {},
        },
        "workstream_focus": workstream_focus or {},
        "role": role or {},
    }


@pytest.fixture
def project_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect the render-time role-map read to tmp_path."""
    monkeypatch.setattr(ssi, "_PROJECT_ROOT_FOR_IMPORTS", tmp_path)
    return tmp_path


def test_topology_label_matches_role_map_cardinality_two_singletons(project_root: Path) -> None:
    """Two singleton harnesses -> rendered topology line shows ``multi_harness``."""
    _write_role_map(
        project_root,
        {
            "harnesses": {
                "A": {"role": ["loyal-opposition"]},
                "B": {"role": ["prime-builder"]},
            }
        },
    )
    model = _make_model(role={"harness_id": "B"})
    rendered = ssi._render_current_project_state(model)
    assert "Harness topology: `multi_harness`" in rendered


def test_topology_label_matches_role_map_cardinality_one_multi_role(project_root: Path) -> None:
    """One harness with both roles -> rendered topology line shows ``single_harness``."""
    _write_role_map(
        project_root,
        {
            "harnesses": {
                "A": {"role": ["prime-builder", "loyal-opposition"]},
            }
        },
    )
    model = _make_model(role={"harness_id": "A"})
    rendered = ssi._render_current_project_state(model)
    assert "Harness topology: `single_harness`" in rendered


def test_topology_label_matches_canonical_fail_closed_for_empty_role_map(project_root: Path) -> None:
    """Empty role-map -> canonical fail-closed ``multi_harness`` (NOT the prior ``single_harness`` literal default)."""
    _write_role_map(project_root, {"harnesses": {}})
    model = _make_model(role={"harness_id": "B"})
    rendered = ssi._render_current_project_state(model)
    assert "Harness topology: `multi_harness`" in rendered


def test_role_slot_renders_singleton_role_token_prime(project_root: Path) -> None:
    """Active harness B with singleton ``["prime-builder"]`` -> rendered slot shows ``prime-builder``."""
    _write_role_map(
        project_root,
        {
            "harnesses": {
                "A": {"role": ["loyal-opposition"]},
                "B": {"role": ["prime-builder"]},
            }
        },
    )
    model = _make_model(role={"harness_id": "B"})
    rendered = ssi._render_current_project_state(model)
    assert "Bridge role slot: `prime-builder`" in rendered


def test_role_slot_renders_singleton_role_token_lo(project_root: Path) -> None:
    """Active harness A with singleton ``["loyal-opposition"]`` -> rendered slot shows ``loyal-opposition``."""
    _write_role_map(
        project_root,
        {
            "harnesses": {
                "A": {"role": ["loyal-opposition"]},
                "B": {"role": ["prime-builder"]},
            }
        },
    )
    model = _make_model(role={"harness_id": "A"})
    rendered = ssi._render_current_project_state(model)
    assert "Bridge role slot: `loyal-opposition`" in rendered


def test_role_slot_renders_shared_for_multi_element(project_root: Path) -> None:
    """Active harness with multi-element role-set -> rendered slot shows ``shared``."""
    _write_role_map(
        project_root,
        {
            "harnesses": {
                "A": {"role": ["prime-builder", "loyal-opposition"]},
            }
        },
    )
    model = _make_model(role={"harness_id": "A"})
    rendered = ssi._render_current_project_state(model)
    assert "Bridge role slot: `shared`" in rendered


def test_role_slot_renders_shared_for_missing_active_harness(project_root: Path) -> None:
    """Active harness ID not in role-map -> canonical fail-safe ``shared``."""
    _write_role_map(
        project_root,
        {
            "harnesses": {
                "A": {"role": ["loyal-opposition"]},
                "B": {"role": ["prime-builder"]},
            }
        },
    )
    model = _make_model(role={"harness_id": "C"})
    rendered = ssi._render_current_project_state(model)
    assert "Bridge role slot: `shared`" in rendered


def test_render_ignores_stale_persisted_workstream_state(project_root: Path) -> None:
    """Stale persisted ``workstream_focus`` is overridden by canonical derivation.

    Persisted state says ``single_harness`` + ``shared``; live role-map has
    two singletons (multi-harness). Render should reflect the live state.
    """
    _write_role_map(
        project_root,
        {
            "harnesses": {
                "A": {"role": ["loyal-opposition"]},
                "B": {"role": ["prime-builder"]},
            }
        },
    )
    model = _make_model(
        workstream_focus={
            "role_slot": "shared",
            "topology_mode": "single_harness",
        },
        role={"harness_id": "B"},
    )
    rendered = ssi._render_current_project_state(model)
    assert "Harness topology: `multi_harness`" in rendered
    assert "Bridge role slot: `prime-builder`" in rendered
    # Stale persisted values should NOT appear in the render
    assert "Harness topology: `single_harness`" not in rendered


def test_topology_label_canonical_fail_closed_for_missing_role_map_file(project_root: Path) -> None:
    """Per -006 F1: no role-map file at the expected path -> canonical fail-closed.

    The render path must always pass through ``topology_from_role_map`` /
    ``role_slot_from_active_harness``, even when the role-map file is absent,
    so the canonical helpers' fail-closed semantics (``multi_harness`` /
    ``shared``) survive.
    """
    # No role-map file is written; the path does not exist. WI-3342 IP-3/IP-4:
    # the role-map file the render path reads is the registry projection.
    assert not (project_root / "harness-state" / "harness-registry.json").exists()
    model = _make_model(role={"harness_id": "B"})
    rendered = ssi._render_current_project_state(model)
    assert "Harness topology: `multi_harness`" in rendered
    assert "Bridge role slot: `shared`" in rendered
    # The literal single_harness fallback that -006 F1 cited must NOT appear
    assert "Harness topology: `single_harness`" not in rendered


def test_topology_label_canonical_fail_closed_for_malformed_role_map_json(
    project_root: Path,
) -> None:
    """Per -006 F1: malformed JSON in role-map file -> canonical fail-closed.

    JSON decode failure must yield an empty role_map dict passed through the
    canonical helper, returning ``multi_harness`` / ``shared`` per the helper's
    fail-closed contract.

    WI-3342 IP-3/IP-4: the role-map file the render path reads is the registry
    projection ``harness-state/harness-registry.json``.
    """
    registry_path = project_root / "harness-state" / "harness-registry.json"
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text("{not valid json,,,", encoding="utf-8")
    model = _make_model(role={"harness_id": "B"})
    rendered = ssi._render_current_project_state(model)
    assert "Harness topology: `multi_harness`" in rendered
    assert "Bridge role slot: `shared`" in rendered
    assert "Harness topology: `single_harness`" not in rendered
