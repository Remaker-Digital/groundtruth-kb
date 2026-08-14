"""Session role-attestation service.

Slice 1 of bridge/gtkb-session-role-attestation-service-slice-1 (GO at -002).

Implements the two attestation stores `DCL-INIT-BOUND-SESSION-IDENTITY-001`
defines and the single canonical resolver `DCL-SESSION-ROLE-RESOLUTION-001` v8
requires:

- **Session-init binding attestation** — immutable, exact-init-only record
  associating one invoking session context with one opaque session-envelope ID
  and the exact accepted init command digest. One binding per invoking context,
  ever (a second init is a typed ``session_already_initialized`` rejection).
- **Role attestation** — append-only owner/dispatcher role statements carrying
  the session-envelope ID, normalized role, source event, issuer, timestamp
  and evidence digest. Deliberately carries NO session lifecycle, activity,
  claim, implementation, wrap or handoff state.
- **Resolver** — ``resolve_effective_role(envelope_id, at_time)`` returns the
  attestation in force at the operation time, or a typed failure. No fallback
  authority participates: no session documents, no per-harness projection, no
  registry role, no vendor identity, no marker files.

Storage is the canonical MemBase (`groundtruth.db`), append-only tables with
no UPDATE/DELETE paths, per the platform's change-control doctrine. The
binding and the initial role attestation are inserted in ONE SQLite
transaction (DCL-INIT-BOUND-SESSION-IDENTITY-001 exact-init transaction
clause 4): a partial transaction rolls back entirely and is recoverable
without creating a second ID.
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
# only role-bearing forms create an initial role attestation).
_EXACT_INIT_RE = re.compile(r"^::init (gtkb|application) (pb|lo)$")
_ROLE_BY_TOKEN = {"pb": "prime-builder", "lo": "loyal-opposition"}

_SCHEMA = """
CREATE TABLE IF NOT EXISTS session_init_bindings (
    invoking_context TEXT NOT NULL,
    envelope_id TEXT NOT NULL,
    command_digest TEXT NOT NULL,
    subject TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(invoking_context),
    UNIQUE(envelope_id)
);
CREATE TABLE IF NOT EXISTS session_role_attestations (
    envelope_id TEXT NOT NULL,
    seq INTEGER NOT NULL,
    role TEXT NOT NULL,
    source_event TEXT NOT NULL,
    issuer TEXT NOT NULL,
    created_at TEXT NOT NULL,
    evidence_digest TEXT NOT NULL,
    UNIQUE(envelope_id, seq)
);
"""


class RoleAttestationError(RuntimeError):
    """Typed failure; ``code`` is machine-readable."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class Binding:
    invoking_context: str
    envelope_id: str
    command_digest: str
    subject: str
    created_at: str


@dataclass(frozen=True)
class Attestation:
    envelope_id: str
    seq: int
    role: str
    source_event: str
    issuer: str
    created_at: str
    evidence_digest: str

    @property
    def evidence_reference(self) -> str:
        """The persistable evidence reference consumers record."""
        return f"role-attestation:{self.envelope_id}:{self.seq}:{self.evidence_digest[:16]}"


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
    invoking_context: str,
    init_command: str,
    issuer: str,
) -> tuple[Binding, Attestation]:
    """The atomic exact-init transaction (DCL clauses 1-6).

    Accepts only the complete canonical role-bearing init message. Creates the
    binding and the initial role attestation in one transaction, or nothing.
    """
    if not invoking_context or not invoking_context.strip():
        raise RoleAttestationError("invalid_invoking_context", "invoking session context is required")
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
    envelope_id = f"SENV-{uuid.uuid4().hex}"
    command_digest = _digest(init_command)
    evidence_digest = _digest(envelope_id, role, "exact_init", issuer, now, command_digest)

    conn = _connect(db_path)
    try:
        with conn:  # one atomic transaction: binding + initial attestation
            existing = conn.execute(
                "SELECT envelope_id FROM session_init_bindings WHERE invoking_context = ?",
                (invoking_context,),
            ).fetchone()
            if existing is not None:
                raise RoleAttestationError(
                    "session_already_initialized",
                    f"invoking context already bound to {existing[0]}; another init creates no ID "
                    "and changes no role, subject, binding, or context-load state",
                )
            conn.execute(
                "INSERT INTO session_init_bindings VALUES (?, ?, ?, ?, ?)",
                (invoking_context, envelope_id, command_digest, subject, now),
            )
            conn.execute(
                "INSERT INTO session_role_attestations VALUES (?, 1, ?, 'exact_init', ?, ?, ?)",
                (envelope_id, role, issuer, now, evidence_digest),
            )
    finally:
        conn.close()
    binding = Binding(invoking_context, envelope_id, command_digest, subject, now)
    attestation = Attestation(envelope_id, 1, role, "exact_init", issuer, now, evidence_digest)
    return binding, attestation


