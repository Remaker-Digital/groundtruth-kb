// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * UserManagement — SPA platform admin user management page (SPEC-1675).
 *
 * Lists all platform admin users (superadmin + operators). Superadmin
 * can create/deactivate operators. All users can generate backup codes
 * and set notification email for themselves.
 *
 * API: GET/POST/DELETE /api/superadmin/platform-admin/users
 *      POST /api/superadmin/platform-admin/users/backup-codes
 *      PUT  /api/superadmin/platform-admin/users/notification-email
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useCallback, useEffect, useState } from 'react';
import {
  ActionIcon,
  Alert,
  Badge,
  Button,
  Card,
  Code,
  CopyButton,
  Group,
  Modal,
  Paper,
  Stack,
  Table,
  Text,
  TextInput,
  Title,
  Tooltip,
} from '@mantine/core';
import { useProviderContext } from '../layouts/ProviderLayout';
import { LoadingState } from '../../shared/LoadingState';
import { HelpTooltip } from '../../shared/HelpTooltip';
import { tokens } from '../../shared/theme/styles';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface PlatformAdminUser {
  adminId: string;
  email: string;
  displayName: string;
  role: string;
  isActive: boolean;
  createdAt: string | null;
  lastLoginAt: string | null;
  notificationEmailAddress: string | null;
  backupCodesRemaining: number;
  createdBy: string | null;
}

interface CreateOperatorResponse {
  adminId: string;
  email: string;
  displayName: string;
  role: string;
  apiKey: string;
  message: string;
}

