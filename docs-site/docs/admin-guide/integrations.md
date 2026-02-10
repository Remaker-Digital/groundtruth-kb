---
sidebar_position: 8
title: Integrations
description: Connect Agent Red to Shopify, Zendesk, Mailchimp, and Google Analytics.
---

# Integrations

Agent Red integrates with external platforms to access customer data, route escalations, and track conversation analytics. This page describes each integration toggle and what it controls.

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
