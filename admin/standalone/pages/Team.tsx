// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

/**
 * Team page — Standalone admin.
 *
 * Adapted from the prototype TeamPage (Mantine v7 dark mode design).
 * Replaces mock data with API hooks (useTeamMembers, useInviteTeamMember).
 * Hash-based avatar colors, null-safe field access, API-driven invite flow.
 *
 * Role changes are visual-only in this version (no backend endpoint for role update).
 */

import React, { useState, useCallback } from 'react';
import {
  Paper,
  Table,
  Badge,
  Button,
  Modal,
  TextInput,
  Select,
  Textarea,
  Group,
  Stack,
  Title,
  Text,
  Avatar,
  ActionIcon,
  Tooltip,
  Accordion,
  Loader,
  Alert,
} from '@mantine/core';
import { useAppContext } from '../layouts/StandaloneLayout';
import { useTeamMembers, useInviteTeamMember } from '../../shared/hooks/index';
import type { TeamRole } from '../../shared/types/index';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const BRAND_RED = '#ff3621';

const AVATAR_PALETTE = ['#ff3621', '#2563EB', '#059669', '#D97706', '#7C3AED', '#DB2777'];

const roleColorMap: Record<string, string> = {
  owner: 'red',
  admin: 'blue',
  agent: 'green',
  viewer: 'gray',
};

const statusColorMap: Record<string, { color: string; variant: string }> = {
  active: { color: 'green', variant: 'filled' },
  invited: { color: 'yellow', variant: 'outline' },
  disabled: { color: 'gray', variant: 'filled' },
};

