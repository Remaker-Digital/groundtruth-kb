"""Harness-aware `changed_by` resolver for KB-write helpers.

Authority: bridge/gtkb-kb-attribution-harness-aware-003.md (Codex GO at -004).

Resolves `<role>/<harness_name>` for MemBase write attribution. Replaces the
prior pattern where helper scripts hardcoded `prime-builder/claude-code`,
which caused 39 specs + 20 deliberation inserts to be mis-attributed to
Claude during the 2026-05-03 -> 2026-05-05 Codex-as-Prime period.

Harness-name priority order for resolution:

1. Explicit kwarg `harness_name` (recommended for new helpers).
2. Environment variable `GTKB_HARNESS_NAME` (set by harness wrappers at
   session start; current default for ad-hoc CLI use under a configured
   harness session).
3. A single unambiguous open session envelope under `harness-state/*/`.
4. Deterministic vendor runtime signals for the current process.
5. The active Prime Builder fallback harness. When multiple active harnesses
   hold `prime-builder`, priority-3 fallback resolves only if exactly one is
   dispatchable; otherwise the mutating resolver fails closed and the caller
   must provide an explicit harness name. The active-status filter is applied
   upstream by `load_role_assignments`, which returns only `status == "active"`
   harnesses.

Envelope and vendor runtime sources are candidate harness-name selectors only.
The selected name is still validated through the harness identity and role
sources of truth before a mutating caller receives attribution.

For mutating callers, `resolve_changed_by()` raises `RuntimeError` rather
than returning a fallback when no source resolves a harness or when the
resolved harness has no role assignment (Codex F2 fix; fail-closed).

For read-only-test callers, `resolve_changed_by_or_none()` returns `None`
where the mutating variant raises. Mutating callers MUST NOT use the
`_or_none` variant (per GO Implementation Condition 1).
"""

from __future__ import annotations

import json
import os
from collections.abc import Mapping
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ROLE_ASSIGNMENTS_PATH = PROJECT_ROOT / "harness-state" / "harness-registry.json"
HARNESS_IDENTITIES_PATH = PROJECT_ROOT / "harness-state" / "harness-identities.json"
ENV_VAR_HARNESS_NAME = "GTKB_HARNESS_NAME"

_CLAUDE_RUNTIME_ENV_VARS = ("CLAUDECODE", "CLAUDE_CODE_SESSION_ID", "CLAUDE_PROJECT_DIR")
_CODEX_RUNTIME_ENV_VARS = ("CODEX_HOME", "CODEX_THREAD_ID")


def _load_role_assignments() -> dict[str, dict[str, str]]:
    """Load harness role assignments from the registry projection (WI-3342 IP-4).

    Migrated from a direct read of the retired standalone role mirror to the
    DB-backed registry projection via the foundational loader
    ``scripts.harness_roles.load_role_assignments`` (itself projection-backed
    since IP-3). Returns the ``{harness_id: {...}}`` mapping; ``{}`` on absence.
    """
    from scripts.harness_roles import load_role_assignments  # local: avoid cycle

    return load_role_assignments(PROJECT_ROOT).get("harnesses", {})


def _load_harness_identities() -> dict[str, dict[str, str]]:
    """Load harness identities from the registry projection (WI-3342 IP-4).

    Migrated from a direct read of ``harness-state/harness-identities.json`` to
    the DB-backed registry projection via the foundational loader
    ``scripts.harness_identity.load_harness_identities`` (itself
    projection-backed since IP-3). Returns the ``{harness_name: {...}}``
    mapping; ``{}`` on absence.
    """
    from scripts.harness_identity import load_harness_identities  # local: avoid cycle

    return load_harness_identities(PROJECT_ROOT).get("harnesses", {})


def _harness_id_for_name(harness_name: str) -> str | None:
    """Map a harness_name (e.g. 'codex') to its harness ID (e.g. 'A').

    Identities file keys ARE the harness names; each value carries an `id` field.
    """
    identities = _load_harness_identities()
    record = identities.get(harness_name)
    if not isinstance(record, dict):
        return None
    harness_id = record.get("id")
    return harness_id if isinstance(harness_id, str) else None


