// @ts-nocheck
/**
 * Billing / Account fixture — Shopify billing channel.
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
export function createBillingFixture() {
  return {
    status: {
      plan: "professional",
      status: "active",
      currentPeriodStart: "2026-03-01T00:00:00Z",
      currentPeriodEnd: "2026-03-31T23:59:59Z",
      includedConversations: 500,
      usedConversations: 187,
      overageRate: 0.15,
    },
    contactPreferences: {
      email: "merchant@mock-store.myshopify.com",
      recoveryEmail: null,
      notificationEmail: "merchant@mock-store.myshopify.com",
    },
  };
}
