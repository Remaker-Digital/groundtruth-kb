# Integrations Page Content

> **Page Purpose:** Showcase integration capabilities, demonstrate data access depth, drive adoption
> **Target Audience:** Technical evaluators, IT decision-makers, e-commerce operators, developers
> **Primary CTA:** Start Free Trial
> **Secondary CTA:** Request Integration

---

## Meta Information

```yaml
title: "Integrations - Agent Red Customer Experience"
description: "Connect Agent Red to Shopify, Zendesk, Mailchimp, Google Analytics, and more. Native integrations with real-time data sync for AI customer service."
keywords: "Shopify AI integration, Zendesk integration, customer service integrations, e-commerce API, Agent Red"
og_image: "/images/og-integrations.png"
canonical: "https://agentred.io/integrations"
```

---

## Hero Section

### Headline
**Connect Your Entire Stack**

### Subheadline
Native integrations with the tools you already use. Real-time data sync. Zero manual work. Your AI has the context to actually solve problems.

### Integration Logo Cloud
[Shopify] [Zendesk] [Mailchimp] [Google Analytics] [Slack*] [Gorgias*]
*Coming soon

### CTA
**Start Free Trial** → /signup

---

## Featured Integrations Section

### Section Headline
**Native Integrations**

### Section Description
Deep, bi-directional integrations that keep your systems in sync automatically. Not surface-level widgets — real data access that powers accurate, personalized support.

---

## Integration: Shopify

### Header
#### Logo
Shopify logo (large)

#### Status Badge
**Available** — All Plans (included)

#### Setup Time
15 minutes

---

### Overview

#### Headline
**Deep Shopify Integration**

#### Description
Agent Red connects directly to your Shopify store for real-time access to orders, products, customers, and inventory. Your AI always has the latest information to help customers accurately.

#### Key Benefits
- **Real-time order lookup** — Instant access to order status, tracking, and history
- **Product information** — Current pricing, availability, descriptions, and images
- **Customer profiles** — Purchase history, preferences, and account details
- **Inventory accuracy** — Live stock levels across all locations

---

### Capabilities

#### Capability 1: Order Management
**What It Does:**
Access complete order information including status, items, shipping, and tracking.

**AI Can:**
- Look up order status by order number or email
- Provide tracking information and estimated delivery
- Show order history for returning customers
- Identify orders with issues (delayed, canceled, etc.)

**Example Conversation:**
> **Customer:** Where's my order #12345?
>
> **AI:** Your order #12345 shipped yesterday via UPS. It's currently in transit and scheduled for delivery tomorrow by 5 PM. Here's your tracking link: [tracking URL]

---

#### Capability 2: Product Search
**What It Does:**
Search your entire product catalog with real-time pricing and availability.

**AI Can:**
- Find products by name, description, or attributes
- Show current prices and compare variants
- Check stock availability across locations
- Recommend alternatives for out-of-stock items

**Example Conversation:**
> **Customer:** Do you have the blue sweater in medium?
>
> **AI:** Yes! The Coastal Blue Merino Sweater is in stock in Medium. It's $89 and ships free. Would you like me to send you a link to add it to your cart?

---

#### Capability 3: Customer Profiles
**What It Does:**
Access customer account information and purchase history for personalized service.

**AI Can:**
- Greet returning customers by name
- Reference past purchases in recommendations
- Access saved addresses and preferences
- Identify VIP or high-value customers

**Memory Integration:** Customer profile data from Shopify feeds into Agent Red's Persistent Customer Memory. Purchase history, preferences, and past interactions enrich every future conversation automatically — building a deeper understanding of each customer over time.

**Example Conversation:**
> **Customer:** I bought a jacket from you last month but can't remember the name.
>
> **AI:** Hi Sarah! I found your recent order. You purchased the Alpine Waterproof Jacket in Forest Green on January 15th. Would you like to order another one or find matching items?

---

#### Capability 4: Inventory Check
**What It Does:**
Real-time inventory levels across all locations and variants.

**AI Can:**
- Confirm product availability before purchase
- Suggest alternatives when items are out of stock
- Estimate restock dates when available
- Check inventory at specific locations

---

### Setup Guide

#### Prerequisites
- Shopify store (any plan)
- Store owner or staff account with admin access

