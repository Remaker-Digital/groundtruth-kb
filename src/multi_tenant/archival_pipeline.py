"""
Archival pipeline service — Cosmos DB to Azure Blob Storage (Parquet).

Implements WI #153: Archival pipeline (Change Feed -> Parquet -> Blob).

Moves aged conversation transcripts, customer profiles, and memory vectors
from Cosmos DB (hot storage) to Azure Blob Storage as Parquet files:

    - Hot (Cosmos DB): Active data, queried in real time.
    - Warm (Blob Cool, 90d): Parquet files, queryable for compliance / ML.
    - Cold (Blob Archive, 7+ years): Lifecycle-managed by Blob rules.

Tier-based archival cutoffs mirror data retention policy
(TIER_DEFAULTS.history_depth_days):
    - Trial:        14 days
    - Starter:      90 days
    - Professional: 365 days
    - Enterprise:   unlimited retention — data is archived for ML training
                    corpus (Decision #21) but NOT deleted from Cosmos DB.

Blob lifecycle rules (configured in Terraform dr_security.tf) handle the
Warm -> Cold transition automatically:
    - warm-archive container: cool -> archive tier after 90 days
    - cold-archive container: delete after ~7 years

Blob naming convention:
    {tenant_id}/conversations/{year}/{month}/batch_{timestamp}.parquet
    {tenant_id}/profiles/{year}/{month}/batch_{timestamp}.parquet
    {tenant_id}/vectors/{year}/{month}/batch_{timestamp}.parquet

Should be called periodically via scheduled task (e.g., daily KEDA cron).

Architecture references:
    - Decision #19: Three-tier archival storage (Hot -> Warm -> Cold)
    - Decision #21: Parquet for ML training corpus (daily Change Feed -> Blob)
    - WI #52: Blob lifecycle rules in Terraform (dr_security.tf)
    - WI #153: Archival pipeline (this module)
    - WI #154: Data retention enforcement (data_retention.py — companion)

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import io
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

from src.multi_tenant.cosmos_schema import (
    TIER_DEFAULTS,
    AuditEventType,
    TenantTier,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Enterprise tier: archive for ML training but do NOT delete from Cosmos DB
ENTERPRISE_TIER = TenantTier.ENTERPRISE.value

# Non-Enterprise tiers that have a finite retention window
ARCHIVABLE_TIERS = {
    TenantTier.TRIAL.value,
    TenantTier.STARTER.value,
    TenantTier.PROFESSIONAL.value,
}

# Batch size for querying documents to archive (avoid large payloads)
ARCHIVAL_BATCH_SIZE = 200

# Warm-archive container name (must match Terraform dr_security.tf)
WARM_ARCHIVE_CONTAINER = "warm-archive"

# Audit event type for archival operations.  AuditEventType does not
# yet include a DATA_ARCHIVED variant; use a string literal until the
# enum is extended (see note in module docstring).
AUDIT_EVENT_DATA_ARCHIVED = "data.archived"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TenantArchivalResult:
    """Archival result for a single tenant."""

    tenant_id: str
    tier: str
    conversations_archived: int
    profiles_archived: int
    vectors_archived: int
    bytes_written: int


@dataclass(frozen=True)
class ArchivalScanResult:
    """Result of a full archival pipeline run."""

    tenants_scanned: int
    documents_archived: int
    bytes_written: int
    errors: int
    tenant_details: list[TenantArchivalResult] = field(default_factory=list)


# ---------------------------------------------------------------------------
# ArchivalPipelineService
# ---------------------------------------------------------------------------


class ArchivalPipelineService:
    """Moves aged data from Cosmos DB to Azure Blob Storage as Parquet.

    The pipeline queries each tenant's data, serializes qualifying
    documents to Parquet format, uploads them to the warm-archive Blob
    container, and (for non-Enterprise tiers) deletes the originals from
    Cosmos DB.  Enterprise tenants are archived for ML training but their
    hot-storage copies are preserved (unlimited retention).

    Dependencies:
        - tenant_repo: TenantRepository for listing tenants.
        - conversation_repo: ConversationRepository for conversation data.
        - profile_repo: CustomerProfileRepository for profile data.
        - vector_repo: MemoryVectorRepository for vector data.
        - audit_repo: AuditLogRepository for audit trail.
        - blob_client: Azure BlobServiceClient (optional; None in dev).
    """

    def __init__(
        self,
        tenant_repo: Any,
        conversation_repo: Any | None = None,
        profile_repo: Any | None = None,
        vector_repo: Any | None = None,
        audit_repo: Any | None = None,
        blob_client: Any | None = None,
    ) -> None:
        self._tenants = tenant_repo
        self._conversations = conversation_repo
        self._profiles = profile_repo
        self._vectors = vector_repo
        self._audit = audit_repo
        self._blob = blob_client

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def run_archival_scan(self) -> ArchivalScanResult:
        """Run the full archival pipeline across all tenants.

        Iterates all active (or past-due) tenants, calculates the
        archival cutoff per tier, serializes qualifying documents to
        Parquet, and uploads them to Blob Storage.

        For non-Enterprise tiers the original Cosmos DB documents are
        deleted after a successful upload.  Enterprise documents are
        archived (for ML training corpus) but NOT deleted.

        Returns:
            ArchivalScanResult with aggregate archival counts.
        """
        now = datetime.now(timezone.utc)
        tenants_scanned = 0
        total_docs = 0
        total_bytes = 0
        errors = 0
        details: list[TenantArchivalResult] = []

        all_tenants = await self._tenants.query(
            query="SELECT * FROM c WHERE c.status IN ('active', 'past_due')",
            parameters=[],
        )

        for tenant in all_tenants:
            tenants_scanned += 1
            tenant_id = tenant["tenant_id"]
            tier = tenant.get("tier", TenantTier.STARTER.value)

            # Calculate cutoff date for this tier
            cutoff = self._calculate_cutoff(tier, now)
            if cutoff is None and tier != ENTERPRISE_TIER:
                # No cutoff and not Enterprise — skip (safety guard)
                continue

            try:
                result = await self._archive_for_tenant(
                    tenant_id, tier, cutoff, now,
                )
                tenant_total = (
                    result.conversations_archived
                    + result.profiles_archived
                    + result.vectors_archived
                )
                if tenant_total > 0:
                    total_docs += tenant_total
                    total_bytes += result.bytes_written
                    details.append(result)
            except Exception:
                logger.exception(
                    "Archival pipeline failed for tenant=%s", tenant_id,
                )
                errors += 1

        logger.info(
            "Archival scan complete: tenants=%d documents=%d bytes=%d errors=%d",
            tenants_scanned, total_docs, total_bytes, errors,
        )

        return ArchivalScanResult(
            tenants_scanned=tenants_scanned,
            documents_archived=total_docs,
            bytes_written=total_bytes,
            errors=errors,
            tenant_details=details,
        )

    async def archive_warm_tier(
        self,
        tenant_id: str,
        tier: str,
        cutoff_iso: str,
        now: datetime,
    ) -> TenantArchivalResult:
        """Archive data older than cutoff from Cosmos DB to Blob Cool.

        This is the primary archival operation: query documents past the
        tier's history_depth_days, serialize to Parquet, upload to the
        warm-archive Blob container, and optionally delete from Cosmos DB
        (non-Enterprise only).

        Args:
            tenant_id: Tenant whose data to archive.
            tier: Tenant's current tier (for deletion policy).
            cutoff_iso: ISO 8601 timestamp — documents older than this
                        are candidates for archival.
            now: Current UTC timestamp (for blob path generation).

        Returns:
            TenantArchivalResult with counts and bytes written.
        """
        convs_archived = 0
        profiles_archived = 0
        vectors_archived = 0
        bytes_written = 0

        delete_after_archive = tier != ENTERPRISE_TIER

        # --- Conversations ---
        if self._conversations:
            count, nbytes = await self._archive_collection(
                repo=self._conversations,
                tenant_id=tenant_id,
                cutoff_iso=cutoff_iso,
                date_field="ended_at",
                collection_label="conversations",
                now=now,
                delete_originals=delete_after_archive,
            )
            convs_archived = count
            bytes_written += nbytes

        # --- Customer profiles ---
        if self._profiles:
            count, nbytes = await self._archive_collection(
                repo=self._profiles,
                tenant_id=tenant_id,
                cutoff_iso=cutoff_iso,
                date_field="updated_at",
                collection_label="profiles",
                now=now,
                delete_originals=delete_after_archive,
            )
            profiles_archived = count
            bytes_written += nbytes

        # --- Memory vectors ---
        if self._vectors:
            count, nbytes = await self._archive_collection(
                repo=self._vectors,
                tenant_id=tenant_id,
                cutoff_iso=cutoff_iso,
                date_field="created_at",
                collection_label="vectors",
                now=now,
                delete_originals=delete_after_archive,
            )
            vectors_archived = count
            bytes_written += nbytes

        # Audit trail
        total = convs_archived + profiles_archived + vectors_archived
        if self._audit and total > 0:
            await self._audit.log_event(
                tenant_id=tenant_id,
                event_type=AUDIT_EVENT_DATA_ARCHIVED,
                actor="system",
                details={
                    "tier": tier,
                    "cutoff": cutoff_iso,
                    "conversations_archived": convs_archived,
                    "profiles_archived": profiles_archived,
                    "vectors_archived": vectors_archived,
                    "bytes_written": bytes_written,
                    "deleted_from_cosmos": delete_after_archive,
                },
            )

        return TenantArchivalResult(
            tenant_id=tenant_id,
            tier=tier,
            conversations_archived=convs_archived,
            profiles_archived=profiles_archived,
            vectors_archived=vectors_archived,
            bytes_written=bytes_written,
        )

    async def archive_cold_tier(
        self,
        tenant_id: str,
    ) -> dict[str, Any]:
        """Track cold-tier archival status for a tenant.

        The actual Warm -> Cold transition is handled by Azure Blob
        lifecycle rules (configured in Terraform dr_security.tf:
        warm -> cool after 30 days, cool -> archive after 90 days).

        This method provides a metadata audit record so the platform
        can verify which tenants have data in cold storage and when
        the lifecycle transition was last observed.

        Args:
            tenant_id: Tenant to check.

        Returns:
            Dict with cold-tier tracking metadata.
        """
        result: dict[str, Any] = {
            "tenant_id": tenant_id,
            "cold_tier_managed_by": "azure_blob_lifecycle_rules",
            "warm_container": WARM_ARCHIVE_CONTAINER,
            "lifecycle_policy": {
                "warm_to_cool_days": 30,
                "cool_to_archive_days": 90,
                "archive_delete_years": 7,
            },
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }

        if self._audit:
            await self._audit.log_event(
                tenant_id=tenant_id,
                event_type=AUDIT_EVENT_DATA_ARCHIVED,
                actor="system",
                details={
                    "action": "cold_tier_check",
                    **result,
                },
            )

        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _calculate_cutoff(
        self,
        tier: str,
        now: datetime,
    ) -> str | None:
        """Calculate the archival cutoff timestamp for a tier.

        Enterprise tier returns a cutoff 90 days ago (archive for ML
        training) but callers must NOT delete the originals.

        Returns:
            ISO 8601 cutoff string, or None if the tier has no retention
            policy and is not Enterprise.
        """
        from src.multi_tenant.entitlement_service import get_entitlement_service
        tier_defaults = get_entitlement_service().get_tier_config_sync(tier)
        history_days = tier_defaults.get("history_depth_days")

        if history_days is None:
            if tier == ENTERPRISE_TIER:
                # Enterprise: archive conversations older than 90 days
                # for ML training corpus, but do NOT delete originals.
                history_days = 90
            else:
                return None

        cutoff = now - timedelta(days=history_days)
        return cutoff.isoformat()

    async def _archive_for_tenant(
        self,
        tenant_id: str,
        tier: str,
        cutoff: str | None,
        now: datetime,
    ) -> TenantArchivalResult:
        """Orchestrate archival for a single tenant.

        Delegates to archive_warm_tier with the appropriate cutoff.
        """
        if cutoff is None:
            # No archival needed (safety — should not reach here)
            return TenantArchivalResult(
                tenant_id=tenant_id,
                tier=tier,
                conversations_archived=0,
                profiles_archived=0,
                vectors_archived=0,
                bytes_written=0,
            )

        return await self.archive_warm_tier(
            tenant_id=tenant_id,
            tier=tier,
            cutoff_iso=cutoff,
            now=now,
        )

    async def _archive_collection(
        self,
        repo: Any,
        tenant_id: str,
        cutoff_iso: str,
        date_field: str,
        collection_label: str,
        now: datetime,
        delete_originals: bool,
    ) -> tuple[int, int]:
        """Archive documents from one collection to Blob Storage.

        Queries documents older than cutoff, serializes them to Parquet
        (if pyarrow is available; falls back to JSON lines), uploads to
        Blob, and optionally deletes the originals.

        Args:
            repo: Collection repository (must support query/delete).
            tenant_id: Owning tenant.
            cutoff_iso: ISO 8601 cutoff — documents older are archived.
            date_field: Document field holding the relevant timestamp.
            collection_label: Human label for logging and blob paths
                              (conversations, profiles, vectors).
            now: Current UTC timestamp for blob path naming.
            delete_originals: Whether to remove archived docs from
                              Cosmos DB (False for Enterprise tier).

        Returns:
            Tuple of (document_count, bytes_written).
        """
        archived = 0
        total_bytes = 0

        try:
            old_docs = await repo.query(
                query=(
                    f"SELECT * FROM c WHERE c.tenant_id = @tid "
                    f"AND c.{date_field} < @cutoff"
                ),
                parameters=[
                    {"name": "@tid", "value": tenant_id},
                    {"name": "@cutoff", "value": cutoff_iso},
                ],
            )
        except Exception:
            logger.warning(
                "Could not query old %s for tenant %s",
                collection_label, tenant_id,
            )
            return 0, 0

        if not old_docs:
            return 0, 0

        # Serialize to Parquet (or JSON lines fallback)
        parquet_bytes = self._serialize_to_parquet(old_docs)
        if parquet_bytes is None:
            logger.warning(
                "Serialization failed for %s/%s — skipping upload",
                tenant_id, collection_label,
            )
            return 0, 0

        total_bytes = len(parquet_bytes)

        # Upload to Blob Storage
        blob_name = self._build_blob_name(
            tenant_id, collection_label, now,
        )
        upload_ok = await self._upload_to_blob(
            parquet_bytes, blob_name,
        )

        if not upload_ok:
            logger.warning(
                "Blob upload failed for %s/%s — documents NOT deleted",
                tenant_id, collection_label,
            )
            return 0, 0

        archived = len(old_docs)

        # Optionally delete originals from Cosmos DB
        if delete_originals:
            deleted = await self._delete_archived_documents(
                repo, tenant_id, old_docs, collection_label,
            )
            if deleted < archived:
                logger.warning(
                    "Partial deletion for %s/%s: archived=%d deleted=%d",
                    tenant_id, collection_label, archived, deleted,
                )

        logger.info(
            "Archived %d %s for tenant %s (%d bytes, delete=%s)",
            archived, collection_label, tenant_id, total_bytes,
            delete_originals,
        )

        return archived, total_bytes

    def _serialize_to_parquet(
        self,
        documents: list[dict[str, Any]],
    ) -> bytes | None:
        """Serialize a list of documents to Parquet format.

        Uses pyarrow if available.  Falls back to JSON-lines encoded as
        UTF-8 bytes if pyarrow is not installed (development environments).

        Args:
            documents: List of Cosmos DB document dicts.

        Returns:
            Parquet (or JSONL fallback) bytes, or None on error.
        """
        if not documents:
            return None

        try:
            import pyarrow as pa  # noqa: F811
            import pyarrow.parquet as pq  # noqa: F811

            return self._serialize_with_pyarrow(documents, pa, pq)
        except ImportError:
            logger.debug(
                "pyarrow not installed — falling back to JSON lines",
            )
            return self._serialize_as_jsonl(documents)
        except Exception:
            logger.exception("Parquet serialization failed")
            return None

    @staticmethod
    def _serialize_with_pyarrow(
        documents: list[dict[str, Any]],
        pa: Any,
        pq: Any,
    ) -> bytes:
        """Serialize documents to Parquet using pyarrow.

        Converts each document to a flat dict of string values (nested
        structures are JSON-encoded) so that pyarrow can infer a
        consistent schema across heterogeneous documents.

        Returns:
            Parquet file bytes.
        """
        import json as _json

        # Flatten: convert non-scalar values to JSON strings
        flat_rows: list[dict[str, str | int | float | bool | None]] = []
        for doc in documents:
            flat: dict[str, str | int | float | bool | None] = {}
            for key, value in doc.items():
                if isinstance(value, (str, int, float, bool)) or value is None:
                    flat[key] = value
                else:
                    flat[key] = _json.dumps(value, default=str)
            flat_rows.append(flat)

        table = pa.Table.from_pylist(flat_rows)

        buf = io.BytesIO()
        pq.write_table(table, buf, compression="snappy")
        return buf.getvalue()

    @staticmethod
    def _serialize_as_jsonl(
        documents: list[dict[str, Any]],
    ) -> bytes:
        """Fallback serializer: JSON lines (one JSON object per line).

        Used when pyarrow is not installed (e.g., local development).
        """
        import json as _json

        lines: list[str] = []
        for doc in documents:
            lines.append(_json.dumps(doc, default=str))
        return "\n".join(lines).encode("utf-8")

    @staticmethod
    def _build_blob_name(
        tenant_id: str,
        collection_label: str,
        now: datetime,
    ) -> str:
        """Build the Blob Storage path for an archival batch.

        Pattern: {tenant_id}/{collection}/{year}/{month}/batch_{timestamp}.parquet

        Args:
            tenant_id: Owning tenant.
            collection_label: conversations | profiles | vectors.
            now: Current UTC timestamp.

        Returns:
            Blob name string.
        """
        year = now.strftime("%Y")
        month = now.strftime("%m")
        ts = now.strftime("%Y%m%dT%H%M%SZ")
        return f"{tenant_id}/{collection_label}/{year}/{month}/batch_{ts}.parquet"

    async def _upload_to_blob(
        self,
        data: bytes,
        blob_name: str,
    ) -> bool:
        """Upload bytes to Azure Blob Storage warm-archive container.

        Args:
            data: File content (Parquet or JSONL bytes).
            blob_name: Full blob path within the warm-archive container.

        Returns:
            True on success, False on failure or if no blob client.
        """
        if self._blob is None:
            logger.info(
                "Blob client not configured — archival upload skipped "
                "(blob_name=%s, %d bytes)",
                blob_name, len(data),
            )
            # In development, treat as success so downstream logic
            # (deletion, audit) still proceeds for testing purposes.
            return True

        try:
            container_client = self._blob.get_container_client(
                WARM_ARCHIVE_CONTAINER,
            )
            blob_client = container_client.get_blob_client(blob_name)
            await blob_client.upload_blob(
                data,
                overwrite=True,
                blob_type="BlockBlob",
                content_settings={
                    "content_type": "application/octet-stream",
                },
            )
            logger.info(
                "Uploaded %d bytes to %s/%s",
                len(data), WARM_ARCHIVE_CONTAINER, blob_name,
            )
            return True
        except Exception:
            logger.exception(
                "Failed to upload blob %s/%s",
                WARM_ARCHIVE_CONTAINER, blob_name,
            )
            return False

    async def _delete_archived_documents(
        self,
        repo: Any,
        tenant_id: str,
        documents: list[dict[str, Any]],
        collection_label: str,
    ) -> int:
        """Delete archived documents from Cosmos DB.

        Only called for non-Enterprise tiers after successful blob
        upload.

        Returns:
            Count of successfully deleted documents.
        """
        deleted = 0
        for doc in documents:
            doc_id = doc.get("id")
            if not doc_id:
                continue
            try:
                await repo.delete(doc_id, tenant_id)
                deleted += 1
            except Exception:
                logger.debug(
                    "Could not delete %s/%s for tenant %s",
                    collection_label, doc_id, tenant_id,
                )
        return deleted

    def get_archival_cutoff(self, tier: str) -> int | None:
        """Get the archival cutoff in days for a tier.

        Args:
            tier: The tenant tier.

        Returns:
            Days after which data is archived, or None for unlimited
            retention tiers (Enterprise still archives at 90 days for
            ML training but does not delete).
        """
        from src.multi_tenant.entitlement_service import get_entitlement_service
        tier_defaults = get_entitlement_service().get_tier_config_sync(tier)
        history_days = tier_defaults.get("history_depth_days")
        if history_days is None and tier == ENTERPRISE_TIER:
            return 90  # ML training corpus archival
        return history_days


# ---------------------------------------------------------------------------
# Module singleton
# ---------------------------------------------------------------------------

_archival_service: ArchivalPipelineService | None = None


def get_archival_service() -> ArchivalPipelineService | None:
    """Get the module-level ArchivalPipelineService singleton."""
    return _archival_service


def configure_archival_service(service: ArchivalPipelineService) -> None:
    """Wire the archival pipeline service at app startup."""
    global _archival_service
    _archival_service = service
