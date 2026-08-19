"""Focused implementation-start exact-init role-attestation regressions."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "implementation_authorization.py"


@pytest.fixture(scope="module")
def auth_module():
    spec = importlib.util.spec_from_file_location(
        "wi6465_implementation_authorization", SCRIPT_PATH
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _packet(auth_module, bridge_id: str = "wi6465-fixture") -> dict[str, Any]:
    packet: dict[str, Any] = {
        "schema_version": 2,
        "bridge_id": bridge_id,
        "target_path_globs": ["scripts/implementation_authorization.py"],
    }
    packet["packet_hash"] = auth_module.packet_hash(packet)
    return packet


def _bind(root: Path, session_id: str, *, role: str = "prime-builder"):
    from groundtruth_kb.session.attestation.service import bind_exact_init

    token = "pb" if role == "prime-builder" else "lo"
    return bind_exact_init(
        root / "groundtruth.db",
        invoking_context=session_id,
        init_command=f"::init gtkb {token}",
        issuer="test/exact-init",
    )


def _stub_start_dependencies(
    auth_module,
    monkeypatch: pytest.MonkeyPatch,
    *,
    session_id: str,
    binding,
    attestation,
    holder_overrides: dict[str, Any] | None = None,
) -> None:
    holder = {
        "thread_slug": "wi6465-fixture",
        "session_id": session_id,
        "claim_kind": auth_module.bridge_work_intent_registry.CLAIM_KIND_GO_IMPLEMENTATION,
        "acting_role": attestation.role,
        "session_envelope_id": binding.envelope_id,
        "acting_role_attestation": attestation.evidence_reference,
    }
    holder.update(holder_overrides or {})
    monkeypatch.setattr(
        auth_module, "work_intent_claim_block_reason", lambda *_args, **_kwargs: None
    )
    monkeypatch.setattr(
        auth_module.bridge_work_intent_registry,
        "current_holder",
        lambda *_args, **_kwargs: holder,
    )
    monkeypatch.setattr(
        auth_module,
        "validate_packet_project_authorization_operation",
        lambda *_args, **_kwargs: None,
    )


def test_prime_builder_binding_and_matching_claim_finalize(
    auth_module, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    session_id = "prime-session"
    binding, attestation = _bind(tmp_path, session_id)
    _stub_start_dependencies(
        auth_module,
        monkeypatch,
        session_id=session_id,
        binding=binding,
        attestation=attestation,
    )

    finalized = auth_module.finalize_implementation_start_packet(
        tmp_path,
        _packet(auth_module),
        session_id=session_id,
    )

    start = finalized["implementation_start"]
    assert start["schema_version"] == 2
    assert "worker_role_provenance" not in start
    assert start["role_attestation"] == {
        "schema_version": 1,
        "invoking_context": session_id,
        "session_envelope_id": binding.envelope_id,
        "subject": "gtkb",
        "init_command_digest": binding.command_digest,
        "binding_created_at": binding.created_at,
        "role": "prime-builder",
        "source_event": "exact_init",
        "issuer": "test/exact-init",
        "attested_at": attestation.created_at,
        "evidence_reference": attestation.evidence_reference,
    }
    claim = start["work_intent_claim"]
    assert claim["session_envelope_id"] == binding.envelope_id
    assert claim["acting_role_attestation"] == attestation.evidence_reference


def test_harness_and_worker_document_signals_cannot_override_lo_attestation(
    auth_module, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    session_id = "lo-session"
    binding, attestation = _bind(tmp_path, session_id, role="loyal-opposition")
    _stub_start_dependencies(
        auth_module,
        monkeypatch,
        session_id=session_id,
        binding=binding,
        attestation=attestation,
    )
    monkeypatch.setenv("GTKB_HARNESS_NAME", "codex")
    monkeypatch.setenv("GTKB_HARNESS_ID", "A")
    monkeypatch.setenv("CODEX_THREAD_ID", session_id)
    worker_path = (
        tmp_path
        / "harness-state"
        / "codex"
        / "session-envelopes"
        / f"{session_id}.json"
    )
    worker_path.parent.mkdir(parents=True)
    worker_path.write_text('{"role":"prime-builder","status":"open"}', encoding="utf-8")

    with pytest.raises(
        auth_module.AuthorizationError,
        match="requires a prime-builder exact-init role attestation",
    ):
        auth_module.finalize_implementation_start_packet(
            tmp_path,
            _packet(auth_module),
            session_id=session_id,
        )


def test_missing_binding_fails_closed(
    auth_module, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from groundtruth_kb.session.attestation.service import Attestation, Binding

    session_id = "unbound-session"
    binding = Binding(
        session_id, "SENV-never-written", "digest", "gtkb", "2026-08-16T00:00:00Z"
    )
    attestation = Attestation(
        binding.envelope_id,
        1,
        "prime-builder",
        "exact_init",
        "test/exact-init",
        binding.created_at,
        "evidence-digest",
    )
    _stub_start_dependencies(
        auth_module,
        monkeypatch,
        session_id=session_id,
        binding=binding,
        attestation=attestation,
    )

    with pytest.raises(
        auth_module.AuthorizationError, match="no session-init binding exists"
    ):
        auth_module.finalize_implementation_start_packet(
            tmp_path,
            _packet(auth_module),
            session_id=session_id,
        )


def test_later_role_change_event_cannot_authorize_start(
    auth_module, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from groundtruth_kb.session.attestation.service import attest_role_change

    session_id = "role-change-session"
    binding, _initial = _bind(tmp_path, session_id)
    changed = attest_role_change(
        tmp_path / "groundtruth.db",
        envelope_id=binding.envelope_id,
        role="prime-builder",
        issuer="test/owner-role-change",
        owner_decision_ref="DELIB-OBSOLETE-ROLE-CHANGE",
    )
    _stub_start_dependencies(
        auth_module,
        monkeypatch,
        session_id=session_id,
        binding=binding,
        attestation=changed,
    )

    with pytest.raises(
        auth_module.AuthorizationError, match="immutable exact-init role attestation"
    ):
        auth_module.finalize_implementation_start_packet(
            tmp_path,
            _packet(auth_module),
            session_id=session_id,
        )


@pytest.mark.parametrize(
    ("holder_overrides", "error"),
    [
        ({"acting_role": "loyal-opposition"}, "acting role does not match"),
        ({"session_envelope_id": "SENV-wrong"}, "session envelope does not match"),
        (
            {"acting_role_attestation": "role-attestation:wrong"},
            "role-attestation reference is not current",
        ),
    ],
)
def test_claim_role_evidence_mismatch_fails_closed(
    auth_module,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    holder_overrides: dict[str, Any],
    error: str,
) -> None:
    session_id = "mismatch-session"
    binding, attestation = _bind(tmp_path, session_id)
    _stub_start_dependencies(
        auth_module,
        monkeypatch,
        session_id=session_id,
        binding=binding,
        attestation=attestation,
        holder_overrides=holder_overrides,
    )

    with pytest.raises(auth_module.AuthorizationError, match=error):
        auth_module.finalize_implementation_start_packet(
            tmp_path,
            _packet(auth_module),
            session_id=session_id,
        )
