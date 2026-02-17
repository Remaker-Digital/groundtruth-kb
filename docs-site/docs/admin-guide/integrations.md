---
sidebar_position: 8
title: Integrations
description: Connect Agent Red to Shopify, Stripe, Zendesk, Mailchimp, and Google Analytics.
---

# Integrations

Agent Red integrates with external platforms to access customer data, process payment inquiries, route escalations, and track conversation analytics. This page describes each integration toggle and what it controls.

## Shopify sync

| | |
|---|---|
| **Field** | `shopify_sync_enabled` |
| **Type** | Toggle (on/off) |
| **Default** | On |
| **Affects** | Knowledge retrieval, customer memory |

Enables synchronization of product catalog, order data, and customer profiles from your Shopify store into Agent Red's knowledge base and customer memory layer.

**What syncs:**

| Data type | How it is used |
|---|---|
| Products | Name, description, price, availability — added to knowledge base for product questions |
| Orders | Order status, tracking, delivery dates — available for order lookup queries |
| Customers | Name, email, order history — populates the customer profile for personalized responses |
| Inventory | Stock levels — allows the AI to answer "Is this in stock?" questions accurately |

**When to turn it off:**
- You are testing Agent Red without connecting to real store data.
- You have a separate, non-Shopify product catalog and are importing data manually via knowledge base articles.

**When to leave it on:**
Most stores should leave this on. Without Shopify sync, the AI cannot answer product, order, or inventory questions unless you manually create equivalent knowledge base articles.

---

## Stripe (MCP)

| | |
|---|---|
| **Field** | `stripe_mcp_enabled` |
| **Type** | Toggle (on/off) |
| **Default** | Off |
| **Tier** | Professional and Enterprise |

Connects Agent Red to your Stripe account via the Model Context Protocol (MCP), enabling the AI to answer customer questions about payments, subscriptions, invoices, and refund status directly from Stripe data.

**How it works:**

Agent Red connects to Stripe's official MCP server (`mcp.stripe.com`) using a restricted API key that you provide. The connection is **read-only** — the AI can look up payment and subscription information but cannot modify anything in your Stripe account.

**Setup:**

1. Navigate to **Integrations** in the admin console
2. Enable the **Stripe (MCP)** toggle
3. Enter your Stripe restricted API key (starts with `rk_`)
4. Click **Save Key**, then **Test Connection**
5. A successful test shows a green status badge and the number of available tools

**What the AI can answer:**

| Query type | Example questions |
|---|---|
| Payment status | "Has my payment gone through?" |
| Subscription details | "What plan am I on?" "When does my subscription renew?" |
| Invoice lookup | "Can I see my last invoice?" |
| Refund status | "Where is my refund?" |

**Security:**

- Your Stripe API key is stored in Azure Key Vault (never in the database)
- Keys are cached in memory for 5 minutes to reduce Key Vault latency
- All queries go through the Critic/Supervisor safety validation
- Connection failures are handled gracefully — the AI responds using knowledge base data when Stripe is unavailable

:::tip Restricted keys only
Use a Stripe **restricted key** (`rk_`) with read-only permissions for maximum security. Do not use your secret key (`sk_`).
:::

---

## Zendesk escalation

| | |
|---|---|
| **Field** | `zendesk_escalation_enabled` |
| **Type** | Toggle (on/off) |
| **Default** | Off |
| **Tier** | Professional and Enterprise |
| **Status** | Coming soon |

When enabled, escalated conversations will automatically create a ticket in your Zendesk instance with the full conversation transcript, customer information, and escalation reason.

:::note Coming soon
Zendesk integration is not yet available. The configuration toggle is visible in the admin console for planning purposes. Enabling it has no effect until the backend integration is released.
:::

---

## Mailchimp segment sync

| | |
|---|---|
| **Field** | `mailchimp_segment_sync` |
| **Type** | Toggle (on/off) |
| **Default** | Off |
| **Tier** | Professional and Enterprise |
| **Add-on** | Mailchimp Integration ($49/month) |
| **Status** | Coming soon |

Enables synchronization of customer segments from Mailchimp, providing the AI with marketing context (VIP segment, recent campaign recipient, loyalty status) to personalize responses.

:::note Coming soon
Mailchimp integration is not yet available. The toggle is visible for planning purposes.
:::

---

## Google Analytics

| | |
|---|---|
| **Field** | `google_analytics_enabled` |
| **Type** | Toggle (on/off) |
| **Default** | Off |
| **Tier** | Professional and Enterprise |
| **Add-on** | Google Analytics Integration ($49/month) |
| **Status** | Coming soon |

Sends conversation events (start, end, escalation, resolution) to your Google Analytics 4 property for correlation with site traffic and conversion data.

:::note Coming soon
Google Analytics integration is not yet available. The toggle is visible for planning purposes.
:::

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
