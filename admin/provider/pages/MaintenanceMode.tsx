/**
 * MaintenanceMode — Maintenance mode management.
 *
 * View current maintenance state, enable/disable, configure schedule,
 * exempt IPs, and customize the maintenance message.
 *
 * API: GET /api/superadmin/maintenance
 *      PUT /api/superadmin/maintenance
 *
 * WI-1432 / SPEC-1829
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useCallback, useEffect, useState } from 'react';
import {
  Badge,
  Button,
  Code,
  Group,
  Loader,
  NumberInput,
  Stack,
  Switch,
  Table,
  Text,
  Textarea,
  TextInput,
  Title,
} from '@mantine/core';
import { useProviderContext } from '../layouts/ProviderLayout';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface MaintenanceState {
  enabled: boolean;
  message: string;
  retryAfterSeconds: number;
  scheduledStart: string | null;
  scheduledEnd: string | null;
  exemptIps: string[];
}

interface MaintenanceResponse {
  state: MaintenanceState;
  isActive: boolean;
  version: number;
  updatedAt: string | null;
  updatedBy: string | null;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const MaintenanceModePage: React.FC = () => {
  const { apiFetch, onNotify } = useProviderContext();
  const [data, setData] = useState<MaintenanceResponse | null>(null);
  const [loading, setLoading] = useState(true);

  // Edit state
  const [editing, setEditing] = useState(false);
  const [enabled, setEnabled] = useState(false);
  const [message, setMessage] = useState('');
  const [retryAfter, setRetryAfter] = useState(300);
  const [scheduledStart, setScheduledStart] = useState('');
  const [scheduledEnd, setScheduledEnd] = useState('');
  const [exemptIps, setExemptIps] = useState('');
  const [saving, setSaving] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiFetch('/api/superadmin/maintenance');
      if (res.ok) {
        const d: MaintenanceResponse = await res.json();
        setData(d);
        setEnabled(d.state.enabled);
        setMessage(d.state.message);
        setRetryAfter(d.state.retryAfterSeconds);
        setScheduledStart(d.state.scheduledStart || '');
        setScheduledEnd(d.state.scheduledEnd || '');
        setExemptIps(d.state.exemptIps.join('\n'));
      }
    } catch {
      onNotify('Failed to load maintenance state', 'error');
    } finally {
      setLoading(false);
    }
  }, [apiFetch, onNotify]);

  useEffect(() => { loadData(); }, [loadData]);

  const handleSave = useCallback(async () => {
    setSaving(true);
    try {
      const ips = exemptIps.split('\n').map(s => s.trim()).filter(Boolean);
      const res = await apiFetch('/api/superadmin/maintenance', {
        method: 'PUT',
        body: JSON.stringify({
          enabled,
          message,
          retryAfterSeconds: retryAfter,
          scheduledStart: scheduledStart || null,
          scheduledEnd: scheduledEnd || null,
          exemptIps: ips,
        }),
      });
      if (res.ok) {
        onNotify(enabled ? 'Maintenance mode enabled' : 'Maintenance mode disabled', 'success');
        setEditing(false);
        loadData();
      } else {
        const err = await res.json();
        onNotify(err.detail || 'Save failed', 'error');
      }
    } catch {
      onNotify('Network error', 'error');
    } finally {
      setSaving(false);
    }
  }, [enabled, message, retryAfter, scheduledStart, scheduledEnd, exemptIps, apiFetch, onNotify, loadData]);

  if (loading) return <Loader size="lg" />;

  return (
    <Stack gap="md">
      <Group justify="space-between">
        <div>
          <Title order={2}>Maintenance Mode</Title>
          <Text c="dimmed" size="sm">Enable/disable maintenance mode with schedule support (SPEC-1829)</Text>
        </div>
        {!editing && (
          <Button variant="light" onClick={() => setEditing(true)}>Edit</Button>
        )}
      </Group>

      {!editing && data ? (
        <Stack gap="md">
          {/* Status Overview */}
          <Group>
            <Text size="sm" fw={500}>Current Status:</Text>
            <Badge color={data.isActive ? 'red' : 'green'} size="lg">
              {data.isActive ? 'MAINTENANCE ACTIVE' : 'NORMAL OPERATION'}
            </Badge>
          </Group>

          <Table>
            <Table.Tbody>
              <Table.Tr>
                <Table.Td fw={500}>Enabled</Table.Td>
                <Table.Td>
                  <Badge color={data.state.enabled ? 'red' : 'green'} size="sm">
                    {data.state.enabled ? 'Yes' : 'No'}
                  </Badge>
                </Table.Td>
              </Table.Tr>
              <Table.Tr>
                <Table.Td fw={500}>Message</Table.Td>
                <Table.Td><Text size="sm">{data.state.message}</Text></Table.Td>
              </Table.Tr>
              <Table.Tr>
                <Table.Td fw={500}>Retry-After</Table.Td>
                <Table.Td>{data.state.retryAfterSeconds}s</Table.Td>
              </Table.Tr>
              <Table.Tr>
                <Table.Td fw={500}>Scheduled Start</Table.Td>
                <Table.Td>
                  {data.state.scheduledStart
                    ? new Date(data.state.scheduledStart).toLocaleString()
                    : '—'}
                </Table.Td>
              </Table.Tr>
              <Table.Tr>
                <Table.Td fw={500}>Scheduled End</Table.Td>
                <Table.Td>
                  {data.state.scheduledEnd
                    ? new Date(data.state.scheduledEnd).toLocaleString()
                    : '—'}
                </Table.Td>
              </Table.Tr>
              <Table.Tr>
                <Table.Td fw={500}>Exempt IPs</Table.Td>
                <Table.Td>
                  {data.state.exemptIps.length > 0
                    ? data.state.exemptIps.map(ip => <Code key={ip} mr={4}>{ip}</Code>)
                    : <Text size="sm" c="dimmed">None</Text>}
                </Table.Td>
              </Table.Tr>
              <Table.Tr>
                <Table.Td fw={500}>Version</Table.Td>
                <Table.Td>v{data.version}</Table.Td>
              </Table.Tr>
              <Table.Tr>
                <Table.Td fw={500}>Last Updated</Table.Td>
                <Table.Td>
                  {data.updatedAt ? new Date(data.updatedAt).toLocaleString() : '—'}
                  {data.updatedBy && ` by ${data.updatedBy}`}
                </Table.Td>
              </Table.Tr>
            </Table.Tbody>
          </Table>
        </Stack>
      ) : editing ? (
        <Stack gap="md">
          <Switch
            label="Enable Maintenance Mode"
            checked={enabled}
            onChange={e => setEnabled(e.currentTarget.checked)}
            size="lg"
            color="red"
          />
          <Textarea
            label="Maintenance Message"
            value={message}
            onChange={e => setMessage(e.currentTarget.value)}
            minRows={3}
          />
          <NumberInput
            label="Retry-After (seconds)"
            value={retryAfter}
            onChange={v => setRetryAfter(typeof v === 'number' ? v : 300)}
            min={60}
            max={86400}
          />
          <TextInput
            label="Scheduled Start (ISO 8601)"
            placeholder="2026-03-16T22:00:00Z"
            value={scheduledStart}
            onChange={e => setScheduledStart(e.currentTarget.value)}
          />
          <TextInput
            label="Scheduled End (ISO 8601)"
            placeholder="2026-03-17T02:00:00Z"
            value={scheduledEnd}
            onChange={e => setScheduledEnd(e.currentTarget.value)}
          />
          <Textarea
            label="Exempt IPs (one per line)"
            placeholder="98.210.223.74"
            value={exemptIps}
            onChange={e => setExemptIps(e.currentTarget.value)}
            minRows={3}
          />
          <Group justify="flex-end">
            <Button variant="default" onClick={() => { setEditing(false); loadData(); }}>Cancel</Button>
            <Button onClick={handleSave} loading={saving} color={enabled ? 'red' : undefined}>
              {enabled ? 'Enable Maintenance' : 'Save (Disabled)'}
            </Button>
          </Group>
        </Stack>
      ) : null}
    </Stack>
  );
};
