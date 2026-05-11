"""Comprehensive tests for DataRetentionService — WI #154.

Covers tier-based data retention enforcement: iterating active tenants,
applying tier-specific retention cutoffs (Trial 14d, Starter 90d,
Professional 365d, Enterprise unlimited/skipped), deleting expired
conversations and vectors, purging stale profiles, audit logging,
error isolation, result aggregation, and module singleton management.

Test IDs: DR-01 through DR-15.

Run:
    pytest tests/multi_tenant/test_data_retention.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock


from src.multi_tenant.cosmos_schema import (
    AuditEventType,
    TenantTier,
    TIER_DEFAULTS,
)
from src.multi_tenant.data_retention import (
    UNLIMITED_RETENTION_TIERS,
    DataRetentionService,
    RetentionScanResult,
    configure_retention_service,
    get_retention_service,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_TENANT_TRIAL = "t-ret-trial-001"
_TENANT_STARTER = "t-ret-starter-001"
_TENANT_PRO = "t-ret-pro-001"
_TENANT_ENT = "t-ret-ent-001"


def _make_tenant_doc(
    tenant_id: str,
    tier: str,
    status: str = "active",
) -> dict:
    """Build a minimal tenant document dict."""
    return {
        "id": tenant_id,
        "tenant_id": tenant_id,
        "tier": tier,
        "status": status,
    }


def _make_repos(
    tenant_query_results: list[dict] | None = None,
    conversation_query_results: list[dict] | None = None,
    profile_query_results: list[dict] | None = None,
    vector_query_results: list[dict] | None = None,
) -> tuple[AsyncMock, AsyncMock, AsyncMock, AsyncMock, AsyncMock]:
    """Build mock repositories for DataRetentionService.

    Returns:
        (tenant_repo, conversation_repo, profile_repo, vector_repo, audit_repo)
    """
    tenant_repo = AsyncMock()
    tenant_repo.query.return_value = tenant_query_results if tenant_query_results is not None else []

    conversation_repo = AsyncMock()
    conversation_repo.query.return_value = conversation_query_results if conversation_query_results is not None else []
    conversation_repo.delete.return_value = None

    profile_repo = AsyncMock()
    profile_repo.query.return_value = profile_query_results if profile_query_results is not None else []
    profile_repo.patch.return_value = None

    vector_repo = AsyncMock()
    vector_repo.query.return_value = vector_query_results if vector_query_results is not None else []
    vector_repo.delete.return_value = None

    audit_repo = AsyncMock()
    audit_repo.log_event.return_value = None

    return tenant_repo, conversation_repo, profile_repo, vector_repo, audit_repo


def _make_service(
    tenant_query_results: list[dict] | None = None,
    conversation_query_results: list[dict] | None = None,
    profile_query_results: list[dict] | None = None,
    vector_query_results: list[dict] | None = None,
) -> tuple[DataRetentionService, tuple[AsyncMock, ...]]:
    """Create a DataRetentionService with mocked repos.

    Returns:
        (service, (tenant_repo, conversation_repo, profile_repo,
         vector_repo, audit_repo))
    """
    repos = _make_repos(
        tenant_query_results=tenant_query_results,
        conversation_query_results=conversation_query_results,
        profile_query_results=profile_query_results,
        vector_query_results=vector_query_results,
    )
    tenant_repo, conversation_repo, profile_repo, vector_repo, audit_repo = repos

    service = DataRetentionService(
        tenant_repo=tenant_repo,
        conversation_repo=conversation_repo,
        profile_repo=profile_repo,
        vector_repo=vector_repo,
        audit_repo=audit_repo,
    )
    return service, repos


# ===========================================================================
# DR-01 through DR-15: Data retention enforcement
# ===========================================================================


class TestRetentionEnforcement:
    """DR-01 through DR-13: enforce_retention() scan logic."""

    async def test_dr_01_iterates_all_active_tenants(self):
        """DR-01: enforce_retention() queries and iterates all active tenants."""
        tenants = [
            _make_tenant_doc(_TENANT_STARTER, TenantTier.STARTER.value),
            _make_tenant_doc(_TENANT_PRO, TenantTier.PROFESSIONAL.value),
            _make_tenant_doc(_TENANT_ENT, TenantTier.ENTERPRISE.value),
        ]
        service, repos = _make_service(tenant_query_results=tenants)
        tenant_repo = repos[0]

        result = await service.enforce_retention()

        assert isinstance(result, RetentionScanResult)
        assert result.tenants_scanned == 3
        tenant_repo.query.assert_awaited_once()
        # Verify the query fetches active/past_due tenants
        query_arg = tenant_repo.query.call_args.kwargs.get("query") or tenant_repo.query.call_args[1].get("query") or tenant_repo.query.call_args[0][0]
        assert "active" in query_arg
        assert "past_due" in query_arg

    async def test_dr_02_trial_tier_uses_fallback_cutoff(self):
        """DR-02: Trial tier uses fallback retention cutoff (90 days) since
        history_depth_days was removed from TIER_DEFAULTS."""
        service, _ = _make_service()
        retention_days = service.get_retention_days(TenantTier.TRIAL.value)
        assert retention_days == 90
        assert "history_depth_days" not in TIER_DEFAULTS[TenantTier.TRIAL.value]

    async def test_dr_03_starter_tier_uses_90_day_cutoff(self):
        """DR-03: Starter tier uses 90-day retention cutoff (fallback)."""
        service, _ = _make_service()
        retention_days = service.get_retention_days(TenantTier.STARTER.value)
        assert retention_days == 90
        assert "history_depth_days" not in TIER_DEFAULTS[TenantTier.STARTER.value]

    async def test_dr_04_professional_tier_uses_fallback_cutoff(self):
        """DR-04: Professional tier uses fallback retention cutoff (90 days) since
        history_depth_days was removed from TIER_DEFAULTS."""
        service, _ = _make_service()
        retention_days = service.get_retention_days(TenantTier.PROFESSIONAL.value)
        assert retention_days == 90
        assert "history_depth_days" not in TIER_DEFAULTS[TenantTier.PROFESSIONAL.value]

    async def test_dr_05_enterprise_tier_skipped(self):
        """DR-05: Enterprise tier is skipped (unlimited retention)."""
        enterprise_tenant = _make_tenant_doc(_TENANT_ENT, TenantTier.ENTERPRISE.value)
        service, repos = _make_service(tenant_query_results=[enterprise_tenant])
        conversation_repo = repos[1]

        result = await service.enforce_retention()

        assert result.tenants_scanned == 1
        assert result.conversations_deleted == 0
        assert result.tenants_with_deletions == 0
        # Enterprise skipped — no conversation queries issued
        conversation_repo.query.assert_not_awaited()

        # Also verify via get_retention_days
        assert service.get_retention_days(TenantTier.ENTERPRISE.value) is None
        assert TenantTier.ENTERPRISE.value in UNLIMITED_RETENTION_TIERS

    async def test_dr_06_conversations_older_than_cutoff_deleted(self):
        """DR-06: Conversations older than the tier cutoff are deleted."""
        starter_tenant = _make_tenant_doc(_TENANT_STARTER, TenantTier.STARTER.value)
        old_convs = [{"id": "conv-old-1"}, {"id": "conv-old-2"}, {"id": "conv-old-3"}]

        service, repos = _make_service(
            tenant_query_results=[starter_tenant],
            conversation_query_results=old_convs,
        )
        conversation_repo = repos[1]

        result = await service.enforce_retention()

        assert result.conversations_deleted == 3
        assert conversation_repo.delete.await_count == 3
        # Verify each doc was deleted with the correct tenant_id
        for call_item in conversation_repo.delete.call_args_list:
            assert call_item[0][1] == _TENANT_STARTER

    async def test_dr_07_conversations_newer_than_cutoff_preserved(self):
        """DR-07: When no conversations are older than cutoff, none are deleted."""
        starter_tenant = _make_tenant_doc(_TENANT_STARTER, TenantTier.STARTER.value)
        # Empty query result = no old conversations found
        service, repos = _make_service(
            tenant_query_results=[starter_tenant],
            conversation_query_results=[],
        )
        conversation_repo = repos[1]

        result = await service.enforce_retention()

        assert result.conversations_deleted == 0
        conversation_repo.delete.assert_not_awaited()

    async def test_dr_08_memory_vectors_older_than_cutoff_deleted(self):
        """DR-08: Memory vectors older than cutoff are deleted."""
        starter_tenant = _make_tenant_doc(_TENANT_STARTER, TenantTier.STARTER.value)
        old_vectors = [{"id": "vec-1"}, {"id": "vec-2"}]

        service, repos = _make_service(
            tenant_query_results=[starter_tenant],
            vector_query_results=old_vectors,
        )
        vector_repo = repos[3]

        result = await service.enforce_retention()

        assert result.vectors_deleted == 2
        assert vector_repo.delete.await_count == 2

    async def test_dr_09_stale_customer_profiles_purged(self):
        """DR-09: Stale customer profiles are purged (fields cleared, not deleted)."""
        starter_tenant = _make_tenant_doc(_TENANT_STARTER, TenantTier.STARTER.value)
        stale_profiles = [{"id": "prof-1"}, {"id": "prof-2"}]

        service, repos = _make_service(
            tenant_query_results=[starter_tenant],
            profile_query_results=stale_profiles,
        )
        profile_repo = repos[2]

        result = await service.enforce_retention()

        assert result.profiles_purged == 2
        assert profile_repo.patch.await_count == 2
        # Verify patch operations clear conversation_history and reset interaction_count
        for call_item in profile_repo.patch.call_args_list:
            operations = call_item.kwargs.get("operations", call_item[0][2] if len(call_item[0]) > 2 else [])
            op_paths = [op["path"] for op in operations]
            assert "/conversation_history" in op_paths
            assert "/interaction_count" in op_paths

    async def test_dr_10_audit_log_records_deletion_events(self):
        """DR-10: Audit log records deletion events for tenants with deletions."""
        starter_tenant = _make_tenant_doc(_TENANT_STARTER, TenantTier.STARTER.value)
        old_convs = [{"id": "conv-1"}]

        service, repos = _make_service(
            tenant_query_results=[starter_tenant],
            conversation_query_results=old_convs,
        )
        audit_repo = repos[4]

        await service.enforce_retention()

        audit_repo.log_event.assert_awaited_once()
        log_call = audit_repo.log_event.call_args
        assert log_call.kwargs["tenant_id"] == _TENANT_STARTER
        assert log_call.kwargs["event_type"] == AuditEventType.DATA_DELETED
        assert log_call.kwargs["actor"] == "system"
        assert log_call.kwargs["details"]["reason"] == "retention_policy"
        assert log_call.kwargs["details"]["tier"] == TenantTier.STARTER.value
        assert log_call.kwargs["details"]["retention_days"] == 90
        assert log_call.kwargs["details"]["conversations_deleted"] == 1

    async def test_dr_11_errors_for_one_tenant_dont_stop_others(self):
        """DR-11: Error processing one tenant does not stop other tenants.

        The error must escape _enforce_for_tenant to increment the errors
        counter. Internal methods (_delete_old_documents, _purge_stale_profile_data)
        catch their own exceptions. The audit_repo.log_event call inside
        _enforce_for_tenant is NOT wrapped in try/except, so making it raise
        for a specific tenant (which has deletions) triggers the error path.
        """
        good_tenant = _make_tenant_doc(_TENANT_STARTER, TenantTier.STARTER.value)
        bad_tenant = _make_tenant_doc("t-bad-001", TenantTier.STARTER.value)
        good_tenant_2 = _make_tenant_doc(_TENANT_PRO, TenantTier.PROFESSIONAL.value)

        service, repos = _make_service(
            tenant_query_results=[good_tenant, bad_tenant, good_tenant_2],
        )
        conversation_repo = repos[1]
        audit_repo = repos[4]

        # Return old docs for all tenants so _enforce_for_tenant calls audit
        async def _conv_query(**kwargs):
            return [{"id": "conv-1"}]

        conversation_repo.query.side_effect = _conv_query

        # Make audit_repo.log_event raise only for the bad tenant
        async def _audit_side_effect(**kwargs):
            if kwargs.get("tenant_id") == "t-bad-001":
                raise RuntimeError("Simulated audit write error")

        audit_repo.log_event.side_effect = _audit_side_effect

        result = await service.enforce_retention()

        assert result.tenants_scanned == 3
        assert result.errors == 1
        # The good tenants were still processed and had deletions
        assert result.conversations_deleted >= 2

    async def test_dr_12_retention_scan_result_aggregates_correctly(self):
        """DR-12: RetentionScanResult aggregates counts from multiple tenants."""
        trial_tenant = _make_tenant_doc(_TENANT_TRIAL, TenantTier.TRIAL.value)
        starter_tenant = _make_tenant_doc(_TENANT_STARTER, TenantTier.STARTER.value)

        service, repos = _make_service(
            tenant_query_results=[trial_tenant, starter_tenant],
        )
        conversation_repo = repos[1]
        vector_repo = repos[3]
        profile_repo = repos[2]

        # Configure repos to return different results per tenant
        conv_call_count = 0

        async def _conv_query(**kwargs):
            nonlocal conv_call_count
            conv_call_count += 1
            params = kwargs.get("parameters", [])
            tenant_id = None
            for p in params:
                if p.get("name") == "@tid":
                    tenant_id = p["value"]
            if tenant_id == _TENANT_TRIAL:
                return [{"id": "c1"}, {"id": "c2"}]
            if tenant_id == _TENANT_STARTER:
                return [{"id": "c3"}]
            return []

        async def _vec_query(**kwargs):
            params = kwargs.get("parameters", [])
            tenant_id = None
            for p in params:
                if p.get("name") == "@tid":
                    tenant_id = p["value"]
            if tenant_id == _TENANT_TRIAL:
                return [{"id": "v1"}]
            return []

        async def _prof_query(**kwargs):
            params = kwargs.get("parameters", [])
            tenant_id = None
            for p in params:
                if p.get("name") == "@tid":
                    tenant_id = p["value"]
            if tenant_id == _TENANT_STARTER:
                return [{"id": "p1"}]
            return []

        conversation_repo.query.side_effect = _conv_query
        vector_repo.query.side_effect = _vec_query
        profile_repo.query.side_effect = _prof_query

        result = await service.enforce_retention()

        assert result.tenants_scanned == 2
        assert result.conversations_deleted == 3  # 2 from trial + 1 from starter
        assert result.vectors_deleted == 1         # 1 from trial
        assert result.profiles_purged == 1         # 1 from starter
        assert result.tenants_with_deletions == 2
        assert len(result.tenant_details) == 2

    async def test_dr_13_empty_tenant_list_returns_zero_counts(self):
        """DR-13: Empty tenant list returns zero counts."""
        service, repos = _make_service(tenant_query_results=[])

        result = await service.enforce_retention()

        assert result.tenants_scanned == 0
        assert result.tenants_with_deletions == 0
        assert result.conversations_deleted == 0
        assert result.profiles_purged == 0
        assert result.vectors_deleted == 0
        assert result.errors == 0
        assert result.tenant_details == []


class TestModuleSingleton:
    """DR-14 through DR-15: Module singleton management."""

    def test_dr_14_get_retention_service_default_none(self):
        """DR-14: get_retention_service() returns None before configuration."""
        # Reset the module singleton to a known state
        import src.multi_tenant.data_retention as dr_mod
        original = dr_mod._retention_service
        try:
            dr_mod._retention_service = None
            assert get_retention_service() is None
        finally:
            dr_mod._retention_service = original

    def test_dr_15_configure_retention_service_replaces_singleton(self):
        """DR-15: configure_retention_service() replaces the module singleton."""
        import src.multi_tenant.data_retention as dr_mod
        original = dr_mod._retention_service
        try:
            tenant_repo = AsyncMock()
            service_a = DataRetentionService(tenant_repo=tenant_repo)
            service_b = DataRetentionService(tenant_repo=tenant_repo)

            configure_retention_service(service_a)
            assert get_retention_service() is service_a

            configure_retention_service(service_b)
            assert get_retention_service() is service_b
            assert get_retention_service() is not service_a
        finally:
            dr_mod._retention_service = original
