---
sidebar_position: 14
title: Conflict and duplication scanner
description: Scan your knowledge base for duplicate articles, conflicting information, and topical overlaps — with resolution guidance for each issue.
---

# Conflict and duplication scanner

As your knowledge base grows, duplicate and conflicting articles can slip in unnoticed — especially when multiple team members create content or when documents are imported from external sources. The conflict scanner identifies these issues so you can resolve them before they affect customer-facing answers.

## Why it matters

When the AI retrieves knowledge to answer a customer question, it pulls the most relevant articles from your knowledge base. If two articles cover the same topic with different details, the AI may:

- Give **inconsistent answers** depending on which article it retrieves first
- **Blend contradictory information** into a single response (e.g., "returns are accepted within 14-30 days")
- Waste the **retrieval budget** on redundant content, pushing out other relevant articles

A clean knowledge base directly improves answer quality.

## Running a scan

1. Open **Knowledge Base** in the admin console
2. Click **Scan for conflicts** in the toolbar
3. Wait for the scan to complete (typically a few seconds)
4. Review the results panel that appears below the toolbar

The scanner examines every active article in your knowledge base. Results are cached for five minutes — clicking "Scan" again within that window returns the cached result instantly. Click **Re-scan** to force a fresh analysis.

## Understanding the results

Each detected issue is assigned a **severity** and **conflict type**.

### Severity levels

| Severity | Meaning | Action |
|----------|---------|--------|
| **High** | Near-duplicate content or directly conflicting facts | Resolve before it affects customers |
| **Medium** | Topical overlap that may be intentional | Review to confirm it's intentional |
| **Low** | Similar titles but different content | Consider renaming for clarity |

### Conflict types

#### Near-duplicate (high severity)

Two articles contain nearly identical content. This usually happens when:

- The same article was uploaded twice
- A document import created overlapping chunks
- An article was copied and slightly edited

**Resolution:** Merge the best parts into a single article and archive or delete the other.

#### Conflicting (high severity)

Two articles cover the same topic but contain different factual claims. The scanner highlights specific contradictions it finds — for example, different return windows, prices, or contact emails.

**Resolution:** Determine which article is authoritative (usually the most recently updated one), then update the incorrect article or archive it.

#### Topical overlap (medium severity)

Two articles cover similar topics. This may be intentional — for example, a general shipping policy and a separate international shipping policy. Or it may indicate content that should be consolidated.

**Resolution:** If both articles serve a distinct purpose, no action is needed. If they cover the same scope, merge them.

#### Similar titles (low severity)

Two articles have similar titles but substantially different content. Similar titles can confuse the retrieval system, causing it to surface the wrong article.

**Resolution:** Rename one article to be more specific about what it covers.

## What the scanner checks

The scanner runs four analysis phases, all using data already in your knowledge base — no additional AI API calls are made during a scan.

1. **Embedding similarity** — Compares the mathematical representations of your articles to find pairs that are semantically similar. Only compares articles of the same type and language.

2. **Title similarity** — Compares article titles using text matching to catch renamed duplicates that embedding analysis might miss (e.g., "Return Policy" vs. "Returns Policy" vs. "Our Return Policy").

3. **Content overlap** — For flagged pairs, measures how much sentence-level content is shared to distinguish true duplicates from articles that merely cover related topics.

4. **Factual conflict detection** — Extracts specific data points (durations, prices, percentages, email addresses) and checks for contradictions between paired articles.

## Best practices for prevention

- **Use descriptive, unique titles.** "Return Policy" and "Refund Policy" may both be needed, but "Return Policy — Physical Products" and "Refund Policy — Digital Products" make the distinction clear to both the AI and your team.

- **Check before importing.** Before bulk-importing articles from a document or URL, scan your existing knowledge base to see if the topic is already covered.

- **Archive instead of duplicating.** When updating a policy, edit the existing article rather than creating a new one. If you need to keep the old version for reference, archive it.

- **Run periodic scans.** Schedule a monthly review using the scanner to catch drift as your team adds content.

- **Review "medium" results.** Topical overlaps are not always problems, but they're worth reviewing to ensure the articles complement rather than contradict each other.

## Limitations

- The scanner requires articles to have embeddings. Articles that haven't been embedded yet (shown as "entries without embeddings" in the result summary) are only checked by title similarity, not by content or semantic comparison.
- Factual conflict detection uses pattern matching for common data types (durations, prices, percentages, emails). It does not detect subjective or nuanced contradictions.
- The scanner compares articles within the same entry type and language. Cross-type and cross-language comparisons are intentionally skipped to reduce false positives.
