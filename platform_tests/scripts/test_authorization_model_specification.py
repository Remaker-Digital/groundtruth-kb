"""The authorization model states a project-record field, not an authorization instrument.

WI-7673 amended ``GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`` from "exact-project PAUTH is the
sole bounded implementation grant" to the simplified model: authorization is a field on the project
row, and no authorization instrument is normative.

Each test maps to one of the seven amendment clauses in the approved proposal at
``bridge/gtkb-wi7673-authorization-specification-amendment-003.md`` (GO at ``-004``).

The tests read the live specification row rather than a fixture. The amendment's value is that the
canonical row says this; a fixture would prove only that the fixture says it.
"""

from __future__ import annotations

import pytest
from groundtruth_kb.db import KnowledgeDB

SPEC_ID = "GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001"


@pytest.fixture(scope="module")
def spec() -> dict:
    row = KnowledgeDB().get_spec(SPEC_ID)
    assert row is not None, f"{SPEC_ID} is absent from MemBase"
    return row


@pytest.fixture(scope="module")
def body(spec: dict) -> str:
    """Whitespace-normalized description.

    Assertions target what the specification *says*, not where its lines happen to
    wrap, so runs of whitespace collapse to a single space before matching.
    """
    return " ".join((spec.get("description") or "").split()).lower()


def test_specification_is_active_governance(spec: dict) -> None:
    """The amendment is a new version of a live governance record, not a draft."""
    assert spec["status"] == "active"
    assert spec["type"] == "governance"
    assert spec["version"] >= 5, "the amended version is v5 or later"


# --- clause 1: authorization is a field on the project row ------------------------


def test_clause_1_authorization_is_a_project_row_field(body: str) -> None:
    assert "field on the project row" in body
    assert "`authorized` or `not authorized`" in body
    assert "new projects are created `authorized`" in body


def test_clause_1_only_owner_direction_sets_it(body: str) -> None:
    assert "owner direction sets it and nothing else does" in body


# --- clause 2: no authorization instrument ---------------------------------------


def test_clause_2_no_authorization_instrument_exists(body: str) -> None:
    """The abolished vocabulary is named as absent, not merely omitted."""
    for noun in ("instrument", "record", "envelope", "packet", "receipt", "token", "identifier"):
        assert noun in body, f"clause 2 must name {noun!r} among the abolished forms"
    assert "none is created or referenced" in body


def test_clause_2_the_title_no_longer_names_an_instrument_as_the_grant(spec: dict) -> None:
    """The prior title made the instrument the sole grant; that is the claim being retired."""
    title = (spec.get("title") or "").lower()
    assert "sole bounded implementation grant" not in title
    assert "field on the project row" in title


# --- clause 3: authorization carries no scope ------------------------------------


def test_clause_3_authorization_carries_no_scope_semantics(body: str) -> None:
    assert "no scope, expiry, mutation-class, or forbidden-operation semantics" in body


def test_clause_3_scope_lives_on_membership_and_target_paths(body: str) -> None:
    assert "work-item scope is project membership" in body
    assert "target_paths" in body


# --- clause 4: purpose is work ordering ------------------------------------------


def test_clause_4_purpose_is_work_ordering_not_permission(body: str) -> None:
    assert "work ordering" in body
    assert "not a permission system" in body
    assert "not yet, not forbidden" in body


# --- clause 5: dispatch is complete proof ----------------------------------------


def test_clause_5_dispatch_is_itself_complete_proof(body: str) -> None:
    assert "dispatch is itself" in body and "complete proof" in body
    assert "does not re-derive" in body


def test_clause_5_dispatchable_when_any_project_is_authorized(body: str) -> None:
    assert "dispatchable when any project it belongs to is `authorized`" in body


# --- clause 6: legacy records grant and deny nothing ------------------------------


def test_clause_6_legacy_records_grant_and_deny_nothing(body: str) -> None:
    assert "grant and deny nothing" in body
    assert "no live gate may derive authorization" in body


# --- clause 7: readiness controls retained, and are not authorization -------------


def test_clause_7_readiness_controls_are_retained(body: str) -> None:
    """All five controls survive the amendment; only their characterization changes."""
    for control in (
        "specification-linked implementation proposal",
        "independent loyal opposition review",
        "linked executable test",
        "live work-intent claim",
        "applicable active formal authority",
    ):
        assert control in body, f"readiness control {control!r} must be retained"


def test_clause_7_readiness_controls_are_not_authorization(body: str) -> None:
    """The distinction is the point: passing a review gate is not being authorized."""
    assert "they are not authorization" in body
    assert "passing them does not make them authorization" in body
