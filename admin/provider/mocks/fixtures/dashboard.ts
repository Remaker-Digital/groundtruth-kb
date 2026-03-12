// @ts-nocheck
/**
 * Provider dashboard fixture — system health + tenant summary.
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
export function createDashboardFixture() {
  return {
    health: {
      product_version: "1.82.0-mock",
      status: "healthy",
      uptime_seconds: 864000,
      total_tenants: 19,
      active_tenants: 14,
      api_requests_24h: 12847,
      error_rate_24h: 0.003,
      avg_latency_ms: 142,
      sla_uptime_30d: 99.97,
    },
    tenantSummary: {
      total: 19,
      byStatus: { active: 14, trial: 3, suspended: 1, expired: 1 },
      byTier: { starter: 8, professional: 7, enterprise: 3, trial: 1 },
      byBillingChannel: { stripe: 12, shopify: 5, manual: 2 },
    },
    recentDeployments: [
      { version: "1.82.0", environment: "staging", timestamp: "2026-03-11T10:30:00Z", status: "success", revision: "0000043" },
      { version: "1.80.5", environment: "production", timestamp: "2026-03-09T14:20:00Z", status: "success", revision: "0000095" },
      { version: "1.81.2", environment: "staging", timestamp: "2026-03-08T09:15:00Z", status: "success", revision: "0000041" },
    ],
    slaSummary: {
      uptime_30d: 99.97,
      p50_latency_ms: 135,
      p99_latency_ms: 890,
      incidents_30d: 0,
    },
  };
}
