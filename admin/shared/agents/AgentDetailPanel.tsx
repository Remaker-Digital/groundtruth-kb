/**
 * AgentDetailPanel — right panel showing agent overview, unified skills
 * table with inline toggle/select controls, and provider logo.
 *
 * Changes from Phase 4a initial:
 *   - Unified skills table replaces modal + two-section layout (Change 3)
 *   - Tooltips on agent/skill names, mode, status, credential (Change 4)
 *   - Agent description from registry replaces overlay system message (Change 4)
 *   - Provider logo 80x80 in header (Change 6)
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useCallback, useState } from 'react';
import {
  Title,
  Text,
  Badge,
  Switch,
  Stack,
  Group,
  Divider,
  Table,
  Tooltip,
  Select,
} from '@mantine/core';
import type { AgentSummary, AgentBindingInput } from '../types/agents';
import type { ApiFetch } from '../hooks/useApi';
import {
  useAgentOverlay,
  useAgentBindings,
  useBindableSkills,
  useToggleOverlay,
  useCreateBinding,
  useDeleteBinding,
} from '../hooks/useAgents';
import { getAgentLogo } from '../icons/agent-logos';
import { tokens } from '../theme/styles';

interface AgentDetailPanelProps {
  agent: AgentSummary;
  apiFetch: ApiFetch;
  onNotify: (message: string, type: 'success' | 'error' | 'warning' | 'info') => void;
  onAgentChanged: () => void;
}

// Tooltip text for mode values
const MODE_TOOLTIPS: Record<string, string> = {
  read: 'Read-only: can query data but not modify it',
  mutate: 'Mutate: can make changes (create, update, delete)',
  internal: 'Internal: runs in-process within the pipeline',
};

// Tooltip text for credential states
const CREDENTIAL_TOOLTIPS: Record<string, string> = {
  none: 'No external credential required — this skill runs internally',
  configured: 'Credential is stored securely in Key Vault',
};

const MODE_OPTIONS = [
  { value: 'read', label: 'Read' },
  { value: 'mutate', label: 'Mutate' },
];

const POLICY_OPTIONS = [
  { value: 'auto', label: 'Auto-approve' },
  { value: 'require_confirmation', label: 'Require confirmation' },
];

export const AgentDetailPanel: React.FC<AgentDetailPanelProps> = ({
  agent,
  apiFetch,
  onNotify,
  onAgentChanged,
}) => {
  const overlayResult = useAgentOverlay(apiFetch, agent.agentId);
  const bindingsResult = useAgentBindings(apiFetch, agent.agentId);
  const bindableSkillsResult = useBindableSkills(apiFetch, agent.agentId);

  const { toggle: toggleOverlay, loading: toggleLoading } = useToggleOverlay(apiFetch);
  const { create: createBinding } = useCreateBinding(apiFetch);
  const { remove: removeBinding } = useDeleteBinding(apiFetch);

  // Track in-flight skill toggles to prevent double-clicks
  const [busySkills, setBusySkills] = useState<Set<string>>(new Set());

  const overlay = overlayResult.data;
  const isEnabled = overlay?.enabled ?? agent.enabled;
  const bindings = bindingsResult.data ?? [];
  const bindableSkills = bindableSkillsResult.data ?? [];

  // Build a map of current bindings by skill_id
  const bindingMap = new Map(bindings.map((b) => [b.skillId, b]));

  const Logo = getAgentLogo(agent.agentId);

  const handleToggleAgent = async () => {
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

  const handleToggleSkill = useCallback(async (skillId: string, currentlyBound: boolean) => {
    setBusySkills((prev) => new Set(prev).add(skillId));
    try {
      if (currentlyBound) {
        const ok = await removeBinding(agent.agentId, skillId);
        if (ok) {
          onNotify(`Skill disabled: ${skillId}`, 'success');
          bindingsResult.refetch();
        } else {
          onNotify('Failed to disable skill', 'error');
        }
      } else {
        const result = await createBinding(agent.agentId, skillId, {
          mode: 'read',
          approvalPolicy: 'auto',
          enabled: true,
        });
        if (result) {
          onNotify(`Skill enabled: ${skillId}`, 'success');
          bindingsResult.refetch();
        } else {
          onNotify('Failed to enable skill', 'error');
        }
      }
    } finally {
      setBusySkills((prev) => {
        const next = new Set(prev);
        next.delete(skillId);
        return next;
      });
    }
  }, [agent.agentId, createBinding, removeBinding, bindingsResult, onNotify]);

  const handleModeChange = useCallback(async (skillId: string, mode: string) => {
    const binding = bindingMap.get(skillId);
    if (!binding) return;
    const result = await createBinding(agent.agentId, skillId, {
      mode,
      approvalPolicy: binding.approvalPolicy,
      enabled: true,
    });
    if (result) {
      bindingsResult.refetch();
    }
  }, [agent.agentId, createBinding, bindingMap, bindingsResult]);

  const handlePolicyChange = useCallback(async (skillId: string, policy: string) => {
    const binding = bindingMap.get(skillId);
    if (!binding) return;
    const result = await createBinding(agent.agentId, skillId, {
      mode: binding.mode,
      approvalPolicy: policy,
      enabled: true,
    });
    if (result) {
      bindingsResult.refetch();
    }
  }, [agent.agentId, createBinding, bindingMap, bindingsResult]);

  return (
    <div style={{ padding: '16px 20px', overflowY: 'auto', height: '100%' }}>
      <Stack gap="lg">
        {/* Header with logo */}
        <Group justify="space-between" align="flex-start" wrap="nowrap">
          <Group gap="md" wrap="nowrap">
            <Logo size={80} />
            <div>
              <Tooltip label={agent.description || agent.agentId} multiline w={300} withArrow>
                <Title order={3} style={{ cursor: 'help' }}>{agent.displayName}</Title>
              </Tooltip>
              <Group gap={8} mt={4}>
                <Text size="xs" c="dimmed" ff="monospace">{agent.agentId}</Text>
                <Badge size="xs" variant="light" color="gray">{agent.agentKind}</Badge>
                {agent.category && (
                  <Badge size="xs" variant="light" color="blue">{agent.category}</Badge>
                )}
              </Group>
              <Text size="sm" c="dimmed" mt={8} maw={500}>
                {agent.description || 'No description available.'}
              </Text>
            </div>
          </Group>

          <Switch
            label={isEnabled ? 'Enabled' : 'Disabled'}
            checked={isEnabled}
            onChange={handleToggleAgent}
            disabled={toggleLoading}
            size="md"
            color="green"
          />
        </Group>

        <Divider />

        {/* Unified Skills Table */}
        <div>
          <Group justify="space-between" mb="sm">
            <Text size="sm" fw={500}>Skills</Text>
            <Badge size="sm" variant="light">
              {bindableSkills.length} available
            </Badge>
          </Group>

          {bindableSkills.length === 0 ? (
            <Text size="sm" c="dimmed" ta="center" py="xl">
              No skills registered for this agent.
            </Text>
          ) : (
            <Table striped highlightOnHover withTableBorder>
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Skill</Table.Th>
                  <Table.Th style={{ width: 120 }}>
                    <Tooltip label="Controls whether this skill is authorized for the tenant" withArrow>
                      <Text size="xs" fw={600} style={{ cursor: 'help' }}>Enabled</Text>
                    </Tooltip>
                  </Table.Th>
                  <Table.Th style={{ width: 120 }}>
                    <Tooltip label="Read: query-only access. Mutate: can make changes." withArrow>
                      <Text size="xs" fw={600} style={{ cursor: 'help' }}>Mode</Text>
                    </Tooltip>
                  </Table.Th>
                  <Table.Th style={{ width: 170 }}>
                    <Tooltip label="Auto-approve: no human review. Require confirmation: human must approve." withArrow>
                      <Text size="xs" fw={600} style={{ cursor: 'help' }}>Approval</Text>
                    </Tooltip>
                  </Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {bindableSkills.map((skill) => {
                  const binding = bindingMap.get(skill.skillId);
                  const isBound = !!binding;
                  const isBusy = busySkills.has(skill.skillId);

                  return (
                    <Table.Tr key={skill.skillId}>
                      <Table.Td>
                        <Tooltip
                          label={skill.description || skill.skillId}
                          multiline
                          w={250}
                          withArrow
                        >
                          <div style={{ cursor: 'help' }}>
                            <Text size="sm">{skill.displayName}</Text>
                            <Text size="xs" c="dimmed" ff="monospace">{skill.skillId}</Text>
                          </div>
                        </Tooltip>
                      </Table.Td>
                      <Table.Td>
                        <Switch
                          checked={isBound}
                          onChange={() => handleToggleSkill(skill.skillId, isBound)}
                          disabled={isBusy}
                          size="sm"
                          color="green"
                        />
                      </Table.Td>
                      <Table.Td>
                        <Select
                          data={MODE_OPTIONS}
                          value={binding?.mode ?? 'read'}
                          onChange={(v) => v && handleModeChange(skill.skillId, v)}
                          size="xs"
                          disabled={!isBound}
                          styles={{
                            input: {
                              opacity: isBound ? 1 : 0.4,
                            },
                          }}
                        />
                      </Table.Td>
                      <Table.Td>
                        <Select
                          data={POLICY_OPTIONS}
                          value={binding?.approvalPolicy ?? 'auto'}
                          onChange={(v) => v && handlePolicyChange(skill.skillId, v)}
                          size="xs"
                          disabled={!isBound}
                          styles={{
                            input: {
                              opacity: isBound ? 1 : 0.4,
                            },
                          }}
                        />
                      </Table.Td>
                    </Table.Tr>
                  );
                })}
              </Table.Tbody>
            </Table>
          )}
        </div>
      </Stack>
    </div>
  );
};
