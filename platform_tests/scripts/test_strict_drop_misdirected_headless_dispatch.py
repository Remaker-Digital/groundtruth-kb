"""Slice 10: receiver-side end-to-end regression for both rows of
DCL-SESSION-ROLE-RESOLUTION-001 assertion 1 in both SessionStart dispatchers.

bridge/gtkb-interactive-session-role-override-slice-10-regression-tests-005.md
(Codex GO at -006); revised post Codex NO-GO at -008 F1 to add the
authorized-row coverage that the approved scoping plan
(bridge/gtkb-interactive-session-role-override-scoping-003.md:458-459)
required alongside the misdirected-row coverage.

Module scope (per the slice proposal and the scoping verification plan):

- Assertion 1 has TWO rows in the scoping plan:
    1a. Authorized headless dispatch (env-var present, keyword matches
        receiver's durable role set) -> ``StartupDecision.DISPATCH_AUTHORIZED``.
    1b. Misdirected headless dispatch (env-var present, keyword does NOT
        match) -> ``StartupDecision.STRICT_DROP`` + audit-log entry.
- This module exercises ``_bridge_dispatch_keyword_check`` in BOTH
  dispatchers and asserts the correct decision for each row.
- Misdirected-row (STRICT_DROP) coverage (per the slice proposal):
    A. Claude STRICT_DROP when keyword mode is not in Claude's role set.
    B. Codex STRICT_DROP when keyword mode is not in Codex's role set.
    C. Silent clean exit -- the keyword check returns a (decision, reason)
       tuple without raising.
    D. Audit-log kind correctness -- the JSONL record uses the canonical
       ``misdirected_dispatch_strict_drop`` kind literal.
    E. STRICT_DROP is unaffected by interactive session-role marker
       presence -- the dispatcher's STRICT_DROP logic does not consult the
       marker, only the receiver's durable role set
       (``GOV-SESSION-ROLE-AUTHORITY-001``).
- Authorized-row (DISPATCH_AUTHORIZED) coverage (per the scoping plan and
  Codex NO-GO -008 F1 required revision):
    F. Claude DISPATCH_AUTHORIZED when keyword mode IS in Claude's role set.
    G. Codex DISPATCH_AUTHORIZED when keyword mode IS in Codex's role set.

Existing ``test_canonical_init_keyword_assertions.py`` covers the
GREP-level invariants (audit-log path, set-membership pattern presence)
but no module currently exercises the actual decision behavior end-to-end.
This module is that behavioral regression for both authorized and
misdirected receiver-side rows.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

_DISPATCHERS = {
    "claude": REPO_ROOT / ".claude" / "hooks" / "session_start_dispatch.py",
    "codex": REPO_ROOT / ".codex" / "gtkb-hooks" / "session_start_dispatch.py",
}


def _load_dispatcher(harness: str) -> ModuleType:
    """Load a SessionStart dispatcher module by file path.

    Distinct synthetic module names per harness keep both modules importable
    in the same pytest session without sys.modules collision.
    """
    path = _DISPATCHERS[harness]
    module_name = f"_slice10_strict_drop_{harness}_dispatcher"
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _stage_harness_registry(project_root: Path) -> Path:
    """Stage harness-state files so ``_resolve_own_role_set`` succeeds.

    Mirrors the fixture in test_cross_harness_trigger_durable_keyed_regression.py
    (claude=B=prime-builder, codex=A=loyal-opposition). Both dispatchers'
    ``_resolve_own_role_set`` consults ``harness-state/harness-registry.json``
    via ``load_harness_projection``.
    """
    (project_root / "groundtruth.toml").write_text(
        '[project]\nproject_name = "TestStrictDrop"\nprofile = "dual-agent"\n',
        encoding="utf-8",
    )
    harness_state = project_root / "harness-state"
    harness_state.mkdir(exist_ok=True)
    (harness_state / "harness-identities.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": {"claude": {"id": "B"}, "codex": {"id": "A"}},
            }
        ),
        encoding="utf-8",
    )
    (harness_state / "role-assignments.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": {
                    "B": {"role": "prime-builder", "harness_type": "claude"},
                    "A": {"role": "loyal-opposition", "harness_type": "codex"},
                },
            }
        ),
        encoding="utf-8",
    )
    (harness_state / "harness-registry.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": [
                    {
                        "id": "A",
                        "harness_name": "codex",
                        "harness_type": "codex",
                        "status": "active",
                        "role": ["loyal-opposition"],
                    },
                    {
                        "id": "B",
                        "harness_name": "claude",
                        "harness_type": "claude",
                        "status": "active",
                        "role": ["prime-builder"],
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    return project_root


def _write_session_role_marker(project_root: Path, role: str, session_id: str) -> Path:
    marker = project_root / ".claude" / "session" / "active-session-role.json"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(json.dumps({"role": role, "session_id": session_id}), encoding="utf-8")
    return marker


def _set_dispatch_env(
    monkeypatch: pytest.MonkeyPatch,
    *,
    run_id: str = "dispatch-id-misdirected",
    keyword_mode: str,
) -> None:
    """Set the env vars the dispatch keyword check reads."""
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", run_id)
    monkeypatch.setenv("GTKB_BRIDGE_DISPATCH_KEYWORD", f"::init gtkb {keyword_mode}")


# ---------------------------------------------------------------------------
# Test 1: Claude STRICT_DROP when keyword mode not in Claude's role set.
# ---------------------------------------------------------------------------


def test_claude_strict_drop_when_keyword_mode_outside_role_set(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Claude's HARNESS_NAME is ``claude``; the fixture maps claude=B=prime-builder
    (role set = {pb}). A dispatch with keyword mode ``lo`` is misdirected
    and must return STRICT_DROP.
    """
    project_root = _stage_harness_registry(tmp_path)
    failures_path = tmp_path / "dispatch-failures.jsonl"
    _set_dispatch_env(monkeypatch, keyword_mode="lo")

    dispatcher = _load_dispatcher("claude")
    decision, reason = dispatcher._bridge_dispatch_keyword_check(project_root=project_root, failures_path=failures_path)

    assert decision == dispatcher.StartupDecision.STRICT_DROP, (
        f"Claude expected STRICT_DROP for misdirected keyword mode 'lo'; got {decision!r} ({reason})"
    )
    assert "not in role set" in reason or "misdirected" in reason


