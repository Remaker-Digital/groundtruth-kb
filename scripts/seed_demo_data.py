"""
Seed demo data for the Agent Red standalone admin preview.

Creates realistic conversations, team members, and usage counters in
Cosmos DB so the UX designer can see a populated admin dashboard.

Usage:
    # Preview only (no DB writes):
    python scripts/seed_demo_data.py

    # Write to Cosmos DB:
    python scripts/seed_demo_data.py --seed

    # Also seed knowledge base (32 articles):
    python scripts/seed_demo_data.py --seed --seed-kb

Requires Azure credentials in .env.local:
    COSMOS_DB_ENDPOINT, COSMOS_DB_KEY, COSMOS_DB_DATABASE

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import random
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Project setup
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

_env_path = PROJECT_ROOT / ".env.local"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TENANT_ID = "remaker-digital-001"
NOW = datetime.now(timezone.utc)
BILLING_PERIOD = NOW.strftime("%Y-%m")

# Customer personas for realistic conversations
CUSTOMERS = [
    {"id": "cust-sarah-001", "name": "Sarah Chen", "email": "sarah@example.com"},
    {"id": "cust-marcus-002", "name": "Marcus Rivera", "email": "marcus@example.com"},
    {"id": "cust-emily-003", "name": "Emily Thompson", "email": "emily@example.com"},
    {"id": "cust-james-004", "name": "James Park", "email": "james@example.com"},
    {"id": "cust-aisha-005", "name": "Aisha Patel", "email": "aisha@example.com"},
    {"id": "cust-tom-006", "name": "Tom Brewster", "email": "tom@example.com"},
    {"id": "cust-nina-007", "name": "Nina Kowalski", "email": "nina@example.com"},
    {"id": "cust-david-008", "name": "David Kim", "email": "david@example.com"},
    {"id": "cust-rachel-009", "name": "Rachel Green", "email": "rachel@example.com"},
    {"id": "cust-alex-010", "name": "Alex Moreau", "email": "alex@example.com"},
]

# Realistic conversation templates
CONVERSATION_TEMPLATES = [
    {
        "topic": "pricing",
        "messages": [
            {"role": "customer", "content": "Hi, I'm interested in Agent Red for my Shopify store. How does the pricing work?"},
            {"role": "agent", "content": "Welcome! Agent Red offers three tiers:\n\n- **Starter** ($149/mo): 1,000 conversations included\n- **Professional** ($399/mo): 5,000 conversations included\n- **Enterprise** ($999/mo): 20,000 conversations included\n\nAll plans include our full AI pipeline with 6 specialized agents, Persistent Customer Memory, and fail-closed safety validation. Would you like me to help you estimate which tier fits your store's volume?"},
            {"role": "customer", "content": "We get about 3,000 support messages a month. Which plan would you recommend?"},
            {"role": "agent", "content": "Based on 3,000 monthly conversations, the **Professional plan** ($399/mo) would be ideal. It includes 5,000 conversations, giving you room to grow. You'd also get cross-session learning (Layer 3 memory) which builds customer preference profiles over time.\n\nAt your volume, the effective cost per conversation is about $0.08 - compared to $0.40-$1.00+ with competitors like Gorgias or Tidio Pro. That's 4-12x more cost-effective.\n\nWould you like to start a 14-day free trial?"},
        ],
        "agents": ["intent-classifier", "knowledge-retrieval", "response-generator", "critic-supervisor"],
        "status": "ended",
    },
    {
        "topic": "setup",
        "messages": [
            {"role": "customer", "content": "I just installed the Agent Red app on my Shopify store. How do I set it up?"},
            {"role": "agent", "content": "Great choice! Here's how to get started:\n\n1. **Complete the Setup Wizard** - Go to the Agent Red admin panel. The 9-step wizard will guide you through brand voice, escalation rules, and widget appearance.\n\n2. **Seed your Knowledge Base** - Add your FAQs, product info, and policies. The AI uses this to answer customer questions accurately.\n\n3. **Customize your Widget** - Choose colors, position, greeting message, and avatar to match your store's brand.\n\n4. **Enable the Chat Widget** - In Shopify Admin > Online Store > Themes > Customize, toggle the Agent Red Chat app embed.\n\nThe whole process takes about 15-20 minutes. Need help with any specific step?"},
            {"role": "customer", "content": "How do I add my return policy to the knowledge base?"},
            {"role": "agent", "content": "Go to **Knowledge Base** in the left sidebar. Click **Add Article**, then:\n\n- **Title**: \"Return Policy\"\n- **Category**: Select \"Policy\"\n- **Content**: Paste your return policy text\n\nOnce saved, the AI will immediately start using it to answer return-related questions. You can also add articles for shipping, warranty, sizing guides, and any other common topics.\n\nTip: The more detailed your knowledge base, the better the AI responses. Would you like help formatting any of your policies?"},
            {"role": "customer", "content": "That's perfect, thanks!"},
            {"role": "agent", "content": "You're welcome! If you need anything else during setup, just ask. Your AI assistant is ready to start helping customers as soon as you enable the widget. Have a great day!"},
        ],
        "agents": ["intent-classifier", "knowledge-retrieval", "response-generator", "critic-supervisor"],
        "status": "ended",
    },
    {
        "topic": "integration",
        "messages": [
            {"role": "customer", "content": "Does Agent Red integrate with Zendesk? We use it for our support tickets."},
            {"role": "agent", "content": "Yes! Agent Red integrates with Zendesk for seamless escalation. When the AI detects a conversation that needs human attention - complex complaints, refund disputes, or when a customer explicitly asks for a person - it automatically creates a Zendesk ticket with the full conversation context.\n\nThe integration uses Zendesk's REST API with your existing API token. You can configure escalation rules in the Configuration page - set keywords, confidence thresholds, and routing preferences.\n\nWould you like me to walk you through the Zendesk setup?"},
            {"role": "customer", "content": "Yes please, what do I need to configure?"},
            {"role": "agent", "content": "Here's what you'll need:\n\n1. Your Zendesk subdomain (e.g., yourcompany.zendesk.com)\n2. An API token from Zendesk Admin > API > OAuth Tokens\n3. The email associated with your Zendesk admin account\n\nIn Agent Red, go to **Configuration** > **Integrations** section and enter these credentials. The connection is tested immediately.\n\nEscalated conversations will appear in Zendesk with:\n- Full conversation transcript\n- Customer sentiment analysis\n- AI's confidence score\n- Suggested category tags\n\nThis saves your agents significant context-switching time. Need anything else?"},
        ],
        "agents": ["intent-classifier", "knowledge-retrieval", "response-generator", "critic-supervisor"],
        "status": "ended",
    },
    {
        "topic": "escalation",
        "messages": [
            {"role": "customer", "content": "I need to speak with a human agent please. The AI keeps giving me wrong information about my order."},
            {"role": "agent", "content": "I completely understand your frustration, and I apologize for any incorrect information. Let me connect you with a human agent right away.\n\nI'm transferring you now with the full context of our conversation so you won't need to repeat yourself. A team member will be with you shortly.\n\nIs there anything specific you'd like me to flag for the agent about your order issue?"},
            {"role": "customer", "content": "Yes, my order #1234 was supposed to arrive 3 days ago and tracking shows it's still in transit."},
            {"role": "system", "content": "Conversation escalated to human agent. Reason: Customer requested human assistance. Order tracking issue flagged."},
        ],
        "agents": ["intent-classifier", "knowledge-retrieval", "response-generator", "escalation", "critic-supervisor"],
        "status": "escalated",
    },
    {
        "topic": "features",
        "messages": [
            {"role": "customer", "content": "What makes Agent Red different from Tidio or Gorgias?"},
            {"role": "agent", "content": "Great question! Here are Agent Red's key differentiators:\n\n**1. Persistent Customer Memory** - Our unique 4-layer memory system remembers every customer across sessions. No competitor offers per-customer vector RAG over historical transcripts.\n\n**2. Price** - Agent Red is 4-21x cheaper per conversation than Gorgias, Tidio Pro, Zendesk, or Intercom.\n\n**3. Speed** - Our P50 latency target is 1,500ms, compared to Intercom's published 7,000ms.\n\n**4. Safety** - Fail-closed Critic validation means no unvalidated AI response ever reaches your customers.\n\n**5. Lightweight Widget** - 15-20KB gzip vs Tidio's 40-60KB or Intercom's 80-100KB.\n\nWould you like a detailed comparison for any specific feature?"},
        ],
        "agents": ["intent-classifier", "knowledge-retrieval", "response-generator", "critic-supervisor"],
        "status": "ended",
    },
    {
        "topic": "billing",
        "messages": [
            {"role": "customer", "content": "I'm on the Starter plan and just hit my 1,000 conversation limit. What happens now?"},
            {"role": "agent", "content": "No worries - your service continues uninterrupted! Here's how overage works:\n\nOnce you exceed your included 1,000 conversations, additional conversations are billed at $0.04 each. You can also pre-purchase **Conversation Packs** at a discount:\n\n- 1,000 pack: $29 ($0.029/conv)\n- 5,000 pack: $99 ($0.020/conv)\n- 20,000 pack: $249 ($0.012/conv)\n\nPacks are valid for 90 days and consumed before overage billing kicks in.\n\nAlternatively, upgrading to **Professional** ($399/mo for 5,000 included) might save you money if your volume stays above 1,000. Would you like me to help you compare?"},
        ],
        "agents": ["intent-classifier", "knowledge-retrieval", "response-generator", "critic-supervisor"],
        "status": "ended",
    },
    {
        "topic": "widget_customization",
        "messages": [
            {"role": "customer", "content": "Can I change the colors of the chat widget to match my store's theme?"},
            {"role": "agent", "content": "Absolutely! The widget is fully customizable. Go to **Widget** in the admin sidebar. You can configure:\n\n- **Primary color** - Button and header accent color\n- **Position** - Bottom-right, bottom-left, or custom offset\n- **Dark/Light mode** - Including auto-detection\n- **Agent name and avatar** - Your brand identity\n- **Greeting message** - First message customers see\n- **Pre-chat form** - Collect name/email before chat starts\n\nChanges preview in real-time on the right side of the configuration page. Once saved, they deploy instantly to your live store.\n\nThe widget uses Shadow DOM isolation, so your store's CSS never interferes with the chat styling and vice versa."},
            {"role": "customer", "content": "Perfect, can I also hide it on certain pages like the checkout?"},
            {"role": "agent", "content": "Yes! Use **Page Rules** in the Widget configuration. You can set glob patterns like:\n\n- `/checkout/*` - Hide on checkout pages\n- `/account/*` - Hide on account pages\n- `/collections/sale` - Hide on specific collection\n\nThe widget will only appear on pages that don't match your exclusion rules. This is great for reducing distractions during checkout."},
        ],
        "agents": ["intent-classifier", "knowledge-retrieval", "response-generator", "critic-supervisor"],
        "status": "ended",
    },
    {
        "topic": "memory",
        "messages": [
            {"role": "customer", "content": "I chatted with your AI last week about sizing for the blue jacket. Does it remember me?"},
            {"role": "agent", "content": "Yes! I can see from our previous conversation that you were looking at the Alpine Blue Puffer Jacket in size L. You mentioned you typically wear L in most brands but were concerned about the chest measurement.\n\nBased on your preferences, the L should fit well - the chest measures 44 inches which matches what you described. We also noted you prefer a slightly relaxed fit.\n\nWould you like to go ahead with the L, or would you like me to check any other measurements?"},
            {"role": "customer", "content": "Wow, that's impressive! Yes, I'll go with the L. Thanks for remembering!"},
            {"role": "agent", "content": "Happy to help! That's our Persistent Customer Memory at work - every interaction builds on the last so you never have to repeat yourself.\n\nYou can add the Alpine Blue Puffer Jacket in size L to your cart directly from our product page. If you have any questions about care instructions or return policy, I'm here!\n\nEnjoy the jacket!"},
        ],
        "agents": ["intent-classifier", "knowledge-retrieval", "response-generator", "critic-supervisor"],
        "status": "ended",
    },
    {
        "topic": "trial",
        "messages": [
            {"role": "customer", "content": "How does the free trial work?"},
            {"role": "agent", "content": "Our 14-day free trial includes:\n\n- 50 conversations to test with real customers\n- Layer 1 Persistent Customer Memory\n- Full admin dashboard access\n- Demo data pre-loaded so you can explore immediately\n- No credit card required to start\n\nDuring the trial, you'll see exactly how the AI handles your customers, including the memory system and safety validation. At the end of 14 days, you choose a plan or the trial expires naturally - no surprise charges. Your configuration and knowledge base are preserved when you upgrade.\n\nWant to start your trial now?"},
        ],
        "agents": ["intent-classifier", "knowledge-retrieval", "response-generator", "critic-supervisor"],
        "status": "active",
    },
    {
        "topic": "technical",
        "messages": [
            {"role": "customer", "content": "What AI models does Agent Red use? I want to understand the tech behind it."},
            {"role": "agent", "content": "Agent Red uses a pipeline of 6 specialized AI agents, each optimized for their task:\n\n1. **Intent Classifier** (GPT-4o-mini) - Routes queries across 17 intent categories with 98% accuracy\n2. **Knowledge Retrieval** (text-embedding-3-large) - Searches your knowledge base using semantic vector search\n3. **Response Generator** (GPT-4o) - Crafts personalized responses using context from all other agents\n4. **Escalation Handler** (GPT-4o-mini) - Detects when human intervention is needed\n5. **Critic/Supervisor** (GPT-4o-mini) - Validates every response for safety before delivery\n6. **Analytics** (GPT-4o-mini) - Monitors performance metrics\n\nAll models run on Azure OpenAI Service within the Azure security perimeter. PII is tokenized before any external AI call.\n\nWant to know more about any specific component?"},
        ],
        "agents": ["intent-classifier", "knowledge-retrieval", "response-generator", "critic-supervisor"],
        "status": "ended",
    },
    {
        "topic": "order_tracking",
        "messages": [
            {"role": "customer", "content": "Where's my order? I placed it 5 days ago."},
            {"role": "agent", "content": "I'd be happy to help you track your order! Could you please provide your order number? It should be in your confirmation email, starting with # followed by numbers."},
            {"role": "customer", "content": "It's #2847"},
            {"role": "agent", "content": "Thank you! I can see order #2847 was shipped on February 1st via USPS Priority Mail. The tracking number is 9400111899223847562. According to the latest update, it's currently at the regional distribution center and is expected to arrive by February 7th.\n\nYou can track it directly at usps.com with that tracking number. Would you like me to help with anything else regarding your order?"},
            {"role": "customer", "content": "Thanks, that's all I needed!"},
        ],
        "agents": ["intent-classifier", "knowledge-retrieval", "response-generator", "critic-supervisor"],
        "status": "ended",
    },
    {
        "topic": "return_request",
        "messages": [
            {"role": "customer", "content": "I want to return the shoes I bought. They don't fit right."},
            {"role": "agent", "content": "I'm sorry to hear the shoes didn't fit! I can help you with a return.\n\nBased on our return policy, you have 30 days from delivery for a full refund on unworn items. Here's what to do:\n\n1. Pack the shoes in their original box\n2. Include the packing slip from your order\n3. Use our prepaid return label (I can email it to you)\n\nOnce we receive the return, your refund will be processed within 3-5 business days.\n\nWould you like me to send the return label to your email on file, or would you prefer an exchange for a different size?"},
            {"role": "customer", "content": "Exchange for a half size up please"},
            {"role": "agent", "content": "I'll set up an exchange for one half size up. Let me check availability... Great news, that size is in stock!\n\nI'll send a return label to your email and the exchange pair will ship as soon as we receive the return. You'll get a new tracking number by email.\n\nIs there anything else I can help with?"},
        ],
        "agents": ["intent-classifier", "knowledge-retrieval", "response-generator", "critic-supervisor"],
        "status": "ended",
    },
]

# Team members
TEAM_MEMBERS = [
    {"email": "mike@remakerdigital.com", "name": "Mike VanDusen", "role": "owner"},
    {"email": "sarah@remakerdigital.com", "name": "Sarah Mitchell", "role": "admin"},
    {"email": "carlos@remakerdigital.com", "name": "Carlos Mendez", "role": "agent"},
    {"email": "priya@remakerdigital.com", "name": "Priya Sharma", "role": "agent"},
]


# ---------------------------------------------------------------------------
# Data generation helpers
# ---------------------------------------------------------------------------


def random_past_datetime(days_back_max: int = 30) -> datetime:
    """Return a random datetime within the last N days."""
    delta = timedelta(
        days=random.randint(0, days_back_max),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59),
    )
    return NOW - delta


def build_conversation_docs() -> list[dict]:
    """Generate conversation documents from templates."""
    docs = []

    for i, template in enumerate(CONVERSATION_TEMPLATES):
        customer = CUSTOMERS[i % len(CUSTOMERS)]
        started = random_past_datetime(28)
        # Space messages ~30-120 seconds apart
        msg_list = []
        current_ts = started
        for msg in template["messages"]:
            current_ts = current_ts + timedelta(seconds=random.randint(15, 120))
            msg_list.append({
                "role": msg["role"],
                "content": msg["content"],
                "timestamp": current_ts.isoformat(),
                "message_id": str(uuid.uuid4()),
            })

        ended = current_ts + timedelta(seconds=random.randint(5, 60))
        is_ended = template["status"] in ("ended", "escalated")
        conv_id = f"conv-demo-{i+1:03d}"

        doc = {
            "id": conv_id,
            "tenant_id": TENANT_ID,
            "conversation_id": conv_id,
            "status": template["status"],
            "customer_id": customer["id"],
            "customer_name": customer["name"],
            "is_billable": True,
            "is_escalated": template["status"] == "escalated",
            "message_count": len(msg_list),
            "turn_count": len([m for m in msg_list if m["role"] == "customer"]),
            "agents_invoked": template["agents"],
            "model_used": "gpt-4o",
            "critic_passed": True if template["status"] != "escalated" else None,
            "assigned_to": "carlos@remakerdigital.com" if template["status"] == "escalated" else None,
            "internal_notes": [],
            "messages": msg_list,
            "started_at": started.isoformat(),
            "ended_at": ended.isoformat() if is_ended else None,
            "last_activity_at": current_ts.isoformat(),
            "last_message_at": current_ts.isoformat(),
        }
        docs.append(doc)

    # Add a few more conversations to pad daily volume (no messages, just stats)
    for j in range(len(CONVERSATION_TEMPLATES), 45):
        customer = random.choice(CUSTOMERS)
        started = random_past_datetime(30)
        ended = started + timedelta(minutes=random.randint(1, 15))
        conv_id = f"conv-demo-{j+1:03d}"

        simple_messages = [
            {"role": "customer", "content": "Quick question about shipping times.",
             "timestamp": started.isoformat(), "message_id": str(uuid.uuid4())},
            {"role": "agent", "content": "Standard shipping takes 3-5 business days. Express is 1-2 days for an additional fee.",
             "timestamp": (started + timedelta(seconds=45)).isoformat(), "message_id": str(uuid.uuid4())},
        ]

        doc = {
            "id": conv_id,
            "tenant_id": TENANT_ID,
            "conversation_id": conv_id,
            "status": random.choice(["ended", "ended", "ended", "active"]),
            "customer_id": customer["id"],
            "customer_name": customer["name"],
            "is_billable": True,
            "is_escalated": False,
            "message_count": 2,
            "turn_count": 1,
            "agents_invoked": ["intent-classifier", "knowledge-retrieval", "response-generator", "critic-supervisor"],
            "model_used": "gpt-4o",
            "critic_passed": True,
            "assigned_to": None,
            "internal_notes": [],
            "messages": simple_messages,
            "started_at": started.isoformat(),
            "ended_at": ended.isoformat() if random.random() > 0.15 else None,
            "last_activity_at": ended.isoformat(),
            "last_message_at": ended.isoformat(),
        }
        docs.append(doc)

    return docs


def build_team_member_docs() -> list[dict]:
    """Generate team member documents."""
    docs = []
    for member in TEAM_MEMBERS:
        doc_id = f"{TENANT_ID}:{member['email']}"
        joined = NOW - timedelta(days=random.randint(7, 60))
        last_login = NOW - timedelta(hours=random.randint(1, 72))
        docs.append({
            "id": doc_id,
            "tenant_id": TENANT_ID,
            "email": member["email"],
            "display_name": member["name"],
            "role": member["role"],
            "is_active": True,
            "max_concurrent_conversations": 10 if member["role"] in ("owner", "admin") else 5,
            "created_at": joined.isoformat(),
            "updated_at": last_login.isoformat(),
            "last_login_at": last_login.isoformat(),
            "invited_by": "mike@remakerdigital.com" if member["role"] != "owner" else None,
        })
    return docs


# ---------------------------------------------------------------------------
# Persistent Customer Memory demo data (WI-D)
# ---------------------------------------------------------------------------

# Sarah's 3-session narrative (Starter tier — Layer 1 profile recognition)
SARAH_SESSIONS = [
    {
        "conv_id": "conv-sarah-mem-001",
        "days_ago": 14,
        "topic": "Initial product inquiry",
        "messages": [
            {"role": "customer", "content": "Hi! I'm looking for a winter jacket for hiking. I'm usually a size M in women's."},
            {"role": "agent", "content": "Welcome, Sarah! I'd recommend our Alpine Trail Puffer in size M. It's rated to -15C and weighs only 450g. Our customers love it for winter hiking. Would you like to see the color options?"},
            {"role": "customer", "content": "Yes! Do you have it in dark green?"},
            {"role": "agent", "content": "Great choice! The Alpine Trail Puffer comes in Forest Green, Midnight Blue, and Charcoal. The Forest Green is one of our most popular colors. I've noted your preference for dark green. Shall I add it to your cart?"},
            {"role": "customer", "content": "Not yet, I want to think about it. Thanks!"},
        ],
    },
    {
        "conv_id": "conv-sarah-mem-002",
        "days_ago": 7,
        "topic": "Return visit — AI remembers preferences",
        "messages": [
            {"role": "customer", "content": "Hi again! I'm back to look at that jacket."},
            {"role": "agent", "content": "Welcome back, Sarah! I remember you were interested in the Alpine Trail Puffer in Forest Green, size M. It's still in stock! Since your last visit, we've also started a 15% winter clearance sale that applies to this jacket. Would you like to take advantage of that?"},
            {"role": "customer", "content": "Oh nice! Yes, that sounds great. Can you also tell me about the return policy?"},
            {"role": "agent", "content": "Absolutely! We offer a 30-day no-questions-asked return policy. If the M doesn't fit, you can exchange it for free — we'll even cover return shipping. Given that you mentioned hiking, I'd note the jacket is designed for a slightly athletic fit, so it may run a touch slimmer than casual brands. Would you like me to add the Forest Green M to your cart at the sale price?"},
            {"role": "customer", "content": "Yes please! Add it to my cart."},
            {"role": "agent", "content": "Done! The Alpine Trail Puffer in Forest Green, size M has been added to your cart at $169.15 (15% off $199). Happy hiking, Sarah!"},
        ],
    },
    {
        "conv_id": "conv-sarah-mem-003",
        "days_ago": 2,
        "topic": "Post-purchase — AI references purchase history",
        "messages": [
            {"role": "customer", "content": "Hi! I received my jacket yesterday. It fits perfectly but the zipper feels a bit stiff."},
            {"role": "agent", "content": "Hi Sarah! I'm glad the Alpine Trail Puffer in Forest Green fits well! The zipper stiffness is common with new jackets — it should loosen up after a few uses. You can also apply a small amount of zipper wax or silicone lubricant to help. If it doesn't improve within a week, we'll exchange it under our 30-day policy. How does that sound?"},
            {"role": "customer", "content": "That's helpful, I'll try the wax. Also, do you have matching hiking pants?"},
            {"role": "agent", "content": "Yes! Since you liked the Alpine Trail Puffer, you might love the Alpine Trail Softshell Pants. They come in Forest Green (matching your jacket!) in size M. They're water-resistant with articulated knees for hiking. $89 regular price, or $75.65 with the winter clearance. Would you like to see more details?"},
        ],
    },
]

# Marcus's 5-session narrative (Professional tier — Layer 3 patterns)
MARCUS_SESSIONS = [
    {
        "conv_id": "conv-marcus-mem-001",
        "days_ago": 30,
        "topic": "First interaction — product research",
        "messages": [
            {"role": "customer", "content": "Looking for a road bike under $2000. I commute 15 miles daily."},
            {"role": "agent", "content": "For a 15-mile daily commute under $2,000, I'd recommend the Velocity Commuter Pro ($1,799). It features a lightweight aluminum frame, Shimano 105 groupset, and hydraulic disc brakes — ideal for stop-and-go urban riding. We also have the Endurance Sport ($1,499) if you'd prefer to save for accessories. Which interests you more?"},
            {"role": "customer", "content": "Tell me more about the Velocity. What's the weight?"},
            {"role": "agent", "content": "The Velocity Commuter Pro weighs 9.2kg (20.3 lbs). Key specs:\n- Shimano 105 R7000 11-speed\n- Hydraulic disc brakes (all-weather stopping)\n- 700x28c puncture-resistant tires\n- Integrated rear rack mounts\n\nIt's been our best-selling commuter for the past two seasons. Would you like to schedule a test ride?"},
        ],
    },
    {
        "conv_id": "conv-marcus-mem-002",
        "days_ago": 25,
        "topic": "Follow-up — prefers concise technical answers",
        "messages": [
            {"role": "customer", "content": "Back about the Velocity. What tire width can the frame handle?"},
            {"role": "agent", "content": "Max tire clearance: 35mm. Stock is 28mm. Most commuters run 28-32mm for the speed/comfort balance."},
            {"role": "customer", "content": "Good. Fender compatibility?"},
            {"role": "agent", "content": "Full fender mounts, front and rear. SKS Bluemels 45mm fit perfectly. Want me to bundle them with the bike?"},
            {"role": "customer", "content": "Not yet. What colors?"},
            {"role": "agent", "content": "Matte Black, Gunmetal Grey, and Racing Red. All three in stock in your size range (I'll confirm exact sizing when you're ready)."},
        ],
    },
    {
        "conv_id": "conv-marcus-mem-003",
        "days_ago": 18,
        "topic": "Purchase decision — AI adapts to communication style",
        "messages": [
            {"role": "customer", "content": "Ready to buy the Velocity in Matte Black. I'm 5'11\". What size?"},
            {"role": "agent", "content": "56cm frame. Our sizing chart puts 5'11\" at 56cm for road geometry. Added to cart: Velocity Commuter Pro, Matte Black, 56cm — $1,799. Proceed to checkout?"},
            {"role": "customer", "content": "Yes. Also add the SKS fenders you mentioned."},
            {"role": "agent", "content": "Done. Cart total: $1,799 + $45 (SKS Bluemels 45mm) = $1,844 before tax. Free shipping on orders over $100. Anything else?"},
            {"role": "customer", "content": "That's it. Thanks."},
        ],
    },
    {
        "conv_id": "conv-marcus-mem-004",
        "days_ago": 10,
        "topic": "Post-purchase — pattern: prefers minimal interaction",
        "messages": [
            {"role": "customer", "content": "Bike arrived. Front derailleur needs adjusting — shifts skip between 3rd and 4th gear."},
            {"role": "agent", "content": "That's a cable tension issue — common after shipping. Two options:\n1. Self-adjust: quarter-turn clockwise on the barrel adjuster near the shifter\n2. Free tune-up at any partner shop (use order #MR-2847)\n\nWhich do you prefer?"},
            {"role": "customer", "content": "I'll try the barrel adjuster first. If that doesn't work, where's the nearest partner shop to 94110?"},
            {"role": "agent", "content": "Nearest to 94110:\n- Bay City Bikes, 1489 Valencia St (0.8 mi) — open until 7pm today\n- Pedal Works, 3255 21st St (1.2 mi) — appointment only\n\nBoth honor the free tune-up with your order number."},
        ],
    },
    {
        "conv_id": "conv-marcus-mem-005",
        "days_ago": 3,
        "topic": "Accessory inquiry — AI uses learned preferences",
        "messages": [
            {"role": "customer", "content": "Need a bike lock recommendation. Something portable."},
            {"role": "agent", "content": "For your daily commute, two options:\n- Kryptonite Evolution Mini-7 ($79) — 3.5 lbs, fits in a jersey pocket\n- ABUS Bordo 6000 ($89) — foldable, mounts on frame\n\nBoth are Sold Secure Gold rated. Given your preference for minimal gear, the Bordo frame mount keeps it out of your way."},
            {"role": "customer", "content": "Bordo. Add to cart."},
            {"role": "agent", "content": "Added: ABUS Bordo 6000, $89. Ships free. Your Velocity accessories are building up nicely. Anything else?"},
            {"role": "customer", "content": "No. Thanks."},
        ],
    },
]

# Marcus's extracted patterns (Layer 3)
MARCUS_PATTERNS = [
    {
        "pattern_type": "communication_preferences",
        "pattern_key": "prefers_concise_replies",
        "value": "Customer prefers brief, technical answers without unnecessary elaboration",
        "confidence": 0.92,
        "reinforcement_count": 4,
    },
    {
        "pattern_type": "communication_preferences",
        "pattern_key": "minimal_social_interaction",
        "value": "Customer uses short responses and prefers transactional exchanges",
        "confidence": 0.85,
        "reinforcement_count": 3,
    },
    {
        "pattern_type": "product_interests",
        "pattern_key": "cycling_commuter",
        "value": "Daily cycling commuter, interested in practical urban riding gear",
        "confidence": 0.95,
        "reinforcement_count": 5,
    },
    {
        "pattern_type": "product_interests",
        "pattern_key": "values_specs_over_marketing",
        "value": "Asks direct technical questions (weight, specs, dimensions) rather than subjective opinions",
        "confidence": 0.88,
        "reinforcement_count": 3,
    },
    {
        "pattern_type": "purchase_behavior",
        "pattern_key": "decisive_buyer",
        "value": "Makes purchase decisions quickly once technical questions are answered",
        "confidence": 0.80,
        "reinforcement_count": 2,
    },
    {
        "pattern_type": "geographic_context",
        "pattern_key": "location_sf_94110",
        "value": "Located in San Francisco 94110 (Mission District), commutes by bike",
        "confidence": 0.90,
        "reinforcement_count": 1,
    },
]


def build_customer_profile_docs() -> list[dict]:
    """Generate customer profile documents (Layer 1)."""
    profiles = []

    # Sarah — Starter tier, basic profile
    sarah_profile = {
        "id": f"{TENANT_ID}:cust-sarah-001",
        "tenant_id": TENANT_ID,
        "customer_id": "cust-sarah-001",
        "purchase_history": [
            {
                "product_id": "alpine-trail-puffer",
                "product_name": "Alpine Trail Puffer - Forest Green M",
                "date": (NOW - timedelta(days=5)).isoformat(),
                "amount": 169.15,
                "rating": None,
                "review_snippet": None,
            },
        ],
        "product_questions": [
            {
                "question": "Do you have the Alpine Trail Puffer in dark green?",
                "product_id": "alpine-trail-puffer",
                "date": (NOW - timedelta(days=14)).isoformat(),
                "resolved": True,
            },
            {
                "question": "Zipper feels stiff on new jacket",
                "product_id": "alpine-trail-puffer",
                "date": (NOW - timedelta(days=2)).isoformat(),
                "resolved": True,
            },
        ],
        "region_codes": {
            "shipping_region": "US-West",
            "timezone": "America/Los_Angeles",
            "locale": "en-US",
        },
        "marketing_segments": ["outdoor-enthusiasts", "winter-clearance-shopper"],
        "jurisdiction_codes": {"country": "US", "state": "CA"},
        "cart_contents": {"active": [], "abandoned": []},
        "consent_status": "granted",
        "created_at": (NOW - timedelta(days=14)).isoformat(),
        "updated_at": (NOW - timedelta(days=2)).isoformat(),
        "last_interaction_at": (NOW - timedelta(days=2)).isoformat(),
    }
    profiles.append(sarah_profile)

    # Marcus — Professional tier, rich profile
    marcus_profile = {
        "id": f"{TENANT_ID}:cust-marcus-002",
        "tenant_id": TENANT_ID,
        "customer_id": "cust-marcus-002",
        "purchase_history": [
            {
                "product_id": "velocity-commuter-pro",
                "product_name": "Velocity Commuter Pro - Matte Black 56cm",
                "date": (NOW - timedelta(days=15)).isoformat(),
                "amount": 1799.00,
                "rating": 5,
                "review_snippet": "Perfect commuter bike, exactly as described",
            },
            {
                "product_id": "sks-bluemels-45mm",
                "product_name": "SKS Bluemels 45mm Fenders",
                "date": (NOW - timedelta(days=15)).isoformat(),
                "amount": 45.00,
                "rating": None,
                "review_snippet": None,
            },
            {
                "product_id": "abus-bordo-6000",
                "product_name": "ABUS Bordo 6000 Folding Lock",
                "date": (NOW - timedelta(days=3)).isoformat(),
                "amount": 89.00,
                "rating": None,
                "review_snippet": None,
            },
        ],
        "product_questions": [
            {
                "question": "Max tire width for Velocity frame?",
                "product_id": "velocity-commuter-pro",
                "date": (NOW - timedelta(days=25)).isoformat(),
                "resolved": True,
            },
            {
                "question": "Front derailleur adjustment after shipping",
                "product_id": "velocity-commuter-pro",
                "date": (NOW - timedelta(days=10)).isoformat(),
                "resolved": True,
            },
        ],
        "region_codes": {
            "shipping_region": "US-West",
            "availability_zone": "SF-Bay",
            "timezone": "America/Los_Angeles",
            "locale": "en-US",
        },
        "marketing_segments": ["cycling-commuter", "high-value-customer", "repeat-buyer"],
        "jurisdiction_codes": {"country": "US", "state": "CA", "zip": "94110"},
        "cart_contents": {"active": [], "abandoned": []},
        "consent_status": "granted",
        "created_at": (NOW - timedelta(days=30)).isoformat(),
        "updated_at": (NOW - timedelta(days=3)).isoformat(),
        "last_interaction_at": (NOW - timedelta(days=3)).isoformat(),
    }
    profiles.append(marcus_profile)

    return profiles


def build_memory_vector_docs() -> list[dict]:
    """Generate mock memory vector documents (Layer 2).

    Uses zero-vectors (placeholder) since real embeddings require
    an Azure OpenAI call. The presence of these documents is
    sufficient to demonstrate the memory retrieval UI.
    """
    vectors = []
    mock_embedding = [0.0] * 3072  # Placeholder 3072-dim vector

    # Sarah's conversation chunks (3 sessions, ~2 chunks each)
    sarah_chunks = [
        ("Looking for winter hiking jacket, size M women's, prefers dark green",
         "conv-sarah-mem-001", 14, ["hiking", "jacket", "sizing"]),
        ("Alpine Trail Puffer, Forest Green, size M — interested but not ready to buy",
         "conv-sarah-mem-001", 14, ["product-interest", "puffer"]),
        ("Returned for jacket, remembered 15% winter clearance, added to cart at $169.15",
         "conv-sarah-mem-002", 7, ["purchase", "clearance-sale"]),
        ("Received jacket, zipper stiffness question, suggested wax lubricant",
         "conv-sarah-mem-003", 2, ["post-purchase", "product-care"]),
        ("Asked about matching hiking pants, suggested Alpine Trail Softshell",
         "conv-sarah-mem-003", 2, ["cross-sell", "hiking-pants"]),
    ]

    for i, (text, conv_id, days_ago, topics) in enumerate(sarah_chunks):
        vectors.append({
            "id": f"vec-sarah-{i+1:03d}",
            "tenant_id": TENANT_ID,
            "customer_id": "cust-sarah-001",
            "conversation_id": conv_id,
            "chunk_text": text,
            "chunk_index": i,
            "embedding": mock_embedding,
            "language": "en",
            "topics": topics,
            "created_at": (NOW - timedelta(days=days_ago)).isoformat(),
            "conversation_date": (NOW - timedelta(days=days_ago)).isoformat(),
        })

    # Marcus's conversation chunks (5 sessions, ~2 chunks each)
    marcus_chunks = [
        ("Road bike research, daily 15-mile commute, budget under $2000",
         "conv-marcus-mem-001", 30, ["commuter-bike", "budget", "research"]),
        ("Velocity Commuter Pro specs: 9.2kg, Shimano 105, hydraulic disc",
         "conv-marcus-mem-001", 30, ["velocity-pro", "specs"]),
        ("Frame clearance 35mm, fender mounts confirmed, color options",
         "conv-marcus-mem-002", 25, ["specs", "fenders", "customization"]),
        ("Purchased Velocity Matte Black 56cm + SKS fenders, total $1844",
         "conv-marcus-mem-003", 18, ["purchase", "sizing"]),
        ("Front derailleur cable tension issue, self-repair instructions provided",
         "conv-marcus-mem-004", 10, ["maintenance", "derailleur"]),
        ("Partner bike shop near 94110: Bay City Bikes, Pedal Works",
         "conv-marcus-mem-004", 10, ["service", "location"]),
        ("ABUS Bordo 6000 lock purchase, frame-mount preference noted",
         "conv-marcus-mem-005", 3, ["accessory", "lock", "purchase"]),
    ]

    for i, (text, conv_id, days_ago, topics) in enumerate(marcus_chunks):
        vectors.append({
            "id": f"vec-marcus-{i+1:03d}",
            "tenant_id": TENANT_ID,
            "customer_id": "cust-marcus-002",
            "conversation_id": conv_id,
            "chunk_text": text,
            "chunk_index": i,
            "embedding": mock_embedding,
            "language": "en",
            "topics": topics,
            "created_at": (NOW - timedelta(days=days_ago)).isoformat(),
            "conversation_date": (NOW - timedelta(days=days_ago)).isoformat(),
        })

    return vectors


def build_pattern_docs() -> list[dict]:
    """Generate pattern extraction records (Layer 3) for Marcus."""
    patterns = []
    for i, p in enumerate(MARCUS_PATTERNS):
        patterns.append({
            "id": f"{TENANT_ID}:cust-marcus-002:pattern-{i+1:03d}",
            "tenant_id": TENANT_ID,
            "customer_id": "cust-marcus-002",
            "pattern_type": p["pattern_type"],
            "pattern_key": p["pattern_key"],
            "value": p["value"],
            "confidence": p["confidence"],
            "last_seen_at": (NOW - timedelta(days=3)).isoformat(),
            "last_reinforced_at": (NOW - timedelta(days=3)).isoformat(),
            "reinforcement_count": p["reinforcement_count"],
            "created_at": (NOW - timedelta(days=30)).isoformat(),
        })
    return patterns


def build_memory_conversation_docs() -> list[dict]:
    """Generate conversation docs for multi-session personas."""
    docs = []
    all_sessions = [
        ("cust-sarah-001", "Sarah Chen", SARAH_SESSIONS),
        ("cust-marcus-002", "Marcus Rivera", MARCUS_SESSIONS),
    ]

    for customer_id, customer_name, sessions in all_sessions:
        for session in sessions:
            started = NOW - timedelta(days=session["days_ago"])
            msg_list = []
            current_ts = started
            for msg in session["messages"]:
                current_ts += timedelta(seconds=random.randint(15, 90))
                msg_list.append({
                    "role": msg["role"],
                    "content": msg["content"],
                    "timestamp": current_ts.isoformat(),
                    "message_id": str(uuid.uuid4()),
                })

            ended = current_ts + timedelta(seconds=30)
            docs.append({
                "id": session["conv_id"],
                "tenant_id": TENANT_ID,
                "conversation_id": session["conv_id"],
                "status": "ended",
                "customer_id": customer_id,
                "customer_name": customer_name,
                "is_billable": True,
                "is_escalated": False,
                "message_count": len(msg_list),
                "turn_count": len([m for m in msg_list if m["role"] == "customer"]),
                "agents_invoked": [
                    "intent-classifier", "knowledge-retrieval",
                    "response-generator", "critic-supervisor",
                ],
                "model_used": "gpt-4o",
                "critic_passed": True,
                "assigned_to": None,
                "internal_notes": [],
                "messages": msg_list,
                "started_at": started.isoformat(),
                "ended_at": ended.isoformat(),
                "last_activity_at": current_ts.isoformat(),
                "last_message_at": current_ts.isoformat(),
            })

    return docs


def build_usage_counter_doc(total_convs: int) -> dict:
    """Generate usage counter for current billing period."""
    return {
        "id": f"{TENANT_ID}:{BILLING_PERIOD}",
        "tenant_id": TENANT_ID,
        "billing_period": BILLING_PERIOD,
        "total_conversations": total_convs,
        "overage_reported": 0,
        "pack_consumed": 0,
        "tier": "professional",
        "included_allowance": 5000,
        "last_reconciled_at": NOW.isoformat(),
        "stripe_meter_total": 0,
    }


# ---------------------------------------------------------------------------
# Seeding logic
# ---------------------------------------------------------------------------


async def seed(dry_run: bool = True, seed_kb: bool = False) -> None:
    """Insert demo data into Cosmos DB."""

    conversations = build_conversation_docs()
    team_members = build_team_member_docs()
    customer_profiles = build_customer_profile_docs()
    memory_vectors = build_memory_vector_docs()
    patterns = build_pattern_docs()
    memory_conversations = build_memory_conversation_docs()
    all_conversations = conversations + memory_conversations
    usage_counter = build_usage_counter_doc(len(all_conversations))

    print()
    print("=" * 65)
    print("  AGENT RED - DEMO DATA SEEDING")
    print("=" * 65)
    print()
    print(f"  Tenant:           {TENANT_ID}")
    print(f"  Billing period:   {BILLING_PERIOD}")
    print()
    print(f"  Conversations:    {len(all_conversations)}")
    print(f"    - with full transcript: {len(CONVERSATION_TEMPLATES)}")
    print(f"    - memory personas:      {len(memory_conversations)}")
    print(f"    - padding (short):      {len(conversations) - len(CONVERSATION_TEMPLATES)}")
    print()
    print("  Persistent Customer Memory:")
    print(f"    Customer profiles:  {len(customer_profiles)}")
    print(f"    Memory vectors:     {len(memory_vectors)}")
    print(f"    Extracted patterns: {len(patterns)}")
    print()
    print(f"  Team members:     {len(team_members)}")
    print(f"  Usage counter:    1 (total={usage_counter['total_conversations']})")
    print()

    if dry_run:
        print("[DRY RUN] No database writes. Run with --seed to create.")
        print()
        print("Sample conversation IDs:")
        for c in conversations[:5]:
            print(f"  {c['id']}: {c['status']} ({c['message_count']} msgs)")
        print(f"  ... and {len(conversations) - 5} more")
        print()
        print("Memory persona conversations:")
        for c in memory_conversations:
            print(f"  {c['id']}: {c['customer_name']} ({c['message_count']} msgs)")
        print()
        print("Customer profiles:")
        for p in customer_profiles:
            purchases = len(p.get("purchase_history", []))
            print(f"  {p['customer_id']}: {purchases} purchases, consent={p['consent_status']}")
        print()
        print(f"Memory vectors: {len(memory_vectors)} chunks")
        print(f"  Sarah:  {len([v for v in memory_vectors if 'sarah' in v['id']])} chunks")
        print(f"  Marcus: {len([v for v in memory_vectors if 'marcus' in v['id']])} chunks")
        print()
        print(f"Extracted patterns: {len(patterns)} (Marcus, Layer 3)")
        for p in patterns:
            print(f"  {p['pattern_key']}: confidence={p['confidence']}")
        print()
        print("Team members:")
        for m in team_members:
            print(f"  {m['display_name']} ({m['role']}) - {m['email']}")
        print()
        return

    # Initialize Cosmos DB
    from src.multi_tenant.cosmos_client import get_cosmos_manager

    cosmos = get_cosmos_manager()
    await cosmos.initialize()

    # Get containers
    conversations_container = cosmos.get_container("conversations")
    team_container = cosmos.get_container("team_members")
    usage_container = cosmos.get_container("usage")
    profiles_container = cosmos.get_container("customer_profiles")
    vectors_container = cosmos.get_container("memory_vectors")

    # Seed conversations (generic + memory persona sessions)
    print("Seeding conversations...")
    created_convs = 0
    for doc in all_conversations:
        try:
            await conversations_container.upsert_item(doc)
            created_convs += 1
        except Exception as e:
            logger.warning("  Failed conversation %s: %s", doc["id"], e)
    print(f"  [OK] {created_convs}/{len(all_conversations)} conversations seeded")

    # Seed team members
    print("Seeding team members...")
    created_team = 0
    for doc in team_members:
        try:
            await team_container.upsert_item(doc)
            created_team += 1
        except Exception as e:
            logger.warning("  Failed team member %s: %s", doc["id"], e)
    print(f"  [OK] {created_team}/{len(team_members)} team members seeded")

    # Seed customer profiles (Layer 1)
    print("Seeding customer profiles (Layer 1)...")
    created_profiles = 0
    for doc in customer_profiles:
        try:
            await profiles_container.upsert_item(doc)
            created_profiles += 1
        except Exception as e:
            logger.warning("  Failed profile %s: %s", doc["id"], e)
    print(f"  [OK] {created_profiles}/{len(customer_profiles)} profiles seeded")

    # Seed memory vectors (Layer 2)
    print("Seeding memory vectors (Layer 2)...")
    created_vectors = 0
    for doc in memory_vectors:
        try:
            await vectors_container.upsert_item(doc)
            created_vectors += 1
        except Exception as e:
            logger.warning("  Failed vector %s: %s", doc["id"], e)
    print(f"  [OK] {created_vectors}/{len(memory_vectors)} vectors seeded")

    # Seed extracted patterns (Layer 3) — stored in customer_profiles container
    print("Seeding extracted patterns (Layer 3)...")
    created_patterns = 0
    for doc in patterns:
        try:
            await profiles_container.upsert_item(doc)
            created_patterns += 1
        except Exception as e:
            logger.warning("  Failed pattern %s: %s", doc["id"], e)
    print(f"  [OK] {created_patterns}/{len(patterns)} patterns seeded")

    # Seed usage counter
    print("Seeding usage counter...")
    try:
        await usage_container.upsert_item(usage_counter)
        print("  [OK] Usage counter seeded")
    except Exception as e:
        logger.warning("  Failed usage counter: %s", e)

    # Optionally seed knowledge base
    if seed_kb:
        print()
        print("Seeding knowledge base (32 articles)...")
        from scripts.seed_knowledge_base import load_to_cosmos
        await load_to_cosmos(tenant_id=TENANT_ID)

    print()
    print("=" * 65)
    print("  DEMO DATA SEEDING COMPLETE")
    print("=" * 65)
    print()
    print(f"  Conversations:      {created_convs}")
    print(f"  Customer profiles:  {created_profiles}")
    print(f"  Memory vectors:     {created_vectors}")
    print(f"  Extracted patterns: {created_patterns}")
    print(f"  Team members:       {created_team}")
    print(f"  Usage counter:      1")
    if seed_kb:
        print(f"  KB articles:        32")
    print()
    print("  The standalone admin at /admin/standalone/ should now")
    print("  show populated data across all pages, including")
    print("  Persistent Customer Memory data for Sarah and Marcus.")
    print()


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seed demo data for Agent Red admin preview",
    )
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Write demo data to Cosmos DB (omit for dry run)",
    )
    parser.add_argument(
        "--seed-kb",
        action="store_true",
        help="Also seed the knowledge base with 32 Agent Red articles",
    )
    args = parser.parse_args()

    await seed(dry_run=not args.seed, seed_kb=args.seed_kb)


if __name__ == "__main__":
    asyncio.run(main())
