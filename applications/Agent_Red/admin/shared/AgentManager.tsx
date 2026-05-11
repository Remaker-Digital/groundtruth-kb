// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * AgentManager — two-panel orchestrator for tenant agent lifecycle.
 *
 * Left panel: searchable agent list (AgentListPanel)
 * Right panel: overlay toggle + effective config + bindings (AgentDetailPanel)
 *
 * URL state management is handled by the shell page wrapper (Agents.tsx)
 * via initialAgentId / onAgentSelected props — keeps this component
 * framework-agnostic (no react-router-dom dependency in shared/).
 *
 * Responsive: collapses to single pane below 768px.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Button, Text } from '@mantine/core';
import type { BaseComponentProps } from './types';
import { useAgents } from './hooks/useAgents';
import { AgentListPanel } from './agents/AgentListPanel';
import { AgentDetailPanel } from './agents/AgentDetailPanel';
import { tokens } from './theme/styles';

const BREAKPOINT = 768;

interface AgentManagerProps extends BaseComponentProps {
  /** Initial agent ID (from URL query param). */
  initialAgentId?: string | null;
  /** Called when the selected agent changes (for URL sync). */
  onAgentSelected?: (agentId: string | null) => void;
}

export const AgentManager: React.FC<AgentManagerProps> = ({
  tenantContext,
  apiFetch,
  onNotify,
  initialAgentId = null,
  onAgentSelected,
}) => {
  const agentsList = useAgents(apiFetch);
  const [selectedId, setSelectedId] = useState<string | null>(initialAgentId);

  // Sync selectedId when initialAgentId prop changes (back/forward, manual URL edit)
  useEffect(() => {
    setSelectedId(initialAgentId ?? null);
  }, [initialAgentId]);

  // Track viewport for responsive collapse
  const [isNarrow, setIsNarrow] = useState(
    typeof window !== 'undefined' ? window.innerWidth < BREAKPOINT : false,
  );

  useEffect(() => {
    const handler = () => setIsNarrow(window.innerWidth < BREAKPOINT);
    window.addEventListener('resize', handler);
    return () => window.removeEventListener('resize', handler);
  }, []);

  const handleSelect = useCallback(
    (agentId: string) => {
      setSelectedId(agentId);
      onAgentSelected?.(agentId);
    },
    [onAgentSelected],
  );

  const handleBack = useCallback(() => {
    setSelectedId(null);
    onAgentSelected?.(null);
  }, [onAgentSelected]);

  // Find the full agent summary for the selected agent
  const selectedAgent = agentsList.data?.find((a) => a.agentId === selectedId) ?? null;

  // Error state
  if (agentsList.error) {
    return (
      <Text size="sm" c="red">
        Failed to load agents: {agentsList.error}
      </Text>
    );
  }

  // Responsive: narrow viewport
  if (isNarrow) {
    if (selectedId && selectedAgent) {
      return (
        <div>
          <Button
            variant="subtle"
            size="xs"
            mb="sm"
            onClick={handleBack}
            leftSection="←"
          >
            Back to agents
          </Button>
          <AgentDetailPanel
            agent={selectedAgent}
            apiFetch={apiFetch}
            onNotify={onNotify}
            onAgentChanged={agentsList.refetch}
          />
        </div>
      );
    }
    return (
      <AgentListPanel
        agents={agentsList.data ?? []}
        loading={agentsList.loading}
        selectedId={selectedId}
        onSelect={handleSelect}
      />
    );
  }

  // Desktop: two-panel layout
  return (
    <div
      style={{
        display: 'flex',
        height: 'calc(100vh - 160px)',
        border: `1px solid ${tokens.border}`,
        borderRadius: 8,
        overflow: 'hidden',
      }}
    >
      {/* Left panel: agent list */}
      <div
        style={{
          width: 300,
          minWidth: 240,
          borderRight: `1px solid ${tokens.border}`,
          overflow: 'hidden',
        }}
      >
        <AgentListPanel
          agents={agentsList.data ?? []}
          loading={agentsList.loading}
          selectedId={selectedId}
          onSelect={handleSelect}
        />
      </div>

      {/* Right panel: detail */}
      <div style={{ flex: 1, overflow: 'hidden' }}>
        {selectedAgent ? (
          <AgentDetailPanel
            agent={selectedAgent}
            apiFetch={apiFetch}
            onNotify={onNotify}
            onAgentChanged={agentsList.refetch}
          />
        ) : (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%',
            }}
          >
            <Text size="sm" c="dimmed">
              Select an agent to view details
            </Text>
          </div>
        )}
      </div>
    </div>
  );
};
