// @ts-nocheck
/**
 * Mock handlers — Billing / Account endpoints.
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { GET, POST, PUT } from '../router';
import { getStore } from '../store';
import type { MockRequest, MockResponse } from '../router';

export function registerBillingHandlers(): void {
  const s = () => getStore().billing;

  GET('/api/billing/status', (_req: MockRequest): MockResponse => {
    return { status: 200, body: s().status };
  });

  GET('/api/billing/packs', (_req: MockRequest): MockResponse => {
    return { status: 200, body: { balance: 5, packs: [] } };
  });

  GET('/api/admin/contact-preferences', (_req: MockRequest): MockResponse => {
    return { status: 200, body: s().contactPreferences };
  });

  PUT('/api/admin/contact-preferences', (req: MockRequest): MockResponse => {
    const store = getStore();
    store.billing.contactPreferences = { ...store.billing.contactPreferences, ...req.body };
    return { status: 200, body: store.billing.contactPreferences };
  });

  // Email change request/confirm
  POST('/api/admin/email/request', (req: MockRequest): MockResponse => {
    return { status: 200, body: { success: true, message: 'Verification email sent to ' + (req.body?.newEmail ?? 'unknown') } };
  });

  POST('/api/admin/email/confirm', (_req: MockRequest): MockResponse => {
    return { status: 200, body: { success: true, message: 'Email updated successfully' } };
  });
}
