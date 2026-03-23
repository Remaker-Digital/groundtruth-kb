"""Superadmin API -- shared state, router, and configuration functions.

This module holds module-level service references, the shared router, and
configure_*() functions. Domain endpoints live in sibling modules:
  _tenants.py       -- Tenant directory, CRUD, tier override, expiry
  _dashboard.py     -- Dashboard, billing, SLA, queues, compliance, secrets, integrations
  _operations.py    -- Incidents, alerts, MFA, cost analytics, abuse detection
  _copilot.py       -- Co-Pilot knowledge management, document CRUD, ingestion, config
  _platform.py      -- Pipeline observatory, service messages, platform admin management
  _entitlements.py  -- Entitlement CRUD, feature flags (SPEC-1816, SPEC-1824)
  _blocklists.py    -- Allow/block lists, maintenance mode (SPEC-1820, SPEC-1829)
  _rate_limits.py   -- Rate limit config, retry/back-off config (SPEC-1819, SPEC-1821)
  _alerts.py        -- Alert thresholds, notification channels (SPEC-1822, SPEC-1823)
  _diagnostics.py   -- Test pipeline trigger, diagnostic export (SPEC-1826, SPEC-1827)
  _deployments.py   -- Self-service deployment pipeline (SPEC-1825)

All domain modules import `router` from this module and register their endpoints
on it. The router is a single shared object across all modules.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends

from src.multi_tenant.middleware import require_platform_admin
from src.multi_tenant.repository import (
    AuditLogRepository,
    ConversationRepository,
    PreferencesRepository,
    TenantRepository,
    UsageRepository,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Module-level service references (set via configure function)
# ---------------------------------------------------------------------------

_tenant_repo: TenantRepository | None = None
_audit_repo: AuditLogRepository | None = None
_conv_repo: ConversationRepository | None = None
_usage_repo: UsageRepository | None = None
_prefs_repo: PreferencesRepository | None = None
_nats_mgr: Any = None
_secret_service: Any = None
_incident_repo: Any = None
_alert_rule_repo: Any = None
_alert_history_repo: Any = None
_platform_admin_repo: Any = None


def configure_superadmin_services(
    tenant_repo: TenantRepository,
    audit_repo: AuditLogRepository,
    conv_repo: ConversationRepository | None = None,
    usage_repo: UsageRepository | None = None,
    prefs_repo: PreferencesRepository | None = None,
    nats_mgr: Any = None,
    secret_service: Any = None,
    incident_repo: Any = None,
    alert_rule_repo: Any = None,
    alert_history_repo: Any = None,
    platform_admin_repo: Any = None,
) -> None:
    """Wire repositories into module-level variables.

    Called during application startup from main.py.
    """
    global _tenant_repo, _audit_repo, _conv_repo, _usage_repo, _prefs_repo
    global _nats_mgr, _secret_service
    global _incident_repo, _alert_rule_repo, _alert_history_repo
    global _platform_admin_repo
    _tenant_repo = tenant_repo
    _audit_repo = audit_repo
    _conv_repo = conv_repo
    _usage_repo = usage_repo
    _prefs_repo = prefs_repo
    _nats_mgr = nats_mgr
    _secret_service = secret_service
    _incident_repo = incident_repo
    _alert_rule_repo = alert_rule_repo
    _alert_history_repo = alert_history_repo
    _platform_admin_repo = platform_admin_repo
    logger.info("Superadmin API services configured")


# ---------------------------------------------------------------------------
# Co-Pilot Knowledge Management state
# ---------------------------------------------------------------------------

_admin_doc_repo: Any = None


def configure_copilot_knowledge_service(
    admin_doc_repo: Any = None,
) -> None:
    """Wire Co-Pilot knowledge repository. Called during startup."""
    global _admin_doc_repo
    _admin_doc_repo = admin_doc_repo
    logger.info("Co-Pilot Knowledge services configured")


# ---------------------------------------------------------------------------
# Pipeline Observatory state
# ---------------------------------------------------------------------------

_pipeline_metrics_configured = False


def configure_pipeline_observatory(enabled: bool = True) -> None:
    """Enable pipeline observatory endpoints."""
    global _pipeline_metrics_configured
    _pipeline_metrics_configured = enabled


# ---------------------------------------------------------------------------
# Router (shared across all domain modules)
# ---------------------------------------------------------------------------

router = APIRouter(
    prefix="/api/superadmin",
    tags=["superadmin"],
    dependencies=[Depends(require_platform_admin())],
)
