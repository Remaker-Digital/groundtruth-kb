"""Harness-aware `changed_by` resolver for KB-write helpers.

Authority: bridge/gtkb-kb-attribution-harness-aware-003.md (Codex GO at -004).

Resolves `<role>/<harness_name>` for MemBase write attribution. Replaces the
prior pattern where helper scripts hardcoded `prime-builder/claude-code`,
which caused 39 specs + 20 deliberation inserts to be mis-attributed to
Claude during the 2026-05-03 -> 2026-05-05 Codex-as-Prime period.

Three-source priority order for resolution:

1. Explicit kwarg `harness_name` (recommended for new helpers).
2. Environment variable `GTKB_HARNESS_NAME` (set by harness wrappers at
   session start; current default for ad-hoc CLI use under a configured
   harness session).
3. Single Prime Builder slot in `harness-state/role-assignments.json` (only
   when EXACTLY ONE harness is currently assigned `role: "prime-builder"`;
   raises `RuntimeError` if zero or multiple Prime Builders exist).

The resolver does NOT attempt to "infer" the harness from a process ID,
parent-shell name, or any other derived signal. The above three sources
are the only authoritative inputs.

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
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ROLE_ASSIGNMENTS_PATH = PROJECT_ROOT / "harness-state" / "role-assignments.json"
HARNESS_IDENTITIES_PATH = PROJECT_ROOT / "harness-state" / "harness-identities.json"
ENV_VAR_HARNESS_NAME = "GTKB_HARNESS_NAME"


def _load_role_assignments() -> dict[str, dict[str, str]]:
    """Load harness-state/role-assignments.json; return {} on absence."""
    if not ROLE_ASSIGNMENTS_PATH.is_file():
        return {}
    return json.loads(ROLE_ASSIGNMENTS_PATH.read_text(encoding="utf-8")).get("harnesses", {})


def _load_harness_identities() -> dict[str, dict[str, str]]:
    """Load harness-state/harness-identities.json; return {} on absence."""
    if not HARNESS_IDENTITIES_PATH.is_file():
        return {}
    return json.loads(HARNESS_IDENTITIES_PATH.read_text(encoding="utf-8")).get("harnesses", {})


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
        _normalize_role_field,
        ROLE_ACTING_PRIME_BUILDER,
        ROLE_LOYAL_OPPOSITION,
        ROLE_PRIME_BUILDER,
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


def _sole_prime_builder_harness_name() -> str | None:
    """Return the harness_name of the sole Prime Builder, or None if 0 or >1.

    Per IP-8 of gtkb-single-harness-bridge-dispatcher-001: Prime membership is
    set-membership against the role-set wire form. Multi-element role sets
    (single-harness mode) count toward Prime membership iff they contain
    ``prime-builder`` (or the compatibility/provenance value
    ``acting-prime-builder``).
    """
    from scripts.harness_roles import is_prime_builder  # local import: avoid cycle

    assignments = _load_role_assignments()
    prime_ids = [
        hid
        for hid, rec in assignments.items()
        if isinstance(rec, dict) and is_prime_builder(rec)
    ]
    if len(prime_ids) != 1:
        return None
    return _name_for_harness_id(prime_ids[0])


def _resolve_harness_name(harness_name: str | None) -> str | None:
    """Three-source priority resolution; returns name or None if unresolved."""
    if harness_name:
        return harness_name
    env_value = os.environ.get(ENV_VAR_HARNESS_NAME, "").strip()
    if env_value:
        return env_value
    return _sole_prime_builder_harness_name()


def resolve_changed_by(*, harness_name: str | None = None) -> str:
    """Resolve `<role>/<harness_name>` for KB-write attribution.

    Mutating callers MUST use this function (NOT `resolve_changed_by_or_none`)
    per `bridge/gtkb-kb-attribution-harness-aware-004.md` GO Implementation
    Condition 1.

    Priority:
        1. Explicit kwarg `harness_name`.
        2. `GTKB_HARNESS_NAME` env var.
        3. Single Prime Builder slot in `harness-state/role-assignments.json`.

    Raises:
        RuntimeError: if no source resolves a harness, if the harness has
            no role assignment in role-assignments.json, or if priority-3
            finds zero or multiple Prime Builders.
    """
    resolved = _resolve_harness_name(harness_name)
    if not resolved:
        raise RuntimeError(
            "resolve_changed_by: no harness_name resolved. "
            f"Provide explicit kwarg, set ${ENV_VAR_HARNESS_NAME}, "
            f"or ensure exactly one Prime Builder is assigned in {ROLE_ASSIGNMENTS_PATH.name}."
        )
    harness_id = _harness_id_for_name(resolved)
    if not harness_id:
        raise RuntimeError(
            f"resolve_changed_by: harness_name '{resolved}' has no entry in "
            f"{HARNESS_IDENTITIES_PATH.name}."
        )
    role = _role_for_harness_id(harness_id)
    if not role:
        raise RuntimeError(
            f"resolve_changed_by: harness_id '{harness_id}' (harness_name "
            f"'{resolved}') has no role assignment in {ROLE_ASSIGNMENTS_PATH.name}."
        )
    return f"{role}/{resolved}"


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
