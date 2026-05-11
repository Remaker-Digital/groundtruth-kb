# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""HV-1: Support Diagnostics API — per-tenant diagnostic snapshots.

Provider-level (SPA) API that gives the platform operator diagnostic
information about a specific tenant for support purposes.

Endpoints:
    GET /api/superadmin/diagnostics/{tenant_id}        — Comprehensive snapshot
    GET /api/superadmin/diagnostics/{tenant_id}/errors  — Recent error entries

All endpoints require SUPERADMIN role. Widget keys and tenant-level API
keys are rejected. Only per-user API keys with SUPERADMIN role are accepted.

Architecture notes:
    - Graceful degradation: each subsystem is queried independently; if one
      fails, partial data is returned with the error noted in the response.
    - Lazy imports: repositories are imported inside function bodies.
    - Cross-partition queries omit partition_key (SDK 4.14+ pattern).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import Field

from src.multi_tenant.api_models import CamelCaseModel
from src.multi_tenant.middleware import require_platform_admin

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class ConfigStateSummary(CamelCaseModel):
    """Tenant configuration state snapshot."""

    is_active: bool = False
    is_configured: bool = False
    has_pending_changes: bool = False
    active_version: int | None = None
    activated_at: str | None = None


class AIConfigSummary(CamelCaseModel):
    """AI configuration presence summary (no sensitive data)."""

    model: str | None = None
    brand_name_present: bool = False
    brand_voice_present: bool = False


class KnowledgeBaseStats(CamelCaseModel):
    """Knowledge base article statistics."""

    total_articles: int = 0
    draft_count: int = 0
    active_count: int = 0


class TeamInfo(CamelCaseModel):
    """Team membership summary."""

    member_count: int = 0
    roles_breakdown: dict[str, int] = Field(default_factory=dict)


class ConversationStats(CamelCaseModel):
    """Recent conversation statistics."""

    last_24h_count: int = 0
    last_7d_count: int = 0
    status_breakdown: dict[str, int] = Field(default_factory=dict)


class IntegrationHealth(CamelCaseModel):
    """Integration connectivity summary."""

    shopify_connected: bool = False
    stripe_connected: bool = False
    nats_deployed: bool = False
    nats_connected: bool = False


class WidgetDeployment(CamelCaseModel):
    """Widget deployment status."""

    widget_key_present: bool = False
    origin_configured: bool = False


class RateLimitStatus(CamelCaseModel):
    """Rate limit status for the tenant."""

    current_rpm: int | None = None


class TenantDiagnosticSnapshot(CamelCaseModel):
    """Comprehensive tenant diagnostic snapshot for support."""

    # Basic info
    tenant_id: str
    status: str = "unknown"
    tier: str | None = None
    billing_channel: str | None = None
    created_at: str | None = None

    # Subsystem snapshots
    config_state: ConfigStateSummary = Field(default_factory=ConfigStateSummary)
    ai_config: AIConfigSummary = Field(default_factory=AIConfigSummary)
    knowledge_base: KnowledgeBaseStats = Field(default_factory=KnowledgeBaseStats)
    team: TeamInfo = Field(default_factory=TeamInfo)
    conversations: ConversationStats = Field(default_factory=ConversationStats)
    integrations: IntegrationHealth = Field(default_factory=IntegrationHealth)
    widget: WidgetDeployment = Field(default_factory=WidgetDeployment)
    rate_limit: RateLimitStatus = Field(default_factory=RateLimitStatus)

    # Timestamps
    last_activity_at: str | None = None

    # Errors encountered during snapshot collection
    collection_errors: list[str] = Field(default_factory=list)

    # Metadata
    generated_at: str = ""


class ErrorEntry(CamelCaseModel):
    """Single error entry from audit log."""

    event_type: str
    timestamp: str
    actor: str = "system"
    payload: dict[str, Any] = Field(default_factory=dict)
    conversation_id: str | None = None


class TenantErrorsResponse(CamelCaseModel):
    """Recent error entries for a tenant."""

    tenant_id: str
    entries: list[ErrorEntry] = Field(default_factory=list)
    total: int = 0
    generated_at: str = ""


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(
    prefix="/api/superadmin/diagnostics",
    tags=["Support Diagnostics"],
    dependencies=[Depends(require_platform_admin())],
)


# ---------------------------------------------------------------------------
# Helpers — each subsystem collector catches its own exceptions
# ---------------------------------------------------------------------------


