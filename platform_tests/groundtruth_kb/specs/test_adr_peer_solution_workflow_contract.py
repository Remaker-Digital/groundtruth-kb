"""Slice 1 regression tests for ADR-PEER-SOLUTION-WORKFLOW-CONTRACT-001.

Trace: ``bridge/gtkb-peer-solution-workflow-contract-adr-007.md`` (REVISED-3)
IP-3 content-invariant assertions; Codex GO at ``-008``.

The ADR records the architectural decision to borrow Archon's declarative
workflow / DAG vocabulary without importing Archon as a runtime authority.
These tests assert the structural shape of the MemBase row and the four
content-invariant authority claims (Archon no-runtime-authority + MemBase +
bridge + Deliberation Archive each tied to authoritative-language tokens).

Per the bridge proposal's IP-3, the assertions use substring search with
case-insensitive options where the authority terms are canonical so that
wording variations within the same semantic constraint still pass.
"""

from __future__ import annotations

import re

import pytest

from groundtruth_kb import KnowledgeDB

ADR_ID = "ADR-PEER-SOLUTION-WORKFLOW-CONTRACT-001"


@pytest.fixture(scope="module")
def adr_spec() -> dict:
    db = KnowledgeDB("groundtruth.db")
    spec = db.get_spec(ADR_ID)
    assert spec is not None, f"{ADR_ID} not found in MemBase"
    return spec


def _decision_text(spec: dict) -> str:
    desc = spec.get("description") or ""
    match = re.search(
        r"##\s+Decision\s*\n(?P<body>.+?)(?=^##\s+\S|\Z)",
        desc,
        re.DOTALL | re.MULTILINE,
    )
    assert match, "## Decision section anchor not located in ADR description"
    return match.group("body")


def test_adr_row_structure(adr_spec: dict) -> None:
    """T1 (structural): ADR row exists with type='architecture_decision',
    status='specified', and the four required ADR sections."""
    assert adr_spec.get("type") == "architecture_decision"
    assert adr_spec.get("status") == "specified"
    desc = adr_spec.get("description") or ""
    assert desc.strip(), "ADR description must be non-empty"
    for header in ("## Context", "## Decision", "## Failed Approaches", "## Consequences"):
        assert header in desc, f"ADR description missing required section: {header}"


def test_decision_claims_archon_no_runtime_authority(adr_spec: dict) -> None:
    """T2 (content-invariant 1 of 4): the Decision text negates Archon as a
    runtime authority."""
    decision = _decision_text(adr_spec)
    canonical = re.search(r"does not import Archon", decision, re.IGNORECASE)
    alternative = re.search(
        r"(no|not|does not)[^.\n]{0,40}Archon as a runtime authority",
        decision,
        re.IGNORECASE,
    )
    assert canonical or alternative, (
        "Decision section must include a no-runtime-authority claim against "
        "Archon: expected 'does not import Archon' or an equivalent negation "
        "of 'Archon as a runtime authority'"
    )


def test_decision_names_membase_as_authoritative(adr_spec: dict) -> None:
    """T3 (content-invariant 2 of 4): the Decision text ties MemBase to
    authoritative or source-of-truth language."""
    decision = _decision_text(adr_spec)
    assert re.search(
        r"MemBase[^.\n]{0,120}(authoritative|source of truth)",
        decision,
        re.IGNORECASE,
    ), (
        "Decision section must tie MemBase to authoritative / source-of-truth "
        "language"
    )


def test_decision_names_bridge_as_authoritative(adr_spec: dict) -> None:
    """T4 (content-invariant 3 of 4): the Decision text ties bridge to
    authoritative or review language."""
    decision = _decision_text(adr_spec)
    assert re.search(
        r"\bbridge\b[^.\n]{0,120}(authoritative|review)",
        decision,
        re.IGNORECASE,
    ), "Decision section must tie bridge to authoritative / review language"


def test_decision_names_deliberation_archive_as_authoritative(adr_spec: dict) -> None:
    """T5 (content-invariant 4 of 4): the Decision text ties Deliberation
    Archive to authoritative or reasoning language."""
    decision = _decision_text(adr_spec)
    assert re.search(
        r"Deliberation Archive[^.\n]{0,150}(authoritative|reasoning)",
        decision,
        re.IGNORECASE,
    ), (
        "Decision section must tie Deliberation Archive to authoritative / "
        "reasoning language"
    )
