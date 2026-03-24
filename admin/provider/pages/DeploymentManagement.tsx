/**
 * DeploymentManagement — Self-service deployment pipeline.
 *
 * Trigger builds, deployments, and full pipelines from the SPA console.
 * All pipeline stages are visible with real-time status polling.
 *
 * Pipeline: Build (GitHub Actions) → Deploy (Azure REST) → Verify (Health) → Rollback (auto)
 *
 * API: GET  /api/superadmin/deployments
 *      POST /api/superadmin/deployments/trigger
 *      GET  /api/superadmin/deployments/{deploy_id}/status
 *
 * SPEC-1825 / S213
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  Badge,
  Button,
  Card,
  Code,
  Group,
  Loader,
  Modal,
  Select,
  SimpleGrid,
  Stack,
  Stepper,
  Table,
  Text,
  TextInput,
  Title,
} from '@mantine/core';
import { useProviderContext } from '../layouts/ProviderLayout';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface PipelineStep {
  name: string;
  status: string;
  detail: string;
  startedAt: string | null;
  completedAt: string | null;
  durationS: number | null;
}

interface DeploymentRecord {
  deployId: string;
  environment: string;
  version: string;
  action: string;
  status: string;
  triggeredBy: string;
  startedAt: string;
  completedAt: string | null;
  durationS: number | null;
  steps: PipelineStep[];
  error: string | null;
  previousImage: string | null;
}

interface DeploymentListResponse {
  deployments: DeploymentRecord[];
  total: number;
}

const STATUS_COLORS: Record<string, string> = {
  queued: 'blue',
  building: 'orange',
  deploying: 'violet',
  verifying: 'cyan',
  succeeded: 'green',
  failed: 'red',
  rolled_back: 'yellow',
};

const STEP_LABELS: Record<string, string> = {
  build_gateway: 'Build Gateway',
  build_test_host: 'Build Test Host',
  deploy_gateway: 'Deploy Gateway',
  deploy_test_host: 'Deploy Test Host',
  health_check: 'Health Check',
  rollback: 'Rollback',
};

// ---------------------------------------------------------------------------
// Version suggestion (SPEC-1841)
// ---------------------------------------------------------------------------

/**
 * Parse a semver-style version string and return the next patch version.
 * Handles formats: "v1.98.15", "1.98.15", "v1.98"
 */
