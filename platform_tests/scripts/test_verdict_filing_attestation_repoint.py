"""Verdict filing derives author metadata from the role attestation (WI-6262).

Landed by bridge/gtkb-session-role-attestation-service-slice-1 (GO at -004),
verification expectation V1/V2: the repoint lands in
``groundtruth_kb/bridge/verdict_filing.py`` and consumer tests accompany it.

The load-bearing assertions are the ordering ones. Before this repoint the
first resolver consulted inferred role from durable registry state, which is a
routing label rather than an identity oracle; the attestation resolver must be
consulted first, and a session that HAS a binding must not fall through.
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

from groundtruth_kb.bridge import verdict_filing  # noqa: E402
from groundtruth_kb.session.attestation import (  # noqa: E402
    RoleAttestationError,
    bind_exact_init,
)

CONTENT = (
    "VERIFIED\n\n"
    "author_model: test-model\n"
    "author_model_version: test-model-v1\n"
    "author_model_configuration: fixture configuration\n\n"
    "# Body\n"
)


def _schema(db_path: Path) -> None:
    """Create only the two attestation tables the service reads and writes."""
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
def bound_root(tmp_path: Path) -> tuple[Path, str]:
    """A project root whose DB carries a binding for a known invoking context."""
    db_path = tmp_path / "groundtruth.db"
    _schema(db_path)
    context = "11111111-2222-3333-4444-555555555555"
    bind_exact_init(
        db_path,
        invoking_context=context,
        init_command="::init gtkb pb",
        issuer="fixture-harness",
    )
    return tmp_path, context


def test_attestation_metadata_carries_the_attested_role(bound_root):
    root, context = bound_root
    metadata = verdict_filing._metadata_from_attestation(context, root, CONTENT)
    assert metadata is not None
    assert metadata["author_identity"].startswith("prime-builder/")
    assert metadata["author_session_context_id"] == context


def test_attestation_metadata_persists_the_evidence_reference(bound_root):
    """The evidence reference is what makes the attribution auditable."""
    root, context = bound_root
    metadata = verdict_filing._metadata_from_attestation(context, root, CONTENT)
    reference = metadata["author_role_attestation"]
    assert reference.startswith("role-attestation:SENV-")
    assert reference.count(":") == 3


def test_attested_role_reflects_the_init_command_not_the_registry(tmp_path):
    """A `lo` init yields loyal-opposition regardless of durable registry role."""
    db_path = tmp_path / "groundtruth.db"
    _schema(db_path)
    context = "99999999-8888-7777-6666-555555555555"
    bind_exact_init(
        db_path,
        invoking_context=context,
        init_command="::init gtkb lo",
        issuer="fixture-harness",
    )
    metadata = verdict_filing._metadata_from_attestation(context, tmp_path, CONTENT)
    assert metadata["author_identity"].startswith("loyal-opposition/")


def test_model_fields_come_from_the_artifact_declaration(bound_root):
    """Model identity is not derivable; it must not be fabricated."""
    root, context = bound_root
    metadata = verdict_filing._metadata_from_attestation(context, root, CONTENT)
    assert metadata["author_model"] == "test-model"
    assert metadata["author_model_version"] == "test-model-v1"
    assert metadata["author_model_configuration"] == "fixture configuration"


def test_model_fields_omitted_when_the_artifact_declares_none(bound_root):
    root, context = bound_root
    metadata = verdict_filing._metadata_from_attestation(context, root, "VERIFIED\n\n# Body\n")
    assert "author_model" not in metadata


def test_unbound_context_returns_none_for_ordered_migration(bound_root):
    """no_session_binding is the ONLY case that falls through to legacy paths."""
    root, _context = bound_root
    assert verdict_filing._metadata_from_attestation("not-a-bound-context", root, CONTENT) is None


def test_bound_context_with_unresolvable_role_raises_rather_than_falling_through(bound_root):
    """A session that HAS a binding must not silently reach the legacy resolver.

    Falling through would re-admit registry-inferred role, which is the defect
    the attestation service exists to remove.
    """
    root, context = bound_root
    conn = sqlite3.connect(root / "groundtruth.db")
    with conn:
        conn.execute("DELETE FROM session_role_attestations")
    conn.close()

    with pytest.raises((verdict_filing.VerdictFilingError, RoleAttestationError)):
        verdict_filing._metadata_from_attestation(context, root, CONTENT)


def test_envelope_entry_point_prefers_the_attestation(bound_root):
    """_metadata_from_envelope consults the attestation before legacy resolvers."""
    root, context = bound_root
    metadata = verdict_filing._metadata_from_envelope(context, root, CONTENT)
    assert "author_role_attestation" in metadata, (
        "the attestation branch must win; a metadata dict without the evidence "
        "reference means a legacy resolver answered first"
    )
    assert metadata["author_session_context_id"] == context


def test_harness_id_resolves_from_the_identity_map_not_from_the_name():
    """The name-to-ID mapping is owner-assigned, so it must be read, not derived."""
    assert verdict_filing._harness_id_for("", PROJECT_ROOT) == ""
    assert verdict_filing._harness_id_for("definitely-not-a-harness", PROJECT_ROOT) == ""
    assert verdict_filing._harness_id_for("claude", PROJECT_ROOT) == "B"
