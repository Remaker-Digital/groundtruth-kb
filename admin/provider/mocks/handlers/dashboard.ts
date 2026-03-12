// @ts-nocheck
/**
 * Mock handlers — Provider dashboard endpoints.
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { GET } from '../router';
import { getStore } from '../store';
import type { MockRequest, MockResponse } from '../router';

export function registerDashboardHandlers(): void {
  GET('/api/superadmin/dashboard', (_req: MockRequest): MockResponse => {
    const d = getStore().dashboard;
    return { status: 200, body: d.health };
  });
}
