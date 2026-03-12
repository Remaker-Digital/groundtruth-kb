// @ts-nocheck
/**
 * Mock handlers — Provider service messages (bulk notifications).
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { POST } from '../router';
import { getStore } from '../store';
import type { MockRequest, MockResponse } from '../router';

export function registerServiceMessageHandlers(): void {
  POST('/api/superadmin/service-messages/preview', (req: MockRequest): MockResponse => {
    const body = req.body as Record<string, unknown>;
    let tenants = [...getStore().tenants.tenants];
    if (body.filterStatus) tenants = tenants.filter(t => t.status === body.filterStatus);
    if (body.filterTier) tenants = tenants.filter(t => t.tier === body.filterTier);
    return {
      status: 200,
      body: { recipients: tenants.map(t => ({ tenantId: t.id, email: t.email, domain: t.domain })) },
    };
  });

  POST('/api/superadmin/service-messages/send', (req: MockRequest): MockResponse => {
    const store = getStore();
    const body = req.body as Record<string, unknown>;
    const msg = {
      id: `sm-${Date.now()}`, subject: body.subject, body: body.body,
      recipientCount: (body.recipients as string[] || []).length || 14,
      sentAt: new Date().toISOString(), filterStatus: body.filterStatus || null, filterTier: body.filterTier || null,
    };
    store.serviceMessages.sentMessages.unshift(msg);
    return { status: 200, body: { sent: true, recipientCount: msg.recipientCount } };
  });
}
