"""Spec-derived tests for the session init-binding service.

Derived from `DCL-INIT-BOUND-SESSION-IDENTITY-001` v2 (exact-init transaction,
binding record boundary) and `DCL-SESSION-ROLE-RESOLUTION-001` v9 ("Role
resolves only from the immutable session binding").

`ADR-SESSION-ROLE-ATTESTATION-SERVICE-001` is retired. Its retirement forbids
any test retaining its separate attestation log, role-change, registry
fallback, or migration design, so the three former owner-role-change tests
are deleted rather than ported: with role carried on the immutable binding
row there is no role-change operation to exercise.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from groundtruth_kb.session.attestation import (  # noqa: E402
    RoleAttestationError,
    bind_exact_init,
    binding_for_context,
)

LIVE_BINDING_COLUMNS = [
    "native_context_id",
    "session_context_id",
    "subject",
    "role",
    "created_at",
    "minimum_idempotency_identity",
]


@pytest.fixture()
def db(tmp_path: Path) -> Path:
    return tmp_path / "session-binding-fixture.db"


def _rows(db_path: Path, table: str) -> list[tuple]:
    conn = sqlite3.connect(str(db_path))
    try:
        return conn.execute(f"SELECT * FROM {table}").fetchall()  # noqa: S608 - fixed test table name
    except sqlite3.OperationalError:
        return []
    finally:
        conn.close()


# --- exact-init transaction ---------------------------------------------------


@pytest.mark.parametrize(
    "command,subject,role",
    [
        ("::init gtkb pb", "gtkb", "prime-builder"),
        ("::init gtkb lo", "gtkb", "loyal-opposition"),
        ("::init application pb", "application", "prime-builder"),
        ("::init application lo", "application", "loyal-opposition"),
    ],
)
def test_valid_exact_init_creates_binding_carrying_role(db, command, subject, role):
    binding = bind_exact_init(db, native_context_id="ctx-1", init_command=command)
    assert binding.session_context_id.startswith("SENV-")
    assert binding.native_context_id == "ctx-1"
    assert binding.subject == subject
    assert binding.role == role
    assert binding.minimum_idempotency_identity
    assert len(_rows(db, "session_init_bindings")) == 1


@pytest.mark.parametrize(
    "bad",
    [
        "",
        "::init gtkb",
        "::init  gtkb  pb",
        "::init gtkb pb ",
        "::INIT gtkb pb",
        "::init unknown pb",
        "::init gtkb owner",
        "::init gtkb pb\n::init gtkb lo",
    ],
)
def test_invalid_init_creates_nothing(db, bad):
    with pytest.raises(RoleAttestationError) as exc:
        bind_exact_init(db, native_context_id="ctx-2", init_command=bad)
    assert exc.value.code == "invalid_init_command"
    assert _rows(db, "session_init_bindings") == []


def test_second_init_is_typed_rejection_and_creates_no_second_id(db):
    first = bind_exact_init(db, native_context_id="ctx-3", init_command="::init gtkb pb")
    with pytest.raises(RoleAttestationError) as exc:
        bind_exact_init(db, native_context_id="ctx-3", init_command="::init gtkb lo")
    assert exc.value.code == "session_already_initialized"
    rows = _rows(db, "session_init_bindings")
    assert len(rows) == 1
    # The immutable binding is unchanged: neither a second ID nor a new role.
    assert binding_for_context(db, "ctx-3") == first
    assert binding_for_context(db, "ctx-3").role == "prime-builder"


def test_missing_native_context_is_typed_rejection(db):
    with pytest.raises(RoleAttestationError) as exc:
        bind_exact_init(db, native_context_id="  ", init_command="::init gtkb pb")
    assert exc.value.code == "invalid_native_context_id"


# --- resolution (DCL-SESSION-ROLE-RESOLUTION-001 v9) ---------------------------


def test_resolver_requires_binding(db):
    with pytest.raises(RoleAttestationError) as exc:
        binding_for_context(db, "never-bound")
    assert exc.value.code == "no_session_binding"


def test_resolver_returns_role_from_the_binding(db):
    bind_exact_init(db, native_context_id="ctx-9", init_command="::init gtkb lo")
    binding = binding_for_context(db, "ctx-9")
    assert binding.native_context_id == "ctx-9"
    assert binding.role == "loyal-opposition"
    assert binding.evidence_reference.startswith(f"session-binding:{binding.session_context_id}:")


def test_unsupported_bound_role_is_typed_failure(db):
    bind_exact_init(db, native_context_id="ctx-10", init_command="::init gtkb pb")
    conn = sqlite3.connect(str(db))
    try:
        conn.execute("UPDATE session_init_bindings SET role = 'owner' WHERE native_context_id = 'ctx-10'")
        conn.commit()
    finally:
        conn.close()
    with pytest.raises(RoleAttestationError) as exc:
        binding_for_context(db, "ctx-10")
    assert exc.value.code == "invalid_role"


# --- schema conformance -------------------------------------------------------


def test_created_schema_matches_the_canonical_binding_shape(db):
    bind_exact_init(db, native_context_id="ctx-11", init_command="::init gtkb pb")
    conn = sqlite3.connect(str(db))
    try:
        columns = [row[1] for row in conn.execute("PRAGMA table_info(session_init_bindings)")]
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    finally:
        conn.close()
    assert columns == LIVE_BINDING_COLUMNS
    # The retired separate attestation log must not be recreated.
    assert "session_role_attestations" not in tables
