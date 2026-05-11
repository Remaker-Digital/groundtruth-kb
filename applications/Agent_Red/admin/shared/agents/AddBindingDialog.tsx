// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * AddBindingDialog — modal for creating a new skill binding.
 *
 * Shows a searchable select of available skills (filtered to exclude
 * already-bound skills) with mode and approval policy options.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useState } from 'react';
import { Modal, Select, Button, Group, Stack, Text } from '@mantine/core';
import type { EffectiveSkill, AgentBindingInput } from '../types/agents';

interface AddBindingDialogProps {
  opened: boolean;
  availableSkills: EffectiveSkill[];
  boundSkillIds: string[];
  loading: boolean;
  onConfirm: (skillId: string, input: AgentBindingInput) => void;
  onClose: () => void;
}

const MODE_OPTIONS = [
  { value: 'read', label: 'Read' },
  { value: 'mutate', label: 'Mutate' },
];

const POLICY_OPTIONS = [
  { value: 'auto', label: 'Auto-approve' },
  { value: 'require_confirmation', label: 'Require confirmation' },
];

export const AddBindingDialog: React.FC<AddBindingDialogProps> = ({
  opened,
  availableSkills,
  boundSkillIds,
  loading,
  onConfirm,
  onClose,
}) => {
  const [selectedSkill, setSelectedSkill] = useState<string | null>(null);
  const [mode, setMode] = useState('read');
  const [policy, setPolicy] = useState('auto');

  // Filter to skills not already bound
  const unboundSkills = availableSkills.filter(
    (s) => !boundSkillIds.includes(s.skillId),
  );

  const skillOptions = unboundSkills.map((s) => ({
    value: s.skillId,
    label: `${s.displayName} (${s.skillId})`,
  }));

  const handleConfirm = () => {
    if (!selectedSkill) return;
    onConfirm(selectedSkill, {
      mode,
      approvalPolicy: policy,
      enabled: true,
    });
    // Reset for next use
    setSelectedSkill(null);
    setMode('read');
    setPolicy('auto');
  };

  const handleClose = () => {
    setSelectedSkill(null);
    setMode('read');
    setPolicy('auto');
    onClose();
  };

  return (
    <Modal
      opened={opened}
      onClose={handleClose}
      title="Add skill binding"
      size="md"
    >
      <Stack gap="md">
        <Text size="sm" c="dimmed">
          Select a skill to bind to this agent. The binding authorizes the agent
          to invoke this skill for the tenant.
        </Text>

        <Select
          label="Skill"
          placeholder="Select a skill…"
          data={skillOptions}
          value={selectedSkill}
          onChange={setSelectedSkill}
          searchable
          nothingFoundMessage={
            unboundSkills.length === 0
              ? 'All available skills are already bound'
              : 'No matching skills'
          }
        />

        <Group grow>
          <Select
            label="Mode"
            data={MODE_OPTIONS}
            value={mode}
            onChange={(v) => setMode(v || 'read')}
          />
          <Select
            label="Approval policy"
            data={POLICY_OPTIONS}
            value={policy}
            onChange={(v) => setPolicy(v || 'auto')}
          />
        </Group>

        <Group justify="flex-end" mt="md">
          <Button variant="subtle" onClick={handleClose}>
            Cancel
          </Button>
          <Button
            onClick={handleConfirm}
            disabled={!selectedSkill}
            loading={loading}
          >
            Create binding
          </Button>
        </Group>
      </Stack>
    </Modal>
  );
};
