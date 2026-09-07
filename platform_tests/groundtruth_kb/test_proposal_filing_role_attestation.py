"""Proposal filing resolves Prime eligibility from exact-init attestation only."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
for _extra in (PROJECT_ROOT, SRC):
    if str(_extra) not in sys.path:
        sys.path.insert(0, str(_extra))

from groundtruth_kb.bridge import proposal_filing  # noqa: E402
from groundtruth_kb.session.attestation import attest_role_change, bind_exact_init  # noqa: E402


def _schema(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    with conn:
        conn.execute(
            "CREATE TABLE session_init_bindings ("
            "invoking_context TEXT PRIMARY KEY, envelope_id TEXT, command_digest TEXT, "
            "subject TEXT, created_at TEXT)"
        )
        conn.execute(
            "CREATE TABLE session_role_attestations ("
            "envelope_id TEXT, seq INTEGER, role TEXT, source_event TEXT, "
            "issuer TEXT, created_at TEXT, evidence_digest TEXT, "
            "PRIMARY KEY (envelope_id, seq))"
        )
    conn.close()


def _bind(root: Path, context: str, role: str):
    _schema(root / "groundtruth.db")
    return bind_exact_init(
        root / "groundtruth.db",
        invoking_context=context,
        init_command=f"::init gtkb {role}",
        issuer="fixture-harness",
    )


def test_prime_exact_init_persists_binding_and_attestation_evidence(tmp_path: Path) -> None:
    context = "proposal-pb-context"
    binding, attestation = _bind(tmp_path, context, "pb")

    actor = proposal_filing._resolve_actor_context(tmp_path, session_context_id=context)

    assert actor == {
        "session_context_id": context,
        "session_envelope_id": binding.envelope_id,
        "acting_role_attestation": attestation.evidence_reference,
        "role": "prime-builder",
    }


def test_lo_exact_init_cannot_file_prime_proposal(tmp_path: Path) -> None:
    context = "proposal-lo-context"
    _bind(tmp_path, context, "lo")

    with pytest.raises(proposal_filing.ProposalFilingError, match="requires prime-builder role"):
        proposal_filing._resolve_actor_context(tmp_path, session_context_id=context)


def test_unbound_context_fails_without_registry_or_session_document_fallback(tmp_path: Path) -> None:
    _schema(tmp_path / "groundtruth.db")
    registry = tmp_path / "harness-state" / "harness-registry.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        '{"harnesses":[{"id":"A","harness_name":"codex","role":["prime-builder"]}]}',
        encoding="utf-8",
    )

    with pytest.raises(proposal_filing.ProposalFilingError, match="session-init binding exists"):
        proposal_filing._resolve_actor_context(tmp_path, session_context_id="unbound-context")


def test_later_role_change_cannot_make_one_context_prime(tmp_path: Path) -> None:
    context = "proposal-role-change-context"
    binding, _attestation = _bind(tmp_path, context, "lo")
    attest_role_change(
        tmp_path / "groundtruth.db",
        envelope_id=binding.envelope_id,
        role="prime-builder",
        issuer="fixture-owner",
        owner_decision_ref="DELIB-OBSOLETE-ROLE-CHANGE-FIXTURE",
    )

    with pytest.raises(proposal_filing.ProposalFilingError, match="exact-init"):
        proposal_filing._resolve_actor_context(tmp_path, session_context_id=context)
