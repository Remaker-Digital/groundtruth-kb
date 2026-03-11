// @ts-nocheck
/**
 * Mock handlers — Quick Actions endpoints.
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { GET, POST, PUT, DELETE } from '../router';
import { getStore } from '../store';
import type { MockRequest, MockResponse } from '../router';

export function registerQuickActionHandlers(): void {
  const s = () => getStore().quickActions;

  GET('/api/admin/quick-actions', (_req: MockRequest): MockResponse => {
    return { status: 200, body: { actions: s().actions } };
  });

  POST('/api/admin/quick-actions', (req: MockRequest): MockResponse => {
    const store = getStore();
    const id = 'qa-' + String(store.quickActions.actions.length + 1).padStart(3, '0');
    const action = { id, ...req.body, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() };
    store.quickActions.actions.push(action);
    return { status: 201, body: action };
  });

  PUT('/api/admin/quick-actions/:id', (req: MockRequest): MockResponse => {
    const store = getStore();
    const idx = store.quickActions.actions.findIndex((a: Record<string, unknown>) => a.id === req.params.id);
    if (idx === -1) return { status: 404, body: { detail: 'Quick action not found' } };
    store.quickActions.actions[idx] = { ...store.quickActions.actions[idx], ...req.body, updatedAt: new Date().toISOString() };
    return { status: 200, body: store.quickActions.actions[idx] };
  });

  DELETE('/api/admin/quick-actions/:id', (req: MockRequest): MockResponse => {
    const store = getStore();
    store.quickActions.actions = store.quickActions.actions.filter((a: Record<string, unknown>) => a.id !== req.params.id);
    return { status: 200, body: { success: true } };
  });
}
