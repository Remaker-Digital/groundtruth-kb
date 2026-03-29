// @ts-nocheck
/**
 * Mock API barrel export — registers all handlers with the router.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { registerTenantHandlers } from './handlers/tenant';
import { registerDashboardHandlers } from './handlers/dashboard';
import { registerTeamHandlers } from './handlers/team';
import { registerInboxHandlers } from './handlers/inbox';
import { registerConfigHandlers } from './handlers/config';
import { registerKnowledgeHandlers } from './handlers/knowledge';
import { registerQuickActionHandlers } from './handlers/quick-actions';
import { registerWidgetHandlers } from './handlers/widget';
import { registerBillingHandlers } from './handlers/billing';
import { registerMemoryHandlers } from './handlers/memory';
import { registerIntegrationHandlers } from './handlers/integrations';
import { registerAgentHandlers } from './handlers/agents';

let registered = false;

/**
 * Idempotent registration of all mock API handlers.
 * Called once when the Vite dev server starts in mock mode.
 */
export function registerAllHandlers(): void {
  if (registered) return;

  registerTenantHandlers();
  registerDashboardHandlers();
  registerTeamHandlers();
  registerInboxHandlers();
  registerConfigHandlers();
  registerKnowledgeHandlers();
  registerQuickActionHandlers();
  registerWidgetHandlers();
  registerBillingHandlers();
  registerMemoryHandlers();
  registerIntegrationHandlers();
  registerAgentHandlers();

  registered = true;
  console.log('[mock] All API handlers registered');
}

// Re-export plugin for vite.config.ts to import
export { mockApiPlugin } from './plugin';
