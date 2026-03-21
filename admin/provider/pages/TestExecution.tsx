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
  Checkbox,
  Code,
  Group,
  Loader,
  Modal,
  Select,
  Stack,
  Switch,
  Table,
  Tabs,
  Text,
  Title,
} from '@mantine/core';
import { useProviderContext } from '../layouts/ProviderLayout';
import { PerformanceChart } from './PerformanceChart';

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
  errored: number;
  durationS: number | null;
  phasesRun: string[];
  phasesCompleted: string[];
  currentPhase: string;
  phasesTotal: number;
  checks: CheckResult[];
  stdoutTail: string;
}

const STATUS_COLORS: Record<string, string> = {
  queued: 'blue',
  running: 'orange',
  passed: 'green',
  failed: 'red',
  error: 'red',
};

// ---------------------------------------------------------------------------
// Suite definitions with dependency graph for checkbox selection
// ---------------------------------------------------------------------------

interface SuiteDefinition {
  value: string;
  label: string;
  estimate: string;
  group: string;
  /** Other suites this one includes (for composite suites) */
  includes?: string[];
}

const SUITE_DEFS: SuiteDefinition[] = [
  // Quick Verification (in-process)
  { value: 'smoke', label: 'Smoke — Health probes', estimate: '8 checks, ~5s', group: 'Quick Verification' },
  { value: 'regression', label: 'Regression — API endpoints', estimate: '25 checks, ~3min', group: 'Quick Verification' },
  { value: 'e2e', label: 'Verification — Full checks', estimate: '35 checks, ~8min', group: 'Quick Verification' },
  { value: 'all', label: 'All Checks — Complete verification', estimate: '40 checks, ~12min', group: 'Quick Verification' },

  // Comprehensive (test host container)
  { value: 'unit', label: 'Unit Tests', estimate: '~950 tests, ~2min', group: 'Comprehensive' },
  { value: 'core', label: 'Core / Multi-Tenant', estimate: '~3,700 tests, ~5min', group: 'Comprehensive' },
  { value: 'integration', label: 'Integration Tests', estimate: '~270 tests, ~3min', group: 'Comprehensive' },
  { value: 'agents', label: 'Agent & Chat Tests', estimate: '~300 tests, ~3min', group: 'Comprehensive' },
  { value: 'security', label: 'Security & Penetration', estimate: '~150 tests, ~3min', group: 'Comprehensive' },
  { value: 'ops', label: 'Operations & Resilience', estimate: '~80 tests, ~4min', group: 'Comprehensive' },
  { value: 'widget', label: 'Widget Tests', estimate: '~60 tests, ~2min', group: 'Comprehensive' },
  { value: 'e2e_live', label: 'E2E Live — Playwright', estimate: '~1,100 tests, ~15min', group: 'Comprehensive' },
  { value: 'load', label: 'Load Testing — Locust', estimate: '~5min', group: 'Comprehensive' },
  { value: 'fuzzing', label: 'API Fuzzing — Schemathesis', estimate: '307 ops, ~5min', group: 'Comprehensive' },
  { value: 'property', label: 'Property Tests — Hypothesis', estimate: '46 tests, ~2min', group: 'Comprehensive' },

  // Full Suite (composite — selecting auto-selects all dependencies)
  {
    value: 'full', label: 'Complete Suite', estimate: 'Everything, ~45min', group: 'Full Suite',
    includes: ['unit', 'core', 'integration', 'agents', 'security', 'regression', 'ops', 'widget', 'e2e_live', 'load', 'fuzzing', 'property'],
  },
];

const SUITE_GROUPS = ['Quick Verification', 'Comprehensive', 'Full Suite'];

/** When a suite with `includes` is toggled on, auto-select all its dependencies. */
function applySuiteDependencies(selected: string[], toggled: string, wasChecked: boolean): string[] {
  const def = SUITE_DEFS.find(s => s.value === toggled);
  if (wasChecked) {
    // Unchecking: remove only the toggled suite (keep individual selections)
    return selected.filter(s => s !== toggled);
  }
  // Checking: add the suite + all its includes
  const toAdd = new Set([...selected, toggled]);
  if (def?.includes) {
    def.includes.forEach(s => toAdd.add(s));
  }
  return [...toAdd];
}

