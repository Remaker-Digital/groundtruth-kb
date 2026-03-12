// @ts-nocheck
/**
 * Mock handlers — Provider alert rules and history.
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { GET, POST, PUT, DELETE } from '../router';
import { getStore } from '../store';
import type { MockRequest, MockResponse } from '../router';

export function registerAlertHandlers(): void {
  GET('/api/superadmin/alerts/rules', (_req: MockRequest): MockResponse => {
    return { status: 200, body: { rules: getStore().alerts.rules } };
  });

  GET('/api/superadmin/alerts/history', (req: MockRequest): MockResponse => {
    const limit = parseInt(req.query.limit || '200', 10);
    return { status: 200, body: { alerts: getStore().alerts.history.slice(0, limit) } };
  });

  POST('/api/superadmin/alerts/rules', (req: MockRequest): MockResponse => {
    const store = getStore();
    const body = req.body as Record<string, unknown>;
    const rule = { id: `rule-${String(store.alerts.nextRuleId).padStart(3, '0')}`, ...body, createdAt: new Date().toISOString() };
    store.alerts.rules.push(rule);
    store.alerts.nextRuleId += 1;
    return { status: 201, body: rule };
  });

  PUT('/api/superadmin/alerts/rules/:ruleId', (req: MockRequest): MockResponse => {
    const store = getStore();
    const idx = store.alerts.rules.findIndex(r => r.id === req.params.ruleId);
    if (idx === -1) return { status: 404, body: { detail: 'Alert rule not found' } };
    store.alerts.rules[idx] = { ...store.alerts.rules[idx], ...req.body };
    return { status: 200, body: store.alerts.rules[idx] };
  });

  DELETE('/api/superadmin/alerts/rules/:ruleId', (req: MockRequest): MockResponse => {
    const store = getStore();
    store.alerts.rules = store.alerts.rules.filter(r => r.id !== req.params.ruleId);
    return { status: 200, body: {} };
  });

  POST('/api/superadmin/alerts/history/:alertId/acknowledge', (req: MockRequest): MockResponse => {
    const store = getStore();
    const alert = store.alerts.history.find(a => a.id === req.params.alertId);
    if (!alert) return { status: 404, body: { detail: 'Alert not found' } };
    alert.acknowledged = true;
    alert.acknowledgedBy = 'admin';
    return { status: 200, body: {} };
  });

  POST('/api/superadmin/alerts/evaluate', (_req: MockRequest): MockResponse => {
    return { status: 200, body: { evaluated: true, message: 'Alert evaluation complete — no alerts triggered' } };
  });
}
