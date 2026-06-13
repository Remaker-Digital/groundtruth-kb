# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Executable R1-R5 enforcement for DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001.

Authority: bridge/gtkb-role-resolution-r1-r5-assertion-enforcement-003.md
(Loyal Opposition GO at -004). This module is a regression guard on
already-conforming code: the live role-resolution surfaces currently satisfy
R1-R5; the tests lock that conformance against future drift. A failure here
surfaces a genuine R1-R5 conformance gap (handled by a scoped REVISED proposal),
NOT a reason to weaken the test.

The module mirrors the proven assertion-enforcement structure of
``platform_tests/scripts/test_canonical_init_keyword_assertions.py`` (the backing
test for the sibling ``DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001``).

Spec map (DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001 rules R1-R5 plus its four
declared machine-checkable assertions):

- R1 (envelope hint authoritative) / assertion 2 -> the session marker wins over
  a mismatched durable role.
- R2 (registry fallback only)                     -> the durable registry role is
  consulted only when there is no valid marker hint.
- R3 (dispatcher registry-authoritative) / assn 3 -> the cross-harness trigger
  routes via the registry projection and never the interactive marker.
- R4 (warn, do not override) / assertion 4        -> a mismatch is a warn/audit
  surface: the resolver never raises and the doctor topology check is advisory.
- R5 (no invalidation on mismatch alone) / assn 1 -> no gate rejects/raises/
  drops/DEFERs a verdict, dispatch, or work product SOLELY on a registry status
  or registry-vs-declared role mismatch (clean grep_absent target).

Related specs: ADR-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-001 (the decision),
DCL-SESSION-ROLE-RESOLUTION-001 (the deterministic resolution table),
GOV-SESSION-ROLE-AUTHORITY-001 (durable-vs-session-stated split),
ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001 (interactive override),
DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 (the mirrored exemplar pattern).
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path
from types import ModuleType

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RESOLVER_PATH = PROJECT_ROOT / "scripts" / "session_role_resolution.py"
TRIGGER_PATH = PROJECT_ROOT / "scripts" / "cross_harness_bridge_trigger.py"
CORE_PATH = PROJECT_ROOT / "scripts" / "session_start_dispatch_core.py"
DOCTOR_PATH = PROJECT_ROOT / "groundtruth-kb" / "src" / "groundtruth_kb" / "project" / "doctor.py"
DB_PATH = PROJECT_ROOT / "groundtruth.db"

DCL_ID = "DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001"

# R5 gate set per proposal -003 § Implementation Design. These are the surfaces
# that could plausibly invalidate work on a registry status/role mismatch.
GATE_SET = (
    PROJECT_ROOT / ".claude" / "hooks" / "lo-file-safety-gate.py",
    PROJECT_ROOT / "scripts" / "implementation_authorization.py",
    PROJECT_ROOT / "scripts" / "implementation_start_gate.py",
    PROJECT_ROOT / "scripts" / "session_start_dispatch_core.py",
    PROJECT_ROOT / "scripts" / "cross_harness_bridge_trigger.py",
)


def _read(path: Path) -> str:
    assert path.is_file(), f"Missing file: {path}"
    return path.read_text(encoding="utf-8")


