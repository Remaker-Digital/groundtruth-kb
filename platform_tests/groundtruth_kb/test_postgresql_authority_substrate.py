"""Executable completeness checks for the WI-6247 PostgreSQL formal authority set."""

from __future__ import annotations

import pathlib
import sqlite3

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
MEMBASE = REPO_ROOT / "groundtruth.db"

ADR = "ADR-POSTGRESQL-AUTHORITY-SUBSTRATE-001"
DCL = "DCL-POSTGRESQL-AUTHORITY-SUBSTRATE-CHECKABLE-001"
GOV = "GOV-POSTGRESQL-LAN-AUTHORITY-SERVICE-001"
REQ = "REQ-POSTGRESQL-LAN-AUTHORITY-SERVICE-001"
MEMBASE_IDENTITY_ADR = "ADR-STANDING-BACKLOG-DB-AUTHORITY-001"
RETIRED_DISPATCHER_ADR = "ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001"


def _spec(spec_id: str) -> sqlite3.Row | None:
    if not MEMBASE.exists():
        pytest.skip("live MemBase not present in this checkout")
    connection = sqlite3.connect(f"file:{MEMBASE}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        return connection.execute(
            "SELECT id, version, status, type, description FROM current_specifications WHERE id = ?",
            (spec_id,),
        ).fetchone()
    finally:
        connection.close()


def _body(spec_id: str) -> str:
    row = _spec(spec_id)
    assert row is not None, f"{spec_id} is absent from MemBase"
    assert row["status"] == "active"
    return row["description"] or ""


def test_complete_formal_set_is_active_and_typed() -> None:
    expected = {
        ADR: "architecture_decision",
        DCL: "design_constraint",
        GOV: "governance",
        REQ: "requirement",
    }
    for spec_id, expected_type in expected.items():
        row = _spec(spec_id)
        assert row is not None, f"{spec_id} is absent from MemBase"
        assert row["status"] == "active"
        assert row["type"] == expected_type


def test_membase_identity_is_preserved_and_retired_dispatcher_stays_retired() -> None:
    identity = _spec(MEMBASE_IDENTITY_ADR)
    retired = _spec(RETIRED_DISPATCHER_ADR)
    assert identity is not None and identity["status"] == "active"
    assert retired is not None and retired["status"] == "retired"


def test_adr_covers_host_transport_service_and_authority_boundaries() -> None:
    body = _body(ADR).lower()
    for phrase in (
        "owner-managed always-on lan host",
        "bound to loopback",
        "private-lan https service boundary",
        "versioned json and cli contracts",
        "never receive database credentials",
        "fail closed",
        "exactly one writable authority",
    ):
        assert phrase in body, f"ADR missing architecture phrase: {phrase}"


def test_adr_records_identity_capability_recovery_and_observability_choices() -> None:
    body = _body(ADR).lower()
    for phrase in (
        "installation, environment, device, harness",
        "project authorization remains only",
        "short-lived, scoped, replay-resistant capabilities",
        "rpo of at most five minutes",
        "rto of at most one hour",
        "separate self-hosted store",
        "progressive",
    ):
        assert phrase in body, f"ADR missing decision phrase: {phrase}"


def test_adr_has_complete_wordpress_adopt_adapt_reject_ledger() -> None:
    body = _body(ADR).lower()
    for phrase in ("wordpress adopt, adapt, reject ledger", "**adopt:**", "**adapt:**", "**reject:**"):
        assert phrase in body
    assert "no runtime, test, credential, secret, content, or availability dependency" in body


def test_adr_records_rejected_alternatives() -> None:
    body = _body(ADR).lower()
    for alternative in (
        "dual-write with reconciliation",
        "direct postgresql access by agents",
        "per-table cutover",
        "public-cloud or public-internet service by default",
        "wordpress as a runtime or authority dependency",
    ):
        assert alternative in body, f"ADR missing rejected alternative: {alternative}"


def test_dcl_contains_every_checkable_constraint() -> None:
    body = _body(DCL)
    for number in range(1, 15):
        assert f"C{number}." in body, f"DCL constraint C{number} is missing"
    for phrase in (
        "Single writable authority",
        "Service-only database access",
        "Private binding and transport",
        "Capability boundary",
        "Fail-closed authority",
        "Recovery objectives",
        "Telemetry separation and privacy",
        "Narrow external-state exception",
        "WordPress non-dependency",
    ):
        assert phrase in body


def test_governance_separates_authorization_from_access_control() -> None:
    body = _body(GOV)
    assert "Project authorization is read only from the project's `authorization` field" in body
    assert "Authentication and short-lived capabilities control service access" in body
    assert "Neither mechanism substitutes for the other" in body


def test_governance_forbids_direct_database_and_fallback_authority() -> None:
    body = _body(GOV).lower()
    for phrase in (
        "direct agent database access",
        "silent fallback",
        "dual writes",
        "may not answer from cached domain state",
        "never an authority source",
    ):
        assert phrase in body


def test_requirement_set_pins_recovery_retention_and_slos() -> None:
    body = _body(REQ).lower()
    for phrase in (
        "rpo no greater than five minutes",
        "rto no greater than one hour",
        "raw logs and traces for 30 days",
        "slo aggregates for 13 months",
        "99.5 percent monthly availability",
        "ordinary reads no greater than 250 ms",
        "init/open no greater than 500 ms",
        "governed mutations no greater than one second",
    ):
        assert phrase in body


def test_requirement_set_pins_security_privacy_and_external_state() -> None:
    body = _body(REQ).lower()
    for phrase in (
        "never expose postgresql credentials",
        "consume it atomically once",
        "reject replay",
        "telemetry to a separate self-hosted",
        "reject credentials, tokens, capabilities, prompts, transcripts, bridge bodies",
        "narrow project-root exception",
    ):
        assert phrase in body


def test_authoritative_bodies_do_not_cite_ephemeral_or_retired_authority_carriers() -> None:
    forbidden = (
        "bridge/",
        "delib-",
        "pauth",
        ".gtkb-state",
        "harness-state",
        ".groundtruth/formal-artifact-approvals",
        "askuserquestion",
    )
    offenders: list[str] = []
    for spec_id in (ADR, DCL, GOV, REQ):
        body = _body(spec_id).lower()
        offenders.extend(f"{spec_id}: {token}" for token in forbidden if token in body)
    assert offenders == [], "forbidden authority-carrier references:\n" + "\n".join(offenders)


def test_no_module_opens_both_membase_stores_for_writing() -> None:
    roots = (REPO_ROOT / "groundtruth-kb" / "src" / "groundtruth_kb", REPO_ROOT / "scripts")
    offenders: list[str] = []
    for root in roots:
        if not root.is_dir():
            continue
        for path in root.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            writes_sqlite = "sqlite3.connect(" in text and "mode=ro" not in text
            writes_postgres = "psycopg.connect(" in text
            if writes_sqlite and writes_postgres:
                offenders.append(str(path.relative_to(REPO_ROOT)))
    assert offenders == [], "dual writable-store modules:\n" + "\n".join(offenders)
