// @ts-nocheck
/**
 * Mock handlers — Provider status page incidents.
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { GET, POST } from '../router';
import { getStore } from '../store';
import type { MockRequest, MockResponse } from '../router';

export function registerIncidentHandlers(): void {
  GET('/api/superadmin/incidents', (_req: MockRequest): MockResponse => {
    return { status: 200, body: { incidents: getStore().incidents.incidents } };
  });

  POST('/api/superadmin/incidents', (req: MockRequest): MockResponse => {
    const store = getStore();
    const body = req.body as Record<string, unknown>;
    const incident = {
      id: `inc-${String(store.incidents.nextIncidentId).padStart(3, '0')}`,
      title: body.title, status: 'investigating', severity: body.severity || 'minor',
      createdAt: new Date().toISOString(), resolvedAt: null,
      updates: [{ id: `upd-${Date.now()}`, message: body.message || 'Investigating', status: 'investigating', createdAt: new Date().toISOString() }],
    };
    store.incidents.incidents.unshift(incident);
    store.incidents.nextIncidentId += 1;
    return { status: 201, body: incident };
  });

  POST('/api/superadmin/incidents/:incidentId/update', (req: MockRequest): MockResponse => {
    const store = getStore();
    const incident = store.incidents.incidents.find(i => i.id === req.params.incidentId);
    if (!incident) return { status: 404, body: { detail: 'Incident not found' } };
    const body = req.body as Record<string, unknown>;
    const update = { id: `upd-${Date.now()}`, message: body.message, status: body.status || 'update', createdAt: new Date().toISOString() };
    incident.updates.push(update);
    incident.status = body.status || incident.status;
    return { status: 200, body: update };
  });

  POST('/api/superadmin/incidents/:incidentId/resolve', (req: MockRequest): MockResponse => {
    const store = getStore();
    const incident = store.incidents.incidents.find(i => i.id === req.params.incidentId);
    if (!incident) return { status: 404, body: { detail: 'Incident not found' } };
    incident.status = 'resolved';
    incident.resolvedAt = new Date().toISOString();
    return { status: 200, body: { resolvedAt: incident.resolvedAt } };
  });
}
