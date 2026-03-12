// @ts-nocheck
/**
 * Shopify tenant fixture — mock data for /api/tenants/lookup (with shop domain).
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

export function createTenantFixture() {
  return {
    lookup: {
      found: true,
      tenant_id: 'mock-shopify-tenant-001',
      tier: 'professional',
      status: 'active',
      billing_channel: 'shopify',
      has_stripe_billing: false,
      shopify_shop_domain: 'mock-store.myshopify.com',
      brand_name: 'Mock Shopify Store',
    },
    activationStatus: {
      has_pending_changes: false,
      active_version: 3,
      active_activated_at: '2026-03-01T12:00:00Z',
      draft_version: 4,
      is_configured: true,
      is_active: true,
      can_activate: true,
    },
    whoami: {
      role: 'superadmin',
      email: 'merchant@mock-store.myshopify.com',
      display_name: 'Shop Owner',
      id: 'member-001',
    },
    productVersion: '1.82.0',
  };
}
