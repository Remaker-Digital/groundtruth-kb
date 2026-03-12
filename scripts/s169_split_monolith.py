"""S169: Split superadmin_api/_monolith.py into domain sub-modules.

WI-1155 / SPEC-1694 completion.
Moves endpoints, models, and helpers from the 5,085-line monolith into
5 domain modules while keeping shared state and router in _monolith.py.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
import os
import sys

SRC = os.path.join("src", "multi_tenant", "superadmin_api", "_monolith.py")
PKG = os.path.join("src", "multi_tenant", "superadmin_api")

with open(SRC, "r", encoding="utf-8") as f:
    all_lines = f.readlines()

total = len(all_lines)
print(f"Source: {total} lines")


def get_lines(start: int, end: int) -> str:
    """Get lines start..end (1-indexed inclusive)."""
    return "".join(all_lines[start - 1 : end])


# ═══════════════════════════════════════════════════════════════════
# _tenants.py
# ═══════════════════════════════════════════════════════════════════

TENANTS_HEADER = '''\
"""Superadmin API -- Tenant directory, CRUD, tier override, expiry.

Domain sub-module extracted from the superadmin_api monolith.
Endpoints are registered on the shared router from _monolith.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import Body, Depends, HTTPException, Query
from pydantic import Field, field_validator

from src.multi_tenant.api_models import CamelCaseModel
from src.multi_tenant.auth import TenantContext
from src.multi_tenant.cosmos_schema import AuditEventType, TenantTier
from src.multi_tenant.middleware import get_tenant_context

from src.multi_tenant.superadmin_api._monolith import (
    router,
    _tenant_repo,
    _audit_repo,
    _prefs_repo,
)

logger = logging.getLogger(__name__)


'''

tenants = TENANTS_HEADER
tenants += get_lines(133, 168)   # TenantSummaryItem, TenantDirectoryResponse, TenantDistributionSummary
tenants += "\n"
tenants += get_lines(527, 536)   # TierOverrideResponse + VALID_TIERS
tenants += "\n"
tenants += get_lines(606, 665)   # CreateTenantRequest, CreateTenantResponse
tenants += "\n"
tenants += get_lines(820, 827)   # ResendWelcomeEmailResponse
tenants += "\n"
tenants += get_lines(940, 965)   # SetExpiryRequest, SetExpiryResponse
tenants += "\n"
# Endpoints (section headers + endpoint code)
tenants += get_lines(401, 1071)  # All tenant endpoints

path = os.path.join(PKG, "_tenants.py")
with open(path, "w", encoding="utf-8") as f:
    f.write(tenants)
print(f"_tenants.py: {len(tenants.splitlines())} lines")


# ═══════════════════════════════════════════════════════════════════
# _dashboard.py
# ═══════════════════════════════════════════════════════════════════

DASHBOARD_HEADER = '''\
"""Superadmin API -- Dashboard, billing, SLA, queues, compliance, secrets, integrations.

Domain sub-module extracted from the superadmin_api monolith.
Endpoints are registered on the shared router from _monolith.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException, Query
from pydantic import Field

from src.multi_tenant.api_models import CamelCaseModel

from src.multi_tenant.superadmin_api._monolith import (
    router,
    _tenant_repo,
    _audit_repo,
    _conv_repo,
    _usage_repo,
    _nats_mgr,
    _secret_service,
)

logger = logging.getLogger(__name__)


'''

dashboard = DASHBOARD_HEADER
dashboard += get_lines(170, 388)   # All dashboard models (Deployment, Dashboard, Billing, SLA, Queue, Compliance, Secret, Integration)
dashboard += "\n"
dashboard += get_lines(1074, 1933) # All dashboard endpoints

path = os.path.join(PKG, "_dashboard.py")
with open(path, "w", encoding="utf-8") as f:
    f.write(dashboard)
print(f"_dashboard.py: {len(dashboard.splitlines())} lines")


# ═══════════════════════════════════════════════════════════════════
# _operations.py
# ═══════════════════════════════════════════════════════════════════

OPERATIONS_HEADER = '''\
"""Superadmin API -- Incidents, alerts, MFA, cost analytics, abuse detection.

