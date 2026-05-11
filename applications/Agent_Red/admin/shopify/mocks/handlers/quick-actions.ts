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

  // Assignment endpoints (MUST register before /:id routes)
  GET('/api/admin/quick-actions/assignments', (_req: MockRequest): MockResponse => {
    const store = getStore();
    const actions = store.quickActions.actions;
    const assignments = store.quickActions.assignments.map((a: Record<string, unknown>) => ({
      ...a,
      slot1Action: a.slot1ActionId ? actions.find((act: Record<string, unknown>) => act.id === a.slot1ActionId) || null : null,
      slot2Action: a.slot2ActionId ? actions.find((act: Record<string, unknown>) => act.id === a.slot2ActionId) || null : null,
    }));
    return { status: 200, body: { assignments } };
  });

  PUT('/api/admin/quick-actions/assignments', (req: MockRequest): MockResponse => {
    const store = getStore();
    const body = req.body as Record<string, unknown>;
    const pageType = body.page_type as string;
    const idx = store.quickActions.assignments.findIndex((a: Record<string, unknown>) => a.pageType === pageType);
    const updated = {
      pageType,
      pageHandle: body.page_handle ?? null,
      slot1ActionId: body.slot_1_action_id ?? null,
      slot2ActionId: body.slot_2_action_id ?? null,
      autoOpen: body.auto_open ?? false,
      autoOpenDelayMs: body.auto_open_delay_ms ?? 3000,
    };
    if (idx === -1) {
      store.quickActions.assignments.push(updated);
    } else {
      store.quickActions.assignments[idx] = updated;
    }
    const actions = store.quickActions.actions;
    return {
      status: 200,
      body: {
        ...updated,
        slot1Action: updated.slot1ActionId ? actions.find((a: Record<string, unknown>) => a.id === updated.slot1ActionId) || null : null,
        slot2Action: updated.slot2ActionId ? actions.find((a: Record<string, unknown>) => a.id === updated.slot2ActionId) || null : null,
      },
    };
  });

  DELETE('/api/admin/quick-actions/assignments/:pageType', (req: MockRequest): MockResponse => {
    const store = getStore();
    store.quickActions.assignments = store.quickActions.assignments.filter(
      (a: Record<string, unknown>) => a.pageType !== req.params.pageType,
    );
    return { status: 200, body: { success: true } };
  });

  // Action CRUD endpoints
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
