// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

/**
 * Agents page — Standalone admin (Phase 4a).
 *
 * Thin wrapper around the shared AgentManager component. Handles URL
 * state sync (?agent=<id>) via useSearchParams — the shared component
 * stays framework-agnostic.
 */

import React, { useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Title, Text } from '@mantine/core';
import { useAppContext } from '../layouts/StandaloneLayout';
import { AgentManager } from '../../shared/AgentManager';
import { LoadingState } from '../../shared/LoadingState';


export const AgentsPage: React.FC = () => {
  const { tenantContext, apiFetch, onNotify, loading } = useAppContext();
  const [searchParams, setSearchParams] = useSearchParams();

  const initialAgentId = searchParams.get('agent');

  const handleAgentSelected = useCallback(
    (agentId: string | null) => {
      setSearchParams((prev) => {
        const next = new URLSearchParams(prev);
        if (agentId) {
          next.set('agent', agentId);
        } else {
          next.delete('agent');
        }
        return next;
      }, { replace: true });
    },
    [setSearchParams],
  );

  if (loading || !tenantContext) {
    return <LoadingState text="Loading agents" />;
  }

  return (
    <div>
      <Title order={2} mb="xs">Agents configuration</Title>
      <Text size="sm" c="dimmed" mb="lg">
        Configure agents, manage skill bindings, and connect third-party integrations.
      </Text>

      <AgentManager
        tenantContext={tenantContext}
        apiFetch={apiFetch}
        onNotify={onNotify}
        initialAgentId={initialAgentId}
        onAgentSelected={handleAgentSelected}
      />
    </div>
  );
};
