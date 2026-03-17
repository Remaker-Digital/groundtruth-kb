/**
 * NotificationChannelConfig — Notification channel management.
 *
 * 2 channel types: email, webhook.
 * Email: recipients list + severity filter.
 * Webhook: URL + HMAC secret + timeout.
 * Includes test notification trigger.
 *
 * API: GET/PUT  /api/superadmin/notification-channels[/{channel_type}]
 *      POST     /api/superadmin/notification-channels/{channel_type}/test
 *      GET      /api/superadmin/notification-channels/history
 *
 * WI-1428 / SPEC-1823
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useCallback, useEffect, useState } from 'react';
import {
  Badge,
  Button,
  Code,
  Group,
  JsonInput,
  Loader,
  Modal,
  Stack,
  Table,
  Tabs,
  Text,
  TextInput,
  Title,
} from '@mantine/core';
import { useProviderContext } from '../layouts/ProviderLayout';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface NotificationChannel {
  channelType: string;
  config: Record<string, unknown>;
  enabled: boolean;
  version: number;
  updatedAt: string | null;
  updatedBy: string | null;
}

interface HistoryEntry {
  id: string;
  eventType: string;
  actor: string;
  timestamp: string;
  payload: Record<string, unknown>;
}

interface TestResult {
  sent: boolean;
  detail: string;
}

const CHANNEL_LABELS: Record<string, string> = {
  email: 'Email',
  webhook: 'Webhook',
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const NotificationChannelConfigPage: React.FC = () => {
  const { apiFetch, onNotify } = useProviderContext();
  const [channels, setChannels] = useState<NotificationChannel[]>([]);
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [loading, setLoading] = useState(true);

  // Edit modal
  const [editChannel, setEditChannel] = useState<NotificationChannel | null>(null);
  const [editConfig, setEditConfig] = useState('');
  const [editReason, setEditReason] = useState('');
  const [saving, setSaving] = useState(false);

  // Test notification
  const [testMessage, setTestMessage] = useState('');
  const [testing, setTesting] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [chRes, histRes] = await Promise.all([
        apiFetch('/api/superadmin/notification-channels'),
        apiFetch('/api/superadmin/notification-channels/history'),
      ]);
      if (chRes.ok) { const d = await chRes.json(); setChannels(d.channels || []); }
      if (histRes.ok) { const d = await histRes.json(); setHistory(d.entries || []); }
    } catch {
      onNotify('Failed to load notification channels', 'error');
    } finally {
      setLoading(false);
    }
  }, [apiFetch, onNotify]);

  useEffect(() => { loadData(); }, [loadData]);

  const handleEdit = useCallback((ch: NotificationChannel) => {
    setEditChannel(ch);
    setEditConfig(JSON.stringify(ch.config, null, 2));
    setEditReason('');
  }, []);

  const handleSave = useCallback(async () => {
    if (!editChannel) return;
    setSaving(true);
    try {
      const parsed = JSON.parse(editConfig);
      const res = await apiFetch(`/api/superadmin/notification-channels/${editChannel.channelType}`, {
        method: 'PUT',
        body: JSON.stringify({ config: parsed, changeReason: editReason }),
      });
      if (res.ok) {
        onNotify(`Updated ${editChannel.channelType} channel`, 'success');
        setEditChannel(null);
        loadData();
      } else {
        const err = await res.json();
        onNotify(err.detail || 'Save failed', 'error');
      }
    } catch (e: any) {
      onNotify(e.message || 'Invalid JSON', 'error');
    } finally {
      setSaving(false);
    }
  }, [editChannel, editConfig, editReason, apiFetch, onNotify, loadData]);

  const handleTest = useCallback(async (channelType: string) => {
    setTesting(channelType);
    try {
      const res = await apiFetch(`/api/superadmin/notification-channels/${channelType}/test`, {
        method: 'POST',
        body: JSON.stringify({ message: testMessage || 'Test notification from SPA console' }),
      });
      if (res.ok) {
        const result: TestResult = await res.json();
        if (result.sent) {
          onNotify(`Test notification sent: ${result.detail}`, 'success');
        } else {
          onNotify(`Not sent: ${result.detail}`, 'warning');
        }
      } else {
        onNotify('Test failed', 'error');
      }
    } catch {
      onNotify('Network error', 'error');
    } finally {
      setTesting(null);
    }
  }, [testMessage, apiFetch, onNotify]);

  if (loading) return <Loader size="lg" />;

  return (
    <Stack gap="md">
      <Title order={2}>Notification Channels</Title>
      <Text c="dimmed" size="sm">Configure email and webhook notification delivery (SPEC-1823)</Text>

      <Tabs defaultValue="channels">
        <Tabs.List>
          <Tabs.Tab value="channels">Channels ({channels.length})</Tabs.Tab>
          <Tabs.Tab value="test">Test Notification</Tabs.Tab>
          <Tabs.Tab value="history">History ({history.length})</Tabs.Tab>
        </Tabs.List>

        <Tabs.Panel value="channels" pt="md">
          <Table striped highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Channel</Table.Th>
                <Table.Th>Status</Table.Th>
                <Table.Th>Config Summary</Table.Th>
                <Table.Th>Version</Table.Th>
                <Table.Th>Updated</Table.Th>
                <Table.Th>Actions</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {channels.map(ch => (
                <Table.Tr key={ch.channelType}>
                  <Table.Td>
                    <Badge size="sm">{CHANNEL_LABELS[ch.channelType] || ch.channelType}</Badge>
                  </Table.Td>
                  <Table.Td>
                    <Badge color={ch.enabled ? 'green' : 'gray'} size="sm">
                      {ch.enabled ? 'Enabled' : 'Disabled'}
                    </Badge>
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" lineClamp={1}>
                      {ch.channelType === 'email'
                        ? `Recipients: ${(ch.config.recipients as string[] || []).length}`
                        : `URL: ${ch.config.url || '(not set)'}`}
                    </Text>
                  </Table.Td>
                  <Table.Td>v{ch.version}</Table.Td>
                  <Table.Td>{ch.updatedAt ? new Date(ch.updatedAt).toLocaleString() : '—'}</Table.Td>
                  <Table.Td>
                    <Button size="xs" variant="light" onClick={() => handleEdit(ch)}>Edit</Button>
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </Tabs.Panel>

        <Tabs.Panel value="test" pt="md">
          <Stack gap="md" maw={500}>
            <TextInput
              label="Test Message"
              placeholder="Optional custom message"
              value={testMessage}
              onChange={e => setTestMessage(e.currentTarget.value)}
            />
            <Group>
              {channels.map(ch => (
                <Button
                  key={ch.channelType}
                  variant="light"
                  loading={testing === ch.channelType}
                  onClick={() => handleTest(ch.channelType)}
                >
                  Test {CHANNEL_LABELS[ch.channelType] || ch.channelType}
                </Button>
              ))}
            </Group>
          </Stack>
        </Tabs.Panel>

        <Tabs.Panel value="history" pt="md">
          <Table striped>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Time</Table.Th>
                <Table.Th>Actor</Table.Th>
                <Table.Th>Details</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {history.map(h => (
                <Table.Tr key={h.id}>
                  <Table.Td>{new Date(h.timestamp).toLocaleString()}</Table.Td>
                  <Table.Td>{h.actor}</Table.Td>
                  <Table.Td>
                    <Text size="xs" lineClamp={1}>{JSON.stringify(h.payload).slice(0, 120)}</Text>
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </Tabs.Panel>
      </Tabs>

      {/* Edit Modal */}
      <Modal
        opened={!!editChannel}
        onClose={() => setEditChannel(null)}
        title={`Edit ${CHANNEL_LABELS[editChannel?.channelType || ''] || editChannel?.channelType} Channel`}
        size="lg"
      >
        <Stack gap="md">
          <JsonInput
            label="Channel Configuration (JSON)"
            value={editConfig}
            onChange={setEditConfig}
            minRows={10}
            autosize
            formatOnBlur
            validationError="Invalid JSON"
          />
          <TextInput
            label="Change Reason"
            placeholder="Why are you making this change?"
            value={editReason}
            onChange={e => setEditReason(e.currentTarget.value)}
          />
          <Group justify="flex-end">
            <Button variant="default" onClick={() => setEditChannel(null)}>Cancel</Button>
            <Button onClick={handleSave} loading={saving}>Save</Button>
          </Group>
        </Stack>
      </Modal>
    </Stack>
  );
};
