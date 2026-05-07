---
sidebar_position: 1
title: Billable Conversation Definition
description: How Agent Red defines, counts, and bills conversations — the binding reference for usage metering.
---

# Billable Conversation Definition

This page defines what counts as a billable conversation on Agent Red. It is the binding reference document for usage metering and billing disputes.

**Version:** 1.0.0
**Effective date:** Aligned with your Terms of Service effective date.

---

## What is a conversation?

A **conversation** is a single customer interaction session with Agent Red's AI pipeline. Each conversation receives a unique `conversation_id` and is processed through the six-agent pipeline (intent classification, knowledge retrieval, response generation, escalation detection, analytics, and content safety).

One conversation = one billable unit, regardless of how many messages are exchanged within it.

---

## When does a conversation start?

A conversation starts when the **first customer message** is received and a new `conversation_id` is assigned by the system.

---

## When does a conversation end?

A conversation ends when any of the following occur:

| Condition | Description |
|-----------|-------------|
| **Idle timeout** | No messages received for 30 minutes |
| **Customer ends** | The customer explicitly closes the conversation |
| **Escalated** | The conversation is escalated to a human agent |
| **Turn limit** | 50 conversation turns (customer-AI message pairs) are reached |

If a customer returns after the 30-minute idle timeout, a new conversation is started with a new `conversation_id`.

---

## What is NOT billable?

The following interactions are never counted as billable conversations:

| Interaction type | How it's identified |
|-----------------|-------------------|
| **Test conversations** | `conversation_id` starts with `test_` |
| **Admin interactions** | `conversation_id` starts with `admin_` |
| **Health checks** | `conversation_id` starts with `health_` |
| **System operations** | `conversation_id` starts with `system_` |
| **Pre-response errors** | A platform error occurs before the first AI response is delivered |

---

## How are conversations consumed?

Each billable conversation is consumed in a specific order (three-tier consumption):

```
1. Included allowance (free with your subscription tier)
       ↓ (exhausted)
2. Pack balance (pre-purchased conversation packs, oldest-first)
       ↓ (exhausted)
3. Overage (billed per-conversation via your payment method)
```

### Included allowance

Every subscription tier includes a monthly conversation allowance:

| Tier | Included conversations/month |
|------|------|
| Starter | 1,000 |
| Professional | 5,000 |
| Enterprise | 20,000 |

The included allowance resets at the start of each billing period. Unused conversations do not roll over.

### Conversation packs

Pre-purchased conversation packs are consumed after the included allowance is exhausted. Packs are consumed FIFO (first-in, first-out) — the oldest pack is drawn from first. Packs expire 90 days after purchase.

| Pack size | Price | Effective rate |
|-----------|-------|----------------|
| 1,000 | $29 | $0.029/conv |
| 5,000 | $99 | $0.020/conv |
| 20,000 | $249 | $0.012/conv |

### Overage

Conversations beyond the included allowance and pack balance are billed as overage at your tier's rate:

| Tier | Overage rate |
|------|-------------|
| Starter | $0.04/conv |
| Professional | $0.025/conv |
| Enterprise | $0.015/conv |

---

## Proactive alerts

Agent Red sends alerts before you incur unexpected charges:

| Alert | Trigger |
|-------|---------|
| **80% warning** | 80% of included allowance consumed |
| **100% notice** | Included allowance fully consumed |
| **Pack balance low** | Less than 10% of pack balance remaining |
| **Volume spike** | Daily volume exceeds 2x your 7-day trailing average |

Alerts are delivered to the merchant dashboard and via the notification channel configured in your account settings. Each alert fires once per billing period.

---

## Transparency and auditing

### Real-time dashboard

Your merchant dashboard shows real-time usage including: conversations used, remaining allowance, pack balance, overage count, and estimated overage cost.

### Per-conversation audit trail

Every billable conversation is recorded with: conversation ID, status, customer identifier, message count, turn count, timestamps, pipeline stages invoked, model used, and content safety pass/fail. This data is accessible via the dashboard and exportable as CSV.

### Daily reconciliation

We perform daily automated reconciliation between our internal conversation counter and the billing system. Any discrepancy exceeding 5% is flagged for manual review.

### Dispute resolution

If you believe a conversation was incorrectly billed, contact support@remakerdigital.com with the conversation ID. We will review the audit trail and resolve the dispute within 10 business days.

---

## Billing examples

**Example 1 — Within allowance:**
Starter tier merchant uses 800 conversations in a month. All 800 are covered by the 1,000 included allowance. No additional charges.

**Example 2 — Pack consumption:**
Starter tier merchant uses 1,200 conversations with a 1,000 pack purchased. First 1,000 from included allowance, next 200 from the pack. No overage charges.

**Example 3 — Overage:**
Starter tier merchant uses 1,500 conversations with no packs. First 1,000 from included allowance, remaining 500 billed as overage at $0.04 each = $20.00 overage charge.

---

*This document is published as part of Agent Red's commitment to transparent, predictable billing. For billing inquiries, contact support@remakerdigital.com.*

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
