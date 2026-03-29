// @ts-nocheck
/**
 * Agent fixture data — mock agents, overlays, bindings, and available skills.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

const NOW = new Date().toISOString();

export function createAgentsFixture() {
  const overlays: Record<string, any> = {
    'campaigns': {
      agentId: 'campaigns',
      enabled: true,
      promptOverrides: {},
      skillOverrides: {},
      customMetadata: {},
      updatedAt: NOW,
    },
    'sales': {
      agentId: 'sales',
      enabled: true,
      promptOverrides: {},
      skillOverrides: {},
      customMetadata: {},
      updatedAt: NOW,
    },
    'gateway': {
      agentId: 'gateway',
      enabled: false,
      promptOverrides: {},
      skillOverrides: {},
      customMetadata: {},
      updatedAt: NOW,
    },
  };

  const agents = [
    { agentId: 'campaigns', displayName: 'Campaigns Agent', agentKind: 'conversational', hasOverlay: true, enabled: true },
    { agentId: 'sales', displayName: 'Sales Agent', agentKind: 'conversational', hasOverlay: true, enabled: true },
    { agentId: 'bot-agent', displayName: 'Bot Agent', agentKind: 'a2a', hasOverlay: false, enabled: true },
    { agentId: 'gateway', displayName: 'Gateway Agent', agentKind: 'routing', hasOverlay: true, enabled: false },
    { agentId: 'schedule', displayName: 'Schedule Agent', agentKind: 'conversational', hasOverlay: false, enabled: true },
    { agentId: 'knowledge-retrieval', displayName: 'Knowledge Retrieval', agentKind: 'internal', hasOverlay: false, enabled: true },
    { agentId: 'external-mcp', displayName: 'External MCP', agentKind: 'external', hasOverlay: false, enabled: true },
  ];

  const bindings = [
    { agentId: 'campaigns', skillId: 'campaigns:list-active', credentialRef: null, mode: 'read', approvalPolicy: 'auto', enabled: true },
    { agentId: 'campaigns', skillId: 'campaigns:get-discount-codes', credentialRef: null, mode: 'read', approvalPolicy: 'auto', enabled: true },
    { agentId: 'campaigns', skillId: 'campaigns:get-talking-points', credentialRef: null, mode: 'read', approvalPolicy: 'auto', enabled: true },
    { agentId: 'sales', skillId: 'sales:search-products', credentialRef: 'vault://mock/shopify-key', mode: 'read', approvalPolicy: 'auto', enabled: true },
    { agentId: 'sales', skillId: 'sales:manage-cart', credentialRef: 'vault://mock/shopify-key', mode: 'read', approvalPolicy: 'require_confirmation', enabled: true },
  ];

  const availableSkills = [
    { skillId: 'campaigns:list-active', displayName: 'List Active Campaigns', mode: 'read', enabled: true, credentialRef: null },
    { skillId: 'campaigns:get-discount-codes', displayName: 'Get Discount Codes', mode: 'read', enabled: true, credentialRef: null },
    { skillId: 'campaigns:get-talking-points', displayName: 'Get Talking Points', mode: 'read', enabled: true, credentialRef: null },
    { skillId: 'campaigns:track-metrics', displayName: 'Track Metrics', mode: 'read', enabled: true, credentialRef: null },
    { skillId: 'sales:search-products', displayName: 'Search Products', mode: 'read', enabled: true, credentialRef: null },
    { skillId: 'sales:manage-cart', displayName: 'Manage Cart', mode: 'read', enabled: true, credentialRef: null },
    { skillId: 'sales:check-inventory', displayName: 'Check Inventory', mode: 'read', enabled: true, credentialRef: null },
    { skillId: 'sales:order-tracking', displayName: 'Order Tracking', mode: 'read', enabled: true, credentialRef: null },
    { skillId: 'gateway:check-availability', displayName: 'Check Availability', mode: 'read', enabled: true, credentialRef: null },
    { skillId: 'schedule:create-followup', displayName: 'Create Follow-up', mode: 'read', enabled: true, credentialRef: null },
  ];

  return { agents, overlays, bindings, availableSkills };
}
