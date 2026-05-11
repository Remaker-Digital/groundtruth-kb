// @ts-nocheck
/**
 * Mock handlers — Memory & Privacy endpoints.
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { GET, PUT } from '../router';
import { getStore } from '../store';
import type { MockRequest, MockResponse } from '../router';

export function registerMemoryHandlers(): void {
  const s = () => getStore().memory.settings;

  GET('/api/admin/memory', (_req: MockRequest): MockResponse => {
    return {
      status: 200,
      body: {
        layers: s().layers,
        privacySettings: {
          memoryEnabled: s().memoryEnabled,
          retentionDays: s().retentionDays,
          piiMaskingEnabled: s().piiMaskingEnabled,
          gdprCompliant: s().gdprCompliant,
        },
      },
    };
  });

  PUT('/api/admin/memory', (req: MockRequest): MockResponse => {
    const store = getStore();
    const settings = store.memory.settings;
    if (req.body?.layers) settings.layers = req.body.layers;
    if (req.body?.privacySettings) {
      Object.assign(settings, req.body.privacySettings);
    }
    return {
      status: 200,
      body: {
        layers: settings.layers,
        privacySettings: {
          memoryEnabled: settings.memoryEnabled,
          retentionDays: settings.retentionDays,
          piiMaskingEnabled: settings.piiMaskingEnabled,
          gdprCompliant: settings.gdprCompliant,
        },
      },
    };
  });

  GET('/api/admin/memory/stats', (_req: MockRequest): MockResponse => {
    return {
      status: 200,
      body: {
        totalMemories: 142, activeCustomers: 38,
        avgMemoriesPerCustomer: 3.7, storageUsedBytes: 524288,
      },
    };
  });
}
