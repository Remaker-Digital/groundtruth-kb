"""Startup binds the session role attestation (WI-6262, attestation slice 1).

Landed by bridge/gtkb-session-role-attestation-service-slice-1 (GO at -004).

The load-bearing assertion is the refusal one: a binding is created ONLY from a
literal canonical init command. The binding digests that command and is
immutable, so reconstructing it from resolved role plus work subject could bind
a subject the owner never typed, permanently.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
for _extra in (PROJECT_ROOT, PROJECT_ROOT / "groundtruth-kb" / "src"):
    if str(_extra) not in sys.path:
        sys.path.insert(0, str(_extra))

from groundtruth_kb.session.attestation import binding_for_context  # noqa: E402

import scripts.session_self_initialization as ssi  # noqa: E402

CONTEXT = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"


def _schema(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    with conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS session_init_bindings ("
            "invoking_context TEXT PRIMARY KEY, envelope_id TEXT, command_digest TEXT, "
            "subject TEXT, created_at TEXT)"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS session_role_attestations ("
            "envelope_id TEXT, seq INTEGER, role TEXT, source_event TEXT, "
            "issuer TEXT, created_at TEXT, evidence_digest TEXT, "
            "PRIMARY KEY (envelope_id, seq))"
        )
    conn.close()


@pytest.fixture
def root(tmp_path: Path) -> Path:
    _schema(tmp_path / "groundtruth.db")
    return tmp_path


def test_literal_init_command_creates_a_binding(root):
    reference = ssi._bind_session_role_attestation(root, CONTEXT, "::init gtkb pb", "claude")
    assert reference is not None
    assert reference.startswith("role-attestation:SENV-")
    binding = binding_for_context(root / "groundtruth.db", CONTEXT)
    assert binding.subject == "gtkb"


def test_binding_records_the_role_the_command_states(root):
    ssi._bind_session_role_attestation(root, CONTEXT, "::init gtkb lo", "claude")
    conn = sqlite3.connect(root / "groundtruth.db")
    role = conn.execute("SELECT role FROM session_role_attestations").fetchone()[0]
    conn.close()
    assert role == "loyal-opposition"


def test_absent_command_creates_nothing(root):
    """--role-profile startups carry no literal command; nothing may be bound."""
    assert ssi._bind_session_role_attestation(root, CONTEXT, "", "claude") is None
    conn = sqlite3.connect(root / "groundtruth.db")
    count = conn.execute("SELECT COUNT(*) FROM session_init_bindings").fetchone()[0]
    conn.close()
    assert count == 0, "a startup without a literal init command must not bind"


def test_malformed_command_creates_nothing(root):
    """Only the exact canonical grammar binds; near-misses create nothing."""
    for command in ("::init gtkb", "init gtkb pb", "::init gtkb pb ", "::INIT gtkb pb", "::init gtkb prime"):
        assert ssi._bind_session_role_attestation(root, CONTEXT, command, "claude") is None
    conn = sqlite3.connect(root / "groundtruth.db")
    count = conn.execute("SELECT COUNT(*) FROM session_init_bindings").fetchone()[0]
    conn.close()
    assert count == 0


def test_re_entry_is_a_no_op_not_a_failure(root):
    """The binding is immutable; a second init changes nothing and raises nothing."""
    first = ssi._bind_session_role_attestation(root, CONTEXT, "::init gtkb pb", "claude")
    assert first is not None
    second = ssi._bind_session_role_attestation(root, CONTEXT, "::init gtkb lo", "claude")
    assert second is None

    conn = sqlite3.connect(root / "groundtruth.db")
    roles = [r[0] for r in conn.execute("SELECT role FROM session_role_attestations")]
    subject = conn.execute("SELECT subject FROM session_init_bindings").fetchone()[0]
    conn.close()
    assert roles == ["prime-builder"], "re-init must not append a contradicting attestation"
    assert subject == "gtkb"


def test_missing_session_id_creates_nothing(root):
    assert ssi._bind_session_role_attestation(root, "", "::init gtkb pb", "claude") is None


def test_unexpected_failure_is_logged_and_swallowed(root, monkeypatch):
    """Startup must never break on attestation, but faults must leave a trace."""

    def _boom(*_args, **_kwargs):
        from groundtruth_kb.session.attestation import RoleAttestationError

        raise RoleAttestationError("some_other_code", "synthetic")

    monkeypatch.setattr("groundtruth_kb.session.attestation.bind_exact_init", _boom, raising=True)
    assert ssi._bind_session_role_attestation(root, CONTEXT, "::init gtkb pb", "claude") is None

    log = root / ".gtkb-state" / "session-attestation" / "bind-failures.jsonl"
    assert log.exists(), "an unexpected binding failure must be recorded"
    assert "some_other_code" in log.read_text(encoding="utf-8")


def test_absent_schema_is_self_created(tmp_path):
    """A bare project root still binds: the service creates its own schema.

    Asserted explicitly because it is what makes the startup call safe on a
    fresh checkout, where no attestation tables exist yet.
    """
    reference = ssi._bind_session_role_attestation(tmp_path, CONTEXT, "::init gtkb pb", "claude")
    assert reference is not None
    assert binding_for_context(tmp_path / "groundtruth.db", CONTEXT).subject == "gtkb"


def test_corrupt_database_does_not_break_startup(tmp_path):
    """A non-database file where the DB belongs: return None, never raise."""
    (tmp_path / "groundtruth.db").write_bytes(b"this is not a sqlite database")
    assert ssi._bind_session_role_attestation(tmp_path, CONTEXT, "::init gtkb pb", "claude") is None
