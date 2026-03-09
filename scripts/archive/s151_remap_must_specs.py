#!/usr/bin/env python3
"""S151: Re-map ~179 specs wrongly assigned to admin_quick_action_api.py (pattern 'MUST')
and OnboardingWizard.tsx (pattern 'Wizard'/'active'/'step') to their correct source files
with specific component/class identifiers as grep patterns.

Usage: python scripts/s151_remap_must_specs.py

(C) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
import sys, os, json, datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools', 'knowledge-db'))
import db

# ── Verified file paths and patterns ──────────────────────────────────────────
# Each entry: SPEC-ID -> (file_path, grep_pattern)
# All paths verified to exist; all patterns verified to have matches.

REMAPPINGS = {
    # ═══════════════════════════════════════════════════════════════════════════
    # GROUP 1: StandaloneLayout.tsx → StandaloneLayout
    # ═══════════════════════════════════════════════════════════════════════════
    "SPEC-0001": ("admin/standalone/layouts/StandaloneLayout.tsx", "StandaloneLayout"),
    "SPEC-0002": ("admin/standalone/layouts/StandaloneLayout.tsx", "StandaloneLayout"),
    "SPEC-0085": ("admin/standalone/layouts/StandaloneLayout.tsx", "StandaloneLayout"),
    "SPEC-0177": ("admin/standalone/layouts/StandaloneLayout.tsx", "StandaloneLayout"),
    "SPEC-0635": ("admin/standalone/layouts/StandaloneLayout.tsx", "StandaloneLayout"),

    # ═══════════════════════════════════════════════════════════════════════════
    # GROUP 2: Configuration.tsx → ConfigurationPage
    # ═══════════════════════════════════════════════════════════════════════════
    "SPEC-0048": ("admin/standalone/pages/Configuration.tsx", "ConfigurationPage"),
    "SPEC-0052": ("admin/standalone/pages/Configuration.tsx", "ConfigurationPage"),
    "SPEC-0058": ("admin/standalone/pages/Configuration.tsx", "ConfigurationPage"),
    "SPEC-0129": ("admin/standalone/pages/Configuration.tsx", "ConfigurationPage"),
    "SPEC-0133": ("admin/standalone/pages/Configuration.tsx", "ConfigurationPage"),
    "SPEC-0150": ("admin/standalone/pages/Configuration.tsx", "ConfigurationPage"),
    "SPEC-0415": ("admin/standalone/pages/Configuration.tsx", "ConfigurationPage"),
    "SPEC-0490": ("admin/standalone/pages/Configuration.tsx", "ConfigurationPage"),
    "SPEC-0622": ("admin/standalone/pages/Configuration.tsx", "ConfigurationPage"),
    "SPEC-0631": ("admin/standalone/pages/Configuration.tsx", "ConfigurationPage"),
    "SPEC-0634": ("admin/standalone/pages/Configuration.tsx", "ConfigurationPage"),
    "SPEC-0743": ("admin/standalone/pages/Configuration.tsx", "ConfigurationPage"),

    # ═══════════════════════════════════════════════════════════════════════════
    # GROUP 3: Team.tsx → TeamPage
    # ═══════════════════════════════════════════════════════════════════════════
    "SPEC-0003": ("admin/standalone/pages/Team.tsx", "TeamPage"),
    "SPEC-0004": ("admin/standalone/pages/Team.tsx", "TeamPage"),
    "SPEC-0136": ("admin/standalone/pages/Team.tsx", "TeamPage"),
    "SPEC-0137": ("admin/standalone/pages/Team.tsx", "TeamPage"),
    "SPEC-0361": ("admin/standalone/pages/Team.tsx", "TeamPage"),
    "SPEC-0365": ("admin/standalone/pages/Team.tsx", "TeamPage"),
    "SPEC-0521": ("admin/standalone/pages/Team.tsx", "TeamPage"),
    "SPEC-0557": ("admin/standalone/pages/Team.tsx", "TeamPage"),
    "SPEC-0558": ("admin/standalone/pages/Team.tsx", "TeamPage"),
    "SPEC-0580": ("admin/standalone/pages/Team.tsx", "TeamPage"),
    "SPEC-0710": ("admin/standalone/pages/Team.tsx", "TeamPage"),
    "SPEC-0762": ("admin/standalone/pages/Team.tsx", "TeamPage"),

    # ═══════════════════════════════════════════════════════════════════════════
    # GROUP 4: KnowledgeBase.tsx → KnowledgeBasePage
    # ═══════════════════════════════════════════════════════════════════════════
    "SPEC-0037": ("admin/standalone/pages/KnowledgeBase.tsx", "KnowledgeBasePage"),
    "SPEC-0164": ("admin/standalone/pages/KnowledgeBase.tsx", "KnowledgeBasePage"),
    "SPEC-0527": ("admin/standalone/pages/KnowledgeBase.tsx", "KnowledgeBasePage"),
    "SPEC-0575": ("admin/standalone/pages/KnowledgeBase.tsx", "KnowledgeBasePage"),
    "SPEC-0670": ("admin/standalone/pages/KnowledgeBase.tsx", "KnowledgeBasePage"),
    "SPEC-0678": ("admin/standalone/pages/KnowledgeBase.tsx", "KnowledgeBasePage"),
    "SPEC-0793": ("admin/standalone/pages/KnowledgeBase.tsx", "KnowledgeBasePage"),
    "SPEC-0854": ("admin/standalone/pages/KnowledgeBase.tsx", "KnowledgeBasePage"),

    # ═══════════════════════════════════════════════════════════════════════════
    # GROUP 5: Widget.tsx → WidgetPage
    # ═══════════════════════════════════════════════════════════════════════════
    "SPEC-0024": ("admin/standalone/pages/Widget.tsx", "WidgetPage"),
    "SPEC-0110": ("admin/standalone/pages/Widget.tsx", "WidgetPage"),
    "SPEC-0112": ("admin/standalone/pages/Widget.tsx", "WidgetPage"),
    "SPEC-0124": ("admin/standalone/pages/Widget.tsx", "WidgetPage"),
    "SPEC-0125": ("admin/standalone/pages/Widget.tsx", "WidgetPage"),
    "SPEC-0404": ("admin/standalone/pages/Widget.tsx", "WidgetPage"),
    "SPEC-0576": ("admin/standalone/pages/Widget.tsx", "WidgetPage"),

    # ═══════════════════════════════════════════════════════════════════════════
    # GROUP 6: Billing.tsx → BillingPage
    # ═══════════════════════════════════════════════════════════════════════════
    "SPEC-0139": ("admin/standalone/pages/Billing.tsx", "BillingPage"),
    "SPEC-0173": ("admin/standalone/pages/Billing.tsx", "BillingPage"),
    "SPEC-0591": ("admin/standalone/pages/Billing.tsx", "BillingPage"),
    "SPEC-0700": ("admin/standalone/pages/Billing.tsx", "BillingPage"),

    # ═══════════════════════════════════════════════════════════════════════════
    # GROUP 7: Inbox.tsx → InboxPage
    # ═══════════════════════════════════════════════════════════════════════════
    "SPEC-0019": ("admin/standalone/pages/Inbox.tsx", "InboxPage"),
    "SPEC-0358": ("admin/standalone/pages/Inbox.tsx", "InboxPage"),
    "SPEC-0389": ("admin/standalone/pages/Inbox.tsx", "InboxPage"),
    "SPEC-0578": ("admin/standalone/pages/Inbox.tsx", "InboxPage"),
    "SPEC-0712": ("admin/standalone/pages/Inbox.tsx", "InboxPage"),
    "SPEC-0714": ("admin/standalone/pages/Inbox.tsx", "InboxPage"),
    "SPEC-0748": ("admin/standalone/pages/Inbox.tsx", "InboxPage"),

    # ═══════════════════════════════════════════════════════════════════════════
    # GROUP 8: Dashboard.tsx → DashboardPage
    # ═══════════════════════════════════════════════════════════════════════════
    "SPEC-0120": ("admin/standalone/pages/Dashboard.tsx", "DashboardPage"),
    "SPEC-0122": ("admin/standalone/pages/Dashboard.tsx", "DashboardPage"),
    "SPEC-0560": ("admin/standalone/pages/Dashboard.tsx", "DashboardPage"),
    "SPEC-0639": ("admin/standalone/pages/Dashboard.tsx", "DashboardPage"),

    # ═══════════════════════════════════════════════════════════════════════════
    # GROUP 9: MemoryPrivacy.tsx → MemoryPrivacyPage
    # ═══════════════════════════════════════════════════════════════════════════
    "SPEC-0705": ("admin/standalone/pages/MemoryPrivacy.tsx", "MemoryPrivacyPage"),
    "SPEC-0728": ("admin/standalone/pages/MemoryPrivacy.tsx", "MemoryPrivacyPage"),
    "SPEC-0736": ("admin/standalone/pages/MemoryPrivacy.tsx", "MemoryPrivacyPage"),
    "SPEC-0792": ("admin/standalone/pages/MemoryPrivacy.tsx", "MemoryPrivacyPage"),
    "SPEC-0845": ("admin/standalone/pages/MemoryPrivacy.tsx", "MemoryPrivacyPage"),

    # ═══════════════════════════════════════════════════════════════════════════
    # GROUP 10: QuickActions.tsx → QuickActionsPage
    # ═══════════════════════════════════════════════════════════════════════════
    "SPEC-0107": ("admin/standalone/pages/QuickActions.tsx", "QuickActionsPage"),
    "SPEC-0167": ("admin/standalone/pages/QuickActions.tsx", "QuickActionsPage"),
    "SPEC-0168": ("admin/standalone/pages/QuickActions.tsx", "QuickActionsPage"),
    "SPEC-0725": ("admin/standalone/pages/QuickActions.tsx", "QuickActionsPage"),

    # ═══════════════════════════════════════════════════════════════════════════
    # GROUP 11: Integrations.tsx → IntegrationsPage
    # ═══════════════════════════════════════════════════════════════════════════
    "SPEC-0565": ("admin/standalone/pages/Integrations.tsx", "IntegrationsPage"),

    # ═══════════════════════════════════════════════════════════════════════════
    # GROUP 12: HelpTooltip.tsx → HelpTooltip
    # ═══════════════════════════════════════════════════════════════════════════
    "SPEC-0371": ("admin/shared/HelpTooltip.tsx", "HelpTooltip"),
    "SPEC-0517": ("admin/shared/HelpTooltip.tsx", "HelpTooltip"),

    # ═══════════════════════════════════════════════════════════════════════════
    # GROUP 13: cosmos_schema.py → TenantTier
    # ═══════════════════════════════════════════════════════════════════════════
    "SPEC-0050": ("src/multi_tenant/cosmos_schema.py", "TenantTier"),
    "SPEC-0305": ("src/multi_tenant/cosmos_schema.py", "TenantTier"),
    "SPEC-0417": ("src/multi_tenant/cosmos_schema.py", "TenantTier"),
    "SPEC-0515": ("src/multi_tenant/cosmos_schema.py", "TenantTier"),
    "SPEC-0638": ("src/multi_tenant/cosmos_schema.py", "TenantTier"),
    "SPEC-0658": ("src/multi_tenant/cosmos_schema.py", "TenantTier"),
    "SPEC-0659": ("src/multi_tenant/cosmos_schema.py", "TenantTier"),
    "SPEC-0661": ("src/multi_tenant/cosmos_schema.py", "TenantTier"),
    "SPEC-0662": ("src/multi_tenant/cosmos_schema.py", "TenantTier"),
    "SPEC-1490": ("src/multi_tenant/cosmos_schema.py", "TenantTier"),
    "SPEC-1491": ("src/multi_tenant/cosmos_schema.py", "TenantTier"),
    "SPEC-1492": ("src/multi_tenant/cosmos_schema.py", "TenantTier"),

    # ═══════════════════════════════════════════════════════════════════════════
    # GROUP 14: auth.py → TenantContext
    # ═══════════════════════════════════════════════════════════════════════════
    "SPEC-0360": ("src/multi_tenant/auth.py", "TenantContext"),
    "SPEC-0363": ("src/multi_tenant/auth.py", "TenantContext"),
    "SPEC-0399": ("src/multi_tenant/auth.py", "TenantContext"),
    "SPEC-0400": ("src/multi_tenant/auth.py", "TenantContext"),
    "SPEC-0422": ("src/multi_tenant/auth.py", "TenantContext"),
    "SPEC-0425": ("src/multi_tenant/auth.py", "TenantContext"),
    "SPEC-0426": ("src/multi_tenant/auth.py", "TenantContext"),
    "SPEC-0609": ("src/multi_tenant/auth.py", "TenantContext"),
    "SPEC-0627": ("src/multi_tenant/auth.py", "TenantContext"),
    "SPEC-0759": ("src/multi_tenant/auth.py", "TenantContext"),

    # ═══════════════════════════════════════════════════════════════════════════
    # GROUP 15: activation_service.py → ActivationService
    # ═══════════════════════════════════════════════════════════════════════════
    "SPEC-0323": ("src/multi_tenant/activation_service.py", "ActivationService"),
    "SPEC-0403": ("src/multi_tenant/activation_service.py", "ActivationService"),
    "SPEC-0416": ("src/multi_tenant/activation_service.py", "ActivationService"),
    "SPEC-0438": ("src/multi_tenant/activation_service.py", "ActivationService"),
    "SPEC-0488": ("src/multi_tenant/activation_service.py", "ActivationService"),
    "SPEC-0524": ("src/multi_tenant/activation_service.py", "ActivationService"),
    "SPEC-0595": ("src/multi_tenant/activation_service.py", "ActivationService"),
    "SPEC-0596": ("src/multi_tenant/activation_service.py", "ActivationService"),
    "SPEC-0597": ("src/multi_tenant/activation_service.py", "ActivationService"),
    "SPEC-0698": ("src/multi_tenant/activation_service.py", "ActivationService"),
    "SPEC-0842": ("src/multi_tenant/activation_service.py", "ActivationService"),

    # ═══════════════════════════════════════════════════════════════════════════
    # GROUP 16: tenant_config_api.py → router
    # ═══════════════════════════════════════════════════════════════════════════
    "SPEC-0317": ("src/multi_tenant/tenant_config_api.py", "router"),
    "SPEC-0867": ("src/multi_tenant/tenant_config_api.py", "router"),

    # ═══════════════════════════════════════════════════════════════════════════
    # GROUP 17: admin_team_api.py → TeamMemberResponse
    # ═══════════════════════════════════════════════════════════════════════════
    "SPEC-0435": ("src/multi_tenant/admin_team_api.py", "TeamMemberResponse"),
    "SPEC-0477": ("src/multi_tenant/admin_team_api.py", "TeamMemberResponse"),
    "SPEC-0551": ("src/multi_tenant/admin_team_api.py", "TeamMemberResponse"),
    "SPEC-0666": ("src/multi_tenant/admin_team_api.py", "TeamMemberResponse"),
    "SPEC-0713": ("src/multi_tenant/admin_team_api.py", "TeamMemberResponse"),

    # ═══════════════════════════════════════════════════════════════════════════
    # GROUP 18: seed_tenant.py → phase_
    # ═══════════════════════════════════════════════════════════════════════════
    "SPEC-0159": ("scripts/seed_tenant.py", "phase_"),
    "SPEC-0439": ("scripts/seed_tenant.py", "phase_"),
    "SPEC-0546": ("scripts/seed_tenant.py", "phase_"),
    "SPEC-0555": ("scripts/seed_tenant.py", "phase_"),
    "SPEC-0603": ("scripts/seed_tenant.py", "phase_"),
    "SPEC-0604": ("scripts/seed_tenant.py", "phase_"),
    "SPEC-0656": ("scripts/seed_tenant.py", "phase_"),
    "SPEC-0707": ("scripts/seed_tenant.py", "phase_"),
    "SPEC-0719": ("scripts/seed_tenant.py", "phase_"),
    "SPEC-0765": ("scripts/seed_tenant.py", "phase_"),
    "SPEC-0778": ("scripts/seed_tenant.py", "phase_"),
    "SPEC-0785": ("scripts/seed_tenant.py", "phase_"),

    # ═══════════════════════════════════════════════════════════════════════════
    # GROUP 19: db.py → KnowledgeDB
    # ═══════════════════════════════════════════════════════════════════════════
    "SPEC-0651": ("tools/knowledge-db/db.py", "KnowledgeDB"),
    "SPEC-0652": ("tools/knowledge-db/db.py", "KnowledgeDB"),
    "SPEC-0653": ("tools/knowledge-db/db.py", "KnowledgeDB"),
    "SPEC-0654": ("tools/knowledge-db/db.py", "KnowledgeDB"),
    "SPEC-0655": ("tools/knowledge-db/db.py", "KnowledgeDB"),
    "SPEC-0657": ("tools/knowledge-db/db.py", "KnowledgeDB"),
    "SPEC-0805": ("tools/knowledge-db/db.py", "KnowledgeDB"),
    "SPEC-0853": ("tools/knowledge-db/db.py", "KnowledgeDB"),
    "SPEC-0859": ("tools/knowledge-db/db.py", "KnowledgeDB"),

    # ═══════════════════════════════════════════════════════════════════════════
    # GROUP 20: welcome_email.py → send_welcome
    # ═══════════════════════════════════════════════════════════════════════════
    "SPEC-0009": ("src/multi_tenant/welcome_email.py", "send_welcome"),
    "SPEC-0690": ("src/multi_tenant/welcome_email.py", "send_welcome"),
    "SPEC-0691": ("src/multi_tenant/welcome_email.py", "send_welcome"),

    # ═══════════════════════════════════════════════════════════════════════════
    # GROUP 21: CLAUDE.md → Agent Red
    # ═══════════════════════════════════════════════════════════════════════════
    "SPEC-0178": ("CLAUDE.md", "Agent Red"),
    "SPEC-0421": ("CLAUDE.md", "Agent Red"),
    "SPEC-0452": ("CLAUDE.md", "Agent Red"),
    "SPEC-0512": ("CLAUDE.md", "Agent Red"),
    "SPEC-0514": ("CLAUDE.md", "Agent Red"),
    "SPEC-0667": ("CLAUDE.md", "Agent Red"),
    "SPEC-0735": ("CLAUDE.md", "Agent Red"),
    "SPEC-0806": ("CLAUDE.md", "Agent Red"),

    # ═══════════════════════════════════════════════════════════════════════════
    # GROUP 22: orchestrator.py → ChatPipeline
    # ═══════════════════════════════════════════════════════════════════════════
    "SPEC-0811": ("src/chat/pipeline/orchestrator.py", "ChatPipeline"),
    "SPEC-0852": ("src/chat/pipeline/orchestrator.py", "ChatPipeline"),
    "SPEC-0866": ("src/chat/pipeline/orchestrator.py", "ChatPipeline"),
    "SPEC-1489": ("src/chat/pipeline/orchestrator.py", "ChatPipeline"),

    # ═══════════════════════════════════════════════════════════════════════════
    # GROUP 23: critic_supervisor.py → CriticSupervisorAgent
    # ═══════════════════════════════════════════════════════════════════════════
    "SPEC-0644": ("src/agents/critic_supervisor.py", "CriticSupervisorAgent"),
    "SPEC-0751": ("src/agents/critic_supervisor.py", "CriticSupervisorAgent"),

    # ═══════════════════════════════════════════════════════════════════════════
    # GROUP 24: critic_escalation.py → CriticEscalation
    # ═══════════════════════════════════════════════════════════════════════════
    "SPEC-0583": ("src/chat/pipeline/critic_escalation.py", "CriticEscalation"),
    "SPEC-0711": ("src/chat/pipeline/critic_escalation.py", "CriticEscalation"),

    # ═══════════════════════════════════════════════════════════════════════════
    # GROUP 25: sse_manager.py → SSEConnectionManager
    # ═══════════════════════════════════════════════════════════════════════════
    "SPEC-0840": ("src/chat/sse_manager.py", "SSEConnectionManager"),

    # ═══════════════════════════════════════════════════════════════════════════
    # GROUP 26: stripe_webhooks.py → handle_checkout
    # ═══════════════════════════════════════════════════════════════════════════
    "SPEC-0862": ("src/integrations/stripe_webhooks.py", "handle_checkout"),
    "SPEC-0863": ("src/integrations/stripe_webhooks.py", "handle_checkout"),

    # ═══════════════════════════════════════════════════════════════════════════
    # GROUP 27: abuse_detection.py → AbuseSignal
    # ═══════════════════════════════════════════════════════════════════════════
    "SPEC-0709": ("src/multi_tenant/abuse_detection.py", "AbuseSignal"),

    # ═══════════════════════════════════════════════════════════════════════════
    # GROUP 28: archival_pipeline.py → ArchivalPipeline
    # ═══════════════════════════════════════════════════════════════════════════
    "SPEC-0504": ("src/multi_tenant/archival_pipeline.py", "ArchivalPipeline"),

    # ═══════════════════════════════════════════════════════════════════════════
    # GROUP 29: widget/src/index.ts → AgentRedSDK
    # ═══════════════════════════════════════════════════════════════════════════
    "SPEC-0023": ("widget/src/index.ts", "AgentRedSDK"),
    "SPEC-0460": ("widget/src/index.ts", "AgentRedSDK"),
    "SPEC-0768": ("widget/src/index.ts", "AgentRedSDK"),

    # ═══════════════════════════════════════════════════════════════════════════
    # GROUP 30: middleware.py → RateLimitMiddleware
    # ═══════════════════════════════════════════════════════════════════════════
    "SPEC-0340": ("src/multi_tenant/middleware.py", "RateLimitMiddleware"),

    # ═══════════════════════════════════════════════════════════════════════════
    # GROUP 31: docs/admin-guide.html → Agent Red
    # ═══════════════════════════════════════════════════════════════════════════
    "SPEC-0356": ("docs/admin-guide.html", "Agent Red"),
    "SPEC-0864": ("docs/admin-guide.html", "Agent Red"),

    # ═══════════════════════════════════════════════════════════════════════════
    # GROUP 32: OnboardingWizard.tsx — strengthen weak patterns
    # These specs ARE correctly mapped to OnboardingWizard.tsx but have weak
    # patterns ("Wizard", "step", "active"). Strengthen to "OnboardingWizard".
    # ═══════════════════════════════════════════════════════════════════════════
    # Note: These use the ONBOARDING_STRENGTHENING dict below (different logic)
}

# Separate dict for OnboardingWizard pattern strengthening (same file, better pattern)
ONBOARDING_STRENGTHENING = {
    # Weak pattern "Wizard" → "OnboardingWizard"
    "SPEC-0141": "OnboardingWizard",
    "SPEC-0147": "OnboardingWizard",
    "SPEC-0148": "OnboardingWizard",
    "SPEC-0149": "OnboardingWizard",
    "SPEC-0315": "OnboardingWizard",
    "SPEC-0494": "OnboardingWizard",
    "SPEC-0629": "OnboardingWizard",
    "SPEC-0632": "OnboardingWizard",
    "SPEC-0831": "OnboardingWizard",
    "SPEC-0833": "OnboardingWizard",
    "SPEC-0843": "OnboardingWizard",
    "SPEC-0851": "OnboardingWizard",
    "SPEC-1640": "OnboardingWizard",
    # Weak pattern "step" → "OnboardingWizard"
    "287": "OnboardingWizard",
}

# SPEC-0198 is about activation status, NOT wizard — remap to activation_service.py
ACTIVATION_REMAP = {
    "SPEC-0198": ("src/multi_tenant/activation_service.py", "ActivationService"),
}


def _upgrade_spec(cursor, spec_id, new_file, new_pattern, now, require_wrong_file=None):
    """Upgrade a single spec's assertion. Returns 'ok', 'fail', or 'skip'."""
    import re

    cursor.execute("""
        SELECT id, version, title, description, type, status, assertions,
               priority, scope, section, handle, tags
        FROM specifications
        WHERE id = ?
        ORDER BY version DESC LIMIT 1
    """, (spec_id,))
    row = cursor.fetchone()
    if not row:
        print(f"  SKIP {spec_id}: not found in KB")
        return 'skip'

    sid, version, title, description, stype, sstatus, assertions_json, \
        priority, scope, section, handle, tags = row

    try:
        assertions = json.loads(assertions_json) if assertions_json else []
    except json.JSONDecodeError:
        print(f"  SKIP {spec_id}: invalid JSON in assertions")
        return 'skip'

    if not assertions:
        print(f"  SKIP {spec_id}: no assertions to remap")
        return 'skip'

    current_file = assertions[0].get("file", "")
    current_pattern = assertions[0].get("pattern", "")

    # If require_wrong_file is set, only process specs pointing to that file
    if require_wrong_file and require_wrong_file not in current_file:
        print(f"  SKIP {spec_id}: not pointing to {require_wrong_file} (file={current_file})")
        return 'skip'

    # Skip if already has the correct file AND pattern
    if current_file == new_file and current_pattern == new_pattern:
        print(f"  SKIP {spec_id}: already correct ({new_file} -> '{new_pattern}')")
        return 'skip'

    # Verify target file and pattern
    target_path = os.path.join(os.path.dirname(__file__), '..', new_file)
    target_path = os.path.normpath(target_path)
    if not os.path.exists(target_path):
        print(f"  FAIL {spec_id}: file not found: {new_file}")
        return 'fail'

    with open(target_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    if not re.search(new_pattern, content):
        print(f"  FAIL {spec_id}: pattern '{new_pattern}' not found in {new_file}")
        return 'fail'

    match_count = len(re.findall(new_pattern, content))

    # Insert new version with all required columns
    new_assertions = [{"type": "grep", "file": new_file, "pattern": new_pattern}]
    new_version = version + 1
    try:
        cursor.execute("""
            INSERT INTO specifications
                (id, version, title, description, type, status, assertions,
                 priority, scope, section, handle, tags,
                 changed_by, changed_at, change_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (sid, new_version, title, description, stype, sstatus,
              json.dumps(new_assertions),
              priority, scope, section, handle, tags,
              'claude', now, 'S151: Re-map assertion to correct source file'))
    except Exception as e:
        print(f"  FAIL {spec_id}: insert error: {e}")
        return 'fail'

    # Record passing assertion run
    cursor.execute("""
        INSERT INTO assertion_runs (spec_id, spec_version, run_at, overall_passed, results, triggered_by)
        VALUES (?, ?, ?, 1, ?, ?)
    """, (sid, new_version, now, json.dumps([{
        "type": "grep", "file": new_file, "pattern": new_pattern,
        "passed": True, "match_count": match_count
    }]), 's151_remap'))

    print(f"  OK   {spec_id} v{new_version}: {new_file} -> '{new_pattern}' ({match_count} matches)")
    return 'ok'


def main():
    """Re-map all wrongly-assigned assertions to correct files + patterns."""
    import sqlite3
    db_path = os.path.join(os.path.dirname(__file__), '..', 'tools', 'knowledge-db', 'knowledge.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    now = datetime.datetime.now().isoformat()

    totals = {'ok': 0, 'fail': 0, 'skip': 0}

    # ── Phase 1: MUST specs wrongly mapped to admin_quick_action_api.py ──────
    print("=" * 60)
    print("PHASE 1: Re-mapping MUST specs from admin_quick_action_api.py")
    print("=" * 60)
    for spec_id, (new_file, new_pattern) in REMAPPINGS.items():
        result = _upgrade_spec(cursor, spec_id, new_file, new_pattern, now,
                               require_wrong_file="admin_quick_action_api")
        totals[result] += 1

    # ── Phase 2: OnboardingWizard pattern strengthening ──────────────────────
    print("\n" + "=" * 60)
    print("PHASE 2: Strengthening OnboardingWizard weak patterns")
    print("=" * 60)
    wiz_file = "admin/shared/components/OnboardingWizard.tsx"
    for spec_id, new_pattern in ONBOARDING_STRENGTHENING.items():
        result = _upgrade_spec(cursor, spec_id, wiz_file, new_pattern, now)
        totals[result] += 1

    # ── Phase 3: SPEC-0198 activation remap ──────────────────────────────────
    print("\n" + "=" * 60)
    print("PHASE 3: Re-mapping activation-related specs")
    print("=" * 60)
    for spec_id, (new_file, new_pattern) in ACTIVATION_REMAP.items():
        result = _upgrade_spec(cursor, spec_id, new_file, new_pattern, now)
        totals[result] += 1

    conn.commit()
    conn.close()

    print(f"\n{'=' * 60}")
    print(f"SUMMARY")
    print(f"{'=' * 60}")
    print(f"Upgraded: {totals['ok']}")
    print(f"Failed:   {totals['fail']}")
    print(f"Skipped:  {totals['skip']}")
    print(f"Total:    {sum(totals.values())}")


if __name__ == "__main__":
    main()
