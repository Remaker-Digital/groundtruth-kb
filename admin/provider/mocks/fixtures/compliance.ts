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
    costs: {
      totalCost30d: 487.32,
      costPerConversation: 0.038,
      costByService: { openai: 312.40, cosmos: 89.50, compute: 62.00, email: 15.42, nats: 8.00 },
      projectedMonthly: 510.00,
      trend: "stable",
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
