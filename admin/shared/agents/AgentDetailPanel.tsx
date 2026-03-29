/**
 * AgentDetailPanel — right panel showing overlay toggle, effective config
 * summary, and skill bindings for the selected agent.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React from 'react';
import {
  Title,
  Text,
  Badge,
  Switch,
  Paper,
  Stack,
  Group,
  Divider,
  Table,
  Collapse,
} from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import type { AgentSummary, AgentBindingInput } from '../types/agents';
import type { ApiFetch } from '../hooks/useApi';
import {
  useAgentOverlay,
  useAgentBindings,
  useBindableSkills,
  useEffectiveConfig,
  useToggleOverlay,
  useCreateBinding,
  useDeleteBinding,
} from '../hooks/useAgents';
import { SkillBindingsTable } from './SkillBindingsTable';
import { tokens } from '../theme/styles';

interface AgentDetailPanelProps {
  agent: AgentSummary;
  apiFetch: ApiFetch;
  onNotify: (message: string, type: 'success' | 'error' | 'warning' | 'info') => void;
  onAgentChanged: () => void;
}

export const AgentDetailPanel: React.FC<AgentDetailPanelProps> = ({
  agent,
  apiFetch,
  onNotify,
  onAgentChanged,
}) => {
  const overlayResult = useAgentOverlay(apiFetch, agent.agentId);
  const bindingsResult = useAgentBindings(apiFetch, agent.agentId);
  const bindableSkillsResult = useBindableSkills(apiFetch, agent.agentId);
  const effectiveResult = useEffectiveConfig(apiFetch, agent.agentId);

  const { toggle: toggleOverlay, loading: toggleLoading } = useToggleOverlay(apiFetch);
  const { create: createBinding } = useCreateBinding(apiFetch);
  const { remove: removeBinding } = useDeleteBinding(apiFetch);

  const [configOpen, { toggle: toggleConfig }] = useDisclosure(false);

  const overlay = overlayResult.data;
  const hasOverlay = agent.hasOverlay;
  const isEnabled = overlay?.enabled ?? agent.enabled;

  const handleToggle = async () => {
    const newEnabled = !isEnabled;
    const result = await toggleOverlay(agent.agentId, newEnabled);
    if (result) {
      onNotify(
        `${agent.displayName} ${newEnabled ? 'enabled' : 'disabled'}`,
        'success',
      );
      overlayResult.refetch();
      onAgentChanged();
    } else {
      onNotify('Failed to toggle agent', 'error');
    }
  };

  const handleAddBinding = async (skillId: string, input: AgentBindingInput) => {
    const result = await createBinding(agent.agentId, skillId, input);
    if (result) {
      onNotify(`Binding created for ${skillId}`, 'success');
      bindingsResult.refetch();
      bindableSkillsResult.refetch();
      effectiveResult.refetch();
    } else {
      onNotify('Failed to create binding', 'error');
    }
  };

  const handleDeleteBinding = async (skillId: string) => {
    const ok = await removeBinding(agent.agentId, skillId);
    if (ok) {
      onNotify(`Binding removed for ${skillId}`, 'success');
      bindingsResult.refetch();
      bindableSkillsResult.refetch();
      effectiveResult.refetch();
    } else {
      onNotify('Failed to delete binding', 'error');
    }
  };

  return (
    <div style={{ padding: '16px 20px', overflowY: 'auto', height: '100%' }}>
      <Stack gap="lg">
        {/* Header */}
        <div>
          <Group justify="space-between" align="flex-start">
            <div>
              <Title order={3}>{agent.displayName}</Title>
              <Group gap={8} mt={4}>
                <Text size="xs" c="dimmed" ff="monospace">{agent.agentId}</Text>
                <Badge size="xs" variant="light" color="gray">{agent.agentKind}</Badge>
              </Group>
            </div>
            <Switch
              label={isEnabled ? 'Enabled' : 'Disabled'}
              checked={isEnabled}
              onChange={handleToggle}
              disabled={toggleLoading}
              size="md"
              color="green"
            />
          </Group>
          {!hasOverlay && (
            <Text size="xs" c="dimmed" mt={8}>
              Base configuration — toggle to create a tenant overlay.
            </Text>
          )}
        </div>

        <Divider />

        {/* Effective Config Summary */}
        <Paper
          p="sm"
          withBorder
          style={{ cursor: 'pointer' }}
          onClick={toggleConfig}
        >
          <Group justify="space-between">
            <Text size="sm" fw={500}>
              Effective configuration
            </Text>
            <Badge size="sm" variant="light">
              {effectiveResult.data?.skills.length ?? 0} skills
            </Badge>
          </Group>
          <Collapse in={configOpen}>
            <div style={{ marginTop: 12 }}>
              {effectiveResult.loading && (
                <Text size="xs" c="dimmed">Loading…</Text>
              )}
              {effectiveResult.data && effectiveResult.data.skills.length > 0 ? (
                <Table withRowBorders={false}>
                  <Table.Thead>
                    <Table.Tr>
                      <Table.Th style={{ fontSize: 11 }}>Skill</Table.Th>
                      <Table.Th style={{ fontSize: 11 }}>Mode</Table.Th>
                      <Table.Th style={{ fontSize: 11 }}>Status</Table.Th>
                      <Table.Th style={{ fontSize: 11 }}>Credential</Table.Th>
                    </Table.Tr>
                  </Table.Thead>
                  <Table.Tbody>
                    {effectiveResult.data.skills.map((s) => (
                      <Table.Tr key={s.skillId}>
                        <Table.Td>
                          <Text size="xs">{s.displayName}</Text>
                          <Text size="xs" c="dimmed" ff="monospace">{s.skillId}</Text>
                        </Table.Td>
                        <Table.Td>
                          <Badge size="xs" variant="light">{s.mode}</Badge>
                        </Table.Td>
                        <Table.Td>
                          <Badge
                            size="xs"
                            variant="light"
                            color={s.enabled ? 'green' : 'red'}
                          >
                            {s.enabled ? 'active' : 'disabled'}
                          </Badge>
                        </Table.Td>
                        <Table.Td>
                          <Text size="xs" c="dimmed">
                            {s.credentialRef ? 'configured' : 'none'}
                          </Text>
                        </Table.Td>
                      </Table.Tr>
                    ))}
                  </Table.Tbody>
                </Table>
              ) : (
                <Text size="xs" c="dimmed">No resolved skills</Text>
              )}
            </div>
          </Collapse>
        </Paper>

        {/* Skill Bindings */}
        <SkillBindingsTable
          bindings={bindingsResult.data ?? []}
          availableSkills={bindableSkillsResult.data ?? []}
          loading={bindingsResult.loading}
          onAdd={handleAddBinding}
          onDelete={handleDeleteBinding}
        />
      </Stack>
    </div>
  );
};
