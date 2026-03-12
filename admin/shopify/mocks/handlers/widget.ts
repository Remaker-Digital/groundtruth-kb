// @ts-nocheck
/**
 * Mock handlers — Widget endpoints.
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { GET, POST } from '../router';
import { getStore } from '../store';
import type { MockRequest, MockResponse } from '../router';

export function registerWidgetHandlers(): void {
  const s = () => getStore().widget;

  GET('/api/admin/widget/embed-code', (_req: MockRequest): MockResponse => {
    return { status: 200, body: { embedCode: s().embedCode } };
  });

  GET('/api/admin/widget/preview-config', (_req: MockRequest): MockResponse => {
    return { status: 200, body: s().previewConfig };
  });

  POST('/api/admin/widget/test', (_req: MockRequest): MockResponse => {
    return { status: 200, body: { success: true, message: 'Widget test message sent' } };
  });

  GET('/widget.js', (_req: MockRequest): MockResponse => {
    return {
      status: 200,
      body: '/* Mock widget.js */',
      headers: { 'Content-Type': 'application/javascript' },
    };
  });
}
