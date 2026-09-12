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
  a mismatched registry fallback role.
- R2 (registry fallback only)                     -> the dispatcher/default registry role is
  consulted only when there is no valid marker hint.
- R3 (dispatcher registry-authoritative) / assn 3 -> the dispatcher daemon
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
DOCTOR_PATH = PROJECT_ROOT / "groundtruth-kb" / "src" / "groundtruth_kb" / "project" / "doctor.py"
DB_PATH = PROJECT_ROOT / "groundtruth.db"

DCL_ID = "DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001"

# R5 gate set per proposal -003 § Implementation Design. These are the surfaces
# that could plausibly invalidate work on a registry status/role mismatch.
GATE_SET = (PROJECT_ROOT / "scripts" / "implementation_start_gate.py",)
_REGISTRY_STATUS_PATTERNS = (
    re.compile(r"\bsuspended\b", re.IGNORECASE),
    re.compile(r"\bnon[-_]functional\b", re.IGNORECASE),
)
_ROLE_MISMATCH_PATTERNS = (
    re.compile(r"role[-_ ]mismatch\b", re.IGNORECASE),
    re.compile(r"\brole\b.*\bmismatch\b", re.IGNORECASE),
)
_REGISTRY_CONTEXT_TOKENS = ("durable", "harness", "registry", "role")
_R5_INVALIDATION_TOKENS = (
    "block",
    "defer",
    "deny",
    "drop",
    "fail",
    "invalidat",
    "raise",
    "reject",
    "refuse",
    "strict_drop",
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


def _r5_registry_mismatch_invalidation_hits(src: str) -> list[tuple[int, str]]:
    """Find lines that combine registry mismatch evidence with invalidation."""
    hits: list[tuple[int, str]] = []
    for lineno, line in enumerate(src.splitlines(), start=1):
        lowered = line.lower()
        has_registry_context = any(token in lowered for token in _REGISTRY_CONTEXT_TOKENS)
        has_registry_status = any(pattern.search(line) for pattern in _REGISTRY_STATUS_PATTERNS)
        has_role_mismatch = any(pattern.search(line) for pattern in _ROLE_MISMATCH_PATTERNS)
        has_invalidation = any(token in lowered for token in _R5_INVALIDATION_TOKENS)
        if has_registry_context and (has_registry_status or has_role_mismatch) and has_invalidation:
            hits.append((lineno, line.strip()))
    return hits


# ──────────────────────────────────────────────────────────────────────────
# R1 - envelope-hint marker wins over a mismatched registry fallback role (assertion 2)
# ──────────────────────────────────────────────────────────────────────────


def test_r1_marker_role_wins_and_absent_marker_fails_closed(tmp_path: Path) -> None:
    """R1 (behavioral, WI-5933 C1): a valid session marker resolves to its role,
    and absent explicit evidence the resolver FAILS CLOSED with ``None``.

    WI-5933 Slice B (``DCL-SESSION-ROLE-RESOLUTION-001`` v7): the interactive
    resolver never substitutes the dispatcher/default registry role. Without a
    marker the baseline is ``(None, "durable_marker_absent")``; a matching
    marker carrying a valid role still wins (``(role, "marker")``), proving
    marker-WINS semantics without any durable-role substitution.
    """
    mod = _load_resolver()
    # No marker -> fail closed with None (never the durable role).
    baseline_role, baseline_source = mod.resolve_interactive_session_role(
        tmp_path, current_session_id="S-1", harness_name="claude"
    )
    assert baseline_source == "durable_marker_absent"
    assert baseline_role is None

    # A matching valid marker wins.
    marker_path = mod.session_role_marker_path(tmp_path)
    marker_path.parent.mkdir(parents=True, exist_ok=True)
    marker_path.write_text(json.dumps({"role": mod.ROLE_LO, "session_id": "S-1"}), encoding="utf-8")

    role, source = mod.resolve_interactive_session_role(tmp_path, current_session_id="S-1", harness_name="claude")
    assert (role, source) == (mod.ROLE_LO, "marker"), (
        f"marker role {mod.ROLE_LO!r} must resolve as marker evidence; got {(role, source)!r}. "
        f"R1 (declared-not-detected) regressed."
    )


def test_r1_resolver_reads_marker_before_durable_fallback() -> None:
    """R1 (structural): the resolver reads the marker and returns the marker-wins
    ``return role, "marker"``; its durable fallbacks are exactly the three
    documented marker-absent / invalid-role / stale-session branches.
    """
    body = _extract_function(_read(RESOLVER_PATH), "resolve_interactive_session_role")
    assert "_read_marker(" in body, "resolver must consult the marker before the registry fallback role."
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


def test_r2_marker_absent_invalid_or_stale_fails_closed(tmp_path: Path) -> None:
    """R2 (behavioral, WI-5933 C1): absent, invalid, or stale marker evidence
    FAILS CLOSED with ``role is None`` - never the durable registry role.

    WI-5933 Slice B: the dispatcher/default registry role is routing authority
    only and is not an interactive fallback. Each no-valid-hint branch returns
    ``None`` with its preserved ``durable_*`` source string.
    """
    mod = _load_resolver()
    marker_path = mod.session_role_marker_path(tmp_path)
    marker_path.parent.mkdir(parents=True, exist_ok=True)

    # Marker absent -> fail closed (None), never the durable role.
    role, source = mod.resolve_interactive_session_role(tmp_path, current_session_id="S-1", harness_name="claude")
    assert source == "durable_marker_absent"
    assert role is None

    # Invalid role -> fail closed (assertion 7).
    marker_path.write_text(json.dumps({"role": "supervisor", "session_id": "S-1"}), encoding="utf-8")
    role, source = mod.resolve_interactive_session_role(tmp_path, current_session_id="S-1", harness_name="claude")
    assert source == "durable_marker_invalid_role"
    assert role is None

    # Stale session_id -> fail closed (assertion 6).
    marker_path.write_text(json.dumps({"role": mod.ROLE_PRIME, "session_id": "OTHER"}), encoding="utf-8")
    role, source = mod.resolve_interactive_session_role(tmp_path, current_session_id="S-1", harness_name="claude")
    assert source == "durable_marker_stale_session"
    assert role is None


# ──────────────────────────────────────────────────────────────────────────
# R3 — dispatcher routing is registry-authoritative (assertion 3)
# ──────────────────────────────────────────────────────────────────────────


# ──────────────────────────────────────────────────────────────────────────
# R4 — a mismatch is a warn/audit surface, not an override (assertion 4, code)
# ──────────────────────────────────────────────────────────────────────────


# ──────────────────────────────────────────────────────────────────────────
# R5 — no gate invalidates work on a registry mismatch alone (assertion 1)
# ──────────────────────────────────────────────────────────────────────────


def test_r5_registry_mismatch_scan_ignores_application_subject_state() -> None:
    """R5 scan must not false-positive on non-harness application state."""
    src = 'WORK_SUBJECT_APPLICATION_SUSPENDED_REASON = "work_subject_application_suspended"'
    assert _r5_registry_mismatch_invalidation_hits(src) == []


def test_r5_registry_mismatch_scan_catches_actual_invalidation() -> None:
    """R5 scan must still catch registry-status and role-mismatch gates."""
    src = "\n".join(
        (
            'if harness_status == "suspended": raise RuntimeError("block bridge work")',
            "if registry_role_mismatch: return StartupDecision.STRICT_DROP",
        )
    )
    assert _r5_registry_mismatch_invalidation_hits(src) == [
        (1, 'if harness_status == "suspended": raise RuntimeError("block bridge work")'),
        (2, "if registry_role_mismatch: return StartupDecision.STRICT_DROP"),
    ]


def test_r5_no_gate_invalidates_on_registry_mismatch_alone() -> None:
    """R5 (targeted scan): no gate rejects/raises/drops/DEFERs a verdict, dispatch,
    or work product SOLELY on a registry status (suspended / non-functional) or a
    registry-vs-declared role disagreement.

    This is a targeted semantic scan locked against future regression. The
    prompt-role authority emergency fix removed the prior strict-drop carve-out:
    a registry-vs-declared role mismatch is audited, not used to invalidate the
    explicit prompt/dispatch keyword. If a future change legitimately needs one
    of these tokens, the R5 guard must be revisited via a scoped REVISED
    proposal, not silently widened.
    """
    for path in GATE_SET:
        src = _read(path)
        hits = _r5_registry_mismatch_invalidation_hits(src)
        assert hits == [], (
            f"{path.name} appears to invalidate work on a registry status/role mismatch (DCL assertion 1): {hits!r}."
        )


# ──────────────────────────────────────────────────────────────────────────
# Meta — the DCL is present in MemBase with R1-R5 in its body
# ──────────────────────────────────────────────────────────────────────────


# ──────────────────────────────────────────────────────────────────────────
# WI-4781 — GOV-SESSION-ROLE-AUTHORITY-001 dispatcher-only section present
# ──────────────────────────────────────────────────────────────────────────


# ──────────────────────────────────────────────────────────────────────────
# WI-4781 — DCL-SESSION-ROLE-RESOLUTION-001 enforcement gate split (assertion 8)
# ──────────────────────────────────────────────────────────────────────────


def test_dcl_session_role_resolution_001_enforcement_gate_split() -> None:
    """DCL-SESSION-ROLE-RESOLUTION-001 v4+ must contain assertion 8
    (assertion_registry_not_authority_for_enforcement_gates) and the
    Non-dispatcher enforcement gate row in the Resolution Table.

    Authority: DCL-SESSION-ROLE-RESOLUTION-001 assertion 8 per WI-4781.
    """
    if not DB_PATH.is_file():
        pytest.skip(f"MemBase not present at {DB_PATH}; spec-presence anchor not checkable in this environment.")
    from groundtruth_kb.db import KnowledgeDB

    db = KnowledgeDB(str(DB_PATH))
    try:
        spec = db.get_spec("DCL-SESSION-ROLE-RESOLUTION-001")
    finally:
        db.close()

    assert spec is not None, "DCL-SESSION-ROLE-RESOLUTION-001 missing from MemBase."
    assert int(spec.get("version", 0)) >= 4, (
        f"DCL-SESSION-ROLE-RESOLUTION-001 must be at least v4 (WI-4781); found v{spec.get('version')}."
    )
    description = str(spec.get("description") or "")
    assert "Non-dispatcher enforcement gate" in description, (
        "DCL-SESSION-ROLE-RESOLUTION-001 description missing 'Non-dispatcher enforcement gate' "
        "row in the Resolution Table (WI-4781)."
    )
    assert "assertion_registry_not_authority_for_enforcement_gates" in description, (
        "DCL-SESSION-ROLE-RESOLUTION-001 description missing assertion 8 "
        "'assertion_registry_not_authority_for_enforcement_gates' (WI-4781)."
    )
    # Verify the assertion is also in the structured assertions JSON.
    raw_assertions = spec.get("assertions") or "[]"
    assertions = json.loads(raw_assertions) if isinstance(raw_assertions, str) else raw_assertions
    assertion_ids = [a.get("id", "") for a in assertions if isinstance(a, dict)]
    assert "assertion_registry_not_authority_for_enforcement_gates" in assertion_ids, (
        f"DCL-SESSION-ROLE-RESOLUTION-001 assertions JSON missing assertion 8 id "
        f"'assertion_registry_not_authority_for_enforcement_gates'; found: {assertion_ids!r}."
    )
