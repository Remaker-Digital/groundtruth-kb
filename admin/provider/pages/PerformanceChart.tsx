// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * PerformanceChart — Time-series chart of test run performance.
 *
 * Plots run duration and latency stats across recent runs to detect
 * performance regressions. Uses recharts LineChart.
 *
 * API: GET /api/superadmin/tests/performance-history
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useEffect, useState } from 'react';
import {
  Card,
  Group,
  SegmentedControl,
  Select,
  Stack,
  Text,
  Title,
} from '@mantine/core';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { useProviderContext } from '../layouts/ProviderLayout';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface PerformancePoint {
  runId: string;
  suite: string;
  environment: string;
  startedAt: string | null;
  durationS: number | null;
  totalTests: number;
  passed: number;
  failed: number;
  avgLatencyMs: number | null;
  p95LatencyMs: number | null;
}

interface ChartPoint {
  label: string;
  runId: string;
  suite: string;
  durationS: number | null;
  avgLatencyMs: number | null;
  p95LatencyMs: number | null;
  passed: number;
  failed: number;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const METRIC_OPTIONS = [
  { value: 'duration', label: 'Duration (s)' },
  { value: 'avgLatency', label: 'Avg Latency (ms)' },
  { value: 'p95Latency', label: 'P95 Latency (ms)' },
];

const SUITE_COLORS: Record<string, string> = {
  full: '#ff3621',
  pipeline: '#e64980',
  unit: '#228be6',
  core: '#40c057',
  integration: '#fab005',
  agents: '#7950f2',
  security: '#fd7e14',
  regression: '#12b886',
  e2e: '#be4bdb',
  load: '#868e96',
};

function getSuiteColor(suite: string): string {
  return SUITE_COLORS[suite] || '#868e96';
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

interface PerformanceChartProps {
  className?: string;
}

export const PerformanceChart: React.FC<PerformanceChartProps> = () => {
  const { apiFetch } = useProviderContext();
  const [points, setPoints] = useState<PerformancePoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [metric, setMetric] = useState('duration');
  const [suiteFilter, setSuiteFilter] = useState<string | null>(null);
  const [envFilter, setEnvFilter] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams({ limit: '50' });
    if (suiteFilter) params.set('suite', suiteFilter);
    if (envFilter) params.set('environment', envFilter);

    apiFetch(`/api/superadmin/tests/performance-history?${params}`)
      .then((res: Response) => res.json())
      .then((data: { points: PerformancePoint[] }) => {
        setPoints(data.points || []);
      })
      .catch(() => setPoints([]))
      .finally(() => setLoading(false));
  }, [apiFetch, suiteFilter, envFilter]);

  // Transform to chart data
  const chartData: ChartPoint[] = points.map((p) => ({
    label: p.startedAt
      ? new Date(p.startedAt).toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
        })
      : p.runId.slice(0, 8),
    runId: p.runId,
    suite: p.suite,
    durationS: p.durationS,
    avgLatencyMs: p.avgLatencyMs,
    p95LatencyMs: p.p95LatencyMs,
    passed: p.passed,
    failed: p.failed,
  }));

  // Get unique suites in data for legend/coloring
  const suites = [...new Set(points.map((p) => p.suite))];

  // Determine Y-axis key based on metric
  const yKey =
    metric === 'duration'
      ? 'durationS'
      : metric === 'avgLatency'
        ? 'avgLatencyMs'
        : 'p95LatencyMs';

  const yLabel =
    metric === 'duration'
      ? 'Duration (seconds)'
      : metric === 'avgLatency'
        ? 'Avg Latency (ms)'
        : 'P95 Latency (ms)';

  // Suite options for filter
  const suiteOptions = [
    { value: '', label: 'All suites' },
    ...suites.map((s) => ({ value: s, label: s })),
  ];

  return (
    <Stack gap="md">
      <Group justify="space-between" align="flex-end">
        <Title order={4}>Performance Trends</Title>
        <Group gap="sm">
          <Select
            size="xs"
            label="Suite"
            placeholder="All suites"
            data={suiteOptions}
            value={suiteFilter || ''}
            onChange={(v) => setSuiteFilter(v || null)}
            clearable
            w={140}
          />
          <Select
            size="xs"
            label="Environment"
            placeholder="All"
            data={[
              { value: '', label: 'All' },
              { value: 'staging', label: 'Staging' },
              { value: 'production', label: 'Production' },
            ]}
            value={envFilter || ''}
            onChange={(v) => setEnvFilter(v || null)}
            clearable
            w={130}
          />
          <div>
            <Text size="xs" c="dimmed" mb={4}>
              Metric
            </Text>
            <SegmentedControl
              size="xs"
              value={metric}
              onChange={setMetric}
              data={METRIC_OPTIONS}
            />
          </div>
        </Group>
      </Group>

      <Card withBorder p="md">
        {loading ? (
          <Text c="dimmed" ta="center" py="xl">
            Loading performance data...
          </Text>
        ) : chartData.length === 0 ? (
          <Text c="dimmed" ta="center" py="xl">
            No test runs found. Trigger a test run to see performance trends.
          </Text>
        ) : (
          <ResponsiveContainer width="100%" height={360}>
            <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--mantine-color-dark-4)" />
              <XAxis
                dataKey="label"
                tick={{ fontSize: 11, fill: 'var(--mantine-color-dimmed)' }}
                interval="preserveStartEnd"
              />
              <YAxis
                tick={{ fontSize: 11, fill: 'var(--mantine-color-dimmed)' }}
                label={{
                  value: yLabel,
                  angle: -90,
                  position: 'insideLeft',
                  style: { fontSize: 11, fill: 'var(--mantine-color-dimmed)' },
                }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--mantine-color-dark-7)',
                  border: '1px solid var(--mantine-color-dark-4)',
                  borderRadius: 4,
                  fontSize: 12,
                }}
                labelStyle={{ color: 'var(--mantine-color-dimmed)' }}
                formatter={(value: number, name: string) => [
                  value != null ? value.toFixed(1) : '—',
                  name,
                ]}
              />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              {/* If filtered to one suite, show single line; otherwise per-suite */}
              {suiteFilter ? (
                <Line
                  type="monotone"
                  dataKey={yKey}
                  stroke={getSuiteColor(suiteFilter)}
                  name={suiteFilter}
                  strokeWidth={2}
                  dot={{ r: 3 }}
                  connectNulls
                />
              ) : (
                suites.map((suite) => (
                  <Line
                    key={suite}
                    type="monotone"
                    dataKey={yKey}
                    data={chartData.filter((d) => d.suite === suite)}
                    stroke={getSuiteColor(suite)}
                    name={suite}
                    strokeWidth={2}
                    dot={{ r: 3 }}
                    connectNulls
                  />
                ))
              )}
            </LineChart>
          </ResponsiveContainer>
        )}
      </Card>

      <Text size="xs" c="dimmed">
        Showing {chartData.length} runs.{' '}
        {chartData.length > 0 && (
          <>
            Earliest: {chartData[0].label} | Latest:{' '}
            {chartData[chartData.length - 1].label}
          </>
        )}
      </Text>
    </Stack>
  );
};
