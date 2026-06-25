// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * SPEC-1587 Pipeline Observatory — Tenant Comparison tab coverage (WI-3223).
 *
 * Deterministic Vitest + React Testing Library component coverage for the live
 * `TenantComparisonTab` in pages/PipelineObservatory.tsx. The provider context
 * (`apiFetch`/`onNotify`) is mocked so the tab's tenants fetch is driven by a
 * fixture; Mantine renders under happy-dom via tests/setup.ts. Reuses the Vitest
 * harness committed by WI-3221. SPEC-1587 is retired but the tab still ships;
 * covered per the in-session owner AskUserQuestion decision.
 *
 * Maps the stale e2e tests TEST-2775/TEST-2776/TEST-2777 to executable evidence.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MantineProvider } from '@mantine/core';

const { mockApiFetch, mockOnNotify } = vi.hoisted(() => ({
  mockApiFetch: vi.fn(),
  mockOnNotify: vi.fn(),
}));

vi.mock('../layouts/ProviderLayout', () => ({
  useProviderContext: () => ({ apiFetch: mockApiFetch, onNotify: mockOnNotify }),
}));

import { TenantComparisonTab } from '../pages/PipelineObservatory';

const tenantsFixture = {
  tenants: [
    {
      tenantId: 'tnt-acme',
      displayName: 'Acme Corp',
      tier: 'professional',
      totalConversations: 1234,
      billableConversations: 1200,
      avgLatencyMs: 150,
      errorRate: 0.02,
      escalationRate: 0.05,
      tokenConsumption: 50000,
      cost: 12.34,
      estimatedRu: 999,
      resolutionRate: 0.9,
    },
  ],
  total: 1,
  sortBy: 'totalConversations',
  sortOrder: 'desc',
};

function renderTab() {
  return render(
    <MantineProvider>
      <TenantComparisonTab />
    </MantineProvider>,
  );
}

describe('TenantComparisonTab (SPEC-1587)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the tenant comparison table from the tenants API', async () => {
    mockApiFetch.mockResolvedValue({ ok: true, json: async () => tenantsFixture });
    renderTab();

    // Tenant row renders its display name and total-conversation count.
    await screen.findByText('Acme Corp');
    screen.getByText('1234');
    expect(mockApiFetch).toHaveBeenCalledWith(expect.stringContaining('/api/superadmin/pipeline/tenants'));
  });

  it('surfaces an error notification on a non-ok tenants fetch', async () => {
    mockApiFetch.mockResolvedValue({ ok: false, json: async () => ({}) });
    renderTab();

    await screen.findByText('Unable to load tenant comparison');
    await waitFor(() => {
      expect(mockOnNotify).toHaveBeenCalledWith('Failed to load tenant comparison', 'error');
    });
  });
});
