# Features Page Content

> **Page Purpose:** Detailed feature showcase to educate prospects and support sales conversations
> **Target Audience:** Technical evaluators, customer service managers, e-commerce leaders
> **Primary CTA:** Start Free Trial
> **Secondary CTA:** Compare Plans

---

## Meta Information

```yaml
title: "Features - Agent Red Customer Experience Platform"
description: "Six specialized AI agents for customer service: intent classification, knowledge retrieval, response generation, content safety, smart escalation, and analytics. Built for e-commerce."
keywords: "AI customer service features, e-commerce support automation, Shopify AI chatbot, multi-agent customer service, Agent Red"
og_image: "/images/og-features.png"
canonical: "https://agentred.io/features"
```

---

## Hero Section

### Headline
**Six AI Agents. One Exceptional Support Experience.**

### Subheadline
Every feature is built to do one thing: help you serve customers better while spending less. No complexity, no compromises.

### CTA
**Start Free Trial** → /signup

---

## Feature Categories Navigation

### Sticky Nav (Scrollspy)
- [AI Agents](#ai-agents)
- [Integrations](#integrations)
- [Customization](#customization)
- [Analytics](#analytics)
- [Personalization](#personalization)
- [Security](#security)
- [Support](#support)

---

## AI Agents Section {#ai-agents}

### Section Headline
**Six Specialized AI Agents**

### Section Description
Simple chatbots use one model for everything. Agent Red deploys six purpose-built agents that each excel at a specific job — classification, research, response, validation, escalation, and analysis. The result: higher accuracy, better safety, and responses that actually resolve issues.

---

### Agent 1: Intent Classification

#### Visual
Agent icon with neural network illustration

#### Headline
**Understand Every Customer Instantly**

#### Description
The Intent Classification Agent analyzes incoming messages and identifies exactly what customers need — in milliseconds. Order status, product questions, returns, complaints, or any of 17 intent categories. 98% accuracy, every time.

#### Key Capabilities
- **17 Intent Categories:** Order status, product info, returns, shipping, account help, billing, complaints, and more
- **Confidence Scoring:** Each classification includes a confidence score for smart routing
- **Context Awareness:** Understands follow-up questions in ongoing conversations
- **Multi-Language:** Classifies intent in English, French (CA), and Spanish

#### Technical Specs
| Metric | Value |
|--------|-------|
| Accuracy | 98%+ |
| Processing Time | < 200ms |
| False Positive Rate | < 2% |
| Model | GPT-4o-mini |

#### Use Case Example
> **Customer:** "Hey, I ordered something last week but it still hasn't arrived. Can you check?"
>
> **Intent Detected:** Order Status Inquiry (confidence: 0.96)
> **Extracted Entities:** Timeframe (last week), Issue type (delivery delay)

---

### Agent 2: Knowledge Retrieval

#### Visual
Agent icon with search/database illustration

#### Headline
**Find the Right Answer, Every Time**

#### Description
The Knowledge Retrieval Agent searches your product catalog, FAQs, policies, and order data to find exactly the right information. Semantic search powered by vector embeddings means it understands meaning — not just keywords.

#### Key Capabilities
- **Real-Time Shopify Sync:** Product details, prices, and inventory always current
- **Semantic Search:** Finds relevant info even when wording differs from your documentation
- **Multi-Source:** Searches products, FAQs, policies, and custom content simultaneously
- **Ranked Results:** Returns the most relevant documents with confidence scores

#### Technical Specs
| Metric | Value |
|--------|-------|
| Retrieval Accuracy | 100% retrieval@1 |
| Query Latency | < 500ms P95 |
| Index Freshness | < 1 hour |
| Embedding Model | text-embedding-3-large |

#### Knowledge Sources
- Shopify product catalog (automatic sync)
- FAQ documents (markdown upload)
- Policy documents (shipping, returns, privacy)
- Custom knowledge base articles
- Conversation history for context

---

### Agent 3: Response Generation

#### Visual
Agent icon with chat bubble/writing illustration

#### Headline
**Natural Responses That Sound Like You**

#### Description
The Response Generation Agent crafts personalized, natural responses using retrieved knowledge and conversation context. Powered by GPT-4o, it generates human-quality responses in your brand voice — never robotic, never off-brand.

#### Key Capabilities
- **Brand Voice Customization:** Configure tone, formality, and personality
- **Personalization:** Uses customer name, order history, and preferences
- **Context Continuity:** Maintains conversation thread across messages
- **Memory-Informed:** Draws from the customer's full interaction history via Persistent Customer Memory to personalize every response
- **Multi-Language:** Generates native-quality responses in supported languages

#### Customization Options
| Setting | Options |
|---------|---------|
| Tone | Professional, Friendly, Casual, Formal |
| Length | Concise, Detailed, Comprehensive |
| Personality | Configurable name and style |
| Branding | White-label available (Enterprise) |

#### Technical Specs
| Metric | Value |
|--------|-------|
| Quality Score | 88.4% (human evaluation) |
| Generation Time | < 2 seconds P95 |
| Model | GPT-4o |

#### Example Response
> **Customer Query:** "Do you have the blue sweater in medium?"
>
> **Generated Response:** "Great choice! Yes, we have the Coastal Blue Merino Sweater in Medium in stock. It's $89 and ships free. Would you like me to add it to your cart, or do you have any questions about sizing?"

---

### Agent 4: Critic/Supervisor

#### Visual
Agent icon with shield/checkmark illustration

#### Headline
**Quality Control for Every Response**

#### Description
The Critic/Supervisor Agent validates every response before it reaches your customer. It checks for accuracy, safety, brand alignment, and potential issues — ensuring zero hallucinations, zero embarrassments, and complete brand consistency.

#### Key Capabilities
- **Accuracy Validation:** Verifies facts against your knowledge base
- **Safety Filtering:** Blocks harmful, offensive, or inappropriate content
- **Brand Compliance:** Ensures responses match your brand guidelines
- **PII Protection:** Prevents accidental data leakage in responses

#### Protection Categories
- Prompt injection detection and blocking
- Profanity and offensive content filtering
- Competitor mention filtering
- Compliance violation detection
- Hallucination prevention

#### Technical Specs
| Metric | Value |
|--------|-------|
| Malicious Block Rate | 100% |
| False Positive Rate | < 5% |
| Validation Latency | < 200ms P95 |
| Model | GPT-4o-mini |

---

### Agent 5: Escalation

#### Visual
Agent icon with human handoff illustration

#### Headline
**Smart Handoffs to Your Team**

#### Description
The Escalation Agent knows when to involve humans. It automatically routes complex, sensitive, or high-value issues to your team via Zendesk — with complete conversation context so your agents hit the ground running.

#### Key Capabilities
- **Intelligent Triggers:** Escalates based on confidence, sentiment, and complexity
- **Full Context Transfer:** Human agents see the complete conversation history
- **Priority Assignment:** Routes based on customer value and urgency
- **Seamless Handoff:** Customers never repeat themselves

#### Escalation Triggers
| Trigger | Description |
|---------|-------------|
| Low Confidence | AI confidence below threshold |
| Negative Sentiment | Frustrated or angry customer detected |
| Human Request | Customer explicitly asks for a person |
| Complex Issue | Multi-part or unusual request |
| VIP Customer | High-value customer flag |
| Compliance Topic | Legal, safety, or sensitive subject |

#### Technical Specs
| Metric | Value |
|--------|-------|
| Precision | 100% |
| Recall | 100% |
| False Escalation Rate | 0% |
| Handoff Time | < 30 seconds |

---

### Agent 6: Analytics

#### Visual
Agent icon with chart/graph illustration

#### Headline
**Insights That Drive Improvement**

#### Description
The Analytics Agent continuously tracks performance, identifies trends, and generates actionable insights. Understand what customers ask, how issues resolve, and where to focus improvement efforts.

#### Key Capabilities
- **Real-Time Dashboard:** Live metrics on volume, resolution, and satisfaction
- **Trend Analysis:** Spot patterns in customer inquiries over time
- **Cost Tracking:** Monitor and optimize support costs per conversation
- **Custom Reports:** Build reports tailored to your needs (Enterprise)

#### Metrics Tracked
- Conversation volume (hourly/daily/weekly)
- Intent distribution
- Automation rate vs. escalation rate
- Average response time
- Customer satisfaction (CSAT)
- Cost per conversation
- Knowledge base effectiveness
- Agent performance comparisons

#### Report Types by Tier
| Report | Starter | Professional | Enterprise |
|--------|---------|--------------|------------|
| Daily Summary | ✓ | ✓ | ✓ |
| Weekly Trends | — | ✓ | ✓ |
| Monthly Executive | — | ✓ | ✓ |
| Custom Queries | — | — | ✓ |
| API Export | — | ✓ | ✓ |

---

## Integrations Section {#integrations}

### Section Headline
**Connects to Your Entire Stack**

### Section Description
Agent Red integrates natively with the tools you already use. Real-time data sync means your AI always has the latest information — no stale answers, no missing context.

---

### Integration: Shopify

#### Logo
Shopify logo

#### Headline
**Native Shopify Integration**

#### Description
Deep, real-time integration with your Shopify store. Agent Red automatically accesses orders, products, customers, and inventory to provide accurate, personalized support.

#### Capabilities
- **Order Lookup:** Real-time order status, tracking, and history
- **Product Search:** Catalog search with pricing and availability
- **Customer Profiles:** Purchase history and preferences
- **Inventory Check:** Real-time stock availability
- **Return Processing:** Initiate returns and refunds (Enterprise)

#### Setup Time
15 minutes

#### Required Scopes
`read_orders`, `read_products`, `read_customers`, `read_inventory`

---

### Integration: Zendesk

#### Logo
Zendesk logo

#### Headline
**Seamless Zendesk Escalation**

#### Description
When issues need human attention, Agent Red creates Zendesk tickets with full conversation context. Your agents get a head start. Customers never repeat themselves.

#### Capabilities
- **Automatic Ticket Creation:** Escalated conversations become tickets instantly
- **Context Attachment:** Full conversation history included
- **Priority Assignment:** Smart priority based on issue type and customer value
- **Agent Routing:** Route to the right team based on issue type
- **Status Sync:** Ticket updates reflect in Agent Red

#### Setup Time
30 minutes

#### Available On
Professional, Enterprise

---

### Integration: Mailchimp

#### Logo
Mailchimp logo

#### Headline
**Marketing Intelligence**

#### Description
Access customer marketing data to provide more personalized support. Know which campaigns they've engaged with and their subscription preferences.

#### Capabilities
- **Segment Lookup:** See which customer segments apply
- **Campaign History:** Know which emails they've received
- **Subscription Status:** Check email preferences
- **Preference Updates:** Update marketing preferences in real time

#### Setup Time
20 minutes

#### Available On
Enterprise

---

### Integration: Google Analytics

#### Logo
Google Analytics logo

#### Headline
**Unified Analytics**

#### Description
Track customer service interactions alongside your other analytics. Understand how support impacts conversion and customer lifetime value.

#### Capabilities
- **Event Tracking:** Conversation events flow into GA4
- **Goal Completion:** Track support-influenced conversions
- **Attribution:** Connect support interactions to revenue
- **Custom Dimensions:** Enrich analytics with support data

#### Setup Time
15 minutes

#### Available On
Enterprise

---

### Coming Soon

#### Slack
Real-time notifications and team collaboration

#### Gorgias
Alternative helpdesk integration for e-commerce

#### Klaviyo
E-commerce marketing automation

#### Salesforce
Enterprise CRM integration

### Integration CTA
**Request an Integration** → /contact

---

## Customization Section {#customization}

### Section Headline
**Make It Yours**

### Section Description
Agent Red adapts to your brand, not the other way around. Customize everything from tone of voice to escalation rules.

---

### Feature: Brand Voice

#### Headline
**Your Tone, Your Style**

#### Description
Configure your AI agent's personality to match your brand. From casual and friendly to professional and formal — you control exactly how Agent Red speaks to your customers.

#### Options
| Setting | Choices |
|---------|---------|
| Tone | Professional, Friendly, Casual, Formal |
| Formality | High, Medium, Low |
| Emoji Use | Never, Sometimes, Often |
| Agent Name | Custom (e.g., "Sophie", "Support Team") |
| Greeting Style | Formal, Casual, Personalized |
| Sign-off Style | Formal, Casual, None |

---

### Feature: Knowledge Base

#### Headline
**Teach Your AI**

#### Description
Upload FAQs, policies, product guides, and any content you want Agent Red to know. The more you teach it, the better it serves your customers.

#### Supported Formats
- Markdown (.md)
- Plain text (.txt)
- PDF documents
- CSV for structured data
- Direct Shopify product sync

#### Management Features
- Version history
- Bulk upload
- Category organization
- Search and preview
- Usage analytics

---

### Feature: Escalation Rules

#### Headline
**Control When Humans Step In**

#### Description
Define exactly when conversations should escalate to your team. Set thresholds, keywords, and conditions to match your support strategy.

#### Configurable Rules
| Rule Type | Description |
|-----------|-------------|
| Confidence Threshold | Escalate below X% confidence |
| Sentiment Detection | Escalate on negative sentiment |
| Keyword Triggers | Escalate on specific words or phrases |
| Topic Categories | Always escalate certain topics |
| Customer Tags | Auto-escalate VIP customers |
| Time Limits | Escalate after X exchanges |

---

### Feature: Response Templates

#### Headline
**Consistent Answers to Common Questions**

#### Description
Create templates for frequently asked questions. Ensure consistent, accurate responses while maintaining natural conversation flow.

#### Template Features
- Variable insertion (customer name, order number, product details)
- A/B testing variants
- Performance tracking
- Multi-language versions
- Category organization

---

### Feature: White-Label (Enterprise)

#### Headline
**Your Brand, Completely**

#### Description
Remove all Agent Red branding for a completely white-label experience. Your customers interact with your brand — and only your brand.

#### Includes
- Custom domain for chat widget
- Custom email sender address
- Branded dashboard
- Custom favicon and logos
- Full CSS styling control

---

## Analytics Section {#analytics}

### Section Headline
**Data-Driven Customer Service**

### Section Description
Real-time insights into every aspect of your customer support. Track what matters, spot trends, and continuously improve.

---

### Dashboard Overview

#### Screenshot
Analytics dashboard screenshot showing key metrics

#### Key Metrics Displayed
- Total conversations (today/week/month)
- Automation rate percentage
- Average response time
- Customer satisfaction score
- Top intents chart
- Resolution rate trend

---

### Feature: Real-Time Metrics

#### Headline
**See What's Happening Now**

#### Description
Live dashboard shows current conversation volume, response times, and performance. Spot issues before they become problems.

#### Metrics
- Active conversations
- Queue depth
- Average wait time
- Resolution rate (live)
- Escalation rate (live)

---

### Feature: Trend Analysis

#### Headline
**Understand Patterns Over Time**

#### Description
Weekly and monthly reports reveal trends in customer inquiries. Anticipate busy periods, identify emerging issues, and optimize staffing.

#### Insights
- Volume trends by day and hour
- Seasonal patterns
- Intent category shifts
- Satisfaction trends
- Cost per conversation trends

---

### Feature: Custom Reports (Enterprise)

#### Headline
**Build Reports That Matter to You**

#### Description
Create custom reports with the metrics you care about. Export to CSV, schedule automated delivery, or access via API for your BI tools.

#### Capabilities
- Drag-and-drop report builder
- Custom date ranges
- Metric filtering
- Scheduled email delivery
- API access for BI tools

---

## Personalization Section {#personalization}

### Section Headline
**Persistent Customer Memory**

### Section Description
Every conversation builds on the last. Agent Red maintains a persistent memory for each customer — their preferences, past issues, communication style, and interaction history — so responses feel personal and customers never have to repeat themselves.

No competitor has confirmed implementing per-customer vector RAG over historical transcripts. Agent Red is the first platform to deliver true persistent customer memory at scale.

---

### Feature: Customer Context (Layer 1)

#### Headline
**Instant Customer Awareness**

#### Description
Every AI interaction begins with a complete picture of the customer. A structured profile — preferences, account state, plan tier, active integrations, and interaction summary — is automatically injected into every conversation. The agent knows who the customer is before they say a word.

#### Capabilities
- Customer name, plan tier, and account state injected automatically
- Active integrations and configuration visible to the agent
- Communication preferences (formal vs. casual, detail level) applied
- Shopify order history, product preferences, and engagement data included

#### Available On
All tiers (Starter, Professional, Enterprise)

---

### Feature: Conversation Memory (Layer 2)

#### Headline
**Full Interaction History at the Agent's Fingertips**

#### Description
Past conversation transcripts are cleansed, vectorized, and stored in a per-customer index. When a customer starts a new session, the system performs semantic search across their entire interaction history to surface relevant context. If a customer asks "any update on my return?" — the agent already knows what product, when it was discussed, and what was promised.

#### Capabilities
- Semantic search across full interaction history
- Time-weighted recency boosting (recent interactions preferred)
- Tenant-isolated vector indexes (no cross-customer data leakage)
- Sub-500ms retrieval latency
- PII-safe: transcripts cleansed before vectorization

#### Available On
All tiers (Starter, Professional, Enterprise)

---

### Feature: Cross-Session Learning (Layer 3)

#### Headline
**An Agent That Learns Your Customers Over Time**

#### Description
A memory framework processes interaction history to extract structured insights — communication style preferences, recurring issues, product usage patterns, escalation triggers, and satisfaction signals. These memories persist across sessions and update automatically as new interactions occur.

#### Capabilities
- Learns communication preferences (technical depth, formality, verbosity)
- Recognizes recurring issues and proactively addresses them
- Detects escalation patterns and adjusts response strategy
- Updates preferences in real time as customer behavior evolves
- Memory entries are auditable and human-reviewable

#### Available On
Professional and Enterprise tiers

---

### Feature: Dedicated Model Training (Layer 4)

#### Badge
Enterprise Add-On — $299/month

#### Headline
**A Dedicated AI Model for Your Highest-Value Customers**

#### Description
For Enterprise customers with 1,000+ historical interactions, Agent Red creates a fine-tuned AI model trained exclusively on that customer's data. The model captures nuanced communication style, domain-specific vocabulary, and behavioral patterns beyond what memory and context can achieve. An automated quality gate ensures the fine-tuned model matches or exceeds baseline quality before deployment.

#### Capabilities
- Per-customer fine-tuned AI model (trained on their data only)
- Style adaptation (matches customer's tone and formality)
- Domain vocabulary adoption (uses customer-specific terminology)
- Automated quality gate with fallback to base model
- Periodic retraining on accumulated new interactions
- Full consent management (opt-in, revocable at any time)

#### Requirements
- Minimum 1,000 historical interactions
- Explicit customer opt-in (not enabled by default)
- Enterprise tier only

#### Available On
Enterprise only (add-on, $299/month)

---

### Tier Availability

| Layer | Starter | Professional | Enterprise |
|-------|---------|-------------|------------|
| Customer Context | Included | Included | Included |
| Conversation Memory | Included | Included | Included |
| Cross-Session Learning | — | Included | Included |
| Dedicated Model Training | — | — | Add-on ($299/mo) |

---

### Competitive Advantage

Agent Red's Persistent Customer Memory delivers enterprise-grade personalization at approximately $0.01 per customer per month in marginal cost. No competitor — not Sierra, Intercom, Zendesk, Gorgias, or any other platform — has confirmed implementing per-customer vector RAG over historical transcripts. Most rely on basic CRM data lookup or session-scoped context. Agent Red goes further.

---

### Example Scenario

**Without Persistent Customer Memory:**
> **Customer:** Hi, I'm having trouble with my Shopify orders not syncing.
> **Agent:** I'm sorry to hear that. Can you tell me your store name and what integration you're using?

**With Persistent Customer Memory:**
> **Customer:** Hi, I'm having trouble with my Shopify orders not syncing.
> **Agent:** Hi Sarah — I can see this has come up before with your Acme Store Shopify integration. Last time (January 15th), it was a webhook configuration issue that we resolved by re-registering the orders/updated webhook. Let me check if the same issue has recurred.

---

## Security Section {#security}

### Section Headline
**Enterprise-Grade Security**

### Section Description
Your customer data is precious. Agent Red protects it with bank-grade security, strict compliance, and transparent practices.

---

### Feature: Data Encryption

#### Headline
**Encrypted Everywhere**

#### Description
All data is encrypted in transit and at rest. Your customers' information is protected at every step — no exceptions.

#### Details
- TLS 1.3 for all connections
- AES-256 encryption at rest
- Azure managed encryption keys
- PII tokenization for all AI processing

---

### Feature: Compliance

#### Headline
**Built for Compliance**

#### Description
Agent Red is designed to meet strict compliance requirements from day one. GDPR, CCPA, and SOC 2 (in progress) compliant.

#### Certifications & Compliance
| Standard | Status |
|----------|--------|
| GDPR | ✓ Compliant |
| CCPA | ✓ Compliant |
| SOC 2 Type 2 | In Progress (Q3 2026) |
| PCI DSS | Not Applicable |

---

### Feature: Privacy Controls

#### Headline
**Respect Customer Privacy**

#### Description
Full support for data subject rights. Customers can access, export, or delete their data at any time.

#### Capabilities
- Right to access (data export)
- Right to deletion (data purge)
- Consent management
- Cookie-less tracking option
- Anonymous analytics mode

---

### Feature: Access Control

#### Headline
**Control Who Sees What**

#### Description
Role-based access control ensures team members only see what they need. Full audit logging tracks every action.

#### Features
- Role-based permissions
- Team member management
- SSO integration (Enterprise)
- Audit logging
- Session management

---

## Support Section {#support}

### Section Headline
**We're Here to Help**

### Section Description
From self-service documentation to dedicated success managers, Agent Red provides the support you need to succeed.

---

### Support Tiers

#### Starter Support
- Comprehensive documentation
- Community forum access
- Email support (48-hour response)
- Knowledge base

#### Professional Support
- Everything in Starter
- Chat support
- 24-hour email response
- Priority ticket queue
- Monthly check-in calls

#### Enterprise Support
- Everything in Professional
- Dedicated Customer Success Manager
- Phone support (4-hour response)
- Direct Slack channel
- Quarterly business reviews
- Custom training sessions

---

### Support Resources

#### Documentation
Comprehensive guides, tutorials, and API reference

#### Community Forum
Connect with other users, share tips, get answers

#### Status Page
Real-time system status and incident history

#### Changelog
Latest updates, improvements, and new features

---

## Final CTA Section

### Headline
**Ready to See Agent Red in Action?**

### Description
Start your free trial today. Full Professional features, no credit card required, live in 15 minutes.

### Primary CTA
**Start Free Trial** → /signup

### Secondary CTA
**Compare Plans** → /pricing

### Trust Elements
- 14-day free trial
- No credit card required
- Full Professional features
- Setup in 15 minutes

---

## Technical Notes

### SEO Requirements
- Semantic HTML5 structure
- Schema markup: Product, ItemList (features)
- Scrollspy navigation with smooth scrolling
- Alt text for all agent icons and screenshots

### Analytics Events

| Event | Trigger | Parameters |
|-------|---------|------------|
| `page_view` | Page load | page_name |
| `feature_section_view` | Section enters viewport | section_name |
| `agent_card_expand` | Agent detail expanded | agent_name |
| `cta_click` | CTA button click | cta_type, cta_location |
| `integration_click` | Integration card clicked | integration_name |

---

*Content Version: 2.0.0*
*Last Updated: 2026-01-29*
*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
