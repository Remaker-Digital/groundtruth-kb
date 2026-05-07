---
slug: /
sidebar_position: 1
title: Welcome
hide_title: true
---

import ThemedImage from '@theme/ThemedImage';

<div style={{textAlign: 'center', marginBottom: '2rem'}}>
  <ThemedImage
    alt="Agent Red"
    sources={{
      light: '/img/primary-logo-no-wordmark_black_text.svg',
      dark: '/img/agent-red-logo.svg',
    }}
    style={{maxHeight: '240px', marginTop: '100px', marginBottom: '80px'}}
  />
  <h1 style={{fontSize: '2.5rem', marginBottom: '0.25rem'}}>Agent Red Customer Experience</h1>
  <p style={{fontSize: '1.1rem', opacity: 0.7}}>
    A product of <a href="https://remakerdigital.com" target="_blank" rel="noopener noreferrer">Remaker Digital</a>
  </p>
</div>

Agent Red is an AI-powered customer service platform that automates support conversations across your e-commerce channels. Built on a proven open-source foundation with a multi-agent AI pipeline, Agent Red delivers accurate, context-aware responses at scale.

## What you'll find here

- **[Getting started](/docs/getting-started/overview)** — Understand what Agent Red does, how it works, and how to set up your first deployment.
- **[Admin guide](/docs/admin-guide)** — Complete reference for every setting in the admin console — what each input does, how changing it affects system behavior, and best practices.
- **[Integrations](/docs/integrations/shopify)** — Connect Agent Red to Shopify and other platforms.
- **[Billing](/docs/billing/billable-conversation-spec)** — How conversations are metered and billed.
- **[Changelog](/docs/changelog)** — What's new in each release.

## Project dashboard and session startup

Agent Red uses GT-KB as project governance and delivery infrastructure. The project dashboard highlights delivery history, release posture, tool integration health, risks, backlog pressure, and stakeholder-ready PDF export.

<img src="/img/gtkb-dashboard/dashboard-top.png" alt="Agent Red GT-KB dashboard top section" style={{width: '100%', border: '1px solid #d8e2ee', borderRadius: '8px'}} />

Every new work session starts from dashboard-derived choices in the AI/user chat stream. The focus list turns current evidence into action: release blockers, failing integrations, known risks, stage/test readiness, internal review cleanup, backlog selection, or a custom focus.

<img src="/img/gtkb-dashboard/session-focus-options.png" alt="Session startup focus choices derived from the dashboard" style={{width: '100%', border: '1px solid #d8e2ee', borderRadius: '8px'}} />

## Key capabilities

| Capability | Description |
|------------|-------------|
| **Intent classification** | Routes customer queries across 18 intent categories (17 customer-facing plus 1 admin-only route) |
| **Knowledge retrieval** | Searches products, FAQs, and policies using hybrid vector + keyword search |
| **Response generation** | Crafts personalized, brand-consistent replies powered by GPT-4o |
| **Escalation detection** | Identifies conversations requiring human intervention |
| **Analytics** | Monitors conversation quality, resolution rates, and AI performance |
| **Content safety** | Validates every response before delivery to customers |
| **Persistent customer memory** | Builds customer context, conversation history, and learned preferences across sessions |
| **Customer identity** | Pre-chat form, OTP email verification, and Shopify HMAC passthrough ensure every conversation is linked to a real customer |
| **Automated onboarding** | Widget keys, welcome emails, and setup wizard guide new merchants from signup to first conversation |
| **MCP integrations** | Connects to Stripe and Shopify Storefront via the Model Context Protocol for real-time payment and product data |
| **Admin security** | API key authentication, magic-link sign-in, and optional two-factor verification for admin-console access |

## Platform tiers

| Tier | Included conversations | Starting at |
|------|----------------------|-------------|
| Starter | 1,000/month | $149/month |
| Professional | 5,000/month | $399/month |
| Enterprise | 20,000/month | $999/month |

All tiers include the full six-agent pipeline and a 14-day free trial. [Get started with Shopify](/docs/integrations/shopify) or [contact us](mailto:support@remakerdigital.com) for standalone deployments.

## Need help?

- **Support:** [support@remakerdigital.com](mailto:support@remakerdigital.com)
- **Install:** [Shopify integration guide](/docs/integrations/shopify)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
