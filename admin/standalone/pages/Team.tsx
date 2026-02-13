// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

/**
 * Team page — Standalone admin.
 *
 * Thin wrapper around the shared TeamManager component, which handles all
 * API calls, inline editing, escalation category assignment, and role
 * management. This page provides the standalone layout context (apiFetch,
 * tenantContext, onNotify) to the shared component.
 *
 * Previously this file contained a 548-line standalone Mantine implementation
 * that was replaced in the role model redesign (session 8) to ensure a single
 * source of truth for team management UI.
 */

import React from 'react';
import { Title, Text, Loader, Stack } from '@mantine/core';
import { useAppContext } from '../layouts/StandaloneLayout';
import { TeamManager } from '../../shared/TeamManager';

const BRAND_RED = '#ff3621';

export const TeamPage: React.FC = () => {
  const { tenantContext, apiFetch, onNotify, loading } = useAppContext();

  if (loading || !tenantContext) {
    return (
      <Stack gap="lg" align="center" py="xl">
        <Loader size="md" color={BRAND_RED} />
        <Text c="dimmed" size="sm">Loading team...</Text>
      </Stack>
    );
  }

  return (
    <div style={{ maxWidth: 900, margin: '0 auto' }}>
      <Title order={2} mb="xs">Team members</Title>
      <Text size="sm" c="dimmed" mb="lg">
        Manage team members, assign roles, and configure escalation categories.
      </Text>

      <TeamManager
        tenantContext={tenantContext}
        apiFetch={apiFetch}
        onNotify={onNotify}
      />
    </div>
  );
};
