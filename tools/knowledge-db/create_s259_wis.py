"""Create S259 work items in Knowledge Database."""
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

import sys
sys.path.insert(0, "tools/knowledge-db")
from db import KnowledgeDB

kb = KnowledgeDB()

WORK_ITEMS = [
    {
        "id": "WI-3030",
        "title": "Escalation Pipeline v1: sequential routing, timeout, real-time delivery, co-pilot inbox integration",
        "description": (
            "S259 D13/D15/D16/D17/D18. Escalation pipeline non-functional end-to-end. "
            "Phase A: timeout + sequential routing + fallback. "
            "Phase B: real-time admin inbox (SSE/WS + push notifications + presence). "
            "Phase C: co-pilot draft suggestions in inbox. "
            "Phase D: conversation flow polish (AI responds first, varied system messages)."
        ),
        "origin": "defect",
        "component": "escalation",
        "priority": 0,
        "tags": ["s259", "P0", "escalation"],
    },
    {
        "id": "WI-3031",
        "title": "API Gateway cold start latency - verify and fix staging Container App scaling",
        "description": (
            "S259 D1. ~30s delay on first request. TF reference shows min_replicas=2 but actual "
            "deployed settings may differ (Container Apps managed via CLI, not TF). "
            "Verify via az CLI, fix scaling, document cost impact."
        ),
        "origin": "defect",
        "component": "infrastructure",
        "priority": 1,
        "tags": ["s259", "P1", "cold-start"],
    },
    {
        "id": "WI-3032",
        "title": "Widget focus ring: switch onFocus to focus-visible to prevent mouse-click persistence",
        "description": (
            "S259 D5. White border persists on close button and launcher after mouse click. "
            "Root cause: Header.tsx/Launcher.tsx/InputBar.tsx/ConsentBanner.tsx/MessageList.tsx "
            "use onFocus/onBlur events not :focus-visible. Fix all 5 components."
        ),
        "origin": "defect",
        "component": "widget",
        "priority": 2,
        "tags": ["s259", "P2", "focus-ring", "WCAG"],
    },
    {
        "id": "WI-3033",
        "title": "Remove all Coming Soon UI elements: languages + integrations",
        "description": (
            "S259 D6/D19. Remove Spanish/French coming-soon from language config. "
            "Remove Zendesk/Mailchimp coming-soon from IntegrationsManager.tsx (line 291). "
            "Audit all surfaces for remaining coming-soon patterns."
        ),
        "origin": "defect",
        "component": "admin-ui",
        "priority": 2,
        "tags": ["s259", "P2", "coming-soon"],
    },
    {
        "id": "WI-3034",
        "title": "Conversation Preview must use draft config, not activated config",
        "description": (
            "S259 D7. admin_preview_api.py line 140: get_active() fetches activated config. "
            "Owner decision: preview is the safe sandbox, must use draft/pending config. "
            "Change to get_draft() or equivalent. Update SPEC-1872."
        ),
        "origin": "defect",
        "component": "admin-api",
        "priority": 1,
        "tags": ["s259", "P1", "conversation-preview", "SPEC-1872"],
    },
    {
        "id": "WI-3035",
        "title": "Agent icons: use real logos from integration-logos/ instead of fallback letter squares",
        "description": (
            "S259 D9/D10/D11. Agents page uses placeholder letter icons. Correct logos already "
            "exist in admin/dist/standalone/integration-logos/. Update LOGO_MAP in agent-logos.tsx. "
            "Core agents: use icon-master.svg from branding/logo/SVG/."
        ),
        "origin": "defect",
        "component": "admin-ui",
        "priority": 2,
        "tags": ["s259", "P2", "branding", "agent-icons"],
    },
    {
        "id": "WI-3036",
        "title": "Saved Configurations: add per-row delete + column sorting",
        "description": (
            "S259 D8. Table grows unbounded. Delete exists as dropdown but needs per-row trash icon "
            "with confirmation. Add sortable column headers (Name, Saved, Fields). "
            "WidgetConfigurator.tsx line 1317-1330."
        ),
        "origin": "new",
        "component": "admin-ui",
        "priority": 2,
        "tags": ["s259", "P2", "saved-configs", "UX"],
    },
    {
        "id": "WI-3037",
        "title": "Quick Action page type detection: verify end-to-end wiring",
        "description": (
            "S259 D12. Page detection EXISTS in widget (templateVars.ts detectPageContext). "
            "URL pattern matching for Shopify page types. Need to verify: "
            "(a) backend filters quick_actions by page_type, "
            "(b) standalone tenants have documentation, "
            "(c) admin grid maps correctly to backend."
        ),
        "origin": "defect",
        "component": "widget",
        "priority": 1,
        "tags": ["s259", "P1", "quick-actions", "page-type"],
    },
    {
        "id": "WI-3038",
        "title": "Suppress consent banner for authenticated admin users",
        "description": (
            "S259 D14. Consent banner appears in admin context. Owner decision: admin users "
            "have implicit consent. Pass admin flag during widget init, skip ConsentBanner."
        ),
        "origin": "defect",
        "component": "widget",
        "priority": 2,
        "tags": ["s259", "P2", "consent", "admin-context"],
    },
    {
        "id": "WI-3039",
        "title": "Launcher color should not preview before activation",
        "description": (
            "S259 D4. Launcher color previews in real-time before activation, inconsistent "
            "with activation-first model. Remove real-time preview binding. P3."
        ),
        "origin": "defect",
        "component": "admin-ui",
        "priority": 3,
        "tags": ["s259", "P3", "launcher-color", "activation-model"],
    },
]

for wi in WORK_ITEMS:
    try:
        result = kb.insert_work_item(
            id=wi["id"],
            title=wi["title"],
            description=wi["description"],
            origin=wi["origin"],
            component=wi["component"],
            priority=str(wi["priority"]),
            resolution_status="open",
            changed_by="prime-builder",
            change_reason="S259 manual testing defect collection",
        )
        print(f"{wi['id']}: created (v{result.get('version', '?')})")
    except Exception as e:
        print(f"{wi['id']}: ERROR - {e}")
