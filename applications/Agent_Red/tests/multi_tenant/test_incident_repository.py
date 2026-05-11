"""Tests for IncidentRepository — CRUD operations on the incidents collection.

Covers:
    - create_incident: happy path, default severity, custom fields
    - get_incident: found, not found
    - find_incident: cross-partition search, not found
    - list_active: multiple statuses, empty
    - list_all: cross-partition listing, limit
    - add_update: same partition (patch), status change (delete+recreate)
    - resolve_incident: delegates to add_update with resolved status

Total: 18 tests

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.cosmos_schema import IncidentSeverity, IncidentStatus


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class FakeAsyncIterator:
    """Async iterator for mocking Cosmos query results."""

    def __init__(self, items: list[dict[str, Any]]) -> None:
        self._items = items
        self._index = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._index >= len(self._items):
            raise StopAsyncIteration
        item = self._items[self._index]
        self._index += 1
        return item


def make_incident(
    incident_id: str = "inc-abc123",
    title: str = "API outage",
    description: str = "API is down",
    status: str = "investigating",
    severity: str = "major",
    affected_services: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "id": incident_id,
        "incident_id": incident_id,
        "title": title,
        "description": description,
        "status": status,
        "severity": severity,
        "affected_services": affected_services or ["API"],
        "updates": [],
        "created_at": "2026-02-18T10:00:00+00:00",
        "updated_at": "2026-02-18T10:00:00+00:00",
        "resolved_at": None,
        "created_by": "admin",
    }


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_container():
    container = MagicMock()
    container.create_item = AsyncMock()
    container.read_item = AsyncMock()
    container.delete_item = AsyncMock()
    container.patch_item = AsyncMock()
    container.query_items = MagicMock(return_value=FakeAsyncIterator([]))
    return container


@pytest.fixture()
def repo(mock_container):
    with patch("src.multi_tenant.repositories.incidents.get_cosmos_manager") as mock_mgr:
        mock_mgr.return_value.get_container.return_value = mock_container
        from src.multi_tenant.repositories.incidents import IncidentRepository

        r = IncidentRepository()
        # Override the _container property for direct access
        r._mock_container = mock_container
        type(r)._container = property(lambda self: self._mock_container)
        yield r


# ---------------------------------------------------------------------------
# create_incident
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_incident_happy_path(repo, mock_container):
    """Create an incident with all fields."""
    mock_container.create_item = AsyncMock(
        side_effect=lambda body: body,
    )
    result = await repo.create_incident(
        title="DB outage",
        description="Database is unreachable",
        severity=IncidentSeverity.CRITICAL.value,
        affected_services=["Cosmos DB"],
        created_by="ops@test.com",
    )
    assert result["title"] == "DB outage"
    assert result["severity"] == "critical"
    assert result["status"] == "investigating"
    assert "Cosmos DB" in result["affected_services"]
    assert len(result["updates"]) == 1
    assert result["created_by"] == "ops@test.com"
    assert result["incident_id"].startswith("inc-")


@pytest.mark.asyncio
async def test_create_incident_defaults(repo, mock_container):
    """Default severity is minor, empty services list."""
    mock_container.create_item = AsyncMock(side_effect=lambda body: body)
    result = await repo.create_incident(
        title="Minor issue",
        description="Something minor",
    )
    assert result["severity"] == "minor"
    assert result["affected_services"] == []
    assert result["created_by"] == "system"


# ---------------------------------------------------------------------------
# get_incident
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_incident_found(repo, mock_container):
    doc = make_incident()
    mock_container.read_item = AsyncMock(return_value=doc)
    result = await repo.get_incident("inc-abc123", "investigating")
    assert result is not None
    assert result["incident_id"] == "inc-abc123"
    mock_container.read_item.assert_awaited_once_with(
        item="inc-abc123",
        partition_key="investigating",
    )


@pytest.mark.asyncio
async def test_get_incident_not_found(repo, mock_container):
    from azure.cosmos.exceptions import CosmosResourceNotFoundError

    mock_container.read_item = AsyncMock(
        side_effect=CosmosResourceNotFoundError(status_code=404, message="Not found"),
    )
    result = await repo.get_incident("inc-missing", "investigating")
    assert result is None


# ---------------------------------------------------------------------------
# find_incident (cross-partition)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_find_incident_found(repo, mock_container):
    doc = make_incident(status="identified")
    mock_container.query_items = MagicMock(return_value=FakeAsyncIterator([doc]))
    result = await repo.find_incident("inc-abc123")
    assert result is not None
    assert result["status"] == "identified"


@pytest.mark.asyncio
async def test_find_incident_not_found(repo, mock_container):
    mock_container.query_items = MagicMock(return_value=FakeAsyncIterator([]))
    result = await repo.find_incident("inc-missing")
    assert result is None


# ---------------------------------------------------------------------------
# list_active
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_active_multiple_statuses(repo, mock_container):
    """list_active queries 3 partitions: investigating, identified, monitoring."""
    call_count = 0
    items_by_status = {
        "investigating": [make_incident(incident_id="inc-1", status="investigating")],
        "identified": [make_incident(incident_id="inc-2", status="identified")],
        "monitoring": [],
    }

    def side_effect(**kwargs):
        nonlocal call_count
        pk = kwargs.get("partition_key", "")
        call_count += 1
        return FakeAsyncIterator(items_by_status.get(pk, []))

    mock_container.query_items = MagicMock(side_effect=side_effect)
    result = await repo.list_active()
    assert len(result) == 2
    assert call_count == 3  # queried all 3 partitions


@pytest.mark.asyncio
async def test_list_active_empty(repo, mock_container):
    mock_container.query_items = MagicMock(return_value=FakeAsyncIterator([]))
    result = await repo.list_active()
    assert result == []


# ---------------------------------------------------------------------------
# list_all
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_all(repo, mock_container):
    docs = [make_incident(incident_id=f"inc-{i}") for i in range(3)]
    mock_container.query_items = MagicMock(return_value=FakeAsyncIterator(docs))
    result = await repo.list_all(limit=50)
    assert len(result) == 3


@pytest.mark.asyncio
async def test_list_all_empty(repo, mock_container):
    mock_container.query_items = MagicMock(return_value=FakeAsyncIterator([]))
    result = await repo.list_all()
    assert result == []


# ---------------------------------------------------------------------------
# add_update — same partition
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_add_update_same_partition(repo, mock_container):
    """Adding an update within the same status patches in place."""
    doc = make_incident(status="investigating")
    mock_container.read_item = AsyncMock(return_value=doc)
    mock_container.patch_item = AsyncMock()

    result = await repo.add_update(
        incident_id="inc-abc123",
        current_status="investigating",
        new_status="investigating",
        message="Still looking into it",
        author="ops@test.com",
    )
    assert result is not None
    assert len(result["updates"]) == 1  # original empty + appended
    mock_container.patch_item.assert_awaited_once()
    mock_container.delete_item.assert_not_awaited()


# ---------------------------------------------------------------------------
# add_update — status change (delete + recreate)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_add_update_status_change(repo, mock_container):
    """Changing status deletes old doc and recreates in new partition."""
    doc = make_incident(status="investigating")
    mock_container.read_item = AsyncMock(return_value=doc)
    mock_container.delete_item = AsyncMock()
    mock_container.create_item = AsyncMock(side_effect=lambda body: body)

    result = await repo.add_update(
        incident_id="inc-abc123",
        current_status="investigating",
        new_status="identified",
        message="Root cause found",
        author="ops@test.com",
    )
    assert result is not None
    assert result["status"] == "identified"
    mock_container.delete_item.assert_awaited_once()
    mock_container.create_item.assert_awaited_once()


@pytest.mark.asyncio
async def test_add_update_incident_not_found(repo, mock_container):
    from azure.cosmos.exceptions import CosmosResourceNotFoundError

    mock_container.read_item = AsyncMock(
        side_effect=CosmosResourceNotFoundError(status_code=404, message=""),
    )
    result = await repo.add_update(
        incident_id="inc-missing",
        current_status="investigating",
        new_status="identified",
        message="nope",
    )
    assert result is None


# ---------------------------------------------------------------------------
# resolve_incident
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_resolve_incident(repo, mock_container):
    """resolve_incident delegates to add_update with 'resolved' status."""
    doc = make_incident(status="monitoring")
    mock_container.read_item = AsyncMock(return_value=doc)
    mock_container.delete_item = AsyncMock()
    mock_container.create_item = AsyncMock(side_effect=lambda body: body)

    result = await repo.resolve_incident(
        incident_id="inc-abc123",
        current_status="monitoring",
        message="All clear",
        author="ops@test.com",
    )
    assert result is not None
    assert result["status"] == IncidentStatus.RESOLVED.value
    assert result["resolved_at"] is not None


@pytest.mark.asyncio
async def test_resolve_incident_sets_resolved_at(repo, mock_container):
    """Resolved timestamp is set when resolving."""
    doc = make_incident(status="identified")
    mock_container.read_item = AsyncMock(return_value=doc)
    mock_container.delete_item = AsyncMock()
    mock_container.create_item = AsyncMock(side_effect=lambda body: body)

    result = await repo.resolve_incident(
        incident_id="inc-abc123",
        current_status="identified",
    )
    assert result["resolved_at"] is not None
    assert result["status"] == "resolved"