// Keep the old grouped format for backward compat with Select (used in some filter UIs)
const SUITE_OPTIONS = SUITE_GROUPS.map(group => ({
  group,
  items: SUITE_DEFS.filter(s => s.group === group).map(s => ({
    value: s.value,
    label: `${s.label} (${s.estimate})`,
  })),
}));

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
  const [triggerSuites, setTriggerSuites] = useState<string[]>(['smoke']);
  const [triggering, setTriggering] = useState(false);

  // Dynamic suite availability — fetched from backend
  const [availableSuites, setAvailableSuites] = useState<Set<string> | null>(null);

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

  // Fetch available suites when environment changes
  useEffect(() => {
    if (!triggerEnv) return;
    (async () => {
      try {
        const res = await apiFetch(`/api/superadmin/tests/available-suites?environment=${triggerEnv}`);
        if (res.ok) {
          const data = await res.json();
          const names = new Set<string>();
          // In-process suites
          (data.inprocess || []).forEach((s: any) => {
            if (s.runnable !== false) names.add(s.name);
          });
          // Test host suites
          (data.testhost || []).forEach((s: any) => {
            if (s.runnable !== false) names.add(s.name);
          });
          setAvailableSuites(names);
          // Deselect any suites that are no longer available
          setTriggerSuites(prev => prev.filter(s => names.has(s)));
        }
      } catch {
        // Fallback: show all suites (graceful degradation)
        setAvailableSuites(null);
      }
    })();
  }, [triggerEnv, apiFetch]);

  const handleTrigger = useCallback(async () => {
    if (!triggerEnv || triggerSuites.length === 0) return;
    setTriggering(true);

    // Determine the suite to send: if a composite is selected, use it;
    // otherwise use the first selected (backend runs one suite at a time)
    const composites = triggerSuites.filter(s =>
      SUITE_DEFS.find(d => d.value === s)?.includes,
    );
    const suite = composites.length > 0
      ? composites[composites.length - 1]  // Use largest composite
      : triggerSuites[0];

    try {
      const res = await apiFetch('/api/superadmin/tests/run', {
        method: 'POST',
        body: JSON.stringify({
          environment: triggerEnv,
          suite,
          phases: [],
          dryRun: false,
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
  }, [triggerEnv, triggerSuites, apiFetch, onNotify, loadData]);

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

  // Fetch full run data (with checks) when detail modal opens
  useEffect(() => {
    if (detailRunId) {
      refreshRun(detailRunId);
    }
  }, [detailRunId, refreshRun]);

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

      <Tabs defaultValue="runs">
        <Tabs.List>
          <Tabs.Tab value="runs">Runs</Tabs.Tab>
          <Tabs.Tab value="performance">Performance Trends</Tabs.Tab>
        </Tabs.List>

        <Tabs.Panel value="runs" pt="md">

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
          <div>
            <Text fw={500} size="sm" mb="xs">Test Suites</Text>
            <div style={{ maxHeight: 320, overflowY: 'auto' }}>
              {SUITE_GROUPS.map(group => (
                <div key={group} style={{ marginBottom: 12 }}>
                  <Text size="xs" fw={600} c="dimmed" mb={4}>{group}</Text>
                  <Stack gap={4} pl="xs">
                    {SUITE_DEFS.filter(s => s.group === group && (availableSuites === null || availableSuites.has(s.value))).map(suite => (
                      <Checkbox
                        key={suite.value}
                        label={
                          <Group gap={6}>
                            <Text size="sm">{suite.label}</Text>
                            <Text size="xs" c="dimmed">({suite.estimate})</Text>
                          </Group>
                        }
                        checked={triggerSuites.includes(suite.value)}
                        onChange={() => {
                          const wasChecked = triggerSuites.includes(suite.value);
                          setTriggerSuites(applySuiteDependencies(triggerSuites, suite.value, wasChecked));
                        }}
                      />
                    ))}
                  </Stack>
                </div>
              ))}
            </div>
            {triggerSuites.length > 0 && (
              <Text size="xs" c="dimmed" mt="xs">
                {triggerSuites.length} suite{triggerSuites.length !== 1 ? 's' : ''} selected
              </Text>
            )}
          </div>
          <Group justify="flex-end">
            <Button variant="default" onClick={() => setTriggerOpen(false)}>Cancel</Button>
            <Button onClick={handleTrigger} loading={triggering}>
              Run Tests
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
                {detailRun.passed} passed, {detailRun.failed} failed
                {detailRun.errored > 0 && `, ${detailRun.errored} errors`}
                {detailRun.skipped > 0 && `, ${detailRun.skipped} skipped`}
                {' '}({detailRun.totalTests} total)
              </Text>
              <Text size="sm" fw={500} ml="md">Duration:</Text>
              <Text size="sm">{detailRun.durationS != null ? `${detailRun.durationS}s` : 'In progress'}</Text>
            </Group>

            {/* Progress bar for running tests */}
            {(detailRun.status === 'running' || detailRun.status === 'queued') && detailRun.totalTests > 0 && (
              <div>
                <Group justify="space-between" mb={4}>
                  <Text size="xs" c="dimmed">
                    {detailRun.currentPhase
                      ? `Running: ${detailRun.currentPhase} (${(detailRun.phasesCompleted?.length || 0) + 1}/${detailRun.phasesTotal || '?'} phases)`
                      : 'Progress'
                    }
                  </Text>
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

            {/* Categories / phases completed */}
            {(detailRun.phasesCompleted?.length > 0 || detailRun.phasesRun?.length > 0) && (
              <Group>
                <Text size="sm" fw={500}>Phases:</Text>
                {(detailRun.phasesCompleted || detailRun.phasesRun || []).map(p =>
                  <Badge key={p} size="sm" variant="light">{p}</Badge>
                )}
              </Group>
            )}

            {/* Checks table — show failures first, then all */}
            {detailRun.checks && detailRun.checks.length > 0 && (() => {
              const failures = detailRun.checks.filter(c => c.status === 'fail' || c.status === 'error');
              const passes = detailRun.checks.filter(c => c.status === 'pass');
              const skips = detailRun.checks.filter(c => c.status === 'skip');
              // For large test runs (>100 checks), show failures + summary
              const isLarge = detailRun.checks.length > 100;
              const displayChecks = isLarge ? failures : detailRun.checks;
              return (
                <>
                  <Text size="sm" fw={600} mt="sm">
                    {isLarge
                      ? `Failures (${failures.length} of ${detailRun.checks.length} tests)`
                      : `Verification Checks (${detailRun.checks.length})`
                    }
                  </Text>
                  {isLarge && failures.length === 0 && (
                    <Text size="sm" c="green" mt="xs">All {detailRun.checks.length} tests passed.</Text>
                  )}
                  {displayChecks.length > 0 && (
                    <div style={{ maxHeight: 400, overflowY: 'auto' }}>
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
                          {displayChecks.map((c, i) => (
                            <Table.Tr
                              key={`${c.category}-${c.name}-${i}`}
                              style={{ cursor: 'pointer' }}
                              onClick={() => window.open(
                                `/admin/provider/test-execution/${detailRun.runId}?check=${encodeURIComponent(c.name)}`,
                                '_blank',
                              )}
                            >
                              <Table.Td><Text size="xs" td="underline" c="blue">{c.name}</Text></Table.Td>
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
                    </div>
                  )}
                  {isLarge && (
                    <Text size="xs" c="dimmed" mt="xs">
                      {passes.length} passed, {failures.length} failed, {skips.length} skipped
                    </Text>
                  )}
                </>
              );
            })()}

            {/* Stdout tail for test host runs */}
            {detailRun.stdoutTail && (
              <>
                <Text size="sm" fw={600} mt="sm">Test Output (last 2000 chars)</Text>
                <Code block style={{ maxHeight: 200, overflowY: 'auto', fontSize: 11 }}>
                  {detailRun.stdoutTail}
                </Code>
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
                <Button
                  size="xs"
                  variant="subtle"
                  onClick={() => window.open(
                    `/admin/provider/test-execution/${detailRun.runId}`,
                    '_blank',
                  )}
                >
                  View All Checks
                </Button>
              )}
              <Button size="xs" variant="subtle" onClick={() => copyForClaude(detailRun)}>
                Copy for Claude
              </Button>
            </Group>
          </Stack>
        )}
      </Modal>

        </Tabs.Panel>

        <Tabs.Panel value="performance" pt="md">
          <PerformanceChart />
        </Tabs.Panel>
      </Tabs>
    </Stack>
  );
};