# ---------------------------------------------------------------------------
# Test 2: Codex STRICT_DROP when keyword mode not in Codex's role set.
# ---------------------------------------------------------------------------


def test_codex_strict_drop_when_keyword_mode_outside_role_set(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Codex's HARNESS_NAME is ``codex``; the fixture maps codex=A=loyal-opposition
    (role set = {lo}). A dispatch with keyword mode ``pb`` is misdirected
    and must return STRICT_DROP.
    """
    project_root = _stage_harness_registry(tmp_path)
    failures_path = tmp_path / "dispatch-failures.jsonl"
    _set_dispatch_env(monkeypatch, keyword_mode="pb")

    dispatcher = _load_dispatcher("codex")
    decision, reason = dispatcher._bridge_dispatch_keyword_check(project_root=project_root, failures_path=failures_path)

    assert decision == dispatcher.StartupDecision.STRICT_DROP, (
        f"Codex expected STRICT_DROP for misdirected keyword mode 'pb'; got {decision!r} ({reason})"
    )
    assert "not in role set" in reason or "misdirected" in reason


# ---------------------------------------------------------------------------
# Test 3: silent clean exit — STRICT_DROP returns cleanly, no exception.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("harness", sorted(_DISPATCHERS))
def test_strict_drop_returns_cleanly_without_raising(
    harness: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The STRICT_DROP path returns a (decision, reason) tuple cleanly even
    under the fail-closed branch where role-set resolution itself fails.

    This is the silent-clean-exit contract: an unreadable harness-registry
    or any other read failure during role-set resolution must not propagate
    out of ``_bridge_dispatch_keyword_check``; it must be caught and
    converted to a STRICT_DROP audit-and-return.
    """
    # Stage a project root WITHOUT a harness-registry so role-set resolution
    # fails in the fail-closed branch.
    (tmp_path / "groundtruth.toml").write_text(
        '[project]\nproject_name = "TestStrictDropFailClosed"\nprofile = "dual-agent"\n',
        encoding="utf-8",
    )
    failures_path = tmp_path / "dispatch-failures.jsonl"
    _set_dispatch_env(monkeypatch, keyword_mode="pb")

    dispatcher = _load_dispatcher(harness)
    # Must not raise; must return STRICT_DROP per the fail-closed-treat-as-
    # misdirected contract.
    decision, reason = dispatcher._bridge_dispatch_keyword_check(project_root=tmp_path, failures_path=failures_path)

    assert decision == dispatcher.StartupDecision.STRICT_DROP
    assert "could not resolve own role set" in reason or "misdirected" in reason


# ---------------------------------------------------------------------------
# Test 4: audit log uses the canonical kind literal.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "harness,sent_keyword_mode",
    [
        ("claude", "lo"),  # claude is pb; lo is misdirected
        ("codex", "pb"),  # codex is lo; pb is misdirected
    ],
)
def test_strict_drop_audit_log_uses_canonical_kind_literal(
    harness: str,
    sent_keyword_mode: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The STRICT_DROP path appends an audit record with kind
    ``misdirected_dispatch_strict_drop`` to the failures JSONL. Any drift
    in the kind literal would defeat the
    PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001 v2 audit-trail contract:
    investigators searching the JSONL for that specific kind would miss
    the silent-drop events.
    """
    project_root = _stage_harness_registry(tmp_path)
    failures_path = tmp_path / "dispatch-failures.jsonl"
    _set_dispatch_env(monkeypatch, run_id="audit-log-test-run-id", keyword_mode=sent_keyword_mode)

    dispatcher = _load_dispatcher(harness)
    decision, _reason = dispatcher._bridge_dispatch_keyword_check(
        project_root=project_root, failures_path=failures_path
    )
    assert decision == dispatcher.StartupDecision.STRICT_DROP

    assert failures_path.is_file(), "audit log was not written on STRICT_DROP"
    audit_lines = [line for line in failures_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert audit_lines, "audit log file exists but contains no records"
    audit_record = json.loads(audit_lines[-1])
    assert audit_record.get("kind") == "misdirected_dispatch_strict_drop", (
        f"audit kind literal drifted: {audit_record.get('kind')!r}"
    )
    assert audit_record.get("observed_keyword_mode") == sent_keyword_mode
    assert audit_record.get("run_id") == "audit-log-test-run-id"
    assert audit_record.get("own_harness_name") == harness


# ---------------------------------------------------------------------------
# Test 5: STRICT_DROP is unaffected by session-role marker presence.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "harness,sent_keyword_mode,marker_role",
    [
        # Claude is durable-pb; the marker tries to "give it lo authority";
        # the misdirected pb dispatch (own role set = {pb}) matches sent mode
        # but we send LO to force STRICT_DROP regardless of marker.
        ("claude", "lo", "loyal-opposition"),
        # Symmetric Codex case.
        ("codex", "pb", "prime-builder"),
    ],
)
def test_strict_drop_unaffected_by_session_role_marker_presence(
    harness: str,
    sent_keyword_mode: str,
    marker_role: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A session-state marker MUST NOT influence the STRICT_DROP path.

    The interactive session role override (``::init gtkb (pb|lo)``) is an
    in-session surface for SessionStart disclosure, AXIS 2 surface, AUQ
    routing, and attribution. Headless dispatch routing remains keyed to
    the durable role per GOV-SESSION-ROLE-AUTHORITY-001. If the marker
    leaked into the dispatcher's keyword check, a durable-Prime harness
    receiving a dispatched LO keyword could be coerced into accepting the
    work via a planted marker — defeating the receiver-side audit contract.
    """
    project_root = _stage_harness_registry(tmp_path)
    failures_path = tmp_path / "dispatch-failures.jsonl"
    # Plant a marker whose role would "promote" the receiver into accepting
    # the misdirected keyword if the dispatcher consulted markers.
    _write_session_role_marker(project_root, role=marker_role, session_id="S375-marker-influence-test")
    _set_dispatch_env(monkeypatch, keyword_mode=sent_keyword_mode)

    dispatcher = _load_dispatcher(harness)
    decision, reason = dispatcher._bridge_dispatch_keyword_check(project_root=project_root, failures_path=failures_path)

    assert decision == dispatcher.StartupDecision.STRICT_DROP, (
        f"marker presence influenced dispatcher decision: marker_role={marker_role!r}, "
        f"sent_keyword_mode={sent_keyword_mode!r}, decision={decision!r} ({reason})"
    )
    # Audit log still emitted with marker-independent fields.
    audit_record = json.loads(failures_path.read_text(encoding="utf-8").splitlines()[-1])
    assert audit_record["kind"] == "misdirected_dispatch_strict_drop"
    # Audit record must not include any marker-related field name.
    for marker_field in ("session_role", "session_role_marker", "active_session_role", "marker_role"):
        assert marker_field not in audit_record, f"audit record leaked marker field {marker_field!r}: {audit_record!r}"


# ---------------------------------------------------------------------------
# Test 6 (authorized row): DISPATCH_AUTHORIZED when keyword mode matches own
# role set. Added per Codex NO-GO -008 F1 to close the second row of
# DCL-SESSION-ROLE-RESOLUTION-001 assertion 1 that the scoping plan
# (bridge/gtkb-interactive-session-role-override-scoping-003.md:458)
# explicitly required alongside the STRICT_DROP misdirected row at :459.
# ---------------------------------------------------------------------------


def test_claude_dispatch_authorized_when_keyword_mode_matches_role_set(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Claude's HARNESS_NAME is ``claude``; the fixture maps claude=B=prime-builder
    (role set = {pb}). A dispatch with keyword mode ``pb`` matches and must
    return DISPATCH_AUTHORIZED.

    This is the assertion-1 authorized row counterpart to Test 1's STRICT_DROP
    misdirected row: both rows of assertion 1 are exercised in this module so
    the spec-derived verification table maps cleanly onto a single test file.
    """
    project_root = _stage_harness_registry(tmp_path)
    failures_path = tmp_path / "dispatch-failures.jsonl"
    _set_dispatch_env(monkeypatch, run_id="dispatch-id-authorized", keyword_mode="pb")

    dispatcher = _load_dispatcher("claude")
    decision, reason = dispatcher._bridge_dispatch_keyword_check(project_root=project_root, failures_path=failures_path)

    assert decision == dispatcher.StartupDecision.DISPATCH_AUTHORIZED, (
        f"Claude expected DISPATCH_AUTHORIZED for matching keyword mode 'pb'; got {decision!r} ({reason})"
    )
    # No audit-log entry on the authorized path -- the failures JSONL is only
    # written on the misdirected (STRICT_DROP) branch. The authorized path is
    # the happy-path of receiver-side dispatch and intentionally silent.
    assert not failures_path.exists() or failures_path.read_text(encoding="utf-8").strip() == "", (
        f"authorized path must not write to dispatch-failures.jsonl; found: {failures_path.read_text(encoding='utf-8')!r}"
    )


def test_codex_dispatch_authorized_when_keyword_mode_matches_role_set(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Codex's HARNESS_NAME is ``codex``; the fixture maps codex=A=loyal-opposition
    (role set = {lo}). A dispatch with keyword mode ``lo`` matches and must
    return DISPATCH_AUTHORIZED.

    Symmetric counterpart to the Claude authorized test; together with the
    two Test 1/Test 2 STRICT_DROP cases, the four tests cover both
    (harness x assertion-1-row) combinations the scoping plan required.
    """
    project_root = _stage_harness_registry(tmp_path)
    failures_path = tmp_path / "dispatch-failures.jsonl"
    _set_dispatch_env(monkeypatch, run_id="dispatch-id-authorized", keyword_mode="lo")

    dispatcher = _load_dispatcher("codex")
    decision, reason = dispatcher._bridge_dispatch_keyword_check(project_root=project_root, failures_path=failures_path)

    assert decision == dispatcher.StartupDecision.DISPATCH_AUTHORIZED, (
        f"Codex expected DISPATCH_AUTHORIZED for matching keyword mode 'lo'; got {decision!r} ({reason})"
    )
    assert not failures_path.exists() or failures_path.read_text(encoding="utf-8").strip() == "", (
        f"authorized path must not write to dispatch-failures.jsonl; found: {failures_path.read_text(encoding='utf-8')!r}"
    )
