// @ts-nocheck
/**
 * Mock handlers — Provider MFA endpoints.
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { GET, POST } from '../router';
import { getStore } from '../store';
import type { MockRequest, MockResponse } from '../router';

export function registerMfaHandlers(): void {
  GET('/api/superadmin/mfa/status', (_req: MockRequest): MockResponse => {
    return { status: 200, body: getStore().userManagement.mfaStatus };
  });

  POST('/api/superadmin/mfa/verify', (req: MockRequest): MockResponse => {
    const body = req.body as Record<string, unknown>;
    if (body.code === '000000') {
      return { status: 400, body: { detail: 'Invalid TOTP code' } };
    }
    return { status: 200, body: { mfaToken: `mfa_mock_${Date.now()}` } };
  });

  // Emergency recovery (SPEC-1678)
  POST('/api/auth/spa-recovery/recover', (_req: MockRequest): MockResponse => {
    return { status: 200, body: { recovered: true, apiKey: `ar_spa_plat_recovered_${Date.now()}` } };
  });
}
