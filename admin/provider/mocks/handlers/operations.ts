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
}
