---
sidebar_position: 2
title: Brand and tone
description: Configure your brand name, voice, greeting, and farewell to shape how the AI agent communicates with your customers.
---

# Brand and tone

These settings define your AI agent's identity and communication style. Every response the agent generates is shaped by these values — they are injected into the system prompt that guides the response generator.

:::info Agent identity section
These fields are located in the **Agent identity** section of the Configuration page, which combines brand & persona settings with [custom instructions](./custom-instructions.md).
:::

![Agent configuration page showing saved configurations, brand & persona settings, and escalation categories](/img/admin/agent-configuration.png)

## Brand name

| | |
|---|---|
| **Field** | `brand_name` |
| **Type** | Text (1–100 characters) |
| **Default** | `My Store` |
| **Required** | Yes |
| **Affects** | Intent classifier, knowledge retrieval, response generator, escalation handler, analytics |

Your brand name appears in greetings, sign-offs, and whenever the AI references your business. It is injected into the system prompt for five of the six agents, so it influences classification accuracy (the intent classifier knows it is acting on behalf of your brand), search relevance, and response phrasing.

**How to set it:**
- Use the exact name your customers recognize — the same name that appears on your storefront header.
- Do not include legal suffixes (LLC, Inc.) unless your customers commonly use them.
- If your business has a short name and a long name (e.g., "ACME" vs. "ACME Outdoor Equipment Co."), use the short version. The AI will sound more natural.

**What happens if you change it:**
Changing the brand name takes effect on new conversations immediately. In-progress conversations will use the new name from the next message onward — this can feel abrupt to a customer mid-conversation, so change it during a low-traffic period if possible.

---

## Brand voice

| | |
|---|---|
| **Field** | `brand_voice` |
| **Type** | Text (up to 200 characters) |
| **Default** | `friendly and helpful` |
| **Required** | Yes (mandatory for activation) |
| **Affects** | Response generator |

Brand voice is required for activation. If it is empty when you attempt to activate, the activation dialog will show a hard error and the **Activate now** button will be disabled. This was promoted from an optional warning to a mandatory requirement because the brand voice has a significant impact on response quality — without it, the AI falls back to a generic tone that may not represent your brand.

This is a short personality description that controls the AI's communication style — word choice, sentence length, level of warmth, and overall tone. The value is inserted directly into the response generator's system prompt.

**Effective examples:**

| Voice description | Result |
|---|---|
| `friendly and casual` | Uses contractions, informal phrasing, conversational structure |
| `professional and concise` | Shorter sentences, formal register, no emoji |
| `warm and empathetic` | Acknowledges emotions, uses softer language, offers reassurance |
| `technical and precise` | Uses exact terminology, provides specific details, minimal filler |
| `enthusiastic and playful` | Upbeat tone, exclamation points, brand personality forward |

**How to write a good brand voice:**
- Use 2–4 adjectives separated by "and" or commas.
- Describe how you want the agent to *sound*, not what you want it to *do*.
- Test different values by running a few conversations and reviewing the tone.
- The voice description is advisory — the AI also follows formality, emoji, and response length settings (see [Response style](./response-style.md)), which provide more granular control.

**What happens if you leave it blank:**
The AI defaults to `friendly and helpful`, which produces neutral, polite responses suitable for most e-commerce stores.

---

## Greeting message

| | |
|---|---|
| **Field** | `greeting_message` |
| **Type** | Multi-line text (up to 500 characters) |
| **Default** | None (AI generates a greeting) |
| **Required** | No |
| **Affects** | Response generator |

An optional fixed message sent as the first response when a customer starts a conversation. If set, this message is delivered verbatim — the AI does not modify or rephrase it.

**When to use a fixed greeting:**
- You have a specific promotional message (e.g., "Free shipping this week on orders over $50!").
- Your brand requires a legally mandated disclosure at the start of conversations.
- You want an identical experience across every conversation.

**When to leave it blank:**
- You want the AI to generate a contextual greeting that varies based on the time of day, the page the customer is on, or the customer's history (if Persistent Customer Memory is enabled).
- A fixed greeting can feel robotic if every conversation starts the same way.

**Tips:**
- Keep it under 2 sentences. Long greetings feel like they were not written by a human.
- Do not include questions in the greeting — the customer already has a question; asking them another one adds friction.

---

## Farewell message

| | |
|---|---|
| **Field** | `farewell_message` |
| **Type** | Multi-line text (up to 500 characters) |
| **Default** | None (AI generates a farewell) |
| **Required** | No |
| **Affects** | Response generator |

An optional fixed message sent when a conversation is resolved. Like the greeting, it is delivered verbatim if set.

**When to use a fixed farewell:**
- You want to include a consistent call-to-action (e.g., "Leave us a review!").
- Your brand has a signature sign-off.

**When to leave it blank:**
The AI generates a contextual farewell based on the conversation content and your brand voice. This typically sounds more natural than a fixed message.

---

## How these settings interact

The brand and tone settings form the foundation of the AI's personality. Other settings refine it:

```
Brand name + Brand voice → Base personality
  + Formality level → Register (casual/formal)
  + Emoji usage → Expressiveness
  + Response length → Verbosity
  + Custom instructions → Specific behavioral rules
```

If your brand voice says "casual" but your formality level is set to "formal," the formality level wins for structural decisions (contractions, sentence structure) while the brand voice influences word choice and warmth. When in doubt, make them consistent.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
