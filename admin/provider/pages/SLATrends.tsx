/**
 * SLATrends — SLA uptime & latency time-series with error budget gauges.
 *
 * Shows:
 *   1. Range selector (1d / 7d / 30d / 90d)
 *   2. Recharts line chart: uptime %, P50, P95, P99 latency
 *   3. Error budget ring gauges per tier (STARTER, PROFESSIONAL, ENTERPRISE)
 *
 * API: GET /api/superadmin/sla/trends?range_days=N&period_days=30
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useEffect, useState } from 'react';
import {
  Card,
  Group,
  RingProgress,
  SegmentedControl,
  SimpleGrid,
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
import { LoadingState } from '../../shared/LoadingState';
import { tokens, chartAxisTick, chartTooltipStyle, chartLabelStyle } from '../../shared/theme/styles';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface TrendPoint {
  timestamp: string;
  uptime_pct: number;
  p50_ms: number;
  p95_ms: number;
  p99_ms: number;
  total_requests: number;
}

interface ErrorBudget {
  tier: string;
  period_days: number;
  allowed_downtime_minutes: number;
  actual_downtime_minutes: number;
  budget_remaining: number;
  budget_consumed_pct: number;
  is_within_budget: boolean;
}

interface SLATrendsResponse {
  range_days: number;
  trend_points: TrendPoint[];
  error_budgets: Record<string, ErrorBudget>;
  generated_at: string;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const RANGE_OPTIONS = [
  { value: '1', label: '1 day' },
  { value: '7', label: '7 days' },
  { value: '30', label: '30 days' },
  { value: '90', label: '90 days' },
];

const TIER_COLORS: Record<string, string> = {
  STARTER: tokens.chartAxis,
  PROFESSIONAL: tokens.chartLine1,
  ENTERPRISE: tokens.chartPurple,
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function SLATrendsPage() {
  const { apiFetch, onNotify } = useProviderContext();
  const [data, setData] = useState<SLATrendsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [range, setRange] = useState('7');

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      try {
        const res = await apiFetch(
          `/api/superadmin/sla/trends?range_days=${range}&period_days=30`,
        );
        if (res.ok && !cancelled) {
          setData(await res.json());
        } else if (!cancelled) {
          onNotify('Failed to load SLA trends', 'error');
        }
      } catch {
        if (!cancelled) onNotify('Network error loading SLA trends', 'error');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [apiFetch, onNotify, range]);

  // Prepare chart data
  const chartData = (data?.trend_points ?? []).map((pt) => ({
    ...pt,
    label: formatTimestamp(pt.timestamp, parseInt(range)),
  }));

  return (
    <Stack gap="lg">
      <Group justify="space-between" align="center">
        <Title order={3} c={tokens.textPrimary}>SLA Trends</Title>
        <SegmentedControl
          value={range}
          onChange={setRange}
          data={RANGE_OPTIONS}
          size="xs"
          color="action"
        />
      </Group>

      {loading ? (
        <LoadingState text="Loading SLA data" />
      ) : !data ? (
        <Text c="dimmed" ta="center" mt="xl">
          Unable to load SLA trend data.
        </Text>
      ) : (
        <>
          {/* Uptime chart */}
          <Card withBorder padding="lg" radius="md" bg={tokens.surface}>
            <Text fw={600} size="sm" c={tokens.textSecondary} mb="md">Uptime %</Text>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke={tokens.chartGrid} />
                <XAxis dataKey="label" tick={chartAxisTick} />
                <YAxis
                  domain={[99, 100]}
                  tick={chartAxisTick}
                  tickFormatter={(v: number) => `${v}%`}
                />
                <Tooltip
                  contentStyle={chartTooltipStyle}
                  labelStyle={chartLabelStyle}
                />
                <Line
                  type="monotone"
                  dataKey="uptime_pct"
                  stroke={tokens.success}
                  strokeWidth={2}
                  dot={false}
                  name="Uptime %"
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>

          {/* Latency chart */}
          <Card withBorder padding="lg" radius="md" bg={tokens.surface}>
            <Text fw={600} size="sm" c={tokens.textSecondary} mb="md">Response Latency (ms)</Text>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke={tokens.chartGrid} />
                <XAxis dataKey="label" tick={chartAxisTick} />
                <YAxis tick={chartAxisTick} />
                <Tooltip
                  contentStyle={chartTooltipStyle}
                  labelStyle={chartLabelStyle}
                />
                <Legend wrapperStyle={{ color: tokens.textMuted, fontSize: '12px' }} />
                <Line type="monotone" dataKey="p50_ms" stroke={tokens.chartLine1} strokeWidth={2} dot={false} name="P50" />
                <Line type="monotone" dataKey="p95_ms" stroke={tokens.chartLine2} strokeWidth={2} dot={false} name="P95" />
                <Line type="monotone" dataKey="p99_ms" stroke={tokens.chartLine3} strokeWidth={2} dot={false} name="P99" />
              </LineChart>
            </ResponsiveContainer>
          </Card>

          {/* Error budget gauges */}
          {Object.keys(data.error_budgets ?? {}).length > 0 && (
            <>
              <Title order={4} c={tokens.textSecondary}>Error Budgets (30-day period)</Title>
              <SimpleGrid cols={{ base: 1, sm: 3 }} spacing="md">
                {Object.entries(data.error_budgets ?? {}).map(([tier, budget]) => (
                  <Card key={tier} withBorder padding="lg" radius="md" bg={tokens.surface}>
                    <Group justify="space-between" mb="sm">
                      <Text fw={600} size="sm" c={tokens.textSecondary}>{tier}</Text>
                      <Text
                        size="xs"
                        fw={600}
                        c={budget.is_within_budget ? tokens.success : tokens.danger}
                      >
                        {budget.is_within_budget ? 'Within budget' : 'Budget exceeded'}
                      </Text>
                    </Group>
                    <Group justify="center">
                      <RingProgress
                        size={120}
                        thickness={10}
                        roundCaps
                        sections={[
                          {
                            value: Math.min(budget.budget_consumed_pct, 100),
                            color: budget.budget_consumed_pct > 80
                              ? tokens.danger
                              : budget.budget_consumed_pct > 50
                                ? tokens.warning
                                : TIER_COLORS[tier] ?? tokens.chartLine1,
                          },
                        ]}
                        label={
                          <Text ta="center" size="xs" c={tokens.textSecondary}>
                            {budget.budget_consumed_pct.toFixed(1)}%
                            <br />
                            <Text span size="xs" c="dimmed">used</Text>
                          </Text>
                        }
                      />
                    </Group>
                    <Stack gap={4} mt="sm">
                      <Group justify="space-between">
                        <Text size="xs" c="dimmed">Allowed</Text>
                        <Text size="xs" c={tokens.textMuted}>{budget.allowed_downtime_minutes.toFixed(1)} min</Text>
                      </Group>
                      <Group justify="space-between">
                        <Text size="xs" c="dimmed">Actual</Text>
                        <Text size="xs" c={tokens.textMuted}>{budget.actual_downtime_minutes.toFixed(1)} min</Text>
                      </Group>
                      <Group justify="space-between">
                        <Text size="xs" c="dimmed">Remaining</Text>
                        <Text size="xs" c={tokens.textMuted}>{(budget.budget_remaining * 100).toFixed(1)}%</Text>
                      </Group>
                    </Stack>
                  </Card>
                ))}
              </SimpleGrid>
            </>
          )}

          {/* Request volume */}
          {chartData.length > 0 && (
            <Card withBorder padding="lg" radius="md" bg={tokens.surface}>
              <Text fw={600} size="sm" c={tokens.textSecondary} mb="md">Request Volume</Text>
              <ResponsiveContainer width="100%" height={180}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke={tokens.chartGrid} />
                  <XAxis dataKey="label" tick={chartAxisTick} />
                  <YAxis tick={chartAxisTick} />
                  <Tooltip
                    contentStyle={chartTooltipStyle}
                    labelStyle={chartLabelStyle}
                  />
                  <Line
                    type="monotone"
                    dataKey="total_requests"
                    stroke={tokens.chartLine4}
                    strokeWidth={1.5}
                    dot={false}
                    name="Requests"
                  />
                </LineChart>
              </ResponsiveContainer>
            </Card>
          )}
        </>
      )}
    </Stack>
  );
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatTimestamp(iso: string, rangeDays: number): string {
  const d = new Date(iso);
  if (rangeDays <= 3) {
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }
  return d.toLocaleDateString([], { month: 'short', day: 'numeric' });
}
