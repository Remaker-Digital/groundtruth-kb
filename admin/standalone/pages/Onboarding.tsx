/**
 * Onboarding page — Standalone admin.
 *
 * Wraps the shared OnboardingWizard with standalone-specific context
 * (Mantine page header, StandaloneLayout AppContext, react-router navigation).
 *
 * After onboarding completes, redirects to the Configuration page.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useCallback, useEffect, useState } from 'react';
import { Stack, Title, Text } from '@mantine/core';
import { useNavigate } from 'react-router-dom';
import { useAppContext } from '../layouts/StandaloneLayout';
import { OnboardingWizard } from '../../shared/OnboardingWizard';
import type { TestModeStatus } from '../../shared/hooks/index';

// ---------------------------------------------------------------------------
// OnboardingPage
// ---------------------------------------------------------------------------

export function OnboardingPage() {
  const { tenantContext, testMode, refetchTestMode, apiFetch, onNotify } =
    useAppContext();
  const navigate = useNavigate();

  // Check whether a production config already exists (enables C16 mode selector)
  const [hasProductionConfig, setHasProductionConfig] = useState(false);

  useEffect(() => {
    if (!tenantContext) return;
    apiFetch('/api/config')
      .then(async (resp) => {
        if (!resp.ok) return;
        const data = await resp.json();
        setHasProductionConfig(!!data.version && data.version > 0);
      })
      .catch(() => {
        // Assume no production config on error
      });
  }, [tenantContext, apiFetch]);

  // Map StandaloneLayout TestModeState (camelCase) → shared TestModeStatus (snake_case)
  const testModeStatus: TestModeStatus | null = testMode
    ? {
        enabled: testMode.enabled,
        percentage: testMode.percentage,
        overrides: testMode.overrides,
        assignment_seed: 0, // Not exposed by layout; wizard only needs enabled/percentage/overrides
        activated_at: testMode.activatedAt,
        override_field_count: testMode.overrideFieldCount,
      }
    : null;

  const handleComplete = useCallback(() => {
    onNotify('Setup complete! Your AI agent is ready.', 'success');
    // Clear onboarding wizard localStorage state
    try {
      localStorage.removeItem('agentred-onboarding-wizard-state');
    } catch {
      // Ignore
    }
    navigate('/configuration');
  }, [onNotify, navigate]);

  const handleNavigate = useCallback(
    (path: string) => {
      navigate(path);
    },
    [navigate],
  );

  if (!tenantContext) return null;

  return (
    <Stack gap="lg">
      <div>
        <Title order={2}>Setup wizard</Title>
        <Text c="dimmed" size="sm">
          Complete these steps to get your AI agent ready
        </Text>
      </div>

      <OnboardingWizard
        tenantContext={tenantContext}
        apiFetch={apiFetch}
        onNotify={onNotify}
        onComplete={handleComplete}
        onNavigate={handleNavigate}
        hasProductionConfig={hasProductionConfig}
        testModeStatus={testModeStatus}
        onTestModeChange={refetchTestMode}
      />
    </Stack>
  );
}
