"""Executable contract for the minimal immutable session-init binding."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from groundtruth_kb.session.attestation.service import (
    RoleAttestationError,
    bind_exact_init,
    binding_for_context,
    retire_binding,
)


def test_legacy_session_surfaces_reduce_to_immutable_tuple(tmp_path: Path) -> None:
    db_path = tmp_path / "groundtruth.db"
    native_context_id = "11111111-2222-3333-4444-555555555555"

    created = bind_exact_init(
        db_path,
        native_context_id=native_context_id,
        init_command="::init gtkb pb",
    )
    assert binding_for_context(db_path, native_context_id) == created
    assert created.native_context_id == native_context_id
    assert created.subject == "gtkb"
    assert created.role == "prime-builder"
    assert created.session_context_id.startswith("SENV-")

    with pytest.raises(RoleAttestationError) as duplicate:
        bind_exact_init(
            db_path,
            native_context_id=native_context_id,
            init_command="::init gtkb lo",
        )
    assert duplicate.value.code == "session_already_initialized"

    assert retire_binding(db_path, native_context_id) == "retired"
    with pytest.raises(RoleAttestationError) as missing:
        binding_for_context(db_path, native_context_id)
    assert missing.value.code == "no_session_binding"
    with pytest.raises(RoleAttestationError) as replay:
        retire_binding(db_path, native_context_id)
    assert replay.value.code == "no_session_binding"

    connection = sqlite3.connect(db_path)
    try:
        retained_tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name LIKE 'session_%'"
            ).fetchall()
        }
    finally:
        connection.close()
    assert retained_tables == {"session_init_bindings"}
