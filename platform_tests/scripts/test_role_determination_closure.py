"""Executable closure proof for WI-7311 / TEST-12296."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from groundtruth_kb.authority_client import AuthorityClient

ROOT = Path(__file__).resolve().parents[2]
OPERATING_ROLE = ROOT / ".harness-baseline-configuration" / "rules" / "operating-role.md"
CLAUDE_MD = ROOT / "CLAUDE.md"

CONTRADICTING_SPEC_IDS = {
    "GOV-HARNESS-ROLE-PORTABILITY-001",
    "GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001",
    "REQ-HARNESS-REGISTRY-001",
}


def _current_specs() -> dict[str, tuple[int, str]]:
    """Current versions and statuses from the explicitly selected native authority; no local store is read."""
    url = os.environ.get("GTKB_FORMAL_TEST_AUTHORITY_URL")
    if not url:
        pytest.fail("Set GTKB_FORMAL_TEST_AUTHORITY_URL explicitly for current formal-corpus tests")
    client = AuthorityClient(url)
    rows = {}
    for spec_id in sorted(CONTRADICTING_SPEC_IDS):
        record = client.request("GET", f"/v1/specifications/{spec_id}")
        rows[record["id"]] = (record["version"], record["status"])
    return rows


def test_contradicting_formal_records_are_no_longer_active() -> None:
    current = _current_specs()
    assert set(current) == CONTRADICTING_SPEC_IDS
    assert all(status in {"retired", "superseded"} for _, status in current.values()), current


def test_canonical_operating_role_rule_has_one_session_context_authority() -> None:
    text = OPERATING_ROLE.read_text(encoding="utf-8")
    lowered = text.lower()

    assert "::init gtkb <pb|lo>" in text
    assert "immutable for the lifetime of that context" in lowered

    forbidden = (
        "harness-state",
        "harness-registry",
        "dispatcher/default",
        "set-role",
        "gt harness roles",
        ".gtkb-state",
        "active_role:",
    )
    assert not {token for token in forbidden if token in lowered}


def test_root_guidance_has_no_retired_role_authority_or_lookup_route() -> None:
    text = CLAUDE_MD.read_text(encoding="utf-8")
    lowered = text.lower()

    assert "::init gtkb <pb|lo>" in text
    forbidden = (
        "roles attach to harnesses",
        "registered harness may hold this role",
        "dispatcher/default role",
        "gt harness roles",
        "gov-session-role-authority-001",
        "adr-role-authority-interactive-persistence-001",
        "dcl-interactive-session-role-persistence-001",
        "gov-harness-role-portability-001",
        "gov-gtkb-multi-harness-role-config-001",
    )
    assert not {token for token in forbidden if token in lowered}
