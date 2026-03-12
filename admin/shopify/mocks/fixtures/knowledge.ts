// @ts-nocheck
/**
 * Knowledge base fixture - articles, staleness, conflict scan results.
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

export function createKnowledgeFixture() {
  return {
    articles: [
      { id: "kb-001", title: "Return Policy", content: "Items can be returned within 30 days of purchase for a full refund.", category: "policies", status: "published", entryType: "article", is_active: true, createdAt: "2026-01-20T10:00:00Z", updatedAt: "2026-03-01T14:00:00Z", sourceType: "manual", stalenessScore: 0.1, stalenessCategory: "fresh" },
      { id: "kb-002", title: "Shipping Information", content: "Free standard shipping on orders over $50. Express shipping: $9.99.", category: "policies", status: "published", entryType: "article", is_active: true, createdAt: "2026-01-20T10:30:00Z", updatedAt: "2026-02-28T11:00:00Z", sourceType: "manual", stalenessScore: 0.2, stalenessCategory: "fresh" },
      { id: "kb-003", title: "Product Care Guide", content: "Hand wash recommended for delicate items.", category: "products", status: "published", entryType: "article", is_active: true, createdAt: "2026-02-01T09:00:00Z", updatedAt: "2026-02-01T09:00:00Z", sourceType: "manual", stalenessScore: 0.4, stalenessCategory: "aging" },
      { id: "kb-004", title: "FAQ - Payment Methods", content: "We accept Visa, Mastercard, American Express, PayPal, and Shop Pay.", category: "faq", status: "published", entryType: "faq", is_active: true, createdAt: "2026-02-10T08:00:00Z", updatedAt: "2026-02-10T08:00:00Z", sourceType: "manual", stalenessScore: 0.3, stalenessCategory: "fresh" },
    ],
    staleness: { totalEntries: 4, avgStalenessScore: 0.25, freshCount: 3, agingCount: 1, staleCount: 0, veryStaleCount: 0, needsAttention: 0 },
    nextId: 5,
  };
}
