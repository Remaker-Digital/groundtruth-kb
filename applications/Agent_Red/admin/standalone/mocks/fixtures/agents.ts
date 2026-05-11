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
      visibilityScope: 'public',
      staffDomainTags: [],
      updatedAt: NOW,
    },
    'sales': {
      agentId: 'sales',
      enabled: true,
      promptOverrides: {},
      skillOverrides: {},
      customMetadata: {},
      visibilityScope: 'private',
      staffDomainTags: ['sales-dept', 'commerce'],
      updatedAt: NOW,
    },
    'gateway': {
      agentId: 'gateway',
      enabled: false,
      promptOverrides: {},
      skillOverrides: {},
      customMetadata: {},
      visibilityScope: 'public',
      staffDomainTags: [],
      updatedAt: NOW,
    },
  };

  const agents = [
    { agentId: 'intent-classifier', displayName: 'Intent Classifier', description: 'Classifies customer intent from conversation context', agentKind: 'core', category: 'core-pipeline', hasOverlay: false, enabled: true },
    { agentId: 'knowledge-retrieval', displayName: 'Knowledge Retrieval', description: 'Retrieves relevant knowledge articles for response generation', agentKind: 'core', category: 'core-pipeline', hasOverlay: false, enabled: true },
    { agentId: 'response-generator', displayName: 'Response Generator', description: 'Generates customer-facing responses from knowledge and context', agentKind: 'core', category: 'core-pipeline', hasOverlay: false, enabled: true },
    { agentId: 'campaigns', displayName: 'Campaigns Agent', description: 'Marketing campaign information and promotional content', agentKind: 'peer', category: 'marketing', hasOverlay: true, enabled: true },
    { agentId: 'sales', displayName: 'Sales Agent', description: 'In-line product discovery and purchase completion', agentKind: 'peer', category: 'commerce', hasOverlay: true, enabled: true },
    { agentId: 'gateway', displayName: 'Gateway Agent', description: 'Human escalation and live agent connection', agentKind: 'peer', category: 'escalation', hasOverlay: true, enabled: false },
    { agentId: 'stripe_mcp', displayName: 'Stripe MCP', description: 'Payments, refunds, subscriptions via Stripe MCP server', agentKind: 'peer', category: 'external', hasOverlay: false, enabled: true },
    { agentId: 'shopify_mcp', displayName: 'Shopify Storefront MCP', description: 'Product catalog, orders, fulfillment via Shopify MCP', agentKind: 'peer', category: 'external', hasOverlay: false, enabled: true },
    { agentId: 'zendesk', displayName: 'Zendesk', description: 'Helpdesk ticket sync and customer support integration via Zendesk', agentKind: 'peer', category: 'integration', hasOverlay: false, enabled: true },
    { agentId: 'slack', displayName: 'Slack', description: 'Channel messaging and team notification integration via Slack', agentKind: 'peer', category: 'integration', hasOverlay: false, enabled: true },
    { agentId: 'google_docs', displayName: 'Google Docs', description: 'Knowledge ingestion and document sync from Google Docs', agentKind: 'peer', category: 'integration', hasOverlay: false, enabled: true },
  ];

  const bindings = [
    { agentId: 'campaigns', skillId: 'campaigns:list-active', credentialRef: null, mode: 'read', approvalPolicy: 'auto', enabled: true },
    { agentId: 'campaigns', skillId: 'campaigns:get-discount-codes', credentialRef: null, mode: 'read', approvalPolicy: 'auto', enabled: true },
    { agentId: 'sales', skillId: 'sales:search-products', credentialRef: 'vault://mock/shopify-key', mode: 'read', approvalPolicy: 'auto', enabled: true },
  ];

  const availableSkills = [
    { skillId: 'campaigns:list-active', displayName: 'List Active Campaigns', description: 'List currently active marketing campaigns', mode: 'read', enabled: true, credentialRef: null },
    { skillId: 'campaigns:get-discount-codes', displayName: 'Get Discount Codes', description: 'Retrieve discount codes for a campaign', mode: 'read', enabled: true, credentialRef: null },
    { skillId: 'campaigns:get-talking-points', displayName: 'Get Talking Points', description: 'Retrieve talking points for a campaign', mode: 'read', enabled: true, credentialRef: null },
    { skillId: 'campaigns:track-metrics', displayName: 'Track Metrics', description: 'Record campaign interaction metrics', mode: 'mutate', enabled: true, credentialRef: null },
    { skillId: 'sales:search-products', displayName: 'Search Products', description: 'Search the product catalog', mode: 'read', enabled: true, credentialRef: null },
    { skillId: 'sales:manage-cart', displayName: 'Manage Cart', description: 'Add, remove, or update cart items', mode: 'mutate', enabled: true, credentialRef: null },
    { skillId: 'sales:check-inventory', displayName: 'Check Inventory', description: 'Check product availability and stock levels', mode: 'read', enabled: true, credentialRef: null },
    { skillId: 'sales:create-checkout', displayName: 'Create Checkout', description: 'Create a checkout session for the customer', mode: 'mutate', enabled: true, credentialRef: null },
    { skillId: 'sales:track-order', displayName: 'Track Order', description: 'Look up order status and tracking information', mode: 'read', enabled: true, credentialRef: null },
    { skillId: 'stripe_mcp:get-balance', displayName: 'Get Balance', description: 'Retrieve Stripe account balance', mode: 'read', enabled: true, credentialRef: null },
    { skillId: 'stripe_mcp:list-charges', displayName: 'List Charges', description: 'List recent Stripe charges', mode: 'read', enabled: true, credentialRef: null },
    { skillId: 'zendesk:sync-tickets', displayName: 'Sync Tickets', description: 'Synchronize helpdesk tickets from Zendesk', mode: 'read', enabled: true, credentialRef: null },
    { skillId: 'zendesk:create-ticket', displayName: 'Create Ticket', description: 'Create a new support ticket in Zendesk', mode: 'mutate', enabled: true, credentialRef: null },
    { skillId: 'slack:send-message', displayName: 'Send Message', description: 'Send a message to a Slack channel', mode: 'mutate', enabled: true, credentialRef: null },
    { skillId: 'google_docs:ingest-document', displayName: 'Ingest Document', description: 'Import a Google Doc into the knowledge base', mode: 'mutate', enabled: true, credentialRef: null },
  ];

  return { agents, overlays, bindings, availableSkills };
}
