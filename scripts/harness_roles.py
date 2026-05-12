"""Single source of truth for GT-KB harness role assignment.

IP-8 of bridge/gtkb-single-harness-bridge-dispatcher-001-013.md (Codex GO at
-014) migrates this module from scalar role-string semantics to role-set
semantics. The wire form of ``harness-state/role-assignments.json`` is now a
JSON list of role tokens (the wire representation of a role set); the
in-process form is ``frozenset[str]``. Legacy scalar values are accepted on
READ and upgraded to list form on first WRITE.

Authority: ADR-SINGLE-HARNESS-OPERATING-MODE-001 (Path 2 atomic migration);
``.claude/rules/operating-role.md`` § Role Set Schema (Active Authority).
"""

from __future__ import annotations

import json
import os
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:
    from scripts.harness_identity import (
        DEFAULT_HARNESS_IDS as _DEFAULT_HARNESS_IDS,
    )
    from scripts.harness_identity import (
        normalize_harness_id,
        normalize_harness_name,
    )
    from scripts.harness_identity import (
        resolved_harness_id as _resolved_persistent_harness_id,
    )
except ImportError:  # pragma: no cover - direct script execution path
    from harness_identity import (  # type: ignore[no-redef]
        DEFAULT_HARNESS_IDS as _DEFAULT_HARNESS_IDS,
    )
    from harness_identity import (
        normalize_harness_id,
        normalize_harness_name,
    )
    from harness_identity import (
        resolved_harness_id as _resolved_persistent_harness_id,
    )

ROLE_PRIME_BUILDER = "prime-builder"
ROLE_LOYAL_OPPOSITION = "loyal-opposition"
# Compatibility/provenance value (per
# .claude/rules/acting-prime-builder.md § Compatibility/Provenance
# Classification). Accepted on READ; rejected on SET.
ROLE_ACTING_PRIME_BUILDER = "acting-prime-builder"

# READ vocabulary includes the legacy compatibility/provenance value so older
# role-assignments.json records continue to load without error.
VALID_ROLES_FOR_READ = frozenset({
    ROLE_PRIME_BUILDER,
    ROLE_LOYAL_OPPOSITION,
    ROLE_ACTING_PRIME_BUILDER,
})

# WRITE vocabulary excludes the legacy compatibility/provenance value; only
# ``prime-builder`` and ``loyal-opposition`` are valid SET targets. Per
# the Acting-Prime Compatibility Contract, ``acting-prime-builder`` is
# READ-accepted but SET-rejected.
VALID_ROLES_FOR_WRITE = frozenset({ROLE_PRIME_BUILDER, ROLE_LOYAL_OPPOSITION})

# Backward-compat: callers that previously imported ``VALID_ROLES`` get the
# READ vocabulary (the strictly-larger set). New callers should reference
# ``VALID_ROLES_FOR_READ`` or ``VALID_ROLES_FOR_WRITE`` explicitly.
VALID_ROLES = VALID_ROLES_FOR_READ

ROLE_ASSIGNMENTS_RELATIVE_PATH = Path("harness-state") / "role-assignments.json"
DEFAULT_HARNESS_IDS = _DEFAULT_HARNESS_IDS


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


# ---------------------------------------------------------------------------
# Role-set helper API (IP-8 of gtkb-single-harness-bridge-dispatcher-001).
# ---------------------------------------------------------------------------


def _normalize_role_field(raw: Any) -> frozenset[str]:
    """Normalize a role field into a ``frozenset[str]``.

    Accepts:

    - ``None`` or empty string -> ``frozenset()``.
    - Scalar role string (legacy) -> singleton frozenset.
    - List/tuple/set/frozenset of role strings -> frozenset of valid tokens.

    Only tokens in ``VALID_ROLES_FOR_READ`` survive normalization. Unknown
    tokens are silently dropped (caller-side validation policy is to treat
    an empty result as "no recognized role").
    """
    if raw is None or raw == "":
        return frozenset()
    if isinstance(raw, str):
        normalized = raw.strip().lower()
        return frozenset({normalized}) if normalized in VALID_ROLES_FOR_READ else frozenset()
    if isinstance(raw, (list, tuple, set, frozenset)):
        tokens = (str(r).strip().lower() for r in raw if r)
        return frozenset(tok for tok in tokens if tok in VALID_ROLES_FOR_READ)
    return frozenset()


def _role_set_to_json(role_set: Iterable[str]) -> list[str]:
    """Serialize a role set into a JSON-canonical sorted list.

    The wire form always uses sorted-list order so two role records that
    represent the same role set serialize identically (stable hashing,
    drift detection).
    """
    return sorted(frozenset(role_set))


