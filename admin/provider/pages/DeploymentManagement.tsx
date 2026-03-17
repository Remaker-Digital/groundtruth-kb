/**
 * DeploymentManagement — Deployment orchestration and status.
 *
 * View recent deployments, trigger new deployments, and monitor
 * deployment status. Integrates with the deployment orchestrator
 * backend for ACR image builds and container app revisions.
 *
 * API: GET  /api/superadmin/deployments
 *      POST /api/superadmin/deployments/trigger
 *      GET  /api/superadmin/deployments/{deploy_id}/status
 *
 * WI-1430 / SPEC-1825
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
  Select,
  Stack,
  Table,
  Text,
  TextInput,
  Title,
} from '@mantine/core';
import { useProviderContext } from '../layouts/ProviderLayout';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface DeploymentRecord {
  deployId: string;
  environment: string;
  version: string;
  status: string;
  triggeredBy: string;
  startedAt: string;
  completedAt: string | null;
  durationS: number | null;
  imageTag: string;
  revisionName: string | null;
}

interface DeploymentListResponse {
  deployments: DeploymentRecord[];
  total: number;
}

const STATUS_COLORS: Record<string, string> = {
  queued: 'blue',
  running: 'orange',
  succeeded: 'green',
  failed: 'red',
  cancelled: 'gray',
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const DeploymentManagementPage: React.FC = () => {
  const { apiFetch, onNotify } = useProviderContext();
  const [deployments, setDeployments] = useState<DeploymentRecord[]>([]);
  const [loading, setLoading] = useState(true);

  // Trigger modal
  const [triggerOpen, setTriggerOpen] = useState(false);
  const [triggerEnv, setTriggerEnv] = useState<string | null>('staging');
  const [triggerVersion, setTriggerVersion] = useState('');
  const [triggering, setTriggering] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiFetch('/api/superadmin/deployments');
      if (res.ok) {
        const data: DeploymentListResponse = await res.json();
        setDeployments(data.deployments || []);
      }
    } catch {
      onNotify('Failed to load deployments', 'error');
    } finally {
      setLoading(false);
    }
  }, [apiFetch, onNotify]);

  useEffect(() => { loadData(); }, [loadData]);

  const handleTrigger = useCallback(async () => {
    if (!triggerEnv) return;
    setTriggering(true);
    try {
      const res = await apiFetch('/api/superadmin/deployments/trigger', {
        method: 'POST',
        body: JSON.stringify({
          environment: triggerEnv,
          version: triggerVersion || undefined,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        onNotify(`Deployment ${data.deployId || ''} triggered for ${triggerEnv}`, 'success');
        setTriggerOpen(false);
        loadData();
      } else {
        const err = await res.json();
        onNotify(err.detail || 'Trigger failed', 'error');
      }
    } catch {
      onNotify('Network error', 'error');
    } finally {
      setTriggering(false);
    }
  }, [triggerEnv, triggerVersion, apiFetch, onNotify, loadData]);

  const refreshStatus = useCallback(async (deployId: string) => {
    try {
      const res = await apiFetch(`/api/superadmin/deployments/${deployId}/status`);
      if (res.ok) {
        loadData();
      }
    } catch {
      onNotify('Failed to refresh status', 'error');
    }
  }, [apiFetch, onNotify, loadData]);

  if (loading) return <Loader size="lg" />;

  return (
    <Stack gap="md">
      <Group justify="space-between">
        <div>
          <Title order={2}>Deployment Management</Title>
          <Text c="dimmed" size="sm">Trigger and monitor deployment orchestration (SPEC-1825)</Text>
        </div>
        <Group>
          <Button variant="light" onClick={loadData}>Refresh</Button>
          <Button onClick={() => { setTriggerOpen(true); setTriggerVersion(''); }}>
            Trigger Deployment
          </Button>
        </Group>
      </Group>

      {deployments.length === 0 ? (
        <Text c="dimmed" ta="center" mt="xl">No deployment records found.</Text>
      ) : (
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Deploy ID</Table.Th>
              <Table.Th>Environment</Table.Th>
              <Table.Th>Version</Table.Th>
              <Table.Th>Status</Table.Th>
              <Table.Th>Image</Table.Th>
              <Table.Th>Started</Table.Th>
              <Table.Th>Duration</Table.Th>
              <Table.Th>Actions</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {deployments.map(d => (
              <Table.Tr key={d.deployId}>
                <Table.Td><Code>{d.deployId.slice(0, 12)}</Code></Table.Td>
                <Table.Td><Badge size="sm">{d.environment}</Badge></Table.Td>
                <Table.Td>{d.version}</Table.Td>
                <Table.Td>
                  <Badge color={STATUS_COLORS[d.status] || 'gray'} size="sm">
                    {d.status}
                  </Badge>
                </Table.Td>
                <Table.Td><Code>{d.imageTag}</Code></Table.Td>
                <Table.Td>{new Date(d.startedAt).toLocaleString()}</Table.Td>
                <Table.Td>{d.durationS != null ? `${d.durationS}s` : '—'}</Table.Td>
                <Table.Td>
                  {(d.status === 'queued' || d.status === 'running') && (
                    <Button size="xs" variant="light" onClick={() => refreshStatus(d.deployId)}>
                      Refresh
                    </Button>
                  )}
                </Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      )}

      {/* Trigger Modal */}
      <Modal opened={triggerOpen} onClose={() => setTriggerOpen(false)} title="Trigger Deployment" size="md">
        <Stack gap="md">
          <Select
            label="Environment"
            data={[
              { value: 'staging', label: 'Staging' },
              { value: 'production', label: 'Production' },
            ]}
            value={triggerEnv}
            onChange={setTriggerEnv}
          />
          <TextInput
            label="Version (optional)"
            placeholder="Leave blank for latest"
            value={triggerVersion}
            onChange={e => setTriggerVersion(e.currentTarget.value)}
          />
          {triggerEnv === 'production' && (
            <Text size="sm" c="red" fw={500}>
              Warning: This will deploy to production. Ensure staging has been verified first.
            </Text>
          )}
          <Group justify="flex-end">
            <Button variant="default" onClick={() => setTriggerOpen(false)}>Cancel</Button>
            <Button
              onClick={handleTrigger}
              loading={triggering}
              color={triggerEnv === 'production' ? 'red' : undefined}
            >
              Deploy to {triggerEnv}
            </Button>
          </Group>
        </Stack>
      </Modal>
    </Stack>
  );
};
