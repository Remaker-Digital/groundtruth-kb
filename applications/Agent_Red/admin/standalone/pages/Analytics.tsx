// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

/**
 * Analytics page — Standalone admin.
 *
 * Adapted from prototype AnalyticsPage with API hooks replacing mock data.
 * Mantine v7 dark mode design with Recharts area chart.
 *
 * Changes from prototype:
 *   - Mock data replaced with useAnalyticsSummary, useDailyVolume,
 *     useIntentBreakdown, useKnowledgeGaps hooks.
 *   - StatCard delta badges removed (API AnalyticsSummary has no delta fields).
 *   - "AI Handled" StatCard removed (no aiHandledRate in API).
 *   - Period selector retained as visual placeholder (API does not support
 *     period filtering yet); no data scaling applied.
 *   - Chart simplified from 4 series to 2 (API DailyVolume: total + billable).
 *   - Intent table: avgConfidence and trend columns removed.
 *   - Knowledge Gaps section uses API data (query, frequency, lastSeen)
 *     instead of prototype inline constant (title, reason, priority, impact).
 *   - Null-safety guards on all API data access.
 */

import React, { useState } from 'react';
import {
  Paper,
  Group,
  Stack,
  Text,
  SimpleGrid,
  Title,
  Table,
  Progress,
  SegmentedControl,
  Box,
  Badge,
  Loader,
  useComputedColorScheme,
} from '@mantine/core';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from 'recharts';
import { useAppContext } from '../layouts/StandaloneLayout';
import {
  useAnalyticsSummary,
  useDailyVolume,
  useIntentBreakdown,
  useKnowledgeGaps,
} from '../../shared/hooks/index';
import { agentDisplayLabel } from '../../shared/AnalyticsOverview';
import { tokens } from '../../shared/theme/styles';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const BRAND_RED = tokens.brand;

// ---------------------------------------------------------------------------
// StatCard — simplified (no delta badge)
// ---------------------------------------------------------------------------

interface StatCardProps {
  label: string;
  value: string;
  detail?: string;
}

function StatCard({ label, value, detail }: StatCardProps) {
  return (
    <Paper p="lg" radius="md" withBorder>
      <Text size="xs" c="dimmed" fw={600} mb={4}>
        {label}
      </Text>
      <Text size="xl" fw={700} lh={1}>
        {value}
      </Text>
      {detail && (
        <Text size="xs" c="dimmed" mt={6}>
          {detail}
        </Text>
      )}
    </Paper>
  );
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatChartDate(dateStr: string): string {
  const d = new Date(dateStr);
  return `${d.getMonth() + 1}/${d.getDate()}`;
}

function formatLastSeen(dateStr: string): string {
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
  } catch {
    return dateStr;
  }
}

// ---------------------------------------------------------------------------
// AnalyticsPage
// ---------------------------------------------------------------------------

