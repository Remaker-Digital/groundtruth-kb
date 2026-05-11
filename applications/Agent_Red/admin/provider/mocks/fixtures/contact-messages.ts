// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * Provider contact messages fixture.
 *
 * Shape must match the ContactMessage interface in ContactMessages.tsx:
 *   - `message` (not `body`)
 *   - `memberEmail` (not `email`)
 *   - `memberRole`, `memberId`, `tier`, `updatedAt`
 *   - status: new | read | resolved | archived
 *   - topic: support | feature_request | billing | bug_report | general
 *
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
export function createContactMessagesFixture() {
  return {
    messages: [
      {
        id: 'cm-001',
        tenantId: 'acme-corp-001',
        topic: 'billing',
        subject: 'Invoice question',
        message: 'I have a question about our latest invoice. The amount seems higher than expected.',
        memberEmail: 'sarah@acme-corp.com',
        memberRole: 'admin',
        memberId: 'member-acme-001',
        tier: 'professional',
        status: 'new',
        notes: '',
        createdAt: '2026-03-10T14:30:00Z',
        updatedAt: '2026-03-10T14:30:00Z',
      },
      {
        id: 'cm-002',
        tenantId: 'blanco-9939',
        topic: 'bug_report',
        subject: 'Widget not loading on mobile',
        message: 'The chat widget doesn\'t appear on our mobile site. Works fine on desktop.',
        memberEmail: 'mike@blanco.com',
        memberRole: 'owner',
        memberId: 'member-blanco-001',
        tier: 'professional',
        status: 'read',
        notes: 'Investigating viewport detection',
        createdAt: '2026-03-09T09:15:00Z',
        updatedAt: '2026-03-09T11:30:00Z',
      },
      {
        id: 'cm-003',
        tenantId: 'trial-user-001',
        topic: 'general',
        subject: 'Upgrading from trial',
        message: 'We love the product! What are the pricing options for upgrading from our trial?',
        memberEmail: 'emily@newshop.com',
        memberRole: 'admin',
        memberId: 'member-trial-001',
        tier: 'trial',
        status: 'resolved',
        notes: 'Sent pricing sheet',
        createdAt: '2026-03-07T16:45:00Z',
        updatedAt: '2026-03-08T09:00:00Z',
      },
      {
        id: 'cm-004',
        tenantId: 'harrison-001',
        topic: 'feature_request',
        subject: 'Multi-language support',
        message: 'Our customers speak Spanish and French. Any plans for multi-language responses?',
        memberEmail: 'roger@harrisoncorp.com',
        memberRole: 'member',
        memberId: 'member-harrison-001',
        tier: 'starter',
        status: 'new',
        notes: '',
        createdAt: '2026-03-06T11:00:00Z',
        updatedAt: '2026-03-06T11:00:00Z',
      },
    ],
    total: 4,
  };
}
