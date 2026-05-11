// @ts-nocheck
/**
 * Shopify tenant handlers - lookup (with found flag), activation status, whoami.
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { GET, POST } from '../router';
import { getStore, resetStore } from '../store';

export function registerTenantHandlers() {
  const s = () => getStore().tenant;

  // Shopify tenant lookup — returns `found: true` (ShopifyAppLayout checks this)
  GET('/api/tenants/lookup', () => ({
    status: 200,
    body: s().lookup,
  }));

  GET('/api/admin/team/whoami', () => ({
    status: 200,
    body: s().whoami,
  }));

  GET('/api/admin/product-version', () => ({
    status: 200,
    body: { version: s().productVersion },
  }));

  GET('/api/health', () => ({
    status: 200,
    body: { status: 'healthy', product_version: s().productVersion },
  }));

  // GDPR data export (Settings page)
  POST('/api/admin/gdpr/export', () => ({
    status: 200,
    body: { success: true, message: 'Data export initiated. You will receive a download link.' },
  }));

  // Test-only: reset store to initial fixture data
  POST('/api/__test__/reset', () => {
    resetStore();
    return { status: 200, body: { success: true, message: 'Store reset to fixture data' } };
  });
}
