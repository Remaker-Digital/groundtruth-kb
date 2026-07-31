"""Role-map partition checks for the operating-mode subsystem.

``REQ-HARNESS-REGISTRY-001`` FR9-F12 require active bridge dispatch to retain
Prime Builder and Loyal Opposition lane coverage. Durable active-harness role
membership supplies that coverage by default. A current owner-declared
interactive Prime Builder session may supply Prime Builder coverage for an
LO-only headless surge, but only when its per-session role marker is readable
and proves the session is Prime Builder. Loyal Opposition coverage still comes
from at least one active durable harness role. When more than one harness is
active, no active harness may carry both roles. Non-active harnesses may retain
operating roles for interactive or owner-directed work; they do not participate
in active dispatch partitioning.

It reads the harness registry projection
(``harness-state/harness-registry.json``) and computes over the role-set wire
form — a list of role tokens, or a legacy scalar string per
``ADR-SINGLE-HARNESS-OPERATING-MODE-001``.

Authority: ``REQ-HARNESS-REGISTRY-001`` FR9-F12;
``DELIB-20263438`` (role/dispatchability orthogonality);
``GOV-HARNESS-ROLE-PORTABILITY-001`` (Prime Builder and Loyal Opposition are
portable harness-assigned roles).

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights
reserved.
"""

from __future__ import annotations

import json
import os
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Role tokens that count as holding the prime-builder role. The legacy
# ``acting-prime-builder`` provenance token is READ-accepted per
# ``GOV-ACTING-PRIME-BUILDER-001``; it counts toward the active-prime-builder
# invariant so stale provenance cannot mask a missing prime-class harness.
_PRIME_BUILDER_TOKENS = frozenset({"prime-builder", "acting-prime-builder"})
_ROLE_PRIME_BUILDER = "prime-builder"
_ROLE_LOYAL_OPPOSITION = "loyal-opposition"
_INTERACTIVE_PRIME_BUILDER_PREFIX = "interactive-prime-builder"
_SESSION_MARKER_DIR = (".claude", "session")
_PER_SESSION_ROLE_MARKER_PREFIX = "role-"
_PER_SESSION_ROLE_MARKER_SUFFIX = ".json"
_MARKER_CONTINUITY_ORDER = (
    "GTKB_SESSION_ID",
    "CODEX_SESSION_ID",
    "CODEX_THREAD_ID",
    "CLAUDE_SESSION_ID",
    "CLAUDE_CODE_SESSION_ID",
)
_UNSAFE_SESSION_ID_CHARS = re.compile(r"[^A-Za-z0-9._-]+")
_MAX_SANITIZED_SESSION_ID_LEN = 128


class RolePartitionViolation(RuntimeError):
    """Raised when the active role map is not a valid registrar partition."""


@dataclass(frozen=True)
class RolePartitionSummary:
    prime_builder_id: str
    loyal_opposition_id: str
    active_harness_ids: tuple[str, ...]
    prime_builder_ids: tuple[str, ...] = ()
    loyal_opposition_ids: tuple[str, ...] = ()
    prime_builder_coverage_source: str = "durable"
    interactive_prime_builder_session_id: str | None = None


def _role_tokens(role_field: Any) -> set[str]:
    """Normalize a harness record's ``role`` field to a set of role tokens.

    Accepts the list wire form (``["prime-builder"]``) and the legacy scalar
    wire form (``"prime-builder"``); any other value yields an empty set.
    """
    if isinstance(role_field, list):
        return {str(token).strip() for token in role_field if str(token).strip()}
    if isinstance(role_field, str) and role_field.strip():
        return {role_field.strip()}
    return set()


def prime_builder_ids(role_document: dict[str, Any]) -> list[str]:
    """Return the sorted harness ids holding a prime-builder-class role.

    A harness counts when its role set contains ``prime-builder`` or the
    READ-compatible ``acting-prime-builder`` provenance token.
    """
    harnesses = role_document.get("harnesses", {})
    if not isinstance(harnesses, dict):
        return []
    return sorted(
        harness_id
        for harness_id, record in harnesses.items()
        if isinstance(record, dict)
        and record.get("status") == "active"
        and _PRIME_BUILDER_TOKENS & _role_tokens(record.get("role"))
    )