#### Steps
1. Log in to your Agent Red dashboard
2. Navigate to Settings → Integrations
3. Click "Connect Shopify"
4. Authorize Agent Red in Shopify
5. Select data to sync (recommended: all)
6. Test the connection

#### Required Permissions
| Permission | Purpose |
|------------|---------|
| `read_orders` | Access order information for customer queries |
| `read_products` | Search product catalog and pricing |
| `read_customers` | Access customer profiles for personalization |
| `read_inventory` | Check stock availability |

#### Data Sync Frequency
| Data Type | Sync Frequency |
|-----------|----------------|
| Orders | Real-time (webhook) |
| Products | Hourly |
| Customers | Real-time (webhook) |
| Inventory | Every 15 minutes |

---

### CTA
**Connect Shopify Now** → /signup

---

## Integration: Zendesk

### Header
#### Logo
Zendesk logo (large)

#### Status Badge
**Available** — Professional & Enterprise (included)

#### Setup Time
30 minutes

---

### Overview

#### Headline
**Seamless Escalation to Zendesk**

#### Description
When conversations need human attention, Agent Red creates Zendesk tickets automatically with full conversation context. Your agents get a head start. Customers never repeat themselves.

#### Key Benefits
- **Automatic ticket creation** — Escalated conversations become tickets instantly
- **Full context transfer** — Complete conversation history attached
- **Smart routing** — Assign to the right team based on issue type
- **Bi-directional sync** — Ticket updates reflect in Agent Red

---

### Capabilities

#### Capability 1: Automatic Escalation
**What It Does:**
Creates Zendesk tickets when AI determines human intervention is needed.

**Triggers Include:**
- Low AI confidence score
- Negative customer sentiment
- Explicit request for human agent
- Complex multi-part issues
- VIP customer flagged
- Compliance-sensitive topics

**Ticket Includes:**
- Full conversation transcript
- Customer information
- Order/product context
- AI's analysis of the issue
- Suggested resolution

---

#### Capability 2: Priority Assignment
**What It Does:**
Automatically assigns ticket priority based on issue and customer value.

**Priority Logic:**
| Factor | Impact |
|--------|--------|
| Customer lifetime value | High value = higher priority |
| Sentiment score | Negative = higher priority |
| Issue type | Order issues = higher priority |
| Wait time | Longer wait = escalated priority |

---

#### Capability 3: Team Routing
**What It Does:**
Routes tickets to the appropriate team or agent based on issue category.

**Routing Options:**
- Route by intent category (billing, shipping, technical)
- Route by customer segment (VIP, international)
- Route by language (English, French, Spanish)
- Custom routing rules (Enterprise)

---

#### Capability 4: Status Sync
**What It Does:**
Keeps Agent Red and Zendesk in sync as tickets progress.

**Synced Data:**
- Ticket status changes
- Agent responses
- Resolution notes
- Customer satisfaction scores

---

### Setup Guide

#### Prerequisites
- Zendesk account (any plan)
- Admin access to Zendesk

#### Steps
1. Log in to your Agent Red dashboard
2. Navigate to Settings → Integrations
3. Click "Connect Zendesk"
4. Enter your Zendesk subdomain
5. Authorize Agent Red in Zendesk
6. Configure routing rules
7. Test with a sample escalation

#### Required Permissions
| Permission | Purpose |
|------------|---------|
| `tickets:write` | Create and update tickets |
| `users:read` | Access agent information for routing |
| `organizations:read` | Access customer organization data |

---

### CTA
**Connect Zendesk** → /signup?plan=professional

---

## Integration: Mailchimp

### Header
#### Logo
Mailchimp logo (large)

#### Status Badge
**Available** — Add-on ($49/month, Professional & Enterprise)

#### Setup Time
20 minutes

---

### Overview

#### Headline
**Marketing Intelligence for Better Support**

#### Description
Enrich customer interactions with marketing data. Know which campaigns they've engaged with, which segments they belong to, and tailor support accordingly.

#### Key Benefits
- **Segment awareness** — Know which customer segments apply
- **Campaign context** — See which emails they've received
- **Subscription management** — Check and update preferences
- **Personalized service** — Tailor responses to marketing engagement

---

### Capabilities

#### Capability 1: Customer Segments
**What It Does:**
Shows which Mailchimp segments/tags apply to each customer.

**AI Can:**
- Identify VIP customers from marketing data
- Recognize first-time vs. repeat buyers
- Understand customer interests from segment membership
- Personalize responses based on segment

