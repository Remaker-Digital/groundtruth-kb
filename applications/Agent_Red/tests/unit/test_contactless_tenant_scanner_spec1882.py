"""SPEC-1882 coverage for contactless active tenant deactivation."""

from __future__ import annotations

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from src.app.background import (
    _CONTACTLESS_TENANT_SCAN_INTERVAL,
    _CONTACTLESS_TENANT_SCAN_STARTUP_DELAY,
    _contactless_tenant_scanner_loop,
    _shutdown_contactless_tenant_scanner,
    _startup_contactless_tenant_scanner,
    register_contactless_tenant_scanner,
    register_expiry_scanner,
)
from src.multi_tenant.repositories.tenant import TenantRepository


_REPO_PATCH = "src.multi_tenant.repository.TenantRepository"


def _contactless_tenant(tenant_id: str = "t-contactless") -> dict:
    return {
        "id": tenant_id,
        "tenant_id": tenant_id,
        "status": "active",
        "customer_email": "",
        "customer_phone": None,
    }


@pytest.mark.asyncio
async def test_contactless_scanner_deactivates_active_tenant_without_contact():
    mock_repo = AsyncMock()
    mock_repo.list_active_contactless_tenants.return_value = [_contactless_tenant()]
    mock_repo.patch.return_value = {}

    with (
        patch(_REPO_PATCH, return_value=mock_repo),
        patch("src.app.background.asyncio.sleep", side_effect=[None, asyncio.CancelledError]),
    ):
        with pytest.raises(asyncio.CancelledError):
            await _contactless_tenant_scanner_loop()

    mock_repo.list_active_contactless_tenants.assert_awaited_once()
    mock_repo.patch.assert_awaited_once()
    call_kwargs = mock_repo.patch.call_args.kwargs
    assert call_kwargs["tenant_id"] == "t-contactless"
    assert call_kwargs["document_id"] == "t-contactless"

    ops = call_kwargs["operations"]
    ops_by_path = {op["path"]: op["value"] for op in ops}
    assert ops_by_path["/status"] == "deactivated"
    assert ops_by_path["/deactivation_reason"] == "missing_superadmin_contact"
    assert datetime.fromisoformat(ops_by_path["/updated_at"]).tzinfo is not None
    assert datetime.fromisoformat(ops_by_path["/deactivated_at"]).tzinfo is not None


@pytest.mark.asyncio
async def test_contactless_scanner_skips_missing_tenant_id_and_continues_after_patch_failure():
    mock_repo = AsyncMock()
    mock_repo.list_active_contactless_tenants.return_value = [
        {"status": "active"},
        _contactless_tenant("t-fail"),
        _contactless_tenant("t-ok"),
    ]
    mock_repo.patch.side_effect = [RuntimeError("Cosmos throttled"), {}]

    with (
        patch(_REPO_PATCH, return_value=mock_repo),
        patch("src.app.background.asyncio.sleep", side_effect=[None, asyncio.CancelledError]),
    ):
        with pytest.raises(asyncio.CancelledError):
            await _contactless_tenant_scanner_loop()

    assert mock_repo.patch.await_count == 2
    patched_ids = [call.kwargs["tenant_id"] for call in mock_repo.patch.call_args_list]
    assert patched_ids == ["t-fail", "t-ok"]


@pytest.mark.asyncio
async def test_contactless_scanner_cycle_failure_does_not_crash():
    mock_repo = AsyncMock()
    mock_repo.list_active_contactless_tenants.side_effect = [
        RuntimeError("Cosmos unavailable"),
        [],
    ]

    call_count = 0

    async def controlled_sleep(seconds):
        nonlocal call_count
        call_count += 1
        if call_count >= 3:
            raise asyncio.CancelledError

    with (
        patch(_REPO_PATCH, return_value=mock_repo),
        patch("src.app.background.asyncio.sleep", side_effect=controlled_sleep),
    ):
        with pytest.raises(asyncio.CancelledError):
            await _contactless_tenant_scanner_loop()

    assert mock_repo.list_active_contactless_tenants.await_count == 2


def test_contactless_scanner_registration_collects_handlers():
    from src.app.background import _bg_shutdown_handlers, _bg_startup_handlers

    startup_before = len(_bg_startup_handlers)
    shutdown_before = len(_bg_shutdown_handlers)

    register_contactless_tenant_scanner()

    assert len(_bg_startup_handlers) == startup_before + 1
    assert len(_bg_shutdown_handlers) == shutdown_before + 1
    assert _bg_startup_handlers[-1] is _startup_contactless_tenant_scanner
    assert _bg_shutdown_handlers[-1] is _shutdown_contactless_tenant_scanner


def test_expiry_scanner_registration_also_registers_contactless_scanner():
    from src.app.background import _bg_shutdown_handlers, _bg_startup_handlers

    startup_before = len(_bg_startup_handlers)
    shutdown_before = len(_bg_shutdown_handlers)

    register_expiry_scanner()

    assert len(_bg_startup_handlers) == startup_before + 2
    assert len(_bg_shutdown_handlers) == shutdown_before + 2
    assert _startup_contactless_tenant_scanner in _bg_startup_handlers[-2:]
    assert _shutdown_contactless_tenant_scanner in _bg_shutdown_handlers[-2:]


def test_contactless_scanner_timing_constants():
    assert _CONTACTLESS_TENANT_SCAN_INTERVAL == 3600
    assert _CONTACTLESS_TENANT_SCAN_STARTUP_DELAY == 165


def test_repository_contactless_query_matches_missing_null_empty_active_contacts():
    query_calls: list[str] = []

    class FakeContainer:
        async def query_items(self, query: str, **kwargs):
            query_calls.append(query)
            if False:
                yield {}

    class FakeManager:
        def get_container(self, collection_name: str) -> FakeContainer:
            return FakeContainer()

    async def run_query() -> list[dict]:
        with patch("src.multi_tenant.repositories.base.get_cosmos_manager", return_value=FakeManager()):
            repo = TenantRepository()
            return await repo.list_active_contactless_tenants()

    assert asyncio.run(run_query()) == []
    query = query_calls[0]
    assert "c.status = 'active'" in query
    assert "NOT IS_DEFINED(c.customer_email)" in query
    assert "IS_NULL(c.customer_email)" in query
    assert "c.customer_email = ''" in query
    assert "NOT IS_DEFINED(c.customer_phone)" in query
    assert "IS_NULL(c.customer_phone)" in query
    assert "c.customer_phone = ''" in query
