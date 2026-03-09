---
sidebar_position: 13
title: Knowledge base management
description: Create, edit, upload, and organize knowledge base articles — best practices for avoiding duplication, resolving conflicts, and optimizing AI response quality.
---

# Knowledge base management

The knowledge base is the single most important factor in the quality of your AI agent's responses. A well-organized knowledge base with clear, non-overlapping articles produces accurate, consistent answers. A messy knowledge base with duplicated or conflicting information produces confused, contradictory answers.

This page covers the operational side of managing your knowledge base — creating articles, uploading documents, organizing content, and avoiding common pitfalls.

![Knowledge base management page showing articles, categories, and status indicators](/img/admin/knowledge-base.png)

:::info
For settings that control how the AI *searches* the knowledge base (retrieval depth, search weights, relevance thresholds), see [Knowledge base configuration](./knowledge-base.md).
:::

## Article structure

Every knowledge base article has four fields:

| Field | Required | Max length | Description |
|---|---|---|---|
| **Title** | Yes | 200 characters | A clear, descriptive headline. The AI uses the title for relevance matching, so write it as a question or topic descriptor. |
| **Content** | Yes | 50,000 characters | The article body. This is what the AI reads to generate answers. |
| **Category** | Yes | Freeform text | An organizational label (e.g., "Shipping", "Returns", "Product Info"). Used for filtering in the admin console and optionally for intent-to-source routing. |
| **Status** | Yes | `draft` / `published` / `archived` | Only `published` articles are searchable by the AI. |

### Writing effective titles

The title is the first thing the hybrid search evaluates. A good title significantly improves retrieval accuracy.

| Poor title | Better title |
|---|---|
| "Returns" | "How to return an item and get a refund" |
| "Shipping" | "Shipping options, costs, and delivery timeframes" |
| "Product care" | "How to clean and maintain leather products" |
| "FAQ #12" | "Do you offer gift wrapping?" |

**Rules:**
- Write the title as a question the customer would ask, or as a descriptive topic phrase.
- Include the key terms a customer would use (e.g., "refund" not just "return").
- Do not use internal codes, numbers, or abbreviations that customers would not recognize.

### Writing effective content

The content field is what the AI reads to construct its answer. The AI does not need marketing language, formatting, or persuasion — it needs clear, factual information that it can rephrase in your brand voice.

**Do:**
```
Returns are accepted within 30 days of delivery. Items must be unworn
with original tags attached. Refunds are issued to the original payment
method within 5-7 business days of receiving the return. Final sale
items marked "No Returns" on the product page are not eligible.
Customers are responsible for return shipping costs unless the item
is defective. To start a return, email returns@yourstore.com with
your order number.
```

**Don't:**
```
🎉 We want you to LOVE your purchase! But if things don't work out,
no worries — we've got you covered with our hassle-free return process!
Simply reach out to our amazing support team and we'll take care of
everything. Easy peasy! 😊
```

The first version gives the AI clear facts it can present in any tone. The second version gives the AI marketing copy that it will awkwardly rephrase, potentially losing the actual policy details.

---

## Creating articles

From the Knowledge Base page in the admin console:

1. Click **Add article**.
2. Fill in the title, content, and category.
3. Set the status to `draft` if you are still working on it, or `published` to make it immediately searchable.
4. Click **Save**.

**What happens after saving:**
- The article is stored in your knowledge base.
- If the status is `published`, the article is automatically embedded (converted to a vector representation) within a few seconds.
- The article becomes searchable in the next conversation that triggers a knowledge retrieval query.

---

## Uploading documents

You can upload files to bulk-create knowledge base articles. Supported formats:

| Format | How it is processed |
|---|---|
| **PDF** | Text extracted page-by-page. Each page becomes a separate article (or multiple articles if the page exceeds the chunk size). |
| **DOCX** | Text extracted with paragraph structure preserved. Headings are used as article titles where possible. |
| **CSV** | Each row becomes an article. The CSV must have `title` and `content` columns. Optional: `category`, `status`. |
| **TXT** | Raw text split into articles by paragraph boundaries. |
| **HTML** | Text extracted, HTML tags stripped. Structure inferred from headings. |

**Upload limits:**
- Maximum file size: 10 MB per file.
- Files are automatically chunked into articles of approximately 400 tokens (about 300 words) each to ensure optimal retrieval performance.

