"""Superadmin Provider Operations API — package init.

Re-exports all public names from sub-modules for backward compatibility.
All existing imports (from src.multi_tenant.superadmin_api import X) continue to work.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
# Re-export everything from the legacy monolith for backward compatibility.
# Sub-modules are imported below for domain organization.
from src.multi_tenant.superadmin_api._monolith import *  # noqa: F403
from src.multi_tenant.superadmin_api._monolith import (  # noqa: F401
    router,
    configure_superadmin_services,
    configure_copilot_knowledge_service,
    configure_pipeline_observatory,
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
    _resolve_service_message_recipients,
    _get_mfa_svc,
    _get_team_member,
    _incident_to_model,
    _rule_to_model,
    _history_to_model,
    _infer_category_from_filename,
    _generate_embedding,
    _get_copilot_config,
    _save_copilot_config,
)

# Domain sub-modules (import for registration)
from src.multi_tenant.superadmin_api import (  # noqa: F401
    _tenants,
    _dashboard,
    _operations,
    _copilot,
    _platform,
)

__all__ = [
    "router",
    "configure_superadmin_services",
    "configure_copilot_knowledge_service",
    "configure_pipeline_observatory",
]