interface BackupCodesResponse {
  adminId: string;
  codes: string[];
  count: number;
  message: string;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function UserManagementPage() {
  const { apiFetch, onNotify } = useProviderContext();

  const [users, setUsers] = useState<PlatformAdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Create operator modal
  const [showCreate, setShowCreate] = useState(false);
  const [createEmail, setCreateEmail] = useState('');
  const [createName, setCreateName] = useState('');
  const [createLoading, setCreateLoading] = useState(false);
  const [createdKey, setCreatedKey] = useState<string | null>(null);

  // Backup codes modal
  const [showBackupCodes, setShowBackupCodes] = useState(false);
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  const [backupLoading, setBackupLoading] = useState(false);

  // Notification email
  const [editingNotifEmail, setEditingNotifEmail] = useState(false);
  const [notifEmailValue, setNotifEmailValue] = useState('');
  const [notifEmailLoading, setNotifEmailLoading] = useState(false);

  // Deactivate confirmation
  const [deactivateTarget, setDeactivateTarget] = useState<PlatformAdminUser | null>(null);
  const [deactivateLoading, setDeactivateLoading] = useState(false);

  // Current user role (from first user that matches session)
  const currentUserRole = users.find(u => u.isActive)?.role ?? 'operator';
  const isSuperadmin = currentUserRole === 'superadmin';

  // Fetch users
  const fetchUsers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiFetch('/api/superadmin/platform-admin/users');
      if (!res.ok) throw new Error(`Failed to load users: ${res.status}`);
      const data = await res.json();
      setUsers(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load users');
    } finally {
      setLoading(false);
    }
  }, [apiFetch]);

  useEffect(() => { fetchUsers(); }, [fetchUsers]);

  // Create operator
  const handleCreate = useCallback(async () => {
    setCreateLoading(true);
    try {
      const res = await apiFetch('/api/superadmin/platform-admin/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: createEmail, displayName: createName }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Failed: ${res.status}`);
      }
      const data: CreateOperatorResponse = await res.json();
      setCreatedKey(data.apiKey);
      onNotify(`Operator ${data.email} created`, 'success');
      fetchUsers();
    } catch (err: any) {
      onNotify(err.message, 'error');
    } finally {
      setCreateLoading(false);
    }
  }, [apiFetch, createEmail, createName, onNotify, fetchUsers]);

  // Deactivate operator
  const handleDeactivate = useCallback(async () => {
    if (!deactivateTarget) return;
    setDeactivateLoading(true);
    try {
      const res = await apiFetch(
        `/api/superadmin/platform-admin/users/${deactivateTarget.adminId}`,
        { method: 'DELETE' },
      );
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Failed: ${res.status}`);
      }
      onNotify(`Operator ${deactivateTarget.email} deactivated`, 'success');
      setDeactivateTarget(null);
      fetchUsers();
    } catch (err: any) {
      onNotify(err.message, 'error');
    } finally {
      setDeactivateLoading(false);
    }
  }, [apiFetch, deactivateTarget, onNotify, fetchUsers]);

  // Generate backup codes
  const handleBackupCodes = useCallback(async () => {
    setBackupLoading(true);
    try {
      const res = await apiFetch('/api/superadmin/platform-admin/users/backup-codes', {
        method: 'POST',
      });
      if (!res.ok) throw new Error(`Failed: ${res.status}`);
      const data: BackupCodesResponse = await res.json();
      setBackupCodes(data.codes);
      setShowBackupCodes(true);
      onNotify(`${data.count} backup codes generated`, 'success');
      fetchUsers();
    } catch (err: any) {
      onNotify(err.message, 'error');
    } finally {
      setBackupLoading(false);
    }
  }, [apiFetch, onNotify, fetchUsers]);

  // Update notification email
  const handleNotifEmail = useCallback(async () => {
    setNotifEmailLoading(true);
    try {
      const res = await apiFetch('/api/superadmin/platform-admin/users/notification-email', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: notifEmailValue || null }),
      });
      if (!res.ok) throw new Error(`Failed: ${res.status}`);
      onNotify('Notification email updated', 'success');
      setEditingNotifEmail(false);
      fetchUsers();
    } catch (err: any) {
      onNotify(err.message, 'error');
    } finally {
      setNotifEmailLoading(false);
    }
  }, [apiFetch, notifEmailValue, onNotify, fetchUsers]);

  if (loading) return <LoadingState text="Loading users..." />;

  if (error) {
    return (
      <Alert color="red" title="Error">{error}</Alert>
    );
  }

  return (
    <Stack gap="lg">
      <Group justify="space-between" align="center">
        <Group gap="xs">
          <Title order={3}>User Management</Title>
          <HelpTooltip text="Manage SPA platform admin users. Superadmins can create and deactivate operator accounts." />
        </Group>
        <Group gap="sm">
          <Button
            variant="light"
            onClick={handleBackupCodes}
            loading={backupLoading}
          >
            Generate Backup Codes
          </Button>
          {isSuperadmin && (
            <Button
              onClick={() => {
                setShowCreate(true);
                setCreateEmail('');
                setCreateName('');
                setCreatedKey(null);
              }}
            >
              Add Operator
            </Button>
          )}
        </Group>
      </Group>

      {/* Self-service: Notification Email */}
      <Card p="md" radius="md" withBorder>
        <Group justify="space-between" align="center">
          <div>
            <Text fw={600} size="sm">Login Notification Email</Text>
            <Text size="xs" c="dimmed">
              {users[0]?.notificationEmailAddress || 'Not set — notifications go to your primary email'}
            </Text>
          </div>
          {editingNotifEmail ? (
            <Group gap="xs">
              <TextInput
                size="xs"
                placeholder="notification@example.com"
                value={notifEmailValue}
                onChange={(e) => setNotifEmailValue(e.currentTarget.value)}
                style={{ width: 250 }}
              />
              <Button size="xs" onClick={handleNotifEmail} loading={notifEmailLoading}>
                Save
              </Button>
              <Button size="xs" variant="subtle" onClick={() => setEditingNotifEmail(false)}>
                Cancel
              </Button>
            </Group>
          ) : (
            <Button
              size="xs"
              variant="light"
              onClick={() => {
                setEditingNotifEmail(true);
                setNotifEmailValue(users[0]?.notificationEmailAddress || '');
              }}
            >
              Edit
            </Button>
          )}
        </Group>
      </Card>

      {/* Users table */}
      <Paper p="md" radius="md" withBorder>
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Name</Table.Th>
              <Table.Th>Email</Table.Th>
              <Table.Th>Role</Table.Th>
              <Table.Th>Backup Codes</Table.Th>
              <Table.Th>Last Login</Table.Th>
              <Table.Th>Actions</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {users.map((user) => (
              <Table.Tr key={user.adminId}>
                <Table.Td>{user.displayName}</Table.Td>
                <Table.Td>{user.email}</Table.Td>
                <Table.Td>
                  <Badge
                    color={user.role === 'superadmin' ? 'red' : 'blue'}
                    variant="light"
                    size="sm"
                  >
                    {user.role}
                  </Badge>
                </Table.Td>
                <Table.Td>
                  <Text size="sm" c={user.backupCodesRemaining > 0 ? undefined : 'dimmed'}>
                    {user.backupCodesRemaining} remaining
                  </Text>
                </Table.Td>
                <Table.Td>
                  <Text size="sm" c="dimmed">
                    {user.lastLoginAt
                      ? new Date(user.lastLoginAt).toLocaleString()
                      : 'Never'}
                  </Text>
                </Table.Td>
                <Table.Td>
                  {isSuperadmin && user.role === 'operator' && (
                    <Button
                      size="xs"
                      variant="subtle"
                      color="red"
                      onClick={() => setDeactivateTarget(user)}
                    >
                      Remove
                    </Button>
                  )}
                </Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      </Paper>

      {/* Create Operator Modal */}
      <Modal
        opened={showCreate}
        onClose={() => setShowCreate(false)}
        title="Add Operator"
        size="md"
      >
        {createdKey ? (
          <Stack gap="md">
            <Alert color="green" title="Operator Created">
              Save the API key below — it cannot be retrieved later.
            </Alert>
            <Paper p="sm" withBorder>
              <Group gap="xs">
                <Code style={{ flex: 1, wordBreak: 'break-all' }}>{createdKey}</Code>
                <CopyButton value={createdKey}>
                  {({ copied, copy }) => (
                    <Button size="xs" variant="light" onClick={copy}>
                      {copied ? 'Copied' : 'Copy'}
                    </Button>
                  )}
                </CopyButton>
              </Group>
            </Paper>
            <Button onClick={() => setShowCreate(false)}>Done</Button>
          </Stack>
        ) : (
          <Stack gap="md">
            <TextInput
              label="Email"
              placeholder="operator@remaker.digital"
              value={createEmail}
              onChange={(e) => setCreateEmail(e.currentTarget.value)}
              required
            />
            <TextInput
              label="Display Name"
              placeholder="Jane Operator"
              value={createName}
              onChange={(e) => setCreateName(e.currentTarget.value)}
              required
            />
            <Button
              onClick={handleCreate}
              loading={createLoading}
              disabled={!createEmail || !createName}
            >
              Create Operator
            </Button>
          </Stack>
        )}
      </Modal>

      {/* Backup Codes Modal */}
      <Modal
        opened={showBackupCodes}
        onClose={() => setShowBackupCodes(false)}
        title="Backup Recovery Codes"
        size="md"
      >
        <Stack gap="md">
          <Alert color="orange" title="Save These Codes">
            These codes cannot be retrieved later. Each code can only be used once
            to recover your account if you lose your API key.
          </Alert>
          <Paper p="md" withBorder>
            <Stack gap="xs">
              {backupCodes.map((code, i) => (
                <Group key={i} gap="xs">
                  <Text size="sm" c="dimmed" w={20}>{i + 1}.</Text>
                  <Code>{code}</Code>
                </Group>
              ))}
            </Stack>
          </Paper>
          <CopyButton value={backupCodes.join('\n')}>
            {({ copied, copy }) => (
              <Button variant="light" onClick={copy}>
                {copied ? 'Copied All' : 'Copy All Codes'}
              </Button>
            )}
          </CopyButton>
          <Button onClick={() => setShowBackupCodes(false)}>Done</Button>
        </Stack>
      </Modal>

      {/* Deactivate Confirmation Modal */}
      <Modal
        opened={!!deactivateTarget}
        onClose={() => setDeactivateTarget(null)}
        title="Deactivate Operator"
        size="sm"
      >
        <Stack gap="md">
          <Text>
            Are you sure you want to deactivate <strong>{deactivateTarget?.email}</strong>?
            Their API key will stop working immediately.
          </Text>
          <Group justify="flex-end" gap="sm">
            <Button variant="subtle" onClick={() => setDeactivateTarget(null)}>
              Cancel
            </Button>
            <Button
              color="red"
              onClick={handleDeactivate}
              loading={deactivateLoading}
            >
              Deactivate
            </Button>
          </Group>
        </Stack>
      </Modal>
    </Stack>
  );
}
