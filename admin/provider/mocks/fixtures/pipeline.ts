// @ts-nocheck
/**
 * Provider pipeline fixture — agent topology and metrics.
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
export function createPipelineFixture() {
  return {
    topology: {
      nodes: [
        { id: "orchestrator", name: "Orchestrator", type: "router", status: "healthy" },
        { id: "classifier", name: "Intent Classifier", type: "agent", status: "healthy" },
        { id: "retrieval", name: "Retrieval Agent", type: "agent", status: "healthy" },
        { id: "response", name: "Response Generator", type: "agent", status: "healthy" },
        { id: "critic", name: "Critic Supervisor", type: "supervisor", status: "healthy" },
        { id: "escalation", name: "Escalation Handler", type: "agent", status: "healthy" },
      ],
      edges: [
        { from: "orchestrator", to: "classifier", label: "classify" },
        { from: "classifier", to: "retrieval", label: "needs_kb" },
        { from: "classifier", to: "response", label: "direct" },
        { from: "retrieval", to: "response", label: "context" },
        { from: "response", to: "critic", label: "review" },
        { from: "critic", to: "response", label: "revise" },
        { from: "critic", to: "escalation", label: "escalate" },
      ],
    },
    agentMetrics: {
      orchestrator: { avgLatencyMs: 45, p99LatencyMs: 120, requestCount24h: 12847, errorRate: 0.001, tokensUsed24h: 0 },
      classifier: { avgLatencyMs: 180, p99LatencyMs: 450, requestCount24h: 12847, errorRate: 0.002, tokensUsed24h: 384210 },
      retrieval: { avgLatencyMs: 320, p99LatencyMs: 890, requestCount24h: 8421, errorRate: 0.001, tokensUsed24h: 126420 },
      response: { avgLatencyMs: 1200, p99LatencyMs: 3200, requestCount24h: 12847, errorRate: 0.003, tokensUsed24h: 1847200 },
      critic: { avgLatencyMs: 800, p99LatencyMs: 2100, requestCount24h: 12847, errorRate: 0.001, tokensUsed24h: 962100 },
      escalation: { avgLatencyMs: 50, p99LatencyMs: 150, requestCount24h: 384, errorRate: 0.0, tokensUsed24h: 11520 },
    },
    tenantComparison: [
      { tenantId: "acme-corp-001", conversations24h: 847, avgLatencyMs: 1150, errorRate: 0.002, tokensUsed24h: 542100 },
      { tenantId: "blanco-9939", conversations24h: 421, avgLatencyMs: 1280, errorRate: 0.003, tokensUsed24h: 287400 },
      { tenantId: "remaker-digital-001", conversations24h: 218, avgLatencyMs: 1120, errorRate: 0.001, tokensUsed24h: 148200 },
      { tenantId: "harrison-001", conversations24h: 156, avgLatencyMs: 1340, errorRate: 0.004, tokensUsed24h: 98700 },
    ],
    database: {
      avgQueryLatencyMs: 12,
      p99QueryLatencyMs: 45,
      storageUsedMb: 847,
      ruUsed24h: 142000,
      ruLimit: 400000,
    },
  };
}
