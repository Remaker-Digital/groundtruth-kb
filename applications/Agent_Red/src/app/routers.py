# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Router registration for Agent Red Customer Experience.

Imports all 45 API routers and provides a single function to register
them on the FastAPI application instance.

R1 refactoring — session 31.
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from fastapi import FastAPI

from src.chat.endpoints import router as chat_router
from src.integrations.provisioning import router as provisioning_router
from src.integrations.shopify_billing import router as shopify_billing_router
from src.integrations.shopify_gdpr_webhooks import router as shopify_gdpr_router
from src.integrations.stripe_checkout import router as checkout_router
from src.integrations.stripe_packs import router as packs_router
from src.integrations.stripe_portal import router as portal_router
from src.integrations.stripe_usage import router as usage_router
from src.integrations.stripe_webhooks import router as webhooks_router
from src.multi_tenant.abuse_detection import router as abuse_router
from src.multi_tenant.addon_checkout import router as addon_checkout_router
from src.multi_tenant.admin_agent_api import router as admin_agent_router
from src.multi_tenant.admin_analytics_api import router as admin_analytics_router
from src.multi_tenant.admin_apikey_api import router as admin_apikey_router
from src.multi_tenant.admin_audit_api import router as admin_audit_router
from src.multi_tenant.admin_contact_api import router as admin_contact_router
from src.multi_tenant.admin_conversation_api import router as admin_inbox_router
from src.multi_tenant.admin_customer_profile_api import router as admin_profile_router
from src.multi_tenant.admin_fine_tuning_api import router as admin_fine_tuning_router
from src.multi_tenant.admin_gdpr_api import router as admin_gdpr_router
from src.multi_tenant.admin_ingestion_api import router as admin_ingestion_router
from src.multi_tenant.admin_integration_api import router as admin_integration_router
from src.multi_tenant.admin_knowledge_api import router as admin_knowledge_router
from src.multi_tenant.admin_knowledge_score_api import router as admin_knowledge_score_router
from src.multi_tenant.admin_marketplace_api import router as admin_marketplace_router
from src.multi_tenant.admin_mfa_auth import router as admin_mfa_auth_router
from src.multi_tenant.admin_presets_api import router as admin_presets_router
from src.multi_tenant.admin_preview_api import router as admin_preview_router
from src.multi_tenant.admin_quick_action_api import router as admin_quick_action_router
from src.multi_tenant.admin_team_api import router as admin_team_router
from src.multi_tenant.avatar_upload import router as avatar_router
from src.multi_tenant.communication_capture import router as capture_router
from src.multi_tenant.config_locking import router as config_lock_router
from src.multi_tenant.cost_analytics import router as cost_router
from src.multi_tenant.email_change import router as email_change_router
from src.multi_tenant.email_verification import router as email_verify_router
from src.multi_tenant.launcher_image_upload import router as launcher_image_router
from src.multi_tenant.magic_link_auth import router as magic_link_router
from src.multi_tenant.memory_dashboard import router as memory_dashboard_router
from src.multi_tenant.security_hardening import rotation_router
from src.multi_tenant.spa_recovery import router as spa_recovery_router
from src.multi_tenant.status_api import router as status_router
from src.multi_tenant.superadmin_api import router as superadmin_router
from src.multi_tenant.superadmin_contact_api import router as superadmin_contact_router
from src.multi_tenant.support_diagnostics import router as diagnostics_router
from src.multi_tenant.tenant_config_api import router as config_router
from src.multi_tenant.tenant_recovery import recovery_verify_router
from src.multi_tenant.tenant_recovery import router as tenant_recovery_router
from src.multi_tenant.tier_upgrade import router as tier_upgrade_router
from src.multi_tenant.trial_management import trial_router
from src.multi_tenant.usage_dashboard_api import router as dashboard_router
from src.multi_tenant.widget_otp_verification import router as widget_otp_router


def register_routers(app: FastAPI) -> None:
    """Register all 46 API routers on the FastAPI application.

    This mirrors the router registration block from main.py lines 186-209.
    """
    app.include_router(provisioning_router)
    app.include_router(checkout_router)
    app.include_router(packs_router)
    app.include_router(portal_router)
    app.include_router(usage_router)
    app.include_router(webhooks_router)
    app.include_router(shopify_billing_router)
    app.include_router(dashboard_router)
    app.include_router(config_router)
    app.include_router(chat_router)
    app.include_router(admin_inbox_router)
    app.include_router(admin_ingestion_router)  # Must be before knowledge router (shared prefix, specific routes first)
    app.include_router(
        admin_knowledge_score_router
    )  # Must be before knowledge router (shared /api/admin/knowledge prefix)
    app.include_router(admin_knowledge_router)
    app.include_router(admin_preview_router)  # SPEC-1872: conversation preview (SSE)
    app.include_router(admin_analytics_router)
    app.include_router(admin_team_router)
    app.include_router(admin_gdpr_router)
    app.include_router(shopify_gdpr_router)
    app.include_router(admin_audit_router)
    app.include_router(trial_router)
    app.include_router(rotation_router)
    app.include_router(admin_profile_router)
    app.include_router(admin_apikey_router)
    app.include_router(admin_integration_router)
    app.include_router(admin_quick_action_router)
    app.include_router(superadmin_router)
    app.include_router(email_verify_router)
    app.include_router(magic_link_router)
    app.include_router(admin_mfa_auth_router)
    app.include_router(status_router)
    app.include_router(diagnostics_router)
    app.include_router(abuse_router)
    app.include_router(config_lock_router)
    app.include_router(cost_router)
    app.include_router(avatar_router)
    app.include_router(launcher_image_router)
    app.include_router(tier_upgrade_router)
    app.include_router(addon_checkout_router)
    app.include_router(memory_dashboard_router)
    app.include_router(admin_contact_router)
    app.include_router(superadmin_contact_router)
    app.include_router(admin_fine_tuning_router)
    app.include_router(admin_agent_router)
    app.include_router(widget_otp_router)
    app.include_router(spa_recovery_router)  # SPEC-1678: unauthenticated
    app.include_router(tenant_recovery_router)  # SPEC-1677: SPA-facing
    app.include_router(recovery_verify_router)  # SPEC-1677: unauthenticated
    app.include_router(capture_router)  # SPEC-1687: communication capture
    app.include_router(email_change_router)  # SPEC-1682/1683: email change
    app.include_router(admin_presets_router)  # SPEC-1878: G6 vertical presets
    app.include_router(admin_marketplace_router)  # SPEC-1865: agent marketplace