async def _collect_config_state(
    tenant_id: str,
) -> tuple[ConfigStateSummary, AIConfigSummary | None]:
    """Collect configuration state and AI config summary."""
    from src.multi_tenant.repositories import PreferencesRepository

    prefs_repo = PreferencesRepository()
    active = await prefs_repo.get_active(tenant_id)

    config = ConfigStateSummary()
    ai_cfg = AIConfigSummary()

    if active:
        config.is_active = True
        config.is_configured = bool(active.get("brand_name"))
        config.active_version = active.get("version")
        config.activated_at = active.get("activated_at")

        ai_cfg.model = active.get("model")
        ai_cfg.brand_name_present = bool(active.get("brand_name"))
        ai_cfg.brand_voice_present = bool(active.get("brand_voice"))

    # Check for pending draft
    draft = await prefs_repo.get_draft(tenant_id)
    if draft:
        config.has_pending_changes = True

    return config, ai_cfg


async def _collect_kb_stats(tenant_id: str) -> KnowledgeBaseStats:
    """Collect knowledge base statistics."""
    from src.multi_tenant.repositories import KnowledgeBaseRepository

    kb_repo = KnowledgeBaseRepository()
    all_items = await kb_repo.query(
        tenant_id=tenant_id,
        query_text="SELECT c.id, c.is_active FROM c",
    )
    total = len(all_items)
    active = sum(1 for item in all_items if item.get("is_active"))
    return KnowledgeBaseStats(
        total_articles=total,
        active_count=active,
        draft_count=total - active,
    )


async def _collect_team_info(tenant_id: str) -> TeamInfo:
    """Collect team membership summary."""
    from src.multi_tenant.repositories import TeamMemberRepository

    team_repo = TeamMemberRepository()
    members = await team_repo.list_members(tenant_id=tenant_id, limit=200)
    roles: dict[str, int] = {}
    for m in members:
        role = m.get("role", "unknown")
        roles[role] = roles.get(role, 0) + 1
    return TeamInfo(member_count=len(members), roles_breakdown=roles)


async def _collect_conversation_stats(tenant_id: str) -> ConversationStats:
    """Collect recent conversation statistics."""
    from src.multi_tenant.repositories import ConversationRepository

    conv_repo = ConversationRepository()
    now = datetime.now(UTC)
    since_24h = (now - timedelta(hours=24)).isoformat()
    since_7d = (now - timedelta(days=7)).isoformat()

    count_24h = await conv_repo.query_count(
        tenant_id=tenant_id,
        query_text=(
            "SELECT VALUE COUNT(1) FROM c WHERE c.started_at >= @since"
        ),
        parameters=[{"name": "@since", "value": since_24h}],
    )
    count_7d = await conv_repo.query_count(
        tenant_id=tenant_id,
        query_text=(
            "SELECT VALUE COUNT(1) FROM c WHERE c.started_at >= @since"
        ),
        parameters=[{"name": "@since", "value": since_7d}],
    )

    # Status breakdown for last 7 days
    status_items = await conv_repo.query(
        tenant_id=tenant_id,
        query_text=(
            "SELECT c.status FROM c WHERE c.started_at >= @since"
        ),
        parameters=[{"name": "@since", "value": since_7d}],
    )
    status_breakdown: dict[str, int] = {}
    for item in status_items:
        s = item.get("status", "unknown")
        status_breakdown[s] = status_breakdown.get(s, 0) + 1

    return ConversationStats(
        last_24h_count=count_24h,
        last_7d_count=count_7d,
        status_breakdown=status_breakdown,
    )


async def _collect_integration_health(tenant_doc: dict[str, Any]) -> IntegrationHealth:
    """Derive integration health from the tenant document.

    NATS status is determined from the injected superadmin_api module-level
    ``_nats_mgr`` (set via ``configure_superadmin_services``).  The global
    ``get_nats_manager()`` singleton always creates a manager, so it cannot
    distinguish "not deployed" from "deployed but disconnected".
    """
    # Check the dependency-injected NATS manager.
    # NATS is decommissioned (USE_AGENT_CONTAINERS=false) — treat an
    # unconnected manager as "not deployed" rather than showing a false alarm.
    nats_connected = False
    try:
        from src.multi_tenant.superadmin_api import _nats_mgr
        if _nats_mgr is not None:
            nats_connected = bool(_nats_mgr.is_connected)
    except Exception:
        pass
    nats_deployed = nats_connected  # Only report as deployed if actually connected

    return IntegrationHealth(
        shopify_connected=bool(tenant_doc.get("shopify_shop_domain")),
        stripe_connected=bool(tenant_doc.get("stripe_customer_id")),
        nats_deployed=nats_deployed,
        nats_connected=nats_connected,
    )


