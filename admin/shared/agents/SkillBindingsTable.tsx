/**
 * SkillBindingsTable — table of current skill bindings with add/delete.
 *
 * Shows each binding's skill ID, display name, mode, approval policy,
 * and enabled state. Delete action uses a confirm dialog.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useState } from 'react';
import {
  Table,
  Badge,
  Button,
  Group,
  Text,
  ActionIcon,
  Modal,
  Stack,
} from '@mantine/core';
import type { AgentBinding, EffectiveSkill, AgentBindingInput } from '../types/agents';
import { AddBindingDialog } from './AddBindingDialog';

interface SkillBindingsTableProps {
  bindings: AgentBinding[];
  availableSkills: EffectiveSkill[];
  loading: boolean;
  onAdd: (skillId: string, input: AgentBindingInput) => Promise<void>;
  onDelete: (skillId: string) => Promise<void>;
}

// Simple trash icon SVG
const TrashIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="3 6 5 6 21 6" />
    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
  </svg>
);

export const SkillBindingsTable: React.FC<SkillBindingsTableProps> = ({
  bindings,
  availableSkills,
  loading,
  onAdd,
  onDelete,
}) => {
  const [addOpen, setAddOpen] = useState(false);
  const [addLoading, setAddLoading] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);
  const [deleteLoading, setDeleteLoading] = useState(false);

  const boundSkillIds = bindings.map((b) => b.skillId);

  const handleAdd = async (skillId: string, input: AgentBindingInput) => {
    setAddLoading(true);
    try {
      await onAdd(skillId, input);
      setAddOpen(false);
    } finally {
      setAddLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setDeleteLoading(true);
    try {
      await onDelete(deleteTarget);
      setDeleteTarget(null);
    } finally {
      setDeleteLoading(false);
    }
  };

  return (
    <>
      <Group justify="space-between" mb="sm">
        <Text size="sm" fw={500}>Skill bindings</Text>
        <Button size="xs" variant="light" onClick={() => setAddOpen(true)}>
          Add binding
        </Button>
      </Group>

      {bindings.length === 0 ? (
        <Text size="sm" c="dimmed" ta="center" py="xl">
          No skill bindings. This agent cannot invoke any skills for this tenant.
        </Text>
      ) : (
        <Table striped highlightOnHover withTableBorder>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Skill</Table.Th>
              <Table.Th>Mode</Table.Th>
              <Table.Th>Policy</Table.Th>
              <Table.Th>Status</Table.Th>
              <Table.Th style={{ width: 48 }} />
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {bindings.map((b) => (
              <Table.Tr key={b.skillId}>
                <Table.Td>
                  <Text size="sm">{b.skillId}</Text>
                </Table.Td>
                <Table.Td>
                  <Badge size="xs" variant="light" color={b.mode === 'mutate' ? 'orange' : 'blue'}>
                    {b.mode}
                  </Badge>
                </Table.Td>
                <Table.Td>
                  <Text size="xs" c="dimmed">{b.approvalPolicy}</Text>
                </Table.Td>
                <Table.Td>
                  <Badge size="xs" variant="light" color={b.enabled ? 'green' : 'red'}>
                    {b.enabled ? 'active' : 'disabled'}
                  </Badge>
                </Table.Td>
                <Table.Td>
                  <ActionIcon
                    size="sm"
                    variant="subtle"
                    color="red"
                    onClick={() => setDeleteTarget(b.skillId)}
                    title="Delete binding"
                  >
                    <TrashIcon />
                  </ActionIcon>
                </Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      )}

      <AddBindingDialog
        opened={addOpen}
        availableSkills={availableSkills}
        boundSkillIds={boundSkillIds}
        loading={addLoading}
        onConfirm={handleAdd}
        onClose={() => setAddOpen(false)}
      />

      {/* Delete confirmation */}
      <Modal
        opened={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        title="Delete skill binding"
        size="sm"
      >
        <Stack gap="md">
          <Text size="sm">
            Remove binding for <strong>{deleteTarget}</strong>? This will revoke
            the agent's ability to invoke this skill for the tenant.
          </Text>
          <Group justify="flex-end">
            <Button variant="subtle" onClick={() => setDeleteTarget(null)}>
              Cancel
            </Button>
            <Button color="red" onClick={handleDelete} loading={deleteLoading}>
              Delete
            </Button>
          </Group>
        </Stack>
      </Modal>
    </>
  );
};
