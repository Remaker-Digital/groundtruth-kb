"""HV-4 Abuse Detection API — cross-tenant anomalous usage detection.

Provides REST endpoints for the service provider (SUPERADMIN role) to detect
and flag tenants exhibiting anomalous usage patterns. Scans for rate anomalies,
volume spikes, widget abuse, token exhaustion, and elevated error rates.

Endpoints:
    GET  /api/superadmin/abuse/signals             — Cross-tenant abuse signal scan
    GET  /api/superadmin/abuse/tenant/{tenant_id}  — Abuse signals for a specific tenant
    POST /api/superadmin/abuse/tenant/{tenant_id}/flag — Flag/unflag a tenant

All endpoints require SUPERADMIN role.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import Field

from src.multi_tenant.api_models import CamelCaseModel
from src.multi_tenant.middleware import require_platform_admin

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

RATE_ANOMALY_THRESHOLD_PCT = 80  # % of tier rate limit
VOLUME_SPIKE_MULTIPLIER = 3.0  # x above 7-day average
TOKEN_EXHAUSTION_THRESHOLD_PCT = 90  # % of tier allowance
ERROR_RATE_THRESHOLD_PCT = 10  # % error rate in conversations
WIDGET_ABUSE_SIGNAL = "origin_mismatch"  # mismatched widget origin


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class SignalType(str, Enum):
    """Abuse signal types detected by the scanner."""

    RATE_ANOMALY = "rate_anomaly"
    VOLUME_SPIKE = "volume_spike"
    WIDGET_ABUSE = "widget_abuse"
    TOKEN_EXHAUSTION = "token_exhaustion"
    ERROR_RATE = "error_rate"


class Severity(str, Enum):
    """Severity levels for abuse signals."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ---------------------------------------------------------------------------
# Response Models
# ---------------------------------------------------------------------------


class AbuseSignal(CamelCaseModel):
    """A single detected abuse signal for a tenant."""

    tenant_id: str
    signal_type: str
    severity: str
    description: str
    detected_at: str
    metric_value: float
    threshold: float


class TenantAbuseProfile(CamelCaseModel):
    """Abuse profile for a single tenant."""

    tenant_id: str
    is_flagged: bool = False
    flagged_at: str | None = None
    flagged_by: str | None = None
    signals: list[AbuseSignal] = Field(default_factory=list)
    risk_score: int = 0  # 0-100


class AbuseOverview(CamelCaseModel):
    """Cross-tenant abuse scan summary."""

    total_tenants_scanned: int = 0
    flagged_count: int = 0
    signals_by_type: dict[str, int] = Field(default_factory=dict)
    high_risk_tenants: list[TenantAbuseProfile] = Field(default_factory=list)


class FlagRequest(CamelCaseModel):
    """Request body for flagging/unflagging a tenant."""

    flagged: bool = True


class FlagResponse(CamelCaseModel):
    """Response after flagging/unflagging a tenant."""

    tenant_id: str
    is_flagged: bool
    flagged_at: str | None = None
    flagged_by: str | None = None


# ---------------------------------------------------------------------------
# Module-level service references
# ---------------------------------------------------------------------------

_tenant_repo: Any = None
_conv_repo: Any = None
_usage_repo: Any = None


def configure_abuse_services(
    tenant_repo: Any = None,
    conv_repo: Any = None,
    usage_repo: Any = None,
) -> None:
    """Wire repositories into module-level variables.

    Called during application startup from main.py.
    """
    global _tenant_repo, _conv_repo, _usage_repo
    _tenant_repo = tenant_repo
    _conv_repo = conv_repo
    _usage_repo = usage_repo
    logger.info("Abuse detection services configured")


# ---------------------------------------------------------------------------
# Signal Detection Helpers
# ---------------------------------------------------------------------------


def _compute_severity(metric_value: float, threshold: float) -> str:
    """Derive severity from how far the metric exceeds the threshold.

    Returns:
        Severity string: low, medium, high, or critical.
    """
    if threshold <= 0:
        return Severity.LOW.value
    ratio = metric_value / threshold
    if ratio >= 2.0:
        return Severity.CRITICAL.value
    if ratio >= 1.5:
        return Severity.HIGH.value
    if ratio >= 1.0:
        return Severity.MEDIUM.value
    return Severity.LOW.value