def binding_for_context(db_path: Path, invoking_context: str) -> Binding:
    """Resolve the immutable binding for an invoking session context."""
    conn = _connect(db_path)
    try:
        row = conn.execute(
            "SELECT invoking_context, envelope_id, command_digest, subject, created_at "
            "FROM session_init_bindings WHERE invoking_context = ?",
            (invoking_context,),
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        raise RoleAttestationError(
            "no_session_binding",
            f"no session-init binding exists for invoking context {invoking_context!r}; "
            "run the canonical '::init <subject> <role>' first",
        )
    return Binding(*row)


def attest_role_change(
    db_path: Path,
    *,
    envelope_id: str,
    role: str,
    issuer: str,
    owner_decision_ref: str,
) -> Attestation:
    """Append an owner-directed role change (never re-runs init, never mutates).

    The evidence digest chains the prior attestation, so verifiers can always
    see that the same envelope held the earlier role - an owner role change
    cannot make one session context an independent reviewer of its own
    earlier work.
    """
    if role not in VALID_ROLES:
        raise RoleAttestationError("invalid_role", f"role must be one of {sorted(VALID_ROLES)}")
    if not owner_decision_ref or not owner_decision_ref.strip():
        raise RoleAttestationError(
            "owner_decision_required",
            "an owner-directed role change requires a durable owner-decision reference",
        )
    now = _utc_now()
    conn = _connect(db_path)
    try:
        with conn:
            bound = conn.execute(
                "SELECT envelope_id FROM session_init_bindings WHERE envelope_id = ?",
                (envelope_id,),
            ).fetchone()
            if bound is None:
                raise RoleAttestationError("unknown_envelope_id", f"no binding exists for envelope id {envelope_id!r}")
            prior = conn.execute(
                "SELECT seq, evidence_digest FROM session_role_attestations "
                "WHERE envelope_id = ? ORDER BY seq DESC LIMIT 1",
                (envelope_id,),
            ).fetchone()
            seq = (prior[0] + 1) if prior else 1
            chain = prior[1] if prior else ""
            evidence_digest = _digest(envelope_id, role, "owner_role_change", issuer, now, owner_decision_ref, chain)
            conn.execute(
                "INSERT INTO session_role_attestations VALUES (?, ?, ?, 'owner_role_change', ?, ?, ?)",
                (envelope_id, seq, role, issuer, now, evidence_digest),
            )
    finally:
        conn.close()
    return Attestation(envelope_id, seq, role, "owner_role_change", issuer, now, evidence_digest)


def resolve_effective_role(
    db_path: Path,
    *,
    envelope_id: str,
    at_time: str | None = None,
) -> Attestation:
    """The one canonical resolver (DCL-SESSION-ROLE-RESOLUTION-001 v8).

    Returns the attestation in force at ``at_time`` (default: now). No
    fallback authority of any kind participates; absence is a typed failure,
    never a default role.
    """
    operation_time = at_time or _utc_now()
    conn = _connect(db_path)
    try:
        row = conn.execute(
            "SELECT envelope_id, seq, role, source_event, issuer, created_at, evidence_digest "
            "FROM session_role_attestations WHERE envelope_id = ? AND created_at <= ? "
            "ORDER BY seq DESC LIMIT 1",
            (envelope_id, operation_time),
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        raise RoleAttestationError(
            "no_role_attestation",
            f"no role attestation is in force for {envelope_id!r} at {operation_time}; "
            "no fallback authority participates in role resolution",
        )
    return Attestation(*row)


def resolve_effective_role_for_context(
    db_path: Path,
    *,
    invoking_context: str,
    at_time: str | None = None,
) -> tuple[Binding, Attestation]:
    """Convenience composition: invoking context -> binding -> effective role."""
    binding = binding_for_context(db_path, invoking_context)
    return binding, resolve_effective_role(db_path, envelope_id=binding.envelope_id, at_time=at_time)