def is_prime_builder(record: dict[str, Any]) -> bool:
    """True iff this record's durable role set carries Prime-Builder authority.

    Per the Acting-Prime Compatibility Contract, ``acting-prime-builder`` in
    the role set ALSO counts as Prime-equivalent for attribution purposes
    (READ-side compatibility; SET-side is separately gated).
    """
    role_set = _normalize_role_field(record.get("role"))
    return ROLE_PRIME_BUILDER in role_set or ROLE_ACTING_PRIME_BUILDER in role_set


def is_loyal_opposition(record: dict[str, Any]) -> bool:
    """True iff this record's durable role set carries Loyal-Opposition authority."""
    return ROLE_LOYAL_OPPOSITION in _normalize_role_field(record.get("role"))


def primary_role(record: dict[str, Any]) -> str:
    """Return the primary role string for a record (Prime-first ordering).

    Used by call sites that expect a scalar role string for display or
    backward-compat. When the record's role set is multi-element, Prime
    takes precedence. When the record's role set is empty, returns
    ``ROLE_LOYAL_OPPOSITION`` (the default-on-bootstrap value).

    ``acting-prime-builder`` returns ``ROLE_PRIME_BUILDER`` for primary-role
    display per the Compatibility/Provenance Classification (the harness's
    primary effective role is still Prime-equivalent for attribution).
    """
    role_set = _normalize_role_field(record.get("role"))
    if ROLE_PRIME_BUILDER in role_set or ROLE_ACTING_PRIME_BUILDER in role_set:
        return ROLE_PRIME_BUILDER
    if ROLE_LOYAL_OPPOSITION in role_set:
        return ROLE_LOYAL_OPPOSITION
    return ROLE_LOYAL_OPPOSITION


def resolved_harness_id(
    project_root: Path | None = None,
    *,
    harness_id: str | None = None,
    harness_name: str | None = None,
) -> str | None:
    return _resolved_persistent_harness_id(
        project_root,
        harness_id=harness_id,
        harness_name=harness_name,
        bootstrap_missing=True,
    )


def role_assignments_path(project_root: Path, override: Path | None = None) -> Path:
    if override is not None:
        return override.expanduser().resolve()
    env_override = os.environ.get("GTKB_ROLE_ASSIGNMENTS_PATH")
    if env_override:
        return Path(env_override).expanduser().resolve()
    return project_root.resolve() / ROLE_ASSIGNMENTS_RELATIVE_PATH


def _empty_document(project_root: Path) -> dict[str, Any]:
    _ = project_root
    return {
        "schema_version": 1,
        "source_of_truth": "GT-KB harness role assignments",
        "description": (
            "Maps durable harness installation IDs to operating roles. "
            "Harness IDs are defined by harness-state/harness-identities.json. "
            "Role field is a JSON list (the wire representation of a role set) "
            "drawn from {prime-builder, loyal-opposition}. Legacy scalar values "
            "are accepted on READ and upgraded to list form on first WRITE."
        ),
        "updated_at": _now_iso(),
        "harnesses": {},
    }


def _normalize_document(raw: Any, project_root: Path) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raw = {}
    document = _empty_document(project_root)
    document.update({key: value for key, value in raw.items() if key != "harnesses"})
    harnesses = raw.get("harnesses")
    normalized_harnesses: dict[str, dict[str, Any]] = {}
    if isinstance(harnesses, dict):
        for raw_id, raw_record in harnesses.items():
            harness_id = normalize_harness_id(str(raw_id))
            if not harness_id or not isinstance(raw_record, dict):
                continue
            role_set = _normalize_role_field(raw_record.get("role"))
            if not role_set:
                # Record has no recognized role; skip rather than infer.
                continue
            normalized_harnesses[harness_id] = dict(raw_record)
            normalized_harnesses[harness_id]["role"] = _role_set_to_json(role_set)
    if normalized_harnesses:
        document["harnesses"] = normalized_harnesses
    return document


def load_role_assignments(project_root: Path, assignment_path: Path | None = None) -> dict[str, Any]:
    path = role_assignments_path(project_root, assignment_path)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        raw = {}
    return _normalize_document(raw, project_root)


def write_role_assignments(project_root: Path, document: dict[str, Any], assignment_path: Path | None = None) -> Path:
    path = role_assignments_path(project_root, assignment_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.tmp.{os.getpid()}")
    tmp.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)
    return path


def _ensure_record(
    document: dict[str, Any],
    harness_id: str,
    *,
    harness_name: str | None = None,
) -> dict[str, Any]:
    harnesses = document.setdefault("harnesses", {})
    record = harnesses.setdefault(harness_id, {})
    normalized_name = normalize_harness_name(harness_name)
    if normalized_name:
        record.setdefault("harness_type", normalized_name)
    if "role" not in record:
        record["role"] = _role_set_to_json({ROLE_LOYAL_OPPOSITION})
    return record


