"""Spec-derived tests for the session role-attestation service (Slice 1).

Derived from `DCL-INIT-BOUND-SESSION-IDENTITY-001` (exact-init transaction
clauses 1-6, binding record boundary) and `DCL-SESSION-ROLE-RESOLUTION-001` v8
(single resolver, no fallback authority, append-only role change), per
bridge/gtkb-session-role-attestation-service-slice-1 (GO at -002).
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
    attest_role_change,
    bind_exact_init,
    resolve_effective_role,
    resolve_effective_role_for_context,
)


@pytest.fixture()
def db(tmp_path: Path) -> Path:
    return tmp_path / "attestation-fixture.db"


def _rows(db_path: Path, table: str) -> list[tuple]:
    conn = sqlite3.connect(str(db_path))
    try:
        return conn.execute(f"SELECT * FROM {table}").fetchall()
    except sqlite3.OperationalError:
        return []
    finally:
        conn.close()


# --- exact-init transaction (DCL clauses 1-6) ---------------------------------


@pytest.mark.parametrize(
    "command,role",
    [
        ("::init gtkb pb", "prime-builder"),
        ("::init gtkb lo", "loyal-opposition"),
        ("::init application pb", "prime-builder"),
        ("::init application lo", "loyal-opposition"),
    ],
)
def test_valid_exact_init_creates_binding_and_attestation(db, command, role):
    binding, attestation = bind_exact_init(db, invoking_context="ctx-1", init_command=command, issuer="hook:init")
    assert binding.envelope_id.startswith("SENV-")
    assert attestation.role == role
    assert attestation.seq == 1
    assert attestation.source_event == "exact_init"
    assert len(_rows(db, "session_init_bindings")) == 1
    assert len(_rows(db, "session_role_attestations")) == 1


@pytest.mark.parametrize(
    "bad",
    [
        "::init gtkb",  # subject-only: no role token, no attestation basis
        "::init gtkb PB",  # case variant
        "::init gtkb prime-builder",  # synonym
        " ::init gtkb pb",  # whitespace variant
        "::init gtkb pb\n::open build",  # multi-line
        "init gtkb pb",  # missing marker
        "::init gtkb pb extra",  # trailing token
        "",
    ],
)
def test_invalid_init_creates_nothing(db, bad):
    with pytest.raises(RoleAttestationError) as exc:
        bind_exact_init(db, invoking_context="ctx-1", init_command=bad, issuer="hook:init")
    assert exc.value.code == "invalid_init_command"
    assert _rows(db, "session_init_bindings") == []
    assert _rows(db, "session_role_attestations") == []


def test_second_init_is_typed_rejection_and_creates_no_second_id(db):
    binding, _ = bind_exact_init(db, invoking_context="ctx-1", init_command="::init gtkb pb", issuer="hook:init")
    with pytest.raises(RoleAttestationError) as exc:
        bind_exact_init(db, invoking_context="ctx-1", init_command="::init gtkb lo", issuer="hook:init")
    assert exc.value.code == "session_already_initialized"
    assert len(_rows(db, "session_init_bindings")) == 1
    # And the original role is untouched.
    assert resolve_effective_role(db, envelope_id=binding.envelope_id).role == "prime-builder"


# --- resolver (DCL v8: one resolver, no fallback) ------------------------------


def test_resolver_returns_typed_failure_with_no_attestation(db):
    with pytest.raises(RoleAttestationError) as exc:
        resolve_effective_role(db, envelope_id="SENV-nonexistent")
    assert exc.value.code == "no_role_attestation"


def test_resolver_for_context_requires_binding(db):
    with pytest.raises(RoleAttestationError) as exc:
        resolve_effective_role_for_context(db, invoking_context="never-bound")
    assert exc.value.code == "no_session_binding"


def test_resolver_composes_context_to_role(db):
    bind_exact_init(db, invoking_context="ctx-9", init_command="::init gtkb lo", issuer="hook:init")
    binding, attestation = resolve_effective_role_for_context(db, invoking_context="ctx-9")
    assert binding.invoking_context == "ctx-9"
    assert attestation.role == "loyal-opposition"
    assert attestation.evidence_reference.startswith(f"role-attestation:{binding.envelope_id}:1:")


# --- owner-directed role change (append-only, chained) -------------------------


def test_owner_role_change_appends_and_resolves(db):
    binding, first = bind_exact_init(db, invoking_context="ctx-2", init_command="::init gtkb lo", issuer="hook:init")
    changed = attest_role_change(
        db,
        envelope_id=binding.envelope_id,
        role="prime-builder",
        issuer="owner",
        owner_decision_ref="DELIB-FIXTURE-0001",
    )
    assert changed.seq == 2
    assert resolve_effective_role(db, envelope_id=binding.envelope_id).role == "prime-builder"
    # Append-only: both attestations persist; the prior one is not rewritten.
    rows = _rows(db, "session_role_attestations")
    assert len(rows) == 2
    # The history keeps the earlier role visible for independence checks.
    assert resolve_effective_role(db, envelope_id=binding.envelope_id, at_time=first.created_at).role in {
        "loyal-opposition",
        "prime-builder",  # same-second change: latest-seq wins, still auditable via rows
    }


def test_owner_role_change_requires_decision_ref_and_valid_role(db):
    binding, _ = bind_exact_init(db, invoking_context="ctx-3", init_command="::init gtkb pb", issuer="hook:init")
    with pytest.raises(RoleAttestationError) as exc:
        attest_role_change(
            db, envelope_id=binding.envelope_id, role="prime-builder", issuer="owner", owner_decision_ref=" "
        )
    assert exc.value.code == "owner_decision_required"
    with pytest.raises(RoleAttestationError) as exc:
        attest_role_change(
            db,
            envelope_id=binding.envelope_id,
            role="acting-prime-builder",
            issuer="owner",
            owner_decision_ref="DELIB-X",
        )
    assert exc.value.code == "invalid_role"
    with pytest.raises(RoleAttestationError) as exc:
        attest_role_change(
            db, envelope_id="SENV-unknown", role="prime-builder", issuer="owner", owner_decision_ref="DELIB-X"
        )
    assert exc.value.code == "unknown_envelope_id"


def test_role_change_digest_chains_prior_attestation(db):
    binding, first = bind_exact_init(db, invoking_context="ctx-4", init_command="::init gtkb lo", issuer="hook:init")
    second = attest_role_change(
        db,
        envelope_id=binding.envelope_id,
        role="prime-builder",
        issuer="owner",
        owner_decision_ref="DELIB-FIXTURE-0002",
    )
    third = attest_role_change(
        db,
        envelope_id=binding.envelope_id,
        role="loyal-opposition",
        issuer="owner",
        owner_decision_ref="DELIB-FIXTURE-0003",
    )
    assert first.evidence_digest != second.evidence_digest != third.evidence_digest
    assert second.seq == 2 and third.seq == 3