**When to upload vs. create manually:**
- **Upload** when you have existing documentation (policy PDFs, FAQ pages, product manuals) that you want to import quickly.
- **Create manually** when you want precise control over the title, content, and categorization of each article.

**After uploading:** Review the auto-generated articles. Auto-chunking may split content at awkward boundaries or create titles that need refinement. Spending 10 minutes reviewing and editing uploaded articles significantly improves retrieval quality.

---

## Bulk import and export

**Export (CSV):** Downloads all knowledge base articles as a CSV file with columns for title, content, category, and status. Useful for backup, migration, or bulk editing in a spreadsheet.

**Import (CSV):** Upload a CSV file to create multiple articles at once. The CSV must have:
- `title` column (required)
- `content` column (required)
- `category` column (optional, defaults to "General")
- `status` column (optional, defaults to "draft")

---

## Article status lifecycle

```
draft → published → archived
  ↑         ↓          ↓
  ←─────────←──────────←── (can revert to any previous status)
```

| Status | AI searchable? | When to use |
|---|---|---|
| **Draft** | No | Article is being written or reviewed. Not visible to the AI. |
| **Published** | Yes | Article is complete and ready for the AI to use. |
| **Archived** | No | Article is outdated or no longer relevant. Preserved for reference but not searchable. |

**Important:** Archiving an article is reversible. The vector embedding is preserved, so re-publishing an archived article makes it immediately searchable again without re-embedding.

---

## Staleness and freshness

Every knowledge base article has a staleness score (0.0–1.0) that indicates how likely the content is to be outdated. The staleness score is calculated from three factors:

| Factor | Weight | Description |
|---|---|---|
| **Age** | 50% | How long since the article was created or last edited |
| **Embedding drift** | 30% | Whether the content has changed since the last embedding |
| **Verification recency** | 20% | How long since a team member manually verified the article |

**Staleness categories:**

| Score | Category | Badge color | Action |
|---|---|---|---|
| 0.0–0.3 | Fresh | Green | No action needed |
| 0.3–0.6 | Aging | Yellow | Review when convenient |
| 0.6–0.8 | Stale | Orange | Review and update soon |
| 0.8–1.0 | Very stale | Red | Update immediately — may contain outdated information |

**Mark as verified:** If you review an article and confirm the content is still accurate, click **Mark as verified** to reset the verification recency factor. This reduces the staleness score without requiring you to edit the content.

**Automatic re-embedding:** Articles with high staleness scores and content changes (detected via content hash comparison) are automatically re-embedded to ensure the vector representation matches the current text.

---

## Avoiding duplication

Duplication is the most common knowledge base problem and the primary cause of inconsistent AI responses. When two articles cover the same topic with slightly different information, the AI may retrieve both and produce a response that blends them — often incorrectly.

### How to identify duplication

| Symptom | Likely cause |
|---|---|
| AI gives different answers to the same question on different conversations | Two articles cover the same topic with different details |
| AI responses include contradictory information in a single message | Conflicting articles both retrieved for the same query |
| AI cites an outdated policy despite you updating a different article | The old article was not archived when the new one was created |

### Rules to prevent duplication

1. **One topic, one article.** Each article should cover a single, distinct topic. If you find yourself writing about returns in both a "Return Policy" article and a "How to Return Items" article, merge them.

2. **Use the policy fields for policies.** Return, shipping, warranty, and support hours should go in the [Business policies](./business-policies.md) fields, not in knowledge base articles. If you put shipping information in both the policy field and a knowledge base article, you have duplication.

3. **Search before creating.** Before creating a new article, search your existing knowledge base for the topic. The search bar matches against both article titles and content, so you can find existing articles even if you only remember a phrase from the body. If an article already exists, edit it instead of creating a new one.

4. **Archive, don't duplicate.** When a policy changes, update the existing article instead of creating a new one and leaving the old one published. If you must keep both (for audit purposes), archive the old version.

5. **Categories help.** Consistent categorization makes it easier to spot duplicates. If you have three articles in the "Shipping" category, review them to ensure they cover different aspects (general policy, international, express) rather than the same content three ways.

### How the AI handles duplicates

When the hybrid search retrieves multiple articles on the same topic:
- The response generator receives all retrieved articles as context.
- It attempts to synthesize a coherent answer from all sources.
- If the sources conflict, the response generator picks the most specific or most recently updated source — but this behavior is not guaranteed.
- The Critic/Supervisor may flag the response if it detects factual inconsistency.

