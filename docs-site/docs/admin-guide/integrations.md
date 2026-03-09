---
sidebar_position: 8
title: Integrations
description: Connect Agent Red to Shopify, Stripe, Zendesk, Mailchimp, and Google Analytics — setup guides for each platform.
---

# Integrations

Agent Red integrates with external platforms to access customer data, process payment inquiries, route escalations, and track conversation analytics. This page describes each integration, how to set it up, and what configuration changes are needed in the third-party system.

## Integration overview

| Integration | Tier | Purpose | Status |
|---|---|---|---|
| Shopify | All tiers | Product catalog, orders, customers, inventory | Available |
| Stripe (MCP) | Professional+ | Payment status, subscriptions, invoices | Available |
| Zendesk | Professional+ | Ticket creation and escalation routing | Available |
| Mailchimp | Professional+ | Post-conversation email campaigns | Available |
| Google Analytics | Professional+ | Conversation event tracking | Available |
| Custom Integration | Enterprise | Custom API connectors | Available |

## Enabling and disabling integrations

1. Navigate to **Integrations** in the admin console.
2. Each integration is shown as a card with a status badge (Connected or Not Connected).
3. Click **Activate** to enable an integration, or **Deactivate** to pause it.
4. **Disconnect** fully removes the integration configuration.

:::info Tier requirements
Some integrations require the Professional or Enterprise tier. If your plan does not include an integration, the card shows "Requires [Tier] tier" with an upgrade prompt.
:::

---

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

### Prerequisites — setting up your Stripe account

Before enabling this integration, you need a Stripe account with a restricted API key:

