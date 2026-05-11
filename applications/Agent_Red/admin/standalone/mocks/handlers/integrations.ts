// @ts-nocheck
/**
 * Mock handlers — Integrations endpoints.
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { GET, POST, DELETE } from '../router';
import type { MockRequest, MockResponse } from '../router';

/** Fixture data for available integrations. */
const INTEGRATIONS = [
  {
    type: 'shopify',
    name: 'Shopify',
    description: 'Sync orders, customers, and products from your Shopify store.',
    icon: '🛍️',
    enabled: true,
    status: 'connected',
    tierGate: null,
    tierMet: true,
    comingSoon: false,
  },
  {
    type: 'stripe',
    name: 'Stripe',
    description: 'Process payments, refunds, and manage subscriptions.',
    icon: '💳',
    enabled: false,
    status: 'disconnected',
    tierGate: null,
    tierMet: true,
    comingSoon: false,
  },
  {
    type: 'zendesk',
    name: 'Zendesk',
    description: 'Route escalated conversations to Zendesk tickets.',
    icon: '🎫',
    enabled: false,
    status: 'disconnected',
    tierGate: 'professional',
    tierMet: true,
    comingSoon: false,
  },
  {
    type: 'mailchimp',
    name: 'Mailchimp',
    description: 'Sync customer contacts and manage email campaigns.',
    icon: '📧',
    enabled: false,
    status: null,
    tierGate: 'professional',
    tierMet: true,
    comingSoon: false,
  },
  {
    type: 'google_analytics',
    name: 'Google Analytics',
    description: 'Track widget interactions and conversation events.',
    icon: '📊',
    enabled: false,
    status: null,
    tierGate: null,
    tierMet: true,
    comingSoon: false,
  },
];

// In-memory mutable copy for activate/deactivate
let integrationState = INTEGRATIONS.map((i) => ({ ...i }));

export function registerIntegrationHandlers(): void {
  // List all integrations
  GET('/api/admin/integrations', (_req: MockRequest): MockResponse => {
    return { status: 200, body: integrationState };
  });

  // Get single integration detail
  GET('/api/admin/integrations/:type', (req: MockRequest): MockResponse => {
    const item = integrationState.find((i) => i.type === req.params?.type);
    if (!item) return { status: 404, body: { detail: 'Integration not found' } };
    return { status: 200, body: { ...item, configFields: [] } };
  });

  // Activate integration
  POST('/api/admin/integrations/:type/activate', (req: MockRequest): MockResponse => {
    const item = integrationState.find((i) => i.type === req.params?.type);
    if (!item) return { status: 404, body: { detail: 'Integration not found' } };
    item.enabled = true;
    item.status = 'connected';
    return { status: 200, body: { success: true, message: `${item.name} activated`, integration: item } };
  });

  // Deactivate integration
  POST('/api/admin/integrations/:type/deactivate', (req: MockRequest): MockResponse => {
    const item = integrationState.find((i) => i.type === req.params?.type);
    if (!item) return { status: 404, body: { detail: 'Integration not found' } };
    item.enabled = false;
    item.status = 'disconnected';
    return { status: 200, body: { success: true, message: `${item.name} deactivated`, integration: item } };
  });

  // Disconnect (delete) integration
  DELETE('/api/admin/integrations/:type', (req: MockRequest): MockResponse => {
    const item = integrationState.find((i) => i.type === req.params?.type);
    if (!item) return { status: 404, body: { detail: 'Integration not found' } };
    item.enabled = false;
    item.status = 'disconnected';
    return { status: 200, body: { success: true, message: `${item.name} disconnected`, integration: item } };
  });

  // Stripe credentials (for McpConfigPanel)
  GET('/api/admin/integrations/stripe/credentials', (_req: MockRequest): MockResponse => {
    return { status: 200, body: { hasCredentials: false, publishableKey: null } };
  });

  POST('/api/admin/integrations/stripe/credentials', (_req: MockRequest): MockResponse => {
    return { status: 200, body: { success: true, message: 'Stripe credentials saved' } };
  });

  POST('/api/admin/integrations/stripe/test', (_req: MockRequest): MockResponse => {
    return { status: 200, body: { success: true, message: 'Stripe connection verified' } };
  });
}