---

#### Capability 2: Campaign History
**What It Does:**
Shows which email campaigns the customer has received and engaged with.

**AI Can:**
- Reference recent promotions customer received
- Understand context when customers mention "that email"
- Confirm promotional offers and terms
- Track email-to-support journey

---

#### Capability 3: Subscription Status
**What It Does:**
Check and update email subscription preferences.

**AI Can:**
- Confirm subscription status
- Process unsubscribe requests
- Update preferences (frequency, topics)
- Explain what emails customer will receive

---

### Setup Guide

#### Prerequisites
- Mailchimp account (any plan)
- API key with appropriate permissions

#### Steps
1. Log in to your Agent Red dashboard
2. Navigate to Settings → Integrations
3. Click "Connect Mailchimp"
4. Enter your API key
5. Select audiences to sync
6. Test the connection

---

### CTA
**Add Mailchimp Integration** → /pricing

---

## Integration: Google Analytics

### Header
#### Logo
Google Analytics logo (large)

#### Status Badge
**Available** — Add-on ($49/month, Professional & Enterprise)

#### Setup Time
15 minutes

---

### Overview

#### Headline
**Unified Customer Analytics**

#### Description
Track customer service interactions alongside your existing analytics. Understand how support impacts conversion and customer lifetime value.

#### Key Benefits
- **Event tracking** — Conversation events flow into GA4
- **Conversion attribution** — Connect support to sales
- **Behavior insights** — Understand support impact on customer journey
- **Custom dimensions** — Enrich analytics with support data

---

### Capabilities

#### Capability 1: Event Tracking
**What It Does:**
Sends conversation events to Google Analytics 4.

**Events Tracked:**
| Event | Parameters |
|-------|------------|
| `conversation_started` | source, intent |
| `conversation_ended` | resolution, duration, satisfaction |
| `message_sent` | intent, confidence |
| `escalation_created` | reason, priority |

---

#### Capability 2: Conversion Attribution
**What It Does:**
Tracks how support interactions influence purchases.

**Metrics Available:**
- Support-influenced conversions
- Time from support to purchase
- Support impact on cart abandonment
- Revenue attributed to support

---

#### Capability 3: Custom Dimensions
**What It Does:**
Adds customer service data as custom dimensions for deeper analysis.

**Available Dimensions:**
- Customer satisfaction score
- Support issue category
- Resolution type (AI vs. human)
- Response time

---

### Setup Guide

#### Prerequisites
- Google Analytics 4 property
- GA4 Measurement ID
- API access enabled

#### Steps
1. Log in to your Agent Red dashboard
2. Navigate to Settings → Integrations
3. Click "Connect Google Analytics"
4. Enter your GA4 Measurement ID
5. Configure event tracking options
6. Verify events in GA4 DebugView

---

### CTA
**Add Google Analytics Integration** → /pricing

---

## Coming Soon Section

### Section Headline
**Coming Soon**

### Section Description
We're always adding new integrations. Here's what's next on our roadmap.

---

### Coming Soon: Slack

#### Logo
Slack logo

#### Expected
Q2 2026

#### Description
Real-time notifications, escalation alerts, and team collaboration directly in Slack.

#### Planned Features
- Escalation notifications to channels
- Quick actions from Slack
- Team @mentions for complex issues
- Daily digest summaries

---

### Coming Soon: Gorgias

#### Logo
Gorgias logo

#### Expected
Q2 2026

#### Description
Alternative helpdesk integration for teams already using Gorgias.

#### Planned Features
- Automatic ticket creation
- Full context transfer
- Macro suggestions
- Performance sync

---

### Coming Soon: Klaviyo

#### Logo
Klaviyo logo

#### Expected
Q3 2026

#### Description
E-commerce marketing automation integration for personalized support.

#### Planned Features
- Flow trigger data
- Segment membership
- Campaign engagement history
- Subscription management

---

### Coming Soon: Salesforce

#### Logo
Salesforce logo

#### Expected
Q3 2026

#### Description
Enterprise CRM integration for larger organizations.

#### Planned Features
- Contact and account sync
- Case creation
- Custom object access
- Salesforce Flow triggers

---

### Request an Integration
Don't see what you need? Let us know.

**Request Integration** → /contact?subject=integration-request

---

## API Section

### Section Headline
**Build Custom Integrations**

