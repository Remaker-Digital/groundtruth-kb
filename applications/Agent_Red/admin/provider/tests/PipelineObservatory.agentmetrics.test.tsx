// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * SPEC-1586 Pipeline Observatory — Agent Metrics tab coverage (WI-3222).
 *
 * Deterministic Vitest + React Testing Library coverage for the live
 * `AgentMetricsTab` (PipelineObservatory.tsx). SPEC-1586 is retired but the tab
 * still ships; covered per the in-session owner AskUserQuestion decision. Builds
 * on the Vitest harness established by WI-3221.
 *
 * Failure-path coverage matches live `AgentMetricsTab` semantics (per the -002
 * NO-GO / -003 REVISED): the tab calls `onNotify` ONLY in the catch branch
 * (a thrown/rejected fetch). A resolved `{ ok: false }` response renders the
 * empty state WITHOUT notifying — distinct from the sibling `TrafficFlowTab`.
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

import { AgentMetricsTab } from '../pages/PipelineObservatory';

const topologyFixture = {
  nodes: [
    {
      agent: 'gateway',
      invocationCount: 567,
      avgLatencyMs: 120,
      p50LatencyMs: 100,
      p95LatencyMs: 200,
      p99LatencyMs: 300,
      errorRate: 0.012,
      avgTokensIn: 50,
      avgTokensOut: 30,
      avgCost: 0.0012,
    },
  ],
  edges: [],
  totalConversations: 0,
  period: '24h',
};

function renderTab() {
  return render(
    <MantineProvider>
      <AgentMetricsTab />
    </MantineProvider>,
  );
}

describe('AgentMetricsTab (SPEC-1586)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders per-agent performance cards from the topology API', async () => {
    mockApiFetch.mockResolvedValue({ ok: true, json: async () => topologyFixture });
    renderTab();

    // Agent card renders its invocation count and error-rate badge.
    await screen.findByText('567');
    screen.getByText(/1\.2% errors/);
    expect(mockApiFetch).toHaveBeenCalledWith(expect.stringContaining('/api/superadmin/pipeline/topology'));
  });

  it('notifies and shows the unable-to-load state on a thrown fetch error', async () => {
    mockApiFetch.mockRejectedValue(new Error('network down'));
    renderTab();

    await screen.findByText('Unable to load agent metrics');
    await waitFor(() => {
      expect(mockOnNotify).toHaveBeenCalledWith('Failed to load agent metrics', 'error');
    });
  });

  it('shows the unable-to-load state WITHOUT notifying on a resolved non-ok fetch', async () => {
    // Live AgentMetricsTab only notifies in the catch branch; a resolved
    // non-ok response leaves data null and renders the empty state silently.
    mockApiFetch.mockResolvedValue({ ok: false, json: async () => ({}) });
    renderTab();

    await screen.findByText('Unable to load agent metrics');
    expect(mockOnNotify).not.toHaveBeenCalled();
  });
});
