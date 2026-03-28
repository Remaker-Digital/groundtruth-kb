// @ts-nocheck
/**
 * Mock handlers — Provider operations (deployments, queues, integrations, diagnostics).
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { GET } from '../router';
import { getStore } from '../store';
import type { MockRequest, MockResponse } from '../router';

export function registerOperationsHandlers(): void {
  GET('/api/superadmin/deployments', (_req: MockRequest): MockResponse => {
    return { status: 200, body: { deployments: getStore().operations.deployments } };
  });

  GET('/api/superadmin/queue-health', (_req: MockRequest): MockResponse => {
    return { status: 200, body: getStore().operations.queueHealth };
  });

  GET('/api/superadmin/integrations', (_req: MockRequest): MockResponse => {
    return { status: 200, body: { integrations: getStore().operations.integrations } };
  });

  GET('/api/superadmin/diagnostics', (_req: MockRequest): MockResponse => {
    return { status: 200, body: getStore().operations.diagnostics };
  });

  GET('/api/superadmin/diagnostics/:tenant_id', (req: MockRequest): MockResponse => {
    const tid = req.params.tenant_id;
    return {
      status: 200,
      body: {
        tenantId: tid,
        status: "active",
        tier: "professional",
        billingChannel: "stripe",
        createdAt: "2025-09-15T10:00:00Z",
        configState: {
          isActive: true,
          isConfigured: true,
          hasPendingChanges: false,
          activeVersion: 4,
          activatedAt: "2026-03-20T08:00:00Z",
        },
        aiConfig: {
          model: "gpt-4o",
          brandNamePresent: true,
          brandVoicePresent: true,
        },
        knowledgeBase: { totalArticles: 24, draftCount: 2, activeCount: 22 },
        team: { memberCount: 3, rolesBreakdown: { admin: 1, editor: 1, viewer: 1 } },
        conversations: {
          last24hCount: 42,
          last7dCount: 287,
          statusBreakdown: { completed: 250, escalated: 20, active: 17 },
        },
        integrations: {
          shopifyConnected: true,
          stripeConnected: true,
          natsDeployed: true,
          natsConnected: true,
        },
        widget: { widgetKeyPresent: true, originConfigured: true },
        lastActivityAt: "2026-03-28T11:30:00Z",
        collectionErrors: [],
        generatedAt: new Date().toISOString(),
      },
    };
  });

  GET('/api/superadmin/diagnostics/:tenant_id/errors', (req: MockRequest): MockResponse => {
    const tid = req.params.tenant_id;
    return {
      status: 200,
      body: {
        tenantId: tid,
        entries: [
          {
            eventType: "pipeline_error",
            timestamp: "2026-03-27T14:22:00Z",
            actor: "system",
            payload: { stage: "knowledge_retrieval", error: "Cosmos timeout after 5000ms" },
            conversationId: "conv-mock-001",
          },
          {
            eventType: "auth_failure",
            timestamp: "2026-03-26T09:10:00Z",
            actor: "widget",
            payload: { reason: "Invalid widget key", ip: "203.0.113.42" },
            conversationId: null,
          },
        ],
        total: 2,
        generatedAt: new Date().toISOString(),
      },
    };
  });
}