def current_prime_ids(document: dict[str, Any]) -> list[str]:
    harnesses = document.get("harnesses")
    if not isinstance(harnesses, dict):
        return []
    return [
        str(harness_id)
        for harness_id, record in harnesses.items()
        if isinstance(record, dict) and is_prime_builder(record)
    ]


def role_for_harness(
    project_root: Path,
    *,
    harness_id: str | None = None,
    harness_name: str | None = None,
    assignment_path: Path | None = None,
    ensure_prime_on_startup: bool = True,
) -> tuple[str, dict[str, Any], Path]:
    """Resolve the primary role string for the given harness.

    Returns ``(primary_role_str, document, path)``. The primary role is
    Prime-first (Prime-equivalent for ``acting-prime-builder``). The
    full role set is available via ``_normalize_role_field(record["role"])``
    in the returned document.

    When ``ensure_prime_on_startup`` is True and no harness in the document
    currently holds Prime, the resolving harness self-corrects to Prime and
    other harnesses are demoted to LO.
    """
    resolved_id = resolved_harness_id(project_root, harness_id=harness_id, harness_name=harness_name)
    path = role_assignments_path(project_root, assignment_path)
    document = load_role_assignments(project_root, assignment_path)
    if resolved_id is None:
        return ROLE_PRIME_BUILDER, document, path

    record = _ensure_record(document, resolved_id, harness_name=harness_name)
    changed = False
    if ensure_prime_on_startup and not current_prime_ids(document):
        for other_id, other_record in document.get("harnesses", {}).items():
            if other_id != resolved_id and isinstance(other_record, dict):
                other_record["role"] = _role_set_to_json({ROLE_LOYAL_OPPOSITION})
        record["role"] = _role_set_to_json({ROLE_PRIME_BUILDER})
        record["assigned_reason"] = "startup-self-correction-no-prime-builder"
        changed = True

    role_set = _normalize_role_field(record.get("role"))
    if not role_set:
        # Defensive: record has no recognized role -> default to Prime.
        record["role"] = _role_set_to_json({ROLE_PRIME_BUILDER})
        role_set = frozenset({ROLE_PRIME_BUILDER})
        changed = True

    primary = primary_role(record)
    if changed or (ensure_prime_on_startup and not path.is_file()):
        document["updated_at"] = _now_iso()
        write_role_assignments(project_root, document, assignment_path)
    return primary, document, path


def _set_role_validate(role: str) -> str:
    """Validate a SET-target role string and return its canonical form.

    Per the Acting-Prime Compatibility Contract, ``acting-prime-builder`` is
    REJECTED on SET; only ``prime-builder`` and ``loyal-opposition`` are
    valid SET targets.
    """
    requested_role = str(role or "").strip().lower()
    if requested_role not in VALID_ROLES_FOR_WRITE:
        if requested_role == ROLE_ACTING_PRIME_BUILDER:
            raise ValueError(
                "acting-prime-builder is a READ-only compatibility/provenance value "
                "and is not a valid SET target. Use prime-builder or loyal-opposition."
            )
        raise ValueError(f"Unsupported next-session role: {role}")
    return requested_role


def set_harness_role(
    project_root: Path,
    role: str,
    *,
    harness_id: str | None = None,
    harness_name: str | None = None,
    assignment_path: Path | None = None,
) -> tuple[str, dict[str, Any], Path]:
    requested_role = _set_role_validate(role)
    resolved_id = resolved_harness_id(project_root, harness_id=harness_id, harness_name=harness_name)
    if resolved_id is None:
        raise ValueError("Cannot set harness role without a durable harness ID.")

    document = load_role_assignments(project_root, assignment_path)
    record = _ensure_record(document, resolved_id, harness_name=harness_name)
    # Single-role assignment via set_harness_role writes a singleton role-set
    # for the target harness. Multi-element role sets (single-harness mode)
    # are set by a different code path; see the single-harness bridge
    # dispatcher Slice 2 thread for the bootstrap flow.
    record["role"] = _role_set_to_json({requested_role})
    record["assigned_at"] = _now_iso()
    record["assigned_by"] = "harness-role-command"
    if requested_role == ROLE_PRIME_BUILDER:
        for other_id, other_record in document.get("harnesses", {}).items():
            if other_id != resolved_id and isinstance(other_record, dict):
                other_record["role"] = _role_set_to_json({ROLE_LOYAL_OPPOSITION})
    document["updated_at"] = _now_iso()
    path = write_role_assignments(project_root, document, assignment_path)
    return requested_role, document, path
