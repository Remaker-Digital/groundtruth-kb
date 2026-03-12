// @ts-nocheck
/**
 * Provider alerts fixture — alert rules and history.
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
export function createAlertsFixture() {
  return {
    rules: [
      { id: "rule-001", name: "High Error Rate", condition: "error_rate > 5%", threshold: 5, metric: "error_rate", enabled: true, severity: "critical", notifyEmail: "ops@remaker.digital", createdAt: "2025-12-01T10:00:00Z" },
      { id: "rule-002", name: "Latency Spike", condition: "p99_latency > 2000ms", threshold: 2000, metric: "p99_latency_ms", enabled: true, severity: "warning", notifyEmail: "ops@remaker.digital", createdAt: "2025-12-01T10:05:00Z" },
      { id: "rule-003", name: "Queue Depth", condition: "queue_depth > 1000", threshold: 1000, metric: "queue_depth", enabled: false, severity: "warning", notifyEmail: "ops@remaker.digital", createdAt: "2025-12-15T08:00:00Z" },
      { id: "rule-004", name: "Tenant Inactive", condition: "no_activity_days > 30", threshold: 30, metric: "inactive_days", enabled: true, severity: "info", notifyEmail: "admin@remaker.digital", createdAt: "2026-01-10T14:00:00Z" },
    ],
    history: [
      { id: "alert-001", ruleId: "rule-002", ruleName: "Latency Spike", severity: "warning", firedAt: "2026-03-10T15:42:00Z", resolvedAt: "2026-03-10T15:58:00Z", acknowledged: true, acknowledgedBy: "admin", value: 2340 },
      { id: "alert-002", ruleId: "rule-001", ruleName: "High Error Rate", severity: "critical", firedAt: "2026-03-08T03:12:00Z", resolvedAt: "2026-03-08T03:25:00Z", acknowledged: true, acknowledgedBy: "admin", value: 7.2 },
      { id: "alert-003", ruleId: "rule-004", ruleName: "Tenant Inactive", severity: "info", firedAt: "2026-03-05T00:00:00Z", resolvedAt: null, acknowledged: false, acknowledgedBy: null, value: 35 },
    ],
    nextRuleId: 5,
  };
}
