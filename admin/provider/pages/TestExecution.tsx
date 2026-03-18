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

import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  Badge,
  Button,
  Code,
  Group,
  Loader,
  Modal,
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

interface CheckResult {
  name: string;
  category: string;
  status: string;
  latencyMs: number;
  detail: string;
}

interface PipelineRun {
  runId: string;
  environment: string;
  suite: string;
  status: string;
  triggeredBy: string;
  startedAt: string;
  completedAt: string | null;
  totalTests: number;
  completed: number;
  passed: number;
  failed: number;
  skipped: number;
  durationS: number | null;
  phasesRun: string[];
  checks: CheckResult[];
}

const STATUS_COLORS: Record<string, string> = {
  queued: 'blue',
  running: 'orange',
  passed: 'green',
  failed: 'red',
  error: 'red',
};

// SPEC-1846: Cloud-native verification suites (no pytest/unit in-container)
const SUITE_OPTIONS = [
  { value: 'smoke', label: 'Smoke — Health probes (~5s)' },
  { value: 'regression', label: 'Regression — API + config (~3min)' },
  { value: 'e2e', label: 'End-to-End — Full verification (~8min)' },
  { value: 'all', label: 'Full Suite — All checks (~12min)' },
];

const CHECK_STATUS_COLORS: Record<string, string> = {
  pass: 'green',
  fail: 'red',
  skip: 'gray',
  error: 'orange',
};

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
  const [triggerSuite, setTriggerSuite] = useState<string | null>('smoke');
  const [triggerDryRun, setTriggerDryRun] = useState(false);
  const [triggering, setTriggering] = useState(false);

  // Detail modal — track by ID, derive data from runs to stay in sync with polling
  const [detailRunId, setDetailRunId] = useState<string | null>(null);
  const detailRun = detailRunId ? runs.find(r => r.runId === detailRunId) ?? null : null;

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
          suite: triggerSuite || 'smoke',
          phases: [],
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
  }, [triggerEnv, triggerSuite, triggerDryRun, apiFetch, onNotify, loadData]);

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

  // SPEC-1846: Auto-refresh running tests every 3 seconds (with unmount guard)
  const mountedRef = useRef(true);
  useEffect(() => {
    mountedRef.current = true;
    return () => { mountedRef.current = false; };
  }, []);

  useEffect(() => {
    const runningRuns = runs.filter(r => r.status === 'running' || r.status === 'queued');
    if (runningRuns.length === 0) return;
    const interval = setInterval(() => {
      if (mountedRef.current) {
        runningRuns.forEach(r => refreshRun(r.runId));
      }
    }, 3000);
    return () => clearInterval(interval);
  }, [runs, refreshRun]);

  // Copy failures as JSON for Claude diagnosis
  const copyForClaude = useCallback((run: PipelineRun) => {
    const output = {
      runId: run.runId,
      environment: run.environment,
      suite: run.suite,
      status: run.status,
      totalTests: run.totalTests,
      passed: run.passed,
      failed: run.failed,
      durationS: run.durationS,
      failures: (run.checks || []).filter(c => c.status === 'fail' || c.status === 'error'),
    };
    navigator.clipboard.writeText(JSON.stringify(output, null, 2));
    onNotify('Copied failure details to clipboard', 'success');
  }, [onNotify]);

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
                <Table.Td>{r.startedAt ? new Date(r.startedAt).toLocaleString() : '—'}</Table.Td>
                <Table.Td>
                  <Group gap="xs">
                    <Button size="xs" variant="subtle" onClick={() => setDetailRunId(r.runId)}>Details</Button>
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

      {/* Detail Modal — SPEC-1846: progress bar, checks table, copy for Claude */}
      <Modal opened={!!detailRun} onClose={() => setDetailRunId(null)} title={`Run ${detailRun?.runId}`} size="xl">
        {detailRun && (
          <Stack gap="sm">
            <Group>
              <Text size="sm" fw={500}>Environment:</Text>
              <Badge>{detailRun.environment}</Badge>
              <Text size="sm" fw={500} ml="md">Suite:</Text>
              <Text size="sm">{detailRun.suite}</Text>
              <Text size="sm" fw={500} ml="md">Status:</Text>
              <Badge color={STATUS_COLORS[detailRun.status] || 'gray'}>{detailRun.status}</Badge>
            </Group>
            <Group>
              <Text size="sm" fw={500}>Results:</Text>
              <Text size="sm">
                {detailRun.passed} passed, {detailRun.failed} failed, {detailRun.skipped} skipped
                ({detailRun.totalTests} total)
              </Text>
              <Text size="sm" fw={500} ml="md">Duration:</Text>
              <Text size="sm">{detailRun.durationS != null ? `${detailRun.durationS}s` : 'In progress'}</Text>
            </Group>

            {/* Progress bar for running tests */}
            {(detailRun.status === 'running' || detailRun.status === 'queued') && detailRun.totalTests > 0 && (
              <div>
                <Group justify="space-between" mb={4}>
                  <Text size="xs" c="dimmed">Progress</Text>
                  <Text size="xs" c="dimmed">{detailRun.completed || 0} / {detailRun.totalTests}</Text>
                </Group>
                <div style={{ background: '#e9ecef', borderRadius: 4, height: 8, overflow: 'hidden' }}>
                  <div style={{
                    background: '#228be6',
                    height: '100%',
                    width: `${Math.round(((detailRun.completed || 0) / detailRun.totalTests) * 100)}%`,
                    transition: 'width 0.3s ease',
                  }} />
                </div>
              </div>
            )}

            {/* Categories completed */}
            {detailRun.phasesRun.length > 0 && (
              <Group>
                <Text size="sm" fw={500}>Categories:</Text>
                {detailRun.phasesRun.map(p => <Badge key={p} size="sm" variant="light">{p}</Badge>)}
              </Group>
            )}

            {/* Checks table */}
            {detailRun.checks && detailRun.checks.length > 0 && (
              <>
                <Text size="sm" fw={600} mt="sm">Verification Checks</Text>
                <Table striped highlightOnHover withTableBorder>
                  <Table.Thead>
                    <Table.Tr>
                      <Table.Th>Check</Table.Th>
                      <Table.Th>Category</Table.Th>
                      <Table.Th>Status</Table.Th>
                      <Table.Th>Latency</Table.Th>
                      <Table.Th>Detail</Table.Th>
                    </Table.Tr>
                  </Table.Thead>
                  <Table.Tbody>
                    {detailRun.checks.map((c) => (
                      <Table.Tr key={`${c.category}-${c.name}`}>
                        <Table.Td><Text size="xs">{c.name}</Text></Table.Td>
                        <Table.Td><Badge size="xs" variant="light">{c.category}</Badge></Table.Td>
                        <Table.Td>
                          <Badge size="xs" color={CHECK_STATUS_COLORS[c.status] || 'gray'}>{c.status}</Badge>
                        </Table.Td>
                        <Table.Td><Text size="xs" c="dimmed">{c.latencyMs}ms</Text></Table.Td>
                        <Table.Td><Text size="xs" lineClamp={2}>{c.detail}</Text></Table.Td>
                      </Table.Tr>
                    ))}
                  </Table.Tbody>
                </Table>
              </>
            )}

            {/* Action buttons */}
            <Group justify="flex-end" mt="sm">
              {(detailRun.status === 'running' || detailRun.status === 'queued') && (
                <Button size="xs" variant="light" onClick={() => refreshRun(detailRun.runId)}>
                  Refresh
                </Button>
              )}
              {detailRun.checks && detailRun.checks.length > 0 && (
                <Button size="xs" variant="subtle" onClick={() => copyForClaude(detailRun)}>
                  Copy for Claude
                </Button>
              )}
            </Group>
          </Stack>
        )}
      </Modal>
    </Stack>
  );
};
