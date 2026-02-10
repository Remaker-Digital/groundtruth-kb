---
sidebar_position: 6
title: Business policies
description: Enter your return, shipping, warranty, and support policies so the AI agent can answer policy questions accurately.
---

# Business policies

These text fields provide the AI agent with your business-specific policies. When a customer asks about returns, shipping, warranties, or support availability, the response generator uses these fields as authoritative reference material.

## How policies are used

Policy text is stored in your knowledge base as a special source type (`policy`). The knowledge retrieval agent searches these entries alongside your FAQ articles and product catalog. When a policy field matches a customer query, the response generator uses the policy text to construct an accurate answer.

**All policy fields share these properties:**

| | |
|---|---|
| **Type** | Multi-line text (up to 2,000 characters each) |
| **Required** | No |
| **Affects** | Knowledge retrieval, response generator |

---

## Return policy

Your refund and return terms. The AI references this when customers ask about returning items, requesting refunds, exchange eligibility, or restocking fees.

**What to include:**
- Return window (e.g., 30 days from delivery)
- Condition requirements (unworn, tags attached, original packaging)
- Refund method (original payment, store credit, exchange)
- Any exclusions (final sale items, personalized products)
- Who pays return shipping
- How long refunds take to process

**Example:**
```
Returns accepted within 30 days of delivery. Items must be unworn with
tags attached. Refunds issued to original payment method within 5-7
business days of receiving the return. Final sale items are not eligible
for return. Customer pays return shipping unless the item is defective.
```

**Tip:** Write your policy as a set of clear, factual statements. Avoid marketing language. The AI will rephrase these facts in your brand voice when responding to customers — you do not need to write the policy in a conversational tone.

---

## Shipping information

Your shipping options, costs, and delivery timeframes. The AI references this when customers ask about delivery times, shipping costs, tracking, or international availability.

**What to include:**
- Available shipping methods and costs
- Delivery timeframes by region
- Free shipping thresholds (if any)
- International shipping availability
- Tracking information (how and when it is sent)
- Handling time before shipment

---

## Warranty information

Your product warranty terms. The AI references this when customers ask about defective products, warranty claims, coverage duration, or repair/replacement options.

**What to include:**
- Warranty duration
- What is covered (and what is not)
- How to file a warranty claim
- Repair vs. replacement policy
- Contact information for warranty claims

---

## Support hours

Your human support team's business hours. The AI uses this to inform customers when human agents are available and to set expectations about response times for escalated issues.

| | |
|---|---|
| **Type** | Text (up to 500 characters) |
| **Default** | None |

**Examples:**
- `Monday through Friday, 9 AM to 5 PM Eastern Time`
- `24/7 via chat. Phone support: Mon-Fri 8am-8pm PST`
- `Business days only. Response within 24 hours.`

**Why this matters:** When the AI escalates a conversation to a human agent outside business hours, it can tell the customer when to expect a response instead of leaving them waiting.

---

## Additional policies

A catch-all field for any business rules not covered above — loyalty programs, price matching, gift cards, custom orders, age verification, or anything else the AI should know.

**Tips for writing effective policy text:**
- One policy per paragraph. Do not mix return and shipping rules in the same block.
- Use definitive language: "We do" / "We do not" rather than "We may" / "We might." Ambiguity in your policy text leads to ambiguity in AI responses.
- If a policy has exceptions, list them explicitly.

---

## Avoiding conflicts between policies and knowledge base articles

A common mistake is writing the same policy information in both the policy fields and in separate knowledge base articles. This creates a risk of conflicting information if one is updated and the other is not.

**Best practice:**
- Use the policy fields for canonical policy text. This is the authoritative source.
- Knowledge base articles should reference or supplement policies, not duplicate them.
- If you have a detailed shipping FAQ ("How long does shipping take to Hawaii?"), put that in a knowledge base article and put the general shipping policy in the Shipping information field.
- The AI will combine both sources when answering — the policy provides the rules, and the FAQ article provides the specific detail.

See [Knowledge base management — Avoiding duplication](./knowledge-base-management.md#avoiding-duplication) for more guidance.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