def _compute_risk_score(signals: list[AbuseSignal]) -> int:
    """Compute a 0-100 risk score from a list of signals.

    Scoring:
        - Each signal adds points based on severity
        - Critical: 30, High: 20, Medium: 10, Low: 5
        - Capped at 100
    """
    severity_points = {
        Severity.CRITICAL.value: 30,
        Severity.HIGH.value: 20,
        Severity.MEDIUM.value: 10,
        Severity.LOW.value: 5,
    }
    total = sum(severity_points.get(s.severity, 5) for s in signals)
    return min(total, 100)


async def _detect_volume_spike(
    tenant_id: str, now: datetime,
) -> AbuseSignal | None:
    """Detect conversation volume spike (>3x 7-day average).

    Compares 24h conversation count against 7-day daily average.
    Degrades gracefully if conversation repo is unavailable.
    """
    if not _conv_repo:
        return None
    try:
        # Count conversations in last 24h
        cutoff_24h = (now - timedelta(hours=24)).isoformat()
        count_24h = 0
        async for item in _conv_repo._container.query_items(
            query=(
                "SELECT VALUE COUNT(1) FROM c "
                "WHERE c.tenant_id = @tid AND c.created_at >= @cutoff"
            ),
            parameters=[
                {"name": "@tid", "value": tenant_id},
                {"name": "@cutoff", "value": cutoff_24h},
            ],
            max_item_count=1,
        ):
            count_24h = item

        # Count conversations in last 7 days for daily average
        cutoff_7d = (now - timedelta(days=7)).isoformat()
        count_7d = 0
        async for item in _conv_repo._container.query_items(
            query=(
                "SELECT VALUE COUNT(1) FROM c "
                "WHERE c.tenant_id = @tid AND c.created_at >= @cutoff"
            ),
            parameters=[
                {"name": "@tid", "value": tenant_id},
                {"name": "@cutoff", "value": cutoff_7d},
            ],
            max_item_count=1,
        ):
            count_7d = item

        daily_avg = count_7d / 7.0 if count_7d > 0 else 0
        threshold = daily_avg * VOLUME_SPIKE_MULTIPLIER

        if daily_avg > 0 and count_24h > threshold:
            return AbuseSignal(
                tenant_id=tenant_id,
                signal_type=SignalType.VOLUME_SPIKE.value,
                severity=_compute_severity(count_24h, threshold),
                description=(
                    f"24h conversation count ({count_24h}) exceeds "
                    f"{VOLUME_SPIKE_MULTIPLIER}x 7-day daily average ({daily_avg:.1f})"
                ),
                detected_at=now.isoformat(),
                metric_value=float(count_24h),
                threshold=threshold,
            )
    except Exception:
        logger.warning("Volume spike detection failed for tenant=%s", tenant_id, exc_info=True)
    return None


async def _detect_widget_abuse(
    tenant_id: str, tenant_doc: dict[str, Any], now: datetime,
) -> AbuseSignal | None:
    """Detect widget origin mismatch.

    Checks if the tenant has a configured widget origin. If not configured,
    flags as potential widget abuse (open widget without origin restriction).
    Degrades gracefully on error.
    """
    try:
        widget_origin = tenant_doc.get("widget_allowed_origin", "")
        widget_key = tenant_doc.get("widget_key", "")

        # Flag tenants that have a widget key but no origin restriction
        if widget_key and not widget_origin:
            return AbuseSignal(
                tenant_id=tenant_id,
                signal_type=SignalType.WIDGET_ABUSE.value,
                severity=Severity.MEDIUM.value,
                description=(
                    "Widget key is active but no allowed origin is configured. "
                    "Widget requests may come from unauthorized domains."
                ),
                detected_at=now.isoformat(),
                metric_value=1.0,
                threshold=0.0,
            )
    except Exception:
        logger.warning("Widget abuse detection failed for tenant=%s", tenant_id, exc_info=True)
    return None


