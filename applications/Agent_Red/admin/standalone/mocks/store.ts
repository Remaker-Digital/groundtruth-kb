// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
// @ts-nocheck
/**
 * Mock data store — in-memory mutable state for all mock API handlers.
 *
 * Initialized from fixture files on server start. Handlers mutate the store
 * for POST/PUT/DELETE so subsequent GETs reflect changes. Survives HMR
 * because the Vite dev server process stays running.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { createTenantFixture } from './fixtures/tenant';
import { createDashboardFixture } from './fixtures/dashboard';
import { createTeamFixture } from './fixtures/team';
import { createInboxFixture } from './fixtures/inbox';
import { createConfigFixture } from './fixtures/config';
import { createKnowledgeFixture } from './fixtures/knowledge';
import { createQuickActionsFixture } from './fixtures/quick-actions';
import { createWidgetFixture } from './fixtures/widget';
import { createBillingFixture } from './fixtures/billing';
import { createMemoryFixture } from './fixtures/memory';
import { createAgentsFixture } from './fixtures/agents';

export interface MockStore {
  tenant: ReturnType<typeof createTenantFixture>;
  dashboard: ReturnType<typeof createDashboardFixture>;
  team: ReturnType<typeof createTeamFixture>;
  inbox: ReturnType<typeof createInboxFixture>;
  config: ReturnType<typeof createConfigFixture>;
  knowledge: ReturnType<typeof createKnowledgeFixture>;
  quickActions: ReturnType<typeof createQuickActionsFixture>;
  widget: ReturnType<typeof createWidgetFixture>;
  billing: ReturnType<typeof createBillingFixture>;
  memory: ReturnType<typeof createMemoryFixture>;
  agents: ReturnType<typeof createAgentsFixture>;
}

let _store: MockStore | null = null;

/** Get or initialize the singleton store. */
export function getStore(): MockStore {
  if (!_store) {
    _store = {
      tenant: createTenantFixture(),
      dashboard: createDashboardFixture(),
      team: createTeamFixture(),
      inbox: createInboxFixture(),
      config: createConfigFixture(),
      knowledge: createKnowledgeFixture(),
      quickActions: createQuickActionsFixture(),
      widget: createWidgetFixture(),
      billing: createBillingFixture(),
      memory: createMemoryFixture(),
      agents: createAgentsFixture(),
    };
    console.log('[mock] Store initialized with fixture data');
  }
  return _store;
}

/** Reset the store to initial fixture data (for testing). */
export function resetStore(): void {
  _store = null;
}
