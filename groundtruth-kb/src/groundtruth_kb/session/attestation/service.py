"""Session init-binding service.

Implements the single immutable binding `DCL-INIT-BOUND-SESSION-IDENTITY-001`
v2 defines and the single resolver `DCL-SESSION-ROLE-RESOLUTION-001` v9
requires: **role resolves only from the immutable session binding**.

- **Session-init binding** - immutable, exact-init-only record associating one
  native session context with one opaque GT-KB session-context ID, the exact
  accepted subject and role, and the minimum idempotency identity of the
  accepted init command. One binding per native context, ever (a second init
  is a typed ``session_already_initialized`` rejection).
- **Resolver** - ``binding_for_context(native_context_id)`` returns the binding
  or a typed failure. No fallback authority participates: no session
  documents, no per-harness projection, no registry role, no vendor identity,
  no marker files.

Role is a column on the immutable binding row, so it cannot change for the
lifetime of a session context. There is deliberately no separate attestation
log, no role-change operation, no sequence chain and no
"role in force at a point in time" resolution: with an immutable role those
concepts are vacuous. ``ADR-SESSION-ROLE-ATTESTATION-SERVICE-001`` is retired
and its retirement forbids retaining that separate attestation log,
role-change, registry fallback, or migration design.

Storage is the canonical MemBase (``groundtruth.db``), append-only with no
UPDATE/DELETE paths, per the platform's change-control doctrine.
"""

from __future__ import annotations

import hashlib
import re
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

VALID_ROLES = frozenset({"prime-builder", "loyal-opposition"})

# The valid exact-init forms carrying a mandatory role token
# (SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001: subject mandatory, role optional -
# only role-bearing forms create a binding).
_EXACT_INIT_RE = re.compile(r"^::init (gtkb|application) (pb|lo)$")
_ROLE_BY_TOKEN = {"pb": "prime-builder", "lo": "loyal-opposition"}

# Mirrors the live canonical table exactly. Column ORDER is load-bearing for
# nothing here because every statement names its columns, but the shape must
# match or CREATE TABLE IF NOT EXISTS silently diverges on a fresh install.
_SCHEMA = """
CREATE TABLE IF NOT EXISTS session_init_bindings (
    native_context_id TEXT NOT NULL,
    session_context_id TEXT NOT NULL,
    subject TEXT NOT NULL,
    role TEXT NOT NULL,
    created_at TEXT NOT NULL,
    minimum_idempotency_identity TEXT NOT NULL,
    UNIQUE(native_context_id),
    UNIQUE(session_context_id)
);
"""

_BINDING_COLUMNS = (
    "native_context_id",
    "session_context_id",
    "subject",
    "role",
    "created_at",
    "minimum_idempotency_identity",
)


class RoleAttestationError(RuntimeError):
    """Typed failure; ``code`` is machine-readable."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class Binding:
    """One immutable session-init binding. Role is intrinsic and unchangeable."""

    native_context_id: str
    session_context_id: str
    subject: str
    role: str
    created_at: str
    minimum_idempotency_identity: str

    @property
    def evidence_reference(self) -> str:
        """The persistable evidence reference consumers record."""
        return f"session-binding:{self.session_context_id}:{self.minimum_idempotency_identity[:16]}"


def _utc_now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _digest(*parts: str) -> str:
    h = hashlib.sha256()
    for part in parts:
        h.update(part.encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.executescript(_SCHEMA)
    return conn


def bind_exact_init(
    db_path: Path,
    *,
    native_context_id: str,
    init_command: str,
) -> Binding:
    """The atomic exact-init transaction (DCL-INIT-BOUND-SESSION-IDENTITY-001).

    Accepts only the complete canonical role-bearing init message. Creates the
    one immutable binding, or nothing.
    """
    if not native_context_id or not native_context_id.strip():
        raise RoleAttestationError("invalid_native_context_id", "native session context is required")
    match = _EXACT_INIT_RE.match(init_command or "")
    if match is None:
        raise RoleAttestationError(
            "invalid_init_command",
            "only the complete canonical '::init <subject> <role>' message creates a binding; "
            "malformed, subject-only, synonym, whitespace-variant and multi-line forms create nothing",
        )
    subject, role_token = match.group(1), match.group(2)
    role = _ROLE_BY_TOKEN[role_token]
    now = _utc_now()
    session_context_id = f"SENV-{uuid.uuid4().hex}"
    minimum_idempotency_identity = _digest(init_command)

    conn = _connect(db_path)
    try:
        with conn:  # one atomic transaction
            existing = conn.execute(
                "SELECT session_context_id FROM session_init_bindings WHERE native_context_id = ?",
                (native_context_id,),
            ).fetchone()
            if existing is not None:
                raise RoleAttestationError(
                    "session_already_initialized",
                    f"native context already bound to {existing[0]}; another init creates no ID "
                    "and changes no role, subject, binding, or context-load state",
                )
            conn.execute(
                "INSERT INTO session_init_bindings "
                "(native_context_id, session_context_id, subject, role, created_at, "
                "minimum_idempotency_identity) VALUES (?, ?, ?, ?, ?, ?)",
                (native_context_id, session_context_id, subject, role, now, minimum_idempotency_identity),
            )
    finally:
        conn.close()
    return Binding(native_context_id, session_context_id, subject, role, now, minimum_idempotency_identity)


def binding_for_context(db_path: Path, native_context_id: str) -> Binding:
    """Resolve the immutable binding, and therefore the role, for a native context."""
    conn = _connect(db_path)
    try:
        row = conn.execute(
            f"SELECT {', '.join(_BINDING_COLUMNS)} "  # noqa: S608 - fixed identifier tuple, no user input
            "FROM session_init_bindings WHERE native_context_id = ?",
            (native_context_id,),
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        raise RoleAttestationError(
            "no_session_binding",
            f"no session-init binding exists for native context {native_context_id!r}; "
            "run the canonical '::init <subject> <role>' first",
        )
    binding = Binding(*row)
    if binding.role not in VALID_ROLES:
        raise RoleAttestationError(
            "invalid_role",
            f"binding for {native_context_id!r} carries unsupported role {binding.role!r}",
        )
    return binding
