---
sidebar_position: 3
title: Languages
description: Set the primary language your AI agent uses and enable additional languages for multilingual support.
---

# Languages

These settings control which languages the AI agent communicates in and whether it automatically detects the customer's language.

## Primary language

| | |
|---|---|
| **Field** | `primary_language` |
| **Type** | Dropdown (language code) |
| **Default** | `en` (English) |
| **Required** | Yes |
| **Affects** | Intent classifier, response generator, escalation handler |

The main language for AI responses. The intent classifier uses this to optimize its accuracy for your primary customer base, and the response generator defaults to this language unless the customer writes in a different supported language.

**Primary language:** English (`en`) is the only supported primary language at this time.

**Language availability:**

| Language | Status |
|----------|--------|
| English (`en`) | Fully supported (primary) |

**What happens when you change it:**
- New conversations immediately use the new primary language.
- The intent classifier re-optimizes for the new language's patterns.
- If you have FAQ entries written in the old language, they still work — the knowledge retrieval agent uses semantic search, which is language-aware. However, responses will sound more natural if your knowledge base content matches the primary language.

---

## Additional languages

| | |
|---|---|
| **Field** | `additional_languages` |
| **Type** | Multi-select (up to 10 languages) |
| **Default** | None |
| **Required** | No |
| **Requires** | Multi-Language Pack add-on ($99/month) |
| **Affects** | Intent classifier, response generator, escalation handler |

Enables the AI to respond in languages beyond the primary. When a customer writes in one of the additional languages, the AI detects it and responds in that language.

**How language detection works:**
1. The intent classifier analyzes the customer's message.
2. If the message is in one of the configured languages (primary or additional), the response generator uses that language.
3. If auto-detect is enabled and the language is not in the configured list, the AI falls back to the primary language.

**Tips:**
- Only add languages you actually serve customers in. Adding languages you do not support in your knowledge base will produce lower-quality responses because the AI has less reference material.
- If your knowledge base articles are in English but you add Spanish as an additional language, the AI will translate on the fly. This works well for simple answers but can lose nuance on complex policy explanations. For best results, add FAQ entries in each supported language.

---

## Auto-detect language

| | |
|---|---|
| **Field** | `auto_detect_language` |
| **Type** | Toggle (on/off) |
| **Default** | On |
| **Affects** | Intent classifier, response generator |

When enabled, the AI automatically detects what language the customer is writing in and responds accordingly (if that language is in the primary or additional languages list).

**When to turn it off:**
- Your store operates in a single language and you want the AI to always respond in that language, even if a customer writes in another language. This avoids confusion if the AI misidentifies a language from a short or ambiguous message.
- You serve a bilingual market (e.g., English and French in Canada) and want customers to explicitly select their language rather than relying on detection.

**When to leave it on:**
- Most stores should leave this enabled. It provides a better experience for multilingual customers without requiring them to select a language.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
