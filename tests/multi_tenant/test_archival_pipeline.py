"""Comprehensive tests for ArchivalPipelineService — WI #153.

Covers the archival pipeline: iterating active tenants, tier-based archival
cutoffs (Trial 14d, Starter 90d, Enterprise ML-archive without deletion),
Parquet serialization, blob upload path patterns, dry-run mode (no blob
client), error isolation, result aggregation, and module singleton management.

Test IDs: AP-01 through AP-15.

Run:
    pytest tests/multi_tenant/test_archival_pipeline.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock


from src.multi_tenant.cosmos_schema import (
    TenantTier,
    TIER_DEFAULTS,
)
from src.multi_tenant.archival_pipeline import (
    WARM_ARCHIVE_CONTAINER,
    ArchivalPipelineService,
    ArchivalScanResult,
    configure_archival_service,
    get_archival_service,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_TENANT_TRIAL = "t-arch-trial-001"
_TENANT_STARTER = "t-arch-starter-001"
_TENANT_PRO = "t-arch-pro-001"
_TENANT_ENT = "t-arch-ent-001"


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


def _make_old_docs(prefix: str, count: int) -> list[dict]:
    """Build a list of document dicts with sequential IDs."""
    return [{"id": f"{prefix}-{i}", "tenant_id": "placeholder", "data": f"val-{i}"} for i in range(count)]


def _make_repos(
    tenant_query_results: list[dict] | None = None,
    conversation_query_results: list[dict] | None = None,
    profile_query_results: list[dict] | None = None,
    vector_query_results: list[dict] | None = None,
) -> tuple[AsyncMock, AsyncMock, AsyncMock, AsyncMock, AsyncMock]:
    """Build mock repositories for ArchivalPipelineService.

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
    profile_repo.delete.return_value = None

    vector_repo = AsyncMock()
    vector_repo.query.return_value = vector_query_results if vector_query_results is not None else []
    vector_repo.delete.return_value = None

    audit_repo = AsyncMock()
    audit_repo.log_event.return_value = None

    return tenant_repo, conversation_repo, profile_repo, vector_repo, audit_repo


def _make_blob_client() -> MagicMock:
    """Build a mock Azure BlobServiceClient.

    get_container_client() and get_blob_client() are synchronous calls
    in the Azure SDK. Only upload_blob() is awaited.
    """
    blob_client = MagicMock()
    container_client = MagicMock()
    blob_ref = AsyncMock()

    blob_client.get_container_client.return_value = container_client
    container_client.get_blob_client.return_value = blob_ref
    blob_ref.upload_blob.return_value = None

    return blob_client