Domain sub-module extracted from the superadmin_api monolith.
Endpoints are registered on the shared router from _monolith.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import Body, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from src.multi_tenant.api_models import CamelCaseModel
from src.multi_tenant.auth import TenantContext
from src.multi_tenant.cosmos_schema import AuditEventType
from src.multi_tenant.middleware import get_tenant_context

from src.multi_tenant.superadmin_api._monolith import (
    router,
    _tenant_repo,
    _audit_repo,
    _conv_repo,
    _usage_repo,
    _incident_repo,
    _alert_rule_repo,
    _alert_history_repo,
    _platform_admin_repo,
)

logger = logging.getLogger(__name__)


'''

operations = OPERATIONS_HEADER
# Incident + alert + MFA models (lines 1936-2285)
operations += get_lines(1936, 2285)
operations += "\n"
# Incident helper + incident endpoints (lines 1989-2150... but models already included)
# Actually, the helpers and endpoints start after models.
# _incident_to_model is at line 1994, but that's within the model section already copied.
# Let me be more careful: models end at 2285 (MfaDisableRequest).
# After that: _rule_to_model (2290), _history_to_model (2312)
# Then alert endpoints (2331-2522), then MFA section (2523-2749)
# Then cost/abuse (2750-3173)

# But wait — _incident_to_model at line 1994 is WITHIN the range 1936-2285,
# and the incident endpoints 2020-2150 are also within that range.
# So lines 1936-2285 already contain: models + _incident_to_model + incident endpoints.

# Lines after 2285:
# 2287-2330: _rule_to_model, _history_to_model helpers
operations += get_lines(2287, 2330)
operations += "\n"
# 2331-2522: Alert endpoints
operations += get_lines(2331, 2522)
operations += "\n"
# 2523-2749: MFA helpers + MFA endpoints
operations += get_lines(2523, 2749)
operations += "\n"
# 2750-3173: Cost/Abuse models + endpoints
operations += get_lines(2750, 3173)

path = os.path.join(PKG, "_operations.py")
with open(path, "w", encoding="utf-8") as f:
    f.write(operations)
print(f"_operations.py: {len(operations.splitlines())} lines")


# ═══════════════════════════════════════════════════════════════════
# _copilot.py
# ═══════════════════════════════════════════════════════════════════

COPILOT_HEADER = '''\
"""Superadmin API -- Co-Pilot knowledge management, document CRUD, ingestion, config.

Domain sub-module extracted from the superadmin_api monolith.
Endpoints are registered on the shared router from _monolith.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any

from fastapi import Body, HTTPException, Query
from pydantic import BaseModel, Field

from src.multi_tenant.api_models import CamelCaseModel

from src.multi_tenant.superadmin_api._monolith import (
    router,
    _admin_doc_repo,
)

logger = logging.getLogger(__name__)


'''

copilot = COPILOT_HEADER
# Models (3191-3290) + endpoints + helpers + config (3292-4120)
# Skip configure_copilot_knowledge_service (3182-3188) — stays in _monolith
copilot += get_lines(3191, 4120)

path = os.path.join(PKG, "_copilot.py")
with open(path, "w", encoding="utf-8") as f:
    f.write(copilot)
print(f"_copilot.py: {len(copilot.splitlines())} lines")


# ═══════════════════════════════════════════════════════════════════
# _platform.py
# ═══════════════════════════════════════════════════════════════════

PLATFORM_HEADER = '''\
"""Superadmin API -- Pipeline observatory, service messages, platform admin management.

Domain sub-module extracted from the superadmin_api monolith.
Endpoints are registered on the shared router from _monolith.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any

from fastapi import Body, Depends, HTTPException, Query
from pydantic import Field

from src.multi_tenant.api_models import CamelCaseModel
from src.multi_tenant.auth import TenantContext
from src.multi_tenant.cosmos_schema import AuditEventType
from src.multi_tenant.middleware import get_tenant_context

from src.multi_tenant.superadmin_api._monolith import (
    router,
    _tenant_repo,
    _audit_repo,
    _platform_admin_repo,
    _pipeline_metrics_configured,
)

logger = logging.getLogger(__name__)


