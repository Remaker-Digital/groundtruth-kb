// @ts-nocheck
/**
 * Mock handlers — Provider tenant directory endpoints.
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { GET, POST, PATCH } from '../router';
import { getStore } from '../store';
import type { MockRequest, MockResponse } from '../router';

export function registerTenantHandlers(): void {
  GET('/api/superadmin/tenants/summary', (_req: MockRequest): MockResponse => {
    return { status: 200, body: getStore().tenants.summary };
  });

  GET('/api/superadmin/tenants', (req: MockRequest): MockResponse => {
    const store = getStore();
    const limit = parseInt(req.query.limit || '25', 10);
    const skip = parseInt(req.query.skip || '0', 10);
    let filtered = [...store.tenants.tenants];
    if (req.query.status) filtered = filtered.filter(t => t.status === req.query.status);
    if (req.query.tier) filtered = filtered.filter(t => t.tier === req.query.tier);
    if (req.query.billing_channel) filtered = filtered.filter(t => t.billingChannel === req.query.billing_channel);
    return {
      status: 200,
      body: { tenants: filtered.slice(skip, skip + limit), total: filtered.length, limit, skip },
    };
  });

  POST('/api/superadmin/tenants', (req: MockRequest): MockResponse => {
    const store = getStore();
    const body = req.body as Record<string, unknown>;
    const id = `tenant-${Date.now()}`;
    const tenant = {
      id, email: body.email, domain: body.domain || 'new-tenant.example.com',
      status: 'active', tier: body.tier || 'starter', billingChannel: body.billingChannel || 'stripe',
      createdAt: new Date().toISOString(), expiresAt: null, conversationCount: 0, teamMemberCount: 1,
    };
    store.tenants.tenants.push(tenant);
    store.tenants.summary.total += 1;
    return { status: 201, body: { tenant_id: id, keys_delivered_via_email: true } };
  });

  PATCH('/api/superadmin/tenants/:tenantId/expiry', (req: MockRequest): MockResponse => {
    const store = getStore();
    const tenant = store.tenants.tenants.find(t => t.id === req.params.tenantId);
    if (!tenant) return { status: 404, body: { detail: 'Tenant not found' } };
    const body = req.body as Record<string, unknown>;
    tenant.expiresAt = body.expiresAt ?? null;
    return { status: 200, body: { expiresAt: tenant.expiresAt } };
  });

  POST('/api/superadmin/tenants/:tenantId/resend-welcome-email', (req: MockRequest): MockResponse => {
    const store = getStore();
    const tenant = store.tenants.tenants.find(t => t.id === req.params.tenantId);
    if (!tenant) return { status: 404, body: { detail: 'Tenant not found' } };
    return { status: 200, body: { sent: true, sentTo: tenant.email, message: 'Welcome email resent' } };
  });
}
