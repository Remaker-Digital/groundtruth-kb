// @ts-nocheck
/**
 * Provider contact messages fixture.
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
export function createContactMessagesFixture() {
  return {
    messages: [
      { id: "cm-001", name: "Sarah Johnson", email: "sarah@acme-corp.com", tenantId: "acme-corp-001", topic: "billing", subject: "Invoice question", body: "I have a question about our latest invoice. The amount seems higher than expected.", status: "open", notes: "", createdAt: "2026-03-10T14:30:00Z" },
      { id: "cm-002", name: "Mike Chen", email: "mike@blanco.com", tenantId: "blanco-9939", topic: "technical", subject: "Widget not loading on mobile", body: "The chat widget doesn't appear on our mobile site. Works fine on desktop.", status: "in_progress", notes: "Investigating viewport detection", createdAt: "2026-03-09T09:15:00Z" },
      { id: "cm-003", name: "Emily Brown", email: "emily@newshop.com", tenantId: "trial-user-001", topic: "sales", subject: "Upgrading from trial", body: "We love the product! What are the pricing options for upgrading from our trial?", status: "resolved", notes: "Sent pricing sheet", createdAt: "2026-03-07T16:45:00Z" },
      { id: "cm-004", name: "Roger Harrison", email: "roger@harrisoncorp.com", tenantId: "harrison-001", topic: "feature_request", subject: "Multi-language support", body: "Our customers speak Spanish and French. Any plans for multi-language responses?", status: "open", notes: "", createdAt: "2026-03-06T11:00:00Z" },
    ],
    total: 4,
  };
}
