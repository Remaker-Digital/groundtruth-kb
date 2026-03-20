/**
 * TestRunDetail — Standalone drill-down page for test run checks.
 *
 * Opened in a new tab from the TestExecution detail modal.
 * Route: /test-execution/:runId?check=<name>
 *
 * - No check param: full sortable/filterable checks table
 * - With check param: single check detail view with full output
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useEffect, useState } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import {
  Badge,
  Button,
  Card,
  Code,
  Group,
  SegmentedControl,
  Stack,
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

interface RunData {
  runId: string;
  environment: string;
  suite: string;
  status: string;
  startedAt: string | null;
  completedAt: string | null;
  totalTests: number;
  passed: number;
  failed: number;
  skipped: number;
  errored: number;
  durationS: number | null;
  checks: CheckResult[];
  stdoutTail: string;
}

const STATUS_COLORS: Record<string, string> = {
  pass: 'green',
  fail: 'red',
  skip: 'yellow',
  error: 'red',
};

const RUN_STATUS_COLORS: Record<string, string> = {
  queued: 'blue',
  running: 'orange',
  passed: 'green',
  failed: 'red',
  error: 'red',
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const TestRunDetailPage: React.FC = () => {
  const { runId } = useParams<{ runId: string }>();
  const [searchParams, setSearchParams] = useSearchParams();
  const checkName = searchParams.get('check');
  const { apiFetch } = useProviderContext();

  const [run, setRun] = useState<RunData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState('all');
  const [categoryFilter, setCategoryFilter] = useState('all');

  useEffect(() => {
    if (!runId) return;
    setLoading(true);
    apiFetch(`/api/superadmin/tests/${runId}/status`)
      .then((res: Response) => res.json())
      .then((data: RunData) => {
        setRun(data);
        setError(null);
      })
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, [runId, apiFetch]);

  if (loading) {
    return (
      <Stack p="xl">
        <Title order={3}>Loading run {runId}...</Title>
      </Stack>
    );
  }

  if (error || !run) {
    return (
      <Stack p="xl">
        <Title order={3} c="red">Error loading run</Title>
        <Text>{error || 'Run not found'}</Text>
      </Stack>
    );
  }

  // Single check detail view
  if (checkName) {
    const check = run.checks.find((c) => c.name === checkName);
    if (!check) {
      return (
        <Stack p="xl">
          <Title order={3}>Check not found</Title>
          <Text>No check named "{checkName}" in run {runId}</Text>
          <Button
            variant="subtle"
            onClick={() => {
              setSearchParams({});
            }}
          >
            View all checks
          </Button>
        </Stack>
      );
    }

    // Extract stdout context lines mentioning this check
    const stdoutLines = run.stdoutTail
      ? run.stdoutTail.split('\n')
      : [];
    const checkBaseName = check.name.split('::').pop() || check.name;
    const contextLines: string[] = [];
    stdoutLines.forEach((line, i) => {
      if (line.toLowerCase().includes(checkBaseName.toLowerCase())) {
        // Include surrounding context (3 lines before/after)
        for (let j = Math.max(0, i - 3); j <= Math.min(stdoutLines.length - 1, i + 3); j++) {
          if (!contextLines.includes(stdoutLines[j])) {
            contextLines.push(stdoutLines[j]);
          }
        }
      }
    });

    return (
      <Stack p="xl" gap="lg">
        <Group>
          <Button
            variant="subtle"
            size="sm"
            onClick={() => setSearchParams({})}
          >
            ← All checks
          </Button>
          <Badge color={RUN_STATUS_COLORS[run.status] || 'gray'} size="lg">
            {run.environment}
          </Badge>
          <Text size="sm" c="dimmed">
            {run.suite} / {run.runId}
          </Text>
        </Group>

        <Title order={2}>{check.name}</Title>

        <Group gap="md">
          <Badge
            color={STATUS_COLORS[check.status] || 'gray'}
            size="lg"
            variant="filled"
          >
            {check.status.toUpperCase()}
          </Badge>
          <Badge variant="outline" size="lg">
            {check.category}
          </Badge>
          <Text size="sm" c="dimmed">
            {check.latencyMs > 0 ? `${check.latencyMs}ms` : '—'}
          </Text>
        </Group>

        {check.detail && (
          <Card withBorder p="md">
            <Text fw={600} mb="xs">
              Detail / Error Output
            </Text>
            <Code
              block
              style={{
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
                maxHeight: 600,
                overflow: 'auto',
                fontSize: 12,
              }}
            >
              {check.detail}
            </Code>
          </Card>
        )}

        {contextLines.length > 0 && (
          <Card withBorder p="md">
            <Text fw={600} mb="xs">
              Stdout Context
            </Text>
            <Code
              block
              style={{
                whiteSpace: 'pre-wrap',
                maxHeight: 400,
                overflow: 'auto',
                fontSize: 11,
              }}
            >
              {contextLines.join('\n')}
            </Code>
          </Card>
        )}

        {!check.detail && contextLines.length === 0 && (
          <Text c="dimmed">No detail or stdout context available for this check.</Text>
        )}
      </Stack>
    );
  }

  // Full checks table view
  const categories = ['all', ...new Set(run.checks.map((c) => c.category))];
  const filtered = run.checks.filter((c) => {
    if (statusFilter !== 'all' && c.status !== statusFilter) return false;
    if (categoryFilter !== 'all' && c.category !== categoryFilter) return false;
    return true;
  });

  return (
    <Stack p="xl" gap="md">
      {/* Run header */}
      <Group justify="space-between">
        <Group gap="sm">
          <Title order={3}>Run {run.runId.slice(0, 16)}</Title>
          <Badge color={RUN_STATUS_COLORS[run.status] || 'gray'} size="lg">
            {run.status}
          </Badge>
        </Group>
        <Group gap="sm">
          <Badge variant="outline">{run.environment}</Badge>
          <Badge variant="outline">{run.suite}</Badge>
          <Text size="sm" c="dimmed">
            {run.durationS ? `${run.durationS}s` : '—'} |{' '}
            {run.startedAt ? new Date(run.startedAt).toLocaleString() : '—'}
          </Text>
        </Group>
      </Group>

      <Group gap="xs">
        <Badge color="green" variant="light">{run.passed}P</Badge>
        <Badge color="red" variant="light">{run.failed}F</Badge>
        {run.errored > 0 && (
          <Badge color="orange" variant="light">{run.errored}E</Badge>
        )}
        <Text size="sm" c="dimmed">/ {run.totalTests} total</Text>
      </Group>

      {/* Filters */}
      <Group gap="md">
        <div>
          <Text size="xs" c="dimmed" mb={4}>Status</Text>
          <SegmentedControl
            size="xs"
            value={statusFilter}
            onChange={setStatusFilter}
            data={[
              { value: 'all', label: 'All' },
              { value: 'pass', label: 'Pass' },
              { value: 'fail', label: 'Fail' },
              { value: 'error', label: 'Error' },
            ]}
          />
        </div>
        <div>
          <Text size="xs" c="dimmed" mb={4}>Category</Text>
          <SegmentedControl
            size="xs"
            value={categoryFilter}
            onChange={setCategoryFilter}
            data={categories.map((c) => ({ value: c, label: c }))}
          />
        </div>
        <Text size="sm" c="dimmed" mt="auto">
          {filtered.length} / {run.checks.length} checks
        </Text>
      </Group>

      {/* Checks table */}
      <div style={{ maxHeight: 'calc(100vh - 280px)', overflow: 'auto' }}>
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Check Name</Table.Th>
              <Table.Th>Category</Table.Th>
              <Table.Th>Status</Table.Th>
              <Table.Th>Latency</Table.Th>
              <Table.Th>Detail</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {filtered.map((c, i) => (
              <Table.Tr
                key={`${c.name}-${i}`}
                style={{ cursor: 'pointer' }}
                onClick={() => setSearchParams({ check: c.name })}
              >
                <Table.Td>
                  <Text size="xs" style={{ fontFamily: 'monospace' }}>
                    {c.name}
                  </Text>
                </Table.Td>
                <Table.Td>
                  <Badge size="xs" variant="outline">{c.category}</Badge>
                </Table.Td>
                <Table.Td>
                  <Badge
                    size="xs"
                    color={STATUS_COLORS[c.status] || 'gray'}
                  >
                    {c.status}
                  </Badge>
                </Table.Td>
                <Table.Td>
                  <Text size="xs">{c.latencyMs > 0 ? `${c.latencyMs}ms` : '—'}</Text>
                </Table.Td>
                <Table.Td>
                  <Text
                    size="xs"
                    lineClamp={1}
                    style={{ maxWidth: 400 }}
                  >
                    {c.detail || '—'}
                  </Text>
                </Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      </div>
    </Stack>
  );
};