def _role_for_harness_id(harness_id: str) -> str | None:
    """Return the primary role assigned to a given harness ID, or None if unassigned.

    Per IP-8 of gtkb-single-harness-bridge-dispatcher-001 (Codex GO at -014):
    the durable role record's ``role`` field is a role-set wire form (JSON
    list of role tokens). This helper returns the Prime-first primary role
    string for backward compatibility with attribution call sites that
    expect a scalar. The legacy compatibility/provenance value
    ``acting-prime-builder`` is accepted on READ and treated as
    Prime-equivalent per the Acting-Prime Compatibility Contract.
    """
    from scripts.harness_roles import (  # local import: avoid top-level cycle
        ROLE_ACTING_PRIME_BUILDER,
        ROLE_LOYAL_OPPOSITION,
        ROLE_PRIME_BUILDER,
        _normalize_role_field,
    )

    assignments = _load_role_assignments()
    record = assignments.get(harness_id)
    if not isinstance(record, dict):
        return None
    role_set = _normalize_role_field(record.get("role"))
    if not role_set:
        return None
    if ROLE_PRIME_BUILDER in role_set or ROLE_ACTING_PRIME_BUILDER in role_set:
        return ROLE_PRIME_BUILDER
    if ROLE_LOYAL_OPPOSITION in role_set:
        return ROLE_LOYAL_OPPOSITION
    return None


def _name_for_harness_id(harness_id: str) -> str | None:
    """Reverse-map: harness ID (e.g. 'B') -> harness_name (e.g. 'claude')."""
    identities = _load_harness_identities()
    for name, record in identities.items():
        if isinstance(record, dict) and record.get("id") == harness_id:
            return name
    return None


def _record_can_receive_dispatch(record: Mapping[str, object]) -> bool:
    """Return whether an active role holder can receive headless dispatch.

    Older registry projections exposed only ``event_driven_hooks`` for this
    axis, so keep it as a compatibility fallback for attribution contexts that
    read historical fixtures.
    """
    if "can_receive_dispatch" in record:
        return record.get("can_receive_dispatch") is True
    return record.get("event_driven_hooks") is True


def _active_prime_builder_harness_name() -> str | None:
    """Return the fallback Prime Builder harness_name, or None if ambiguous.

    Per IP-8 of gtkb-single-harness-bridge-dispatcher-001: Prime membership is
    set-membership against the role-set wire form. Multi-element role sets
    (single-harness mode) count toward Prime membership iff they contain
    ``prime-builder`` (or the compatibility/provenance value
    ``acting-prime-builder``).

    Role/status/dispatchability orthogonality: the active-status filter is
    applied upstream by ``load_role_assignments``. When there are multiple active
    Prime Builders, fallback attribution resolves only if exactly one of them is
    dispatchable; otherwise the mutating caller must pass an explicit harness.
    """
    from scripts.harness_roles import is_prime_builder  # local import: avoid cycle

    assignments = _load_role_assignments()
    prime_ids = [hid for hid, rec in assignments.items() if isinstance(rec, dict) and is_prime_builder(rec)]
    if len(prime_ids) == 1:
        return _name_for_harness_id(prime_ids[0])

    dispatchable_prime_ids = [
        hid
        for hid in prime_ids
        if isinstance(assignments.get(hid), dict) and _record_can_receive_dispatch(assignments[hid])
    ]
    if len(dispatchable_prime_ids) != 1:
        return None
    return _name_for_harness_id(dispatchable_prime_ids[0])


