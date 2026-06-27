"""Spec-derived tests for the cross-harness parity schema (WI-4875, Slice 2).

Verifies ``DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`` assertions
**PARITY-WAIVER-SCHEMA** (typed waiver records) and **PARITY-APPLICABILITY-RULE**
(role-relative / universal resolution) against the live registry and the
additive reader accessors/validators added to
``scripts/check_harness_parity.py``. Hermetic: synthetic registries are
constructed in-test; the live-registry checks are read-only.
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS = _PROJECT_ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import check_harness_parity as parity  # noqa: E402

_KNOWN = {"claude", "codex", "antigravity", "ollama", "cursor", "openrouter"}


def _live_registry() -> dict:
    registry, _ = parity.load_registry(_PROJECT_ROOT)
    return registry


def _wellformed_waiver() -> dict:
    return {
        "capability_id": "hook.advisory-router-scan",
        "harness": "ollama",
        "reason_class": "harness-surface-difference",
        "rationale": "ollama is a cloud-routed shim without a local hook surface",
        "owner_approval_ref": "DELIB-EXAMPLE-0001",
        "review_trigger": "phase-2-role-promotion",
    }


# ── PARITY schema presence + live validity ──────────────────────────────────


def test_parity_schema_version_present() -> None:
    assert _live_registry().get("parity_schema_version") == parity.PARITY_SCHEMA_VERSION


def test_live_registry_schema_valid() -> None:
    # PARITY-WAIVER-SCHEMA + PARITY-APPLICABILITY-RULE: the live registry must
    # validate clean against the schema validator.
    errors = parity.validate_parity_schema(_live_registry(), known_harnesses=_KNOWN)
    assert errors == [], f"live registry parity-schema errors: {errors}"


# ── PARITY-APPLICABILITY-RULE: resolve_applicability ────────────────────────


def test_resolve_applicability_default_role_relative() -> None:
    cap = {"id": "skill.x", "required_for_roles": ["prime-builder"]}
    assert parity.resolve_applicability(cap) == "role-relative"


def test_resolve_applicability_default_universal_when_no_roles() -> None:
    cap = {"id": "skill.y", "required_for_roles": []}
    assert parity.resolve_applicability(cap) == "universal"


def test_resolve_applicability_explicit_universal_override() -> None:
    cap = {"id": "hook.z", "required_for_roles": ["prime-builder"], "applicability": "universal"}
    assert parity.resolve_applicability(cap) == "universal"


def test_live_shared_hook_is_universal() -> None:
    # The session/governance advisory-router-scan hook carries the explicit
    # `applicability = "universal"` override added in Slice 2.
    registry = _live_registry()
    caps = {c.get("id"): c for c in registry.get("capabilities", []) if isinstance(c, dict)}
    assert "hook.advisory-router-scan" in caps
    assert parity.resolve_applicability(caps["hook.advisory-router-scan"]) == "universal"


# ── per-harness surface map ─────────────────────────────────────────────────


def test_surface_map_contains_known_capability() -> None:
    surface_map = parity.build_surface_map(_live_registry())
    assert "skill.kb-query" in surface_map
    harnesses = surface_map["skill.kb-query"]
    assert "claude" in harnesses and "codex" in harnesses
    assert harnesses["claude"]["surface"].endswith("kb-query/SKILL.md")


# ── PARITY-WAIVER-SCHEMA: waiver validation ─────────────────────────────────


def test_waiver_validation_accepts_wellformed() -> None:
    assert parity.validate_parity_waiver(_wellformed_waiver()) == []


def test_waiver_validation_accepts_expiry_instead_of_trigger() -> None:
    waiver = _wellformed_waiver()
    del waiver["review_trigger"]
    waiver["expiry"] = "2026-12-31"
    assert parity.validate_parity_waiver(waiver) == []


def test_waiver_validation_rejects_bad_reason_class() -> None:
    waiver = _wellformed_waiver()
    waiver["reason_class"] = "because-i-said-so"
    errors = parity.validate_parity_waiver(waiver)
    assert any("reason_class" in e for e in errors)


def test_waiver_validation_rejects_missing_required_field() -> None:
    waiver = _wellformed_waiver()
    del waiver["rationale"]
    errors = parity.validate_parity_waiver(waiver)
    assert any("rationale" in e for e in errors)


def test_waiver_validation_rejects_missing_trigger_and_expiry() -> None:
    waiver = _wellformed_waiver()
    del waiver["review_trigger"]
    errors = parity.validate_parity_waiver(waiver)
    assert any("review_trigger" in e or "expiry" in e for e in errors)


# ── validate_parity_schema: synthetic-registry failure modes ────────────────


def test_validate_schema_flags_missing_version() -> None:
    errors = parity.validate_parity_schema({"capabilities": []}, known_harnesses=_KNOWN)
    assert any("parity_schema_version" in e for e in errors)


def test_validate_schema_flags_invalid_applicability() -> None:
    registry = {
        "parity_schema_version": parity.PARITY_SCHEMA_VERSION,
        "capabilities": [{"id": "skill.bad", "applicability": "sometimes"}],
    }
    errors = parity.validate_parity_schema(registry, known_harnesses=_KNOWN)
    assert any("invalid applicability" in e for e in errors)


def test_validate_schema_flags_waiver_unknown_capability() -> None:
    waiver = _wellformed_waiver()
    waiver["capability_id"] = "skill.does-not-exist"
    registry = {
        "parity_schema_version": parity.PARITY_SCHEMA_VERSION,
        "capabilities": [{"id": "hook.advisory-router-scan"}],
        "parity_waivers": [waiver],
    }
    errors = parity.validate_parity_schema(registry, known_harnesses=_KNOWN)
    assert any("matches no registered capability" in e for e in errors)


def test_validate_schema_flags_waiver_unknown_harness() -> None:
    waiver = _wellformed_waiver()
    waiver["harness"] = "nonexistent-harness"
    registry = {
        "parity_schema_version": parity.PARITY_SCHEMA_VERSION,
        "capabilities": [{"id": "hook.advisory-router-scan"}],
        "parity_waivers": [waiver],
    }
    errors = parity.validate_parity_schema(registry, known_harnesses=_KNOWN)
    assert any("not a known harness" in e for e in errors)


# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
