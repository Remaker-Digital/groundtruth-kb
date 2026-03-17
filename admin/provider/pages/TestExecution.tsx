/**
 * TestExecution — Test pipeline trigger and result monitoring.
 *
 * Trigger test runs across environments/suites, view run history,
 * and inspect individual run results with pass/fail counts.
 *
 * API: POST /api/superadmin/tests/run
 *      GET  /api/superadmin/tests/{run_id}/status
 *      GET  /api/superadmin/tests/runs
 *
 * WI-1431 / SPEC-1826
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
  MultiSelect,
  Select,
  Stack,
  Switch,
  Table,
  Text,
  Title,
} from '@mantine/core';
import { useProviderContext } from '../layouts/ProviderLayout';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface PipelineRun {
  runId: string;
  environment: string;
  suite: string;
  status: string;
  triggeredBy: string;
  startedAt: string;
  completedAt: string | null;
  totalTests: number;
  passed: number;
  failed: number;
  skipped: number;
  durationS: number | null;
  phasesRun: string[];
}

const STATUS_COLORS: Record<string, string> = {
  queued: 'blue',
  running: 'orange',
  passed: 'green',
  failed: 'red',
  error: 'red',
};

const SUITE_OPTIONS = [
  { value: 'all', label: 'All Tests' },
  { value: 'regression', label: 'Regression' },
  { value: 'smoke', label: 'Smoke' },
  { value: 'e2e', label: 'End-to-End' },
  { value: 'unit', label: 'Unit' },
];

const PHASE_OPTIONS = [
  { value: 'phase_a', label: 'Phase A' },
  { value: 'phase_b', label: 'Phase B' },
  { value: 'phase_c', label: 'Phase C' },
];

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const TestExecutionPage: React.FC = () => {
  const { apiFetch, onNotify } = useProviderContext();
  const [runs, setRuns] = useState<PipelineRun[]>([]);
  const [loading, setLoading] = useState(true);

  // Trigger modal
  const [triggerOpen, setTriggerOpen] = useState(false);
  const [triggerEnv, setTriggerEnv] = useState<string | null>('staging');
  const [triggerSuite, setTriggerSuite] = useState<string | null>('all');
  const [triggerPhases, setTriggerPhases] = useState<string[]>([]);
  const [triggerDryRun, setTriggerDryRun] = useState(false);
  const [triggering, setTriggering] = useState(false);

  // Detail modal
  const [detailRun, setDetailRun] = useState<PipelineRun | null>(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiFetch('/api/superadmin/tests/runs');
      if (res.ok) {
        const data = await res.json();
        setRuns(data.runs || []);
      }
    } catch {
      onNotify('Failed to load test runs', 'error');
    } finally {
      setLoading(false);
    }
  }, [apiFetch, onNotify]);

  useEffect(() => { loadData(); }, [loadData]);

  const handleTrigger = useCallback(async () => {
    if (!triggerEnv) return;
    setTriggering(true);
    try {
      const res = await apiFetch('/api/superadmin/tests/run', {
        method: 'POST',
        body: JSON.stringify({
          environment: triggerEnv,
          suite: triggerSuite || 'all',
          phases: triggerPhases.length > 0 ? triggerPhases : [],
          dryRun: triggerDryRun,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        onNotify(`Test run ${data.runId || ''} queued`, 'success');
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
  }, [triggerEnv, triggerSuite, triggerPhases, triggerDryRun, apiFetch, onNotify, loadData]);

  const refreshRun = useCallback(async (runId: string) => {
    try {
      const res = await apiFetch(`/api/superadmin/tests/${runId}/status`);
      if (res.ok) {
        const data: PipelineRun = await res.json();
        setRuns(prev => prev.map(r => r.runId === runId ? data : r));
      }
    } catch {
      onNotify('Failed to refresh', 'error');
    }
  }, [apiFetch, onNotify]);

  if (loading) return <Loader size="lg" />;

  return (
    <Stack gap="md">
      <Group justify="space-between">
        <div>
          <Title order={2}>Test Execution</Title>
          <Text c="dimmed" size="sm">Trigger and monitor test pipeline runs (SPEC-1826)</Text>
        </div>
        <Group>
          <Button variant="light" onClick={loadData}>Refresh</Button>
          <Button onClick={() => setTriggerOpen(true)}>Trigger Test Run</Button>
        </Group>
      </Group>

      {runs.length === 0 ? (
        <Text c="dimmed" ta="center" mt="xl">No test runs recorded.</Text>
      ) : (
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Run ID</Table.Th>
              <Table.Th>Environment</Table.Th>
              <Table.Th>Suite</Table.Th>
              <Table.Th>Status</Table.Th>
              <Table.Th>Results</Table.Th>
              <Table.Th>Duration</Table.Th>
              <Table.Th>Started</Table.Th>
              <Table.Th>Actions</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {runs.map(r => (
              <Table.Tr key={r.runId}>
                <Table.Td><Code>{r.runId.slice(0, 12)}</Code></Table.Td>
                <Table.Td><Badge size="sm">{r.environment}</Badge></Table.Td>
                <Table.Td>{r.suite}</Table.Td>
                <Table.Td>
                  <Badge color={STATUS_COLORS[r.status] || 'gray'} size="sm">
                    {r.status}
                  </Badge>
                </Table.Td>
                <Table.Td>
                  {r.totalTests > 0 ? (
                    <Group gap={4}>
                      <Text size="xs" c="green">{r.passed}P</Text>
                      {r.failed > 0 && <Text size="xs" c="red">{r.failed}F</Text>}
                      {r.skipped > 0 && <Text size="xs" c="dimmed">{r.skipped}S</Text>}
                      <Text size="xs" c="dimmed">/ {r.totalTests}</Text>
                    </Group>
                  ) : '—'}
                </Table.Td>
                <Table.Td>{r.durationS != null ? `${r.durationS}s` : '—'}</Table.Td>
                <Table.Td>{new Date(r.startedAt).toLocaleString()}</Table.Td>
                <Table.Td>
                  <Group gap="xs">
                    <Button size="xs" variant="subtle" onClick={() => setDetailRun(r)}>Details</Button>
                    {(r.status === 'queued' || r.status === 'running') && (
                      <Button size="xs" variant="light" onClick={() => refreshRun(r.runId)}>Refresh</Button>
                    )}
                  </Group>
                </Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      )}

      {/* Trigger Modal */}
      <Modal opened={triggerOpen} onClose={() => setTriggerOpen(false)} title="Trigger Test Run" size="md">
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
          <Select
            label="Test Suite"
            data={SUITE_OPTIONS}
            value={triggerSuite}
            onChange={setTriggerSuite}
          />
          <MultiSelect
            label="Phases (optional)"
            data={PHASE_OPTIONS}
            value={triggerPhases}
            onChange={setTriggerPhases}
            placeholder="All phases"
          />
          <Switch
            label="Dry Run (validate without executing)"
            checked={triggerDryRun}
            onChange={e => setTriggerDryRun(e.currentTarget.checked)}
          />
          <Group justify="flex-end">
            <Button variant="default" onClick={() => setTriggerOpen(false)}>Cancel</Button>
            <Button onClick={handleTrigger} loading={triggering}>
              {triggerDryRun ? 'Dry Run' : 'Run Tests'}
            </Button>
          </Group>
        </Stack>
      </Modal>

      {/* Detail Modal */}
      <Modal opened={!!detailRun} onClose={() => setDetailRun(null)} title={`Run ${detailRun?.runId}`} size="lg">
        {detailRun && (
          <Stack gap="sm">
            <Group>
              <Text size="sm" fw={500}>Environment:</Text>
              <Badge>{detailRun.environment}</Badge>
            </Group>
            <Group>
              <Text size="sm" fw={500}>Suite:</Text>
              <Text size="sm">{detailRun.suite}</Text>
            </Group>
            <Group>
              <Text size="sm" fw={500}>Status:</Text>
              <Badge color={STATUS_COLORS[detailRun.status] || 'gray'}>{detailRun.status}</Badge>
            </Group>
            <Group>
              <Text size="sm" fw={500}>Results:</Text>
              <Text size="sm">
                {detailRun.passed} passed, {detailRun.failed} failed, {detailRun.skipped} skipped
                ({detailRun.totalTests} total)
              </Text>
            </Group>
            <Group>
              <Text size="sm" fw={500}>Duration:</Text>
              <Text size="sm">{detailRun.durationS != null ? `${detailRun.durationS}s` : 'In progress'}</Text>
            </Group>
            <Group>
              <Text size="sm" fw={500}>Triggered by:</Text>
              <Text size="sm">{detailRun.triggeredBy}</Text>
            </Group>
            {detailRun.phasesRun.length > 0 && (
              <Group>
                <Text size="sm" fw={500}>Phases:</Text>
                {detailRun.phasesRun.map(p => <Badge key={p} size="sm" variant="light">{p}</Badge>)}
              </Group>
            )}
          </Stack>
        )}
      </Modal>
    </Stack>
  );
};
