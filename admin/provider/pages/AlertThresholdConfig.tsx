/**
 * AlertThresholdConfig — Alert threshold configuration per metric.
 *
 * 5 metric types: error_rate, traffic_volume, response_time, queue_depth, resource_utilization.
 * Each has typed threshold fields and an evaluation interval.
 *
 * API: GET/PUT  /api/superadmin/alert-thresholds[/{metric}]
 *      GET      /api/superadmin/alert-thresholds/history
 *
 * WI-1427 / SPEC-1822
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
  NumberInput,
  Stack,
  Switch,
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

interface AlertThreshold {
  metric: string;
  config: Record<string, unknown>;
  evaluationIntervalS: number;
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

const METRIC_LABELS: Record<string, string> = {
  error_rate: 'Error Rate',
  traffic_volume: 'Traffic Volume',
  response_time: 'Response Time',
  queue_depth: 'Queue Depth',
  resource_utilization: 'Resource Utilization',
};

const METRIC_COLORS: Record<string, string> = {
  error_rate: 'red',
  traffic_volume: 'blue',
  response_time: 'orange',
  queue_depth: 'cyan',
  resource_utilization: 'violet',
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const AlertThresholdConfigPage: React.FC = () => {
  const { apiFetch, onNotify } = useProviderContext();
  const [thresholds, setThresholds] = useState<AlertThreshold[]>([]);
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [loading, setLoading] = useState(true);

  // Edit modal
  const [editThreshold, setEditThreshold] = useState<AlertThreshold | null>(null);
  const [editConfig, setEditConfig] = useState('');
  const [editInterval, setEditInterval] = useState(60);
  const [editEnabled, setEditEnabled] = useState(true);
  const [editReason, setEditReason] = useState('');
  const [saving, setSaving] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [thRes, histRes] = await Promise.all([
        apiFetch('/api/superadmin/alert-thresholds'),
        apiFetch('/api/superadmin/alert-thresholds/history'),
      ]);
      if (thRes.ok) { const d = await thRes.json(); setThresholds(d.thresholds || []); }
      if (histRes.ok) { const d = await histRes.json(); setHistory(d.entries || []); }
    } catch {
      onNotify('Failed to load alert thresholds', 'error');
    } finally {
      setLoading(false);
    }
  }, [apiFetch, onNotify]);

  useEffect(() => { loadData(); }, [loadData]);

  const handleEdit = useCallback((t: AlertThreshold) => {
    setEditThreshold(t);
    setEditConfig(JSON.stringify(t.config, null, 2));
    setEditInterval(t.evaluationIntervalS);
    setEditEnabled(t.enabled);
    setEditReason('');
  }, []);

  const handleSave = useCallback(async () => {
    if (!editThreshold) return;
    setSaving(true);
    try {
      const parsed = JSON.parse(editConfig);
      const res = await apiFetch(`/api/superadmin/alert-thresholds/${editThreshold.metric}`, {
        method: 'PUT',
        body: JSON.stringify({
          config: parsed,
          evaluationIntervalS: editInterval,
          enabled: editEnabled,
          changeReason: editReason,
        }),
      });
      if (res.ok) {
        onNotify(`Updated ${editThreshold.metric} threshold`, 'success');
        setEditThreshold(null);
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
  }, [editThreshold, editConfig, editInterval, editEnabled, editReason, apiFetch, onNotify, loadData]);

  if (loading) return <Loader size="lg" />;

  return (
    <Stack gap="md">
      <Title order={2}>Alert Thresholds</Title>
      <Text c="dimmed" size="sm">Configure warning and critical thresholds per metric type (SPEC-1822)</Text>

      <Tabs defaultValue="thresholds">
        <Tabs.List>
          <Tabs.Tab value="thresholds">Thresholds ({thresholds.length})</Tabs.Tab>
          <Tabs.Tab value="history">History ({history.length})</Tabs.Tab>
        </Tabs.List>

        <Tabs.Panel value="thresholds" pt="md">
          <Table striped highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Metric</Table.Th>
                <Table.Th>Enabled</Table.Th>
                <Table.Th>Eval Interval</Table.Th>
                <Table.Th>Config Summary</Table.Th>
                <Table.Th>Version</Table.Th>
                <Table.Th>Actions</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {thresholds.map(t => (
                <Table.Tr key={t.metric}>
                  <Table.Td>
                    <Badge color={METRIC_COLORS[t.metric] || 'gray'} size="sm">
                      {METRIC_LABELS[t.metric] || t.metric}
                    </Badge>
                  </Table.Td>
                  <Table.Td>
                    <Badge color={t.enabled ? 'green' : 'gray'} size="sm">
                      {t.enabled ? 'Active' : 'Disabled'}
                    </Badge>
                  </Table.Td>
                  <Table.Td>{t.evaluationIntervalS}s</Table.Td>
                  <Table.Td>
                    <Text size="xs" lineClamp={1}>
                      {Object.entries(t.config).map(([k, v]) => `${k}: ${v}`).join(', ')}
                    </Text>
                  </Table.Td>
                  <Table.Td>v{t.version}</Table.Td>
                  <Table.Td>
                    <Button size="xs" variant="light" onClick={() => handleEdit(t)}>Edit</Button>
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
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
        opened={!!editThreshold}
        onClose={() => setEditThreshold(null)}
        title={`Edit ${METRIC_LABELS[editThreshold?.metric || ''] || editThreshold?.metric} Threshold`}
        size="lg"
      >
        <Stack gap="md">
          <JsonInput
            label="Threshold Configuration (JSON)"
            value={editConfig}
            onChange={setEditConfig}
            minRows={8}
            autosize
            formatOnBlur
            validationError="Invalid JSON"
          />
          <NumberInput
            label="Evaluation Interval (seconds)"
            value={editInterval}
            onChange={v => setEditInterval(typeof v === 'number' ? v : 60)}
            min={10}
            max={3600}
          />
          <Switch
            label="Enabled"
            checked={editEnabled}
            onChange={e => setEditEnabled(e.currentTarget.checked)}
          />
          <TextInput
            label="Change Reason"
            placeholder="Why are you making this change?"
            value={editReason}
            onChange={e => setEditReason(e.currentTarget.value)}
          />
          <Group justify="flex-end">
            <Button variant="default" onClick={() => setEditThreshold(null)}>Cancel</Button>
            <Button onClick={handleSave} loading={saving}>Save</Button>
          </Group>
        </Stack>
      </Modal>
    </Stack>
  );
};
