"""Surviving terminology-resolution obligations after static map retirement."""

from __future__ import annotations

from copy import deepcopy

import pytest
from groundtruth_kb.authority import AuthorityResolutionError, compact_status, resolve_term


def term(identifier="PROJECT", *, scope="platform", status="active", aliases=None):
    return {
        "id": identifier,
        "canonical_term": "project",
        "scope": scope,
        "lifecycle_status": status,
        "accepted_synonyms": aliases,
        "discouraged_synonyms": ["bucket"],
    }


@pytest.mark.parametrize("query", ["PROJECT", "project", " Work Group ", "work\tgroup"])
def test_exact_current_names_and_authored_synonyms_resolve_without_files(query):
    record = term(aliases=["Work Group"])
    original = deepcopy(record)
    result = resolve_term(query, records=[record])
    assert result["status"] == "resolved" and result["record"] == record
    assert record == original


@pytest.mark.parametrize("status", ["candidate", "deprecated", "retired"])
def test_noncurrent_terms_never_resolve_as_current_authority(status):
    result = resolve_term("project", records=[term(status=status)])
    assert result["status"] == "not_found"
    assert compact_status(records=[term(status=status)])["active_records"] == 0


def test_discouraged_synonyms_are_not_silent_aliases():
    assert resolve_term("bucket", records=[term()])["status"] == "not_found"


def test_ambiguous_names_require_scope_or_exact_record_id():
    records = [term("PROJECT-A", scope="a"), term("PROJECT-B", scope="b")]
    assert resolve_term("project", records=records)["status"] == "ambiguous"
    assert resolve_term("project", records=records, scope="b")["record"]["id"] == "PROJECT-B"
    assert resolve_term("PROJECT-A", records=records)["record"]["id"] == "PROJECT-A"
    assert compact_status(records=records)["status"] == "pass"
    records[1]["scope"] = "a"
    status = compact_status(records=records)
    assert status["status"] == "fail"
    assert status["ambiguities"] == [{"scope": "a", "term": "project", "ids": ["PROJECT-A", "PROJECT-B"]}]


@pytest.mark.parametrize("aliases", [{}, "", [None], [" "], 17])
def test_malformed_current_names_refuse_instead_of_being_normalized(aliases):
    with pytest.raises(AuthorityResolutionError):
        resolve_term("project", records=[term(aliases=aliases)])


def test_unknown_term_suggests_current_names_only():
    result = resolve_term("projec", records=[term(), term("OLD", status="retired", aliases=["projec"])])
    assert result["status"] == "not_found" and "project" in result["candidates"]
    assert "old" not in result["candidates"]


@pytest.mark.parametrize("aliases", [{}, "", [None], [" "], 17])
def test_unrelated_malformed_entry_does_not_disable_valid_resolution_or_status(aliases):
    valid = term()
    broken = {**term("BROKEN", aliases=aliases), "canonical_term": "broken definition"}
    before = deepcopy([valid, broken])
    records = [valid, broken]
    assert resolve_term("project", records=records)["record"] == valid
    assert resolve_term("not present", records=records)["status"] == "not_found"
    status = compact_status(records=records)
    assert status["status"] == "fail"
    assert status["active_records"] == 2
    assert [r["id"] for r in status["validation_issues"]] == ["BROKEN"]
    with pytest.raises(AuthorityResolutionError, match="BROKEN"):
        resolve_term("BROKEN", records=records)
    assert records == before


def test_a_malformed_entry_sharing_the_requested_name_cannot_be_ignored():
    with pytest.raises(AuthorityResolutionError):
        resolve_term("project", records=[term(), term("BROKEN", aliases=[None])])


def test_malformed_entries_outside_the_requested_scope_do_not_participate():
    records = [term(), term("BROKEN", scope="other", aliases=[None])]
    assert resolve_term("project", records=records, scope="platform")["status"] == "resolved"
    assert compact_status(records=records, scope="platform")["status"] == "pass"
