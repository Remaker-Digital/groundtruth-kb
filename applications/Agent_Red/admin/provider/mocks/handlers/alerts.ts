// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
// @ts-nocheck
/**
 * Mock handlers — Provider alert rules and history.
 *
 * Field names match the CamelCase API contract consumed by AlertConfig.tsx:
 *   rules: ruleId, ruleType, condition: { metric, operator, threshold }, ...
 *   history: alertId, alertDate, ruleType, triggeredAt, metricValue, ...
 *
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { GET, POST, PUT, DELETE } from '../router';
import { getStore } from '../store';
import type { MockRequest, MockResponse } from '../router';

export function registerAlertHandlers(): void {
  GET('/api/superadmin/alerts/rules', (_req: MockRequest): MockResponse => {
    const rules = getStore().alerts.rules;
    return { status: 200, body: { rules, total: rules.length } };
  });

  GET('/api/superadmin/alerts/history', (req: MockRequest): MockResponse => {
    const limit = parseInt(req.query.limit || '200', 10);
    const alerts = getStore().alerts.history.slice(0, limit);
    return { status: 200, body: { alerts, total: alerts.length } };
  });

  POST('/api/superadmin/alerts/rules', (req: MockRequest): MockResponse => {
    const store = getStore();
    const body = req.body as Record<string, unknown>;
    const now = new Date().toISOString();
    const ruleId = `rule-${String(store.alerts.nextRuleId).padStart(3, '0')}`;
    const rule = {
      ruleId,
      ruleType: body.ruleType || 'queue_depth',
      name: body.name || '',
      description: body.description || '',
      enabled: true,
      condition: body.condition || { metric: '', operator: 'gt', threshold: 0 },
      notificationChannels: body.notificationChannels || ['email'],
      cooldownMinutes: body.cooldownMinutes || 60,
      runbookUrl: body.runbookUrl || '',
      createdAt: now,
      updatedAt: now,
    };
    store.alerts.rules.push(rule);
    store.alerts.nextRuleId += 1;
    return { status: 201, body: rule };
  });

  PUT('/api/superadmin/alerts/rules/:ruleId', (req: MockRequest): MockResponse => {
    const store = getStore();
    const idx = store.alerts.rules.findIndex((r: Record<string, unknown>) => r.ruleId === req.params.ruleId);
    if (idx === -1) return { status: 404, body: { detail: 'Alert rule not found' } };
    store.alerts.rules[idx] = {
      ...store.alerts.rules[idx],
      ...req.body,
      updatedAt: new Date().toISOString(),
    };
    return { status: 200, body: store.alerts.rules[idx] };
  });

  DELETE('/api/superadmin/alerts/rules/:ruleId', (req: MockRequest): MockResponse => {
    const store = getStore();
    store.alerts.rules = store.alerts.rules.filter((r: Record<string, unknown>) => r.ruleId !== req.params.ruleId);
    return { status: 200, body: { deleted: true, ruleId: req.params.ruleId } };
  });

  POST('/api/superadmin/alerts/history/:alertId/acknowledge', (req: MockRequest): MockResponse => {
    const store = getStore();
    const alert = store.alerts.history.find((a: Record<string, unknown>) => a.alertId === req.params.alertId);
    if (!alert) return { status: 404, body: { detail: 'Alert not found' } };
    alert.acknowledged = true;
    alert.acknowledgedBy = 'admin';
    return { status: 200, body: alert };
  });

  POST('/api/superadmin/alerts/evaluate', (_req: MockRequest): MockResponse => {
    return { status: 200, body: { evaluated: true, message: 'Alert evaluation complete — no alerts triggered' } };
  });
}