'''

platform = PLATFORM_HEADER
# Everything from Pipeline Observatory section onwards
# Skip configure_pipeline_observatory (4252-4255) — stays in _monolith
# Pipeline models: 4123-4248
# Pipeline endpoints: 4258-4387
# Service messages: 4388-4607
# Platform admin: 4608-5085
platform += get_lines(4123, 4248)  # Pipeline section header + models
platform += "\n"
# configure_pipeline_observatory is at 4252-4255, skip it
# Pipeline endpoints start at 4258
platform += get_lines(4258, 5085)  # All pipeline + service msg + platform admin endpoints

path = os.path.join(PKG, "_platform.py")
with open(path, "w", encoding="utf-8") as f:
    f.write(platform)
print(f"_platform.py: {len(platform.splitlines())} lines")


# ═══════════════════════════════════════════════════════════════════
# _monolith.py (THIN STATE MODULE)
# ═══════════════════════════════════════════════════════════════════

MONOLITH_NEW = '''\
"""Superadmin API -- shared state, router, and configuration functions.

This module holds module-level service references, the shared router, and
configure_*() functions. Domain endpoints live in sibling modules:
  _tenants.py    -- Tenant directory, CRUD, tier override, expiry
  _dashboard.py  -- Dashboard, billing, SLA, queues, compliance, secrets, integrations
  _operations.py -- Incidents, alerts, MFA, cost analytics, abuse detection
  _copilot.py    -- Co-Pilot knowledge management, document CRUD, ingestion, config
  _platform.py   -- Pipeline observatory, service messages, platform admin management

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
'''

path = os.path.join(PKG, "_monolith.py")
with open(path, "w", encoding="utf-8") as f:
    f.write(MONOLITH_NEW)
print(f"_monolith.py: {len(MONOLITH_NEW.splitlines())} lines (was {total})")


# ═══════════════════════════════════════════════════════════════════
# __init__.py (BARREL IMPORTS)
# ═══════════════════════════════════════════════════════════════════

INIT_NEW = '''\
"""Superadmin Provider Operations API -- package init.

Re-exports all public names from sub-modules for backward compatibility.
All existing imports (from src.multi_tenant.superadmin_api import X) continue to work.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
# Shared state, router, and configuration functions
from src.multi_tenant.superadmin_api._monolith import (  # noqa: F401
    router,
    configure_superadmin_services,
    configure_copilot_knowledge_service,
    configure_pipeline_observatory,
    # Private variables (re-exported for test patching via _monolith)
    _tenant_repo,
    _audit_repo,
    _conv_repo,
    _usage_repo,
    _prefs_repo,
    _nats_mgr,
    _secret_service,
    _incident_repo,
    _alert_rule_repo,
    _alert_history_repo,
    _platform_admin_repo,
    _admin_doc_repo,
    _pipeline_metrics_configured,
)

# Domain sub-modules -- import triggers endpoint registration on shared router.
# Star imports re-export all public names (models, endpoint functions).
from src.multi_tenant.superadmin_api._tenants import *  # noqa: F401,F403
from src.multi_tenant.superadmin_api._dashboard import *  # noqa: F401,F403
from src.multi_tenant.superadmin_api._operations import *  # noqa: F401,F403
from src.multi_tenant.superadmin_api._copilot import *  # noqa: F401,F403
from src.multi_tenant.superadmin_api._platform import *  # noqa: F401,F403

# Private helpers re-exported for backward compatibility (test patching)
from src.multi_tenant.superadmin_api._operations import (  # noqa: F401
    _incident_to_model,
    _rule_to_model,
    _history_to_model,
    _get_mfa_svc,
    _get_team_member,
)
from src.multi_tenant.superadmin_api._copilot import (  # noqa: F401
    _infer_category_from_filename,
    _generate_embedding,
    _get_copilot_config,
    _save_copilot_config,
)
from src.multi_tenant.superadmin_api._platform import (  # noqa: F401
    _resolve_service_message_recipients,
)


__all__ = [
    "router",
    "configure_superadmin_services",
    "configure_copilot_knowledge_service",
    "configure_pipeline_observatory",
]
'''

path = os.path.join(PKG, "__init__.py")
with open(path, "w", encoding="utf-8") as f:
    f.write(INIT_NEW)
print(f"__init__.py: {len(INIT_NEW.splitlines())} lines")

print("\n=== Split complete ===")
print("All 7 files written. Run tests to verify.")