1. **Create a Stripe account** (if you do not have one) at [stripe.com](https://stripe.com). Complete the onboarding process including business verification.
2. **Navigate to API keys** in the Stripe dashboard: go to **Developers → API keys**.
3. **Create a restricted key:**
   - Click **Create restricted key**.
   - Name it "Agent Red" (or similar) for easy identification.
   - Set permissions to **Read only** for the following resources:
     - Charges: Read
     - Customers: Read
     - Invoices: Read
     - Payment Intents: Read
     - Subscriptions: Read
     - Refunds: Read
   - Leave all other permissions as "None".
   - Click **Create key**.
4. **Copy the restricted key** (starts with `rk_`). You will need it in the next step.

:::tip Restricted keys only
Use a Stripe **restricted key** (`rk_`) with read-only permissions for maximum security. Do not use your secret key (`sk_`).
:::

### Connecting Stripe to Agent Red

1. Navigate to **Integrations** in the Agent Red admin console.
2. Enable the **Stripe (MCP)** toggle.
3. Enter your Stripe restricted API key (starts with `rk_`).
4. Click **Save Key**, then **Test Connection**.
5. A successful test shows a green status badge and the number of available tools.

**What the AI can answer:**

| Query type | Example questions |
|---|---|
| Payment status | "Has my payment gone through?" |
| Subscription details | "What plan am I on?" "When does my subscription renew?" |
| Invoice lookup | "Can I see my last invoice?" |
| Refund status | "Where is my refund?" |

**Security:**

- Your Stripe API key is stored in Azure Key Vault (never in the database).
- Keys are cached in memory for 5 minutes to reduce Key Vault latency.
- All queries go through the Critic/Supervisor safety validation.
- Connection failures are handled gracefully — the AI responds using knowledge base data when Stripe is unavailable.

---

## Zendesk

| | |
|---|---|
| **Field** | `zendesk_enabled` |
| **Type** | Toggle (on/off) |
| **Default** | Off |
| **Tier** | Professional and Enterprise |

Routes escalated conversations to Zendesk as support tickets, enabling your existing helpdesk workflow to handle cases that the AI cannot resolve.

### Prerequisites — setting up your Zendesk account

1. **Create a Zendesk account** (if you do not have one) at [zendesk.com](https://www.zendesk.com). A Zendesk Suite or Support plan is required.
2. **Create an API token** in Zendesk:
   - Go to **Admin Center → Apps and integrations → Zendesk API**.
   - Click **Settings** and ensure **Token access** is enabled.
   - Click **Add API token**.
   - Name it "Agent Red" and click **Create**.
   - Copy the token — it is only shown once.
3. **Note your Zendesk subdomain** — this is the `yourcompany` part of `yourcompany.zendesk.com`.

### Connecting Zendesk to Agent Red

1. Navigate to **Integrations** in the Agent Red admin console.
2. Enable the **Zendesk** toggle.
3. Enter your Zendesk subdomain, admin email address, and API token.
4. Click **Save** and **Test Connection**.

### What happens when a conversation is escalated

When a conversation is escalated (by AI or manually), Agent Red creates a Zendesk ticket with:

- **Subject:** A summary of the customer's issue
- **Description:** The full conversation transcript
- **Requester:** The customer's email address (if known)
- **Tags:** `agent-red`, the escalation category, and the urgency level
- **Priority:** Mapped from the escalation urgency (High → Urgent, Medium → Normal, Low → Low)

The ticket link is recorded in the Agent Red Inbox so you can track it from either system.

### Zendesk configuration changes

To get the most out of the integration, configure these settings in Zendesk:

- **Create a view** filtered by the `agent-red` tag to see all AI-escalated tickets in one place.
- **Set up an automation** to assign Agent Red tickets to a specific group or agent based on the escalation category tag.
- **Add a trigger** to send an internal notification when a high-priority Agent Red ticket is created.

---

## Mailchimp

| | |
|---|---|
| **Field** | `mailchimp_enabled` |
| **Type** | Toggle (on/off) |
| **Default** | Off |
| **Tier** | Professional and Enterprise |

Sends customer interaction data to Mailchimp, enabling targeted post-conversation email campaigns based on conversation topics and outcomes.

### Prerequisites — setting up your Mailchimp account

1. **Create a Mailchimp account** (if you do not have one) at [mailchimp.com](https://mailchimp.com). A Standard or Premium plan is recommended for automation features.
2. **Generate an API key:**
   - Go to **Account → Extras → API keys**.
   - Click **Create A Key**.
   - Name it "Agent Red" and copy the key.
3. **Note your audience ID:**
   - Go to **Audience → All contacts → Settings → Audience name and defaults**.
   - Copy the **Audience ID** shown at the bottom of the page.
4. **Create tags** in your audience for segmentation (optional but recommended):
   - `agent-red-customer` — for all customers who interacted with Agent Red
   - `escalated` — for customers whose conversations were escalated
   - `resolved` — for customers whose issues were resolved by the AI

### Connecting Mailchimp to Agent Red

1. Navigate to **Integrations** in the Agent Red admin console.
2. Enable the **Mailchimp** toggle.
3. Enter your Mailchimp API key and audience ID.
4. Click **Save** and **Test Connection**.

### What data is sent to Mailchimp

After each conversation ends, Agent Red can add or update the customer in your Mailchimp audience with:

| Field | Description |
|---|---|
| Email address | The customer's email (only if collected or identified) |
| Tags | Conversation topic, outcome (resolved/escalated), product categories discussed |
| Merge fields | Last conversation date, total conversation count |

### Mailchimp campaign ideas

- **Post-purchase follow-up:** Segment customers tagged with product-related conversation topics and send care instructions or upsell emails.
- **Recovery campaigns:** Target customers whose conversations were escalated — send a follow-up email checking on their satisfaction.
- **FAQ awareness:** If many customers ask the same question, send a broadcast email with the answer to reduce future support volume.

---

## Google Analytics

| | |
|---|---|
| **Field** | `google_analytics_enabled` |
| **Type** | Toggle (on/off) |
| **Default** | Off |
| **Tier** | Professional and Enterprise |

Sends conversation events to Google Analytics, enabling you to track widget interactions alongside your existing website analytics.

### Prerequisites — setting up Google Analytics

1. **Create a Google Analytics 4 (GA4) property** (if you do not have one) at [analytics.google.com](https://analytics.google.com).
2. **Get your Measurement ID:**
   - Go to **Admin → Data Streams → Web**.
   - Click your web stream (or create one for your website).
   - Copy the **Measurement ID** (format: `G-XXXXXXXXXX`).
3. **Create a Measurement Protocol API secret** (for server-side events):
   - In the same data stream, scroll to **Measurement Protocol API secrets**.
   - Click **Create** and name it "Agent Red".
   - Copy the secret value.

### Connecting Google Analytics to Agent Red

1. Navigate to **Integrations** in the Agent Red admin console.
2. Enable the **Google Analytics** toggle.
3. Enter your GA4 Measurement ID and API secret.
4. Click **Save** and **Test Connection**.

### Events sent to Google Analytics

Agent Red sends the following custom events:

| Event name | When it fires | Parameters |
|---|---|---|
| `agent_red_conversation_start` | Customer opens the chat widget and sends their first message | `page_type`, `page_url` |
| `agent_red_conversation_end` | Conversation is resolved or archived | `message_count`, `duration_seconds`, `outcome` (resolved/escalated) |
| `agent_red_escalation` | Conversation is escalated to a human | `category`, `urgency` |
| `agent_red_quick_action_click` | Customer clicks a quick action button | `action_label`, `page_type` |

### Google Analytics configuration

To analyze Agent Red data in GA4:

1. **Create a custom report** in GA4 using the `agent_red_` events to track conversation volume, escalation rate, and quick action usage.
2. **Set up a conversion event** for `agent_red_conversation_end` with `outcome = resolved` to measure successful AI resolutions.
3. **Create an audience** of users who had escalated conversations for retargeting or customer satisfaction surveys.

---

## Custom Integration (Enterprise)

| | |
|---|---|
| **Field** | `custom_integration_enabled` |
| **Type** | Toggle (on/off) |
| **Default** | Off |
| **Tier** | Enterprise only |

Enterprise customers can connect Agent Red to custom APIs and data sources. Custom integrations use webhook-based communication — Agent Red sends events to your endpoint and can receive responses.

Contact your account manager to configure a custom integration for your specific use case.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
