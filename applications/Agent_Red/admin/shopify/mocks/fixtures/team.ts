// @ts-nocheck
/**
 * Team fixture — team members with roles and escalation categories.
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

export function createTeamFixture() {
  return {
    members: [
      {
        id: 'member-001',
        tenantId: 'mock-shopify-tenant-001',
        email: 'merchant@mock-store.myshopify.com',
        displayName: 'Shop Owner',
        role: 'superadmin',
        isActive: true,
        maxConcurrentConversations: 10,
        escalationCategories: ['sales', 'support', 'service', 'account', 'technical', 'general'],
        userApiKeyPrefix: 'ar_user_mock...',
        userApiKey: null,
        createdAt: '2025-11-15T08:00:00Z',
        updatedAt: '2026-03-01T10:30:00Z',
        lastLoginAt: '2026-03-10T09:15:00Z',
        invitedBy: null,
        unresolvedEscalationCount: 1,
      },
      {
        id: 'member-002',
        tenantId: 'mock-shopify-tenant-001',
        email: 'support@mock-store.myshopify.com',
        displayName: 'Support Staff',
        role: 'escalation_agent',
        isActive: true,
        maxConcurrentConversations: 8,
        escalationCategories: ['support', 'technical'],
        userApiKeyPrefix: 'ar_user_mock...',
        userApiKey: null,
        createdAt: '2026-01-10T14:00:00Z',
        updatedAt: '2026-02-28T16:45:00Z',
        lastLoginAt: '2026-03-09T11:30:00Z',
        invitedBy: 'merchant@mock-store.myshopify.com',
        unresolvedEscalationCount: 3,
      },
    ],
    nextId: 3,
  };
}
