// @ts-nocheck
/**
 * Provider dashboard fixture — system health + tenant summary.
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
export function createDashboardFixture() {
  return {
    timestamp: "2026-03-28T12:00:00Z",
    systemHealth: {
      cosmos: { healthy: true, status: "connected", detail: "Latency: 8ms" },
      redis: { healthy: true, status: "connected", detail: "Memory: 42%" },
      keyVault: { healthy: true, status: "connected", detail: "Secrets: 4 active" },
      version: { api: "1.0.0", product: "1.98.65-mock" },
    },
    tenantSummary: {
      totalTenants: 19,
      byStatus: { active: 14, trial: 3, suspended: 1, expired: 1 },
      byTier: { starter: 8, professional: 7, enterprise: 3, trial: 1 },
      byBillingChannel: { stripe: 12, shopify: 5, manual: 2 },
    },
    recentDeployments: [
      { eventType: "deploy", timestamp: "2026-03-28T10:30:00Z", actor: "ci/cd", payload: { version: "1.98.65", environment: "production", status: "success" } },
      { eventType: "deploy", timestamp: "2026-03-25T14:20:00Z", actor: "ci/cd", payload: { version: "1.98.61", environment: "staging", status: "success" } },
      { eventType: "config_change", timestamp: "2026-03-24T09:15:00Z", actor: "admin", payload: { description: "Rate limit updated to 300 RPM" } },
    ],
    slaSummary: {
      uptime30d: 99.97,
      p50LatencyMs: 135,
      p99LatencyMs: 890,
      incidents30d: 0,
    },
    usageSummary: {
      conversations24h: 847,
      apiRequests24h: 12847,
      errorRate24h: 0.003,
      avgLatencyMs: 142,
    },
    recentAlerts: [],
  };
}
