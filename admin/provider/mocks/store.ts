// @ts-nocheck
/**
 * Mock data store — Provider admin console.
 *
 * In-memory mutable state for all mock API handlers.
 * Initialized from fixture files on server start.
 *
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { createDashboardFixture } from './fixtures/dashboard';
import { createTenantsFixture } from './fixtures/tenants';
import { createAlertsFixture } from './fixtures/alerts';
import { createIncidentsFixture } from './fixtures/incidents';
import { createCopilotFixture } from './fixtures/copilot';
import { createPipelineFixture } from './fixtures/pipeline';
import { createContactMessagesFixture } from './fixtures/contact-messages';
import { createServiceMessagesFixture } from './fixtures/service-messages';
import { createUserManagementFixture } from './fixtures/user-management';
import { createOperationsFixture } from './fixtures/operations';
import { createComplianceFixture } from './fixtures/compliance';

export interface ProviderMockStore {
  dashboard: ReturnType<typeof createDashboardFixture>;
  tenants: ReturnType<typeof createTenantsFixture>;
  alerts: ReturnType<typeof createAlertsFixture>;
  incidents: ReturnType<typeof createIncidentsFixture>;
  copilot: ReturnType<typeof createCopilotFixture>;
  pipeline: ReturnType<typeof createPipelineFixture>;
  contactMessages: ReturnType<typeof createContactMessagesFixture>;
  serviceMessages: ReturnType<typeof createServiceMessagesFixture>;
  userManagement: ReturnType<typeof createUserManagementFixture>;
  operations: ReturnType<typeof createOperationsFixture>;
  compliance: ReturnType<typeof createComplianceFixture>;
}

let _store: ProviderMockStore | null = null;

export function getStore(): ProviderMockStore {
  if (!_store) {
    _store = {
      dashboard: createDashboardFixture(),
      tenants: createTenantsFixture(),
      alerts: createAlertsFixture(),
      incidents: createIncidentsFixture(),
      copilot: createCopilotFixture(),
      pipeline: createPipelineFixture(),
      contactMessages: createContactMessagesFixture(),
      serviceMessages: createServiceMessagesFixture(),
      userManagement: createUserManagementFixture(),
      operations: createOperationsFixture(),
      compliance: createComplianceFixture(),
    };
    console.log('[mock-provider] Store initialized with fixture data');
  }
  return _store;
}

export function resetStore(): void {
  _store = null;
}