def _open_session_envelope_harness_name() -> str | None:
    """Return the single open interactive session envelope harness, if any.

    This is a candidate harness-name source only. It is skipped for headless
    dispatch and ignored when zero or multiple open envelopes exist.
    """
    if os.environ.get("GTKB_BRIDGE_POLLER_RUN_ID"):
        return None
    harness_state_dir = PROJECT_ROOT / "harness-state"
    try:
        envelope_paths = sorted(harness_state_dir.glob("*/session-envelope.json"))
    except OSError:
        return None
    open_harness_names: list[str] = []
    try:
        from scripts.harness_identity import normalize_harness_name  # local: avoid top-level cycle
    except Exception:
        return None

    for envelope_path in envelope_paths:
        try:
            envelope_data = json.loads(envelope_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(envelope_data, dict) or envelope_data.get("status") != "open":
            continue
        raw_name = envelope_data.get("harness_name") or envelope_path.parent.name
        harness_name = normalize_harness_name(str(raw_name))
        if harness_name:
            open_harness_names.append(harness_name)
    if len(open_harness_names) != 1:
        return None
    return open_harness_names[0]


def _harness_name_from_runtime_env() -> str | None:
    """Return a candidate harness name from deterministic vendor env signals."""
    if any(os.environ.get(name) for name in _CLAUDE_RUNTIME_ENV_VARS):
        return "claude"
    if any(os.environ.get(name) for name in _CODEX_RUNTIME_ENV_VARS):
        return "codex"
    return None


def _resolve_harness_name(harness_name: str | None) -> str | None:
    """Priority-order harness-name resolution; returns name or None."""
    if harness_name:
        return harness_name
    env_value = os.environ.get(ENV_VAR_HARNESS_NAME, "").strip()
    if env_value:
        return env_value
    envelope_value = _open_session_envelope_harness_name()
    if envelope_value:
        return envelope_value
    runtime_value = _harness_name_from_runtime_env()
    if runtime_value:
        return runtime_value
    return _active_prime_builder_harness_name()


def _session_role_override(harness_name: str) -> str | None:
    """Return a declared interactive session role for the attribution LABEL, or None.

    Slice 6 of PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE
    (bridge/gtkb-interactive-session-role-override-slice-6-attribution-role-awareness-001.md,
    Codex GO at -002). Per ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001 Decision 1,
    a declared interactive session role overrides the durable role for the
    ``changed_by`` LABEL. This is a LABEL OVERRIDE ONLY: it is layered on top of
    the fail-closed durable resolution in ``resolve_changed_by`` (the durable
    role must already have resolved, preserving the
    ``gtkb-kb-attribution-harness-aware`` mis-attribution invariant).

    Returns the marker role only when a valid interactive marker won the shared
    resolver's interactive resolution; returns ``None`` for durable sources so
    the caller keeps its already-resolved (fail-closed) durable role.

    Excluded in headless dispatch context (``GTKB_BRIDGE_POLLER_RUN_ID`` set):
    durable role remains the attribution authority for dispatched work. (Slice 3
    already clears the marker at every SessionStart in both dispatchers, so a
    headless session has no marker; this guard makes the interactive-only intent
    explicit.)

    ``current_session_id`` is ``None`` in CLI/subprocess attribution context, so
    the resolver's ``marker_session_id_unverified`` branch applies; Slice 3 keeps
    the marker fresh-per-session. Fail-soft: any resolver error returns ``None``
    (keep the durable role); it never masks a durable-attribution failure.
    """
    if os.environ.get("GTKB_BRIDGE_POLLER_RUN_ID"):
        return None
    try:
        from scripts.session_role_resolution import (  # local: avoid top-level cycle
            resolve_interactive_session_role,
        )

        role, source = resolve_interactive_session_role(
            PROJECT_ROOT, current_session_id=None, harness_name=harness_name
        )
    except Exception:
        return None
    if source in ("marker", "marker_session_id_unverified"):
        return role
    return None


def resolve_changed_by(*, harness_name: str | None = None) -> str:
    """Resolve `<role>/<harness_name>` for KB-write attribution.

    Mutating callers MUST use this function (NOT `resolve_changed_by_or_none`)
    per `bridge/gtkb-kb-attribution-harness-aware-004.md` GO Implementation
    Condition 1.

    Priority:
        1. Explicit kwarg `harness_name`.
        2. `GTKB_HARNESS_NAME` env var.
        3. A single open session envelope harness name, skipped under
           headless dispatch.
        4. Deterministic vendor runtime signals.
        5. The active Prime Builder fallback harness. If multiple active Prime
           Builders exist, fallback resolves only when exactly one is
           dispatchable.

    Raises:
        RuntimeError: if no source resolves a harness, if the harness has
            no role assignment in the harness registry projection, or if priority-3
            finds no unambiguous Prime Builder fallback.
    """
    resolved = _resolve_harness_name(harness_name)
    if not resolved:
        raise RuntimeError(
            "resolve_changed_by: no harness_name resolved. "
            f"Provide explicit kwarg, set ${ENV_VAR_HARNESS_NAME}, "
            "or provide one unambiguous active dispatchable Prime Builder "
            f"fallback in {ROLE_ASSIGNMENTS_PATH.name}."
        )
    harness_id = _harness_id_for_name(resolved)
    if not harness_id:
        raise RuntimeError(
            f"resolve_changed_by: harness_name '{resolved}' has no entry in {HARNESS_IDENTITIES_PATH.name}."
        )
    role = _role_for_harness_id(harness_id)
    if not role:
        raise RuntimeError(
            f"resolve_changed_by: harness_id '{harness_id}' (harness_name "
            f"'{resolved}') has no role assignment in {ROLE_ASSIGNMENTS_PATH.name}."
        )
    # Slice 6: a declared interactive session role overrides the durable role for
    # the attribution LABEL (ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001 Decision 1).
    # This is layered AFTER the fail-closed durable resolution above, so the
    # durable role must still resolve (mis-attribution invariant preserved); the
    # marker overrides only the label, and falls back to the durable role when no
    # valid marker is present.
    effective_role = _session_role_override(resolved) or role
    return f"{effective_role}/{resolved}"


def resolve_changed_by_or_none(*, harness_name: str | None = None) -> str | None:
    """Read-only-test variant; returns None where the mutating variant raises.

    Mutating callers MUST NOT use this function. It exists only for test
    fixtures, dry-run helpers, and other read-only paths that want a
    documented "no current harness" sentinel.
    """
    try:
        return resolve_changed_by(harness_name=harness_name)
    except RuntimeError:
        return None
