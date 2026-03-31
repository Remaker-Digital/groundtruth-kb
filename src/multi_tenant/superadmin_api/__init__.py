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
from src.multi_tenant.superadmin_api._entitlements import *  # noqa: F401,F403
from src.multi_tenant.superadmin_api._blocklists import *  # noqa: F401,F403
from src.multi_tenant.superadmin_api._rate_limits import *  # noqa: F401,F403
from src.multi_tenant.superadmin_api._alerts import *  # noqa: F401,F403
from src.multi_tenant.superadmin_api._diagnostics import *  # noqa: F401,F403
from src.multi_tenant.superadmin_api._feedback import *  # noqa: F401,F403
from src.multi_tenant.superadmin_api._quality import *  # noqa: F401,F403
from src.multi_tenant.superadmin_api._deployments import *  # noqa: F401,F403
from src.multi_tenant.superadmin_api._agent_overlays import *  # noqa: F401,F403

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