async def _collect_widget_status(tenant_id: str) -> WidgetDeployment:
    """Collect widget deployment status from active preferences."""
    from src.multi_tenant.repositories import PreferencesRepository

    prefs_repo = PreferencesRepository()
    active = await prefs_repo.get_active(tenant_id)
    if not active:
        return WidgetDeployment()
    return WidgetDeployment(
        widget_key_present=bool(active.get("widget_key")),
        origin_configured=bool(active.get("allowed_origins")),
    )


async def _collect_last_activity(tenant_id: str) -> str | None:
    """Find the most recent conversation timestamp for the tenant."""
    from src.multi_tenant.repositories import ConversationRepository

    conv_repo = ConversationRepository()
    results = await conv_repo.query(
        tenant_id=tenant_id,
        query_text=(
            "SELECT c.started_at FROM c ORDER BY c.started_at DESC"
        ),
        max_items=1,
    )
    if results:
        return results[0].get("started_at")
    return None


# ---------------------------------------------------------------------------
# GET /{tenant_id} — Diagnostic Snapshot
# ---------------------------------------------------------------------------


@router.get(
    "/{tenant_id}",
    response_model=TenantDiagnosticSnapshot,
    summary="Comprehensive tenant diagnostic snapshot",
    description=(
        "Provider-only: returns a full diagnostic snapshot of a tenant "
        "including configuration state, knowledge base stats, team info, "
        "recent conversation metrics, integration health, and widget status. "
        "Subsystems that fail are reported in collection_errors with partial "
        "data returned."
    ),
    status_code=200,
)
async def get_tenant_diagnostic(
    tenant_id: str,

) -> TenantDiagnosticSnapshot:
    """Collect a comprehensive diagnostic snapshot for a single tenant.

    The *tenant_id* path parameter accepts **either** a tenant slug
    (e.g. ``test-customer-001``) **or** the merchant's registered email
    address.  When an ``@`` is detected the system resolves the email to
    a tenant ID via a cross-partition Cosmos query before proceeding.
    """
    from src.multi_tenant.repositories import TenantRepository

    tenant_repo = TenantRepository()

    # --- Resolve email → tenant_id when input contains '@' (SPEC-1783) ---
    resolved_tenant_id = tenant_id
    if "@" in tenant_id:
        try:
            tenant_doc = await tenant_repo.find_by_customer_email(tenant_id)
        except Exception:
            tenant_doc = None
        if tenant_doc is None:
            raise HTTPException(
                status_code=404,
                detail=f"No tenant found for email: {tenant_id}",
            )
        resolved_tenant_id = tenant_doc["id"]
    else:
        tenant_doc = None

    # --- Load the tenant document (required) ---
    if tenant_doc is None:
        try:
            tenant_doc = await tenant_repo.read(resolved_tenant_id, resolved_tenant_id)
        except Exception:
            raise HTTPException(
                status_code=404,
                detail=f"Tenant not found: {resolved_tenant_id}",
            )

    tenant_id = resolved_tenant_id

    now_iso = datetime.now(UTC).isoformat()
    errors: list[str] = []

    snapshot = TenantDiagnosticSnapshot(
        tenant_id=tenant_id,
        status=tenant_doc.get("status", "unknown"),
        tier=tenant_doc.get("tier"),
        billing_channel=tenant_doc.get("billing_channel"),
        created_at=tenant_doc.get("created_at"),
        generated_at=now_iso,
    )

    # --- Config state + AI config ---
    try:
        config_state, ai_cfg = await _collect_config_state(tenant_id)
        snapshot.config_state = config_state
        if ai_cfg:
            snapshot.ai_config = ai_cfg
    except Exception as exc:
        logger.warning("Diagnostics: config state collection failed for %s: %s", tenant_id, exc)
        errors.append(f"config_state: {exc}")

    # --- Knowledge base stats ---
    try:
        snapshot.knowledge_base = await _collect_kb_stats(tenant_id)
    except Exception as exc:
        logger.warning("Diagnostics: KB stats collection failed for %s: %s", tenant_id, exc)
        errors.append(f"knowledge_base: {exc}")

    # --- Team info ---
    try:
        snapshot.team = await _collect_team_info(tenant_id)
    except Exception as exc:
        logger.warning("Diagnostics: team info collection failed for %s: %s", tenant_id, exc)
        errors.append(f"team: {exc}")

    # --- Conversation stats ---
    try:
        snapshot.conversations = await _collect_conversation_stats(tenant_id)
    except Exception as exc:
        logger.warning("Diagnostics: conversation stats failed for %s: %s", tenant_id, exc)
        errors.append(f"conversations: {exc}")

    # --- Integration health ---
    try:
        snapshot.integrations = await _collect_integration_health(tenant_doc)
    except Exception as exc:
        logger.warning("Diagnostics: integration health failed for %s: %s", tenant_id, exc)
        errors.append(f"integrations: {exc}")

    # --- Widget status ---
    try:
        snapshot.widget = await _collect_widget_status(tenant_id)
    except Exception as exc:
        logger.warning("Diagnostics: widget status failed for %s: %s", tenant_id, exc)
        errors.append(f"widget: {exc}")

    # --- Last activity ---
    try:
        snapshot.last_activity_at = await _collect_last_activity(tenant_id)
    except Exception as exc:
        logger.warning("Diagnostics: last activity failed for %s: %s", tenant_id, exc)
        errors.append(f"last_activity: {exc}")

    snapshot.collection_errors = errors
    return snapshot


