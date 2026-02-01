# Contact Page Content

> **Page Purpose:** Provide clear paths to reach the right team — sales, support, partnerships, and general inquiries
> **Target Audience:** Prospective customers, existing customers, partners, affiliates, press
> **Primary CTA:** Submit Contact Form
> **Secondary CTA:** Start Free Trial

---

## Meta Information

```yaml
title: "Contact Us - Agent Red Customer Experience"
description: "Get in touch with Agent Red. Sales inquiries, support, partnership opportunities, and general questions. We respond within 24 hours."
keywords: "contact Agent Red, AI customer service support, Agent Red sales"
og_image: "/images/og-contact.png"
canonical: "https://agentred.io/contact"
```

---

## Hero Section

### Headline
**Let's Talk**

### Subheadline
Whether you have a question about pricing, need help with setup, or want to explore a partnership — we're here. We respond to every inquiry within 24 hours.

---

## Contact Channels Section

### Section Headline
**Reach the Right Team**

### Channel Cards

#### Sales
**Best for:** Pricing questions, demos, custom plans, volume discounts
**Email:** sales@agentred.io
**Response time:** Within 24 hours (business days)

#### Support
**Best for:** Technical issues, setup help, account questions
**Email:** support@agentred.io
**Response time:** Based on your plan SLA (4hr–48hr)
**Self-service:** [Help Center & Documentation] → /docs

#### Partnerships & Affiliates
**Best for:** Affiliate program, agency partnerships, technology partnerships, reseller inquiries
**Email:** partners@agentred.io
**Response time:** Within 48 hours

#### General Inquiries
**Best for:** Everything else — press, careers, feedback, general questions
**Email:** hello@agentred.io
**Response time:** Within 48 hours

---

## Contact Form Section

### Section Headline
**Send Us a Message**

### Form Fields

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| First Name | Text | Yes | |
| Last Name | Text | Yes | |
| Work Email | Email | Yes | |
| Company Name | Text | No | |
| Company Website | URL | No | |
| Topic | Dropdown | Yes | Sales, Support, Partnerships, General |
| Monthly Conversation Volume | Dropdown | No | Options: Under 500, 500-2,000, 2,000-10,000, 10,000+, Not sure |
| Message | Textarea | Yes | Min 20 characters |

### Form CTA
**Send Message**

### Form Note
We respond to every inquiry within 24 hours on business days. For urgent support issues, existing customers should use the in-app support channel.

---

## Quick Answers Section

### Section Headline
**Before You Reach Out**

### Section Description
Many questions are answered on these pages:

### Quick Links
- **Pricing questions?** → [View transparent pricing](/pricing) — every cost is published
- **How does it work?** → [See all features](/features) — six AI agents explained
- **Integration setup?** → [Integration guides](/integrations) — step-by-step setup
- **Technical docs?** → [Documentation](/docs) — API reference, guides, tutorials
- **Account issues?** → [Help Center](/docs) — self-service troubleshooting

---

## Partner Program Section

### Section Headline
**Interested in Partnering?**

### Section Description
We work with agencies, Shopify Partners, e-commerce consultancies, and content creators. Our partner program includes:

### Partner Benefits
- **Client discounts:** 20% off for your clients
- **Recurring commissions:** Earn on every referral, every month
- **Co-marketing:** Featured in our partner directory
- **Priority support:** Dedicated partner support channel
- **Early access:** Preview new features before launch

### Partner CTA
**Apply to the Partner Program** → /contact?topic=partnerships

---

## Social Section

### Section Headline
**Follow Along**

| Platform | Handle | What We Share |
|----------|--------|---------------|
| Twitter/X | @agentred | Product updates, industry insights |
| LinkedIn | Agent Red | Company news, case studies |
| YouTube | Agent Red | Tutorials, platform demos |
| GitHub | Remaker-Digital | Open-source AGNTCY project |

---

## Final CTA Section

### Headline
**Not Ready to Talk? Try It First.**

### Description
Start a free trial — no sales call required. 14 days, full Professional features, no credit card.

### Primary CTA
**Start Free Trial** → /signup

---

## Technical Notes

### Form Requirements
- CSRF protection on all form submissions
- Honeypot field for spam prevention (no CAPTCHA — keep friction low)
- Form submissions create a record in CRM/email system
- Auto-responder email confirms receipt within 60 seconds
- Topic dropdown routes to the appropriate team inbox

### URL Parameters
The contact form accepts URL parameters to pre-fill fields:
- `?topic=sales` — Pre-selects Sales topic
- `?topic=partnerships` — Pre-selects Partnerships topic
- `?topic=support` — Pre-selects Support topic
- `?plan=starter` — Adds plan context to the message
- `?plan=professional` — Adds plan context
- `?plan=enterprise` — Adds plan context
- `?program=nonprofit` — Pre-fills nonprofit program inquiry
- `?program=startup` — Pre-fills startup program inquiry
- `?program=partner` — Pre-fills partner program inquiry
- `?subject=integration-request` — Pre-fills integration request context

### SEO Requirements
- Semantic HTML5 structure
- Schema markup: ContactPage
- noindex on thank-you/confirmation page

### Analytics Events

| Event | Trigger | Parameters |
|-------|---------|------------|
| `page_view` | Page load | page_name, topic_param |
| `form_start` | First form field focused | — |
| `form_submit` | Form submitted | topic, has_company, has_volume |
| `email_click` | Email address clicked | email_type |
| `social_click` | Social link clicked | platform |
| `partner_cta_click` | Partner program CTA clicked | — |
| `cta_click` | Any CTA clicked | cta_type, cta_location |

---

*Content Version: 2.0.0*
*Last Updated: 2026-01-29*
*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