export const AnalyticsPage: React.FC = () => {
  const { apiFetch } = useAppContext();
  const [period, setPeriod] = useState('30d');
  // API hooks
  const summary = useAnalyticsSummary(apiFetch);
  const dailyVolume = useDailyVolume(apiFetch);
  const intents = useIntentBreakdown(apiFetch);
  const gaps = useKnowledgeGaps(apiFetch);

  // Dark mode chart colors — Mazel design revision (2026-02-03 mockup)
  const computedColorScheme = useComputedColorScheme('dark');
  const isDark = computedColorScheme === 'dark';
  const gridStroke = isDark ? 'rgba(255,255,255,0.06)' : '#e9ecef';
  const axisTickFill = isDark ? tokens.textTertiary : '#868e96';
  const axisLineStroke = isDark ? tokens.border : '#dee2e6';
  const tooltipBg = isDark ? tokens.surface : '#fff';
  const tooltipBorder = isDark ? tokens.border : '#dee2e6';
  const tooltipColor = isDark ? tokens.textSecondary : undefined;
  const cardBorder = isDark ? tokens.border : 'var(--mantine-color-gray-2)';

  // Null-safe data extraction
  const s = summary.data;
  const chartData = dailyVolume.data?.days ?? [];
  const intentList = intents.data?.intents ?? [];
  const gapList = gaps.data?.gaps ?? [];

  // Loading state
  const isLoading = summary.loading && !s;

  return (
    <Stack gap="lg">
      {/* Page header with mode filter + period selector */}
      <Group justify="space-between" align="flex-end">
        <div>
          <Title order={2}>Analytics</Title>
          <Text c="dimmed" size="sm">
            Performance metrics and intent analysis
          </Text>
        </div>
        <Group gap="md">
          <SegmentedControl
            value={period}
            onChange={setPeriod}
            data={[
              { label: '7d', value: '7d' },
              { label: '14d', value: '14d' },
              { label: '30d', value: '30d' },
              { label: '90d', value: '90d' },
            ]}
            size="sm"
          />
        </Group>
      </Group>


      {/* Loading indicator */}
      {isLoading && (
        <Group justify="center" py="xl">
          <Loader size="sm" />
          <Text size="sm" c="dimmed">Loading analytics...</Text>
        </Group>
      )}

      {/* Error state */}
      {summary.error && (
        <Paper p="md" radius="md" withBorder>
          <Text c="red" size="sm">
            Failed to load analytics: {summary.error}
          </Text>
        </Paper>
      )}

      {/* Stat cards — 5 cards, no deltas */}
      <SimpleGrid cols={{ base: 1, xs: 2, md: 3 }} spacing="md">
        <StatCard
          label="Total conversations"
          value={(s?.totalConversations ?? 0).toLocaleString()}
          detail={s ? `Billable: ${(s.billableConversations ?? 0).toLocaleString()}` : undefined}
        />
        <StatCard
          label="Avg response time"
          value={s?.avgResponseTime != null ? `${s.avgResponseTime}s` : '--'}
        />
        <StatCard
          label="Resolution rate"
          value={s?.resolutionRate != null ? `${(s.resolutionRate * 100).toFixed(1)}%` : '--'}
          detail={
            s != null
              ? `${Math.round(s.totalConversations * (s.resolutionRate ?? 0)).toLocaleString()} resolved`
              : undefined
          }
        />
        <StatCard
          label="Customer satisfaction"
          value={s?.customerSatisfaction != null ? `${s.customerSatisfaction}/5` : '--'}
        />
        <StatCard
          label="Escalation rate"
          value={s != null ? `${(s.escalationRate * 100).toFixed(1)}%` : '--'}
          detail={
            s != null
              ? `${(s.escalationCount ?? 0).toLocaleString()} escalated`
              : undefined
          }
        />
      </SimpleGrid>

      {/* Full-width area chart — 2 series: Total (red) + Billable (blue) */}
      <Paper p="lg" radius="md" withBorder>
        <Group justify="space-between" mb="md">
          <Text fw={600}>Conversation volume</Text>
          <Text size="xs" c="dimmed">
            {period === '7d'
              ? 'Last 7 days'
              : period === '14d'
                ? 'Last 14 days'
                : period === '90d'
                  ? 'Last 90 days'
                  : 'Last 30 days'}
          </Text>
        </Group>
        {chartData.length > 0 ? (
          <>
            <ResponsiveContainer width="100%" height={340}>
              <AreaChart
                data={chartData}
                margin={{ top: 8, right: 8, left: -10, bottom: 0 }}
              >
                <defs>
                  <linearGradient id="aGradTotal" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={BRAND_RED} stopOpacity={0.15} />
                    <stop offset="95%" stopColor={BRAND_RED} stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="aGradBillable" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={tokens.actionHover} stopOpacity={0.12} />
                    <stop offset="95%" stopColor={tokens.actionHover} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} />
                <XAxis
                  dataKey="date"
                  tickFormatter={formatChartDate}
                  tick={{ fontSize: 11, fill: axisTickFill }}
                  axisLine={{ stroke: axisLineStroke }}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fontSize: 11, fill: axisTickFill }}
                  axisLine={{ stroke: axisLineStroke }}
                  tickLine={false}
                />
                <Tooltip
                  contentStyle={{
                    borderRadius: 8,
                    border: `1px solid ${tooltipBorder}`,
                    fontSize: 12,
                    background: tooltipBg,
                    color: tooltipColor,
                  }}
                  labelFormatter={(label) => `Date: ${label}`}
                />
                <Area
                  type="monotone"
                  dataKey="total"
                  stroke={BRAND_RED}
                  strokeWidth={2}
                  fill="url(#aGradTotal)"
                  name="Total"
                />
                <Area
                  type="monotone"
                  dataKey="billable"
                  stroke={tokens.actionHover}
                  strokeWidth={1.5}
                  fill="url(#aGradBillable)"
                  name="Billable"
                />
              </AreaChart>
            </ResponsiveContainer>
            {/* Legend */}
            <Group gap="lg" mt="xs" justify="center">
              {[
                { color: BRAND_RED, label: 'Total' },
                { color: tokens.actionHover, label: 'Billable' },
              ].map((item) => (
                <Group gap={6} key={item.label}>
                  <Box
                    style={{
                      width: 10,
                      height: 10,
                      borderRadius: 2,
                      backgroundColor: item.color,
                    }}
                  />
                  <Text size="xs" c="dimmed">
                    {item.label}
                  </Text>
                </Group>
              ))}
            </Group>
          </>
        ) : (
          <Group justify="center" py="xl">
            <Text size="sm" c="dimmed">
              {dailyVolume.loading ? 'Loading chart data...' : 'No volume data available'}
            </Text>
          </Group>
        )}
      </Paper>

      {/* Topic Breakdown Table — 3 columns: Topic, Count, Distribution */}
      <Paper p="lg" radius="md" withBorder>
        <Text fw={600} mb="md">
          Topic breakdown
        </Text>
        {intentList.length > 0 ? (
          <Table striped highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Topic</Table.Th>
                <Table.Th style={{ width: 80 }}>Count</Table.Th>
                <Table.Th style={{ width: 200 }}>Distribution</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {intentList.map((intent) => (
                <Table.Tr key={intent.agent}>
                  <Table.Td>
                    <Text size="sm" fw={500}>
                      {agentDisplayLabel(intent.agent)}
                    </Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="sm">{(intent.invocationCount ?? 0).toLocaleString()}</Text>
                  </Table.Td>
                  <Table.Td>
                    <Group gap="xs" wrap="nowrap">
                      <Progress
                        value={intent.percentage ?? 0}
                        color={BRAND_RED}
                        size="sm"
                        style={{ flex: 1 }}
                        radius="xl"
                      />
                      <Text size="xs" c="dimmed" w={36} ta="right">
                        {intent.percentage ?? 0}%
                      </Text>
                    </Group>
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        ) : (
          <Text size="sm" c="dimmed" ta="center" py="md">
            {intents.loading ? 'Loading topic data...' : 'No topic data available'}
          </Text>
        )}
      </Paper>

      {/* Knowledge Gaps — conversations where AI could not resolve the query */}
      <Paper p="lg" radius="md" withBorder>
        <Group justify="space-between" mb="md">
          <div>
            <Text fw={600}>Knowledge gaps</Text>
            <Text size="xs" c="dimmed">
              Conversations where the AI could not fully resolve the customer query
            </Text>
          </div>
          {gapList.length > 0 && (
            <Badge size="sm" variant="light" color="orange">
              {gapList.length} {gapList.length === 1 ? 'gap' : 'gaps'}
            </Badge>
          )}
        </Group>
        {gapList.length > 0 ? (
          <Table striped highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Conversation</Table.Th>
                <Table.Th style={{ width: 100 }}>Status</Table.Th>
                <Table.Th style={{ width: 80 }}>Turns</Table.Th>
                <Table.Th style={{ width: 80 }}>Messages</Table.Th>
                <Table.Th style={{ width: 120 }}>Started</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {gapList.map((gap, idx) => (
                <Table.Tr key={`gap-${idx}`}>
                  <Table.Td>
                    <Text size="sm" fw={500} lineClamp={1}>
                      {gap.conversationId}
                    </Text>
                    {gap.customerId && (
                      <Text size="xs" c="dimmed">{gap.customerId}</Text>
                    )}
                  </Table.Td>
                  <Table.Td>
                    <Badge size="xs" variant="light" color={
                      gap.status === 'escalated' ? 'red' :
                      gap.status === 'ended' ? 'green' :
                      gap.status === 'active' ? 'blue' : 'gray'
                    }>
                      {gap.status ?? 'unknown'}
                    </Badge>
                  </Table.Td>
                  <Table.Td>
                    <Text size="sm">{gap.turnCount ?? 0}</Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="sm">{gap.messageCount ?? 0}</Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" c="dimmed">
                      {gap.startedAt ? formatLastSeen(gap.startedAt) : '--'}
                    </Text>
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        ) : (
          <Text size="sm" c="dimmed" ta="center" py="md">
            {gaps.loading ? 'Loading knowledge gaps...' : 'No knowledge gaps detected'}
          </Text>
        )}
      </Paper>
    </Stack>
  );
};
