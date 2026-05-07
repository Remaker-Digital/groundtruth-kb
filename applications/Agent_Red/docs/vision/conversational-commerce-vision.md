# Conversational Commerce Vision — Agent Red

> **Status:** Vision document. Work items extracted for prioritization.
> **Origin:** Owner customer story (S89), Hugo.ai competitive gap analysis.
> **Created:** 2026-02-24

## The Customer Story

> Customer asks Agent Red about "...new hats for men this season?"
>
> Agent Red replies "Yes! We have several, and one that I think you'd love. Take a look at this:"
>
> An image of a hat with some brief text describing it (and a clickable navigation icon) appears in the chat window below Agent Red's response, in-line.
>
> The user clicks on the navigation icon and the merchant's web site navigates to a product page corresponding with the previously displayed hat.
>
> Agent Red pops up and the chat resumes with Agent Red adding "Yes, here it is. What do you think?"
>
> Agent Red pauses and two quick actions appear below the latest text in the chat window: "I like deals" and "Stock alert"
>
> Agent Red continues "There are several colors to choose from which are similar to your last 2 purchases with us. I can add it to your watch list if you like. That way you can get a notification if it goes on sale or we run low on inventory."

## Capability Decomposition

### Tier 1: Knowledge-Powered Recommendations (Foundation — BUILT)

The automated website crawling pipeline (S89) provides the data layer:

- Website sources auto-crawl merchant sites on configurable schedules
- KB entries carry `source_url`, `page_type` (product/policy/faq/blog), `link_label`, `source_domain` metadata
- Incremental change detection keeps content fresh
- Tier-gated limits (starter: 3 sources/25 pages, professional: 10/50, enterprise: 25/100)

**Status:** Complete (S89). Backend + Admin UI deployed.

### Tier 2: Clickable Link Injection

The AI includes clickable URLs in responses when answering from knowledge base content that has source URLs. Customer clicks a link and navigates to the merchant's product page, policy, or content.

**Components:**
- WI-CC-1: KB retrieval passes `source_url` to response generator context
- WI-CC-2: System prompt instructs AI to format URLs as markdown links when source_url is available
- WI-CC-3: Widget renders markdown links (`[text](url)`) as clickable `<a>` elements
- WI-CC-4: Link click opens in parent frame (not widget iframe) via `target="_top"`

**Status:** Next immediate action. Foundation data is ready.

### Tier 3: Rich Media Messages

Product cards with images, descriptions, and navigation icons appear inline in chat.

**Components:**
- WI-CC-5: Image URL extraction during website crawl (og:image, product images)
- WI-CC-6: Rich message type in widget (ProductCard component with image, title, price, CTA)
- WI-CC-7: Structured response format from AI (JSON blocks for product cards vs. plain text)
- WI-CC-8: Image proxy/caching for cross-origin display in widget

**Dependencies:** Tier 2 complete. Product page crawl enrichment.
**Status:** Future.

### Tier 4: Quick Action Buttons

Contextual action buttons appear below AI messages (e.g., "I like deals", "Stock alert", "Add to cart").

**Components:**
- WI-CC-9: Action button schema in message metadata
- WI-CC-10: Widget QuickAction component (renders button row below message)
- WI-CC-11: Action dispatch handler (button click → API call or navigation)
- WI-CC-12: AI response format for suggesting actions (structured output)

**Dependencies:** Tier 3 architecture decisions.
**Status:** Future.

### Tier 5: Purchase History Awareness

AI references customer's purchase history to make personalized recommendations ("similar to your last 2 purchases").

**Components:**
- WI-CC-13: Shopify Customer Account MCP integration (order history, preferences)
- WI-CC-14: Customer purchase profile in Layer 4 context (system prompt builder)
- WI-CC-15: Recommendation engine prompt engineering (similarity, recency, category)

**Dependencies:** Shopify Customer Account MCP (deferred post-cycle 14).
**Status:** Future — requires MCP integration.

### Tier 6: Watchlist & Notifications

Customer can add products to a watch list and receive notifications for price drops or low inventory.

**Components:**
- WI-CC-16: Customer watchlist persistence (Cosmos DB WatchlistDocument)
- WI-CC-17: Shopify inventory webhook listener (stock level changes)
- WI-CC-18: Price change detection (periodic crawl comparison)
- WI-CC-19: Push notification pipeline (email, SMS, or in-widget alert)
- WI-CC-20: "Add to watchlist" action handler (Tier 4 quick action)

**Dependencies:** Tier 4 + Tier 5 + Shopify webhook infrastructure.
**Status:** Future — new subsystem.

## Priority Matrix

| Tier | Work Items | Prerequisite | Immediate Value | Effort |
|------|-----------|-------------|-----------------|--------|
| **1** | Foundation | None | High — automates KB population | **DONE** |
| **2** | WI-CC-1→4 | Tier 1 | High — links drive navigation + sales | Small |
| **3** | WI-CC-5→8 | Tier 2 | Medium — visual product cards | Medium |
| **4** | WI-CC-9→12 | Tier 3 | Medium — actionable conversations | Medium |
| **5** | WI-CC-13→15 | MCP integration | High — personalization | Large |
| **6** | WI-CC-16→20 | Tier 4+5 | Medium — retention | Large |

**Recommended sequence:** Tier 2 now → Tier 3 next → Tiers 4-6 as MCP integrations land.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
