// @ts-nocheck
/**
 * Billing / Account fixture.
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
      usedConversations: 342,
      overageRate: 0.15,
    },
    contactPreferences: {
      email: "admin@mockstore.com",
      recoveryEmail: null,
      notificationEmail: "admin@mockstore.com",
    },
  };
}