# ---------------------------------------------------------------------------
# GET /{tenant_id}/errors — Recent Errors
# ---------------------------------------------------------------------------


@router.get(
    "/{tenant_id}/errors",
    response_model=TenantErrorsResponse,
    summary="Recent errors for a tenant",
    description=(
        "Provider-only: returns recent error-level audit log entries for "
        "a specific tenant. Limited to the last 50 entries."
    ),
    status_code=200,
)
async def get_tenant_errors(
    tenant_id: str,

    limit: int = Query(50, ge=1, le=100, description="Max entries to return"),
) -> TenantErrorsResponse:
    """Return recent error-level audit entries for a tenant.

    Accepts tenant slug or email (same resolution as the snapshot endpoint).
    """
    from src.multi_tenant.repositories import AuditLogRepository, TenantRepository

    # Resolve email → tenant_id when input contains '@' (SPEC-1783)
    tenant_repo = TenantRepository()
    if "@" in tenant_id:
        try:
            tenant_doc = await tenant_repo.find_by_customer_email(tenant_id)
        except Exception:
            tenant_doc = None
        if tenant_doc is None:
            raise HTTPException(
                status_code=404,
                detail=f"No tenant found for email: {tenant_id}",
            )
        tenant_id = tenant_doc["id"]
    else:
        try:
            await tenant_repo.read(tenant_id, tenant_id)
        except Exception:
            raise HTTPException(
                status_code=404,
                detail=f"Tenant not found: {tenant_id}",
            )

    audit_repo = AuditLogRepository()
    now_iso = datetime.now(UTC).isoformat()

    # Query for error-level events (event types containing "error" or "fail")
    # Use cross-partition query since audit_log is partitioned by time_partition
    query_text = (
        "SELECT * FROM c "
        "WHERE c.tenant_id = @tenant_id "
        "AND (CONTAINS(c.event_type, 'error') "
        "     OR CONTAINS(c.event_type, 'fail') "
        "     OR CONTAINS(c.event_type, 'violation') "
        "     OR (IS_DEFINED(c.payload.severity) "
        "         AND c.payload.severity = 'error')) "
        "ORDER BY c.timestamp DESC "
        f"OFFSET 0 LIMIT {limit}"
    )
    params = [{"name": "@tenant_id", "value": tenant_id}]

    items: list[dict[str, Any]] = []
    async for item in audit_repo._container.query_items(
        query=query_text,
        parameters=params,
        max_item_count=limit,
    ):
        items.append(item)

    entries = [
        ErrorEntry(
            event_type=item.get("event_type", "unknown"),
            timestamp=item.get("timestamp", ""),
            actor=item.get("actor", "system"),
            payload=item.get("payload", {}),
            conversation_id=item.get("conversation_id"),
        )
        for item in items
    ]

    return TenantErrorsResponse(
        tenant_id=tenant_id,
        entries=entries,
        total=len(entries),
        generated_at=now_iso,
    )
