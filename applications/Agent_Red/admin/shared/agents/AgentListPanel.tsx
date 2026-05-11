// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * AgentListPanel — left panel showing a searchable list of agents.
 *
 * Each row displays agent name, kind badge, and enabled/disabled state.
 * Selected agent is highlighted with a left border accent.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useState, useMemo } from 'react';
import { TextInput, Badge, Text, Stack, Group, Paper, Tooltip } from '@mantine/core';
import type { AgentSummary } from '../types/agents';
import { getAgentLogo } from '../icons/agent-logos';
import { tokens } from '../theme/styles';

interface AgentListPanelProps {
  agents: AgentSummary[];
  loading: boolean;
  selectedId: string | null;
  onSelect: (agentId: string) => void;
}

const AGENT_KIND_COLORS: Record<string, string> = {
  conversational: 'blue',
  routing: 'violet',
  a2a: 'teal',
  internal: 'gray',
  external: 'orange',
};

export const AgentListPanel: React.FC<AgentListPanelProps> = ({
  agents,
  loading,
  selectedId,
  onSelect,
}) => {
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    if (!search.trim()) return agents;
    const q = search.toLowerCase();
    return agents.filter(
      (a) =>
        a.displayName.toLowerCase().includes(q) ||
        a.agentId.toLowerCase().includes(q) ||
        a.agentKind.toLowerCase().includes(q),
    );
  }, [agents, search]);

  if (loading) {
    return (
      <div style={{ padding: 16 }}>
        <Text size="sm" c="dimmed">Loading agents…</Text>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ padding: '12px 12px 8px', borderBottom: `1px solid ${tokens.border}` }}>
        <TextInput
          placeholder="Search agents…"
          size="sm"
          value={search}
          onChange={(e) => setSearch(e.currentTarget.value)}
        />
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '4px 0' }}>
        {filtered.length === 0 && (
          <Text size="sm" c="dimmed" ta="center" mt="xl">
            {search ? 'No matching agents' : 'No agents registered'}
          </Text>
        )}

        <Stack gap={0}>
          {filtered.map((agent) => {
            const isSelected = agent.agentId === selectedId;
            return (
              <Paper
                key={agent.agentId}
                onClick={() => onSelect(agent.agentId)}
                style={{
                  padding: '10px 12px',
                  cursor: 'pointer',
                  borderRadius: 0,
                  borderLeft: isSelected
                    ? `3px solid ${tokens.action}`
                    : '3px solid transparent',
                  backgroundColor: isSelected ? tokens.surface : 'transparent',
                  transition: 'background-color 0.1s',
                }}
                onMouseOver={(e) => {
                  if (!isSelected) (e.currentTarget as HTMLElement).style.backgroundColor = tokens.chrome;
                }}
                onMouseOut={(e) => {
                  if (!isSelected) (e.currentTarget as HTMLElement).style.backgroundColor = 'transparent';
                }}
              >
                <Group justify="space-between" wrap="nowrap">
                  <Group gap={10} wrap="nowrap" style={{ minWidth: 0 }}>
                    {(() => { const L = getAgentLogo(agent.agentId); return <L size={28} />; })()}
                    <Tooltip label={agent.description || agent.agentId} multiline w={250} withArrow>
                      <div style={{ minWidth: 0 }}>
                        <Text size="sm" fw={500} truncate="end">
                          {agent.displayName}
                        </Text>
                        <Text size="xs" c="dimmed" truncate="end">
                          {agent.agentId}
                        </Text>
                      </div>
                    </Tooltip>
                  </Group>
                  <Group gap={6} wrap="nowrap">
                    <Badge
                      size="xs"
                      variant="light"
                      color={AGENT_KIND_COLORS[agent.agentKind] || 'gray'}
                    >
                      {agent.agentKind}
                    </Badge>
                    {!agent.enabled && (
                      <Badge size="xs" variant="light" color="red">
                        disabled
                      </Badge>
                    )}
                  </Group>
                </Group>
              </Paper>
            );
          })}
        </Stack>
      </div>
    </div>
  );
};
