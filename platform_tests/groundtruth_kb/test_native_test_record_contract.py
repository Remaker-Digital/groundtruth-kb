"""Execution results are observed facts: the native TEST writer accepts none from a client."""

from __future__ import annotations

import pytest

from platform_tests.groundtruth_kb.native_fixtures import history_count, put, seed
from platform_tests.groundtruth_kb.native_fixtures import native as native


@pytest.mark.parametrize(
    "supplied",
    [
        {"last_result": "pass"},
        {"last_executed_at": "2026-09-16T00:00:00+00:00"},
        {"last_executed_on": "2026-09-16"},
        {"last_result": "pass", "last_executed_at": "2026-09-16T00:00:00+00:00"},
    ],
)
def test_client_supplied_execution_results_are_refused_without_a_write(native, supplied):
    """A test record's pass/fail is never written through the amendment API, so no gate configuration is needed to
    keep an unexecuted or file-less test from reading as passed."""
    service, client, _, _ = native
    seed(client)
    before = client.get("/v1/tests/TEST-1").json()
    history = history_count(service)
    response = put(client, "tests", "TEST-1", {"title": "Effect test", **supplied}, expected_version=before["version"])
    assert response.status_code == 422, response.text
    assert response.json()["code"] == "invalid_request"
    assert {tuple(item["location"]): item["type"] for item in response.json()["fields"]} == {
        ("body", "fields", field): "extra_forbidden" for field in supplied
    }
    assert client.get("/v1/tests/TEST-1").json() == before
    assert history_count(service) == history


NEW_FIELDS = {
    "title": "New test",
    "spec_id": "SPEC-1",
    "test_type": "integration",
    "test_file": "tests/test_new_effect.py",
    "expected_outcome": "New effect observed",
}


def test_creating_a_test_record_cannot_carry_an_execution_result(native):
    service, client, _, _ = native
    seed(client)
    history = history_count(service)
    response = put(client, "tests", "TEST-NEW", {**NEW_FIELDS, "last_result": "pass"})
    assert response.status_code == 422, response.text
    assert client.get("/v1/tests/TEST-NEW").status_code == 404
    assert history_count(service) == history
    created = put(client, "tests", "TEST-NEW", NEW_FIELDS)
    assert created.status_code == 200, created.text
    record = client.get("/v1/tests/TEST-NEW").json()
    assert record["last_result"] is None and record["last_executed_at"] is None and record["last_executed_on"] is None
