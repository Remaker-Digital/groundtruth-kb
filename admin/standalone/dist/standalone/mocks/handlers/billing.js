// @ts-nocheck
/**
 * Mock handlers — Billing / Account endpoints.
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { GET, POST, PUT } from '../router';
import { getStore } from '../store';
export function registerBillingHandlers() {
    const s = () => getStore().billing;
    GET('/api/billing/status', (_req) => {
        return { status: 200, body: s().status };
    });
    GET('/api/billing/packs', (_req) => {
        return { status: 200, body: { balance: 5, packs: [] } };
    });
    GET('/api/admin/contact-preferences', (_req) => {
        return { status: 200, body: s().contactPreferences };
    });
    PUT('/api/admin/contact-preferences', (req) => {
        const store = getStore();
        store.billing.contactPreferences = { ...store.billing.contactPreferences, ...req.body };
        return { status: 200, body: store.billing.contactPreferences };
    });
    // Email change request/confirm
    POST('/api/admin/email/request', (req) => {
        return { status: 200, body: { success: true, message: 'Verification email sent to ' + (req.body?.newEmail ?? 'unknown') } };
    });
    POST('/api/admin/email/confirm', (_req) => {
        return { status: 200, body: { success: true, message: 'Email updated successfully' } };
    });
}
//# sourceMappingURL=billing.js.map