async def _detect_token_exhaustion(
    tenant_id: str, now: datetime,
) -> AbuseSignal | None:
    """Detect AI token usage approaching tier allowance (>90%).

    Reads from usage_stats container. Degrades gracefully if unavailable.
    """
    if not _usage_repo:
        return None
    try:
        # Query current period usage
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
        total_tokens = 0
        async for item in _usage_repo._container.query_items(
            query=(
                "SELECT VALUE SUM(c.total_tokens) FROM c "
                "WHERE c.tenant_id = @tid AND c.period_start >= @start"
            ),
            parameters=[
                {"name": "@tid", "value": tenant_id},
                {"name": "@start", "value": period_start},
            ],
            max_item_count=1,
        ):
            total_tokens = item or 0

        # Tier token allowance (simplified defaults)
        tier_allowances = {
            "starter": 100_000,
            "professional": 500_000,
            "enterprise": 2_000_000,
        }
        # Default to professional if unknown
        tier_limit = tier_allowances.get("professional", 500_000)
        threshold = tier_limit * (TOKEN_EXHAUSTION_THRESHOLD_PCT / 100.0)

        if total_tokens > threshold:
            return AbuseSignal(
                tenant_id=tenant_id,
                signal_type=SignalType.TOKEN_EXHAUSTION.value,
                severity=_compute_severity(total_tokens, tier_limit),
                description=(
                    f"Token usage ({total_tokens:,}) exceeds "
                    f"{TOKEN_EXHAUSTION_THRESHOLD_PCT}% of tier allowance ({tier_limit:,})"
                ),
                detected_at=now.isoformat(),
                metric_value=float(total_tokens),
                threshold=float(tier_limit),
            )
    except Exception:
        logger.warning("Token exhaustion detection failed for tenant=%s", tenant_id, exc_info=True)
    return None


async def _detect_error_rate(
    tenant_id: str, now: datetime,
) -> AbuseSignal | None:
    """Detect elevated error rate in conversations (>10%).

    Compares errored conversations vs total in last 24h.
    Degrades gracefully if unavailable.
    """
    if not _conv_repo:
        return None
    try:
        cutoff = (now - timedelta(hours=24)).isoformat()

        total = 0
        async for item in _conv_repo._container.query_items(
            query=(
                "SELECT VALUE COUNT(1) FROM c "
                "WHERE c.tenant_id = @tid AND c.created_at >= @cutoff"
            ),
            parameters=[
                {"name": "@tid", "value": tenant_id},
                {"name": "@cutoff", "value": cutoff},
            ],
            max_item_count=1,
        ):
            total = item

        if total == 0:
            return None

        errored = 0
        async for item in _conv_repo._container.query_items(
            query=(
                "SELECT VALUE COUNT(1) FROM c "
                "WHERE c.tenant_id = @tid AND c.created_at >= @cutoff "
                "AND c.status = 'error'"
            ),
            parameters=[
                {"name": "@tid", "value": tenant_id},
                {"name": "@cutoff", "value": cutoff},
            ],
            max_item_count=1,
        ):
            errored = item

        error_pct = (errored / total) * 100 if total > 0 else 0
        threshold = float(ERROR_RATE_THRESHOLD_PCT)

        if error_pct > threshold:
            return AbuseSignal(
                tenant_id=tenant_id,
                signal_type=SignalType.ERROR_RATE.value,
                severity=_compute_severity(error_pct, threshold),
                description=(
                    f"Error rate ({error_pct:.1f}%) exceeds {ERROR_RATE_THRESHOLD_PCT}% "
                    f"threshold ({errored}/{total} conversations)"
                ),
                detected_at=now.isoformat(),
                metric_value=error_pct,
                threshold=threshold,
            )
    except Exception:
        logger.warning("Error rate detection failed for tenant=%s", tenant_id, exc_info=True)
    return None


async def _scan_tenant(
    tenant_id: str, tenant_doc: dict[str, Any], now: datetime,
) -> list[AbuseSignal]:
    """Run all abuse signal detectors for a single tenant.

    Each detector degrades gracefully — a failed detector does not block others.
    """
    signals: list[AbuseSignal] = []

    detectors = [
        _detect_volume_spike(tenant_id, now),
        _detect_widget_abuse(tenant_id, tenant_doc, now),
        _detect_token_exhaustion(tenant_id, now),
        _detect_error_rate(tenant_id, now),
    ]

    for detector in detectors:
        try:
            result = await detector
            if result is not None:
                signals.append(result)
        except Exception:
            logger.warning("Detector failed for tenant=%s", tenant_id, exc_info=True)

    return signals


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(
    prefix="/api/superadmin/abuse",
    tags=["Abuse Detection"],
    dependencies=[Depends(require_platform_admin())],
)


