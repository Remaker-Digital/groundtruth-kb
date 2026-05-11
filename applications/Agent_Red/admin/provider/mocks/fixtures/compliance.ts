// @ts-nocheck
/**
 * Provider compliance fixture — PII, secrets, billing, SLA, costs, abuse.
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
export function createComplianceFixture() {
  return {
    compliance: {
      piiScanStatus: "clean",
      lastScanAt: "2026-03-11T02:00:00Z",
      dsarRequests: { pending: 0, completed: 12, total: 12 },
      dataRetentionDays: 90,
      gdprCompliant: true,
    },
    secrets: {
      posture: "good",
      secrets: [
        { name: "COSMOS_CONNECTION_STRING", source: "env", expiresAt: null, status: "active", rotatedAt: "2026-02-15T10:00:00Z" },
        { name: "OPENAI_API_KEY", source: "env", expiresAt: null, status: "active", rotatedAt: "2026-01-20T14:00:00Z" },
        { name: "SPA-PLATFORM-ADMIN-KEY", source: "key_vault", expiresAt: "2027-03-11T00:00:00Z", status: "active", rotatedAt: "2026-03-09T16:00:00Z" },
        { name: "STRIPE_WEBHOOK_SECRET", source: "env", expiresAt: null, status: "active", rotatedAt: "2025-11-01T09:00:00Z" },
      ],
      expiringWithin30d: 0,
    },
    billing: {
      mrr: 2847.00,
      activeSubscriptions: 14,
      trialConversions: { converted: 8, expired: 5, active: 3 },
      revenueByTier: { starter: 792, professional: 1470, enterprise: 585 },
      churnRate30d: 0.02,
    },
    sla: {
      uptime30d: 99.97,
      uptime90d: 99.94,
      p50LatencyMs: 135,
      p99LatencyMs: 890,
      incidents30d: 0,
      slaTarget: 99.9,
      history: [
        { date: "2026-03-10", uptime: 100.0, p50: 132, p99: 845 },
        { date: "2026-03-09", uptime: 100.0, p50: 138, p99: 912 },
        { date: "2026-03-08", uptime: 99.85, p50: 185, p99: 2340 },
        { date: "2026-03-07", uptime: 100.0, p50: 128, p99: 820 },
      ],
    },
    slaTrends: {
      rangeDays: 7,
      trendPoints: [
        { timestamp: "2026-03-22T00:00:00Z", uptimePct: 100.0, p50Ms: 128, p95Ms: 420, p99Ms: 820, totalRequests: 1820 },
        { timestamp: "2026-03-23T00:00:00Z", uptimePct: 100.0, p50Ms: 132, p95Ms: 445, p99Ms: 845, totalRequests: 1950 },
        { timestamp: "2026-03-24T00:00:00Z", uptimePct: 99.85, p50Ms: 185, p95Ms: 890, p99Ms: 2340, totalRequests: 2100 },
        { timestamp: "2026-03-25T00:00:00Z", uptimePct: 100.0, p50Ms: 138, p95Ms: 460, p99Ms: 912, totalRequests: 1870 },
        { timestamp: "2026-03-26T00:00:00Z", uptimePct: 100.0, p50Ms: 125, p95Ms: 410, p99Ms: 790, totalRequests: 1940 },
        { timestamp: "2026-03-27T00:00:00Z", uptimePct: 100.0, p50Ms: 130, p95Ms: 430, p99Ms: 835, totalRequests: 2050 },
        { timestamp: "2026-03-28T00:00:00Z", uptimePct: 100.0, p50Ms: 135, p95Ms: 450, p99Ms: 890, totalRequests: 1780 },
      ],
      errorBudgets: {
        STARTER: { tier: "STARTER", periodDays: 30, allowedDowntimeMinutes: 43.2, actualDowntimeMinutes: 1.3, budgetRemaining: 41.9, budgetConsumedPct: 3.0, isWithinBudget: true },
        PROFESSIONAL: { tier: "PROFESSIONAL", periodDays: 30, allowedDowntimeMinutes: 14.4, actualDowntimeMinutes: 1.3, budgetRemaining: 13.1, budgetConsumedPct: 9.0, isWithinBudget: true },
        ENTERPRISE: { tier: "ENTERPRISE", periodDays: 30, allowedDowntimeMinutes: 4.3, actualDowntimeMinutes: 1.3, budgetRemaining: 3.0, budgetConsumedPct: 30.2, isWithinBudget: true },
      },
      generatedAt: "2026-03-28T12:00:00Z",
    },
    costs: {
      periodStart: "2026-02-27T00:00:00Z",
      periodEnd: "2026-03-28T23:59:59Z",
      totalPlatformCost: 487.32,
      totalConversations: 12847,
      totalTenants: 19,
      avgCostPerTenant: 25.65,
      avgCostPerConversation: 0.038,
      tenants: [
        { tenantId: "tenant-001", tier: "enterprise", periodStart: "2026-02-27T00:00:00Z", periodEnd: "2026-03-28T23:59:59Z", conversationCount: 3200, totalInputTokens: 2400000, totalOutputTokens: 1800000, articleCount: 45, costBreakdown: { aiTokens: 89.60, cosmosDb: 24.50, storage: 5.20, compute: 18.40, total: 137.70 }, costPerConversation: 0.043, costSharePct: 28.3 },
        { tenantId: "tenant-002", tier: "professional", periodStart: "2026-02-27T00:00:00Z", periodEnd: "2026-03-28T23:59:59Z", conversationCount: 1850, totalInputTokens: 1200000, totalOutputTokens: 900000, articleCount: 22, costBreakdown: { aiTokens: 48.30, cosmosDb: 15.20, storage: 3.10, compute: 12.00, total: 78.60 }, costPerConversation: 0.042, costSharePct: 16.1 },
        { tenantId: "tenant-003", tier: "starter", periodStart: "2026-02-27T00:00:00Z", periodEnd: "2026-03-28T23:59:59Z", conversationCount: 420, totalInputTokens: 280000, totalOutputTokens: 210000, articleCount: 8, costBreakdown: { aiTokens: 11.20, cosmosDb: 4.80, storage: 0.90, compute: 3.50, total: 20.40 }, costPerConversation: 0.049, costSharePct: 4.2 },
      ],
      costByTier: { starter: 102.00, professional: 235.32, enterprise: 150.00 },
    },
    abuse: {
      anomalies: [
        { tenantId: "suspended-001", type: "excessive_requests", description: "4x normal request volume in 1 hour", detectedAt: "2026-03-10T22:00:00Z", severity: "medium", resolved: true },
      ],
      blockedIps: 3,
      rateLimitHits24h: 42,
    },
  };
}
