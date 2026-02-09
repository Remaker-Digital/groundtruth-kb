"""Tests for the schema migration framework.

Validates migration discovery, tracking, forward-only application, and
idempotent baseline migration.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.migrations.apply import (
    ApplyResults,
    MigrationRecord,
    MigrationResult,
    MigrationRunner,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


class MockMigrationContainer:
    """In-memory mock for the _migrations Cosmos DB container."""

    def __init__(self) -> None:
        self._items: dict[str, dict] = {}

    async def read(self) -> dict:
        return {"id": "_migrations"}

    async def upsert_item(self, item: dict) -> dict:
        self._items[item["id"]] = item
        return item

    def query_items(self, query: str, **kwargs: Any) -> "MockAsyncIterator":
        items = list(self._items.values())
        # Simulate WHERE c.success = true filter
        if "success = true" in query.lower():
            items = [i for i in items if i.get("success") is True]
        return MockAsyncIterator(items)


class MockAsyncIterator:
    """Async iterator over a list of dicts."""

    def __init__(self, items: list[dict]) -> None:
        self._items = items
        self._idx = 0

    def __aiter__(self) -> "MockAsyncIterator":
        return self

    async def __anext__(self) -> dict:
        if self._idx >= len(self._items):
            raise StopAsyncIteration
        item = self._items[self._idx]
        self._idx += 1
        return item


class MockCosmosManager:
    """Mock CosmosManager for migration tests."""

    def __init__(self) -> None:
        self._database_name = "agentred"
        self._container = MockMigrationContainer()
        self._database = MagicMock()
        self._database.get_container_client.return_value = self._container
        self._database.create_container_if_not_exists = AsyncMock()
        self._client = MagicMock()
        self._client.get_database_client.return_value = self._database


@pytest.fixture
def cosmos() -> MockCosmosManager:
    return MockCosmosManager()


@pytest.fixture
def runner(cosmos: MockCosmosManager) -> MigrationRunner:
    return MigrationRunner(cosmos)


# ---------------------------------------------------------------------------
# Data class tests
# ---------------------------------------------------------------------------


class TestDataClasses:
    """Test migration data structures."""

    def test_migration_record_fields(self) -> None:
        record = MigrationRecord(
            version="001",
            description="Add widget_theme",
            applied_at="2026-02-08T12:00:00Z",
        )
        assert record.version == "001"
        assert record.success is True
        assert record.applied_by == "migration-runner"
        assert record.error is None

    def test_migration_result_fields(self) -> None:
        result = MigrationResult(
            version="001",
            description="test",
            success=True,
            duration_ms=42.5,
        )
        assert result.success
        assert result.duration_ms == 42.5
        assert result.error is None

    def test_migration_result_failure(self) -> None:
        result = MigrationResult(
            version="001",
            description="test",
            success=False,
            duration_ms=100.0,
            error="Connection refused",
        )
        assert not result.success
        assert result.error == "Connection refused"

    def test_apply_results_empty(self) -> None:
        results = ApplyResults()
        assert results.total == 0
        assert not results.all_succeeded  # No applied = not all_succeeded

    def test_apply_results_all_success(self) -> None:
        results = ApplyResults()
        results.applied.append(
            MigrationResult("001", "test", True, 10.0)
        )
        assert results.total == 1
        assert results.all_succeeded

    def test_apply_results_with_failure(self) -> None:
        results = ApplyResults()
        results.applied.append(
            MigrationResult("001", "test", True, 10.0)
        )
        results.failed.append(
            MigrationResult("002", "test", False, 5.0, "error")
        )
        assert results.total == 2
        assert not results.all_succeeded


# ---------------------------------------------------------------------------
# Discovery tests
# ---------------------------------------------------------------------------


class TestMigrationDiscovery:
    """Test migration module discovery."""

    def test_discovers_baseline_migration(self, runner: MigrationRunner) -> None:
        """Should find the 000_baseline migration."""
        migrations = runner._discover_migrations()
        versions = [m.VERSION for m in migrations]
        assert "000" in versions

    def test_baseline_has_required_attributes(self, runner: MigrationRunner) -> None:
        """Baseline migration must have VERSION, DESCRIPTION, up()."""
        migrations = runner._discover_migrations()
        baseline = [m for m in migrations if m.VERSION == "000"][0]
        assert baseline.DESCRIPTION.startswith("Baseline")
        assert callable(baseline.up)

    def test_migrations_sorted_by_version(self, runner: MigrationRunner) -> None:
        """Discovered migrations should be sorted by VERSION."""
        migrations = runner._discover_migrations()
        versions = [m.VERSION for m in migrations]
        assert versions == sorted(versions)


# ---------------------------------------------------------------------------
# Applied version tracking tests
# ---------------------------------------------------------------------------


class TestAppliedVersions:
    """Test tracking of applied migrations."""

    async def test_no_applied_versions_initially(
        self, runner: MigrationRunner
    ) -> None:
        applied = await runner._get_applied_versions()
        assert applied == set()

    async def test_records_applied_version(
        self, runner: MigrationRunner, cosmos: MockCosmosManager
    ) -> None:
        """After applying, version should appear in applied set."""
        # Manually add a record
        container = await runner._ensure_container()
        await container.upsert_item(
            {"id": "migration-000", "version": "000", "success": True}
        )

        applied = await runner._get_applied_versions()
        assert "000" in applied

    async def test_failed_migrations_not_in_applied(
        self, runner: MigrationRunner, cosmos: MockCosmosManager
    ) -> None:
        """Failed migrations should not count as applied."""
        container = await runner._ensure_container()
        await container.upsert_item(
            {"id": "migration-001", "version": "001", "success": False}
        )

        applied = await runner._get_applied_versions()
        assert "001" not in applied


# ---------------------------------------------------------------------------
# Check pending tests
# ---------------------------------------------------------------------------


class TestCheckPending:
    """Test pending migration detection."""

    async def test_baseline_is_pending_initially(
        self, runner: MigrationRunner
    ) -> None:
        pending = await runner.check_pending()
        versions = [m.VERSION for m in pending]
        assert "000" in versions

    async def test_no_pending_after_baseline_applied(
        self, runner: MigrationRunner
    ) -> None:
        """After marking baseline as applied, no pending migrations."""
        container = await runner._ensure_container()
        await container.upsert_item(
            {"id": "migration-000", "version": "000", "success": True}
        )

        pending = await runner.check_pending()
        assert len(pending) == 0


# ---------------------------------------------------------------------------
# Apply tests
# ---------------------------------------------------------------------------


class TestApplyAll:
    """Test migration application."""

    async def test_apply_baseline(self, runner: MigrationRunner) -> None:
        """Applying baseline should succeed (it's a no-op)."""
        results = await runner.apply_all()

        assert results.total >= 1
        assert results.all_succeeded
        baseline_result = [r for r in results.applied if r.version == "000"]
        assert len(baseline_result) == 1
        assert baseline_result[0].success

    async def test_apply_is_idempotent(self, runner: MigrationRunner) -> None:
        """Running apply_all twice should be safe — second run finds 0 pending."""
        results1 = await runner.apply_all()
        assert results1.total >= 1

        results2 = await runner.apply_all()
        assert results2.total == 0  # Nothing pending

    async def test_applied_migration_recorded_in_container(
        self, runner: MigrationRunner, cosmos: MockCosmosManager
    ) -> None:
        """Applied migrations should be recorded in the _migrations container."""
        await runner.apply_all()

        applied = await runner._get_applied_versions()
        assert "000" in applied


# ---------------------------------------------------------------------------
# Baseline migration tests
# ---------------------------------------------------------------------------


class TestBaselineMigration:
    """Test the 000_baseline migration module directly."""

    async def test_baseline_up_is_noop(self, cosmos: MockCosmosManager) -> None:
        """Baseline migration's up() should complete without error."""
        from src.migrations import _000_baseline as baseline  # noqa: N812

        # Should not raise
        await baseline.up(cosmos)

    def test_baseline_version(self) -> None:
        from src.migrations import _000_baseline as baseline  # noqa: N812

        assert baseline.VERSION == "000"

    def test_baseline_description(self) -> None:
        from src.migrations import _000_baseline as baseline  # noqa: N812

        assert "Baseline" in baseline.DESCRIPTION
        assert "1.0.0" in baseline.DESCRIPTION
