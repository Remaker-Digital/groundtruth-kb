# AGNTCY Customer Engagement Platform - Complete Feature Reference

> **Document Purpose:** This document provides comprehensive product information optimized for RAG (Retrieval-Augmented Generation) systems. It enables AI assistants to accurately answer questions about product features, pricing, capabilities, and technical specifications.

> **Last Updated:** 2026-01-29
> **Version:** 1.0.0
> **Product:** AGNTCY Customer Engagement Platform

---

## Document Structure

This document is organized into the following sections for optimal RAG retrieval:

1. [Product Overview](#product-overview)
2. [Product Tiers & Pricing](#product-tiers--pricing)
3. [Core Features](#core-features)
4. [Add-On Modules](#add-on-modules)
5. [Technical Specifications](#technical-specifications)
6. [Integration Capabilities](#integration-capabilities)
7. [Security & Compliance](#security--compliance)
8. [Support & SLA](#support--sla)
9. [Frequently Asked Questions](#frequently-asked-questions)
10. [Glossary](#glossary)

---

## Product Overview

### What is AGNTCY Customer Engagement Platform?

AGNTCY Customer Engagement Platform is an enterprise-grade, AI-powered customer service automation solution built on multi-agent architecture. It enables e-commerce businesses to provide instant, accurate, and personalized customer support across multiple channels while significantly reducing operational costs.

### Key Value Propositions

| Benefit | Description | Typical Result |
|---------|-------------|----------------|
| **Cost Reduction** | Automate 70%+ of routine customer inquiries | 40-60% reduction in support costs |
| **24/7 Availability** | AI agents respond instantly, any time | 95%+ availability SLA |
| **Scalability** | Handle 10,000+ daily users without additional staff | Linear cost scaling |
| **Personalization** | Context-aware responses using customer history | 25%+ improvement in CSAT |
| **Multi-Language** | Support customers in English, French (CA), and Spanish | Expanded market reach |

### Target Customers

- **Primary:** Mid-market e-commerce businesses ($5M-$100M annual revenue)
- **Secondary:** Enterprise retailers with high support volume
- **Ideal Profile:** Shopify Plus merchants with 500+ daily support tickets

### Platform Architecture

The platform uses a multi-agent architecture with six specialized AI agents:

1. **Intent Classification Agent** - Understands customer intent from natural language
2. **Knowledge Retrieval Agent** - Searches product catalogs and knowledge bases
3. **Response Generation Agent** - Creates personalized, contextual responses
4. **Escalation Agent** - Routes complex issues to human agents intelligently
5. **Analytics Agent** - Tracks performance metrics and generates insights
6. **Critic/Supervisor Agent** - Validates content safety and quality

---

## Product Tiers & Pricing

### Pricing Philosophy

All prices are based on a 10x cost multiplier to ensure sustainable business operations, continuous product development, and premium support services.

### Tier Comparison

| Feature | Starter | Professional | Enterprise |
|---------|---------|--------------|------------|
| **Monthly Price** | $299/mo | $499/mo | $999/mo |
| **Annual Price** | $2,990/yr (save $598) | $4,990/yr (save $998) | $9,990/yr (save $1,998) |
| **Daily Conversations** | Up to 500 | Up to 2,000 | Up to 10,000 |
| **Languages** | English only | English + 1 | English + 2 (all) |
| **Response Time SLA** | < 5 seconds | < 2 seconds | < 1 second |
| **Uptime SLA** | 99.5% | 99.9% | 99.95% |
| **Support** | Email (48hr) | Email + Chat (24hr) | Dedicated CSM + Phone |
| **Integrations** | Shopify | Shopify + Zendesk | All + Custom |
| **Analytics** | Basic dashboard | Advanced analytics | Custom reports + API |
| **Knowledge Base** | 50 articles | 200 articles | Unlimited |
| **Agent Customization** | Basic tone | Full personality | White-label |
| **API Access** | Read-only | Full API | Enterprise API + Webhooks |

### Starter Tier - $299/month

**Best For:** Small e-commerce stores launching AI-powered support

**Includes:**
- Up to 500 AI-handled conversations per day
- English language support
- Basic Shopify integration (orders, products, customers)
- Pre-built response templates
- Email support with 48-hour response time
- Basic analytics dashboard
- 50-article knowledge base
- Standard security features

**Cost Basis:** ~$30/month infrastructure + support overhead

### Professional Tier - $499/month

**Best For:** Growing businesses needing advanced automation

**Includes Everything in Starter, Plus:**
- Up to 2,000 AI-handled conversations per day
- One additional language (French-CA or Spanish)
- Zendesk integration for escalation management
- Advanced analytics with trend analysis
- 200-article knowledge base
- Full API access for custom integrations
- Chat support with 24-hour response time
- Custom agent personality configuration
- Webhook notifications for events
- Priority queue for feature requests

**Cost Basis:** ~$50/month infrastructure + support overhead

### Enterprise Tier - $999/month

**Best For:** High-volume merchants requiring maximum customization

**Includes Everything in Professional, Plus:**
- Up to 10,000 AI-handled conversations per day
- All three languages (English, French-CA, Spanish)
- White-label capability (remove AGNTCY branding)
- Dedicated Customer Success Manager
- Phone support with 4-hour response time
- Unlimited knowledge base articles
- Custom analytics reports and dashboards
- Enterprise API with higher rate limits
- Custom webhook integrations
- Mailchimp marketing automation integration
- Google Analytics event tracking
- Quarterly business reviews
- Early access to new features
- Custom SLA negotiations available

**Cost Basis:** ~$100/month infrastructure + dedicated support

### Volume Discounts

| Annual Commitment | Discount |
|-------------------|----------|
| 1 year | 17% (2 months free) |
| 2 years | 25% |
| 3 years | 33% |

### Overage Pricing

When conversation limits are exceeded:

| Tier | Overage Rate | Soft Cap |
|------|--------------|----------|
| Starter | $0.15/conversation | 150% of limit |
| Professional | $0.10/conversation | 200% of limit |
| Enterprise | $0.05/conversation | No cap |

---

## Core Features

### Intent Classification

**What It Does:** Automatically identifies customer intent from natural language queries.

**How It Works:**
1. Customer sends message (text, email, or chat)
2. Intent Classification Agent analyzes using GPT-4o-mini
3. Classifies into 15+ intent categories with confidence scores
4. Routes to appropriate handling workflow

**Supported Intents:**
- Order status inquiry
- Product information request
- Return/refund request
- Shipping question
- Account management
- Technical support
- Pricing inquiry
- Complaint/feedback
- General question
- Purchase assistance
- Inventory check
- Promotion/discount inquiry
- Cancellation request
- Delivery issue
- Custom intent (Enterprise only)

**Performance Metrics:**
- Classification accuracy: 98%+
- Processing time: < 200ms
- False positive rate: < 2%

### Knowledge Retrieval

**What It Does:** Searches product catalogs, FAQs, and policy documents to find relevant information.

**How It Works:**
1. Receives classified intent and customer query
2. Generates semantic embeddings using text-embedding-3-large
3. Performs vector similarity search in Cosmos DB
4. Returns top-k relevant documents with confidence scores

**Data Sources:**
- Shopify product catalog (real-time sync)
- FAQ documents (markdown format)
- Policy documents (shipping, returns, privacy)
- Custom knowledge base articles
- Historical conversation context

**Performance Metrics:**
- Retrieval accuracy: 100% retrieval@1 for exact matches
- Query latency: < 500ms P95
- Index freshness: < 1 hour for catalog updates

### Response Generation

**What It Does:** Creates natural, personalized responses using retrieved context.

**How It Works:**
1. Receives intent, knowledge results, and conversation history
2. Constructs prompt with customer context and retrieved information
3. Generates response using GPT-4o for quality
4. Applies brand voice and tone guidelines

**Customization Options:**
- Tone: Professional, Friendly, Casual, Formal
- Length: Concise, Detailed, Comprehensive
- Personality: Configurable agent name and style
- Branding: White-label for Enterprise tier

**Performance Metrics:**
- Response quality score: 88.4% (human evaluation)
- Generation time: < 2 seconds P95
- Customer satisfaction: 25%+ improvement vs. templates

### Intelligent Escalation

**What It Does:** Routes complex issues to human agents with full context.

**How It Works:**
1. Monitors conversation for escalation triggers
2. Evaluates complexity, sentiment, and confidence scores
3. Creates Zendesk ticket with conversation summary
4. Assigns priority based on customer value and urgency

**Escalation Triggers:**
- Low confidence score (< 0.5)
- Negative sentiment detected
- Explicit human request
- Complex multi-part issues
- VIP customer flag
- Compliance-sensitive topics
- Repeat contact within 24 hours

**Performance Metrics:**
- Escalation precision: 100%
- Escalation recall: 100%
- False escalation rate: 0%
- Average escalation time: < 30 seconds

### Content Validation (Critic/Supervisor)

**What It Does:** Ensures all AI responses meet safety and quality standards.

**How It Works:**
1. Scans all incoming messages for prompt injection attacks
2. Validates all outgoing responses for harmful content
3. Blocks or regenerates content that fails validation
4. Logs all validation decisions for audit

**Protection Categories:**
- Prompt injection detection
- Profanity and offensive content
- PII leakage prevention
- Competitor mention filtering
- Compliance violation detection
- Hallucination detection

**Performance Metrics:**
- Malicious input block rate: 100%
- False positive rate: < 5%
- Validation latency: < 200ms P95

### Analytics & Reporting

**What It Does:** Tracks performance metrics and generates actionable insights.

**Metrics Tracked:**
- Conversation volume by hour/day/week
- Intent distribution
- Resolution rate (automated vs. escalated)
- Average response time
- Customer satisfaction scores
- Cost per conversation
- Agent utilization
- Knowledge base effectiveness

**Report Types:**
| Report | Starter | Professional | Enterprise |
|--------|---------|--------------|------------|
| Daily summary | ✓ | ✓ | ✓ |
| Weekly trends | - | ✓ | ✓ |
| Monthly executive | - | ✓ | ✓ |
| Custom queries | - | - | ✓ |
| API export | - | ✓ | ✓ |

---

## Add-On Modules

### Multi-Language Support - $149/month

**What It Adds:** Support for French (Canadian) and Spanish languages.

**Includes:**
- Automatic language detection
- Native-quality responses in fr-CA and es
- Language-specific knowledge bases
- Localized date/currency formatting
- Language routing to specialized agents

**Technical Details:**
- Detection accuracy: 99%+
- No translation delay (native generation)
- Separate prompt engineering per language

**Available With:** Professional and Enterprise tiers

### Advanced Analytics - $199/month

**What It Adds:** Deep insights and predictive analytics.

**Includes:**
- Predictive volume forecasting
- Churn risk identification
- Sentiment trend analysis
- A/B testing framework
- Custom metric definitions
- Real-time alerting
- Data warehouse export

**Technical Details:**
- 90-day data retention (vs. 30-day standard)
- 15-minute refresh cycle (vs. hourly)
- Custom SQL query access

**Available With:** All tiers

### Priority Support - $99/month

**What It Adds:** Faster response times and dedicated assistance.

**Includes:**
- 4-hour email response SLA (vs. 24-48 hour)
- Priority ticket queue
- Monthly check-in calls
- Direct Slack channel (Enterprise)
- After-hours emergency support

**Technical Details:**
- Support hours: 6 AM - 10 PM ET (M-F)
- Emergency line: 24/7 for P1 issues

**Available With:** All tiers

### Custom Integrations - $299/month

**What It Adds:** Connect to additional business systems.

**Includes:**
- Custom API connector development
- ERP integration (NetSuite, SAP)
- CRM integration (Salesforce, HubSpot)
- Custom webhook endpoints
- Data transformation pipelines
- Dedicated integration engineer (8 hrs/mo)

**Technical Details:**
- REST and GraphQL support
- OAuth 2.0 authentication
- Rate limiting and retry logic

**Available With:** Professional and Enterprise tiers

### White-Label Package - $499/month

**What It Adds:** Complete brand customization.

**Includes:**
- Remove all AGNTCY branding
- Custom domain for chat widget
- Custom email sender address
- Branded analytics dashboard
- Custom favicon and logos
- CSS/styling customization

**Technical Details:**
- CNAME DNS configuration
- SSL certificate provisioning
- 72-hour setup time

**Available With:** Enterprise tier only

---

## Technical Specifications

### Infrastructure

| Component | Technology | Specification |
|-----------|------------|---------------|
| **Compute** | Azure Container Apps | Auto-scaling 1-20 instances per agent |
| **Database** | Azure Cosmos DB | Serverless, 99.99% SLA |
| **Cache** | Azure Cache for Redis | Basic C0 tier |
| **Vector Search** | Cosmos DB MongoDB API | 1536-dimension embeddings |
| **Message Queue** | NATS JetStream | 7-day retention |
| **Gateway** | SLIM (AGNTCY) | gRPC + TLS 1.3 |
| **CDN** | Azure CDN | Global edge locations |
| **Monitoring** | Azure Application Insights | 7-day log retention |

### Performance Benchmarks

| Metric | Target | Achieved |
|--------|--------|----------|
| Response latency P50 | < 1 second | 0.8 seconds |
| Response latency P95 | < 2 seconds | 1.6 seconds |
| Response latency P99 | < 5 seconds | 3.2 seconds |
| Throughput | 3,000 req/min | 3,071 req/min |
| Concurrent users | 100 | 100 |
| Daily capacity | 10,000 users | 10,000 users |
| Uptime | 99.9% | 99.95% |

### API Specifications

**Base URL:** `https://api.agntcy-platform.com/v1`

**Authentication:** Bearer token (JWT)

**Rate Limits:**
| Tier | Requests/minute | Burst |
|------|-----------------|-------|
| Starter | 60 | 100 |
| Professional | 300 | 500 |
| Enterprise | 1,000 | 2,000 |

**Key Endpoints:**
```
POST /conversations        - Start new conversation
POST /conversations/{id}/messages - Send message
GET  /conversations/{id}   - Get conversation history
GET  /analytics/summary    - Get analytics summary
GET  /knowledge/search     - Search knowledge base
POST /webhooks             - Register webhook (Enterprise)
```

### Data Retention

| Data Type | Starter | Professional | Enterprise |
|-----------|---------|--------------|------------|
| Conversations | 30 days | 90 days | 1 year |
| Analytics | 30 days | 90 days | 2 years |
| Audit logs | 30 days | 90 days | 7 years |
| Knowledge base | Unlimited | Unlimited | Unlimited |

### System Requirements (Self-Hosted)

For customers requiring on-premises deployment:

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| vCPUs | 8 | 16 |
| RAM | 32 GB | 64 GB |
| Storage | 100 GB SSD | 500 GB NVMe |
| Network | 100 Mbps | 1 Gbps |
| OS | Ubuntu 22.04 LTS | Ubuntu 22.04 LTS |
| Docker | 24.0+ | 24.0+ |
| Python | 3.12+ | 3.12+ |

---

## Integration Capabilities

### Native Integrations

#### Shopify

**Capabilities:**
- Real-time order status lookup
- Product catalog sync (hourly)
- Customer profile access
- Inventory availability check
- Return/refund initiation
- Discount code validation

**Setup Time:** 15 minutes
**Required Scopes:** `read_orders`, `read_products`, `read_customers`, `read_inventory`

#### Zendesk

**Capabilities:**
- Automatic ticket creation on escalation
- Conversation history attachment
- Priority assignment
- Agent assignment routing
- Status sync back to platform

**Setup Time:** 30 minutes
**Required Scopes:** `tickets:write`, `users:read`

#### Mailchimp (Enterprise)

**Capabilities:**
- Customer segment lookup
- Campaign history access
- Subscription status check
- Marketing preference updates

**Setup Time:** 20 minutes
**Required Scopes:** `lists:read`, `campaigns:read`

#### Google Analytics (Enterprise)

**Capabilities:**
- Event tracking for conversations
- Goal completion tracking
- E-commerce attribution
- Custom dimension population

**Setup Time:** 15 minutes
**Required Scopes:** GA4 Data API access

### Webhook Events

Available webhook events (Professional and Enterprise):

| Event | Description | Payload |
|-------|-------------|---------|
| `conversation.started` | New conversation initiated | conversation_id, customer_id, channel |
| `conversation.ended` | Conversation resolved | conversation_id, resolution, duration |
| `message.received` | Customer message received | message_id, content, intent |
| `message.sent` | AI response sent | message_id, content, confidence |
| `escalation.created` | Issue escalated to human | ticket_id, reason, priority |
| `feedback.received` | Customer provided feedback | rating, comment |

### API SDKs

Official SDKs available:

| Language | Package | Version |
|----------|---------|---------|
| Python | `agntcy-platform-sdk` | 1.0.0 |
| Node.js | `@agntcy/platform-sdk` | 1.0.0 |
| PHP | `agntcy/platform-sdk` | 1.0.0 |

---

## Security & Compliance

### Security Architecture

**Data Encryption:**
- In transit: TLS 1.3 (all connections)
- At rest: AES-256 (Azure managed keys)
- PII tokenization for AI processing

**Authentication:**
- OAuth 2.0 / OpenID Connect
- API key authentication
- Multi-factor authentication (MFA) supported
- SSO integration (SAML 2.0, Enterprise tier)

**Network Security:**
- Private VNet deployment
- Web Application Firewall (WAF)
- DDoS protection (Azure)
- IP allowlisting (Enterprise)

**Access Control:**
- Role-based access control (RBAC)
- Audit logging for all admin actions
- Session timeout (30 minutes default)

### Compliance Status

| Standard | Status | Notes |
|----------|--------|-------|
| **GDPR** | Compliant | Data processing in EU available |
| **CCPA** | Compliant | California consumer rights supported |
| **SOC 2 Type 2** | In Progress | Expected Q3 2026 |
| **HIPAA** | Not Certified | Healthcare customers require BAA |
| **PCI DSS** | Not Applicable | No payment card data processed |
| **ISO 27001** | Planned | Expected 2027 |

### Data Residency

| Region | Availability | Data Center |
|--------|--------------|-------------|
| United States | Available | Azure East US 2 |
| Canada | Available | Azure Canada Central |
| European Union | Planned Q2 2026 | Azure West Europe |

### Privacy Features

- Right to access (data export)
- Right to deletion (data purge)
- Consent management
- Cookie-less tracking option
- Anonymous analytics mode

---

## Support & SLA

### Support Channels

| Channel | Starter | Professional | Enterprise |
|---------|---------|--------------|------------|
| Documentation | ✓ | ✓ | ✓ |
| Community forum | ✓ | ✓ | ✓ |
| Email support | ✓ (48 hr) | ✓ (24 hr) | ✓ (4 hr) |
| Chat support | - | ✓ | ✓ |
| Phone support | - | - | ✓ |
| Dedicated CSM | - | - | ✓ |
| Slack channel | - | - | ✓ |

### Service Level Agreements

**Uptime SLA:**
| Tier | Target | Credit |
|------|--------|--------|
| Starter | 99.5% | 10% for < 99.5% |
| Professional | 99.9% | 25% for < 99.9% |
| Enterprise | 99.95% | 50% for < 99.95% |

**Response Time SLA:**
| Priority | Description | Starter | Professional | Enterprise |
|----------|-------------|---------|--------------|------------|
| P1 | Service down | 4 hours | 2 hours | 30 minutes |
| P2 | Major feature broken | 8 hours | 4 hours | 2 hours |
| P3 | Minor issue | 48 hours | 24 hours | 8 hours |
| P4 | Question/request | 72 hours | 48 hours | 24 hours |

### Maintenance Windows

- **Scheduled:** Sundays 2 AM - 6 AM ET (monthly)
- **Emergency:** As needed with 4-hour notice
- **Notification:** Email + status page

---

## Frequently Asked Questions

### General Questions

**Q: What makes AGNTCY different from other chatbots?**
A: AGNTCY uses a multi-agent architecture where specialized AI agents collaborate to handle different aspects of customer service. This provides higher accuracy (98%+ intent classification) and more natural responses compared to traditional rule-based or single-model chatbots.

**Q: Can AGNTCY handle complex, multi-turn conversations?**
A: Yes. The platform maintains full conversation context across multiple exchanges, allowing for natural back-and-forth dialogue. The Knowledge Retrieval Agent accesses conversation history to provide contextually relevant responses.

**Q: What happens when the AI can't answer a question?**
A: The Escalation Agent automatically routes complex or ambiguous queries to human agents via Zendesk. The ticket includes full conversation history and AI analysis, enabling faster human resolution.

### Pricing Questions

**Q: Is there a free trial?**
A: Yes. We offer a 14-day free trial of the Professional tier with up to 500 conversations. No credit card required to start.

**Q: Can I upgrade or downgrade my plan?**
A: Yes. Plan changes take effect at the start of the next billing cycle. Upgrades can be applied immediately with prorated billing.

**Q: What happens if I exceed my conversation limit?**
A: You'll receive a notification at 80% and 90% of your limit. Overages are billed at the tier's overage rate. Enterprise customers have no hard caps.

**Q: Do you offer discounts for nonprofits or startups?**
A: Yes. Registered 501(c)(3) nonprofits receive 50% off. Startups in approved accelerators receive 25% off for the first year.

### Technical Questions

**Q: How long does integration take?**
A: Shopify integration takes approximately 15 minutes. Full platform configuration including knowledge base setup typically takes 2-4 hours.

**Q: Can I use AGNTCY with platforms other than Shopify?**
A: Yes. While Shopify is our primary integration, the API supports any e-commerce platform. Custom integrations are available in Professional and Enterprise tiers.

**Q: Where is my data stored?**
A: Data is stored in Azure data centers in East US 2 (Virginia) by default. Canadian customers can opt for Canada Central. EU residency is planned for Q2 2026.

**Q: Can I export my data?**
A: Yes. All tiers support data export via the dashboard. Professional and Enterprise tiers can export via API in JSON or CSV format.

### Security Questions

**Q: Is my customer data used to train AI models?**
A: No. Customer data is never used to train AI models. We use Azure OpenAI Service, which does not use customer data for model training.

**Q: How do you handle PII?**
A: PII is tokenized before being sent to AI models. Tokens are stored in Azure Key Vault with encryption at rest. Original PII never leaves the secure Azure perimeter.

**Q: Do you have SOC 2 certification?**
A: SOC 2 Type 2 certification is in progress, expected Q3 2026. We can provide a SOC 2 readiness report and bridge letter upon request.

---

## Glossary

| Term | Definition |
|------|------------|
| **A2A Protocol** | Agent-to-Agent communication protocol used by AGNTCY SDK |
| **Confidence Score** | AI model's certainty about a classification (0.0 to 1.0) |
| **Conversation** | A complete customer interaction session |
| **Embeddings** | Vector representations of text for semantic search |
| **Escalation** | Routing a conversation to a human agent |
| **Intent** | The purpose or goal behind a customer's message |
| **Knowledge Base** | Collection of articles, FAQs, and documents for retrieval |
| **MCP** | Model Context Protocol for tool integrations |
| **PII** | Personally Identifiable Information |
| **RAG** | Retrieval-Augmented Generation - combining search with AI generation |
| **SLIM** | Secure Low-latency Intelligent Messaging - AGNTCY transport layer |
| **Token** | Unit of text for AI processing (roughly 4 characters) |
| **Vector Search** | Semantic similarity search using embeddings |

---

## Document Metadata

```yaml
document_type: product_feature_reference
version: 1.0.0
last_updated: 2026-01-29
author: AGNTCY Product Team
intended_audience:
  - AI assistants (RAG)
  - Sales teams
  - Customer success
  - Technical support
rag_optimization:
  chunk_size: 512
  overlap: 64
  embedding_model: text-embedding-3-large
update_frequency: monthly
related_documents:
  - docs/WIKI-Architecture.md
  - docs/WIKI-Scalability.md
  - docs/API-REFERENCE.md
  - docs/INTEGRATION-GUIDE.md
```

---

## Change Log

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-29 | Initial release |

---

*This document is automatically indexed for RAG retrieval. For the most current pricing and feature availability, visit [agntcy-platform.com/pricing](https://agntcy-platform.com/pricing).*
