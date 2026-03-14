"""
seed_midflight.py — Populate a staging tenant with realistic mid-flight data.

Unlike seed_tenant.py (which creates a fresh, empty tenant for first-use
wizard testing), this script adds the data a tenant would have after weeks
of active use: team members, conversations, KB articles, quick actions,
and a fully-configured draft/active configuration.

This enables E2E tests that validate:
  - CRUD operations on pre-existing data
  - Data display areas (dashboard stats, inbox, KB list, team table)
  - Search and filtering on populated datasets
  - Period filters with historical conversation data
  - Widget key rotation and configuration

Usage:
    python scripts/seed_midflight.py [--env staging] [--tenant remaker-digital-001]

Prerequisites:
    - Target tenant already provisioned (via seed_tenant.py)
    - API key for the target tenant in .env.local
    - Target environment deployed and healthy

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import uuid
from datetime import datetime, timedelta, timezone

import httpx

# ---------------------------------------------------------------------------
# Auto-load .env.local
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scripts._env import load_env_local

load_env_local()

# ---------------------------------------------------------------------------
# Environment configuration
# ---------------------------------------------------------------------------

ENVIRONMENTS = {
    "staging": {
        "base_url": "https://agent-red-staging.orangeglacier-f566a4e7.eastus.azurecontainerapps.io",
        # SPEC-1667: SPA keys (ar_spa_plat_*) are blocked from /api/admin/*.
        # Seed script MUST use tenant user keys (ar_user_*) for admin API calls.
        "api_key": (
            os.environ.get("STAGING_REMAKER_USER_KEY", "")
            or os.environ.get("STAGING_REMAKER_DIGITAL_001_SUPERADMIN_KEY", "")
            or os.environ.get("SUPERADMIN_PREVIEW_API_KEY", "")
        ),
        "widget_key": (
            os.environ.get("STAGING_REMAKER_WIDGET_KEY", "")
            or os.environ.get("PREVIEW_WIDGET_KEY", "")
        ),
        "tenant_id": "remaker-digital-001",
    },
    "production": {
        "base_url": "https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io",
        "api_key": (
            os.environ.get("PRODUCTION_REMAKER_USER_KEY", "")
            or os.environ.get("SUPERADMIN_PREVIEW_API_KEY", "")
        ),
        "widget_key": (
            os.environ.get("PRODUCTION_REMAKER_WIDGET_KEY", "")
            or os.environ.get("PREVIEW_WIDGET_KEY", "")
        ),
        "tenant_id": "remaker-digital-001",
    },
}

# ---------------------------------------------------------------------------
# Realistic test data
# ---------------------------------------------------------------------------

TEAM_MEMBERS = [
    {
        "email": "sarah.chen@example.com",
        "displayName": "Sarah Chen",
        "role": "admin",
        "escalationCategories": [],
        "maxConcurrentConversations": 10,
    },
    {
        "email": "james.williams@example.com",
        "displayName": "James Williams",
        "role": "escalation_agent",
        "escalationCategories": ["service", "support", "technical_assistance"],
        "maxConcurrentConversations": 5,
    },
    {
        "email": "maria.garcia@example.com",
        "displayName": "Maria Garcia",
        "role": "escalation_agent",
        "escalationCategories": ["sales", "account", "general_inquiry"],
        "maxConcurrentConversations": 8,
    },
    {
        "email": "alex.johnson@example.com",
        "displayName": "Alex Johnson",
        "role": "viewer",
        "escalationCategories": [],
        "maxConcurrentConversations": 5,
    },
]

KB_ARTICLES = [
    {
        "entryType": "faq",
        "title": "How do I track my order?",
        "content": (
            "You can track your order by visiting the Order Status page on our website. "
            "Enter your order number and the email address you used during checkout. "
            "You will see the current status, estimated delivery date, and tracking number "
            "once your order has shipped. Most orders ship within 1-2 business days."
        ),
        "category": "Shipping",
        "status": "published",
        "metadata": {"tags": ["tracking", "orders", "shipping"]},
    },
    {
        "entryType": "policy",
        "title": "Return and Refund Policy",
        "content": (
            "We offer a 30-day return policy for all unused items in their original packaging. "
            "To initiate a return, contact our support team with your order number. "
            "Refunds are processed within 5-7 business days after we receive the returned item. "
            "Shipping costs for returns are the responsibility of the customer unless the item "
            "was defective or we made an error. Exchanges are available for size and color changes."
        ),
        "category": "Returns",
        "status": "published",
        "metadata": {"tags": ["returns", "refunds", "exchanges"]},
    },
    {
        "entryType": "faq",
        "title": "What payment methods do you accept?",
        "content": (
            "We accept all major credit cards (Visa, Mastercard, American Express, Discover), "
            "PayPal, Apple Pay, Google Pay, and Shop Pay. All transactions are encrypted and "
            "secured with PCI-DSS compliant payment processing. We do not store credit card "
            "information on our servers."
        ),
        "category": "Payments",
        "status": "published",
        "metadata": {"tags": ["payments", "credit cards", "security"]},
    },
    {
        "entryType": "product",
        "title": "Premium Wireless Headphones - Model X1",
        "content": (
            "The Premium Wireless Headphones Model X1 feature active noise cancellation, "
            "40-hour battery life, Bluetooth 5.3 connectivity, and memory foam ear cushions. "
            "Available in Black, White, and Navy Blue. Includes USB-C charging cable, "
            "3.5mm audio cable, and carrying case. Weight: 250g. Driver: 40mm custom. "
            "Price: $149.99. Free shipping on orders over $75."
        ),
        "category": "Product Info",
        "status": "published",
        "metadata": {
            "product_id": "WH-X1-2026",
            "price": 149.99,
            "tags": ["headphones", "wireless", "audio"],
        },
    },
    {
        "entryType": "product",
        "title": "Ergonomic Bluetooth Keyboard - K7",
        "content": (
            "The Ergonomic Bluetooth Keyboard K7 offers a split-key design for comfortable typing, "
            "multi-device pairing (up to 3 devices), backlit keys, and a rechargeable battery "
            "lasting up to 6 months. Compatible with Windows, macOS, iOS, and Android. "
            "Available in Space Gray and Silver. Price: $89.99."
        ),
        "category": "Product Info",
        "status": "published",
        "metadata": {
            "product_id": "KB-K7-2026",
            "price": 89.99,
            "tags": ["keyboard", "bluetooth", "ergonomic"],
        },
    },
    {
        "entryType": "faq",
        "title": "Do you offer international shipping?",
        "content": (
            "Yes, we ship to over 50 countries worldwide. International shipping rates are "
            "calculated at checkout based on destination and package weight. Standard international "
            "delivery takes 7-14 business days. Express international shipping (3-5 business days) "
            "is available for an additional fee. Import duties and taxes may apply and are the "
            "responsibility of the recipient."
        ),
        "category": "Shipping",
        "status": "published",
        "metadata": {"tags": ["international", "shipping", "delivery"]},
    },
    {
        "entryType": "policy",
        "title": "Warranty Information",
        "content": (
            "All electronics products come with a 2-year manufacturer warranty covering defects "
            "in materials and workmanship. Accessories carry a 1-year warranty. Warranty claims "
            "require proof of purchase. Physical damage, water damage, and unauthorized modifications "
            "are not covered. Contact our support team to initiate a warranty claim."
        ),
        "category": "Warranty",
        "status": "published",
        "metadata": {"tags": ["warranty", "guarantee", "defects"]},
    },
    {
        "entryType": "faq",
        "title": "How do I contact customer support?",
        "content": (
            "You can reach our customer support team through: (1) Live chat on our website "
            "(available 24/7 via our AI assistant), (2) Email at support@example.com "
            "(response within 24 hours), (3) Phone at 1-800-555-0123 (Mon-Fri 9am-6pm EST). "
            "For urgent issues, live chat provides the fastest response time."
        ),
        "category": "Support",
        "status": "published",
        "metadata": {"tags": ["contact", "support", "help"]},
    },
    {
        "entryType": "article",
        "title": "Setting Up Your New Device - Quick Start Guide",
        "content": (
            "Welcome to your new device! Follow these steps: (1) Charge your device fully "
            "before first use (approximately 2 hours). (2) Download our companion app from "
            "the App Store or Google Play. (3) Enable Bluetooth on your phone or computer. "
            "(4) Press and hold the power button for 3 seconds to enter pairing mode. "
            "(5) Select your device from the Bluetooth menu. Setup complete!"
        ),
        "category": "Getting Started",
        "status": "published",
        "metadata": {"tags": ["setup", "quick start", "guide"]},
    },
    {
        "entryType": "article",
        "title": "Troubleshooting Bluetooth Connectivity",
        "content": (
            "If you are experiencing Bluetooth connectivity issues: (1) Ensure Bluetooth is "
            "enabled on both devices. (2) Move devices within 30 feet of each other. "
            "(3) Remove the device from your Bluetooth list and re-pair. (4) Restart both "
            "devices. (5) Check for firmware updates in our companion app. (6) Ensure no "
            "other device is actively connected. If issues persist, contact support."
        ),
        "category": "Troubleshooting",
        "status": "draft",
        "metadata": {"tags": ["bluetooth", "troubleshooting", "connectivity"]},
    },
    {
        "entryType": "faq",
        "title": "Can I cancel or modify my order?",
        "content": (
            "Orders can be cancelled or modified within 1 hour of placement. After that, "
            "our fulfillment process begins and changes cannot be guaranteed. To request a "
            "modification, contact support immediately with your order number. If your order "
            "has already shipped, you may need to initiate a return instead."
        ),
        "category": "Orders",
        "status": "published",
        "metadata": {"tags": ["cancel", "modify", "orders"]},
    },
    {
        "entryType": "article",
        "title": "Seasonal Sale - Spring 2026 Collection",
        "content": (
            "Our Spring 2026 collection is here! Enjoy 20% off all new arrivals through "
            "April 30, 2026. Use code SPRING26 at checkout. Free shipping on orders over $50 "
            "during the sale period. New items include the X2 headphones, K8 keyboard, and "
            "M3 mouse. Bundle deals available for even greater savings."
        ),
        "category": "Promotions",
        "status": "archived",
        "metadata": {"tags": ["sale", "promotion", "spring"]},
    },
]

QUICK_ACTIONS = [
    {
        "label": "Track my order",
        "promptTemplate": "I would like to track my recent order. Can you help me find the current status and estimated delivery date?",
        "icon": "📦",
        "isActive": True,
        "sortOrder": 0,
    },
    {
        "label": "Start a return",
        "promptTemplate": "I need to return or exchange an item from a recent purchase. Can you walk me through the return process?",
        "icon": "↩️",
        "isActive": True,
        "sortOrder": 1,
    },
    {
        "label": "Product question",
        "promptTemplate": "I have a question about one of your products. Can you help me with product details, compatibility, or availability?",
        "icon": "❓",
        "isActive": True,
        "sortOrder": 2,
    },
    {
        "label": "Shipping info",
        "promptTemplate": "I have a question about shipping options, delivery times, or international shipping availability.",
        "icon": "🚚",
        "isActive": True,
        "sortOrder": 3,
    },
    {
        "label": "Talk to a person",
        "promptTemplate": "I would like to speak with a human support agent about my issue. Please connect me with someone who can help.",
        "icon": "👤",
        "isActive": True,
        "sortOrder": 4,
    },
]

DRAFT_CONFIG = {
    "brand_name": "TechGear Store",
    "brand_voice": "We are a friendly, knowledgeable consumer electronics retailer. We speak in a warm, helpful tone and always try to resolve customer issues quickly. We use clear, simple language and avoid jargon.",
    "custom_instructions": "Always greet the customer warmly. If a customer asks about a product we don't carry, suggest similar alternatives. Never share internal pricing or margin information. If a customer is frustrated, acknowledge their feelings before offering solutions.",
    "return_policy": "30-day return policy for unused items in original packaging. Refunds processed within 5-7 business days. Customer pays return shipping unless item is defective.",
    "shipping_info": "Free shipping on orders over $75. Standard delivery 3-5 business days. Express delivery 1-2 business days ($12.99). International shipping to 50+ countries, 7-14 business days.",
    "escalation_email": "escalations@example.com",
    "escalation_threshold": 0.65,
    "escalation_keywords": ["lawsuit", "lawyer", "attorney", "complaint", "manager", "supervisor", "refund", "fraud"],
    "widget_primary_color": "#2563eb",
    "widget_background_color": "#1a1a2e",
    "widget_position": "bottom-right",
    "widget_greeting": "Hi there! 👋 How can I help you today?",
    "widget_placeholder": "Type your message...",
    "widget_subtitle": "Powered by AI • Usually responds instantly",
    "agent_name": "TechGear Assistant",
    "agent_avatar_type": "initials",
    "gradient_enabled": True,
    "widget_page_rules": [],
}

# Simulated conversation messages for historical data
CONVERSATION_SCENARIOS = [
    {
        "initial_message": "Hi, I ordered a pair of headphones last week and haven't received them yet. Order #WH-8842.",
        "page_url": "https://techgearstore.com/products/wireless-headphones",
    },
    {
        "initial_message": "Do you have the Bluetooth keyboard in a white color option?",
        "page_url": "https://techgearstore.com/products/keyboard-k7",
    },
    {
        "initial_message": "I want to return a defective mouse I received yesterday.",
        "page_url": "https://techgearstore.com/support",
    },
    {
        "initial_message": "What's the difference between the X1 and X2 headphone models?",
        "page_url": "https://techgearstore.com/compare",
    },
    {
        "initial_message": "Can I use my spring sale coupon with the bundle deal?",
        "page_url": "https://techgearstore.com/deals",
    },
]


# ---------------------------------------------------------------------------
# API client
# ---------------------------------------------------------------------------


class SeedClient:
    """Thin HTTP client for seeding data via the Agent Red REST API."""

    def __init__(self, base_url: str, api_key: str, widget_key: str, tenant_id: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.widget_key = widget_key
        self.tenant_id = tenant_id
        self.client = httpx.Client(timeout=30.0)
        self._request_count = 0
        self._rate_limit_pause = 1.5  # seconds between requests to avoid 429s

    def _admin_headers(self) -> dict[str, str]:
        return {"X-API-Key": self.api_key, "Content-Type": "application/json"}

    def _widget_headers(self) -> dict[str, str]:
        return {"X-Widget-Key": self.widget_key, "Content-Type": "application/json"}

    def _throttle(self):
        """Rate-limit-safe pause between requests."""
        self._request_count += 1
        if self._request_count % 10 == 0:
            time.sleep(self._rate_limit_pause * 2)
        else:
            time.sleep(self._rate_limit_pause)

    def admin_get(self, path: str) -> httpx.Response:
        self._throttle()
        return self.client.get(
            f"{self.base_url}{path}", headers=self._admin_headers()
        )

    def admin_post(self, path: str, json_data: dict) -> httpx.Response:
        self._throttle()
        return self.client.post(
            f"{self.base_url}{path}", headers=self._admin_headers(), json=json_data
        )

    def admin_put(self, path: str, json_data: dict) -> httpx.Response:
        self._throttle()
        return self.client.put(
            f"{self.base_url}{path}", headers=self._admin_headers(), json=json_data
        )

    def admin_delete(self, path: str) -> httpx.Response:
        self._throttle()
        return self.client.delete(
            f"{self.base_url}{path}", headers=self._admin_headers()
        )

    def widget_post(self, path: str, json_data: dict) -> httpx.Response:
        self._throttle()
        return self.client.post(
            f"{self.base_url}{path}", headers=self._widget_headers(), json=json_data
        )

    def close(self):
        self.client.close()


# ---------------------------------------------------------------------------
# Seed phases
# ---------------------------------------------------------------------------


def phase_0_health_check(client: SeedClient) -> bool:
    """Verify the target environment is healthy and authenticated."""
    print("\n" + "=" * 60)
    print("Phase 0: Health Check & Authentication")
    print("=" * 60)

    # Health check
    r = client.client.get(f"{client.base_url}/health")
    if r.status_code != 200:
        print(f"  FAIL  Health check returned {r.status_code}")
        return False
    health = r.json()
    print(f"  OK    Health: {health.get('status')} (v{health.get('product_version')})")

    # Auth check
    r = client.admin_get("/api/admin/team?limit=1")
    if r.status_code == 401:
        print(f"  FAIL  API key authentication failed (401)")
        print(f"        Key prefix: {client.api_key[:20]}...")
        return False
    if r.status_code == 429:
        print(f"  WARN  Rate limited (429) — waiting 60s")
        time.sleep(60)
        r = client.admin_get("/api/admin/team?limit=1")
    if r.status_code != 200:
        print(f"  FAIL  Team list returned {r.status_code}: {r.text[:200]}")
        return False
    print(f"  OK    Authentication successful")

    # Widget key check
    r = client.widget_post("/api/chat/conversations", {"initialMessage": "health check"})
    if r.status_code in (200, 201):
        print(f"  OK    Widget key valid")
        # End the health check conversation
        conv_id = r.json().get("conversationId") or r.json().get("conversation_id")
        if conv_id:
            client.widget_post(f"/api/chat/conversations/{conv_id}/end", {})
    elif r.status_code == 401:
        print(f"  WARN  Widget key invalid (401) — conversations won't be seeded")
    else:
        print(f"  WARN  Conversation start returned {r.status_code}")

    return True


def phase_1_cleanup(client: SeedClient) -> dict:
    """Remove any previously-seeded test data to ensure idempotency."""
    print("\n" + "=" * 60)
    print("Phase 1: Cleanup Previous Seed Data")
    print("=" * 60)

    cleaned = {"team": 0, "kb": 0, "quick_actions": 0}

    # Clean up seeded team members (by known test emails)
    test_emails = {m["email"] for m in TEAM_MEMBERS}
    r = client.admin_get("/api/admin/team?limit=100")
    if r.status_code == 200:
        members = r.json().get("members") or r.json().get("items") or []
        for member in members:
            email = member.get("email", "")
            member_id = member.get("id", "")
            if email in test_emails and member_id:
                dr = client.admin_delete(f"/api/admin/team/{member_id}")
                if dr.status_code in (200, 204):
                    cleaned["team"] += 1
                    print(f"  DEL   Team member: {email}")

    # Clean up seeded KB articles (by known test titles)
    test_titles = {a["title"] for a in KB_ARTICLES}
    r = client.admin_get("/api/admin/knowledge?limit=100")
    if r.status_code == 200:
        articles = r.json().get("articles") or r.json().get("items") or []
        for article in articles:
            title = article.get("title", "")
            article_id = article.get("id", "")
            if title in test_titles and article_id:
                dr = client.admin_delete(f"/api/admin/knowledge/{article_id}")
                if dr.status_code in (200, 204):
                    cleaned["kb"] += 1
                    print(f"  DEL   KB article: {title[:40]}...")

    # Clean up seeded quick actions (by known test labels)
    test_labels = {qa["label"] for qa in QUICK_ACTIONS}
    r = client.admin_get("/api/admin/quick-actions")
    if r.status_code == 200:
        data = r.json()
        actions = data if isinstance(data, list) else (data.get("actions") or data.get("items") or [])
        for action in actions:
            label = action.get("label", "")
            action_id = action.get("id", "")
            if label in test_labels and action_id:
                dr = client.admin_delete(f"/api/admin/quick-actions/{action_id}")
                if dr.status_code in (200, 204):
                    cleaned["quick_actions"] += 1
                    print(f"  DEL   Quick action: {label}")

    print(f"  OK    Cleaned: {cleaned['team']} team, {cleaned['kb']} KB, {cleaned['quick_actions']} QA")
    return cleaned


def phase_2_team_members(client: SeedClient) -> list[dict]:
    """Create team members with diverse roles."""
    print("\n" + "=" * 60)
    print("Phase 2: Team Members")
    print("=" * 60)

    created = []
    for member in TEAM_MEMBERS:
        r = client.admin_post("/api/admin/team", member)
        if r.status_code in (200, 201):
            data = r.json()
            created.append(data)
            print(f"  OK    {member['displayName']} ({member['role']})")
        elif r.status_code == 409:
            print(f"  SKIP  {member['displayName']} — already exists")
        elif r.status_code == 429:
            print(f"  WAIT  Rate limited — pausing 60s")
            time.sleep(60)
            r = client.admin_post("/api/admin/team", member)
            if r.status_code in (200, 201):
                created.append(r.json())
                print(f"  OK    {member['displayName']} ({member['role']}) [retry]")
            else:
                print(f"  FAIL  {member['displayName']}: {r.status_code} {r.text[:100]}")
        else:
            print(f"  FAIL  {member['displayName']}: {r.status_code} {r.text[:100]}")

    print(f"  DONE  {len(created)}/{len(TEAM_MEMBERS)} team members created")
    return created


def phase_3_knowledge_base(client: SeedClient) -> list[dict]:
    """Populate the knowledge base with diverse article types."""
    print("\n" + "=" * 60)
    print("Phase 3: Knowledge Base Articles")
    print("=" * 60)

    created = []
    for article in KB_ARTICLES:
        r = client.admin_post("/api/admin/knowledge", article)
        if r.status_code in (200, 201):
            data = r.json()
            created.append(data)
            print(f"  OK    [{article['entryType']:8}] {article['title'][:45]}...")
        elif r.status_code == 429:
            print(f"  WAIT  Rate limited — pausing 60s")
            time.sleep(60)
            r = client.admin_post("/api/admin/knowledge", article)
            if r.status_code in (200, 201):
                created.append(r.json())
                print(f"  OK    [{article['entryType']:8}] {article['title'][:45]}... [retry]")
            else:
                print(f"  FAIL  {article['title'][:45]}: {r.status_code}")
        else:
            print(f"  FAIL  {article['title'][:45]}: {r.status_code} {r.text[:100]}")

    print(f"  DONE  {len(created)}/{len(KB_ARTICLES)} articles created")
    return created


def phase_4_quick_actions(client: SeedClient) -> list[dict]:
    """Create quick action buttons for the widget."""
    print("\n" + "=" * 60)
    print("Phase 4: Quick Actions")
    print("=" * 60)

    created = []
    for action in QUICK_ACTIONS:
        r = client.admin_post("/api/admin/quick-actions", action)
        if r.status_code in (200, 201):
            data = r.json()
            created.append(data)
            print(f"  OK    {action['label']}")
        elif r.status_code == 429:
            print(f"  WAIT  Rate limited — pausing 60s")
            time.sleep(60)
            r = client.admin_post("/api/admin/quick-actions", action)
            if r.status_code in (200, 201):
                created.append(r.json())
                print(f"  OK    {action['label']} [retry]")
            else:
                print(f"  FAIL  {action['label']}: {r.status_code}")
        else:
            print(f"  FAIL  {action['label']}: {r.status_code} {r.text[:100]}")

    print(f"  DONE  {len(created)}/{len(QUICK_ACTIONS)} quick actions created")
    return created


def phase_5_configuration(client: SeedClient) -> bool:
    """Save a realistic draft configuration and activate it."""
    print("\n" + "=" * 60)
    print("Phase 5: Configuration (Draft + Activate)")
    print("=" * 60)

    # Save draft config
    r = client.admin_put("/api/config", {"fields": DRAFT_CONFIG})
    if r.status_code == 200:
        print(f"  OK    Draft configuration saved ({len(DRAFT_CONFIG)} fields)")
    else:
        print(f"  FAIL  Draft save: {r.status_code} {r.text[:200]}")
        return False

    time.sleep(2)

    # Activate the draft
    r = client.admin_post("/api/config/draft/activate", {})
    if r.status_code == 200:
        result = r.json()
        version = result.get("version") or result.get("active_version", "?")
        print(f"  OK    Configuration activated (version {version})")
    elif r.status_code == 422:
        # May have validation issues — still proceed
        print(f"  WARN  Activation returned 422: {r.text[:200]}")
        print(f"        Draft saved but not activated — some fields may need review")
    else:
        print(f"  FAIL  Activation: {r.status_code} {r.text[:200]}")
        return False

    return True


def phase_6_conversations(client: SeedClient) -> list[str]:
    """Create realistic conversations via the widget API."""
    print("\n" + "=" * 60)
    print("Phase 6: Conversations (via Widget API)")
    print("=" * 60)

    if not client.widget_key:
        print("  SKIP  No widget key available — skipping conversations")
        return []

    created_ids = []
    for scenario in CONVERSATION_SCENARIOS:
        r = client.widget_post("/api/chat/conversations", {
            "initialMessage": scenario["initial_message"],
            "pageUrl": scenario.get("page_url"),
            "metadata": {
                "browser": "Chrome 122",
                "device": "Desktop",
                "locale": "en-US",
                "screen": "1920x1080",
            },
        })
        if r.status_code in (200, 201):
            data = r.json()
            conv_id = data.get("conversationId") or data.get("conversation_id", "")
            created_ids.append(conv_id)
            msg_preview = scenario["initial_message"][:50]
            print(f"  OK    Conversation {conv_id[:12]}... \"{msg_preview}...\"")

            # Wait for AI response (the pipeline processes asynchronously)
            time.sleep(3)

        elif r.status_code == 429:
            print(f"  WAIT  Rate limited — pausing 60s")
            time.sleep(60)
            r = client.widget_post("/api/chat/conversations", {
                "initialMessage": scenario["initial_message"],
                "pageUrl": scenario.get("page_url"),
            })
            if r.status_code in (200, 201):
                data = r.json()
                conv_id = data.get("conversationId") or data.get("conversation_id", "")
                created_ids.append(conv_id)
                print(f"  OK    Conversation {conv_id[:12]}... [retry]")
                time.sleep(3)
            else:
                print(f"  FAIL  Conversation: {r.status_code}")
        elif r.status_code == 401:
            print(f"  FAIL  Widget key invalid (401) — cannot create conversations")
            break
        else:
            print(f"  FAIL  Conversation: {r.status_code} {r.text[:100]}")

    print(f"  DONE  {len(created_ids)}/{len(CONVERSATION_SCENARIOS)} conversations created")
    return created_ids


def phase_7_verify(client: SeedClient) -> dict:
    """Verify all seeded data is accessible via the admin API."""
    print("\n" + "=" * 60)
    print("Phase 7: Verification")
    print("=" * 60)

    results = {}

    # Team members
    r = client.admin_get("/api/admin/team?limit=100")
    if r.status_code == 200:
        data = r.json()
        count = data.get("totalCount") or data.get("total_count") or len(data.get("members") or data.get("items") or [])
        results["team"] = count
        print(f"  OK    Team members: {count}")
    else:
        results["team"] = f"ERROR {r.status_code}"
        print(f"  FAIL  Team: {r.status_code}")

    # Knowledge base
    r = client.admin_get("/api/admin/knowledge?limit=100")
    if r.status_code == 200:
        data = r.json()
        count = data.get("totalCount") or data.get("total_count") or len(data.get("articles") or data.get("items") or [])
        results["kb"] = count
        print(f"  OK    KB articles: {count}")
    else:
        results["kb"] = f"ERROR {r.status_code}"
        print(f"  FAIL  KB: {r.status_code}")

    # Quick actions
    r = client.admin_get("/api/admin/quick-actions")
    if r.status_code == 200:
        data = r.json()
        if isinstance(data, list):
            count = len(data)
        else:
            count = data.get("totalCount") or data.get("total_count") or len(data.get("actions") or data.get("items") or [])
        results["quick_actions"] = count
        print(f"  OK    Quick actions: {count}")
    else:
        results["quick_actions"] = f"ERROR {r.status_code}"
        print(f"  FAIL  Quick actions: {r.status_code}")

    # Config activation status
    r = client.admin_get("/api/config/activation-status")
    if r.status_code == 200:
        data = r.json()
        results["config_active"] = data.get("isActive") or data.get("is_active")
        results["config_version"] = data.get("activeVersion") or data.get("active_version")
        print(f"  OK    Config active: {results['config_active']}, version: {results['config_version']}")
    else:
        results["config_active"] = f"ERROR {r.status_code}"
        print(f"  FAIL  Config: {r.status_code}")

    # Conversations
    r = client.admin_get("/api/admin/conversations?limit=100")
    if r.status_code == 200:
        data = r.json()
        count = data.get("totalCount") or data.get("total_count") or len(data.get("conversations") or data.get("items") or [])
        results["conversations"] = count
        print(f"  OK    Conversations: {count}")
    else:
        results["conversations"] = f"ERROR {r.status_code}"
        print(f"  FAIL  Conversations: {r.status_code}")

    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Seed a staging tenant with realistic mid-flight data",
    )
    parser.add_argument(
        "--env",
        choices=["staging", "production"],
        default="staging",
        help="Target environment (default: staging)",
    )
    parser.add_argument(
        "--tenant",
        default=None,
        help="Override tenant ID",
    )
    parser.add_argument(
        "--skip-conversations",
        action="store_true",
        help="Skip conversation seeding (faster, avoids AI pipeline waits)",
    )
    parser.add_argument(
        "--skip-cleanup",
        action="store_true",
        help="Skip cleanup phase (useful when re-running to add more data)",
    )
    parser.add_argument(
        "--self-provision",
        action="store_true",
        help="Self-provision an ephemeral test tenant via SPA key (WI-1107)",
    )
    args = parser.parse_args()

    env_config = ENVIRONMENTS[args.env]
    tenant_id = args.tenant or env_config["tenant_id"]
    effective_api_key = env_config["api_key"]
    effective_widget_key = env_config.get("widget_key", "")

    # WI-1107: Self-provision an ephemeral tenant
    if args.self_provision:
        spa_key = (
            os.environ.get("STAGING_SPA_KEY", "")
            or os.environ.get("STAGING_SPA_API_KEY", "")
            or os.environ.get("PRODUCTION_SPA_KEY", "")
        )
        if not spa_key:
            print("\nERROR: --self-provision requires SPA key in env (STAGING_SPA_KEY)")
            sys.exit(1)
        try:
            from scripts._self_provision import provision_test_tenant
            result = provision_test_tenant(
                base_url=env_config["base_url"],
                spa_key=spa_key,
                tier="professional",
                merchant_name=f"Seed Test {datetime.now(timezone.utc).strftime('%H%M%S')}",
            )
            tenant_id = result.tenant_id
            effective_api_key = result.user_api_key
            effective_widget_key = result.widget_key
            print(f"  Self-provisioned: {tenant_id}")
            print(f"  User key: {effective_api_key[:20]}...")
        except Exception as e:
            print(f"\nERROR: Self-provisioning failed: {e}")
            sys.exit(1)

    print("=" * 60)
    print(f"  Mid-Flight Seed — {args.env.upper()}")
    print(f"  Target: {env_config['base_url']}")
    print(f"  Tenant: {tenant_id}")
    print(f"  Time:   {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    if not effective_api_key:
        print("\nERROR: No API key found. Set keys in .env.local or use --self-provision")
        sys.exit(1)

    client = SeedClient(
        base_url=env_config["base_url"],
        api_key=effective_api_key,
        widget_key=effective_widget_key,
        tenant_id=tenant_id,
    )

    try:
        # Phase 0: Health check
        if not phase_0_health_check(client):
            print("\nABORT: Health check failed")
            sys.exit(1)

        # Phase 1: Cleanup (idempotent)
        if not args.skip_cleanup:
            phase_1_cleanup(client)

        # Phase 2: Team members
        team = phase_2_team_members(client)

        # Phase 3: Knowledge base
        kb = phase_3_knowledge_base(client)

        # Phase 4: Quick actions
        qa = phase_4_quick_actions(client)

        # Phase 5: Configuration
        phase_5_configuration(client)

        # Phase 6: Conversations (optional)
        convos = []
        if not args.skip_conversations:
            convos = phase_6_conversations(client)
        else:
            print("\n  SKIP  Conversations (--skip-conversations)")

        # Phase 7: Verification
        results = phase_7_verify(client)

        # Summary
        print("\n" + "=" * 60)
        print("  SEED COMPLETE")
        print("=" * 60)
        print(f"  Team members:   {len(team)} created")
        print(f"  KB articles:    {len(kb)} created")
        print(f"  Quick actions:  {len(qa)} created")
        print(f"  Conversations:  {len(convos)} created")
        print(f"  Config:         Draft saved + activated")
        print("=" * 60)

    finally:
        client.close()


def run_seed(
    env: str = "staging",
    tenant: str | None = None,
    api_key: str | None = None,
    widget_key: str | None = None,
    skip_conversations: bool = False,
    skip_cleanup: bool = False,
    self_provision: bool = False,
    spa_key: str | None = None,
) -> bool:
    """Programmatic entry point for test pipeline integration.

    Args:
        api_key: Override env config API key (for seeding non-primary tenants).
        widget_key: Override env config widget key.
        self_provision: If True, create an ephemeral tenant via SPA key (WI-1107).
        spa_key: SPA platform admin key for self-provisioning.

    Returns True if seeding succeeded, False otherwise.
    """
    env_config = ENVIRONMENTS.get(env)
    if not env_config:
        print(f"ERROR: Unknown environment '{env}'")
        return False

    tenant_id = tenant or env_config["tenant_id"]
    effective_api_key = api_key or env_config["api_key"]
    effective_widget_key = widget_key or env_config.get("widget_key", "")

    # WI-1107: Self-provision if requested
    if self_provision:
        _spa = spa_key or os.environ.get("STAGING_SPA_KEY", "") or os.environ.get("STAGING_SPA_API_KEY", "")
        if not _spa:
            print("ERROR: self_provision=True requires spa_key or STAGING_SPA_KEY env var")
            return False
        try:
            from scripts._self_provision import provision_test_tenant
            result = provision_test_tenant(
                base_url=env_config["base_url"],
                spa_key=_spa,
                tier="professional",
            )
            tenant_id = result.tenant_id
            effective_api_key = result.user_api_key
            effective_widget_key = result.widget_key
            print(f"  Self-provisioned: {tenant_id}")
        except Exception as e:
            print(f"ERROR: Self-provisioning failed: {e}")
            return False

    if not effective_api_key:
        print(f"ERROR: No API key found for tenant {tenant_id}")
        return False

    client = SeedClient(
        base_url=env_config["base_url"],
        api_key=effective_api_key,
        widget_key=effective_widget_key,
        tenant_id=tenant_id,
    )

    try:
        if not phase_0_health_check(client):
            return False

        if not skip_cleanup:
            phase_1_cleanup(client)

        team = phase_2_team_members(client)
        kb = phase_3_knowledge_base(client)
        qa = phase_4_quick_actions(client)
        phase_5_configuration(client)

        convos = []
        if not skip_conversations:
            convos = phase_6_conversations(client)

        phase_7_verify(client)

        print(f"\n  SEED COMPLETE: {len(team)} team, {len(kb)} KB, "
              f"{len(qa)} QA, {len(convos)} conversations")
        return True

    except Exception as e:
        print(f"ERROR: Seed failed: {e}")
        return False
    finally:
        client.close()


if __name__ == "__main__":
    main()
