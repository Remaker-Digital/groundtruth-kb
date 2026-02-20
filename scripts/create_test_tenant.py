"""Create Simulated Customer Tenant (test-customer-001).

Type: Repeatable Procedure (see docs/operations/REPEATABLE-PROCEDURES.md)
Last verified: 2026-02-19
Last corrected: 2026-02-19 — Initial creation (S52)

Creates a fully populated test tenant for UI testing with realistic data:
  - 9 team members (3 from seed + 6 additional)
  - 12 quick actions with 6 page assignments
  - 3 manual KB documents + 1 KA template (apparel_fashion, ~15 articles)
  - 19 conversations via live AI pipeline
  - Avatar uploaded
  - Tier override verified
  - Knowledge Automation template applied (KA-3)

VARIABLES:
  TENANT_ID          = test-customer-001
  BILLING_CHANNEL    = stripe
  TIER               = starter
  CUSTOMER_EMAIL     = test-customer@remakerdigital.com
  PROD_URL           = https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io
  SUPERADMIN_API_KEY = (from .env.local — remaker-digital-001 superadmin — for tier override only)

Usage:
  # Dry run — preview what will be created
  python scripts/create_test_tenant.py

  # Execute — create the tenant and populate data
  python scripts/create_test_tenant.py --execute

  # Resume from a specific phase (if a phase failed)
  python scripts/create_test_tenant.py --execute --from-phase 3

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

# Force UTF-8 output on Windows to avoid charmap encoding errors
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

TENANT_ID = "test-customer-001"
BILLING_CHANNEL = "stripe"
TIER = "starter"
CUSTOMER_EMAIL = "test-customer@remakerdigital.com"
PROD_URL = os.environ.get(
    "PROD_URL",
    "https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io",
)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Credentials populated during execution
CREDENTIALS: dict[str, str] = {}

# ---------------------------------------------------------------------------
# HTTP helper
# ---------------------------------------------------------------------------

import urllib.request
import urllib.error


def api_call(
    method: str,
    path: str,
    *,
    body: dict | None = None,
    api_key: str | None = None,
    widget_key: str | None = None,
    base_url: str | None = None,
    timeout: int = 30,
) -> tuple[int, dict | str]:
    """Make an HTTP API call and return (status_code, response_body)."""
    url = f"{base_url or PROD_URL}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if api_key:
        req.add_header("X-API-Key", api_key)
    if widget_key:
        req.add_header("X-Widget-Key", widget_key)
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        content = resp.read().decode()
        try:
            return resp.status, json.loads(content)
        except json.JSONDecodeError:
            return resp.status, content
    except urllib.error.HTTPError as e:
        content = e.read().decode()
        try:
            return e.code, json.loads(content)
        except json.JSONDecodeError:
            return e.code, content


def upload_file(
    path: str,
    file_path: str,
    *,
    api_key: str,
    field_name: str = "file",
    timeout: int = 60,
) -> tuple[int, dict | str]:
    """Upload a file via multipart form POST."""
    import mimetypes

    boundary = "----AgentRedBoundary" + str(int(time.time()))
    file_name = os.path.basename(file_path)
    mime_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"

    with open(file_path, "rb") as f:
        file_data = f.read()

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="{field_name}"; filename="{file_name}"\r\n'
        f"Content-Type: {mime_type}\r\n\r\n"
    ).encode() + file_data + f"\r\n--{boundary}--\r\n".encode()

    url = f"{PROD_URL}{path}"
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    req.add_header("X-API-Key", api_key)

    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        content = resp.read().decode()
        return resp.status, json.loads(content)
    except urllib.error.HTTPError as e:
        content = e.read().decode()
        try:
            return e.code, json.loads(content)
        except json.JSONDecodeError:
            return e.code, content


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

class _Colors:
    PASS = "\033[92m"
    FAIL = "\033[91m"
    WARN = "\033[93m"
    INFO = "\033[96m"
    PHASE = "\033[95m"
    RESET = "\033[0m"


def log(level: str, msg: str) -> None:
    color = getattr(_Colors, level, _Colors.INFO)
    print(f"{color}[{level}]{_Colors.RESET} {msg}")


def phase_header(num: int, name: str) -> None:
    log("PHASE", f"\n{'='*60}")
    log("PHASE", f"  PHASE {num}: {name}")
    log("PHASE", f"{'='*60}")


# ---------------------------------------------------------------------------
# Phase 0: Seed Tenant
# ---------------------------------------------------------------------------

def phase_0_seed(dry_run: bool) -> None:
    phase_header(0, "Seed Tenant via seed_tenant.py")

    env = {
        "SEED_TENANT_ID": TENANT_ID,
        "SEED_BILLING_CHANNEL": BILLING_CHANNEL,
        "SEED_TIER": TIER,
        "SEED_CUSTOMER_EMAIL": CUSTOMER_EMAIL,
        "SEED_SHOP_DOMAIN": "",  # No Shopify domain for standalone tenant
    }

    log("INFO", f"Tenant ID: {TENANT_ID}")
    log("INFO", f"Tier: {TIER}, Channel: {BILLING_CHANNEL}")

    if dry_run:
        log("INFO", "[DRY RUN] Would run: seed_tenant.py --execute with ENV overrides")
        log("INFO", f"  ENV: {json.dumps(env, indent=2)}")
        return

    # Run seed script
    seed_script = PROJECT_ROOT / "scripts" / "seed_tenant.py"
    cmd_env = {**os.environ, **env}

    log("INFO", "Running seed_tenant.py --execute ...")
    result = subprocess.run(
        [sys.executable, str(seed_script), "--execute"],
        env=cmd_env,
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )

    if result.returncode != 0:
        log("FAIL", f"Seed script failed (exit {result.returncode})")
        log("FAIL", result.stderr[-1000:] if result.stderr else "No stderr")
        raise RuntimeError("Seed script failed")

    # Parse credentials from output
    output = result.stdout
    log("INFO", "Seed output (last 60 lines):")
    for line in output.strip().split("\n")[-60:]:
        print(f"  {line}")

    # Extract keys from seed output.
    # Seed prints:
    #   Tenant API Key:    arsk_...
    #   Widget Key:        pk_live_...
    #   User API Keys:
    #     Owner <mike@...>          (display_name + email)
    #       ar_user_...             (the key on the NEXT line)
    lines = output.split("\n")
    collecting_user_keys = False
    last_member_line = ""

    for line in lines:
        stripped = line.strip()

        # Tenant-level keys
        if "Tenant API Key:" in line:
            key = stripped.split(":")[-1].strip()
            if key.startswith("arsk_"):
                CREDENTIALS["tenant_api_key"] = key
        elif "Widget Key:" in line and "user" not in line.lower():
            key = stripped.split(":")[-1].strip()
            if key.startswith("pk_"):
                CREDENTIALS["widget_key"] = key
        elif "User API Keys:" in line:
            collecting_user_keys = True
            continue

        # User API keys section: alternating name/key lines
        if collecting_user_keys:
            if stripped.startswith("ar_user_"):
                # This is a user API key — associate with last member
                if "superadmin" in last_member_line.lower() or "owner" in last_member_line.lower():
                    CREDENTIALS["superadmin_key"] = stripped
                else:
                    CREDENTIALS[f"seed_key_{last_member_line.strip()[:30]}"] = stripped
            elif "<" in stripped and ">" in stripped:
                # This is a "Name <email>" line
                last_member_line = stripped
            elif stripped.startswith("---") or stripped.startswith("===") or stripped.startswith("URLS"):
                collecting_user_keys = False

    log("PASS", f"Seed complete. Credentials found: {list(CREDENTIALS.keys())}")

    # Verify tenant exists
    status, body = api_call(
        "GET", "/api/tenants/lookup",
        api_key=CREDENTIALS.get("superadmin_key", ""),
    )
    if status == 200:
        log("PASS", f"Tenant lookup OK: tier={body.get('tier')}, status={body.get('status')}")
    else:
        log("WARN", f"Tenant lookup returned {status} — may need activation first")


# ---------------------------------------------------------------------------
# Phase 1: Configure & Activate
# ---------------------------------------------------------------------------

def phase_1_configure(dry_run: bool) -> None:
    phase_header(1, "Configure & Activate")

    # PUT /api/config expects {"fields": {field_name: value}} wrapper
    config_body = {
        "fields": {
            "brand_name": "Test Customer Store",
            "brand_voice": "Helpful and professional customer service assistant for an online retail store.",
            "custom_instructions": "You help customers with orders, returns, and product questions. Be concise and friendly.",
            "agent_name": "TestBot",
            "greeting_message": "Hi there! How can I help you today?",
            "widget_primary_color": "#2563eb",
            "widget_position": "bottom-right",
            "customer_identification_mode": "standard",
        },
    }

    if dry_run:
        log("INFO", f"[DRY RUN] Would PUT /api/admin/config with {len(config_body)} fields")
        log("INFO", f"[DRY RUN] Would POST /api/admin/config/activate")
        return

    key = CREDENTIALS.get("superadmin_key", "")

    # Save config (PUT /api/config — not /api/admin/config)
    status, body = api_call("PUT", "/api/config", body=config_body, api_key=key)
    if status in (200, 201):
        log("PASS", f"Config saved: {status}")
    else:
        log("FAIL", f"Config save failed: {status} — {body}")
        raise RuntimeError(f"Config save failed: {status}")

    # Activate (POST /api/config/draft/activate — activates the saved draft)
    status, body = api_call("POST", "/api/config/draft/activate", body={}, api_key=key)
    if status in (200, 201):
        log("PASS", f"Config activated: is_active={body.get('isActive', body.get('is_active'))}")
    else:
        log("FAIL", f"Activation failed: {status} — {body}")
        raise RuntimeError(f"Activation failed: {status}")


# ---------------------------------------------------------------------------
# Phase 2: Create Additional Team Members
# ---------------------------------------------------------------------------

ADDITIONAL_TEAM_MEMBERS = [
    {
        "email": "admin@testcustomer.com",
        "displayName": "Admin User",
        "role": "admin",
    },
    {
        "email": "service-agent@testcustomer.com",
        "displayName": "Sarah Service",
        "role": "escalation_agent",
        "escalationCategories": ["service"],
        "maxConcurrentConversations": 5,
    },
    {
        "email": "support-agent@testcustomer.com",
        "displayName": "Sam Support",
        "role": "escalation_agent",
        "escalationCategories": ["support", "general_inquiry"],
        "maxConcurrentConversations": 5,
    },
    {
        "email": "sales-agent@testcustomer.com",
        "displayName": "Steve Sales",
        "role": "escalation_agent",
        "escalationCategories": ["sales"],
        "maxConcurrentConversations": 3,
    },
    {
        "email": "account-agent@testcustomer.com",
        "displayName": "Amy Account",
        "role": "escalation_agent",
        "escalationCategories": ["account"],
        "maxConcurrentConversations": 3,
    },
    {
        "email": "tech-agent@testcustomer.com",
        "displayName": "Tom Technical",
        "role": "escalation_agent",
        "escalationCategories": ["technical_assistance"],
        "maxConcurrentConversations": 3,
    },
    {
        "email": "viewer@testcustomer.com",
        "displayName": "Viewer User",
        "role": "viewer",
    },
]


def phase_2_team(dry_run: bool) -> None:
    phase_header(2, f"Create {len(ADDITIONAL_TEAM_MEMBERS)} Additional Team Members")

    if dry_run:
        for m in ADDITIONAL_TEAM_MEMBERS:
            log("INFO", f"[DRY RUN] Would create: {m['displayName']} ({m['role']})")
        return

    key = CREDENTIALS.get("superadmin_key", "")
    created = 0
    member_keys: dict[str, str] = {}

    for member in ADDITIONAL_TEAM_MEMBERS:
        status, body = api_call("POST", "/api/admin/team", body=member, api_key=key)
        if status == 201:
            member_key = body.get("userApiKey", "")
            member_keys[member["email"]] = member_key
            log("PASS", f"Created: {member['displayName']} ({member['role']}) — key prefix: {member_key[:20]}...")
            created += 1
        elif status == 409:
            log("WARN", f"Already exists: {member['email']} — skipping")
            created += 1
        else:
            log("FAIL", f"Failed to create {member['email']}: {status} — {body}")

    CREDENTIALS["member_keys"] = json.dumps(member_keys)
    log("PASS" if created == len(ADDITIONAL_TEAM_MEMBERS) else "WARN",
        f"Team members created: {created}/{len(ADDITIONAL_TEAM_MEMBERS)}")


# ---------------------------------------------------------------------------
# Phase 3: Create Quick Actions & Assignments
# ---------------------------------------------------------------------------

QUICK_ACTIONS = [
    # home page
    {"label": "What's new today?", "promptTemplate": "What new products or promotions do you have today?", "icon": "🆕", "sortOrder": 0, "page": "home"},
    {"label": "Help me find something", "promptTemplate": "I'm looking for something specific but I'm not sure where to find it.", "icon": "🔍", "sortOrder": 1, "page": "home"},
    # product page
    {"label": "Is this in stock?", "promptTemplate": "Is this product currently in stock and available for shipping?", "icon": "📦", "sortOrder": 0, "page": "product"},
    {"label": "Size guide", "promptTemplate": "Can you help me find the right size for this product?", "icon": "📏", "sortOrder": 1, "page": "product"},
    # collection page
    {"label": "Compare products", "promptTemplate": "Can you help me compare the products in this collection?", "icon": "⚖️", "sortOrder": 0, "page": "collection"},
    {"label": "Best sellers", "promptTemplate": "Which products in this collection are the most popular?", "icon": "⭐", "sortOrder": 1, "page": "collection"},
    # cart page
    {"label": "Apply discount", "promptTemplate": "Do you have any discount codes or promotions I can use on my order?", "icon": "🏷️", "sortOrder": 0, "page": "cart"},
    {"label": "Shipping options", "promptTemplate": "What shipping options are available for my order?", "icon": "🚚", "sortOrder": 1, "page": "cart"},
    # search page
    {"label": "Refine my search", "promptTemplate": "I searched but couldn't find exactly what I need. Can you help me refine my search?", "icon": "🎯", "sortOrder": 0, "page": "search"},
    {"label": "Popular searches", "promptTemplate": "What are other customers commonly searching for?", "icon": "📊", "sortOrder": 1, "page": "search"},
    # blog page
    {"label": "Related products", "promptTemplate": "Are there any products related to this blog post?", "icon": "🛍️", "sortOrder": 0, "page": "blog"},
    {"label": "More articles", "promptTemplate": "Can you recommend more articles on this topic?", "icon": "📚", "sortOrder": 1, "page": "blog"},
]


def phase_3_quick_actions(dry_run: bool) -> None:
    phase_header(3, f"Create {len(QUICK_ACTIONS)} Quick Actions + 6 Page Assignments")

    if dry_run:
        pages = set(qa["page"] for qa in QUICK_ACTIONS)
        log("INFO", f"[DRY RUN] Would create {len(QUICK_ACTIONS)} quick actions across {len(pages)} pages")
        return

    key = CREDENTIALS.get("superadmin_key", "")
    created_ids: dict[str, list[str]] = {}  # page -> [id1, id2]

    for qa in QUICK_ACTIONS:
        page = qa.pop("page")
        status, body = api_call("POST", "/api/admin/quick-actions", body=qa, api_key=key)
        qa["page"] = page  # restore

        if status == 201:
            qa_id = body.get("id", "")
            created_ids.setdefault(page, []).append(qa_id)
            log("PASS", f"Created QA: {qa['label']} -- {page} (id={qa_id[:12]}...)")
        else:
            log("FAIL", f"Failed QA '{qa['label']}': {status} — {body}")

    # Create page assignments
    assigned = 0
    for page_type, ids in created_ids.items():
        if len(ids) >= 2:
            assignment = {
                "pageType": page_type,
                "slot1ActionId": ids[0],
                "slot2ActionId": ids[1],
                "autoOpen": False,
                "autoOpenDelayMs": 3000,
            }
            status, body = api_call(
                "PUT", "/api/admin/quick-actions/assignments",
                body=assignment, api_key=key,
            )
            if status == 200:
                log("PASS", f"Assigned: {page_type} -- [{ids[0][:8]}, {ids[1][:8]}]")
                assigned += 1
            else:
                log("FAIL", f"Assignment {page_type} failed: {status} — {body}")

    log("PASS" if assigned == 6 else "WARN",
        f"Quick actions: {sum(len(v) for v in created_ids.values())} created, {assigned}/6 pages assigned")


# ---------------------------------------------------------------------------
# Phase 4: Upload KB Documents + Create Manual Entries
# ---------------------------------------------------------------------------

MANUAL_KB_ENTRIES = [
    {
        "entryType": "policy",
        "title": "Return and Refund Policy",
        "content": "We accept returns within 30 days of purchase. Items must be in original condition with tags attached. Refunds are processed within 5-7 business days. For defective items, we cover return shipping costs. Contact our support team to initiate a return.",
        "category": "Policies",
        "status": "published",
        "tags": ["returns", "refunds", "policy"],
    },
    {
        "entryType": "faq",
        "title": "Frequently Asked Questions",
        "content": "Q: How long does shipping take? A: Standard shipping takes 3-5 business days. Express shipping takes 1-2 business days.\n\nQ: Do you ship internationally? A: Yes, we ship to over 50 countries. International shipping takes 7-14 business days.\n\nQ: What payment methods do you accept? A: We accept all major credit cards, PayPal, and Apple Pay.\n\nQ: Where can I find product XYZ789? A: Product XYZ789 is available in our Premium Collection.",
        "category": "General",
        "status": "published",
        "tags": ["faq", "shipping", "payment", "XYZ789"],
    },
    {
        "entryType": "article",
        "title": "Seasonal Promotions Guide",
        "content": "Current promotions: Summer Sale — 20% off all outdoor furniture. Back to School — 15% off electronics. Free shipping on orders over $75. Bundle deals available on select categories.",
        "category": "Promotions",
        "status": "published",
        "tags": ["promotions", "sales", "seasonal"],
    },
]

# File paths for upload (relative to project root)
KB_UPLOAD_FILES = [
    # We'll create small test files if they don't exist
]


def phase_4_knowledge(dry_run: bool) -> None:
    phase_header(4, f"Create {len(MANUAL_KB_ENTRIES)} Manual KB Entries")

    if dry_run:
        for entry in MANUAL_KB_ENTRIES:
            log("INFO", f"[DRY RUN] Would create: {entry['title']} ({entry['entryType']})")
        return

    key = CREDENTIALS.get("superadmin_key", "")
    created = 0

    for entry in MANUAL_KB_ENTRIES:
        status, body = api_call("POST", "/api/admin/knowledge", body=entry, api_key=key)
        if status == 201:
            entry_id = body.get("id", "")
            log("PASS", f"Created KB: {entry['title']} (id={entry_id[:12]}...)")
            created += 1
        else:
            log("FAIL", f"Failed KB '{entry['title']}': {status} — {body}")

    log("PASS" if created == len(MANUAL_KB_ENTRIES) else "WARN",
        f"KB entries created: {created}/{len(MANUAL_KB_ENTRIES)}")


# ---------------------------------------------------------------------------
# Phase 4B: Apply Knowledge Automation Template (KA-3)
# ---------------------------------------------------------------------------

TEMPLATE_TO_APPLY = "apparel_fashion"


def phase_4b_ka_template(dry_run: bool) -> None:
    phase_header(4, "Apply Knowledge Automation Template (KA-3)")

    if dry_run:
        log("INFO", f"[DRY RUN] Would POST /api/admin/knowledge/templates/{TEMPLATE_TO_APPLY}/apply")
        return

    key = CREDENTIALS.get("superadmin_key", "")

    # Apply template
    status, body = api_call(
        "POST", f"/api/admin/knowledge/templates/{TEMPLATE_TO_APPLY}/apply",
        body={}, api_key=key,
    )

    if status in (200, 201):
        articles_created = body.get("articlesCreated", body.get("articles_created", "?"))
        log("PASS", f"Template '{TEMPLATE_TO_APPLY}' applied: {articles_created} articles created")
    else:
        log("WARN", f"Template apply failed: {status} — {body}")
        log("INFO", "Template apply is non-critical — continuing")
        return

    # Verify suggestions endpoint works after KB population
    status, body = api_call("GET", "/api/admin/knowledge/suggestions", api_key=key)
    if status == 200:
        suggestion_count = len(body) if isinstance(body, dict) else 0
        log("PASS", f"Config suggestions available: {suggestion_count} suggestions")
    else:
        log("WARN", f"Suggestions endpoint: {status} — non-critical")


# ---------------------------------------------------------------------------
# Phase 5: Create Conversations Through Live AI Pipeline
# ---------------------------------------------------------------------------

CONVERSATIONS = [
    # Quick-action-triggered (6)
    {"name": "QA-home", "message": "What new products or promotions do you have today?", "page_url": "https://testcustomer.com/"},
    {"name": "QA-product", "message": "Is this product currently in stock and available for shipping?", "page_url": "https://testcustomer.com/products/widget-pro"},
    {"name": "QA-collection", "message": "Can you help me compare the products in this collection?", "page_url": "https://testcustomer.com/collections/summer"},
    {"name": "QA-cart", "message": "Do you have any discount codes or promotions I can use on my order?", "page_url": "https://testcustomer.com/cart"},
    {"name": "QA-search", "message": "I searched but couldn't find exactly what I need. Can you help me refine my search?", "page_url": "https://testcustomer.com/search?q=blue+widget"},
    {"name": "QA-blog", "message": "Are there any products related to this blog post?", "page_url": "https://testcustomer.com/blogs/news/summer-trends"},
    # Escalation-triggering (6)
    {"name": "ESC-service", "message": "I received a broken item and I want to speak to a human about getting it replaced", "expect_escalation": True},
    {"name": "ESC-support", "message": "This is completely unacceptable, I demand to speak with a supervisor immediately", "expect_escalation": True},
    {"name": "ESC-sales", "message": "I'm interested in a bulk order of 500 units, I need to discuss pricing with sales", "expect_escalation": True},
    {"name": "ESC-account", "message": "I need to update my account billing information and there's a discrepancy in my charges", "expect_escalation": True},
    {"name": "ESC-tech", "message": "I'm getting error 502 when trying to use the integration API and need technical help", "expect_escalation": True},
    {"name": "ESC-general", "message": "I'd rather just chat with a real person please", "expect_escalation": True},
    # General multi-turn (2)
    {"name": "GENERAL-1", "message": "What's your return policy?"},
    {"name": "GENERAL-2", "message": "Can you tell me about your shipping options?"},
    # Will be manually escalated (2)
    {"name": "MANUAL-ESC-1", "message": "I have a question about my recent order", "manual_escalate": True, "escalation_category": "service"},
    {"name": "MANUAL-ESC-2", "message": "I need help with a product I purchased", "manual_escalate": True, "escalation_category": "support"},
    # Unassigned escalated (2)
    {"name": "UNASSIGNED-1", "message": "I want a human agent, not a bot", "manual_escalate": True},
    {"name": "UNASSIGNED-2", "message": "Transfer me to a real person right now", "manual_escalate": True},
    # Archive candidate (1)
    {"name": "ARCHIVE-1", "message": "Thank you, that answers my question!", "end_after": True},
]


def phase_5_conversations(dry_run: bool) -> None:
    phase_header(5, f"Create {len(CONVERSATIONS)} Conversations via Live AI Pipeline")

    if dry_run:
        for conv in CONVERSATIONS:
            flags = []
            if conv.get("expect_escalation"):
                flags.append("auto-escalation")
            if conv.get("manual_escalate"):
                flags.append("manual-escalate")
            if conv.get("end_after"):
                flags.append("end-after")
            log("INFO", f"[DRY RUN] {conv['name']}: \"{conv['message'][:50]}...\" [{', '.join(flags) or 'general'}]")
        return

    widget_key = CREDENTIALS.get("widget_key", "")
    admin_key = CREDENTIALS.get("superadmin_key", "")
    created = 0
    conversation_ids: dict[str, str] = {}

    for i, conv in enumerate(CONVERSATIONS):
        # Create conversation
        start_body: dict[str, Any] = {
            "initial_message": conv["message"],
        }
        if conv.get("page_url"):
            start_body["page_url"] = conv["page_url"]

        status, body = api_call(
            "POST", "/api/chat/conversations",
            body=start_body,
            widget_key=widget_key,
            timeout=60,
        )

        if status == 201:
            conv_id = body.get("conversationId", body.get("conversation_id", ""))
            conversation_ids[conv["name"]] = conv_id
            log("PASS", f"[{i+1}/{len(CONVERSATIONS)}] {conv['name']}: created (id={conv_id[:12]}...)")
            created += 1

            # Wait for AI response to complete
            time.sleep(3)

            # Add follow-up message for multi-turn conversations
            if conv["name"].startswith("GENERAL"):
                follow_up = "Can you give me more details about that?"
                api_call(
                    "POST", "/api/chat/message",
                    body={"conversation_id": conv_id, "content": follow_up},
                    widget_key=widget_key,
                    timeout=60,
                )
                time.sleep(3)

            # Manual escalation
            if conv.get("manual_escalate"):
                esc_body: dict[str, Any] = {}
                if conv.get("escalation_category"):
                    esc_body["category"] = conv["escalation_category"]
                esc_status, esc_resp = api_call(
                    "POST", f"/api/admin/conversations/{conv_id}/escalate",
                    body=esc_body,
                    api_key=admin_key,
                )
                if esc_status == 200:
                    log("PASS", f"  Escalated: {conv['name']} → {conv.get('escalation_category', 'unassigned')}")
                else:
                    log("WARN", f"  Escalation failed for {conv['name']}: {esc_status}")

            # End conversation (archive candidate)
            if conv.get("end_after"):
                end_status, _ = api_call(
                    "POST", f"/api/chat/conversations/{conv_id}/end",
                    body={},
                    widget_key=widget_key,
                )
                if end_status == 200:
                    log("PASS", f"  Ended: {conv['name']}")
                else:
                    log("WARN", f"  End failed for {conv['name']}: {end_status}")

        elif status == 403:
            log("FAIL", f"[{i+1}] {conv['name']}: 403 — tenant not active. Run Phase 1 first.")
            raise RuntimeError("Tenant not active — conversations blocked")
        else:
            log("FAIL", f"[{i+1}] {conv['name']}: {status} — {body}")

    CREDENTIALS["conversation_ids"] = json.dumps(conversation_ids)
    log("PASS" if created == len(CONVERSATIONS) else "WARN",
        f"Conversations created: {created}/{len(CONVERSATIONS)}")


# ---------------------------------------------------------------------------
# Phase 6: Upload Avatar
# ---------------------------------------------------------------------------

def phase_6_avatar(dry_run: bool) -> None:
    phase_header(6, "Upload Avatar")

    avatar_path = PROJECT_ROOT / "branding" / "logo" / "PNG" / "icon-master.png"

    if dry_run:
        log("INFO", f"[DRY RUN] Would upload: {avatar_path}")
        return

    if not avatar_path.exists():
        log("WARN", f"Avatar file not found: {avatar_path} — skipping")
        return

    key = CREDENTIALS.get("superadmin_key", "")
    status, body = upload_file(
        "/api/admin/avatar/upload",
        str(avatar_path),
        api_key=key,
    )

    if status == 200:
        avatar_url = body.get("avatar_url", body.get("avatarUrl", ""))[:60]
        log("PASS", f"Avatar uploaded: {avatar_url}...")
    else:
        log("WARN", f"Avatar upload failed: {status} — {body}")


# ---------------------------------------------------------------------------
# Phase 7: Verify Tier Override
# ---------------------------------------------------------------------------

def phase_7_tier_verify(dry_run: bool) -> None:
    phase_header(7, "Verify Tier Override")

    # Need remaker-digital-001 superadmin key for tier override (cross-tenant)
    rd_key = os.environ.get("SUPERADMIN_API_KEY", "ar_user_rema_qcHQpv0bhGwXpEou14WH3fnE_RZMvI_N")

    if dry_run:
        log("INFO", f"[DRY RUN] Would PUT /api/superadmin/tenants/{TENANT_ID}/tier with tier=starter")
        return

    status, body = api_call(
        "PUT", f"/api/superadmin/tenants/{TENANT_ID}/tier",
        body={"tier": "starter"},
        api_key=rd_key,
    )

    if status == 200:
        prev = body.get("previousTier", body.get("previous_tier", "?"))
        new = body.get("newTier", body.get("new_tier", "?"))
        log("PASS", f"Tier override OK: {prev} → {new}")
    else:
        log("WARN", f"Tier override failed: {status} — {body}")


# ---------------------------------------------------------------------------
# Postconditions
# ---------------------------------------------------------------------------

def verify_postconditions(dry_run: bool) -> None:
    phase_header(8, "Verify Postconditions")

    if dry_run:
        log("INFO", "[DRY RUN] Would verify 8 postconditions")
        return

    key = CREDENTIALS.get("superadmin_key", "")
    gates_passed = 0
    total_gates = 8

    # Gate 1: Tenant exists and is active
    status, body = api_call("GET", "/api/tenants/lookup", api_key=key)
    if status == 200 and body.get("isActive", body.get("is_active")):
        log("PASS", f"Gate 1: Tenant active, tier={body.get('tier')}")
        gates_passed += 1
    else:
        log("FAIL", f"Gate 1: Tenant not active — {status} {body}")

    # Gate 2: Team members
    status, body = api_call("GET", "/api/admin/team", api_key=key)
    if status == 200:
        members = body if isinstance(body, list) else body.get("members", body.get("items", []))
        count = len(members) if isinstance(members, list) else 0
        if count >= 7:  # 3 seed + 7 additional = 10, but minimum 7 additional
            log("PASS", f"Gate 2: {count} team members found")
            gates_passed += 1
        else:
            log("WARN", f"Gate 2: Only {count} team members (expected ≥7)")
    else:
        log("FAIL", f"Gate 2: Team list failed — {status}")

    # Gate 3: Quick actions
    status, body = api_call("GET", "/api/admin/quick-actions", api_key=key)
    if status == 200:
        actions = body if isinstance(body, list) else body.get("items", [])
        count = len(actions) if isinstance(actions, list) else 0
        if count >= 10:
            log("PASS", f"Gate 3: {count} quick actions found")
            gates_passed += 1
        else:
            log("WARN", f"Gate 3: Only {count} quick actions (expected ≥10)")
    else:
        log("FAIL", f"Gate 3: Quick actions list failed — {status}")

    # Gate 4: KB documents
    status, body = api_call("GET", "/api/admin/knowledge", api_key=key)
    if status == 200:
        entries = body if isinstance(body, list) else body.get("items", body.get("entries", []))
        count = len(entries) if isinstance(entries, list) else 0
        if count >= 10:
            log("PASS", f"Gate 4: {count} KB entries found (manual + template)")
            gates_passed += 1
        else:
            log("WARN", f"Gate 4: Only {count} KB entries (expected ≥10 = 3 manual + template)")
    else:
        log("FAIL", f"Gate 4: KB list failed — {status}")

    # Gate 5: Conversations
    status, body = api_call("GET", "/api/admin/conversations", api_key=key)
    if status == 200:
        convs = body if isinstance(body, list) else body.get("items", body.get("conversations", []))
        count = len(convs) if isinstance(convs, list) else 0
        if count >= 10:
            log("PASS", f"Gate 5: {count} conversations found")
            gates_passed += 1
        else:
            log("WARN", f"Gate 5: Only {count} conversations (expected ≥10)")
    else:
        log("FAIL", f"Gate 5: Conversation list failed — {status}")

    # Gate 6: Avatar
    status, body = api_call("GET", "/api/config", api_key=key)
    if status == 200:
        avatar_url = ""
        if isinstance(body, dict):
            avatar_url = body.get("agentAvatarUrl", body.get("agent_avatar_url", ""))
        if avatar_url and avatar_url.startswith("data:image"):
            log("PASS", f"Gate 6: Avatar uploaded ({len(avatar_url)} chars)")
            gates_passed += 1
        else:
            log("WARN", f"Gate 6: No avatar URL found")
    else:
        log("FAIL", f"Gate 6: Config read failed — {status}")

    # Gate 7: remaker-digital-001 unchanged
    rd_key = "ar_user_rema_qcHQpv0bhGwXpEou14WH3fnE_RZMvI_N"
    status, body = api_call("GET", "/api/tenants/lookup", api_key=rd_key)
    if status == 200:
        tier = body.get("tier", "?")
        active = body.get("isActive", body.get("is_active", False))
        if tier == "professional" and active:
            log("PASS", f"Gate 7: remaker-digital-001 unchanged (tier={tier}, active={active})")
            gates_passed += 1
        else:
            log("WARN", f"Gate 7: remaker-digital-001 changed! tier={tier}, active={active}")
    else:
        log("FAIL", f"Gate 7: remaker-digital-001 lookup failed — {status}")

    # Gate 8: KA config field persisted
    status, body = api_call("GET", "/api/config", api_key=key)
    if status == 200 and isinstance(body, dict):
        id_mode = body.get("customer_identification_mode", body.get("customerIdentificationMode", ""))
        if id_mode in ("off", "gentle", "standard", "aggressive"):
            log("PASS", f"Gate 8: customer_identification_mode={id_mode}")
            gates_passed += 1
        else:
            log("WARN", f"Gate 8: customer_identification_mode missing or invalid: '{id_mode}'")
    else:
        log("FAIL", f"Gate 8: Config read for KA field failed — {status}")

    # Summary
    log("PHASE", f"\n{'='*60}")
    if gates_passed == total_gates:
        log("PASS", f"ALL {total_gates} POSTCONDITION GATES PASSED")
    else:
        log("WARN", f"{gates_passed}/{total_gates} postcondition gates passed")

    # Print credentials summary
    log("PHASE", "\n  CREDENTIALS SUMMARY")
    log("PHASE", "  " + "-" * 40)
    for k, v in CREDENTIALS.items():
        if k in ("member_keys", "conversation_ids"):
            continue
        display = v[:30] + "..." if len(v) > 30 else v
        log("INFO", f"  {k}: {display}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

PHASES = [
    (0, "Seed Tenant", phase_0_seed),
    (1, "Configure & Activate", phase_1_configure),
    (2, "Create Team Members", phase_2_team),
    (3, "Create Quick Actions", phase_3_quick_actions),
    (4, "Create KB Documents", phase_4_knowledge),
    (5, "Apply KA Template", phase_4b_ka_template),
    (6, "Create Conversations", phase_5_conversations),
    (7, "Upload Avatar", phase_6_avatar),
    (8, "Verify Tier Override", phase_7_tier_verify),
    (9, "Verify Postconditions", verify_postconditions),
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Create simulated customer tenant for UI testing")
    parser.add_argument("--execute", action="store_true", help="Actually execute (without this, dry-run only)")
    parser.add_argument("--from-phase", type=int, default=0, help="Resume from phase N")
    parser.add_argument("--credentials", type=str, help="JSON file with credentials from previous run")
    args = parser.parse_args()

    dry_run = not args.execute

    log("PHASE", "=" * 60)
    log("PHASE", "  CREATE SIMULATED CUSTOMER TENANT")
    log("PHASE", f"  Tenant: {TENANT_ID}")
    log("PHASE", f"  Mode: {'EXECUTE' if not dry_run else 'DRY RUN'}")
    log("PHASE", f"  Production: {PROD_URL}")
    if args.from_phase > 0:
        log("PHASE", f"  Resuming from phase: {args.from_phase}")
    log("PHASE", "=" * 60)

    # Load credentials from previous run if resuming
    if args.credentials:
        with open(args.credentials) as f:
            CREDENTIALS.update(json.load(f))
        log("INFO", f"Loaded credentials from {args.credentials}: {list(CREDENTIALS.keys())}")

    for phase_num, phase_name, phase_fn in PHASES:
        if phase_num < args.from_phase:
            log("INFO", f"Skipping phase {phase_num}: {phase_name}")
            continue
        try:
            phase_fn(dry_run)
        except Exception as e:
            log("FAIL", f"\nPhase {phase_num} ({phase_name}) FAILED: {e}")
            log("INFO", f"To resume: python scripts/create_test_tenant.py --execute --from-phase {phase_num}")
            # Save credentials for resume
            creds_file = PROJECT_ROOT / "logs" / "test_tenant_credentials.json"
            creds_file.parent.mkdir(exist_ok=True)
            with open(creds_file, "w") as f:
                json.dump(CREDENTIALS, f, indent=2)
            log("INFO", f"Credentials saved to: {creds_file}")
            sys.exit(1)

    # Save credentials
    creds_file = PROJECT_ROOT / "logs" / "test_tenant_credentials.json"
    creds_file.parent.mkdir(exist_ok=True)
    with open(creds_file, "w") as f:
        json.dump(CREDENTIALS, f, indent=2)
    log("INFO", f"\nCredentials saved to: {creds_file}")

    if dry_run:
        log("WARN", "\nThis was a DRY RUN — no changes were made.")
        log("INFO", "Run with --execute to create the tenant.")


if __name__ == "__main__":
    main()
