/**
 * FeatureFlagConfig — Feature flag management and evaluation.
 *
 * View all flags, toggle enable/disable, evaluate flags per tenant.
 * Flags are stored as a single document with per-flag entries.
 *
 * API: GET  /api/superadmin/feature-flags
 *      PUT  /api/superadmin/feature-flags
 *      GET  /api/superadmin/feature-flags/evaluate?flag=...&tenant_id=...
 *
 * WI-1429 / SPEC-1824
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

interface FeatureFlag {
  name: string;
  enabled: boolean;
  description: string;
  allowedTiers: string[];
  allowedTenants: string[];
  rolloutPercent: number;
}

interface FlagListResponse {
  flags: FeatureFlag[];
  version: number;
  updatedAt: string | null;
  updatedBy: string | null;
}

interface EvaluateResult {
  flag: string;
  enabled: boolean;
  reason: string;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const FeatureFlagConfigPage: React.FC = () => {
  const { apiFetch, onNotify } = useProviderContext();
  const [flagData, setFlagData] = useState<FlagListResponse | null>(null);
  const [loading, setLoading] = useState(true);

  // Edit modal
  const [editOpen, setEditOpen] = useState(false);
  const [editJson, setEditJson] = useState('');
  const [editReason, setEditReason] = useState('');
  const [saving, setSaving] = useState(false);

  // Evaluate panel
  const [evalFlag, setEvalFlag] = useState('');
  const [evalTenant, setEvalTenant] = useState('');
  const [evalResult, setEvalResult] = useState<EvaluateResult | null>(null);
  const [evaluating, setEvaluating] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiFetch('/api/superadmin/feature-flags');
      if (res.ok) {
        setFlagData(await res.json());
      }
    } catch {
      onNotify('Failed to load feature flags', 'error');
    } finally {
      setLoading(false);
    }
  }, [apiFetch, onNotify]);

  useEffect(() => { loadData(); }, [loadData]);

  const handleOpenEdit = useCallback(() => {
    setEditJson(JSON.stringify(flagData?.flags || [], null, 2));
    setEditReason('');
    setEditOpen(true);
  }, [flagData]);

  const handleSave = useCallback(async () => {
    setSaving(true);
    try {
      const parsed = JSON.parse(editJson);
      const res = await apiFetch('/api/superadmin/feature-flags', {
        method: 'PUT',
        body: JSON.stringify({ flags: parsed, changeReason: editReason }),
      });
      if (res.ok) {
        onNotify('Feature flags updated', 'success');
        setEditOpen(false);
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
  }, [editJson, editReason, apiFetch, onNotify, loadData]);

  const handleEvaluate = useCallback(async () => {
    if (!evalFlag.trim()) return;
    setEvaluating(true);
    try {
      const params = new URLSearchParams({ flag: evalFlag });
      if (evalTenant.trim()) params.set('tenant_id', evalTenant.trim());
      const res = await apiFetch(`/api/superadmin/feature-flags/evaluate?${params}`);
      if (res.ok) {
        setEvalResult(await res.json());
      } else {
        onNotify('Evaluation failed', 'error');
      }
    } catch {
      onNotify('Network error', 'error');
    } finally {
      setEvaluating(false);
    }
  }, [evalFlag, evalTenant, apiFetch, onNotify]);

  if (loading) return <Loader size="lg" />;

  const flags = flagData?.flags || [];

  return (
    <Stack gap="md">
      <Group justify="space-between">
        <div>
          <Title order={2}>Feature Flags</Title>
          <Text c="dimmed" size="sm">Toggle features per tier/tenant with rollout percentages (SPEC-1824)</Text>
        </div>
        <Button variant="light" onClick={handleOpenEdit}>Edit Flags</Button>
      </Group>

      <Tabs defaultValue="flags">
        <Tabs.List>
          <Tabs.Tab value="flags">Flags ({flags.length})</Tabs.Tab>
          <Tabs.Tab value="evaluate">Evaluate</Tabs.Tab>
        </Tabs.List>

        <Tabs.Panel value="flags" pt="md">
          {flags.length === 0 ? (
            <Text c="dimmed" ta="center" mt="xl">No feature flags configured.</Text>
          ) : (
            <Table striped highlightOnHover>
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Flag</Table.Th>
                  <Table.Th>Status</Table.Th>
                  <Table.Th>Description</Table.Th>
                  <Table.Th>Tiers</Table.Th>
                  <Table.Th>Rollout</Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {flags.map(f => (
                  <Table.Tr key={f.name}>
                    <Table.Td><Code>{f.name}</Code></Table.Td>
                    <Table.Td>
                      <Badge color={f.enabled ? 'green' : 'gray'} size="sm">
                        {f.enabled ? 'ON' : 'OFF'}
                      </Badge>
                    </Table.Td>
                    <Table.Td><Text size="xs" lineClamp={1}>{f.description || '—'}</Text></Table.Td>
                    <Table.Td>
                      {f.allowedTiers.length > 0
                        ? f.allowedTiers.map(t => <Badge key={t} size="xs" variant="light" mr={4}>{t}</Badge>)
                        : <Text size="xs" c="dimmed">All</Text>}
                    </Table.Td>
                    <Table.Td>{f.rolloutPercent}%</Table.Td>
                  </Table.Tr>
                ))}
              </Table.Tbody>
            </Table>
          )}
          {flagData && (
            <Text size="xs" c="dimmed" mt="sm">
              Version: v{flagData.version} | Updated: {flagData.updatedAt ? new Date(flagData.updatedAt).toLocaleString() : '—'}
            </Text>
          )}
        </Tabs.Panel>

        <Tabs.Panel value="evaluate" pt="md">
          <Stack gap="md" maw={500}>
            <TextInput
              label="Flag Name"
              placeholder="e.g. advanced_analytics"
              value={evalFlag}
              onChange={e => setEvalFlag(e.currentTarget.value)}
            />
            <TextInput
              label="Tenant ID (optional)"
              placeholder="Leave empty for global evaluation"
              value={evalTenant}
              onChange={e => setEvalTenant(e.currentTarget.value)}
            />
            <Button onClick={handleEvaluate} loading={evaluating} disabled={!evalFlag.trim()}>
              Evaluate
            </Button>
            {evalResult && (
              <Stack gap="xs">
                <Group>
                  <Text size="sm" fw={500}>Result:</Text>
                  <Badge color={evalResult.enabled ? 'green' : 'red'} size="lg">
                    {evalResult.enabled ? 'ENABLED' : 'DISABLED'}
                  </Badge>
                </Group>
                <Text size="sm" c="dimmed">Reason: {evalResult.reason}</Text>
              </Stack>
            )}
          </Stack>
        </Tabs.Panel>
      </Tabs>

      {/* Edit Modal */}
      <Modal opened={editOpen} onClose={() => setEditOpen(false)} title="Edit Feature Flags" size="xl">
        <Stack gap="md">
          <JsonInput
            label="Feature Flags (JSON array)"
            value={editJson}
            onChange={setEditJson}
            minRows={15}
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
            <Button variant="default" onClick={() => setEditOpen(false)}>Cancel</Button>
            <Button onClick={handleSave} loading={saving}>Save</Button>
          </Group>
        </Stack>
      </Modal>
    </Stack>
  );
};
