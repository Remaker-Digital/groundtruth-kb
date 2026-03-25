// @ts-nocheck
/**
 * Tenant fixture — mock data for /api/tenants/lookup and related endpoints.
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
export function createTenantFixture() {
    return {
        lookup: {
            tenant_id: 'mock-tenant-001',
            tier: 'professional',
            status: 'active',
            billing_channel: 'stripe',
            has_stripe_billing: true,
            shopify_shop_domain: null,
            brand_name: 'Mock Store',
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
            email: 'admin@mockstore.com',
            display_name: 'Mock Admin',
            id: 'member-001',
        },
        productVersion: '1.81.2',
    };
}
//# sourceMappingURL=tenant.js.map