// @ts-nocheck
/**
 * Mock handlers — Provider contact messages.
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { GET, PATCH } from '../router';
import { getStore } from '../store';
import type { MockRequest, MockResponse } from '../router';

export function registerContactHandlers(): void {
  GET('/api/superadmin/contact-messages', (req: MockRequest): MockResponse => {
    const store = getStore();
    const limit = parseInt(req.query.limit || '25', 10);
    const skip = parseInt(req.query.skip || '0', 10);
    let filtered = [...store.contactMessages.messages];
    if (req.query.status) filtered = filtered.filter(m => m.status === req.query.status);
    if (req.query.topic) filtered = filtered.filter(m => m.topic === req.query.topic);
    if (req.query.tenant_id) filtered = filtered.filter(m => m.tenantId === req.query.tenant_id);
    return { status: 200, body: { messages: filtered.slice(skip, skip + limit), total: filtered.length } };
  });

  GET('/api/superadmin/contact-messages/:id', (req: MockRequest): MockResponse => {
    const msg = getStore().contactMessages.messages.find(m => m.id === req.params.id);
    if (!msg) return { status: 404, body: { detail: 'Message not found' } };
    return { status: 200, body: msg };
  });

  PATCH('/api/superadmin/contact-messages/:id', (req: MockRequest): MockResponse => {
    const store = getStore();
    const msg = store.contactMessages.messages.find(m => m.id === req.params.id);
    if (!msg) return { status: 404, body: { detail: 'Message not found' } };
    const body = req.body as Record<string, unknown>;
    if (body.status !== undefined) msg.status = body.status;
    if (body.notes !== undefined) msg.notes = body.notes;
    return { status: 200, body: msg };
  });

  GET('/api/superadmin/contact-messages/export', (_req: MockRequest): MockResponse => {
    return { status: 200, body: 'id,name,email,topic,subject,status\ncm-001,Sarah Johnson,sarah@acme-corp.com,billing,Invoice question,open', headers: { 'Content-Type': 'text/csv' } };
  });
}
