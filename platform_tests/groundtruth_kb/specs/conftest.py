"""Read-only formal fitness tests against an explicitly selected native authority.

GTKB_FORMAL_TEST_AUTHORITY_URL is required for tests using ``formal_record``.
These tests never select a database from the working directory, import a legacy
SQLite fixture, write canonical records or fall back when the service fails.
Behavioral qualification uses separate disposable-authority native tests.
Reads require active status by default. Retirement checks may explicitly name
the expected retired or superseded status without treating that record as active.
"""

from __future__ import annotations

import os

import pytest
from groundtruth_kb.authority_client import AuthorityClient
from groundtruth_kb.postgres_kernel import canonical_json_bytes


@pytest.fixture(scope="session")
def formal_record():
    url = os.environ.get("GTKB_FORMAL_TEST_AUTHORITY_URL")
    if not url:
        pytest.fail("Set GTKB_FORMAL_TEST_AUTHORITY_URL explicitly for current formal-corpus tests")
    client = AuthorityClient(url)
    observed = {}

    def read(identifier, *, expected_status="active"):
        row = client.request("GET", f"/v1/specifications/{identifier}")
        assert row["id"] == identifier
        assert row["status"] == expected_status, f"{identifier} is not {expected_status}"
        image = canonical_json_bytes(row)
        assert observed.setdefault(identifier, image) == image, f"{identifier} changed during qualification"
        return row

    yield read

    for identifier, image in observed.items():
        current = client.request("GET", f"/v1/specifications/{identifier}")
        assert canonical_json_bytes(current) == image, f"{identifier} changed during qualification"
