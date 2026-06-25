// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * SPEC-1841 Deployment modal — recommended next-version pre-fill coverage (WI-3224).
 *
 * Deterministic Vitest + React Testing Library coverage for the live
 * `suggestNextVersion` pure function and the `DeploymentManagementPage` trigger
 * modal, which pre-fills the Version input with the recommended next version and
 * surfaces the last successful deployment. The provider context
 * (`apiFetch`/`onNotify`) is mocked; Mantine renders under happy-dom via
 * tests/setup.ts. Reuses the Vitest harness committed by WI-3221.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MantineProvider } from '@mantine/core';

const { mockApiFetch, mockOnNotify } = vi.hoisted(() => ({
  mockApiFetch: vi.fn(),
  mockOnNotify: vi.fn(),
}));

vi.mock('../layouts/ProviderLayout', () => ({
  useProviderContext: () => ({ apiFetch: mockApiFetch, onNotify: mockOnNotify }),
}));

import { suggestNextVersion, DeploymentManagementPage } from '../pages/DeploymentManagement';

// ===========================================================================
// Pure function: recommended next version (SPEC-1841)
// ===========================================================================

describe('suggestNextVersion (SPEC-1841)', () => {
  it('bumps the patch version across supported formats', () => {
    expect(suggestNextVersion('v1.98.15')).toBe('v1.98.16');
    expect(suggestNextVersion('1.98.15')).toBe('1.98.16');
    expect(suggestNextVersion('v1.98')).toBe('v1.98.0');
  });

  it('returns an empty string for unparseable input', () => {
    expect(suggestNextVersion('not-a-version')).toBe('');
    expect(suggestNextVersion('')).toBe('');
  });
});

// ===========================================================================
// Modal pre-fill + last-deployed display (SPEC-1841)
// ===========================================================================

const deploymentsFixture = {
  deployments: [
    {
      deployId: 'dep-1',
      environment: 'production',
      version: 'v1.98.15',
      action: 'full',
      status: 'succeeded',
      triggeredBy: 'deploy-bot',
      startedAt: '2026-06-01T00:00:00Z',
      completedAt: '2026-06-01T00:05:00Z',
      durationS: 300,
      steps: [],
      error: null,
      previousImage: null,
    },
  ],
  total: 1,
};

describe('DeploymentManagementPage version pre-fill (SPEC-1841)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('pre-fills the trigger modal with the suggested next version and shows the last deployment', async () => {
    mockApiFetch.mockResolvedValue({ ok: true, json: async () => deploymentsFixture });
    render(
      <MantineProvider>
        <DeploymentManagementPage />
      </MantineProvider>,
    );

    // Wait for the deployments to load — the last succeeded version drives the suggestion.
    await screen.findByText('v1.98.15');

    // Open the trigger modal.
    fireEvent.click(screen.getByText('Trigger Pipeline'));

    // The Version input is pre-filled with the suggested next version (v1.98.15 -> v1.98.16).
    await screen.findByDisplayValue('v1.98.16');
    // The modal surfaces the last successful deployment version.
    screen.getByText(/Last successful deployment: v1\.98\.15/);
  });
});