function suggestNextVersion(version: string): string {
  const match = version.match(/^(v?)(\d+)\.(\d+)(?:\.(\d+))?/);
  if (!match) return '';
  const prefix = match[1]; // 'v' or ''
  const major = match[2];
  const minor = match[3];
  const patch = match[4] !== undefined ? parseInt(match[4], 10) + 1 : 0;
  return `${prefix}${major}.${minor}.${patch}`;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const DeploymentManagementPage: React.FC = () => {
  const { apiFetch, onNotify } = useProviderContext();
  const [deployments, setDeployments] = useState<DeploymentRecord[]>([]);
  const [loading, setLoading] = useState(true);

  // Trigger modal — environment auto-detected server-side (SPEC-0058 isolation)
  const [triggerOpen, setTriggerOpen] = useState(false);
  const [triggerVersion, setTriggerVersion] = useState('');
  const [triggerAction, setTriggerAction] = useState<string | null>('full');
  const [triggering, setTriggering] = useState(false);

  // SPEC-1841: Last deployed version + suggested next version
  const lastSucceeded = useMemo(() => {
    return deployments
      .filter(d => d.status === 'succeeded')
      .sort((a, b) => (b.startedAt || '').localeCompare(a.startedAt || ''))[0] ?? null;
  }, [deployments]);

  const lastVersion = lastSucceeded?.version ?? null;
  const suggestedVersion = lastVersion ? suggestNextVersion(lastVersion) : '';

  // Detail modal
  const [detailDeploy, setDetailDeploy] = useState<DeploymentRecord | null>(null);

  // Auto-polling ref
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const loadData = useCallback(async () => {
    try {
      const res = await apiFetch('/api/superadmin/deployments');
      if (res.ok) {
        const data: DeploymentListResponse = await res.json();
        setDeployments(data.deployments || []);
      }
    } catch {
      // Silent on poll failure
    } finally {
      setLoading(false);
    }
  }, [apiFetch]);

  useEffect(() => {
    loadData();
    // Auto-poll every 5s when there are active pipelines
    pollRef.current = setInterval(() => {
      loadData();
    }, 5000);
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [loadData]);

  // Stop polling when all pipelines are terminal
  useEffect(() => {
    const hasActive = deployments.some(d =>
      ['queued', 'building', 'deploying', 'verifying'].includes(d.status)
    );
    if (!hasActive && pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    } else if (hasActive && !pollRef.current) {
      pollRef.current = setInterval(loadData, 5000);
    }
  }, [deployments, loadData]);

  const handleTrigger = useCallback(async () => {
    if (!triggerVersion) return;
    setTriggering(true);
    try {
      const res = await apiFetch('/api/superadmin/deployments/trigger', {
        method: 'POST',
        body: JSON.stringify({
          version: triggerVersion,
          action: triggerAction || 'full',
        }),
      });
      if (res.ok) {
        const data = await res.json();
        onNotify(`Pipeline ${data.deployId || ''} started`, 'success');
        setTriggerOpen(false);

        // SPEC-1842: Immediately insert optimistic record so the user
        // sees feedback before the first polling cycle returns data.
        const optimistic: DeploymentRecord = {
          deployId: data.deployId || `deploy-pending`,
          environment: 'auto-detected',
          version: triggerVersion,
          action: triggerAction || 'full',
          status: 'queued',
          triggeredBy: 'spa-console',
          startedAt: new Date().toISOString(),
          completedAt: null,
          durationS: null,
          steps: [],
          error: null,
          previousImage: null,
        };
        setDeployments(prev => [optimistic, ...prev]);

        // Re-enable polling — next poll replaces the optimistic record
        // with real server data
        if (!pollRef.current) {
          pollRef.current = setInterval(loadData, 5000);
        }
      } else {
        const err = await res.json();
        onNotify(err.detail || 'Trigger failed', 'error');
      }
    } catch {
      onNotify('Network error', 'error');
    } finally {
      setTriggering(false);
    }
  }, [triggerVersion, triggerAction, apiFetch, onNotify, loadData]);

  if (loading) return <Loader size="lg" />;

  return (
    <Stack gap="md">
      <Group justify="space-between">
        <div>
          <Title order={2}>Deployment Management</Title>
          <Text c="dimmed" size="sm">
            Self-service build, deploy, and verify pipeline (SPEC-1825)
          </Text>
        </div>
        <Group>
          <Button variant="light" onClick={loadData}>Refresh</Button>
          <Button onClick={() => {
            setTriggerOpen(true);
            setTriggerVersion(suggestedVersion);
            setTriggerAction('full');
          }}>
            Trigger Pipeline
          </Button>
        </Group>
      </Group>

      {/* Active Pipelines */}
      {deployments.filter(d => ['queued', 'building', 'deploying', 'verifying'].includes(d.status)).length > 0 && (
        <>
          <Title order={4}>Active Pipelines</Title>
          <SimpleGrid cols={{ base: 1, md: 2 }} spacing="md">
            {deployments
              .filter(d => ['queued', 'building', 'deploying', 'verifying'].includes(d.status))
              .map(d => (
                <PipelineCard key={d.deployId} deployment={d} onClick={() => setDetailDeploy(d)} />
              ))}
          </SimpleGrid>
        </>
      )}

      {/* Deployment History */}
      <Title order={4}>Deployment History</Title>
      {deployments.filter(d => !['queued', 'building', 'deploying', 'verifying'].includes(d.status)).length === 0 ? (
        <Text c="dimmed" ta="center" mt="md">No completed deployments yet.</Text>
      ) : (
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Deploy ID</Table.Th>
              <Table.Th>Environment</Table.Th>
              <Table.Th>Version</Table.Th>
              <Table.Th>Action</Table.Th>
              <Table.Th>Status</Table.Th>
              <Table.Th>Started</Table.Th>
              <Table.Th>Duration</Table.Th>
              <Table.Th>Actions</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {deployments
              .filter(d => !['queued', 'building', 'deploying', 'verifying'].includes(d.status))
              .map(d => (
                <Table.Tr key={d.deployId}>
                  <Table.Td><Code>{d.deployId.slice(0, 16)}</Code></Table.Td>
                  <Table.Td>
                    <Badge size="sm" color={d.environment === 'production' ? 'red' : 'blue'}>
                      {d.environment}
                    </Badge>
                  </Table.Td>
                  <Table.Td><Code>{d.version}</Code></Table.Td>
                  <Table.Td><Badge variant="light" size="sm">{d.action}</Badge></Table.Td>
                  <Table.Td>
                    <Badge color={STATUS_COLORS[d.status] || 'gray'} size="sm">
                      {d.status}
                    </Badge>
                  </Table.Td>
                  <Table.Td>{new Date(d.startedAt).toLocaleString()}</Table.Td>
                  <Table.Td>{d.durationS != null ? `${d.durationS}s` : '—'}</Table.Td>
                  <Table.Td>
                    <Button size="xs" variant="light" onClick={() => setDetailDeploy(d)}>
                      Details
                    </Button>
                  </Table.Td>
                </Table.Tr>
              ))}
          </Table.Tbody>
        </Table>
      )}

      {/* Trigger Modal — environment auto-detected from CONTAINER_APP_FQDN (SPEC-0058) */}
      <Modal opened={triggerOpen} onClose={() => setTriggerOpen(false)} title="Trigger Deployment Pipeline" size="md">
        <Stack gap="md">
          <Text size="sm" c="dimmed">
            Environment is auto-detected. This pipeline will build, deploy, and verify
            the version you specify for <strong>this</strong> environment only.
          </Text>
          <Select
            label="Action"
            data={[
              { value: 'full', label: 'Full Pipeline (Build → Deploy → Verify)' },
              { value: 'build', label: 'Build Only (GitHub Actions)' },
              { value: 'deploy', label: 'Deploy Only (use existing image)' },
            ]}
            value={triggerAction}
            onChange={setTriggerAction}
          />
          <TextInput
            label="Version"
            placeholder={suggestedVersion || 'e.g. v1.98.15'}
            description={lastVersion
              ? `Last successful deployment: ${lastVersion}`
              : 'No previous deployments found'}
            value={triggerVersion}
            onChange={e => setTriggerVersion(e.currentTarget.value)}
            required
          />
          <Group justify="flex-end">
            <Button variant="default" onClick={() => setTriggerOpen(false)}>Cancel</Button>
            <Button
              onClick={handleTrigger}
              loading={triggering}
              disabled={!triggerVersion}
            >
              Start Pipeline
            </Button>
          </Group>
        </Stack>
      </Modal>

      {/* Detail Modal */}
      <Modal
        opened={!!detailDeploy}
        onClose={() => setDetailDeploy(null)}
        title={`Pipeline: ${detailDeploy?.deployId?.slice(0, 16) || ''}`}
        size="lg"
      >
        {detailDeploy && <PipelineDetail deployment={detailDeploy} />}
      </Modal>
    </Stack>
  );
};

// ---------------------------------------------------------------------------
// Pipeline Card (active pipelines)
// ---------------------------------------------------------------------------

function PipelineCard({ deployment, onClick }: { deployment: DeploymentRecord; onClick: () => void }) {
  const activeStep = deployment.steps.find(s => s.status === 'running');
  const completedSteps = deployment.steps.filter(s => s.status === 'succeeded').length;
  const totalSteps = deployment.steps.filter(s => s.status !== 'skipped').length;

  return (
    <Card withBorder padding="md" radius="md" style={{ cursor: 'pointer' }} onClick={onClick}>
      <Group justify="space-between" mb="xs">
        <Group gap="xs">
          <Badge color={STATUS_COLORS[deployment.status] || 'gray'} size="sm">
            {deployment.status}
          </Badge>
          <Badge variant="light" color={deployment.environment === 'production' ? 'red' : 'blue'} size="sm">
            {deployment.environment}
          </Badge>
        </Group>
        <Code>{deployment.version}</Code>
      </Group>
      <Text size="sm" c="dimmed">
        {activeStep
          ? `${STEP_LABELS[activeStep.name] || activeStep.name}: ${activeStep.detail || 'Running...'}`
          : `${completedSteps}/${totalSteps} steps completed`
        }
      </Text>
      <Text size="xs" c="dimmed" mt={4}>
        Started {new Date(deployment.startedAt).toLocaleString()}
      </Text>
    </Card>
  );
}

// ---------------------------------------------------------------------------
// Pipeline Detail (modal content)
// ---------------------------------------------------------------------------

function PipelineDetail({ deployment }: { deployment: DeploymentRecord }) {
  const steps = deployment.steps.filter(s => s.status !== 'skipped');
  const activeIdx = steps.findIndex(s => s.status === 'running');
  const completedIdx = steps.reduce((acc, s, i) => s.status === 'succeeded' ? i : acc, -1);

  return (
    <Stack gap="md">
      <Group justify="space-between">
        <Group gap="xs">
          <Badge color={STATUS_COLORS[deployment.status] || 'gray'}>{deployment.status}</Badge>
          <Badge variant="light">{deployment.action}</Badge>
          <Badge variant="light" color={deployment.environment === 'production' ? 'red' : 'blue'}>
            {deployment.environment}
          </Badge>
        </Group>
        <Text size="sm" c="dimmed">
          {deployment.durationS != null ? `${deployment.durationS}s` : 'In progress...'}
        </Text>
      </Group>

      <Stepper
        active={activeIdx >= 0 ? activeIdx : completedIdx + 1}
        size="sm"
        orientation="vertical"
      >
        {steps.map((step) => (
          <Stepper.Step
            key={step.name}
            label={STEP_LABELS[step.name] || step.name}
            description={step.detail || (step.status === 'pending' ? 'Waiting...' : '')}
            loading={step.status === 'running'}
            color={
              step.status === 'succeeded' ? 'green'
                : step.status === 'failed' ? 'red'
                : step.status === 'running' ? 'blue'
                : 'gray'
            }
            completedIcon={step.status === 'failed' ? '✗' : undefined}
          />
        ))}
      </Stepper>

      {deployment.error && (
        <Card withBorder padding="sm" radius="md" bg="var(--mantine-color-red-light)">
          <Text size="sm" c="red" fw={500}>Error: {deployment.error}</Text>
        </Card>
      )}

      {deployment.previousImage && (
        <Text size="xs" c="dimmed">Previous image: <Code>{deployment.previousImage}</Code></Text>
      )}
    </Stack>
  );
}