def _load_resolver() -> ModuleType:
    """Load ``scripts/session_role_resolution.py`` for the behavioral R1/R2 tests.

    The module imports ``from scripts.harness_identity import ...`` with a
    ``from harness_identity import ...`` fallback, so both PROJECT_ROOT and the
    ``scripts`` dir must be importable. Resolution is a pure read over
    ``(project_root, args)`` so caching the module in ``sys.modules`` is safe.
    """
    assert RESOLVER_PATH.is_file(), f"Expected resolver at {RESOLVER_PATH}"
    module_name = "session_role_resolution"
    if module_name in sys.modules:
        return sys.modules[module_name]
    for extra in (str(PROJECT_ROOT), str(PROJECT_ROOT / "scripts")):
        if extra not in sys.path:
            sys.path.insert(0, extra)
    spec = importlib.util.spec_from_file_location(module_name, RESOLVER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _extract_function(src: str, name: str) -> str:
    """Return the source of top-level ``def <name>(`` through the next top-level
    ``def ``/``class `` (or EOF).

    Scoping structural greps to a single function prevents an assertion about one
    function from being satisfied by unrelated code elsewhere in the file.
    """
    start_match = re.compile(rf"^def {re.escape(name)}\(", re.MULTILINE).search(src)
    assert start_match is not None, f"function {name!r} not found"
    nxt = re.compile(r"^(def |class )", re.MULTILINE).search(src, start_match.end())
    return src[start_match.start() : nxt.start()] if nxt else src[start_match.start() :]


# ──────────────────────────────────────────────────────────────────────────
# R1 — envelope-hint marker wins over a mismatched durable role (assertion 2)
# ──────────────────────────────────────────────────────────────────────────


def test_r1_marker_role_wins_over_mismatched_durable(tmp_path: Path) -> None:
    """R1 (behavioral): the session marker overrides the durable role.

    Derive the durable baseline dynamically (no marker -> durable fallback), then
    write a marker carrying the OPPOSITE role with a matching session_id. The
    resolver MUST return ``(opposite_role, "marker")``, proving marker-WINS
    semantics over a mismatched durable role — not mere read order.
    """
    mod = _load_resolver()
    baseline_role, baseline_source = mod.resolve_interactive_session_role(
        tmp_path, current_session_id="S-1", harness_name="claude"
    )
    assert baseline_source == "durable_marker_absent"
    assert baseline_role in (mod.ROLE_PRIME, mod.ROLE_LO)

    opposite = mod.ROLE_PRIME if baseline_role == mod.ROLE_LO else mod.ROLE_LO
    marker_path = mod.session_role_marker_path(tmp_path)
    marker_path.parent.mkdir(parents=True, exist_ok=True)
    marker_path.write_text(json.dumps({"role": opposite, "session_id": "S-1"}), encoding="utf-8")

    role, source = mod.resolve_interactive_session_role(tmp_path, current_session_id="S-1", harness_name="claude")
    assert (role, source) == (opposite, "marker"), (
        f"marker role {opposite!r} must override mismatched durable {baseline_role!r}; "
        f"got {(role, source)!r}. R1 (declared-not-detected) regressed."
    )


def test_r1_resolver_reads_marker_before_durable_fallback() -> None:
    """R1 (structural): the resolver reads the marker and returns the marker-wins
    ``return role, "marker"``; its durable fallbacks are exactly the three
    documented marker-absent / invalid-role / stale-session branches.
    """
    body = _extract_function(_read(RESOLVER_PATH), "resolve_interactive_session_role")
    assert "_read_marker(" in body, "resolver must consult the marker before the durable role."
    assert 'return role, "marker"' in body, "resolver missing the marker-wins return (R1 regressed)."
    for source_tag in (
        "durable_marker_absent",
        "durable_marker_invalid_role",
        "durable_marker_stale_session",
    ):
        assert source_tag in body, f"resolver missing documented durable fallback tag {source_tag!r}."


# ──────────────────────────────────────────────────────────────────────────
# R2 — the registry role is a fallback only (consulted with no valid hint)
# ──────────────────────────────────────────────────────────────────────────


def test_r2_registry_is_fallback_only(tmp_path: Path) -> None:
    """R2 (behavioral): the durable registry role is returned only when no valid
    marker hint exists — marker absent, invalid role, or stale session_id.
    """
    mod = _load_resolver()
    marker_path = mod.session_role_marker_path(tmp_path)
    marker_path.parent.mkdir(parents=True, exist_ok=True)

    # Marker absent -> durable fallback.
    role, source = mod.resolve_interactive_session_role(tmp_path, current_session_id="S-1", harness_name="claude")
    assert source == "durable_marker_absent"
    assert role in (mod.ROLE_PRIME, mod.ROLE_LO)
    durable = role

    # Invalid role -> durable fallback (assertion 7).
    marker_path.write_text(json.dumps({"role": "supervisor", "session_id": "S-1"}), encoding="utf-8")
    role, source = mod.resolve_interactive_session_role(tmp_path, current_session_id="S-1", harness_name="claude")
    assert (role, source) == (durable, "durable_marker_invalid_role")

    # Stale session_id -> durable fallback (assertion 6).
    marker_path.write_text(json.dumps({"role": mod.ROLE_PRIME, "session_id": "OTHER"}), encoding="utf-8")
    role, source = mod.resolve_interactive_session_role(tmp_path, current_session_id="S-1", harness_name="claude")
    assert (role, source) == (durable, "durable_marker_stale_session")


# ──────────────────────────────────────────────────────────────────────────
# R3 — dispatcher routing is registry-authoritative (assertion 3)
# ──────────────────────────────────────────────────────────────────────────


def test_r3_dispatcher_routes_via_registry_projection() -> None:
    """R3 (structural): the cross-harness trigger routes via the registry
    projection and never consults the interactive session-role marker.
    """
    src = _read(TRIGGER_PATH)
    assert "load_harness_projection(" in src, "trigger must route via the registry projection (R3)."
    assert "def _resolve_dispatch_target(" in src, "trigger missing the registry-keyed dispatch resolver."
    assert "active-session-role.json" not in src, (
        "dispatch routing must not read the interactive session marker; R3 requires "
        "registry-authoritative routing (declared-not-detected)."
    )


# ──────────────────────────────────────────────────────────────────────────
# R4 — a mismatch is a warn/audit surface, not an override (assertion 4, code)
# ──────────────────────────────────────────────────────────────────────────


def test_r4_mismatch_is_warning_surface_not_override() -> None:
    """R4 (structural): a marker/durable (or registry) mismatch is surfaced as a
    warning/audit, never an override or a raise.

    1. The SessionStart core audits misdirected dispatch to dispatch-failures.jsonl.
    2. The resolver never ``raise``s on a marker/durable disagreement — every
       mismatch branch RETURNS a durable fallback with a source tag.
    3. The doctor's role-set topology check is advisory (``required=False``) and
       carries a WARN (``status="warning"``) path — drift is surfaced, not gated.
    """
    core = _read(CORE_PATH)
    assert "_audit_log_misdirected_dispatch" in core, "core missing the misdirected-dispatch audit surface."
    assert "dispatch-failures.jsonl" in core, "core missing the dispatch-failures.jsonl audit-log path."

    resolver_body = _extract_function(_read(RESOLVER_PATH), "resolve_interactive_session_role")
    raising_lines = [ln for ln in resolver_body.splitlines() if ln.strip().startswith("raise ")]
    assert not raising_lines, (
        f"resolver must not raise on a marker/durable disagreement (R4); found: {raising_lines!r}."
    )

    doctor_check = _extract_function(_read(DOCTOR_PATH), "_check_role_set_topology_consistency")
    assert "required=False" in doctor_check, "role-topology doctor check must be advisory (non-blocking)."
    assert 'status="warning"' in doctor_check, "role-topology doctor check must retain a WARN path (R4)."


# ──────────────────────────────────────────────────────────────────────────
# R5 — no gate invalidates work on a registry mismatch alone (assertion 1)
# ──────────────────────────────────────────────────────────────────────────


def test_r5_no_gate_invalidates_on_registry_mismatch_alone() -> None:
    """R5 (grep_absent): no gate rejects/raises/drops/DEFERs a verdict, dispatch,
    or work product SOLELY on a registry status (suspended / non-functional) or a
    registry-vs-declared role disagreement.

    This is a clean grep_absent target locked against future regression. The
    prompt-role authority emergency fix removed the prior strict-drop carve-out:
    a registry-vs-declared role mismatch is audited, not used to invalidate the
    explicit prompt/dispatch keyword. If a future change legitimately needs one
    of these tokens, the R5 guard must be revisited via a scoped REVISED
    proposal, not silently widened.
    """
    status_tokens = ("suspended", "non-functional", "non_functional")
    for path in GATE_SET:
        src = _read(path)
        for token in status_tokens:
            assert token not in src, (
                f"{path.name} references registry status token {token!r}; R5 forbids invalidating "
                "work solely on a registry status/role mismatch (DCL assertion 1)."
            )

    # Anchor the revised behavior: the dispatch keyword checker may resolve and
    # audit the durable role set, but it must not use STRICT_DROP for mismatch.
    core = _read(CORE_PATH)
    core_body = _extract_function(core, "_bridge_dispatch_keyword_check")
    assert "StartupDecision.STRICT_DROP" not in core_body, (
        "_bridge_dispatch_keyword_check must not invalidate work via STRICT_DROP "
        "on a registry-vs-declared role mismatch."
    )
    assert "own_role_set" in core_body and "_audit_log_misdirected_dispatch" in core_body, (
        "expected durable-role mismatch to remain auditable while prompt keyword authorization proceeds."
    )


# ──────────────────────────────────────────────────────────────────────────
# Meta — the DCL is present in MemBase with R1-R5 in its body
# ──────────────────────────────────────────────────────────────────────────


def test_dcl_role_resolution_authority_001_spec_present() -> None:
    """Meta/sanity: the DCL row exists in MemBase with R1-R5 in its description,
    anchoring this regression guard to the live spec."""
    if not DB_PATH.is_file():
        pytest.skip(f"MemBase not present at {DB_PATH}; spec-presence anchor not checkable in this environment.")
    from groundtruth_kb.db import KnowledgeDB

    db = KnowledgeDB(str(DB_PATH))
    try:
        spec = db.get_spec(DCL_ID)
    finally:
        db.close()

    assert spec is not None, f"{DCL_ID} missing from MemBase."
    description = str(spec.get("description") or "")
    for rule in ("R1", "R2", "R3", "R4", "R5"):
        assert rule in description, f"{DCL_ID} description missing rule marker {rule!r}."