def loyal_opposition_ids(role_document: dict[str, Any]) -> list[str]:
    """Return the sorted active harness ids holding loyal-opposition."""
    harnesses = role_document.get("harnesses", {})
    if not isinstance(harnesses, dict):
        return []
    return sorted(
        harness_id
        for harness_id, record in harnesses.items()
        if isinstance(record, dict)
        and record.get("status") == "active"
        and _ROLE_LOYAL_OPPOSITION in _role_tokens(record.get("role"))
    )


def _harnesses_by_id(raw_harnesses: Any, *, source: str) -> dict[str, Any]:
    if isinstance(raw_harnesses, dict):
        return raw_harnesses
    if isinstance(raw_harnesses, list):
        return {str(rec["id"]): rec for rec in raw_harnesses if isinstance(rec, dict) and rec.get("id")}
    raise RolePartitionViolation(f"{source} has no 'harnesses' map or list")


def _sanitize_session_id(session_id: str) -> str:
    cleaned = _UNSAFE_SESSION_ID_CHARS.sub("-", str(session_id)).strip("-.")
    if not cleaned:
        cleaned = "unknown"
    return cleaned[:_MAX_SANITIZED_SESSION_ID_LEN]


def _per_session_role_marker_path(project_root: Path, session_id: str) -> Path:
    return (
        project_root.joinpath(*_SESSION_MARKER_DIR)
        / f"{_PER_SESSION_ROLE_MARKER_PREFIX}{_sanitize_session_id(session_id)}{_PER_SESSION_ROLE_MARKER_SUFFIX}"
    )


def _session_id_from_env(environ: Mapping[str, str] | None = None) -> str | None:
    env = os.environ if environ is None else environ
    for name in _MARKER_CONTINUITY_ORDER:
        value = str(env.get(name) or "").strip()
        if value:
            return value
    return None


def interactive_prime_builder_session_id(
    project_root: Path | None,
    *,
    session_id: str | None = None,
    environ: Mapping[str, str] | None = None,
) -> str | None:
    """Return the current interactive PB session id, if positively marked.

    This mirrors the per-session marker contract used by work-intent claim
    eligibility: the session id must resolve from the interactive marker env
    order (or an explicit test/session argument), the corresponding
    ``.claude/session/role-<session>.json`` file must be readable, and the
    marker must contain the same ``session_id`` with role ``prime-builder``.
    Missing, stale, malformed, or non-Prime markers yield ``None``.
    """

    if project_root is None:
        return None
    resolved_session_id = str(session_id or _session_id_from_env(environ) or "").strip()
    if not resolved_session_id:
        return None
    marker_path = _per_session_role_marker_path(project_root, resolved_session_id)
    try:
        marker = json.loads(marker_path.read_text(encoding="utf-8", errors="replace"))
    except (FileNotFoundError, OSError, ValueError):
        return None
    if not isinstance(marker, dict):
        return None
    if marker.get("session_id") != resolved_session_id:
        return None
    if marker.get("role") != _ROLE_PRIME_BUILDER:
        return None
    return resolved_session_id


def _interactive_prime_builder_id(session_id: str) -> str:
    return f"{_INTERACTIVE_PRIME_BUILDER_PREFIX}:{session_id}"


