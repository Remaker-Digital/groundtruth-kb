// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * SPEC-1585 Pipeline Observatory — Traffic Flow tab coverage (WI-3221).
 *
 * Deterministic Vitest + React Testing Library component coverage for the live
 * `TrafficFlowTab` in pages/PipelineObservatory.tsx. The provider context
 * (`apiFetch`/`onNotify`) is mocked so the tab's topology fetch is driven by a
 * fixture; Mantine renders under happy-dom via tests/setup.ts.
 *
 * Maps the stale e2e tests TEST-2771 (topology render) and TEST-2772
 * (invocation counts on edges) to executable component evidence.
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

import { TrafficFlowTab } from '../pages/PipelineObservatory';

const topologyFixture = {
  nodes: [
    {
      agent: 'gateway',
      invocationCount: 567,
      avgLatencyMs: 120,
      p50LatencyMs: 100,
      p95LatencyMs: 200,
      p99LatencyMs: 300,
      errorRate: 0.01,
      avgTokensIn: 50,
      avgTokensOut: 30,
      avgCost: 0.0012,
    },
  ],
  edges: [
    {
      source: 'gateway',
      target: 'sales',
      volume: 89,
      avgTransitionLatencyMs: 45,
      dropOffRate: 0.05,
    },
  ],
  totalConversations: 1234,
  period: '24h',
};

function renderTab() {
  return render(
    <MantineProvider>
      <TrafficFlowTab />
    </MantineProvider>,
  );
}

describe('TrafficFlowTab (SPEC-1585)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the agent topology from the topology API (TEST-2771)', async () => {
    mockApiFetch.mockResolvedValue({ ok: true, json: async () => topologyFixture });
    renderTab();

    // Total-conversations summary renders the fetched value.
    await screen.findByText('1234');
    // Agent node card renders its invocation count.
    screen.getByText('567');
    // The tab fetched the topology endpoint.
    expect(mockApiFetch).toHaveBeenCalledWith(expect.stringContaining('/api/superadmin/pipeline/topology'));
  });

  it('renders agent-to-agent transition volumes (TEST-2772)', async () => {
    mockApiFetch.mockResolvedValue({ ok: true, json: async () => topologyFixture });
    renderTab();

    // Edge transition volume appears in the agent-to-agent table.
    await screen.findByText('89');
  });

  it('surfaces an error notification on a failed topology fetch', async () => {
    mockApiFetch.mockResolvedValue({ ok: false, json: async () => ({}) });
    renderTab();

    await screen.findByText('Unable to load topology');
    await waitFor(() => {
      expect(mockOnNotify).toHaveBeenCalledWith('Failed to load topology', 'error');
    });
  });
});
