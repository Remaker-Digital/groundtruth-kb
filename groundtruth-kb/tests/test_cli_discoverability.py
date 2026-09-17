"""Work-item readback and history through the native authority (O-7 R04).

Carries the retained duties of the SQLite-era discoverability cases: `gt backlog show` reads the current record,
`--json` emits the record object, `--history` renders the recorded version chain, a missing identifier is a usage
error, an unknown identifier exits nonzero without output that looks like a record, and JSON with history carries
`current` and `history`. History is read-only and comes from the kernel's record_history, not from a client copy.
"""

from __future__ import annotations

import json

import pytest

pytestmark = [pytest.mark.integration, pytest.mark.timeout(300)]


SEED: tuple[tuple[str, str, dict[str, object]], ...] = (
    (
        "specifications",
        "SPEC-1",
        {"fields": {"title": "Required effect", "description": "Preserve complete work", "status": "active"}},
    ),
    (
        "tests",
        "TEST-1",
        {
            "fields": {
                "title": "Effect test",
                "spec_id": "SPEC-1",
                "test_type": "integration",
                "test_file": "tests/test_effect.py",
                "expected_outcome": "Effect observed",
            }
        },
    ),
    ("test-plans", "PLAN-1", {"fields": {"title": "Behavioral qualification"}}),
    (
        "test-phases",
        "PHASE-1",
        {
            "fields": {
                "title": "Native effects",
                "plan_id": "PLAN-1",
                "phase_order": 10,
                "gate_criteria": "Observable result",
                "test_ids": ["TEST-1"],
            }
        },
    ),
    ("projects", "PROGRAM-1", {"kind": "program", "fields": {"name": "Coherent platform"}}),
    (
        "projects",
        "PROJECT-1",
        {
            "fields": {
                "name": "Complete outcome",
                "parent_project_id": "PROGRAM-1",
                "target_outcome": "Complete native authority",
                "repository_ref": "platform",
            }
        },
    ),
    (
        "work-items",
        "WI-TEST-0001",
        {
            "project_id": "PROJECT-1",
            "fields": {
                "title": "Seeded work item",
                "description": "Initial description.",
                "source_spec_id": "SPEC-1",
                "source_test_id": "TEST-1",
                "priority": "P2",
            },
        },
    ),
)


def _seed(client) -> None:
    for domain, record_id, body in SEED:
        client.request(
            "PUT",
            f"/v1/{domain}/{record_id}",
            body={"expected_version": 0, "actor": "qualification", "reason": "Initial seed", **body},
        )
    client.request(
        "PUT",
        "/v1/work-items/WI-TEST-0001",
        body={
            "expected_version": 1,
            "actor": "tester",
            "reason": "Second version",
            "fields": {"description": "Updated work item description.", "priority": "P1"},
        },
    )


def test_backlog_show_emits_work_item_record(native_application) -> None:
    _seed(native_application.client)
    result = native_application.invoke("backlog", "show", "WI-TEST-0001")
    assert result.exit_code == 0, result.output
    assert "WI-TEST-0001 v2: Seeded work item" in result.output
    assert "Updated work item description." in result.output


def test_backlog_show_json_flag_emits_dict(native_application) -> None:
    _seed(native_application.client)
    result = native_application.invoke("backlog", "show", "WI-TEST-0001", "--json")
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["work_item"]["id"] == "WI-TEST-0001" and payload["work_item"]["version"] == 2
    assert payload["work_item"]["priority"] == "P1"


def test_backlog_show_with_history_includes_version_chain(native_application) -> None:
    _seed(native_application.client)
    result = native_application.invoke("backlog", "show", "WI-TEST-0001", "--history")
    assert result.exit_code == 0, result.output
    assert "Version History:" in result.output
    assert "v1" in result.output and "Initial seed" in result.output
    assert "v2" in result.output and "Second version" in result.output
    assert result.output.index("v1 ") < result.output.index("v2 ")


def test_backlog_show_missing_id_is_a_usage_error(native_application) -> None:
    result = native_application.invoke("backlog", "show")
    assert result.exit_code == 2
    assert "Missing argument" in result.output


def test_backlog_show_unknown_id_exits_nonzero(native_application) -> None:
    _seed(native_application.client)
    result = native_application.invoke("backlog", "show", "WI-9999", "--json")
    assert result.exit_code == 1, result.output
    assert "Error: not_found:" in result.output


def test_backlog_show_json_with_history_emits_current_and_history(native_application) -> None:
    _seed(native_application.client)
    result = native_application.invoke("backlog", "show", "WI-TEST-0001", "--history", "--json")
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert set(payload) == {"current", "history"}
    assert payload["current"]["version"] == 2
    assert [entry["version"] for entry in payload["history"]] == [1, 2]
    assert [entry["reason"] for entry in payload["history"]] == ["Initial seed", "Second version"]
    assert payload["history"][0]["state"]["description"] == "Initial description."
    assert payload["history"][1]["state"]["description"] == "Updated work item description."
    assert payload["history"][0]["prior_version"] is None and payload["history"][1]["prior_version"] == 1


def test_history_of_a_missing_record_is_not_found(native_application) -> None:
    from groundtruth_kb.authority_client import AuthorityClientError

    with pytest.raises(AuthorityClientError) as refused:
        native_application.client.request("GET", "/v1/specifications/SPEC-MISSING/history")
    assert refused.value.code == "not_found"
