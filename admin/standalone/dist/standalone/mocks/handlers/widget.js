// @ts-nocheck
/**
 * Mock handlers — Widget endpoints.
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { GET, POST } from '../router';
import { getStore } from '../store';
export function registerWidgetHandlers() {
    const s = () => getStore().widget;
    GET('/api/admin/widget/embed-code', (_req) => {
        return { status: 200, body: { embedCode: s().embedCode, widgetKey: s().widgetKey } };
    });
    GET('/api/admin/widget/preview-config', (_req) => {
        return { status: 200, body: s().previewConfig };
    });
    POST('/api/admin/widget/test', (_req) => {
        return { status: 200, body: { success: true, message: 'Widget test message sent' } };
    });
    // Widget JS file (returns a minimal placeholder)
    GET('/widget.js', (_req) => {
        return {
            status: 200,
            body: '/* Mock widget.js */',
            headers: { 'Content-Type': 'application/javascript' },
        };
    });
}
//# sourceMappingURL=widget.js.map