// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

import React, { useState } from 'react';
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
} from '@mantine/core';
import { TEAM_MEMBERS, TeamMember } from '../../data/mockData';

const BRAND_RED = '#C41E2A';

const avatarColors: Record<string, string> = {
  'Mike VanDusen': '#C41E2A',
  'Alex Kim': '#2563EB',
  'Dana Park': '#059669',
  'Jordan Lee': '#7C3AED',
};

function getInitials(name: string): string {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase();
}

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

function formatLastActive(dateStr: string): string {
  if (!dateStr) return 'Never';
  const now = new Date('2026-02-02T15:35:00Z');
  const then = new Date(dateStr);
  const diffMs = now.getTime() - then.getTime();
  const diffMin = Math.floor(diffMs / 60000);
  if (diffMin < 2) return 'Just now';
  if (diffMin < 60) return `${diffMin} min ago`;
  const diffHours = Math.floor(diffMin / 60);
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
}

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

export function TeamPage() {
  const [inviteModalOpen, setInviteModalOpen] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState<string | null>('agent');
  const [inviteMessage, setInviteMessage] = useState('');
  const [members, setMembers] = useState<TeamMember[]>(TEAM_MEMBERS);

  const activeCount = members.filter((m) => m.status === 'active').length;
  const invitedCount = members.filter((m) => m.status === 'invited').length;

  const handleRoleChange = (memberId: string, newRole: string | null) => {
    if (!newRole) return;
    setMembers((prev) =>
      prev.map((m) =>
        m.id === memberId ? { ...m, role: newRole as TeamMember['role'] } : m
      )
    );
  };

  const handleRemove = (memberId: string) => {
    setMembers((prev) => prev.filter((m) => m.id !== memberId));
  };

  const handleInvite = () => {
    if (!inviteEmail || !inviteRole) return;
    const newMember: TeamMember = {
      id: `team-${Date.now()}`,
      name: inviteEmail.split('@')[0],
      email: inviteEmail,
      role: inviteRole as TeamMember['role'],
      avatar: '',
      status: 'invited',
      lastActive: '',
      assignedConversations: 0,
    };
    setMembers((prev) => [...prev, newMember]);
    setInviteEmail('');
    setInviteRole('agent');
    setInviteMessage('');
    setInviteModalOpen(false);
  };

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
        {invitedCount > 0 ? `, ${invitedCount} invited` : ''})
      </Text>

      {/* Team members table */}
      <Paper radius="md" withBorder>
        <Table.ScrollContainer minWidth={720}>
          <Table verticalSpacing="sm" horizontalSpacing="md">
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Member</Table.Th>
                <Table.Th>Role</Table.Th>
                <Table.Th>Status</Table.Th>
                <Table.Th>Last Active</Table.Th>
                <Table.Th ta="center">Conversations</Table.Th>
                <Table.Th ta="right">Actions</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {members.map((member) => {
                const statusStyle = statusColorMap[member.status] || {
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
                          color={avatarColors[member.name] || '#868e96'}
                          variant="filled"
                        >
                          {getInitials(member.name)}
                        </Avatar>
                        <div>
                          <Text size="sm" fw={500} lh={1.3}>
                            {member.name}
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
                        color={roleColorMap[member.role] || 'gray'}
                        size="sm"
                        tt="capitalize"
                      >
                        {member.role}
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
                        {member.status}
                      </Badge>
                    </Table.Td>

                    {/* Last active */}
                    <Table.Td>
                      <Text size="sm" c="dimmed">
                        {formatLastActive(member.lastActive)}
                      </Text>
                    </Table.Td>

                    {/* Conversations */}
                    <Table.Td ta="center">
                      <Text size="sm">{member.assignedConversations}</Text>
                    </Table.Td>

                    {/* Actions */}
                    <Table.Td>
                      <Group gap="xs" justify="flex-end">
                        {member.role !== 'owner' ? (
                          <>
                            <Select
                              size="xs"
                              w={110}
                              value={member.role}
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
                                onClick={() => handleRemove(member.id)}
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
        onClose={() => setInviteModalOpen(false)}
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
          <Group justify="flex-end" mt="sm">
            <Button variant="default" onClick={() => setInviteModalOpen(false)}>
              Cancel
            </Button>
            <Button
              color={BRAND_RED}
              onClick={handleInvite}
              disabled={!inviteEmail}
            >
              Send Invite
            </Button>
          </Group>
        </Stack>
      </Modal>
    </Stack>
  );
}
