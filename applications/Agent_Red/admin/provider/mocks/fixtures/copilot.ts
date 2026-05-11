// @ts-nocheck
/**
 * Provider Co-Pilot knowledge fixture — documents, stats, config.
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
export function createCopilotFixture() {
  return {
    documents: [
      { id: "doc-001", title: "Getting Started Guide", source: "docs-site", url: "https://agentredcx.com/docs/getting-started", status: "embedded", chunkCount: 24, lastEmbeddedAt: "2026-03-10T08:00:00Z", createdAt: "2025-12-01T10:00:00Z" },
      { id: "doc-002", title: "API Reference", source: "docs-site", url: "https://agentredcx.com/docs/api", status: "embedded", chunkCount: 87, lastEmbeddedAt: "2026-03-10T08:00:00Z", createdAt: "2025-12-01T10:00:00Z" },
      { id: "doc-003", title: "Troubleshooting FAQ", source: "manual", url: null, status: "embedded", chunkCount: 15, lastEmbeddedAt: "2026-03-05T12:00:00Z", createdAt: "2026-01-15T14:00:00Z" },
      { id: "doc-004", title: "Widget Customization", source: "url", url: "https://agentredcx.com/docs/widget", status: "stale", chunkCount: 32, lastEmbeddedAt: "2026-02-01T10:00:00Z", createdAt: "2025-12-15T09:00:00Z" },
    ],
    stats: {
      totalDocuments: 4,
      totalChunks: 158,
      embeddedDocuments: 3,
      staleDocuments: 1,
      lastIngestionAt: "2026-03-10T08:00:00Z",
      vectorDbSize: "42.7 MB",
    },
    config: {
      schedule: { frequency: "weekly", nextRun: "2026-03-17T02:00:00Z" },
      retrieval: { topK: 5, confidenceThreshold: 0.72 },
    },
    nextDocId: 5,
  };
}
