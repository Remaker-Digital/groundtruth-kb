// @ts-nocheck
/**
 * Mock handlers — Quick Actions endpoints.
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { GET, POST, PUT, DELETE } from '../router';
import { getStore } from '../store';
export function registerQuickActionHandlers() {
    const s = () => getStore().quickActions;
    // ---- Assignment endpoints (MUST register before /:id routes) ---------------
    GET('/api/admin/quick-actions/assignments', (_req) => {
        const store = getStore();
        const actions = store.quickActions.actions;
        // Enrich assignments with resolved action objects
        const assignments = store.quickActions.assignments.map((a) => ({
            ...a,
            slot1Action: a.slot1ActionId ? actions.find((act) => act.id === a.slot1ActionId) || null : null,
            slot2Action: a.slot2ActionId ? actions.find((act) => act.id === a.slot2ActionId) || null : null,
        }));
        return { status: 200, body: { assignments } };
    });
    PUT('/api/admin/quick-actions/assignments', (req) => {
        const store = getStore();
        const body = req.body;
        const pageType = body.page_type;
        const idx = store.quickActions.assignments.findIndex((a) => a.pageType === pageType);
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
        }
        else {
            store.quickActions.assignments[idx] = updated;
        }
        const actions = store.quickActions.actions;
        return {
            status: 200,
            body: {
                ...updated,
                slot1Action: updated.slot1ActionId ? actions.find((a) => a.id === updated.slot1ActionId) || null : null,
                slot2Action: updated.slot2ActionId ? actions.find((a) => a.id === updated.slot2ActionId) || null : null,
            },
        };
    });
    DELETE('/api/admin/quick-actions/assignments/:pageType', (req) => {
        const store = getStore();
        store.quickActions.assignments = store.quickActions.assignments.filter((a) => a.pageType !== req.params.pageType);
        return { status: 200, body: { success: true } };
    });
    // ---- Action CRUD endpoints ------------------------------------------------
    GET('/api/admin/quick-actions', (_req) => {
        return { status: 200, body: { actions: s().actions } };
    });
    POST('/api/admin/quick-actions', (req) => {
        const store = getStore();
        const id = 'qa-' + String(store.quickActions.actions.length + 1).padStart(3, '0');
        const action = { id, ...req.body, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() };
        store.quickActions.actions.push(action);
        return { status: 201, body: action };
    });
    PUT('/api/admin/quick-actions/:id', (req) => {
        const store = getStore();
        const idx = store.quickActions.actions.findIndex((a) => a.id === req.params.id);
        if (idx === -1)
            return { status: 404, body: { detail: 'Quick action not found' } };
        store.quickActions.actions[idx] = { ...store.quickActions.actions[idx], ...req.body, updatedAt: new Date().toISOString() };
        return { status: 200, body: store.quickActions.actions[idx] };
    });
    DELETE('/api/admin/quick-actions/:id', (req) => {
        const store = getStore();
        store.quickActions.actions = store.quickActions.actions.filter((a) => a.id !== req.params.id);
        return { status: 200, body: { success: true } };
    });
}
//# sourceMappingURL=quick-actions.js.map