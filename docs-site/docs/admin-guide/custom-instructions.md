---
sidebar_position: 12
title: Custom instructions
description: Advanced — inject specific behavioral rules directly into the AI's system prompt. Use with care.
---

# Custom instructions

| | |
|---|---|
| **Field** | `custom_instructions` |
| **Type** | Multi-line text (up to 4,000 characters) |
| **Default** | None |
| **Required** | No |
| **Affects** | Response generator |

Custom instructions are injected directly into the response generator's system prompt, in a clearly delimited section. This is the most powerful configuration option — and the most likely to cause problems if used carelessly.

:::caution
Custom instructions are sandboxed with a disclaimer that platform safety rules take precedence. However, poorly written instructions can still degrade response quality. Read this entire page before using this feature.
:::

## What custom instructions are for

Use custom instructions for specific behavioral rules that cannot be expressed through the other configuration options. Examples:

**Good uses:**
```
Never recommend competitor products by name.

When a customer asks about our premium membership, mention the 30-day
free trial before discussing pricing.

If a customer mentions they are a returning customer, thank them for
their loyalty.

Always suggest the customer check our size guide before purchasing
clothing items.
```

**Bad uses (avoid these):**
```
❌ Be friendly and helpful.
   → Use the brand_voice field instead.

❌ Respond in Spanish.
   → Use the primary_language field instead.

❌ Keep responses short.
   → Use the response_length field instead.

❌ You are a helpful AI assistant for our store.
   → This is redundant — the system prompt already establishes this context.
```

## How to write effective custom instructions

### Be specific and actionable

The AI follows concrete rules better than abstract guidance.

| Vague (bad) | Specific (good) |
|---|---|
| "Be careful about returns" | "When a customer asks about returns, always confirm the return window (30 days) and mention that the item must be unworn with tags attached" |
| "Upsell when appropriate" | "When a customer is looking at a single product, suggest the matching accessory if one exists in our catalog" |
| "Handle complaints well" | "When a customer expresses frustration, acknowledge their feelings before providing a solution. Use phrases like 'I understand that's frustrating' or 'I'm sorry you're dealing with that'" |

### Use positive language

Tell the AI what to do, not just what not to do.

| Negative only (less effective) | Positive + negative (more effective) |
|---|---|
| "Don't discuss pricing of competitors" | "Focus on our product's value when answering pricing questions. Do not mention competitor pricing." |
| "Don't make promises about delivery dates" | "Provide estimated delivery ranges based on the shipping information policy. Do not commit to specific dates." |

### Keep it concise

Each instruction should be 1–2 sentences. The more text you add, the more the AI has to balance competing priorities. Fewer, clearer rules produce better results than a long list of detailed instructions.

### Test after changing

After updating custom instructions, run 5–10 test conversations that exercise the new rules. Check:
1. Does the AI follow the instruction?
2. Did the instruction break anything else? (e.g., a rule about returns accidentally affecting exchange discussions)
3. Is the AI interpreting the instruction literally in ways you did not intend?

## What custom instructions cannot do

- **Override safety rules.** The Critic/Supervisor agent validates every response before delivery. Custom instructions cannot disable this.
- **Access external systems.** You cannot instruct the AI to call APIs, send emails, or perform actions outside the conversation.
- **Change the AI's fundamental capabilities.** You cannot make the AI perform tasks it is not designed for (image generation, code execution, etc.).
- **Override the platform base prompt.** The core identity, safety guardrails, and pipeline behavior are immutable.

## Interaction with other settings

Custom instructions are applied *after* all other configuration (brand voice, formality, response length, policies). If a custom instruction contradicts another setting, the instruction wins for the specific behavior it describes, but the other settings continue to apply to everything else.

**Example:** If your response length is `concise` but your custom instruction says "When answering sizing questions, provide the full size chart," the AI will give detailed sizing answers but keep other responses concise.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
