"""
Record Co-pilot design decision specifications — S121.

These specifications formalize design decisions that emerged during
implementation of the Co-pilot agent feature (WI-0875..0880).

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, "tools/knowledge-db")

import db

k = db.KnowledgeDB()
SESSION = "S121"

# --- Specifications ---

specs = [
    {
        "id": "SPEC-1563",
        "title": "Admin Conversations Are Non-Billable",
        "description": (
            "Conversations with conversation_type='admin_assistance' must not count "
            "toward a tenant's conversation quota or billing meter. When the pipeline "
            "routes to the Co-pilot agent, it sets is_billable=false on the "
            "ConversationDocument. The billing meter (ConversationMeter) skips metering "
            "for conversations where is_billable is false."
        ),
        "section": "BILLING",
        "priority": "P1",
        "tags": ["co-pilot", "billing", "non-billable", "admin-conversation"],
        "assertions": [
            {
                "description": "Co-pilot routing sets is_billable=false on ConversationDocument",
                "type": "structural",
            },
            {
                "description": "Co-pilot routing sets conversation_type='admin_assistance' on ConversationDocument",
                "type": "structural",
            },
            {
                "description": "ConversationMeter.meter_conversation() skips metering when is_billable=false",
                "type": "functional",
            },
        ],
    },
    {
        "id": "SPEC-1564",
        "title": "Co-Pilot Bypasses Critic Validation",
        "description": (
            "Admin team member conversations routed to the Co-pilot agent bypass the "
            "Critic supervisor agent entirely. The Co-pilot response is emitted directly "
            "as a validated token without Critic review. Rationale: (1) admin context is "
            "trusted — team members are authenticated employees, not anonymous customers; "
            "(2) the Critic is trained to detect hallucination and off-brand responses in "
            "customer-facing contexts, which does not apply to admin documentation queries; "
            "(3) bypassing the Critic reduces latency by ~800ms for admin conversations."
        ),
        "section": "AGENTS",
        "priority": "P2",
        "tags": ["co-pilot", "critic", "validation", "bypass"],
        "assertions": [
            {
                "description": "Co-pilot handler emits validated_event without invoking Critic agent",
                "type": "structural",
            },
            {
                "description": "AI message stored with critic_passed=None for Co-pilot conversations",
                "type": "structural",
            },
        ],
    },
    {
        "id": "SPEC-1565",
        "title": "Admin API Key Query Parameter Authentication",
        "description": (
            "The TenantAuthMiddleware accepts api_key as a query parameter (in addition "
            "to the existing X-API-Key header) for SSE and WebSocket connections. This is "
            "required because the browser's EventSource API does not support custom headers. "
            "When the admin widget operates in Co-pilot mode, it passes the team member's "
            "per-user API key (ar_user_*) as ?api_key=<key> on the SSE stream URL. The "
            "middleware resolves the team member's role from this key, enabling pipeline "
            "routing to the Co-pilot agent."
        ),
        "section": "AUTH",
        "priority": "P1",
        "tags": ["co-pilot", "auth", "sse", "query-param", "api-key"],
        "assertions": [
            {
                "description": "TenantAuthMiddleware checks request.query_params.get('api_key') when X-API-Key header is absent",
                "type": "structural",
            },
            {
                "description": "Per-user API key (ar_user_*) via query param resolves team_member_role on TenantContext",
                "type": "functional",
            },
        ],
    },
    {
        "id": "SPEC-1566",
        "title": "Admin Widget Co-Pilot Mode",
        "description": (
            "When the chat widget is embedded in the admin panel, it operates in Co-pilot "
            "mode. The widget script tag receives a data-admin-key attribute containing the "
            "team member's per-user API key. When this attribute is present: (1) HTTP requests "
            "use X-API-Key header instead of X-Widget-Key; (2) SSE connections use api_key "
            "query param instead of widget_key; (3) the greeting message, header text, and "
            "agent name are overridden to Co-pilot branding; (4) the widget_context is set "
            "to 'admin'. TransportConfig gains an optional adminApiKey field."
        ),
        "section": "WIDGET_UI",
        "priority": "P1",
        "tags": ["co-pilot", "widget", "admin-mode", "transport"],
        "assertions": [
            {
                "description": "TransportConfig interface includes optional adminApiKey field",
                "type": "structural",
            },
            {
                "description": "Widget reads data-admin-key attribute from script tag",
                "type": "structural",
            },
            {
                "description": "SSE transport passes api_key query param when adminApiKey is set",
                "type": "structural",
            },
            {
                "description": "HTTP transport uses X-API-Key header when adminApiKey is set",
                "type": "structural",
            },
            {
                "description": "Admin widget sets header text to 'Agent Red Co-pilot'",
                "type": "structural",
            },
            {
                "description": "StandaloneLayout passes resolvedAuth.value as data-admin-key on widget script",
                "type": "structural",
            },
        ],
    },
]

# --- Record ---

for spec in specs:
    k.insert_spec(
        id=spec["id"],
        title=spec["title"],
        description=spec["description"],
        section=spec["section"],
        priority=spec["priority"],
        status="implemented",
        tags=spec["tags"],
        assertions=spec["assertions"],
        changed_by=SESSION,
        change_reason=f"Co-pilot design decision — recorded during {SESSION} implementation",
    )
    print(f"  Recorded: {spec['id']} — {spec['title']} ({len(spec['assertions'])} assertions)")

print(f"\nDone. {len(specs)} design decision specifications recorded.")
