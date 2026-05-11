// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * RetryConfig — Rate limit and back-off/retry configuration.
 *
 * Two tabs: Rate Limits (per-tier RPM config) and Retry/Back-off (per-service).
 * Both include audit history views.
 *
 * API: GET/PUT  /api/superadmin/rate-limits[/{tier}]
 *      GET      /api/superadmin/rate-limits/history
 *      GET/PUT  /api/superadmin/retry-configs[/{service}]
 *      GET      /api/superadmin/retry-configs/history
 *
 * WI-1426 / SPEC-1819, SPEC-1821
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useCallback, useEffect, useState } from 'react';
import {
  Badge,
  Button,
  Code,
  Group,
  Loader,
  Modal,
  NumberInput,
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

interface RateLimitConfig {
  rpm: number;
  floor: number;
  burstMultiplier: number;
  exemptRoles: string[];
}

interface RateLimitResponse {
  tier: string;
  config: RateLimitConfig;
  version: number;
  updatedAt: string | null;
  updatedBy: string | null;
}

interface RetryConfigData {
  maxRetries: number;
  baseDelayMs: number;
  maxDelayMs: number;
  backoffMultiplier: number;
  jitterEnabled: boolean;
}

interface RetryConfigResponse {
  service: string;
  config: RetryConfigData;
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

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const RetryConfigPage: React.FC = () => {
  const { apiFetch, onNotify } = useProviderContext();
  const [rateLimits, setRateLimits] = useState<RateLimitResponse[]>([]);
  const [retryConfigs, setRetryConfigs] = useState<RetryConfigResponse[]>([]);
  const [rlHistory, setRlHistory] = useState<HistoryEntry[]>([]);
  const [retryHistory, setRetryHistory] = useState<HistoryEntry[]>([]);
  const [loading, setLoading] = useState(true);

  // Rate limit edit modal
  const [editRL, setEditRL] = useState<RateLimitResponse | null>(null);
  const [rlRpm, setRlRpm] = useState(300);
  const [rlFloor, setRlFloor] = useState(10);
  const [rlBurst, setRlBurst] = useState(1.0);
  const [rlReason, setRlReason] = useState('');
  const [rlSaving, setRlSaving] = useState(false);

  // Retry edit modal
  const [editRetry, setEditRetry] = useState<RetryConfigResponse | null>(null);
  const [retryMaxRetries, setRetryMaxRetries] = useState(3);
  const [retryBaseDelay, setRetryBaseDelay] = useState(1000);
  const [retryMaxDelay, setRetryMaxDelay] = useState(30000);
  const [retryMultiplier, setRetryMultiplier] = useState(2.0);
  const [retryReason, setRetryReason] = useState('');
  const [retrySaving, setRetrySaving] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [rlRes, retryRes, rlHistRes, retryHistRes] = await Promise.all([
        apiFetch('/api/superadmin/rate-limits'),
        apiFetch('/api/superadmin/retry-configs'),
        apiFetch('/api/superadmin/rate-limits/history'),
        apiFetch('/api/superadmin/retry-configs/history'),
      ]);
      if (rlRes.ok) { const d = await rlRes.json(); setRateLimits(d.configs || []); }
      if (retryRes.ok) { const d = await retryRes.json(); setRetryConfigs(d.configs || []); }
      if (rlHistRes.ok) { const d = await rlHistRes.json(); setRlHistory(d.entries || []); }
      if (retryHistRes.ok) { const d = await retryHistRes.json(); setRetryHistory(d.entries || []); }
    } catch {
      onNotify('Failed to load configuration data', 'error');
    } finally {
      setLoading(false);
    }
  }, [apiFetch, onNotify]);

  useEffect(() => { loadData(); }, [loadData]);

  const openRLEdit = useCallback((rl: RateLimitResponse) => {
    setEditRL(rl);
    setRlRpm(rl.config.rpm);
    setRlFloor(rl.config.floor);
    setRlBurst(rl.config.burstMultiplier);
    setRlReason('');
  }, []);

  const saveRL = useCallback(async () => {
    if (!editRL) return;
    setRlSaving(true);
    try {
      const res = await apiFetch(`/api/superadmin/rate-limits/${editRL.tier}`, {
        method: 'PUT',
        body: JSON.stringify({
          config: { rpm: rlRpm, floor: rlFloor, burstMultiplier: rlBurst, exemptRoles: ['platform_admin'] },
          changeReason: rlReason,
        }),
      });
      if (res.ok) {
        onNotify(`Updated ${editRL.tier} rate limits`, 'success');
        setEditRL(null);
        loadData();
      } else {
        const err = await res.json();
        onNotify(err.detail || 'Save failed', 'error');
      }
    } catch {
      onNotify('Network error', 'error');
    } finally {
      setRlSaving(false);
    }
  }, [editRL, rlRpm, rlFloor, rlBurst, rlReason, apiFetch, onNotify, loadData]);

  const openRetryEdit = useCallback((rc: RetryConfigResponse) => {
    setEditRetry(rc);
    setRetryMaxRetries(rc.config.maxRetries);
    setRetryBaseDelay(rc.config.baseDelayMs);
    setRetryMaxDelay(rc.config.maxDelayMs);
    setRetryMultiplier(rc.config.backoffMultiplier);
    setRetryReason('');
  }, []);

  const saveRetry = useCallback(async () => {
    if (!editRetry) return;
    setRetrySaving(true);
    try {
      const res = await apiFetch(`/api/superadmin/retry-configs/${editRetry.service}`, {
        method: 'PUT',
        body: JSON.stringify({
          config: {
            maxRetries: retryMaxRetries,
            baseDelayMs: retryBaseDelay,
            maxDelayMs: retryMaxDelay,
            backoffMultiplier: retryMultiplier,
            jitterEnabled: true,
          },
          changeReason: retryReason,
        }),
      });
      if (res.ok) {
        onNotify(`Updated ${editRetry.service} retry config`, 'success');
        setEditRetry(null);
        loadData();
      } else {
        const err = await res.json();
        onNotify(err.detail || 'Save failed', 'error');
      }
    } catch {
      onNotify('Network error', 'error');
    } finally {
      setRetrySaving(false);
    }
  }, [editRetry, retryMaxRetries, retryBaseDelay, retryMaxDelay, retryMultiplier, retryReason, apiFetch, onNotify, loadData]);

  if (loading) return <Loader size="lg" />;

  return (
    <Stack gap="md">
      <Title order={2}>Rate Limits & Retry Configuration</Title>
      <Text c="dimmed" size="sm">Per-tier rate limits (SPEC-1819) and per-service retry/back-off (SPEC-1821)</Text>

      <Tabs defaultValue="rate-limits">
        <Tabs.List>
          <Tabs.Tab value="rate-limits">Rate Limits ({rateLimits.length})</Tabs.Tab>
          <Tabs.Tab value="retry">Retry/Back-off ({retryConfigs.length})</Tabs.Tab>
          <Tabs.Tab value="history">History ({rlHistory.length + retryHistory.length})</Tabs.Tab>
        </Tabs.List>

        <Tabs.Panel value="rate-limits" pt="md">
          <Table striped highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Tier</Table.Th>
                <Table.Th>RPM</Table.Th>
                <Table.Th>Floor</Table.Th>
                <Table.Th>Burst</Table.Th>
                <Table.Th>Version</Table.Th>
                <Table.Th>Updated</Table.Th>
                <Table.Th>Actions</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {rateLimits.map(rl => (
                <Table.Tr key={rl.tier}>
                  <Table.Td><Badge size="sm">{rl.tier}</Badge></Table.Td>
                  <Table.Td><Code>{rl.config.rpm}</Code></Table.Td>
                  <Table.Td>{rl.config.floor}</Table.Td>
                  <Table.Td>{rl.config.burstMultiplier}x</Table.Td>
                  <Table.Td>v{rl.version}</Table.Td>
                  <Table.Td>{rl.updatedAt ? new Date(rl.updatedAt).toLocaleString() : '—'}</Table.Td>
                  <Table.Td>
                    <Button size="xs" variant="light" onClick={() => openRLEdit(rl)}>Edit</Button>
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </Tabs.Panel>

        <Tabs.Panel value="retry" pt="md">
          <Table striped highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Service</Table.Th>
                <Table.Th>Max Retries</Table.Th>
                <Table.Th>Base Delay</Table.Th>
                <Table.Th>Max Delay</Table.Th>
                <Table.Th>Multiplier</Table.Th>
                <Table.Th>Version</Table.Th>
                <Table.Th>Actions</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {retryConfigs.map(rc => (
                <Table.Tr key={rc.service}>
                  <Table.Td><Badge size="sm">{rc.service}</Badge></Table.Td>
                  <Table.Td>{rc.config.maxRetries}</Table.Td>
                  <Table.Td>{rc.config.baseDelayMs}ms</Table.Td>
                  <Table.Td>{rc.config.maxDelayMs}ms</Table.Td>
                  <Table.Td>{rc.config.backoffMultiplier}x</Table.Td>
                  <Table.Td>v{rc.version}</Table.Td>
                  <Table.Td>
                    <Button size="xs" variant="light" onClick={() => openRetryEdit(rc)}>Edit</Button>
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
                <Table.Th>Type</Table.Th>
                <Table.Th>Actor</Table.Th>
                <Table.Th>Details</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {[...rlHistory, ...retryHistory]
                .sort((a, b) => (b.timestamp || '').localeCompare(a.timestamp || ''))
                .map(h => (
                  <Table.Tr key={h.id}>
                    <Table.Td>{new Date(h.timestamp).toLocaleString()}</Table.Td>
                    <Table.Td><Code>{h.eventType}</Code></Table.Td>
                    <Table.Td>{h.actor}</Table.Td>
                    <Table.Td>
                      <Text size="xs" lineClamp={1}>
                        {JSON.stringify(h.payload).slice(0, 120)}
                      </Text>
                    </Table.Td>
                  </Table.Tr>
                ))}
            </Table.Tbody>
          </Table>
        </Tabs.Panel>
      </Tabs>

      {/* Rate Limit Edit Modal */}
      <Modal opened={!!editRL} onClose={() => setEditRL(null)} title={`Edit ${editRL?.tier} Rate Limits`} size="md">
        <Stack gap="md">
          <NumberInput label="Requests Per Minute (RPM)" value={rlRpm} onChange={v => setRlRpm(typeof v === 'number' ? v : 300)} min={1} />
          <NumberInput label="Floor (minimum RPM)" value={rlFloor} onChange={v => setRlFloor(typeof v === 'number' ? v : 0)} min={0} />
          <NumberInput label="Burst Multiplier" value={rlBurst} onChange={v => setRlBurst(typeof v === 'number' ? v : 1.0)} min={1.0} max={5.0} step={0.1} decimalScale={1} />
          <TextInput label="Change Reason" placeholder="Why are you making this change?" value={rlReason} onChange={e => setRlReason(e.currentTarget.value)} />
          <Group justify="flex-end">
            <Button variant="default" onClick={() => setEditRL(null)}>Cancel</Button>
            <Button onClick={saveRL} loading={rlSaving}>Save</Button>
          </Group>
        </Stack>
      </Modal>

      {/* Retry Config Edit Modal */}
      <Modal opened={!!editRetry} onClose={() => setEditRetry(null)} title={`Edit ${editRetry?.service} Retry Config`} size="md">
        <Stack gap="md">
          <NumberInput label="Max Retries" value={retryMaxRetries} onChange={v => setRetryMaxRetries(typeof v === 'number' ? v : 3)} min={0} max={10} />
          <NumberInput label="Base Delay (ms)" value={retryBaseDelay} onChange={v => setRetryBaseDelay(typeof v === 'number' ? v : 1000)} min={100} />
          <NumberInput label="Max Delay (ms)" value={retryMaxDelay} onChange={v => setRetryMaxDelay(typeof v === 'number' ? v : 30000)} min={1000} />
          <NumberInput label="Backoff Multiplier" value={retryMultiplier} onChange={v => setRetryMultiplier(typeof v === 'number' ? v : 2.0)} min={1.0} max={10.0} step={0.5} decimalScale={1} />
          <TextInput label="Change Reason" placeholder="Why are you making this change?" value={retryReason} onChange={e => setRetryReason(e.currentTarget.value)} />
          <Group justify="flex-end">
            <Button variant="default" onClick={() => setEditRetry(null)}>Cancel</Button>
            <Button onClick={saveRetry} loading={retrySaving}>Save</Button>
          </Group>
        </Stack>
      </Modal>
    </Stack>
  );
};
