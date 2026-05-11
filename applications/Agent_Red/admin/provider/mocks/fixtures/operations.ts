// @ts-nocheck
/**
 * Provider operations fixture — deployments, queues, integrations, diagnostics.
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
export function createOperationsFixture() {
  return {
    deployments: [
      { id: "dep-001", version: "1.82.0", environment: "staging", status: "success", timestamp: "2026-03-11T10:30:00Z", revision: "0000043", duration_s: 142 },
      { id: "dep-002", version: "1.80.5", environment: "production", status: "success", timestamp: "2026-03-09T14:20:00Z", revision: "0000095", duration_s: 168 },
      { id: "dep-003", version: "1.81.2", environment: "staging", status: "success", timestamp: "2026-03-08T09:15:00Z", revision: "0000041", duration_s: 135 },
      { id: "dep-004", version: "1.80.4", environment: "staging", status: "failed", timestamp: "2026-03-07T16:45:00Z", revision: "0000039", duration_s: 87, error: "Docker Hub rate limit exceeded" },
    ],
    queueHealth: {
      queues: [
        { name: "chat.inbound", depth: 0, consumers: 2, messagesPerSec: 4.2, status: "healthy" },
        { name: "chat.outbound", depth: 3, consumers: 2, messagesPerSec: 3.8, status: "healthy" },
        { name: "events.analytics", depth: 142, consumers: 1, messagesPerSec: 12.5, status: "healthy" },
        { name: "events.audit", depth: 0, consumers: 1, messagesPerSec: 1.2, status: "healthy" },
        { name: "email.outbound", depth: 0, consumers: 1, messagesPerSec: 0.3, status: "healthy" },
      ],
      totalMessages24h: 184200,
    },
    integrations: [
      { name: "Azure Cosmos DB", status: "healthy", latencyMs: 12, lastCheckAt: "2026-03-11T12:00:00Z", errorRate: 0.0 },
      { name: "Azure OpenAI", status: "healthy", latencyMs: 1200, lastCheckAt: "2026-03-11T12:00:00Z", errorRate: 0.003 },
      { name: "Azure Communication Services", status: "healthy", latencyMs: 340, lastCheckAt: "2026-03-11T12:00:00Z", errorRate: 0.0 },
      { name: "NATS JetStream", status: "healthy", latencyMs: 2, lastCheckAt: "2026-03-11T12:00:00Z", errorRate: 0.0 },
      { name: "Stripe API", status: "degraded", latencyMs: 890, lastCheckAt: "2026-03-11T12:00:00Z", errorRate: 0.012 },
      { name: "Shopify Admin API", status: "healthy", latencyMs: 450, lastCheckAt: "2026-03-11T12:00:00Z", errorRate: 0.001 },
    ],
    diagnostics: {
      systemInfo: { os: "Linux 5.15", python: "3.11.7", nodeCount: 2, region: "East US" },
      recentErrors: [
        { timestamp: "2026-03-11T11:42:00Z", level: "WARNING", message: "Stripe webhook verification failed — signature expired", count: 3 },
        { timestamp: "2026-03-10T23:15:00Z", level: "ERROR", message: "Cosmos RU exceeded for container 'conversations'", count: 1 },
      ],
    },
  };
}