### Section Description
Connect Agent Red to any system with our REST API. Full documentation, official SDKs, and webhook support.

---

### API Overview

#### Base URL
`https://api.agentred.io/v1`

#### Authentication
Bearer token (JWT)

#### Rate Limits
| Plan | Requests/minute | Burst |
|------|-----------------|-------|
| Professional (read-only) | 300 | 500 |
| Enterprise (full access) | 1,000 | 2,000 |

Note: API access is available on Professional (read-only) and Enterprise (full read + write) plans.

---

### Key Endpoints

#### Conversations
```
POST   /conversations              Create new conversation
GET    /conversations/{id}         Get conversation details
POST   /conversations/{id}/messages  Send message
GET    /conversations/{id}/messages  Get message history
```

#### Knowledge Base
```
GET    /knowledge/search           Search knowledge base
POST   /knowledge/articles         Create article
PUT    /knowledge/articles/{id}    Update article
DELETE /knowledge/articles/{id}    Delete article
```

#### Analytics
```
GET    /analytics/summary          Get analytics summary
GET    /analytics/conversations    Get conversation metrics
GET    /analytics/intents          Get intent distribution
```

#### Webhooks
```
POST   /webhooks                   Register webhook
GET    /webhooks                   List webhooks
DELETE /webhooks/{id}              Delete webhook
```

---

### Webhooks

#### Available Events
| Event | Description |
|-------|-------------|
| `conversation.started` | New conversation initiated |
| `conversation.ended` | Conversation resolved |
| `message.received` | Customer message received |
| `message.sent` | AI response sent |
| `escalation.created` | Issue escalated to human |
| `feedback.received` | Customer provided feedback |

#### Webhook Payload Example
```json
{
  "event": "conversation.ended",
  "timestamp": "2026-01-29T14:30:00Z",
  "data": {
    "conversation_id": "conv_abc123",
    "customer_id": "cust_xyz789",
    "resolution": "automated",
    "duration_seconds": 45,
    "satisfaction_score": 5,
    "intent": "order_status"
  }
}
```

---

### SDKs

#### Official SDKs
| Language | Package | Install |
|----------|---------|---------|
| Python | `agentred-sdk` | `pip install agentred-sdk` |
| Node.js | `@agentred/sdk` | `npm install @agentred/sdk` |
| PHP | `agentred/sdk` | `composer require agentred/sdk` |

#### Python Example
```python
from agentred import AgentRedClient

client = AgentRedClient(api_key="your_api_key")

# Start a conversation
conversation = client.conversations.create(
    customer_email="customer@example.com",
    initial_message="Where's my order?"
)

# Get the AI response
response = conversation.messages[-1]
print(response.content)
```

---

### API Documentation
Full API documentation with examples and interactive playground.

**View API Docs** → /docs/api

---

## Integration Support Section

### Section Headline
**Need Help Integrating?**

### Support Options

#### Self-Service
- Comprehensive documentation with screenshots
- Step-by-step setup guides
- Video tutorials
- Community forum

#### Professional Support
- Dedicated integration engineering (Custom Integration add-on, Enterprise)
- Custom connector development
- Migration assistance from other platforms
- Ongoing optimization and maintenance

#### Memory Note
All integration data feeds into Agent Red's Persistent Customer Memory, building richer customer profiles over time. The more integrations you connect, the more context Agent Red has to personalize every interaction.

---

## Final CTA Section

### Headline
**Ready to Connect Your Stack?**

### Description
Start your free trial and connect your first integration in minutes. Shopify setup takes 15 minutes.

### Primary CTA
**Start Free Trial** → /signup

### Secondary CTA
**Request Custom Integration** → /contact

---

## Technical Notes

### SEO Requirements
- Semantic HTML5 structure
- Schema markup: SoftwareApplication, ItemList (integrations)
- Individual integration sections linkable via anchors
- Alt text for all logos and screenshots

### Analytics Events

| Event | Trigger | Parameters |
|-------|---------|------------|
| `page_view` | Page load | page_name |
| `integration_view` | Integration section enters viewport | integration_name |
| `integration_cta_click` | Integration CTA clicked | integration_name, cta_type |
| `api_docs_click` | API docs link clicked | — |
| `coming_soon_click` | Coming soon integration clicked | integration_name |
| `request_integration` | Request integration CTA clicked | — |

---

*Content Version: 2.0.0*
*Last Updated: 2026-01-29*
*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
