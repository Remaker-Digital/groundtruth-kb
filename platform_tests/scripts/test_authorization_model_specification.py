"""Fitness of current project-authorization canon, read from explicit native authority.

These content checks accompany native behavioral tests for authorization,
single-parent membership, program boundaries and NEW-only bridge checks. A
positive content check does not replace execution or independent review.
"""

from __future__ import annotations

import pytest

from platform_tests.groundtruth_kb.specs.conftest import formal_record as formal_record

SPEC_ID = "GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001"
pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def spec(formal_record) -> dict:
    return formal_record(SPEC_ID)


@pytest.fixture(scope="module")
def body(spec: dict) -> str:
    return " ".join(spec["description"].split()).lower()


def test_specification_is_active_governance(spec: dict) -> None:
    assert spec["status"] == "active" and spec["type"] == "governance"
    assert isinstance(spec["version"], int) and spec["version"] > 0
    assert {
        "groundtruth-kb/src/groundtruth_kb/native_authority.py",
        "groundtruth-kb/src/groundtruth_kb/cli_authority.py",
        "groundtruth-kb/src/groundtruth_kb/bridge/native.py",
    } <= set(spec["source_paths"])
    assert "groundtruth-kb/src/groundtruth_kb/db.py" not in spec["source_paths"]


def test_clause_1_authorization_is_a_project_row_field(body: str) -> None:
    assert "one authorization field named authorization" in body
    assert "value authorized or not authorized" in body
    assert "new execution projects default to authorized" in body
    assert "project-gtkb-new-work-intake, which is permanently not authorized" in body
    assert "programs have no authorization value" in body


def test_clause_1_only_owner_direction_sets_it(body: str) -> None:
    assert "owner direction sets it" in body
    assert "agent-initiated membership change cannot set authorization" in body


def test_clause_2_no_authorization_instrument_exists(body: str) -> None:
    assert "no separate authorization artifact, identifier, packet, receipt, token, or decision ledger exists" in body


def test_clause_2_the_title_no_longer_names_an_instrument_as_the_grant(spec: dict) -> None:
    title = spec["title"].lower()
    assert "authorization" in title and "work ordering" in title and "one current field" in title
    assert "sole bounded implementation grant" not in title


def test_clause_3_authorization_carries_no_scope_semantics(body: str) -> None:
    assert (
        "no change scope, expiry, mutation classes, forbidden operations, credentials, or per-action permissions"
        in body
    )


def test_clause_3_scope_lives_on_membership_and_target_paths(body: str) -> None:
    assert "each work item belongs to exactly one execution project" in body
    assert "change scope is the proposal's target_paths together with its applicable current formal authority" in body


def test_clause_4_purpose_is_work_ordering_not_permission(body: str) -> None:
    assert "whether new work may be dispatched now" in body
    assert "distinct from activation, verification, concurrency, independent review, and completion" in body
    assert "no change scope" in body and "per-action permissions" in body


def test_clause_5_dispatch_is_itself_complete_proof(body: str) -> None:
    assert "a dispatch is sufficient direction" in body
    assert "check is confined to a new proposal" in body
    assert "later authorization change does not invalidate an already initiated bridge chain" in body


def test_clause_5_dispatch_uses_exactly_one_current_parent(body: str) -> None:
    assert "derives this ordering condition from that current parent" in body
    assert "program sequences projects and cannot directly contain executable work items" in body
    assert "unattached or multiply attached items require reconciliation to one parent" in body
    assert (
        "move must atomically replace the current parent, retain history, and return the new membership on readback"
        in body
    )
    assert "membership of a commit-terminal work item is immutable" in body


def test_clause_6_legacy_records_grant_and_deny_nothing(body: str) -> None:
    assert "labels and historical membership-role fields confer no alternative membership or authority" in body
    assert "no separate authorization artifact" in body
    assert "legacy resolution label alone is not proof of that terminal state" in body


def test_clause_7_readiness_controls_are_retained(body: str) -> None:
    for requirement in (
        "applicable current formal specification",
        "specification-linked proposal",
        "independent loyal opposition go",
        "linked executable test and test-plan phase",
        "matching claim for the next bridge action",
    ):
        assert requirement in body
    assert "claiming an action does not give an agent ownership of its work item or chain" in body


def test_clause_7_readiness_controls_are_not_authorization(body: str) -> None:
    assert "review, evidence, and concurrency controls, not additional authorization carriers" in body
