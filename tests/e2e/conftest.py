"""
E2E test fixtures for the standalone admin SPA.

Manages the Vite dev server lifecycle and provides pre-configured Playwright
pages with mocked API responses for deterministic admin UI testing.

Architecture:
  - admin_vite_server (session): starts `npm run dev` in admin/standalone/,
    waits for port 3300
  - MOCK_* constants: deterministic API responses for every admin endpoint
  - admin_page: navigates to the admin SPA with all API calls intercepted
  - Fixture variants: admin_team_page, admin_config_page, etc.

All API calls are intercepted via Playwright route() to return deterministic
JSON.  No backend server is needed.  This tests the UI layer in isolation:
  - Does the correct DOM render for given data?
  - Do user interactions (click, type, select) trigger the right API calls?
  - Do error states render correctly?
  - Are tier-gated features hidden/shown correctly?

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import json
import os
import re
import signal
import socket
import subprocess
import sys
import time
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest
from playwright.sync_api import Page, Route

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ADMIN_VITE_PORT = 3300
ADMIN_DIR = Path(__file__).resolve().parent.parent.parent / "admin" / "standalone"

# ---------------------------------------------------------------------------
# Mock API Data — Deterministic responses for every admin endpoint
# ---------------------------------------------------------------------------

# The layout calls GET /api/tenants/lookup and expects snake_case keys.
MOCK_TENANT_CONTEXT = {
    "tenant_id": "test-tenant-001",
    "tier": "professional",
    "status": "active",
    "billing_channel": "stripe",
    "has_stripe_billing": True,
    "shopify_shop_domain": None,
}

MOCK_TENANT_CONTEXT_STARTER = {
    **MOCK_TENANT_CONTEXT,
    "tier": "starter",
}

MOCK_TEAM_MEMBERS = {
    "members": [
        {
            "id": "tm-001",
            "email": "admin@testco.com",
            "displayName": "Test Admin",
            "role": "superadmin",
            "status": "active",
            "createdAt": "2026-01-15T10:00:00Z",
            "lastLoginAt": "2026-02-24T14:30:00Z",
            "escalationCategories": [],
            "unresolvedEscalationCount": 0,
        },
        {
            "id": "tm-002",
            "email": "agent@testco.com",
            "displayName": "Jane Agent",
            "role": "escalation_agent",
            "status": "active",
            "createdAt": "2026-02-01T09:00:00Z",
            "lastLoginAt": "2026-02-23T11:15:00Z",
            "escalationCategories": ["support", "technical"],
            "unresolvedEscalationCount": 3,
        },
        {
            "id": "tm-003",
            "email": "viewer@testco.com",
            "displayName": "View Only",
            "role": "viewer",
            "status": "active",
            "createdAt": "2026-02-10T08:00:00Z",
            "lastLoginAt": None,
            "escalationCategories": [],
            "unresolvedEscalationCount": 0,
        },
    ]
}

MOCK_CONFIG = {
    "config": {
        "brand_name": "TestCo",
        "brand_voice": "Professional and helpful",
        "formality": "balanced",
        "response_length": "standard",
        "language": "en",
        "custom_instructions": "Always greet customers by name when available.",
        "escalation_enabled": True,
        "escalation_threshold": 0.7,
        "escalation_categories": {
            "sales": {"enabled": True, "email": "sales@testco.com", "keywords": ["pricing", "discount", "bulk order", "quote"]},
            "support": {"enabled": True, "email": "support@testco.com", "keywords": ["not working", "broken", "help me", "issue"]},
            "service": {"enabled": True, "email": "service@testco.com", "keywords": ["refund", "return", "exchange", "cancel order"]},
            "account": {"enabled": True, "email": "", "keywords": ["my account", "password", "login", "subscription"]},
            "technical": {"enabled": False, "email": "", "keywords": ["api", "integration", "webhook", "developer"]},
            "general": {"enabled": True, "email": "hello@testco.com", "keywords": ["complaint", "manager", "supervisor"]},
        },
        "return_window": 30,
        "return_policy": "Full refund within 30 days of purchase.",
        "shipping_info": "Free standard shipping on orders over $50.",
        "idle_timeout_minutes": 30,
        "max_ai_turns_before_escalation": 50,
        "primary_language": "en",
        "additional_languages": ["en"],
        "widget_key": "pk_live_test123_abc456",
        "widget_primary_color": "#ff3621",
        "widget_header_gradient_end": "#8B1520",
        "widget_header_gradient_enabled": False,
        "widget_font_family": "Inter, system-ui, sans-serif",
        "widget_border_radius": 16,
        "widget_launcher_size": 60,
        "widget_launcher_icon": "chat",
        "widget_position": "bottom-right",
        "widget_position_offset_x": 20,
        "widget_position_offset_y": 20,
        "widget_shadow_intensity": "standard",
        "widget_panel_width": "standard",
        "widget_color_mode": "light",
        "widget_greeting_enabled": True,
        "widget_greeting_mode": "static",
        "widget_greeting_message": "Hi there! How can I help you today?",
        "widget_pre_chat_form_enabled": False,
        "widget_pre_chat_fields": ["name", "email"],
        "widget_sound_enabled": True,
        "widget_header_title": "Support",
        "widget_header_subtitle": "We typically reply within minutes",
        "widget_input_placeholder": "Type your message...",
        "widget_agent_avatar_url": "",
        "widget_agent_display_name": "Agent Red",
    },
    "draft": None,
    "activationStatus": {
        "status": "active",
        "lastActivatedAt": "2026-02-20T12:00:00Z",
        "pendingChanges": False,
    },
}

MOCK_CONFIG_WITH_DRAFT = {
    **MOCK_CONFIG,
    "draft": {
        "brand_name": "TestCo Updated",
        "brand_voice": "Friendly and casual",
    },
    "activationStatus": {
        "status": "draft",
        "lastActivatedAt": "2026-02-20T12:00:00Z",
        "pendingChanges": True,
    },
}

MOCK_KNOWLEDGE_BASE = {
    "articles": [
        {
            "id": "kb-001",
            "title": "Getting Started",
            "content": "Welcome to TestCo support.",
            "category": "general",
            "status": "published",
            "createdAt": "2026-01-20T10:00:00Z",
            "updatedAt": "2026-02-15T14:00:00Z",
        },
        {
            "id": "kb-002",
            "title": "Billing FAQ",
            "content": "Common billing questions answered.",
            "category": "billing",
            "status": "published",
            "createdAt": "2026-01-25T10:00:00Z",
            "updatedAt": "2026-02-10T09:00:00Z",
        },
    ],
    "totalCount": 2,
}

MOCK_WEBSITE_SOURCES = {
    "tenantId": "test-tenant-001",
    "sources": [
        {
            "id": "ws-001",
            "url": "https://testco.com",
            "domain": "testco.com",
            "maxPages": 50,
            "refreshHours": 168,
            "autoRefresh": True,
            "status": "completed",
            "lastCrawledAt": "2026-02-20T08:00:00Z",
            "pagesCrawled": 23,
            "pagesIngested": 23,
            "articlesCreated": 12,
        },
    ],
    "totalCount": 1,
}

MOCK_WIDGET_CONFIG = {
    "config": {
        "widget_primary_color": "#ff3621",
        "widget_background_color": "#FFFFFF",
        "widget_position": "bottom-right",
        "widget_agent_display_name": "Agent Red",
        "widget_agent_title": "AI Assistant",
        "widget_show_branding": True,
        "widget_dark_mode": False,
        "widget_color_mode": "light",
        "widget_greeting_enabled": True,
        "widget_greeting_message": "Hi there!",
        "widget_key": "pk_live_test123_abc456",
    },
    "widgetKey": "pk_live_test123_abc456",
}

MOCK_MEMORY_PRIVACY = {
    "settings": {
        "memoryEnabled": True,
        "conversationHistory": True,
        "crossSessionMemory": True,
        "piiScrubbing": False,
        "consentMode": "standard",
        "identificationMode": "gentle",
        "retentionDays": 90,
        "patternDecayDays": 180,
        "autoDeleteOnRequest": True,
    },
}

MOCK_ANALYTICS = {
    "overview": {
        "totalConversations": 142,
        "resolvedConversations": 128,
        "avgResponseTime": 2.3,
        "satisfactionScore": 4.2,
    },
    "daily": [],
}

MOCK_BILLING = {
    "plan": {
        "tier": "professional",
        "status": "active",
        "currentPeriodEnd": "2026-03-15T00:00:00Z",
        "conversationsUsed": 142,
        "conversationsLimit": 1000,
    },
}

MOCK_INBOX = {
    "conversations": [
        {
            "id": "conv-001",
            "customerName": "John Doe",
            "customerEmail": "john@example.com",
            "status": "open",
            "lastMessage": "I need help with my order",
            "createdAt": "2026-02-24T10:00:00Z",
            "updatedAt": "2026-02-24T10:05:00Z",
            "messageCount": 3,
        },
    ],
    "totalCount": 1,
}

MOCK_INTEGRATIONS = {
    "integrations": [],
}

MOCK_QUICK_ACTIONS = {
    "quickActions": [
        {
            "id": "qa-001",
            "label": "Track Order",
            "prompt": "Help me track my order",
            "enabled": True,
            "order": 0,
        },
    ],
}

MOCK_INGESTION_STATUS = {
    "status": "idle",
    "lastRun": "2026-02-20T08:00:00Z",
    "documentsIndexed": 25,
    "totalDocuments": 25,
}

# ---------------------------------------------------------------------------
# Dashboard-specific mock data — Analytics, Daily Volume, Intents, Gaps
# ---------------------------------------------------------------------------

MOCK_ANALYTICS_SUMMARY = {
    "tenantId": "test-tenant-001",
    "since": "2026-01-26T00:00:00Z",
    "until": "2026-02-26T00:00:00Z",
    "totalConversations": 142,
    "billableConversations": 128,
    "avgTurns": 4.5,
    "avgMessages": 8.2,
    "avgResponseTime": 2.3,
    "resolutionRate": 0.901,
    "customerSatisfaction": 4.2,
    "statusBreakdown": [
        {"status": "ended", "count": 110},
        {"status": "escalated", "count": 18},
        {"status": "active", "count": 14},
    ],
    "escalationCount": 18,
    "escalationRate": 0.127,
    "criticPassed": 135,
    "criticFailed": 7,
}

MOCK_DAILY_VOLUME = {
    "days": [
        {"date": "2026-02-24", "total": 12, "billable": 10},
        {"date": "2026-02-25", "total": 15, "billable": 14},
        {"date": "2026-02-26", "total": 8, "billable": 7},
    ],
}

MOCK_INTENT_BREAKDOWN = {
    "intents": [
        {"agent": "order-tracking", "invocationCount": 45, "percentage": 31.7},
        {"agent": "product-inquiry", "invocationCount": 38, "percentage": 26.8},
        {"agent": "return-refund", "invocationCount": 25, "percentage": 17.6},
        {"agent": "billing-support", "invocationCount": 20, "percentage": 14.1},
        {"agent": "general-faq", "invocationCount": 14, "percentage": 9.9},
    ],
}

MOCK_KNOWLEDGE_GAPS_DATA = {
    "gaps": [
        {
            "conversationId": "conv-gap-001",
            "status": "escalated",
            "customerId": "cust-101",
            "turnCount": 6,
            "messageCount": 12,
            "agentsInvoked": ["product-inquiry"],
            "criticPassed": False,
            "startedAt": "2026-02-24T09:00:00Z",
            "endedAt": "2026-02-24T09:15:00Z",
        },
        {
            "conversationId": "conv-gap-002",
            "status": "ended",
            "customerId": None,
            "turnCount": 3,
            "messageCount": 6,
            "agentsInvoked": ["general-faq"],
            "criticPassed": False,
            "startedAt": "2026-02-25T14:00:00Z",
            "endedAt": None,
        },
    ],
}

MOCK_INBOX_CONVERSATIONS = {
    "conversations": [
        {
            "conversationId": "conv-001",
            "customerId": "cust-001",
            "customerName": "John Doe",
            "status": "active",
            "assignedTo": None,
            "messageCount": 3,
            "turnCount": 2,
            "startedAt": "2026-02-24T10:00:00Z",
            "endedAt": None,
            "lastActivityAt": "2026-02-24T10:05:00Z",
            "isBillable": True,
            "agentsInvoked": ["order-tracking"],
            "modelUsed": "gpt-4o",
            "criticPassed": True,
            "escalationCategory": None,
            "archivedAt": None,
            "customerVerified": True,
            "identityEmail": "john@example.com",
        },
        {
            "conversationId": "conv-002",
            "customerId": "cust-002",
            "customerName": "Jane Smith",
            "status": "escalated",
            "assignedTo": "Jane Agent",
            "messageCount": 8,
            "turnCount": 5,
            "startedAt": "2026-02-23T14:00:00Z",
            "endedAt": None,
            "lastActivityAt": "2026-02-23T15:30:00Z",
            "isBillable": True,
            "agentsInvoked": ["billing-support"],
            "modelUsed": "gpt-4o",
            "criticPassed": False,
            "escalationCategory": "billing",
            "archivedAt": None,
            "customerVerified": False,
            "identityEmail": None,
        },
        {
            "conversationId": "conv-003",
            "customerId": "cust-003",
            "customerName": "Bob Wilson",
            "status": "ended",
            "assignedTo": None,
            "messageCount": 4,
            "turnCount": 3,
            "startedAt": "2026-02-22T09:00:00Z",
            "endedAt": "2026-02-22T09:12:00Z",
            "lastActivityAt": "2026-02-22T09:12:00Z",
            "isBillable": True,
            "agentsInvoked": ["general-faq"],
            "modelUsed": "gpt-4o",
            "criticPassed": True,
            "escalationCategory": None,
            "archivedAt": None,
            "customerVerified": True,
            "identityEmail": "bob@example.com",
        },
    ],
}

# ---------------------------------------------------------------------------
# Configuration page — Named configs + KB suggestions
# ---------------------------------------------------------------------------

MOCK_NAMED_CONFIGS = {
    "configs": [
        {
            "name": "Default",
            "version": 1,
            "isActive": True,
            "isDefault": True,
            "createdAt": "2026-02-15T10:00:00Z",
            "createdBy": "admin@testco.com",
            "fieldCount": 14,
        },
        {
            "name": "Holiday",
            "version": 2,
            "isActive": False,
            "isDefault": False,
            "createdAt": "2026-02-20T15:30:00Z",
            "createdBy": "admin@testco.com",
            "fieldCount": 14,
        },
        {
            "name": "Black Friday",
            "version": 1,
            "isActive": False,
            "isDefault": False,
            "createdAt": "2026-02-22T09:00:00Z",
            "createdBy": "admin@testco.com",
            "fieldCount": 12,
        },
    ],
    "total": 3,
}

MOCK_CONFIG_SUGGESTIONS = {
    "brand_name": {
        "value": "TestCo Store",
        "confidence": 0.85,
        "source": "website-crawl",
    },
    "brand_voice": {
        "value": "Friendly and professional tone with a focus on customer satisfaction",
        "confidence": 0.72,
        "source": "website-crawl",
    },
    "return_policy": {
        "value": "30-day hassle-free returns on all items",
        "confidence": 0.65,
        "source": "faq-analysis",
    },
    "shipping_info": {
        "value": "Free shipping on orders over $50. Standard delivery 3-5 business days.",
        "confidence": 0.60,
        "source": "faq-analysis",
    },
}


# ---------------------------------------------------------------------------
# API Route Handler
# ---------------------------------------------------------------------------

class AdminApiMocker:
    """Manages Playwright route interception for all admin API endpoints.

    Provides deterministic responses and records all API calls for assertion.
    Tests can override specific responses before navigating.
    """

    def __init__(self, tier: str = "professional") -> None:
        self.tier = tier
        self.api_calls: list[dict[str, Any]] = []
        self._overrides: dict[str, Any] = {}

    def override(self, endpoint_pattern: str, response: Any, status: int = 200) -> None:
        """Override the response for a specific endpoint pattern."""
        self._overrides[endpoint_pattern] = {"body": response, "status": status}

    def get_calls(self, method: str | None = None, path_contains: str | None = None) -> list[dict]:
        """Filter recorded API calls."""
        result = self.api_calls
        if method:
            result = [c for c in result if c["method"] == method]
        if path_contains:
            result = [c for c in result if path_contains in c["url"]]
        return result

    def clear_calls(self) -> None:
        """Clear recorded API calls."""
        self.api_calls.clear()

    def handle_route(self, route: Route) -> None:
        """Route handler for all /api/* requests."""
        url = route.request.url
        method = route.request.method
        path = url.split("/api/")[-1] if "/api/" in url else url

        # Record the call
        call_record = {
            "url": url,
            "method": method,
            "path": path,
        }
        # Capture POST/PUT body
        if method in ("POST", "PUT", "PATCH"):
            try:
                call_record["body"] = route.request.post_data
            except Exception:
                call_record["body"] = None
        self.api_calls.append(call_record)

        # Check overrides first
        for pattern, override in self._overrides.items():
            if pattern in url:
                route.fulfill(
                    status=override["status"],
                    content_type="application/json",
                    body=json.dumps(override["body"]) if not isinstance(override["body"], str) else override["body"],
                )
                return

        # Default route matching
        context = MOCK_TENANT_CONTEXT if self.tier != "starter" else MOCK_TENANT_CONTEXT_STARTER

        if "/api/tenants/lookup" in url or "/api/admin/context" in url:
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps(context))
        elif "/api/admin/team/whoami" in url and method == "GET":
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps({"role": "superadmin", "email": "admin@testco.com"}))
        elif "/api/config/activation-status" in url and method == "GET":
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps({
                              "status": "active",
                              "is_configured": True,
                              "is_active": True,
                              "can_activate": True,
                              "has_pending_changes": False,
                              "active_version": 1,
                              "active_activated_at": "2026-02-20T12:00:00Z",
                              "draft_version": None,
                              "draft_saved_at": None,
                              "pending_changes": False,
                          }))
        elif "/api/admin/team" in url and method == "GET":
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps(MOCK_TEAM_MEMBERS))
        elif re.search(r"/api/admin/team/[^/]+/resend-invite", url) and method == "POST":
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps({"message": "Invitation re-sent"}))
        elif "/api/admin/team" in url and method == "POST":
            # Create team member — echo back with generated ID
            route.fulfill(status=201, content_type="application/json",
                          body=json.dumps({"id": "tm-new-001", "message": "Team member invited"}))
        elif re.search(r"/api/admin/team/[^/]+$", url) and method == "PUT":
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps({"message": "Updated"}))
        elif re.search(r"/api/admin/team/[^/]+$", url) and method == "DELETE":
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps({"message": "Removed"}))
        # --- Named configurations (must come before generic /api/config GET) ---
        elif re.search(r"/api/config/named/[^/]+/activate", url) and method == "POST":
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps({"message": "Configuration activated"}))
        elif re.search(r"/api/config/named/[^/]+$", url) and method == "DELETE":
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps({"message": "Configuration deleted"}))
        elif "/api/config/named" in url and method == "GET":
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps(MOCK_NAMED_CONFIGS))
        elif "/api/config/named" in url and method == "POST":
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps({"message": "Configuration saved", "name": "New Config"}))
        elif ("/api/admin/config" in url or "/api/config" in url) and method == "GET" and "activation-status" not in url:
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps(MOCK_CONFIG))
        elif ("/api/admin/config" in url or "/api/config" in url) and method == "PUT" and "activation-status" not in url:
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps({"message": "Draft saved", "version": 2}))
        elif "/api/admin/config/draft" in url and method in ("POST", "PUT"):
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps({"message": "Draft saved"}))
        elif "/api/admin/config/activate" in url and method == "POST":
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps({"message": "Configuration activated"}))
        elif "/api/admin/knowledge/suggestions" in url and method == "GET":
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps(MOCK_CONFIG_SUGGESTIONS))
        elif "/api/admin/knowledge/sources" in url and method == "GET":
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps(MOCK_WEBSITE_SOURCES))
        elif "/api/admin/knowledge" in url and method == "GET":
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps(MOCK_KNOWLEDGE_BASE))
        elif "/api/admin/widget" in url and method == "GET":
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps(MOCK_WIDGET_CONFIG))
        elif "/api/admin/memory-privacy" in url and method == "GET":
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps(MOCK_MEMORY_PRIVACY))
        elif "/api/admin/memory-privacy" in url and method in ("POST", "PUT"):
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps({"message": "Settings saved"}))
        # --- Dashboard analytics endpoints (non-admin prefix) ---
        elif "/api/analytics/summary" in url and method == "GET":
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps(MOCK_ANALYTICS_SUMMARY))
        elif "/api/analytics/intents" in url and method == "GET":
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps(MOCK_INTENT_BREAKDOWN))
        elif "/api/analytics/gaps" in url and method == "GET":
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps(MOCK_KNOWLEDGE_GAPS_DATA))
        elif "/api/dashboard/usage/daily" in url and method == "GET":
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps(MOCK_DAILY_VOLUME))
        elif "/api/dashboard/usage" in url and method == "GET":
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps(MOCK_ANALYTICS_SUMMARY))
        elif "/api/admin/analytics" in url and method == "GET":
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps(MOCK_ANALYTICS))
        elif "/api/admin/billing" in url and method == "GET":
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps(MOCK_BILLING))
        elif "/api/admin/inbox" in url or "/api/admin/conversations" in url:
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps(MOCK_INBOX_CONVERSATIONS))
        elif "/api/admin/integrations" in url and method == "GET":
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps(MOCK_INTEGRATIONS))
        elif "/api/admin/quick-actions" in url and method == "GET":
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps(MOCK_QUICK_ACTIONS))
        elif "/api/admin/ingestion" in url and method == "GET":
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps(MOCK_INGESTION_STATUS))
        elif "/api/config" in url:
            # Widget config endpoint
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps({"config": MOCK_WIDGET_CONFIG.get("config", {})}))
        else:
            # Catch-all: return 200 with empty object to avoid network errors
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps({}))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _port_is_open(port: int, host: str = "localhost") -> bool:
    """Check if a TCP port is accepting connections."""
    for family, addr in [
        (socket.AF_INET, "127.0.0.1"),
        (socket.AF_INET6, "::1"),
    ]:
        try:
            with socket.socket(family, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect((addr, port))
                return True
        except (ConnectionRefusedError, OSError):
            continue
    return False


# ---------------------------------------------------------------------------
# Session-scoped fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def admin_vite_server():
    """Start the Vite dev server for the standalone admin.

    Launches ``npm run dev`` in ``admin/standalone/`` and waits up to 30 s
    for port 3300 to accept connections.  Tears down on session end.
    """
    node_modules = ADMIN_DIR / "node_modules"
    if not node_modules.exists():
        pytest.skip("admin/standalone/node_modules not found — run `cd admin/standalone && npm install`")

    # Reuse existing server if running
    if _port_is_open(ADMIN_VITE_PORT):
        yield None
        return

    creation_flags = 0
    if sys.platform == "win32":
        creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP

    env = {**os.environ, "VITE_API_URL": ""}  # no proxy — all routes mocked
    proc = subprocess.Popen(
        "npm run dev",
        cwd=str(ADMIN_DIR),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=creation_flags,
        env=env,
    )

    for _ in range(30):
        if _port_is_open(ADMIN_VITE_PORT):
            break
        if proc.poll() is not None:
            stdout = proc.stdout.read().decode(errors="replace") if proc.stdout else ""
            stderr = proc.stderr.read().decode(errors="replace") if proc.stderr else ""
            raise RuntimeError(
                f"Admin Vite dev server exited with code {proc.returncode}.\n"
                f"stdout: {stdout}\nstderr: {stderr}"
            )
        time.sleep(1)
    else:
        proc.kill()
        raise RuntimeError(f"Admin Vite server did not start on port {ADMIN_VITE_PORT} within 30 s")

    yield proc

    # Teardown
    if sys.platform == "win32":
        try:
            os.kill(proc.pid, signal.CTRL_BREAK_EVENT)
            proc.wait(timeout=5)
        except (OSError, subprocess.TimeoutExpired):
            subprocess.run(f"taskkill /F /T /PID {proc.pid}", shell=True, capture_output=True)
    else:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()


# ---------------------------------------------------------------------------
# Per-test fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def api_mocker() -> AdminApiMocker:
    """Return a fresh AdminApiMocker for intercepting API calls."""
    return AdminApiMocker(tier="professional")


@pytest.fixture()
def api_mocker_starter() -> AdminApiMocker:
    """Return a fresh AdminApiMocker configured for Starter tier."""
    return AdminApiMocker(tier="starter")


@pytest.fixture()
def admin_page(page: Page, admin_vite_server, api_mocker: AdminApiMocker) -> Page:
    """Navigate to the admin SPA with all API calls mocked.

    Bypasses the login screen by injecting a session storage API key
    before ANY JavaScript runs (via add_init_script).  Returns the
    Playwright Page after the dashboard has loaded.

    The ``api_mocker`` is attached to the page as ``page._api_mocker``
    for tests to inspect recorded API calls.
    """
    # Intercept all API calls
    page.route("**/api/**", api_mocker.handle_route)

    # Inject auth into sessionStorage BEFORE any page script executes.
    # This ensures the React app sees the key on its first render cycle
    # and skips the login page entirely.
    page.add_init_script("""
        sessionStorage.setItem('agentred_api_key', 'ar_test_key_for_e2e_testing');
    """)

    # Navigate to the admin SPA — app will read the key immediately
    page.goto(
        f"http://localhost:{ADMIN_VITE_PORT}/admin/standalone/",
        wait_until="networkidle",
    )

    # Wait for the layout to render (sidebar should be visible)
    page.wait_for_selector("text=Dashboard", timeout=15_000)

    # Attach mocker to page for test access
    page._api_mocker = api_mocker  # type: ignore[attr-defined]

    return page


def setup_admin_page(page: Page, api_mocker: AdminApiMocker) -> Page:
    """Set up an admin page with custom API mocker (for inline test setups).

    Use this in tests that need non-default mock responses. Sets up route
    interception, injects auth, and navigates to the admin SPA.
    """
    page.route("**/api/**", api_mocker.handle_route)
    page.add_init_script("""
        sessionStorage.setItem('agentred_api_key', 'ar_test_key_for_e2e_testing');
    """)
    page.goto(
        f"http://localhost:{ADMIN_VITE_PORT}/admin/standalone/",
        wait_until="networkidle",
    )
    page.wait_for_selector("text=Dashboard", timeout=15_000)
    page._api_mocker = api_mocker  # type: ignore[attr-defined]
    return page


def _navigate_admin_to(page: Page, nav_text: str, wait_for_text: str | None = None) -> Page:
    """Click a sidebar nav link and wait for the page to load."""
    # Click the nav link in the sidebar
    nav_link = page.locator(f'nav >> text="{nav_text}"').first
    if not nav_link.is_visible():
        # Fallback: try without nav scope
        nav_link = page.get_by_text(nav_text, exact=True).first
    nav_link.click()

    if wait_for_text:
        page.wait_for_selector(f"text={wait_for_text}", timeout=5_000)

    # Small settle time for React state
    page.wait_for_timeout(300)
    return page


@pytest.fixture()
def admin_team_page(admin_page: Page) -> Page:
    """Navigate to the Team page."""
    return _navigate_admin_to(admin_page, "Team members", "Team members")


@pytest.fixture()
def admin_config_page(admin_page: Page) -> Page:
    """Navigate to the Configuration page."""
    return _navigate_admin_to(admin_page, "Agent configuration", "Configuration")


@pytest.fixture()
def admin_memory_page(admin_page: Page) -> Page:
    """Navigate to the Memory & Privacy page."""
    return _navigate_admin_to(admin_page, "Memory & privacy", "Memory")


@pytest.fixture()
def admin_widget_page(admin_page: Page) -> Page:
    """Navigate to the Widget page."""
    return _navigate_admin_to(admin_page, "Widget configuration", "Widget")


@pytest.fixture()
def admin_kb_page(admin_page: Page) -> Page:
    """Navigate to the Knowledge Base page."""
    return _navigate_admin_to(admin_page, "Knowledge base", "Knowledge")


@pytest.fixture()
def admin_inbox_page(admin_page: Page) -> Page:
    """Navigate to the Inbox page."""
    return _navigate_admin_to(admin_page, "Inbox", "Inbox")


@pytest.fixture()
def admin_billing_page(admin_page: Page) -> Page:
    """Navigate to the Billing page."""
    return _navigate_admin_to(admin_page, "Billing", "Billing")


@pytest.fixture()
def admin_quick_actions_page(admin_page: Page) -> Page:
    """Navigate to the Quick Actions page."""
    return _navigate_admin_to(admin_page, "Quick actions", "Quick actions")


@pytest.fixture()
def admin_integrations_page(admin_page: Page) -> Page:
    """Navigate to the Integrations page."""
    # Integrations page may not have a visible heading — just navigate and settle
    return _navigate_admin_to(admin_page, "Integrations", None)