def _make_service(
    tenant_query_results: list[dict] | None = None,
    conversation_query_results: list[dict] | None = None,
    profile_query_results: list[dict] | None = None,
    vector_query_results: list[dict] | None = None,
    blob_client: AsyncMock | None = None,
) -> tuple[ArchivalPipelineService, tuple[AsyncMock, ...]]:
    """Create an ArchivalPipelineService with mocked repos.

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

    service = ArchivalPipelineService(
        tenant_repo=tenant_repo,
        conversation_repo=conversation_repo,
        profile_repo=profile_repo,
        vector_repo=vector_repo,
        audit_repo=audit_repo,
        blob_client=blob_client,
    )
    return service, repos


# ===========================================================================
# AP-01 through AP-15: Archival pipeline
# ===========================================================================


class TestArchivalScan:
    """AP-01 through AP-08: run_archival_scan() and tier-based archival logic."""

    async def test_ap_01_iterates_all_active_tenants(self):
        """AP-01: run_archival_scan() queries and iterates all active tenants."""
        tenants = [
            _make_tenant_doc(_TENANT_STARTER, TenantTier.STARTER.value),
            _make_tenant_doc(_TENANT_PRO, TenantTier.PROFESSIONAL.value),
            _make_tenant_doc(_TENANT_ENT, TenantTier.ENTERPRISE.value),
        ]
        service, repos = _make_service(tenant_query_results=tenants)
        tenant_repo = repos[0]

        result = await service.run_archival_scan()

        assert isinstance(result, ArchivalScanResult)
        assert result.tenants_scanned == 3
        tenant_repo.query.assert_awaited_once()
        query_arg = tenant_repo.query.call_args.kwargs.get("query") or tenant_repo.query.call_args[0][0]
        assert "active" in query_arg
        assert "past_due" in query_arg

    async def test_ap_02_trial_tier_returns_none_after_removal(self):
        """AP-02: Trial tier archival returns None since history_depth_days
        was removed from TIER_DEFAULTS."""
        service, _ = _make_service()
        cutoff_days = service.get_archival_cutoff(TenantTier.TRIAL.value)
        assert cutoff_days is None
        assert "history_depth_days" not in TIER_DEFAULTS[TenantTier.TRIAL.value]

    async def test_ap_03_starter_tier_returns_none_after_removal(self):
        """AP-03: Starter tier archival returns None since history_depth_days
        was removed from TIER_DEFAULTS."""
        service, _ = _make_service()
        cutoff_days = service.get_archival_cutoff(TenantTier.STARTER.value)
        assert cutoff_days is None

    async def test_ap_04_enterprise_archives_but_does_not_delete(self):
        """AP-04: Enterprise tier archives for ML but does NOT delete originals."""
        ent_tenant = _make_tenant_doc(_TENANT_ENT, TenantTier.ENTERPRISE.value)
        old_convs = _make_old_docs("conv", 3)

        service, repos = _make_service(
            tenant_query_results=[ent_tenant],
            conversation_query_results=old_convs,
        )
        conversation_repo = repos[1]

        result = await service.run_archival_scan()

        # Documents should be archived
        assert result.documents_archived == 3
        # But originals should NOT be deleted (Enterprise = unlimited retention)
        conversation_repo.delete.assert_not_awaited()

        # Verify the archival cutoff for Enterprise is 90 days (for ML training)
        assert service.get_archival_cutoff(TenantTier.ENTERPRISE.value) == 90

    async def test_ap_05_non_enterprise_skipped_after_removal(self):
        """AP-05: Non-Enterprise tiers are skipped since history_depth_days
        was removed from TIER_DEFAULTS (cutoff is None)."""
        starter_tenant = _make_tenant_doc(_TENANT_STARTER, TenantTier.STARTER.value)
        old_convs = _make_old_docs("conv", 2)

        service, repos = _make_service(
            tenant_query_results=[starter_tenant],
            conversation_query_results=old_convs,
        )
        conversation_repo = repos[1]

        result = await service.run_archival_scan()

        # With history_depth_days removed, non-enterprise tenants are skipped
        assert result.documents_archived == 0
        conversation_repo.delete.assert_not_awaited()

    async def test_ap_06_starter_skipped_after_removal(self):
        """AP-06: Starter tenants skipped since history_depth_days removed
        from TIER_DEFAULTS (cutoff is None)."""
        starter_tenant = _make_tenant_doc(_TENANT_STARTER, TenantTier.STARTER.value)
        old_convs = [{"id": "conv-1"}, {"id": "conv-2"}, {"id": "conv-3"}]

        service, repos = _make_service(
            tenant_query_results=[starter_tenant],
            conversation_query_results=old_convs,
        )

        result = await service.run_archival_scan()

        # Starter skipped — no cutoff after history_depth_days removal
        assert result.documents_archived == 0
        assert result.tenants_scanned == 1

    async def test_ap_07_profiles_skipped_after_removal(self):
        """AP-07: Customer profiles not archived since history_depth_days
        removed from TIER_DEFAULTS."""
        starter_tenant = _make_tenant_doc(_TENANT_STARTER, TenantTier.STARTER.value)
        old_profiles = [{"id": "prof-1"}, {"id": "prof-2"}]

        service, repos = _make_service(
            tenant_query_results=[starter_tenant],
            profile_query_results=old_profiles,
        )

        result = await service.run_archival_scan()

        assert result.documents_archived == 0

    async def test_ap_08_vectors_skipped_after_removal(self):
        """AP-08: Memory vectors not archived since history_depth_days
        removed from TIER_DEFAULTS."""
        starter_tenant = _make_tenant_doc(_TENANT_STARTER, TenantTier.STARTER.value)
        old_vectors = [{"id": "vec-1"}]

        service, repos = _make_service(
            tenant_query_results=[starter_tenant],
            vector_query_results=old_vectors,
        )

        result = await service.run_archival_scan()

        assert result.documents_archived == 0


class TestParquetSerialization:
    """AP-09: Parquet / JSONL serialization."""

    def test_ap_09_serialization_produces_bytes(self):
        """AP-09: _serialize_to_parquet produces bytes (Parquet or JSONL fallback)."""
        service, _ = _make_service()
        documents = [
            {"id": "doc-1", "name": "Alice", "value": 42},
            {"id": "doc-2", "name": "Bob", "value": 99},
        ]

        result = service._serialize_to_parquet(documents)

        assert result is not None
        assert isinstance(result, bytes)
        assert len(result) > 0

        # Two valid outputs depending on whether pyarrow is installed:
        # 1. Parquet binary — verify by reading back with pyarrow
        # 2. JSONL UTF-8 text (when pyarrow is not available)
        #
        # We check pyarrow availability the SAME way the production code
        # does (try import) to stay in sync with its code path.
        import json
        import io as _io
        try:
            import pyarrow.parquet as _pq

            # pyarrow is available — production code used _serialize_with_pyarrow.
            # Verify the bytes are a valid Parquet file by reading back.
            table = _pq.read_table(_io.BytesIO(result))
            assert len(table) == 2, f"Expected 2 rows, got {len(table)}"
            assert "id" in table.column_names, (
                f"Missing 'id' column; columns={table.column_names}"
            )
            ids = table.column("id").to_pylist()
            assert "doc-1" in ids, f"doc-1 not in Parquet ids: {ids}"
            assert "doc-2" in ids, f"doc-2 not in Parquet ids: {ids}"
        except ImportError:
            # No pyarrow — production code used _serialize_as_jsonl.
            # Verify valid UTF-8 JSON lines.
            lines = result.decode("utf-8").strip().split("\n")
            assert len(lines) == 2
            parsed_0 = json.loads(lines[0])
            assert parsed_0["id"] == "doc-1"
            parsed_1 = json.loads(lines[1])
            assert parsed_1["id"] == "doc-2"

    def test_ap_09b_serialization_returns_none_for_empty(self):
        """AP-09b: _serialize_to_parquet returns None for empty document list."""
        service, _ = _make_service()
        result = service._serialize_to_parquet([])
        assert result is None


class TestBlobUpload:
    """AP-10 through AP-11: Blob upload and path patterns."""

    def test_ap_10_blob_path_pattern(self):
        """AP-10: Blob upload uses correct path pattern."""
        now = datetime(2026, 2, 1, 12, 30, 45, tzinfo=timezone.utc)
        blob_name = ArchivalPipelineService._build_blob_name(
            tenant_id="t-123",
            collection_label="conversations",
            now=now,
        )

        assert blob_name == "t-123/conversations/2026/02/batch_20260201T123045Z.parquet"

    def test_ap_10b_blob_path_for_profiles(self):
        """AP-10b: Blob path pattern works for profiles collection."""
        now = datetime(2026, 6, 15, 8, 0, 0, tzinfo=timezone.utc)
        blob_name = ArchivalPipelineService._build_blob_name(
            tenant_id="t-456",
            collection_label="profiles",
            now=now,
        )

        assert blob_name == "t-456/profiles/2026/06/batch_20260615T080000Z.parquet"

    async def test_ap_11_no_blob_client_dry_run_mode(self):
        """AP-11: No blob client = dry-run mode (archive counts but no real upload).

        Uses Enterprise tier because history_depth_days was removed from
        TIER_DEFAULTS — only Enterprise still archives (90d ML training).
        """
        ent_tenant = _make_tenant_doc(_TENANT_ENT, TenantTier.ENTERPRISE.value)
        old_convs = [{"id": "conv-1"}, {"id": "conv-2"}]

        # No blob_client passed (None) = dry-run
        service, repos = _make_service(
            tenant_query_results=[ent_tenant],
            conversation_query_results=old_convs,
            blob_client=None,
        )

        result = await service.run_archival_scan()

        # Documents are still counted as archived in dry-run
        assert result.documents_archived == 2
        assert result.bytes_written > 0  # Serialization still produces bytes

    async def test_ap_11b_blob_client_upload_called(self):
        """AP-11b: When blob client is provided, upload_blob is called.

        Uses Enterprise tier because history_depth_days was removed from
        TIER_DEFAULTS — only Enterprise still archives (90d ML training).
        """
        ent_tenant = _make_tenant_doc(_TENANT_ENT, TenantTier.ENTERPRISE.value)
        old_convs = [{"id": "conv-1"}]
        blob_client = _make_blob_client()

        service, repos = _make_service(
            tenant_query_results=[ent_tenant],
            conversation_query_results=old_convs,
            blob_client=blob_client,
        )

        result = await service.run_archival_scan()

        assert result.documents_archived == 1
        blob_client.get_container_client.assert_called_with(WARM_ARCHIVE_CONTAINER)


class TestErrorIsolation:
    """AP-12: Error isolation between tenants."""

    async def test_ap_12_errors_for_one_tenant_dont_stop_others(self):
        """AP-12: Error processing one tenant does not stop other tenants.

        The error must escape _archive_for_tenant to increment the errors
        counter. Internal methods (_archive_collection) catch their own
        exceptions. The audit_repo.log_event call inside archive_warm_tier
        is NOT wrapped in try/except, so making it raise for a specific
        tenant (which has archived docs) triggers the error path.

        Uses Enterprise tier because history_depth_days was removed from
        TIER_DEFAULTS — only Enterprise still archives (90d ML training).
        """
        good_tenant = _make_tenant_doc(_TENANT_ENT, TenantTier.ENTERPRISE.value)
        bad_tenant = _make_tenant_doc("t-bad-arch-001", TenantTier.ENTERPRISE.value)
        good_tenant_2 = _make_tenant_doc(_TENANT_PRO + "-ent", TenantTier.ENTERPRISE.value)

        service, repos = _make_service(
            tenant_query_results=[good_tenant, bad_tenant, good_tenant_2],
        )
        conversation_repo = repos[1]
        audit_repo = repos[4]

        # Return old docs for all tenants so archival proceeds to audit step
        async def _conv_query(**kwargs):
            return [{"id": "conv-1"}]

        conversation_repo.query.side_effect = _conv_query

        # Make audit raise only for the bad tenant
        async def _audit_side_effect(**kwargs):
            if kwargs.get("tenant_id") == "t-bad-arch-001":
                raise RuntimeError("Simulated audit write error")

        audit_repo.log_event.side_effect = _audit_side_effect

        result = await service.run_archival_scan()

        assert result.tenants_scanned == 3
        assert result.errors == 1
        # The good tenants were still processed and had archival
        assert result.documents_archived >= 2


class TestResultAggregation:
    """AP-13: ArchivalScanResult aggregation."""

    async def test_ap_13_aggregates_counts_correctly(self):
        """AP-13: ArchivalScanResult aggregates counts from multiple tenants.

        Uses Enterprise tier because history_depth_days was removed from
        TIER_DEFAULTS — only Enterprise still archives (90d ML training).
        """
        ent_tenant_1 = _make_tenant_doc(_TENANT_ENT, TenantTier.ENTERPRISE.value)
        ent_tenant_2 = _make_tenant_doc(_TENANT_ENT + "-2", TenantTier.ENTERPRISE.value)

        service, repos = _make_service(
            tenant_query_results=[ent_tenant_1, ent_tenant_2],
        )
        conversation_repo = repos[1]
        profile_repo = repos[2]

        async def _conv_query(**kwargs):
            params = kwargs.get("parameters", [])
            tenant_id = None
            for p in params:
                if p.get("name") == "@tid":
                    tenant_id = p["value"]
            if tenant_id == _TENANT_ENT:
                return [{"id": "c1"}, {"id": "c2"}]
            if tenant_id == _TENANT_ENT + "-2":
                return [{"id": "c3"}]
            return []

        async def _prof_query(**kwargs):
            params = kwargs.get("parameters", [])
            tenant_id = None
            for p in params:
                if p.get("name") == "@tid":
                    tenant_id = p["value"]
            if tenant_id == _TENANT_ENT + "-2":
                return [{"id": "p1"}]
            return []

        conversation_repo.query.side_effect = _conv_query
        profile_repo.query.side_effect = _prof_query

        result = await service.run_archival_scan()

        # 2 convs from ent + 1 conv from ent-2 + 1 profile from ent-2 = 4
        assert result.documents_archived == 4
        assert result.tenants_scanned == 2
        assert len(result.tenant_details) == 2
        assert result.bytes_written > 0
        assert result.errors == 0

    async def test_ap_13b_empty_tenant_list_returns_zero_counts(self):
        """AP-13b: Empty tenant list returns zero counts."""
        service, _ = _make_service(tenant_query_results=[])

        result = await service.run_archival_scan()

        assert result.tenants_scanned == 0
        assert result.documents_archived == 0
        assert result.bytes_written == 0
        assert result.errors == 0
        assert result.tenant_details == []


class TestModuleSingleton:
    """AP-14 through AP-15: Module singleton management."""

    def test_ap_14_get_archival_service_default_none(self):
        """AP-14: get_archival_service() returns None before configuration."""
        import src.multi_tenant.archival_pipeline as ap_mod
        original = ap_mod._archival_service
        try:
            ap_mod._archival_service = None
            assert get_archival_service() is None
        finally:
            ap_mod._archival_service = original

    def test_ap_15_configure_archival_service_replaces_singleton(self):
        """AP-15: configure_archival_service() replaces the module singleton."""
        import src.multi_tenant.archival_pipeline as ap_mod
        original = ap_mod._archival_service
        try:
            tenant_repo = AsyncMock()
            service_a = ArchivalPipelineService(tenant_repo=tenant_repo)
            service_b = ArchivalPipelineService(tenant_repo=tenant_repo)

            configure_archival_service(service_a)
            assert get_archival_service() is service_a

            configure_archival_service(service_b)
            assert get_archival_service() is service_b
            assert get_archival_service() is not service_a
        finally:
            ap_mod._archival_service = original
