"""Historical deliberation records are readable through the native authority and never amended by it.

Carries the retained retrieval duty of the retired SQLite `gt deliberations` command family (O-7 R20,
SPEC-2098 v2): structured listing with filters and title search, exact readback by ID, pagination, and the
absence of any write route. Redaction of stored content belongs to the historical data and its library tests.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest

from groundtruth_kb.authority_client import AuthorityClientError
from groundtruth_kb.postgres_kernel import TABLE_SPECS

pytestmark = [pytest.mark.integration, pytest.mark.timeout(300)]


def _seed(client, service, rows: list[dict]) -> None:
    client.request(
        "PUT",
        "/v1/specifications/SPEC-1",
        body={
            "expected_version": 0,
            "actor": "qualification",
            "reason": "Linked specification fixture",
            "fields": {"title": "Linked specification", "description": "Fixture", "type": "requirement"},
        },
    )
    columns = TABLE_SPECS["deliberations"].columns
    for row in rows:
        state = {column: None for column in columns}
        state.update(row)
        state.update(
            version=0,
            changed_by="qualification",
            changed_at=datetime.now(UTC).isoformat(),
            change_reason="Historical record fixture",
        )
        service.kernel.mutate_current(
            table="deliberations",
            identity={"id": row["id"]},
            expected_version=0,
            new_state=state,
            actor="qualification",
            reason="Historical record fixture",
        )


ROWS = [
    {
        "id": "DELIB-0001",
        "source_type": "session",
        "source_ref": "S1",
        "title": "Alpha routing decision",
        "summary": "Route A",
        "content": "Reasoning about A",
        "outcome": "decided",
        "redaction_state": "clean",
    },
    {
        "id": "DELIB-0002",
        "source_type": "bridge",
        "source_ref": "B1",
        "title": "Beta review",
        "summary": "Review B",
        "content": "Reasoning about B",
        "outcome": "open",
        "redaction_state": "clean",
        "spec_id": "SPEC-1",
    },
    {
        "id": "DELIB-0003",
        "source_type": "session",
        "source_ref": "S2",
        "title": "Gamma alpha follow-up",
        "summary": "Follow-up",
        "content": "More reasoning",
        "outcome": "decided",
        "redaction_state": "redacted",
    },
]


def test_records_list_filter_search_and_read_back(native_app_authority) -> None:
    client, service = native_app_authority["client"], native_app_authority["service"]
    _seed(client, service, ROWS)
    listed = client.request("GET", "/v1/deliberations", query={"limit": 10})
    assert [row["id"] for row in listed["records"]] == ["DELIB-0001", "DELIB-0002", "DELIB-0003"] and listed[
        "next_after"
    ] is None
    assert all(row["version"] == 1 for row in listed["records"])
    page = client.request("GET", "/v1/deliberations", query={"limit": 2})
    assert [row["id"] for row in page["records"]] == ["DELIB-0001", "DELIB-0002"] and page["next_after"] == "DELIB-0002"
    rest = client.request("GET", "/v1/deliberations", query={"limit": 2, "after": "DELIB-0002"})
    assert [row["id"] for row in rest["records"]] == ["DELIB-0003"]
    sessions = client.request("GET", "/v1/deliberations", query={"source_type": "session"})
    assert [row["id"] for row in sessions["records"]] == ["DELIB-0001", "DELIB-0003"]
    linked = client.request("GET", "/v1/deliberations", query={"spec_id": "SPEC-1"})
    assert [row["id"] for row in linked["records"]] == ["DELIB-0002"]
    found = client.request("GET", "/v1/deliberations", query={"search": "alpha"})
    assert [row["id"] for row in found["records"]] == ["DELIB-0001", "DELIB-0003"]
    shown = client.request("GET", "/v1/deliberations/DELIB-0003")
    assert (
        shown["title"] == "Gamma alpha follow-up"
        and shown["redaction_state"] == "redacted"
        and shown["content"] == "More reasoning"
    )
    with pytest.raises(AuthorityClientError) as missing:
        client.request("GET", "/v1/deliberations/DELIB-9999")
    assert missing.value.code == "not_found"


def test_the_native_service_offers_no_write_route(native_app_authority) -> None:
    client, service = native_app_authority["client"], native_app_authority["service"]
    _seed(client, service, ROWS[:1])
    body = {"expected_version": 1, "actor": "x", "reason": "y", "fields": {"title": "changed", "padding": "x" * 65536}}
    with pytest.raises(AuthorityClientError) as refused:
        client.request("PUT", "/v1/deliberations/DELIB-0001", body=body)
    # A typed refusal, delivered after the body is read: never a framework 405 that can arrive as a reset.
    assert refused.value.code == "read_only_domain" and refused.value.details == {
        "domain": "deliberations",
        "id": "DELIB-0001",
    }
    assert client.request("GET", "/v1/deliberations/DELIB-0001")["title"] == "Alpha routing decision"


def test_cli_lists_and_shows_historical_records_read_only(native_application) -> None:
    _seed(native_application.client, native_application.item["service"], ROWS)
    result = native_application.invoke("deliberations", "list", "--search", "alpha", "--json")
    assert result.exit_code == 0, result.output
    assert [row["id"] for row in json.loads(result.output)] == ["DELIB-0001", "DELIB-0003"]
    result = native_application.invoke("deliberations", "list", "--source-type", "bridge", "--json")
    assert result.exit_code == 0, result.output
    assert [row["id"] for row in json.loads(result.output)] == ["DELIB-0002"]
    result = native_application.invoke("deliberations", "show", "DELIB-0002", "--json")
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["summary"] == "Review B"
    assert native_application.invoke("deliberations", "record", "--id", "DELIB-0002").exit_code != 0
    human = native_application.invoke("deliberations", "show", "DELIB-0001")
    assert human.exit_code == 0 and "Alpha routing decision" in human.output
