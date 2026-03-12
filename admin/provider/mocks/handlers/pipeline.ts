// @ts-nocheck
/**
 * Mock handlers — Provider pipeline observatory.
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { GET } from '../router';
import { getStore } from '../store';
import type { MockRequest, MockResponse } from '../router';

export function registerPipelineHandlers(): void {
  GET('/api/superadmin/pipeline/topology', (_req: MockRequest): MockResponse => {
    return { status: 200, body: getStore().pipeline.topology };
  });

  GET('/api/superadmin/pipeline/agents/:agent/metrics', (req: MockRequest): MockResponse => {
    const metrics = getStore().pipeline.agentMetrics[req.params.agent];
    if (!metrics) return { status: 404, body: { detail: 'Agent not found' } };
    return { status: 200, body: metrics };
  });

  GET('/api/superadmin/pipeline/tenants', (_req: MockRequest): MockResponse => {
    return { status: 200, body: { tenants: getStore().pipeline.tenantComparison } };
  });

  GET('/api/superadmin/pipeline/tenants/:tenantId/metrics', (req: MockRequest): MockResponse => {
    const t = getStore().pipeline.tenantComparison.find(t => t.tenantId === req.params.tenantId);
    if (!t) return { status: 404, body: { detail: 'Tenant not found' } };
    return { status: 200, body: t };
  });

  GET('/api/superadmin/pipeline/database', (_req: MockRequest): MockResponse => {
    return { status: 200, body: getStore().pipeline.database };
  });
}
