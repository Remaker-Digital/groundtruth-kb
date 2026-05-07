---
sidebar_position: 5
title: Knowledge base configuration
description: Tune how the AI searches your knowledge base — retrieval depth, hybrid search weighting, relevance thresholds, source citation, and intent routing.
---

# Knowledge base configuration

These settings control how the AI searches your knowledge base when answering customer questions. The knowledge retrieval agent uses a hybrid search system combining semantic vector search (meaning-based) and BM25 keyword matching (exact term matching). These settings let you tune the balance.

:::info
This page covers search *configuration*. For guidance on creating, editing, and organizing knowledge base articles, see [Knowledge base management](./knowledge-base-management.md).
:::

## Knowledge scope

| | |
|---|---|
| **Field** | `knowledge_scope` |
| **Type** | Dropdown |
| **Options** | `products_only`, `products_and_faqs`, `full` |
| **Default** | `full` |
| **Affects** | Knowledge retrieval |

Controls which types of knowledge the AI can search.

| Setting | What the AI can access |
|---|---|
| **Products only** | Product catalog from Shopify. No FAQ entries or policy documents. |
| **Products and FAQs** | Product catalog plus your FAQ entries. No policy documents. |
| **Full** | Everything: products, FAQs, and policy documents. |

**When to restrict scope:**
- If you have a dedicated support team handling policy questions and want the AI to only answer product questions, use `products_only`.
- Most stores should use `full`. Restricting scope increases the chance the AI triggers the fallback message or escalates unnecessarily.

---

## Results to retrieve (top_k)

| | |
|---|---|
| **Field** | `retrieval_top_k` |
| **Type** | Number (1–20) |
| **Default** | `5` |
| **Affects** | Knowledge retrieval, response generator |

How many knowledge base results the retrieval agent passes to the response generator. Higher values give the response generator more context to work with but increase latency and token consumption.

| Value | Trade-off |
|---|---|
| **1–3** | Fastest responses. Risk: may miss relevant context if the best answer is split across multiple articles. |
| **4–6** | Good balance for most stores. The response generator has enough context without being overwhelmed. |
| **7–10** | Use for stores with large, overlapping knowledge bases where the answer may come from combining multiple sources. |
| **11–20** | Rarely needed. Only for very large catalogs (10,000+ products) or highly specialized domains. Increases latency. |

**Recommendation:** Start with `5`. If you notice the AI missing information that exists in your knowledge base, increase to `7–8`. If responses are slow, decrease to `3`.

---

## Semantic search weight

| | |
|---|---|
| **Field** | `retrieval_vector_weight` |
| **Type** | Slider (0.0–1.0) |
| **Default** | `0.7` |
| **Affects** | Knowledge retrieval |

The weight given to semantic (vector) search results when combining with keyword search results. Semantic search finds articles based on *meaning* — a customer asking "Can I send this back?" will match an article titled "Return Policy" even though no words overlap.

- **Higher values (0.7–1.0):** Prioritize meaning-based matching. Better for natural language questions where exact keywords may not appear in the knowledge base.
- **Lower values (0.0–0.3):** Prioritize exact keyword matching. Better for stores where customers use specific product names, SKU numbers, or technical terms.

**The keyword weight is the complement:** If semantic weight is 0.7, keyword weight is automatically 0.3. The two always sum to 1.0.

---

## Keyword match weight

| | |
|---|---|
| **Field** | `retrieval_bm25_weight` |
| **Type** | Slider (0.0–1.0) |
| **Default** | `0.3` |
| **Affects** | Knowledge retrieval |

The weight given to BM25 keyword search results. BM25 finds articles based on *exact term matching* — it rewards articles that contain the same words the customer used, especially rare words.

**When to increase keyword weight:**
- Your knowledge base uses specific product names, model numbers, or technical terms that customers type exactly.
- Your FAQ entries use the same phrasing customers use.

**When to decrease keyword weight:**
- Customers ask questions in natural language that does not match your article wording.
- Your knowledge base is written in a different register than your customers use (e.g., formal policy language vs. casual customer questions).

---

## Minimum relevance score

| | |
|---|---|
| **Field** | `retrieval_min_score` |
| **Type** | Slider (0.0–1.0) |
| **Default** | `0.1` |
| **Affects** | Knowledge retrieval |

The minimum combined relevance score a knowledge base result must have to be included in the context sent to the response generator. Results below this threshold are filtered out.

**How scoring works:**
Each knowledge base result gets a combined score from the hybrid search (semantic + keyword, weighted by the settings above). Scores are normalized to a 0–1 range using Reciprocal Rank Fusion (RRF).

| Threshold | Behavior |
|---|---|
| **0.0–0.1** | Very permissive. Almost all results pass. May include loosely relevant articles. |
| **0.2–0.4** | Moderate filtering. Good balance of recall and precision. |
| **0.5–0.7** | Strict. Only highly relevant results pass. Risk: the AI may not find context for niche questions. |
| **0.8–1.0** | Very strict. Only near-exact matches. Most stores should not use this. |

**Recommendation:** Start with `0.1` (the default). If the AI is frequently citing irrelevant articles, increase to `0.2–0.3`. If the AI cannot find answers that exist in your knowledge base, decrease to `0.05`.

:::caution
Setting this too high is a common mistake. A threshold of 0.5 will filter out many valid results, especially for conversational queries where the customer's phrasing does not closely match your article text.
:::

---

## Cite sources in response

| | |
|---|---|
| **Field** | `cite_sources_in_response` |
| **Type** | Toggle (on/off) |
| **Default** | Off |
| **Affects** | Response generator |

When enabled, the AI appends the titles of the knowledge base articles it used to generate the response. This appears at the end of the message, formatted as a source list.

**Example with citation enabled:**
> Your order typically ships within 2 business days. Standard delivery takes 5–7 business days, and express delivery takes 2–3 business days.
>
> *Sources: Shipping Policy, Delivery Timeframes*

**When to enable:**
- You want customers to see which policies or articles informed the answer (transparency).
- Your support team reviews conversations and wants to quickly verify which knowledge base articles were used.

**When to leave it off:**
- Citations can make responses feel less conversational and more "robotic." Most consumer-facing stores prefer a natural conversation flow without citations.

---

## Intent-to-source routing

| | |
|---|---|
| **Field** | `intent_source_mapping` |
| **Type** | JSON object |
| **Default** | None (all intents search all sources) |
| **Required** | No |
| **Tier** | Professional and Enterprise |
| **Affects** | Knowledge retrieval |

Maps specific customer intents to specific knowledge base source types, so the retrieval agent only searches relevant sources for each type of question.

**Example configuration:**
```json
{
  "order_status": ["shopify_order"],
  "return_request": ["policy"],
  "product_question": ["product", "faq"],
  "shipping_inquiry": ["policy", "faq"],
  "complaint": ["policy"]
}
```

**How it works:**
1. The intent classifier determines the customer's intent (e.g., `product_question`).
2. The knowledge retrieval agent checks if there is a mapping for that intent.
3. If a mapping exists, the retrieval agent only searches the specified source types.
4. If no mapping exists, it searches all sources (default behavior).

**When to use this:**
- You have a large knowledge base (100+ articles) and want to speed up retrieval by narrowing the search space.
- You want to prevent the AI from citing shipping policies when answering product questions, or vice versa.

**When to skip this:**
- Most stores with fewer than 100 articles do not need intent routing. The hybrid search is accurate enough without it.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