**The solution is always to fix the knowledge base**, not to hope the AI resolves conflicts correctly.

---

## Resolving conflicting information

If you discover the AI is giving inconsistent answers, follow this process:

1. **Identify the conflicting articles.** Go to the Analytics page and look at the Knowledge Gaps section. Review the conversation where the inconsistency appeared. Click the conversation to see which knowledge base articles were cited (if source citation is enabled) or check the decision trace.

2. **Determine which article is authoritative.** Usually the most recently updated article, or the article in the Business Policies fields, is correct.

3. **Update or archive.** Update the incorrect article to match the authoritative version, or archive it if the authoritative version already covers the content.

4. **Verify with a test conversation.** Ask the question that triggered the inconsistency and confirm the AI now gives a consistent answer.

---

## Organizing with categories

Categories are freeform text labels — you can create any category you want. Consistent categories improve both the admin experience (filtering) and AI performance (when using intent-to-source routing).

**Recommended categories for e-commerce:**

| Category | What goes here |
|---|---|
| `Product Info` | Product features, specifications, comparisons, sizing |
| `Shipping` | Delivery options, timeframes, international, tracking |
| `Returns` | Return policy details, exchange process, refund timeline |
| `Orders` | Order status lookups, cancellation, modification |
| `Payment` | Payment methods, billing issues, gift cards, store credit |
| `Account` | Login issues, password reset, account settings |
| `Promotions` | Current sales, discount codes, loyalty rewards |
| `Company` | About us, contact information, store locations, careers |

**Tips:**
- Use 5–10 categories maximum. More than that becomes difficult to maintain.
- Avoid overlapping categories. "Shipping & Returns" is a category that invites mixing topics — use separate "Shipping" and "Returns" categories.
- Avoid hyper-specific categories with only one article. A category with a single article provides no organizational value.

---

## Optimizing for retrieval quality

### Short, focused articles outperform long ones

The retrieval system works best when each article covers a single, well-defined topic. A 5,000-word article covering your entire return, exchange, and warranty policy will perform worse than three separate articles, one for each topic.

**Why:** The vector embedding represents the entire article as a single point in semantic space. A long article covering multiple topics will be a mediocre match for any specific question, while a focused article on exactly that topic will be a strong match.

### Use the customer's language

Write articles using the words and phrases your customers use, not just your internal terminology.

| Internal term | Customer term | Include both |
|---|---|---|
| "Restocking fee" | "Return fee" | Mention both in the article |
| "Lead time" | "How long until it ships" | Use the customer phrasing in the title |
| "SKU" | Product name or description | Use the product name |
| "RMA process" | "How to send it back" | Use the customer phrasing |

### Keep articles current

Outdated knowledge base articles are worse than no articles at all. An outdated article can cause the AI to give confidently wrong answers.

**Maintenance schedule:**
- **Monthly:** Review all articles in the "Aging" or "Stale" staleness category.
- **When policies change:** Update the relevant knowledge base article and Business Policy field the same day.
- **Seasonally:** Archive or update seasonal content (holiday shipping cutoffs, seasonal promotions).

### Optimization workflow

Follow this process to systematically improve your knowledge base over time:

1. **Start with your top 20 questions.** Check your email inbox, help desk, or social media for the 20 most common customer questions. Create one article for each.

2. **Run a conflict scan.** From the Knowledge Base page, click the **Conflict scan** button. The scan checks for duplicate, overlapping, or contradictory entries and reports issues grouped by severity (High, Medium, Low). Each issue shows similarity percentages and a suggested resolution. Fix all High-severity conflicts immediately.

3. **Review the analytics.** After your first week, check the Dashboard for knowledge gaps — questions the AI could not answer confidently. Create articles to cover those gaps.

4. **Test article quality.** Open the chat widget and ask the exact questions your articles should answer. If the AI gives a vague or incomplete response, the article likely needs clearer language, a better title, or both.

5. **Use the staleness indicators.** Articles with orange or red freshness badges need review. Click **Mark as verified** if the content is still accurate, or edit the article if information has changed.

6. **Split long articles.** If an article covers more than one distinct topic (e.g., returns AND exchanges AND warranties), split it into separate articles. Focused articles produce better retrieval scores.

7. **Iterate monthly.** Review escalated conversations for patterns. If customers are frequently escalated for the same topic, the knowledge base is missing coverage. Add or improve articles for that topic.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
