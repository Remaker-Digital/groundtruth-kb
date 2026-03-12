// @ts-nocheck
/**
 * Provider tenants fixture — tenant directory data.
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
export function createTenantsFixture() {
  const now = new Date().toISOString();
  return {
    tenants: [
      { id: "remaker-digital-001", email: "admin@remaker.digital", domain: "remaker.digital", status: "active", tier: "professional", billingChannel: "stripe", createdAt: "2025-11-15T10:00:00Z", expiresAt: null, conversationCount: 1847, teamMemberCount: 5 },
      { id: "staging-001", email: "staging@example.com", domain: "staging.example.com", status: "active", tier: "starter", billingChannel: "stripe", createdAt: "2025-12-01T08:00:00Z", expiresAt: null, conversationCount: 432, teamMemberCount: 2 },
      { id: "staging-002", email: "staging2@example.com", domain: "staging2.example.com", status: "active", tier: "starter", billingChannel: "stripe", createdAt: "2025-12-15T12:00:00Z", expiresAt: null, conversationCount: 218, teamMemberCount: 1 },
      { id: "acme-corp-001", email: "admin@acme-corp.com", domain: "acme-corp.com", status: "active", tier: "enterprise", billingChannel: "stripe", createdAt: "2025-10-01T09:00:00Z", expiresAt: null, conversationCount: 5621, teamMemberCount: 12 },
      { id: "blanco-9939", email: "shop@blanco.com", domain: "blanco-9939.myshopify.com", status: "active", tier: "professional", billingChannel: "shopify", createdAt: "2025-09-20T15:30:00Z", expiresAt: null, conversationCount: 3210, teamMemberCount: 4 },
      { id: "harrison-001", email: "roger@harrisoncorp.com", domain: "harrisoncorp.com", status: "active", tier: "professional", billingChannel: "stripe", createdAt: "2025-11-01T11:00:00Z", expiresAt: null, conversationCount: 980, teamMemberCount: 3 },
      { id: "trial-user-001", email: "trial@newshop.com", domain: "newshop.myshopify.com", status: "trial", tier: "trial", billingChannel: "shopify", createdAt: "2026-03-01T14:00:00Z", expiresAt: "2026-03-15T14:00:00Z", conversationCount: 15, teamMemberCount: 1 },
      { id: "suspended-001", email: "overdue@example.com", domain: "overdue.example.com", status: "suspended", tier: "starter", billingChannel: "stripe", createdAt: "2025-08-10T10:00:00Z", expiresAt: null, conversationCount: 890, teamMemberCount: 2 },
      { id: "expired-001", email: "expired@oldshop.com", domain: "oldshop.myshopify.com", status: "expired", tier: "starter", billingChannel: "shopify", createdAt: "2025-06-01T09:00:00Z", expiresAt: "2025-12-01T09:00:00Z", conversationCount: 120, teamMemberCount: 1 },
    ],
    summary: {
      total: 19,
      byStatus: { active: 14, trial: 3, suspended: 1, expired: 1 },
      byTier: { starter: 8, professional: 7, enterprise: 3, trial: 1 },
      byBillingChannel: { stripe: 12, shopify: 5, manual: 2 },
    },
  };
}