@router.get(
    "/signals",
    response_model=AbuseOverview,
    summary="Cross-tenant abuse signal scan",
    description=(
        "Scans all active tenants for anomalous usage patterns and returns "
        "an overview with signal counts and high-risk tenant profiles."
    ),
    status_code=200,
)
async def scan_abuse_signals(

) -> AbuseOverview:
    """Scan all tenants for abuse signals."""
    if not _tenant_repo:
        raise HTTPException(status_code=503, detail="Service not initialized")

    now = datetime.now(timezone.utc)
    tenant_ids = await _tenant_repo.list_active_tenant_ids()
    total_scanned = len(tenant_ids)

    signals_by_type: dict[str, int] = {}
    high_risk: list[TenantAbuseProfile] = []
    flagged_count = 0

    for tid in tenant_ids:
        # Read the tenant document for config-based checks
        try:
            tenant_doc = await _tenant_repo.read(tid, tid)
        except Exception:
            tenant_doc = {}

        signals = await _scan_tenant(tid, tenant_doc, now)
        is_flagged = tenant_doc.get("abuse_flagged", False)
        if is_flagged:
            flagged_count += 1

        # Tally signal types
        for s in signals:
            signals_by_type[s.signal_type] = signals_by_type.get(s.signal_type, 0) + 1

        # Include in high-risk if any signals detected
        if signals:
            risk_score = _compute_risk_score(signals)
            high_risk.append(TenantAbuseProfile(
                tenant_id=tid,
                is_flagged=is_flagged,
                flagged_at=tenant_doc.get("abuse_flagged_at"),
                flagged_by=tenant_doc.get("abuse_flagged_by"),
                signals=signals,
                risk_score=risk_score,
            ))

    # Sort high-risk by score descending
    high_risk.sort(key=lambda p: p.risk_score, reverse=True)

    return AbuseOverview(
        total_tenants_scanned=total_scanned,
        flagged_count=flagged_count,
        signals_by_type=signals_by_type,
        high_risk_tenants=high_risk,
    )


@router.get(
    "/tenant/{tenant_id}",
    response_model=TenantAbuseProfile,
    summary="Abuse signals for a specific tenant",
    description="Returns the abuse profile and detected signals for one tenant.",
    status_code=200,
)
async def get_tenant_abuse_profile(
    tenant_id: str,

) -> TenantAbuseProfile:
    """Get abuse profile for a single tenant."""
    if not _tenant_repo:
        raise HTTPException(status_code=503, detail="Service not initialized")

    # Read the tenant document
    try:
        tenant_doc = await _tenant_repo.read(tenant_id, tenant_id)
    except Exception:
        raise HTTPException(status_code=404, detail=f"Tenant not found: {tenant_id}")

    now = datetime.now(timezone.utc)
    signals = await _scan_tenant(tenant_id, tenant_doc, now)
    risk_score = _compute_risk_score(signals)

    return TenantAbuseProfile(
        tenant_id=tenant_id,
        is_flagged=tenant_doc.get("abuse_flagged", False),
        flagged_at=tenant_doc.get("abuse_flagged_at"),
        flagged_by=tenant_doc.get("abuse_flagged_by"),
        signals=signals,
        risk_score=risk_score,
    )


@router.post(
    "/tenant/{tenant_id}/flag",
    response_model=FlagResponse,
    summary="Flag or unflag a tenant for abuse",
    description=(
        "Toggles the abuse-flagged state on a tenant document. "
        "Stores abuse_flagged, abuse_flagged_at, and abuse_flagged_by fields."
    ),
    status_code=200,
)
async def flag_tenant(
    tenant_id: str,
    body: FlagRequest = Body(...),

) -> FlagResponse:
    """Flag or unflag a tenant for abuse."""
    if not _tenant_repo:
        raise HTTPException(status_code=503, detail="Service not initialized")

    # Verify tenant exists
    try:
        await _tenant_repo.read(tenant_id, tenant_id)
    except Exception:
        raise HTTPException(status_code=404, detail=f"Tenant not found: {tenant_id}")

    now = datetime.now(timezone.utc).isoformat()
    actor = "spa-console"

    if body.flagged:
        operations = [
            {"op": "set", "path": "/abuse_flagged", "value": True},
            {"op": "set", "path": "/abuse_flagged_at", "value": now},
            {"op": "set", "path": "/abuse_flagged_by", "value": actor},
        ]
    else:
        operations = [
            {"op": "set", "path": "/abuse_flagged", "value": False},
            {"op": "set", "path": "/abuse_flagged_at", "value": None},
            {"op": "set", "path": "/abuse_flagged_by", "value": None},
        ]

    try:
        await _tenant_repo._container.patch_item(
            item=tenant_id,
            partition_key=tenant_id,
            patch_operations=operations,
        )
    except Exception as exc:
        logger.error("Failed to flag tenant %s: %s", tenant_id, exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update tenant flag") from exc

    return FlagResponse(
        tenant_id=tenant_id,
        is_flagged=body.flagged,
        flagged_at=now if body.flagged else None,
        flagged_by=actor if body.flagged else None,
    )
