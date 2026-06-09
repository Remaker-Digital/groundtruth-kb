"""
Create Agent Red marketing pages on the Shopify storefront.

Creates 5 content pages (About, Features, Pricing, Integrations, Contact)
adapted from the website/content/ markdown source files. These pages use
Shopify's page creation API and appear in the storefront navigation.

Note: The Homepage content is not created as a Shopify "page" — it is
configured through the theme editor (Online Store > Themes > Customize).
Homepage content is provided here as HTML for manual insertion into
theme sections.

Usage:
    # Preview pages (no API calls):
    python scripts/create_shopify_pages.py

    # Create pages on Shopify:
    python scripts/create_shopify_pages.py --create

Requires in .env.local:
    SHOPIFY_STORE_URL=blanco-9939.myshopify.com
    SHOPIFY_ACCESS_TOKEN=shpat_...

The access token must have the 'write_content' scope.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Load .env.local (shared loader — R7 refactoring)
from scripts._env import load_env_local

load_env_local()

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Page definitions
# ---------------------------------------------------------------------------

PAGES = [
    {
        "title": "About Agent Red",
        "handle": "about",
        "body_html": (
            '<div class="agent-red-page about-page">'
            '<div class="hero-section">'
            "<h1>Great Customer Service Shouldn't Require a Massive Team</h1>"
            "<p>Agent Red helps e-commerce businesses deliver exceptional support at scale "
            "&mdash; without scaling costs. Built on open-source AI, priced transparently, "
            "and designed to earn your trust every month.</p>"
            "</div>"
            '<div class="section">'
            "<h2>Our Mission</h2>"
            "<blockquote><p><strong>To make world-class customer service accessible to every "
            "e-commerce business &mdash; regardless of team size or budget.</strong></p></blockquote>"
            "<p>Most support automation tools are built for enterprises with enterprise budgets. "
            "The businesses that need automation most &mdash; growing e-commerce stores stretched "
            "thin on support &mdash; are priced out or stuck with basic chatbots that frustrate customers.</p>"
            "<p>Agent Red changes that. We built a six-agent AI platform on proven open-source technology "
            "and priced it so that a store doing a few hundred conversations a month can afford the same "
            "AI capability that enterprise retailers use.</p>"
            "</div>"
            '<div class="section">'
            "<h2>How We Got Here</h2>"
            "<h3>The Problem</h3>"
            "<p>E-commerce support doesn't scale linearly. Every new customer adds tickets, "
            "every promotion creates spikes, and every unanswered question is revenue at risk. "
            "The standard options are: hire more agents (expensive), deploy a basic chatbot "
            "(frustrating), or buy an enterprise platform (overkill).</p>"
            "<p>We saw a gap: there was no AI customer service platform that was genuinely powerful, "
            "honestly priced, and built for the e-commerce mid-market.</p>"
            "<h3>The Foundation</h3>"
            "<p>Instead of building from scratch, we started with a public, open-source multi-agent "
            "AI platform &mdash; the AGNTCY project. Six specialized AI agents working together: "
            "one classifies intent, one retrieves knowledge, one generates responses, one validates "
            "quality, one handles escalation, and one tracks analytics.</p>"
            "<p>The evaluation data is real: 98% intent accuracy, sub-2-second response times, "
            "100% content safety, 3,071 requests per second throughput. Not marketing claims &mdash; "
            "measured results from production workloads.</p>"
            "<h3>The Commercial Product</h3>"
            "<p>Agent Red is the commercial layer on top of that open-source foundation. We added "
            "multi-tenant infrastructure, usage-based billing, enterprise integrations, white-label "
            "capability, Persistent Customer Memory, and professional support &mdash; the things "
            "a business needs to run this in production with confidence.</p>"
            "</div>"
            '<div class="section">'
            "<h2>What We Believe</h2>"
            "<ul>"
            "<li><strong>Transparency First</strong> &mdash; Every price is published. Every performance "
            "metric is verified. The AI foundation is open-source.</li>"
            "<li><strong>Earn It Monthly</strong> &mdash; Month-to-month plans, no lock-in, 30-day "
            "money-back guarantee. The right response to customer retention is building a better product.</li>"
            "<li><strong>Build on Proven Technology</strong> &mdash; We don't chase hype. Agent Red "
            "is built on evaluated, production-tested AI infrastructure.</li>"
            "<li><strong>Empower the Ecosystem</strong> &mdash; Open-source foundation for technical users. "
            "Transparent pricing for affiliates and promoters.</li>"
            "</ul>"
            "</div>"
            '<div class="section">'
            "<h2>Verified Performance</h2>"
            "<table>"
            "<thead><tr><th>Metric</th><th>Value</th><th>How It Was Measured</th></tr></thead>"
            "<tbody>"
            "<tr><td>Intent Accuracy</td><td><strong>98%</strong></td><td>Across 17 intent categories</td></tr>"
            "<tr><td>Response Time (P95)</td><td><strong>&lt; 2 seconds</strong></td><td>Under production load</td></tr>"
            "<tr><td>Throughput</td><td><strong>3,071 req/s</strong></td><td>100 concurrent users</td></tr>"
            "<tr><td>Content Safety</td><td><strong>100% blocked</strong></td><td>Zero false negatives</td></tr>"
            "<tr><td>Automation Rate</td><td><strong>70%+</strong></td><td>Without human intervention</td></tr>"
            "<tr><td>Uptime SLA</td><td><strong>99.95%</strong></td><td>Azure infrastructure</td></tr>"
            "</tbody></table>"
            "</div>"
            '<div class="section">'
            "<h2>The Company</h2>"
            "<p>Agent Red is a product of <strong>Remaker Digital</strong>, a DBA of VanDusen &amp; Palmeter, "
            "LLC &mdash; a Delaware limited liability company.</p>"
            "<p>Agent Red is bootstrapped. No venture capital, no outside investors, no pressure to "
            "prioritize growth over product quality.</p>"
            "<p>Production infrastructure runs on Microsoft Azure (East US 2 region). All customer data "
            "is stored in the United States. GDPR and CCPA compliant.</p>"
            "</div>"
            '<div class="section">'
            "<h2>Get in Touch</h2>"
            "<ul>"
            "<li><strong>Sales:</strong> sales@agentred.io</li>"
            "<li><strong>Support:</strong> support@agentred.io</li>"
            "<li><strong>Partnerships:</strong> partners@agentred.io</li>"
            "<li><strong>General:</strong> hello@agentred.io</li>"
            "</ul>"
            "</div>"
            "</div>"
        ),
    },
    {
        "title": "Features",
        "handle": "features",
        "body_html": (
            '<div class="agent-red-page features-page">'
            '<div class="hero-section">'
            "<h1>Six AI Agents. One Exceptional Support Experience.</h1>"
            "<p>Every feature is built to do one thing: help you serve customers better "
            "while spending less. No complexity, no compromises.</p>"
            "</div>"
            '<div class="section">'
            "<h2>Six Specialized AI Agents</h2>"
            "<p>Simple chatbots use one model for everything. Agent Red deploys six "
            "purpose-built agents that each excel at a specific job.</p>"
            "<h3>1. Intent Classification</h3>"
            "<p><strong>Understand Every Customer Instantly</strong></p>"
            "<p>Analyzes incoming messages and identifies what customers need in milliseconds. "
            "17 intent categories, 98% accuracy, confidence scoring, multi-language support.</p>"
            "<h3>2. Knowledge Retrieval</h3>"
            "<p><strong>Find the Right Answer, Every Time</strong></p>"
            "<p>Searches your product catalog, FAQs, policies, and order data using semantic search. "
            "Real-time Shopify sync. 100% retrieval accuracy.</p>"
            "<h3>3. Response Generation</h3>"
            "<p><strong>Natural Responses That Sound Like You</strong></p>"
            "<p>Crafts personalized, natural responses in your brand voice. Powered by GPT-4o. "
            "Memory-informed &mdash; draws from the customer's full interaction history.</p>"
            "<h3>4. Critic/Supervisor</h3>"
            "<p><strong>Quality Control for Every Response</strong></p>"
            "<p>Reviews every response before it reaches your customer. Blocks 100% of inappropriate "
            "content with zero false negatives. Checks accuracy, safety, and brand alignment.</p>"
            "<h3>5. Escalation Detection</h3>"
            "<p><strong>Smart Handoffs to Your Team</strong></p>"
            "<p>Recognizes when a human is needed &mdash; emotional situations, complex issues, VIP "
            "customers. Hands off with full context. 100% precision and recall.</p>"
            "<h3>6. Analytics</h3>"
            "<p><strong>Insights That Drive Improvement</strong></p>"
            "<p>Tracks what customers ask, how issues resolve, and where to improve. Real-time "
            "dashboard with trend analysis and custom reports.</p>"
            "</div>"
            '<div class="section">'
            "<h2>Integrations</h2>"
            "<ul>"
            "<li><strong>Shopify</strong> (All tiers) &mdash; Orders, products, customers, inventory. "
            "15-minute setup.</li>"
            "<li><strong>Zendesk</strong> (Professional+) &mdash; Seamless escalation with full context.</li>"
            "<li><strong>Mailchimp</strong> (Add-on) &mdash; Marketing data for personalized support.</li>"
            "<li><strong>Google Analytics</strong> (Add-on) &mdash; Track support impact on conversions.</li>"
            "</ul>"
            "</div>"
            '<div class="section">'
            "<h2>Persistent Customer Memory</h2>"
            "<p>Every conversation builds on the last. Agent Red maintains a persistent memory for each "
            "customer. No competitor offers this level of per-customer memory.</p>"
            "<table>"
            "<thead><tr><th>Layer</th><th>What It Does</th><th>Available On</th></tr></thead>"
            "<tbody>"
            "<tr><td><strong>Customer Context</strong></td>"
            "<td>Structured profile injected into every interaction</td>"
            "<td>All tiers</td></tr>"
            "<tr><td><strong>Conversation Memory</strong></td>"
            "<td>Semantic search across full interaction history</td>"
            "<td>All tiers</td></tr>"
            "<tr><td><strong>Cross-Session Learning</strong></td>"
            "<td>Extracts patterns, preferences, communication style</td>"
            "<td>Professional+</td></tr>"
            "<tr><td><strong>Dedicated Model Training</strong></td>"
            "<td>Per-customer fine-tuned AI model (1,000+ interactions)</td>"
            "<td>Enterprise add-on</td></tr>"
            "</tbody></table>"
            "</div>"
            '<div class="section">'
            "<h2>Customization</h2>"
            "<ul>"
            "<li><strong>Brand Voice</strong> &mdash; Configure tone, formality, personality, and greeting style.</li>"
            "<li><strong>Knowledge Base</strong> &mdash; Upload FAQs, policies, guides. Supports MD, TXT, PDF, CSV.</li>"
            "<li><strong>Escalation Rules</strong> &mdash; Define confidence thresholds, keywords, VIP triggers.</li>"
            "<li><strong>White-Label</strong> (Enterprise) &mdash; Complete branding removal, custom domain, CSS theming.</li>"
            "</ul>"
            "</div>"
            '<div class="section">'
            "<h2>Security</h2>"
            "<ul>"
            "<li>TLS 1.3 + AES-256 encryption</li>"
            "<li>PII tokenization for all AI processing</li>"
            "<li>GDPR and CCPA compliant</li>"
            "<li>SOC 2 Type 2 in progress (Q3 2026)</li>"
            "<li>Role-based access control + audit logging</li>"
            "</ul>"
            "</div>"
            "</div>"
        ),
    },
    {
        "title": "Pricing",
        "handle": "pricing",
        "body_html": (
            '<div class="agent-red-page pricing-page">'
            '<div class="hero-section">'
            "<h1>Transparent Pricing. Every Cost Visible.</h1>"
            "<p>Platform fee + AI usage. You see exactly what you pay for &mdash; the platform "
            "that runs your support, and the AI conversations that serve your customers.</p>"
            "</div>"
            '<div class="section">'
            "<h2>How Pricing Works</h2>"
            "<p><strong>Component 1: Platform Fee</strong> &mdash; Your monthly plan covers infrastructure, "
            "integrations, support, and features.</p>"
            "<p><strong>Component 2: AI Conversations</strong> &mdash; Every plan includes a monthly "
            "allowance. Need more? Pay-as-you-go overage or pre-purchase packs at a discount.</p>"
            "<p>Our AI costs less than $0.01 per conversation to run &mdash; and we pass that efficiency to you.</p>"
            "</div>"
            '<div class="section pricing-cards">'
            "<h2>Plans</h2>"
            '<div class="pricing-card">'
            "<h3>Starter &mdash; $149/month</h3>"
            "<p><em>$124/month billed annually ($1,490/year &mdash; save $298)</em></p>"
            "<ul>"
            "<li><strong>1,000 AI conversations/month</strong></li>"
            "<li>All 6 AI agents</li>"
            "<li>Shopify integration</li>"
            "<li>English language</li>"
            "<li>Knowledge base (50 articles + Shopify sync)</li>"
            "<li>Real-time dashboard</li>"
            "<li>Email support (48hr response)</li>"
            "<li>99.5% uptime SLA</li>"
            "</ul>"
            "<p>Overage: $0.04/conversation</p>"
            "</div>"
            '<div class="pricing-card popular">'
            "<h3>Professional &mdash; $399/month</h3>"
            "<p><strong>MOST POPULAR</strong></p>"
            "<p><em>$332/month billed annually ($3,990/year &mdash; save $798)</em></p>"
            "<ul>"
            "<li><strong>5,000 AI conversations/month</strong></li>"
            "<li>All 6 AI agents</li>"
            "<li>Shopify + Zendesk integrations</li>"
            "<li>English + 1 additional language</li>"
            "<li>Knowledge base (500 articles + Shopify sync)</li>"
            "<li>Persistent Customer Memory (Layers 1-3)</li>"
            "<li>Full analytics with data export</li>"
            "<li>Read-only API + audit logging</li>"
            "<li>Chat + email support (24hr response)</li>"
            "<li>99.9% uptime SLA</li>"
            "</ul>"
            "<p>Overage: $0.025/conversation</p>"
            "</div>"
            '<div class="pricing-card">'
            "<h3>Enterprise &mdash; $999/month</h3>"
            "<p><em>$832/month billed annually ($9,990/year &mdash; save $1,998)</em></p>"
            "<ul>"
            "<li><strong>20,000 AI conversations/month</strong></li>"
            "<li>All 6 AI agents</li>"
            "<li>All integrations + full API access</li>"
            "<li>All supported languages</li>"
            "<li>Unlimited knowledge base</li>"
            "<li>Persistent Customer Memory (All 4 Layers)</li>"
            "<li>Custom reports + SSO</li>"
            "<li>Dedicated Customer Success Manager</li>"
            "<li>4hr support response + Slack channel</li>"
            "<li>99.95% uptime SLA</li>"
            "</ul>"
            "<p>Overage: $0.015/conversation</p>"
            "</div>"
            "</div>"
            '<div class="section">'
            "<h2>Conversation Packs (Pre-Purchase &amp; Save)</h2>"
            "<p>Pre-purchase conversation blocks at a discount. Valid for 90 days. Available on all tiers.</p>"
            "<table>"
            "<thead><tr><th>Pack</th><th>Price</th><th>Effective Rate</th></tr></thead>"
            "<tbody>"
            "<tr><td>1,000 conversations</td><td>$29</td><td>$0.029/conv</td></tr>"
            "<tr><td>5,000 conversations</td><td>$99</td><td>$0.020/conv</td></tr>"
            "<tr><td>20,000 conversations</td><td>$249</td><td>$0.012/conv</td></tr>"
            "</tbody></table>"
            "</div>"
            '<div class="section">'
            "<h2>Add-On Modules</h2>"
            "<table>"
            "<thead><tr><th>Module</th><th>Monthly</th><th>Available On</th></tr></thead>"
            "<tbody>"
            "<tr><td>Multi-Language Pack</td><td>$99</td><td>All tiers</td></tr>"
            "<tr><td>Advanced Analytics</td><td>$149</td><td>Professional, Enterprise</td></tr>"
            "<tr><td>White-Label Package</td><td>$399</td><td>Enterprise only</td></tr>"
            "<tr><td>Dedicated Model Training</td><td>$299</td><td>Enterprise only</td></tr>"
            "<tr><td>Priority Support Upgrade</td><td>$99</td><td>Starter, Professional</td></tr>"
            "<tr><td>Custom Integration Dev</td><td>$299</td><td>Enterprise only</td></tr>"
            "</tbody></table>"
            "</div>"
            '<div class="section">'
            "<h2>Special Programs</h2>"
            "<ul>"
            "<li><strong>Nonprofits &amp; Education:</strong> 25% off all plans (verified via TechSoup)</li>"
            "<li><strong>Startups:</strong> 50% off for first 12 months (recognized accelerator programs)</li>"
            "<li><strong>Agency Partners:</strong> 20% off for clients + recurring referral commission</li>"
            "</ul>"
            "</div>"
            '<div class="section">'
            "<h2>Pricing FAQ</h2>"
            "<h3>What counts as an AI conversation?</h3>"
            "<p>A complete customer interaction resolved by Agent Red without human intervention. "
            "Conversations that escalate to your human team are <strong>not counted</strong>.</p>"
            "<h3>What happens when I exceed my included conversations?</h3>"
            "<p>Agent Red notifies you at 80% and 100% of your allowance. Beyond that, you pay the "
            "overage rate for your tier, or pre-purchase conversation packs at a discount.</p>"
            "<h3>Can I change plans?</h3>"
            "<p>Yes. Upgrade instantly (prorated). Downgrade at end of billing cycle. "
            "No penalties, no lock-in.</p>"
            "<h3>Is there a free trial?</h3>"
            "<p>Yes. 14 days free with full Professional features. No credit card required.</p>"
            "<h3>Do you offer refunds?</h3>"
            "<p>30-day money-back guarantee on all plans. No questions asked.</p>"
            "</div>"
            "</div>"
        ),
    },
    {
        "title": "Integrations",
        "handle": "integrations",
        "body_html": (
            '<div class="agent-red-page integrations-page">'
            '<div class="hero-section">'
            "<h1>Connects to Your Entire Stack</h1>"
            "<p>Agent Red integrates natively with the tools you already use. Real-time data sync "
            "means your AI always has the latest information.</p>"
            "</div>"
            '<div class="section">'
            "<h2>Shopify (All Tiers)</h2>"
            "<p><strong>Native Shopify Integration &mdash; 15-minute setup</strong></p>"
            "<p>Deep, real-time integration with your Shopify store. Agent Red automatically "
            "accesses orders, products, customers, and inventory.</p>"
            "<ul>"
            "<li>Real-time order status, tracking, and history</li>"
            "<li>Product catalog search with pricing and availability</li>"
            "<li>Customer profiles with purchase history</li>"
            "<li>Inventory availability checks</li>"
            "</ul>"
            "</div>"
            '<div class="section">'
            "<h2>Zendesk (Professional+)</h2>"
            "<p><strong>Seamless Escalation &mdash; 30-minute setup</strong></p>"
            "<p>When issues need human attention, Agent Red creates Zendesk tickets with full "
            "conversation context. Your agents get a head start.</p>"
            "<ul>"
            "<li>Automatic ticket creation on escalation</li>"
            "<li>Full conversation history attached</li>"
            "<li>Smart priority assignment</li>"
            "<li>Agent routing by issue type</li>"
            "</ul>"
            "</div>"
            '<div class="section">'
            "<h2>Mailchimp (Add-on, $49/mo)</h2>"
            "<p><strong>Marketing Intelligence &mdash; 20-minute setup</strong></p>"
            "<p>Access customer marketing data for personalized support. Know which campaigns "
            "they've engaged with and their subscription preferences.</p>"
            "</div>"
            '<div class="section">'
            "<h2>Google Analytics (Add-on, $49/mo)</h2>"
            "<p><strong>Unified Analytics &mdash; 15-minute setup</strong></p>"
            "<p>Track customer service interactions alongside your other analytics. "
            "GA4 event tracking, conversion attribution, and custom dimensions.</p>"
            "</div>"
            '<div class="section">'
            "<h2>Coming Soon</h2>"
            "<ul>"
            "<li><strong>Slack</strong> &mdash; Real-time notifications and team collaboration</li>"
            "<li><strong>Gorgias</strong> &mdash; Alternative helpdesk for e-commerce</li>"
            "<li><strong>Klaviyo</strong> &mdash; E-commerce marketing automation</li>"
            "<li><strong>Salesforce</strong> &mdash; Enterprise CRM integration</li>"
            "</ul>"
            "<p>Need a specific integration? <a href='/pages/contact'>Contact us</a> &mdash; "
            "we build custom connectors for Enterprise customers.</p>"
            "</div>"
            "</div>"
        ),
    },
    {
        "title": "Contact Us",
        "handle": "contact",
        "body_html": (
            '<div class="agent-red-page contact-page">'
            '<div class="hero-section">'
            "<h1>Let's Talk</h1>"
            "<p>Whether you have a question about pricing, need help with setup, or want to "
            "explore a partnership &mdash; we're here. We respond to every inquiry within 24 hours.</p>"
            "</div>"
            '<div class="section">'
            "<h2>Reach the Right Team</h2>"
            "<h3>Sales</h3>"
            "<p>Pricing questions, demos, custom plans, volume discounts</p>"
            "<p><strong>sales@agentred.io</strong> &mdash; Response within 24 hours</p>"
            "<h3>Support</h3>"
            "<p>Technical issues, setup help, account questions</p>"
            "<p><strong>support@agentred.io</strong> &mdash; Response based on your plan SLA</p>"
            "<h3>Partnerships &amp; Affiliates</h3>"
            "<p>Affiliate program, agency partnerships, technology partnerships</p>"
            "<p><strong>partners@agentred.io</strong> &mdash; Response within 48 hours</p>"
            "<h3>General Inquiries</h3>"
            "<p>Press, careers, feedback, general questions</p>"
            "<p><strong>hello@agentred.io</strong> &mdash; Response within 48 hours</p>"
            "</div>"
            '<div class="section">'
            "<h2>Before You Reach Out</h2>"
            "<ul>"
            '<li><strong>Pricing questions?</strong> <a href="/pages/pricing">View transparent pricing</a></li>'
            '<li><strong>How does it work?</strong> <a href="/pages/features">See all features</a></li>'
            '<li><strong>Integration setup?</strong> <a href="/pages/integrations">Integration guides</a></li>'
            "</ul>"
            "</div>"
            '<div class="section">'
            "<h2>Partner Program</h2>"
            "<p>We work with agencies, Shopify Partners, e-commerce consultancies, and content creators.</p>"
            "<ul>"
            "<li><strong>Client discounts:</strong> 20% off for your clients</li>"
            "<li><strong>Recurring commissions:</strong> Earn on every referral, every month</li>"
            "<li><strong>Co-marketing:</strong> Featured in our partner directory</li>"
            "<li><strong>Priority support:</strong> Dedicated partner channel</li>"
            "<li><strong>Early access:</strong> Preview new features before launch</li>"
            "</ul>"
            "<p>Email <strong>partners@agentred.io</strong> to apply.</p>"
            "</div>"
            "</div>"
        ),
    },
]


# ---------------------------------------------------------------------------
# GraphQL mutation
# ---------------------------------------------------------------------------

CREATE_PAGE_MUTATION = """
mutation pageCreate($page: PageCreateInput!) {
  pageCreate(page: $page) {
    page {
      id
      title
      handle
      createdAt
    }
    userErrors {
      field
      message
    }
  }
}
"""


async def create_pages(dry_run: bool = True) -> None:
    """Create all marketing pages on the Shopify storefront."""

    print()
    print("=" * 65)
    print("  AGENT RED SHOPIFY STOREFRONT PAGES")
    print("=" * 65)
    print(f"  Pages to create: {len(PAGES)}")
    print()

    for i, page in enumerate(PAGES, 1):
        content_len = len(page["body_html"])
        print(f"  {i}. {page['title']}")
        print(f"     Handle: {page['handle']}  |  Content: {content_len:,} chars")

    print()

    if dry_run:
        print("[DRY RUN] No API calls made. Run with --create to create pages.")
        print()
        return

    store_url = os.environ.get("SHOPIFY_STORE_URL", "")
    access_token = os.environ.get("SHOPIFY_ACCESS_TOKEN", "")

    if not store_url or not access_token:
        print("[ERROR] SHOPIFY_STORE_URL and SHOPIFY_ACCESS_TOKEN must be set in .env.local")
        sys.exit(1)

    from src.integrations.shopify_client import ShopifyGraphQLClient

    async with ShopifyGraphQLClient(store_url, access_token) as client:
        created = 0
        errors = 0

        for page in PAGES:
            variables = {
                "page": {
                    "title": page["title"],
                    "handle": page["handle"],
                    "body": page["body_html"],
                }
            }

            try:
                result = await client.execute(CREATE_PAGE_MUTATION, variables)

                if "pageCreate" in result:
                    user_errors = result["pageCreate"].get("userErrors", [])
                    if user_errors:
                        print(f"  [WARN] {page['title']}: {user_errors}")
                        errors += 1
                    else:
                        p = result["pageCreate"]["page"]
                        print(f"  [OK] {p['title']} (handle: {p['handle']})")
                        created += 1
                else:
                    print(f"  [ERROR] {page['title']}: unexpected response: {result}")
                    errors += 1

            except Exception as e:
                print(f"  [ERROR] {page['title']}: {e}")
                errors += 1

    print()
    print(f"  Created: {created}  |  Errors: {errors}")
    print("=" * 65)
    print()


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create Agent Red marketing pages on Shopify storefront",
    )
    parser.add_argument(
        "--create",
        action="store_true",
        help="Create pages via Shopify API (omit for dry run preview)",
    )
    args = parser.parse_args()

    await create_pages(dry_run=not args.create)


if __name__ == "__main__":
    asyncio.run(main())