def verify_role_document_partition(
    role_document: dict[str, Any],
    *,
    project_root: Path | None = None,
    interactive_prime_builder_session: str | None = None,
    environ: Mapping[str, str] | None = None,
) -> RolePartitionSummary:
    """Verify an in-memory role document's active PB/LO lane coverage.

    This is the candidate-state validator used by write paths before durable
    audit or registry mutation. It accepts the canonical dict-keyed document
    shape and the registry projection's list shape for callers that already
    loaded ``harness-state/harness-registry.json``.

    Durable active Prime Builder membership supplies Prime coverage by default.
    When no durable active Prime Builder remains, a readable per-session marker
    for a current interactive Prime Builder session may supply Prime coverage.
    """
    if not isinstance(role_document, dict):
        raise RolePartitionViolation("role document must be a JSON object")
    harnesses = _harnesses_by_id(role_document.get("harnesses"), source="role document")
    normalized_document = {"harnesses": harnesses}
    active_ids = tuple(
        sorted(
            harness_id
            for harness_id, record in harnesses.items()
            if isinstance(record, dict) and record.get("status") == "active"
        )
    )
    if not active_ids:
        raise RolePartitionViolation("role map must include at least one active harness")

    active_roleless: list[str] = []
    for harness_id in active_ids:
        record = harnesses[harness_id]
        tokens = _role_tokens(record.get("role"))
        if not tokens:
            active_roleless.append(harness_id)
    if active_roleless:
        raise RolePartitionViolation(
            "active harnesses must carry operating roles; violations: " + ", ".join(sorted(active_roleless))
        )

    primes = prime_builder_ids(normalized_document)
    interactive_prime_session = None
    if len(primes) < 1:
        interactive_prime_session = interactive_prime_builder_session_id(
            project_root,
            session_id=interactive_prime_builder_session,
            environ=environ,
        )
    if len(primes) < 1 and interactive_prime_session is None:
        raise RolePartitionViolation(
            "active lane coverage must include at least one prime-builder assignment or an "
            f"owner-declared interactive Prime Builder anchor; found {len(primes)} durable prime-builders: "
            f"{primes if primes else '[]'}"
        )
    prime_id = primes[0] if primes else _interactive_prime_builder_id(str(interactive_prime_session))
    prime_source = "durable" if primes else "interactive-session-marker"

    los = loyal_opposition_ids(normalized_document)
    if len(los) < 1:
        raise RolePartitionViolation(
            f"active role map must hold at least one loyal-opposition; found {len(los)}: {los if los else '[]'}"
        )
    lo_id = los[0]
    if len(active_ids) > 1:
        overlapping = set(primes) & set(los)
        if overlapping:
            raise RolePartitionViolation(
                "harnesses cannot carry both prime-builder and loyal-opposition "
                f"when more than one active harness exists; overlapping: {sorted(overlapping)}"
            )
    return RolePartitionSummary(
        prime_builder_id=prime_id,
        loyal_opposition_id=lo_id,
        active_harness_ids=active_ids,
        prime_builder_ids=tuple(primes),
        loyal_opposition_ids=tuple(los),
        prime_builder_coverage_source=prime_source,
        interactive_prime_builder_session_id=interactive_prime_session,
    )


def verify_active_role_partition(
    project_root: Path,
    *,
    role_path: Path | None = None,
    interactive_prime_builder_session: str | None = None,
    environ: Mapping[str, str] | None = None,
) -> RolePartitionSummary:
    """Verify the role map satisfies active PB/LO lane coverage.

    Loads the harness registry projection under ``project_root`` (or the
    explicit ``role_path`` override) and raises ``RolePartitionViolation``
    unless Prime Builder coverage exists through either an active durable
    harness role or a current owner-declared interactive Prime Builder session
    marker, and at least one active harness holds loyal-opposition. With multiple active
    harnesses, no harness may hold both roles. Registered, inactive,
    suspended, and retired harnesses may retain roles but are ignored by the
    active lane-coverage check.

    WI-3342 IP-5: migrated from the retired role mirror to the DB-backed registry
    projection ``harness-state/harness-registry.json``. The projection stores
    ``harnesses`` as a LIST of unified records; it is converted here to the
    ``{harness_id: record}`` document shape that ``prime_builder_ids`` and the
    partition check consume.
    """
    from groundtruth_kb.harness_projection import harness_registry_path

    path = role_path if role_path is not None else harness_registry_path(project_root)
    projection = json.loads(Path(path).read_text(encoding="utf-8"))
    projection_harnesses = projection.get("harnesses", []) if isinstance(projection, dict) else None
    if not isinstance(projection_harnesses, list):
        raise RolePartitionViolation(f"harness registry projection at {path} has no 'harnesses' list")
    return verify_role_document_partition(
        {"harnesses": projection_harnesses},
        project_root=project_root,
        interactive_prime_builder_session=interactive_prime_builder_session,
        environ=environ,
    )


def verify_role_partition(
    project_root: Path,
    *,
    role_path: Path | None = None,
    interactive_prime_builder_session: str | None = None,
    environ: Mapping[str, str] | None = None,
) -> str:
    """Backward-compatible wrapper returning the verified Prime Builder id."""
    return verify_active_role_partition(
        project_root,
        role_path=role_path,
        interactive_prime_builder_session=interactive_prime_builder_session,
        environ=environ,
    ).prime_builder_id
