---
sidebar_position: 4
title: Response style
description: Control how verbose, formal, and expressive the AI agent's responses are, and set a fallback message for when no answer is available.
---

# Response style

These settings fine-tune how the AI structures and phrases its responses, independently of the brand voice.

## Response length

| | |
|---|---|
| **Field** | `response_length` |
| **Type** | Dropdown |
| **Options** | `concise`, `standard`, `detailed` |
| **Default** | `standard` |
| **Affects** | Response generator |

Controls how much detail the AI includes in each response.

| Setting | Typical length | Best for |
|---|---|---|
| **Concise** | 1–2 sentences | Quick answers, order status, simple FAQs |
| **Standard** | 2–4 sentences | General customer service, product questions |
| **Detailed** | 4–8 sentences | Technical products, complex policies, educational content |

**Guidance:**
- Start with `standard`. Review your first 50 conversations and look for patterns — if customers are asking follow-up questions because the initial answer was too brief, switch to `detailed`. If customers stop reading mid-response, switch to `concise`.
- The AI adapts within the constraint. A simple "What are your hours?" question will get a shorter response even on `detailed` because there is not much to say. Complex questions about return eligibility will get longer responses even on `concise` because the AI needs to cover multiple conditions.

---

## Formality level

| | |
|---|---|
| **Field** | `formality_level` |
| **Type** | Dropdown |
| **Options** | `casual`, `balanced`, `formal` |
| **Default** | `balanced` |
| **Affects** | Response generator |

Controls the register and structure of responses.

| Setting | Characteristics |
|---|---|
| **Casual** | Contractions ("I'll", "can't"), conversational flow, shorter sentences, first-person |
| **Balanced** | Mix of contractions and full forms, moderate sentence length, professional but approachable |
| **Formal** | No contractions, complete sentences, structured paragraphs, third-person references to your brand |

**How it interacts with brand voice:**
The formality level controls structural decisions (contractions, sentence structure, paragraph breaks). The brand voice controls personality (warmth, humor, enthusiasm). You can have a `formal` formality with a `warm and empathetic` voice — the result is structured, polished language that still conveys care.

---

## Emoji usage

| | |
|---|---|
| **Field** | `emoji_usage` |
| **Type** | Dropdown |
| **Options** | `none`, `minimal`, `moderate` |
| **Default** | `minimal` |
| **Affects** | Response generator |

Controls how often the AI uses emoji in responses.

| Setting | Behavior |
|---|---|
| **None** | No emoji in any response. Use this for B2B, legal, financial, or medical contexts. |
| **Minimal** | Occasional emoji for emphasis (1–2 per conversation). Default and appropriate for most stores. |
| **Moderate** | Regular emoji use to add personality. Works well for lifestyle brands, fashion, food, and entertainment. |

**Note:** Even with `none`, the AI may still use text-based emoticons or emphasis markers if your brand voice strongly implies expressiveness. If you need strict emoji prohibition, add a note in [Custom instructions](./custom-instructions.md).

---

## Fallback message

| | |
|---|---|
| **Field** | `fallback_message` |
| **Type** | Multi-line text (up to 500 characters) |
| **Default** | None (AI generates a fallback) |
| **Required** | No |
| **Affects** | Response generator |

The message the AI uses when it cannot find a relevant answer in your knowledge base.

**When this triggers:**
- The customer asks about something not covered by your knowledge base articles, policies, or product catalog.
- The knowledge retrieval agent returns no results above the minimum relevance threshold (see [Knowledge base](./knowledge-base.md#minimum-relevance-score)).

**If you set a custom fallback:**
The message is delivered verbatim. Example: *"I don't have information about that yet. Let me connect you with our support team — please email support@yourstore.com or call (555) 123-4567."*

**If you leave it blank:**
The AI generates a contextual fallback that acknowledges the question, explains it does not have the information, and offers to help with something else. This tends to sound more natural but is less predictable.

**Tips:**
- Include a specific action the customer can take (email, phone, link to help center).
- Keep it honest — do not promise the AI will "look into it" because it will not remember to do so.
- If you set up escalation rules (see [Escalation rules](./escalation-rules.md)), the AI may escalate rather than deliver the fallback, depending on your configuration.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
