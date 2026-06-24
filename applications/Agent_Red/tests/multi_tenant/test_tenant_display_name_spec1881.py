"""SPEC-1881 tenant display-name production-path coverage."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from src.integrations import provisioning
from src.integrations.provisioning import _generate_display_name
from src.multi_tenant.superadmin_api import configure_superadmin_services
from src.multi_tenant.superadmin_api._tenants import (
    DisplayNameUpdateRequest,
    list_all_tenants,
    update_tenant_display_name,
)


class _AsyncItems:
    def __init__(self, items: list[Any]) -> None:
        self._items = items

    def __aiter__(self):
        self._iter = iter(self._items)
        return self

    async def __anext__(self):
        try:
            return next(self._iter)
        except StopIteration:
            raise StopAsyncIteration from None


class _TenantListContainer:
    def __init__(self) -> None:
        self.queries: list[str] = []
        self._calls = 0

    def query_items(self, **kwargs):
        self._calls += 1
        query = kwargs["query"]
        self.queries.append(query)
        if self._calls == 1:
            return _AsyncItems([1])
        return _AsyncItems(
            [
                {
                    "tenant_id": "tenant-001",
                    "display_name": "Merchant Friendly Name",
                    "status": "active",
                    "tier": "professional",
                    "billing_channel": "manual",
                    "customer_email": "owner@example.com",
                    "shopify_shop_domain": "merchant.myshopify.com",
                    "created_at": "2026-01-01T00:00:00Z",
                    "updated_at": "2026-01-02T00:00:00Z",
                    "deactivated_at": None,
                    "consent_status": "granted",
                    "expires_at": None,
                }
            ]
        )


class _DisplayNameRepo:
    def __init__(self, duplicates: list[dict[str, str]] | None = None) -> None:
        self._container = MagicMock()
        self._container.query_items = MagicMock(return_value=_AsyncItems(duplicates or []))
        self.read = AsyncMock(
            return_value={
                "tenant_id": "tenant-001",
                "display_name": "Old Tenant Name",
            }
        )
        self.patch = AsyncMock(return_value={})


@pytest.fixture(autouse=True)
def _reset_superadmin_services():
    configure_superadmin_services(tenant_repo=MagicMock(), audit_repo=MagicMock())
    yield
    configure_superadmin_services(tenant_repo=MagicMock(), audit_repo=MagicMock())


@pytest.mark.asyncio
async def test_generate_display_name_increments_when_first_candidate_exists(monkeypatch) -> None:
    class ExistingDisplayNameRepo:
        async def cross_partition_query(self, *, query_text: str, parameters: list[dict[str, str]]):
            assert "c.display_name = @name" in query_text
            candidate = parameters[0]["value"]
            if candidate == "merchant@example.com-001":
                return [{"id": "existing-tenant"}]
            return []

    monkeypatch.setattr(provisioning, "_tenant_repo", ExistingDisplayNameRepo())

    assert await _generate_display_name("merchant@example.com") == "merchant@example.com-002"


@pytest.mark.asyncio
async def test_list_all_tenants_selects_and_returns_display_name() -> None:
    tenant_repo = MagicMock()
    tenant_repo._container = _TenantListContainer()
    configure_superadmin_services(tenant_repo=tenant_repo, audit_repo=MagicMock())

    result = await list_all_tenants(skip=0, limit=50)

    assert "c.display_name" in tenant_repo._container.queries[1]
    assert result.tenants[0].display_name == "Merchant Friendly Name"


def test_display_name_request_strips_and_rejects_blank_input() -> None:
    assert DisplayNameUpdateRequest(display_name="  Friendly Merchant  ").display_name == "Friendly Merchant"

    with pytest.raises(ValidationError, match="display_name must not be blank"):
        DisplayNameUpdateRequest(display_name="   ")


@pytest.mark.asyncio
async def test_update_tenant_display_name_patches_trimmed_unique_value() -> None:
    tenant_repo = _DisplayNameRepo()
    audit_repo = MagicMock()
    audit_repo.log_event = AsyncMock()
    ctx = MagicMock(team_member_email="operator@example.com")
    configure_superadmin_services(tenant_repo=tenant_repo, audit_repo=audit_repo)

    result = await update_tenant_display_name(
        "tenant-001",
        DisplayNameUpdateRequest(display_name="  New Friendly Name  "),
        ctx=ctx,
    )

    tenant_repo.patch.assert_awaited_once()
    _, _, operations = tenant_repo.patch.await_args.args
    assert {"op": "set", "path": "/display_name", "value": "New Friendly Name"} in operations
    assert result.previous_display_name == "Old Tenant Name"
    assert result.display_name == "New Friendly Name"
    audit_repo.log_event.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_tenant_display_name_rejects_duplicate_owned_by_another_tenant() -> None:
    tenant_repo = _DisplayNameRepo(duplicates=[{"tenant_id": "tenant-002"}])
    configure_superadmin_services(tenant_repo=tenant_repo, audit_repo=MagicMock())

    with pytest.raises(HTTPException) as exc:
        await update_tenant_display_name(
            "tenant-001",
            DisplayNameUpdateRequest(display_name="Shared Friendly Name"),
            ctx=MagicMock(team_member_email="operator@example.com"),
        )

    assert exc.value.status_code == 409
    tenant_repo.patch.assert_not_awaited()


def test_provider_spa_display_name_sorting_and_uuid_debug_wiring() -> None:
    root = Path("applications/Agent_Red/admin/provider")
    hook_source = (root / "hooks/useTenantDirectory.ts").read_text(encoding="utf-8")
    page_source = (root / "pages/TenantDirectory.tsx").read_text(encoding="utf-8")
    name_source = (root / "components/TenantName.tsx").read_text(encoding="utf-8")

    assert "displayName: t.displayName || t.tenantId" in hook_source
    assert "isUuid: !hasDisplayName" in hook_source
    assert "useState<SortField>('displayName')" in page_source
    for column in (
        'field="displayName"',
        'field="status"',
        'field="tier"',
        'field="billingChannel"',
        'field="customerEmail"',
        'field="createdAt"',
        'field="expiresAt"',
    ):
        assert column in page_source
    assert "<TenantName" in page_source
    assert "label={tenantId}" in name_source
    assert "displayName = info?.displayName ?? tenantId" in name_source
