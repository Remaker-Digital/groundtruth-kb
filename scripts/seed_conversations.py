"""Seed conversation documents directly into Cosmos DB for UI testing.

This script bypasses the chat pipeline and creates conversation records
directly in the 'conversations' collection. Used when the chat pipeline
is unavailable (e.g., dev_mode without Key Vault).

Usage:
  python scripts/seed_conversations.py --execute

Requirements:
  - .env.local with COSMOS_ENDPOINT and COSMOS_KEY

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts._env import load_env_local
load_env_local()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

TENANT_ID = "test-customer-001"
NOW = datetime.now(timezone.utc)

# Team member IDs from seed (will be loaded from credentials file)
CREDENTIALS_FILE = PROJECT_ROOT / "logs" / "test_tenant_credentials.json"

# Conversation definitions
CONVERSATIONS = [
    # Quick-action-triggered (6) -- status: active
    {
        "name": "QA-home",
        "status": "active",
        "messages": [
            {"role": "customer", "content": "What new products or promotions do you have today?"},
            {"role": "assistant", "content": "Welcome! We currently have several exciting promotions running. Our Summer Sale offers 20% off all outdoor furniture, and we have a Back to School promotion with 15% off electronics. Plus, free shipping on orders over $75!"},
        ],
        "page_url": "https://testcustomer.com/",
    },
    {
        "name": "QA-product",
        "status": "active",
        "messages": [
            {"role": "customer", "content": "Is this product currently in stock and available for shipping?"},
            {"role": "assistant", "content": "Let me check the availability for you. Yes, this product is currently in stock and ready to ship! Standard shipping takes 3-5 business days, or you can choose express shipping for 1-2 business day delivery."},
        ],
        "page_url": "https://testcustomer.com/products/widget-pro",
    },
    {
        "name": "QA-collection",
        "status": "active",
        "messages": [
            {"role": "customer", "content": "Can you help me compare the products in this collection?"},
            {"role": "assistant", "content": "Of course! Let me break down the key differences between the products in our Summer Collection. Each item has unique features suited for different needs. Would you like me to compare specific products, or shall I give you an overview of the top picks?"},
        ],
        "page_url": "https://testcustomer.com/collections/summer",
    },
    {
        "name": "QA-cart",
        "status": "active",
        "messages": [
            {"role": "customer", "content": "Do you have any discount codes or promotions I can use on my order?"},
            {"role": "assistant", "content": "Great question! Currently, you can use code SUMMER20 for 20% off outdoor furniture, or BACK15 for 15% off electronics. Also, your order qualifies for free shipping since it's over $75!"},
        ],
        "page_url": "https://testcustomer.com/cart",
    },
    {
        "name": "QA-search",
        "status": "active",
        "messages": [
            {"role": "customer", "content": "I searched but couldn't find exactly what I need. Can you help me refine my search?"},
            {"role": "assistant", "content": "I'd be happy to help you find what you're looking for! Could you tell me a bit more about what you need? For example, the type of product, your preferred price range, or any specific features you're looking for?"},
        ],
        "page_url": "https://testcustomer.com/search?q=blue+widget",
    },
    {
        "name": "QA-blog",
        "status": "active",
        "messages": [
            {"role": "customer", "content": "Are there any products related to this blog post?"},
            {"role": "assistant", "content": "Yes! Based on this blog post about summer trends, I can recommend several related products from our Summer Collection. These include our popular outdoor furniture sets, seasonal decor items, and patio accessories. Would you like me to show you specific items?"},
        ],
        "page_url": "https://testcustomer.com/blogs/news/summer-trends",
    },

    # Escalation-triggered (6) -- status: escalated
    {
        "name": "ESC-service",
        "status": "escalated",
        "escalation_category": "service",
        "messages": [
            {"role": "customer", "content": "I received a broken item and I want to speak to a human about getting it replaced"},
            {"role": "assistant", "content": "I'm very sorry to hear about the damaged item. I'm connecting you with a service representative who can help with a replacement right away."},
            {"role": "system", "content": "Conversation escalated to human agent (category: service)"},
        ],
    },
    {
        "name": "ESC-support",
        "status": "escalated",
        "escalation_category": "support",
        "messages": [
            {"role": "customer", "content": "This is completely unacceptable, I demand to speak with a supervisor immediately"},
            {"role": "assistant", "content": "I understand your frustration and I sincerely apologize. Let me connect you with a support supervisor right away."},
            {"role": "system", "content": "Conversation escalated to human agent (category: support)"},
        ],
    },
    {
        "name": "ESC-sales",
        "status": "escalated",
        "escalation_category": "sales",
        "messages": [
            {"role": "customer", "content": "I'm interested in a bulk order of 500 units, I need to discuss pricing with sales"},
            {"role": "assistant", "content": "A bulk order of 500 units is great! For orders of this size, I'll connect you with our sales team who can provide custom pricing and delivery options."},
            {"role": "system", "content": "Conversation escalated to human agent (category: sales)"},
        ],
    },
    {
        "name": "ESC-account",
        "status": "escalated",
        "escalation_category": "account",
        "messages": [
            {"role": "customer", "content": "I need to update my account billing information and there's a discrepancy in my charges"},
            {"role": "assistant", "content": "I understand you need help with billing. For security, I'll connect you with our account team to handle the billing update and review the discrepancy."},
            {"role": "system", "content": "Conversation escalated to human agent (category: account)"},
        ],
    },
    {
        "name": "ESC-tech",
        "status": "escalated",
        "escalation_category": "technical_assistance",
        "messages": [
            {"role": "customer", "content": "I'm getting error 502 when trying to use the integration API and need technical help"},
            {"role": "assistant", "content": "I see you're experiencing a 502 error with our API. Let me connect you with our technical support team who can investigate this issue."},
            {"role": "system", "content": "Conversation escalated to human agent (category: technical_assistance)"},
        ],
    },
    {
        "name": "ESC-general",
        "status": "escalated",
        "escalation_category": "general_inquiry",
        "messages": [
            {"role": "customer", "content": "I'd rather just chat with a real person please"},
            {"role": "assistant", "content": "Of course! I'll connect you with a team member right away."},
            {"role": "system", "content": "Conversation escalated to human agent (category: general_inquiry)"},
        ],
    },

    # General multi-turn (2) -- status: active
    {
        "name": "GENERAL-1",
        "status": "active",
        "messages": [
            {"role": "customer", "content": "What's your return policy?"},
            {"role": "assistant", "content": "We accept returns within 30 days of purchase. Items must be in original condition with tags attached. Refunds are processed within 5-7 business days. For defective items, we cover return shipping costs."},
            {"role": "customer", "content": "Can you give me more details about that?"},
            {"role": "assistant", "content": "Sure! Here are the full details of our return policy: You have 30 days from the date of delivery to initiate a return. Items must be unworn, unwashed, and in their original packaging with all tags attached. Once we receive your return, we'll process your refund within 5-7 business days to your original payment method. If you received a defective or damaged item, we'll provide a prepaid return label at no charge."},
        ],
    },
    {
        "name": "GENERAL-2",
        "status": "active",
        "messages": [
            {"role": "customer", "content": "Can you tell me about your shipping options?"},
            {"role": "assistant", "content": "We offer several shipping options: Standard shipping (3-5 business days), Express shipping (1-2 business days), and international shipping (7-14 business days). We ship to over 50 countries!"},
            {"role": "customer", "content": "How much does express shipping cost?"},
            {"role": "assistant", "content": "Express shipping costs $12.99 for orders under $75, and it's free for orders over $150. Standard shipping is free for all orders over $75. The exact cost will be calculated at checkout based on your location and package weight."},
        ],
    },

    # Manually escalated with category (2) -- status: escalated, has assigned_to
    {
        "name": "MANUAL-ESC-1",
        "status": "escalated",
        "escalation_category": "service",
        "assigned_to": True,  # Will be resolved to actual agent ID
        "messages": [
            {"role": "customer", "content": "I have a question about my recent order"},
            {"role": "assistant", "content": "I'd be happy to help with your order! Could you provide your order number so I can look it up for you?"},
            {"role": "system", "content": "Conversation manually escalated by admin (category: service)"},
        ],
    },
    {
        "name": "MANUAL-ESC-2",
        "status": "escalated",
        "escalation_category": "support",
        "assigned_to": True,
        "messages": [
            {"role": "customer", "content": "I need help with a product I purchased"},
            {"role": "assistant", "content": "I'm sorry to hear you're having trouble. Let me connect you with our support team for personalized assistance."},
            {"role": "system", "content": "Conversation manually escalated by admin (category: support)"},
        ],
    },

    # Unassigned escalated (2) -- status: escalated, no assigned_to
    {
        "name": "UNASSIGNED-1",
        "status": "escalated",
        "escalation_category": "general_inquiry",
        "messages": [
            {"role": "customer", "content": "I want a human agent, not a bot"},
            {"role": "assistant", "content": "I understand. Let me connect you with a human team member."},
            {"role": "system", "content": "Conversation escalated (unassigned)"},
        ],
    },
    {
        "name": "UNASSIGNED-2",
        "status": "escalated",
        "messages": [
            {"role": "customer", "content": "Transfer me to a real person right now"},
            {"role": "assistant", "content": "Of course, transferring you now."},
            {"role": "system", "content": "Conversation escalated (unassigned)"},
        ],
    },

    # Archive candidate (1) -- status: resolved (ended)
    {
        "name": "ARCHIVE-1",
        "status": "resolved",
        "messages": [
            {"role": "customer", "content": "Thank you, that answers my question!"},
            {"role": "assistant", "content": "You're welcome! If you have any other questions in the future, don't hesitate to ask. Have a great day!"},
        ],
    },
]


async def seed_conversations(dry_run: bool = True) -> None:
    """Insert conversation documents directly into Cosmos DB."""

    from azure.cosmos.aio import CosmosClient

    endpoint = os.environ.get("COSMOS_DB_ENDPOINT", "")
    key = os.environ.get("COSMOS_DB_KEY", "")

    if not endpoint or not key:
        print("[FAIL] Missing COSMOS_ENDPOINT or COSMOS_KEY in environment")
        return

    # Load team member IDs for assigned_to
    agent_ids: list[str] = []
    if CREDENTIALS_FILE.exists():
        with open(CREDENTIALS_FILE) as f:
            creds = json.load(f)
        # Load member keys to find escalation agent IDs
        member_keys_str = creds.get("member_keys", "{}")
        if isinstance(member_keys_str, str):
            member_keys = json.loads(member_keys_str)
        else:
            member_keys = member_keys_str
        # Use the member emails as agent identifiers
        agent_ids = list(member_keys.keys())[:2]  # first 2 agents

    print(f"[INFO] Tenant: {TENANT_ID}")
    print(f"[INFO] Conversations: {len(CONVERSATIONS)}")
    print(f"[INFO] Agent IDs for assignment: {agent_ids}")
    print(f"[INFO] Mode: {'EXECUTE' if not dry_run else 'DRY RUN'}")

    if dry_run:
        for conv in CONVERSATIONS:
            flags = []
            if conv.get("escalation_category"):
                flags.append(f"cat={conv['escalation_category']}")
            if conv.get("assigned_to"):
                flags.append("assigned")
            print(f"  [DRY] {conv['name']}: status={conv['status']} msgs={len(conv['messages'])} {' '.join(flags)}")
        return

    async with CosmosClient(endpoint, key) as client:
        db = client.get_database_client("agentred")
        container = db.get_container_client("conversations")

        created = 0
        conv_ids: dict[str, str] = {}

        for i, conv in enumerate(CONVERSATIONS):
            conv_id = str(uuid.uuid4())
            conv_ids[conv["name"]] = conv_id

            # Timestamps spread over the last 2 hours for realistic ordering
            offset_minutes = (len(CONVERSATIONS) - i) * 6
            started = NOW - timedelta(minutes=offset_minutes)
            last_activity = started + timedelta(minutes=2)

            # Add timestamps to messages
            messages_with_ts = []
            for j, msg in enumerate(conv["messages"]):
                ts = started + timedelta(seconds=j * 30)
                messages_with_ts.append({
                    **msg,
                    "timestamp": ts.isoformat(),
                })

            # Determine assigned_to
            assigned_to = None
            if conv.get("assigned_to") is True and agent_ids:
                assigned_to = agent_ids[i % len(agent_ids)]

            doc = {
                "id": conv_id,
                "tenant_id": TENANT_ID,
                "conversation_id": conv_id,
                "status": conv["status"],
                "customer_id": f"visitor-{i+1:03d}",
                "is_billable": True,
                "message_count": len(conv["messages"]),
                "turn_count": sum(1 for m in conv["messages"] if m["role"] == "customer"),
                "agents_invoked": ["intent_classifier", "knowledge_retriever", "response_generator", "critic"],
                "model_used": "gpt-4o",
                "critic_passed": True,
                "assigned_to": assigned_to,
                "escalation_category": conv.get("escalation_category"),
                "internal_notes": [],
                "messages": messages_with_ts,
                "started_at": started.isoformat(),
                "ended_at": last_activity.isoformat() if conv["status"] == "resolved" else None,
                "last_activity_at": last_activity.isoformat(),
                "first_chunk_at": (started + timedelta(seconds=2)).isoformat(),
                "archived_at": None,
                "is_test_mode": False,
            }

            try:
                await container.create_item(doc)
                print(f"  [PASS] [{i+1}/{len(CONVERSATIONS)}] {conv['name']}: {conv['status']} (id={conv_id[:12]}...)")
                created += 1
            except Exception as e:
                print(f"  [FAIL] [{i+1}/{len(CONVERSATIONS)}] {conv['name']}: {e}")

        print(f"\n[RESULT] Conversations created: {created}/{len(CONVERSATIONS)}")

        # Save conversation IDs to credentials file
        if CREDENTIALS_FILE.exists():
            with open(CREDENTIALS_FILE) as f:
                creds = json.load(f)
            creds["conversation_ids"] = json.dumps(conv_ids)
            with open(CREDENTIALS_FILE, "w") as f:
                json.dump(creds, f, indent=2)
            print(f"[INFO] Conversation IDs saved to {CREDENTIALS_FILE}")


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Seed conversation documents into Cosmos DB")
    parser.add_argument("--execute", action="store_true", help="Actually insert (without = dry run)")
    args = parser.parse_args()

    asyncio.run(seed_conversations(dry_run=not args.execute))


if __name__ == "__main__":
    main()
