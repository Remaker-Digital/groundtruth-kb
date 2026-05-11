// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

/**
 * Integrations page — Standalone admin.
 *
 * Wraps the shared IntegrationsManager component in the standalone admin
 * page layout. Provides API context (apiFetch, tenantContext, onNotify).
 *
 * C10 capability dependency for Launch UI Test.
 */

import React from 'react';
import { Title, Text, Loader, useComputedColorScheme } from '@mantine/core';
import { useAppContext } from '../layouts/StandaloneLayout';
import { IntegrationsManager } from '../../shared/IntegrationsManager';

export const IntegrationsPage: React.FC = () => {
  const { tenantContext, apiFetch, onNotify, loading } = useAppContext();
  const computedColorScheme = useComputedColorScheme('dark');
  const isDark = computedColorScheme === 'dark';

  if (loading || !tenantContext) {
    return (
      <div style={{ padding: 40, textAlign: 'center' }}>
        <Loader size="sm" />
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 900, margin: '0 auto' }}>
      <Title order={2} mb="xs">Integrations</Title>
      <Text size="sm" c="dimmed" mb="lg">
        Connect third-party services to extend your AI agent&apos;s capabilities.
      </Text>

      <IntegrationsManager
        tenantContext={tenantContext}
        apiFetch={apiFetch}
        onNotify={onNotify}
        isDark={isDark}
        basePath="/admin/standalone"
      />
    </div>
  );
};
