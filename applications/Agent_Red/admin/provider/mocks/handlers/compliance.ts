// @ts-nocheck
/**
 * Mock handlers — Provider compliance, secrets, billing, SLA, costs, abuse.
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { GET } from '../router';
import { getStore } from '../store';
import type { MockRequest, MockResponse } from '../router';

export function registerComplianceHandlers(): void {
  GET('/api/superadmin/compliance', (_req: MockRequest): MockResponse => {
    return { status: 200, body: getStore().compliance.compliance };
  });

  GET('/api/superadmin/secrets', (_req: MockRequest): MockResponse => {
    return { status: 200, body: getStore().compliance.secrets };
  });

  GET('/api/superadmin/billing', (_req: MockRequest): MockResponse => {
    return { status: 200, body: getStore().compliance.billing };
  });

  GET('/api/superadmin/sla', (_req: MockRequest): MockResponse => {
    return { status: 200, body: getStore().compliance.sla };
  });

  GET('/api/superadmin/sla/trends', (req: MockRequest): MockResponse => {
    const trends = getStore().compliance.slaTrends;
    const rangeDays = parseInt(req.query.range_days || '7', 10);
    return {
      status: 200,
      body: { ...trends, rangeDays },
    };
  });

  GET('/api/superadmin/costs', (_req: MockRequest): MockResponse => {
    return { status: 200, body: getStore().compliance.costs };
  });

  GET('/api/superadmin/abuse', (_req: MockRequest): MockResponse => {
    return { status: 200, body: getStore().compliance.abuse };
  });
}