const permissionsData = [
  {
    role: 'Owner',
    color: 'brand',
    permissions: 'Full access, billing management, delete account, manage all team members',
  },
  {
    role: 'Admin',
    color: 'blue',
    permissions: 'Configuration, team management, all conversations, knowledge base editing',
  },
  {
    role: 'Agent',
    color: 'green',
    permissions: 'Assigned conversations, knowledge base (read only), view own analytics',
  },
  {
    role: 'Viewer',
    color: 'gray',
    permissions: 'Read-only access to dashboard and analytics',
  },
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function avatarColor(name: string): string {
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  return AVATAR_PALETTE[Math.abs(hash) % AVATAR_PALETTE.length];
}

function getInitials(name: string): string {
  if (!name) return '?';
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

function formatLastActive(dateStr: string | null | undefined): string {
  if (!dateStr) return 'Never';
  try {
    const now = new Date();
    const then = new Date(dateStr);
    const diffMs = now.getTime() - then.getTime();
    if (diffMs < 0) return 'Just now';
    const diffMin = Math.floor(diffMs / 60000);
    if (diffMin < 2) return 'Just now';
    if (diffMin < 60) return `${diffMin} min ago`;
    const diffHours = Math.floor(diffMin / 60);
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    const diffDays = Math.floor(diffHours / 24);
    if (diffDays < 30) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  } catch {
    return 'Never';
  }
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const TeamPage: React.FC = () => {
  const { apiFetch, onNotify } = useAppContext();
  const teamResult = useTeamMembers(apiFetch);
  const members = teamResult.data?.members ?? [];
  const { invite, loading: inviting, error: inviteError } = useInviteTeamMember(apiFetch);

  // Local role overrides (visual-only — no API endpoint for role update)
  const [roleOverrides, setRoleOverrides] = useState<Record<string, TeamRole>>({});

  // Invite modal state
  const [inviteModalOpen, setInviteModalOpen] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteName, setInviteName] = useState('');
  const [inviteRole, setInviteRole] = useState<string | null>('agent');
  const [inviteMessage, setInviteMessage] = useState('');

  // Computed counts — API returns isActive boolean, not status string
  const activeCount = members.filter((m) => m.isActive).length;
  const inactiveCount = members.filter((m) => !m.isActive).length;

  // ---- Handlers -----------------------------------------------------------

  const handleRoleChange = useCallback((memberId: string, newRole: string | null) => {
    if (!newRole) return;
    setRoleOverrides((prev) => ({ ...prev, [memberId]: newRole as TeamRole }));
  }, []);

  const handleRemove = useCallback(
    async (memberId: string, memberEmail: string) => {
      try {
        const resp = await apiFetch(`/api/admin/team/${memberId}`, { method: 'DELETE' });
        if (!resp.ok) {
          const errText = await resp.text().catch(() => '');
          throw new Error(`${resp.status}: ${errText}`);
        }
        onNotify(`Removed ${memberEmail} from the team.`, 'success');
        teamResult.refetch();
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Removal failed';
        onNotify(`Failed to remove member: ${msg}`, 'error');
      }
    },
    [apiFetch, onNotify, teamResult],
  );

  const handleInvite = useCallback(async () => {
    if (!inviteEmail.trim() || !inviteRole) return;

    const result = await invite(
      inviteEmail.trim(),
      inviteRole,
      inviteName.trim() || undefined,
    );

    if (result) {
      onNotify(`Invited ${inviteEmail.trim()} as ${inviteRole}.`, 'success');
      setInviteEmail('');
      setInviteName('');
      setInviteRole('agent');
      setInviteMessage('');
      setInviteModalOpen(false);
      teamResult.refetch();
    } else {
      onNotify(inviteError || 'Failed to invite team member.', 'error');
    }
  }, [inviteEmail, inviteName, inviteRole, invite, inviteError, onNotify, teamResult]);

  const closeInviteModal = useCallback(() => {
    setInviteModalOpen(false);
    setInviteEmail('');
    setInviteName('');
    setInviteRole('agent');
    setInviteMessage('');
  }, []);

  // ---- Loading state ------------------------------------------------------

  if (teamResult.loading && !teamResult.data) {
    return (
      <Stack gap="lg" align="center" py="xl">
        <Loader size="md" color={BRAND_RED} />
        <Text c="dimmed" size="sm">Loading team members...</Text>
      </Stack>
    );
  }

  // ---- Error state --------------------------------------------------------

  if (teamResult.error && !teamResult.data) {
    return (
      <Stack gap="lg">
        <Title order={2}>Team</Title>
        <Alert color="red" title="Failed to load team">
          {teamResult.error}
          <br />
          <Button
            variant="light"
            color="red"
            size="xs"
            mt="sm"
            onClick={teamResult.refetch}
          >
            Retry
          </Button>
        </Alert>
      </Stack>
    );
  }

  // ---- Render -------------------------------------------------------------

  return (
    <Stack gap="lg">
      {/* Page header */}
      <Group justify="space-between" align="flex-start">
        <div>
          <Title order={2}>Team</Title>
          <Text c="dimmed" size="sm">
            Manage your support team members
          </Text>
        </div>
        <Button color={BRAND_RED} onClick={() => setInviteModalOpen(true)}>
          Invite Member
        </Button>
      </Group>

      {/* Summary line */}
      <Text size="sm" c="dimmed">
        {members.length} member{members.length !== 1 ? 's' : ''} ({activeCount} active
        {inactiveCount > 0 ? `, ${inactiveCount} inactive` : ''})
      </Text>

      {/* Team members table */}
      <Paper radius="md" withBorder>
        <Table.ScrollContainer minWidth={640}>
          <Table verticalSpacing="sm" horizontalSpacing="md">
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Member</Table.Th>
                <Table.Th>Role</Table.Th>
                <Table.Th>Status</Table.Th>
                <Table.Th>Last Active</Table.Th>
                <Table.Th ta="right">Actions</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {members.length === 0 && (
                <Table.Tr>
                  <Table.Td colSpan={5}>
                    <Text ta="center" c="dimmed" py="xl" size="sm">
                      No team members yet. Invite your first team member to get started.
                    </Text>
                  </Table.Td>
                </Table.Tr>
              )}
              {members.map((member) => {
                const displayName = member.displayName || member.email?.split('@')[0] || 'Unknown';
                const displayRole = roleOverrides[member.id] || member.role;
                const memberStatus = member.isActive ? 'active' : 'disabled';
                const statusStyle = statusColorMap[memberStatus] || {
                  color: 'gray',
                  variant: 'filled',
                };

                return (
                  <Table.Tr key={member.id}>
                    {/* Member: avatar + name + email */}
                    <Table.Td>
                      <Group gap="sm">
                        <Avatar
                          size={36}
                          radius="xl"
                          color={avatarColor(displayName)}
                          variant="filled"
                        >
                          {getInitials(displayName)}
                        </Avatar>
                        <div>
                          <Text size="sm" fw={500} lh={1.3}>
                            {displayName}
                          </Text>
                          <Text size="xs" c="dimmed" lh={1.3}>
                            {member.email}
                          </Text>
                        </div>
                      </Group>
                    </Table.Td>

                    {/* Role badge */}
                    <Table.Td>
                      <Badge
                        variant="light"
                        color={roleColorMap[displayRole] || 'gray'}
                        size="sm"
                        tt="capitalize"
                      >
                        {displayRole}
                      </Badge>
                    </Table.Td>

                    {/* Status badge */}
                    <Table.Td>
                      <Badge
                        variant={statusStyle.variant as any}
                        color={statusStyle.color}
                        size="sm"
                        tt="capitalize"
                      >
                        {memberStatus}
                      </Badge>
                    </Table.Td>

                    {/* Last active */}
                    <Table.Td>
                      <Text size="sm" c="dimmed">
                        {formatLastActive(member.lastLoginAt)}
                      </Text>
                    </Table.Td>

                    {/* Actions */}
                    <Table.Td>
                      <Group gap="xs" justify="flex-end">
                        {member.role !== 'owner' ? (
                          <>
                            <Select
                              size="xs"
                              w={110}
                              value={displayRole}
                              data={[
                                { value: 'admin', label: 'Admin' },
                                { value: 'agent', label: 'Agent' },
                                { value: 'viewer', label: 'Viewer' },
                              ]}
                              onChange={(val) => handleRoleChange(member.id, val)}
                              allowDeselect={false}
                            />
                            <Tooltip label="Remove member" position="left">
                              <ActionIcon
                                variant="subtle"
                                color="red"
                                size="sm"
                                onClick={() => handleRemove(member.id, member.email)}
                              >
                                <svg
                                  width="14"
                                  height="14"
                                  viewBox="0 0 24 24"
                                  fill="none"
                                  stroke="currentColor"
                                  strokeWidth="2"
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                >
                                  <polyline points="3 6 5 6 21 6" />
                                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                                </svg>
                              </ActionIcon>
                            </Tooltip>
                          </>
                        ) : (
                          <Text size="xs" c="dimmed" fs="italic">
                            Account owner
                          </Text>
                        )}
                      </Group>
                    </Table.Td>
                  </Table.Tr>
                );
              })}
            </Table.Tbody>
          </Table>
        </Table.ScrollContainer>
      </Paper>

      {/* Roles & Permissions accordion */}
      <Accordion variant="contained" radius="md">
        <Accordion.Item value="permissions">
          <Accordion.Control>
            <Text fw={600} size="sm">
              Roles & Permissions
            </Text>
          </Accordion.Control>
          <Accordion.Panel>
            <Table verticalSpacing="sm" horizontalSpacing="md">
              <Table.Thead>
                <Table.Tr>
                  <Table.Th w={120}>Role</Table.Th>
                  <Table.Th>Permissions</Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {permissionsData.map((row) => (
                  <Table.Tr key={row.role}>
                    <Table.Td>
                      <Badge variant="light" color={row.color} size="sm">
                        {row.role}
                      </Badge>
                    </Table.Td>
                    <Table.Td>
                      <Text size="sm">{row.permissions}</Text>
                    </Table.Td>
                  </Table.Tr>
                ))}
              </Table.Tbody>
            </Table>
          </Accordion.Panel>
        </Accordion.Item>
      </Accordion>

      {/* Invite Modal */}
      <Modal
        opened={inviteModalOpen}
        onClose={closeInviteModal}
        title={
          <Text fw={600} size="lg">
            Invite Team Member
          </Text>
        }
        centered
        size="md"
      >
        <Stack gap="md">
          <TextInput
            label="Email address"
            placeholder="colleague@yourcompany.com"
            required
            value={inviteEmail}
            onChange={(e) => setInviteEmail(e.currentTarget.value)}
            type="email"
          />
          <TextInput
            label="Name (optional)"
            placeholder="Jane Smith"
            value={inviteName}
            onChange={(e) => setInviteName(e.currentTarget.value)}
          />
          <Select
            label="Role"
            placeholder="Select a role"
            data={[
              { value: 'admin', label: 'Admin' },
              { value: 'agent', label: 'Agent' },
              { value: 'viewer', label: 'Viewer' },
            ]}
            value={inviteRole}
            onChange={setInviteRole}
            allowDeselect={false}
          />
          <Textarea
            label="Message (optional)"
            placeholder="Add a personal note to the invitation email..."
            value={inviteMessage}
            onChange={(e) => setInviteMessage(e.currentTarget.value)}
            minRows={3}
          />
          {inviteError && (
            <Text size="sm" c="red">
              {inviteError}
            </Text>
          )}
          <Group justify="flex-end" mt="sm">
            <Button variant="default" onClick={closeInviteModal}>
              Cancel
            </Button>
            <Button
              color={BRAND_RED}
              onClick={handleInvite}
              disabled={!inviteEmail.trim() || !inviteRole}
              loading={inviting}
            >
              Send Invite
            </Button>
          </Group>
        </Stack>
      </Modal>
    </Stack>
  );
};
