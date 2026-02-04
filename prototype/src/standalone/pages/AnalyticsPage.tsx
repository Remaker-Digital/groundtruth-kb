// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

import React, { useState } from 'react';
import {
  Paper,
  Group,
  Stack,
  Text,
  Badge,
  SimpleGrid,
  Title,
  Table,
  Progress,
  SegmentedControl,
  Box,
  ThemeIcon,
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
import {
  ANALYTICS_SUMMARY,
  DAILY_VOLUMES,
  INTENT_BREAKDOWN,
} from '../../data/mockData';
import type { IntentBreakdown, DailyVolume } from '../../data/mockData';

const BRAND_RED = '#C41E2A';

// For response time and escalation rate, a DECREASE is an improvement
function isDeltaPositive(key: string, delta: number): boolean {
  const inverseMetrics = ['avgResponseTime', 'escalationRate'];
  if (inverseMetrics.includes(key)) {
    return delta < 0;
  }
  return delta > 0;
}

function formatDelta(delta: number, suffix: string = '%'): string {
  const sign = delta > 0 ? '+' : '';
  return `${sign}${delta}${suffix}`;
}

function formatChartDate(dateStr: string): string {
  const d = new Date(dateStr);
  return `${d.getMonth() + 1}/${d.getDate()}`;
}

// Filter daily volumes by period
function filterByPeriod(data: DailyVolume[], period: string): DailyVolume[] {
  const days = parseInt(period.replace('d', ''), 10);
  return data.slice(-days);
}

// Scale analytics summary based on selected period (simulates period change)
function scaleForPeriod(period: string): number {
  switch (period) {
    case '7d': return 0.23;
    case '14d': return 0.47;
    case '30d': return 1.0;
    case '90d': return 3.1;
    default: return 1.0;
  }
}

interface StatCardProps {
  label: string;
  value: string;
  delta: number;
  deltaKey: string;
  deltaSuffix?: string;
  detail?: string;
}

function StatCard({ label, value, delta, deltaKey, deltaSuffix = '%', detail }: StatCardProps) {
  const positive = isDeltaPositive(deltaKey, delta);
  return (
    <Paper p="lg" radius="md" withBorder>
      <Text size="xs" c="dimmed" tt="uppercase" fw={600} mb={4}>
        {label}
      </Text>
      <Group justify="space-between" align="flex-end">
        <Text size="xl" fw={700} lh={1}>
          {value}
        </Text>
        <Badge
          size="sm"
          variant="light"
          color={positive ? 'green' : 'red'}
        >
          {formatDelta(delta, deltaSuffix)}
        </Badge>
      </Group>
      {detail && (
        <Text size="xs" c="dimmed" mt={6}>
          {detail}
        </Text>
      )}
    </Paper>
  );
}

// Knowledge gap suggestions based on low-confidence or trending intents
const KNOWLEDGE_GAPS = [
  {
    id: 'gap-1',
    title: 'International Return Process',
    reason: 'High volume "Return/Exchange" queries from international customers lack specific guidance',
    intent: 'Return/Exchange',
    priority: 'high' as const,
    estimatedImpact: '+4% resolution rate',
  },
  {
    id: 'gap-2',
    title: 'Bulk Order Customization Options',
    reason: '"Bulk/Corporate" intent has lowest confidence (0.85) and is trending up',
    intent: 'Bulk/Corporate',
    priority: 'high' as const,
    estimatedImpact: '+8% confidence',
  },
  {
    id: 'gap-3',
    title: 'Account Recovery Self-Service',
    reason: '"Account Issues" intent has 0.89 confidence -- most escalations come from password reset flow',
    intent: 'Account Issues',
    priority: 'medium' as const,
    estimatedImpact: '-3% escalation rate',
  },
  {
    id: 'gap-4',
    title: 'Holiday Shipping Deadlines FAQ',
    reason: 'Seasonal spike in "Shipping Inquiry" expected; proactive article reduces volume',
    intent: 'Shipping Inquiry',
    priority: 'low' as const,
    estimatedImpact: '-12% shipping queries',
  },
];

const priorityColorMap: Record<string, string> = {
  high: 'red',
  medium: 'yellow',
  low: 'blue',
};

function trendArrow(trend: 'up' | 'down' | 'stable'): string {
  if (trend === 'up') return '\u2191';
  if (trend === 'down') return '\u2193';
  return '\u2192';
}

function trendColor(trend: 'up' | 'down' | 'stable'): string {
  if (trend === 'up') return 'green';
  if (trend === 'down') return 'red';
  return 'gray';
}

export function AnalyticsPage() {
  const [period, setPeriod] = useState('30d');
  const summary = ANALYTICS_SUMMARY;
  const scale = scaleForPeriod(period);
  const chartData = filterByPeriod(DAILY_VOLUMES, period);
  const computedColorScheme = useComputedColorScheme('dark');
  const isDark = computedColorScheme === 'dark';

  // Dark-mode-aware chart colors — designer palette (2026-02-03)
  const gridStroke = isDark ? 'rgba(255,255,255,0.06)' : '#e9ecef';
  const axisTickFill = isDark ? '#5C5C5C' : '#868e96';
  const axisLineStroke = isDark ? '#363636' : '#dee2e6';
  const tooltipBg = isDark ? '#19191a' : '#fff';
  const tooltipBorder = isDark ? '#363636' : '#dee2e6';
  const tooltipColor = isDark ? '#E0E0E0' : undefined;
  const cardBorder = isDark ? '#363636' : 'var(--mantine-color-gray-2)';

  // Scale total conversations for period, keep rates unchanged
  const scaledTotal = Math.round(summary.totalConversations * scale);

  return (
    <Stack gap="lg">
      {/* Page header with period selector */}
      <Group justify="space-between" align="flex-end">
        <div>
          <Title order={2}>Analytics</Title>
          <Text c="dimmed" size="sm">
            Performance metrics and intent analysis
          </Text>
        </div>
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

      {/* Stat cards - 2 rows of 3, with detail lines */}
      <SimpleGrid cols={{ base: 1, xs: 2, md: 3 }} spacing="md">
        <StatCard
          label="Total Conversations"
          value={scaledTotal.toLocaleString()}
          delta={summary.totalConversationsDelta}
          deltaKey="totalConversations"
          detail={`${Math.round(scaledTotal * 0.85).toLocaleString()} billable`}
        />
        <StatCard
          label="Avg Response Time"
          value={`${summary.avgResponseTime}s`}
          delta={summary.avgResponseTimeDelta}
          deltaKey="avgResponseTime"
          detail="P50: 1.2s | P95: 1.9s | P99: 3.8s"
        />
        <StatCard
          label="Resolution Rate"
          value={`${summary.resolutionRate}%`}
          delta={summary.resolutionRateDelta}
          deltaKey="resolutionRate"
          detail={`${Math.round(scaledTotal * summary.resolutionRate / 100).toLocaleString()} resolved`}
        />
        <StatCard
          label="Customer Satisfaction"
          value={`${summary.customerSatisfaction}/5`}
          delta={summary.customerSatisfactionDelta}
          deltaKey="customerSatisfaction"
          deltaSuffix=""
          detail="Based on 847 ratings"
        />
        <StatCard
          label="AI Handled"
          value={`${summary.aiHandledRate}%`}
          delta={summary.aiHandledRateDelta}
          deltaKey="aiHandledRate"
          detail={`${Math.round(scaledTotal * summary.aiHandledRate / 100).toLocaleString()} conversations`}
        />
        <StatCard
          label="Escalation Rate"
          value={`${summary.escalationRate}%`}
          delta={summary.escalationRateDelta}
          deltaKey="escalationRate"
          detail={`${Math.round(scaledTotal * summary.escalationRate / 100).toLocaleString()} escalated`}
        />
      </SimpleGrid>

      {/* Full-width area chart */}
      <Paper p="lg" radius="md" withBorder>
        <Group justify="space-between" mb="md">
          <Text fw={600}>Conversation Volume</Text>
          <Text size="xs" c="dimmed">
            {period === '30d' ? 'Last 30 days' : period === '7d' ? 'Last 7 days' : period === '14d' ? 'Last 14 days' : 'Last 90 days'}
          </Text>
        </Group>
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
                <stop offset="5%" stopColor="#2563EB" stopOpacity={0.12} />
                <stop offset="95%" stopColor="#2563EB" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="aGradAI" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#059669" stopOpacity={0.12} />
                <stop offset="95%" stopColor="#059669" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="aGradEscalated" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#D97706" stopOpacity={0.12} />
                <stop offset="95%" stopColor="#D97706" stopOpacity={0} />
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
              stroke="#2563EB"
              strokeWidth={1.5}
              fill="url(#aGradBillable)"
              name="Billable"
            />
            <Area
              type="monotone"
              dataKey="aiResolved"
              stroke="#059669"
              strokeWidth={1.5}
              fill="url(#aGradAI)"
              name="AI Resolved"
            />
            <Area
              type="monotone"
              dataKey="escalated"
              stroke="#D97706"
              strokeWidth={1.5}
              fill="url(#aGradEscalated)"
              name="Escalated"
            />
          </AreaChart>
        </ResponsiveContainer>
        {/* Legend */}
        <Group gap="lg" mt="xs" justify="center">
          {[
            { color: BRAND_RED, label: 'Total' },
            { color: '#2563EB', label: 'Billable' },
            { color: '#059669', label: 'AI Resolved' },
            { color: '#D97706', label: 'Escalated' },
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
      </Paper>

      {/* Intent Breakdown Table */}
      <Paper p="lg" radius="md" withBorder>
        <Text fw={600} mb="md">
          Intent Breakdown
        </Text>
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Intent</Table.Th>
              <Table.Th style={{ width: 80 }}>Count</Table.Th>
              <Table.Th style={{ width: 200 }}>Distribution</Table.Th>
              <Table.Th style={{ width: 120 }}>Avg Confidence</Table.Th>
              <Table.Th style={{ width: 70, textAlign: 'center' }}>Trend</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {INTENT_BREAKDOWN.map((intent: IntentBreakdown) => (
              <Table.Tr key={intent.intent}>
                <Table.Td>
                  <Text size="sm" fw={500}>
                    {intent.intent}
                  </Text>
                </Table.Td>
                <Table.Td>
                  <Text size="sm">{intent.count}</Text>
                </Table.Td>
                <Table.Td>
                  <Group gap="xs" wrap="nowrap">
                    <Progress
                      value={intent.percentage}
                      color={BRAND_RED}
                      size="sm"
                      style={{ flex: 1 }}
                      radius="xl"
                    />
                    <Text size="xs" c="dimmed" w={36} ta="right">
                      {intent.percentage}%
                    </Text>
                  </Group>
                </Table.Td>
                <Table.Td>
                  <Badge
                    size="sm"
                    variant="light"
                    color={intent.avgConfidence >= 0.93 ? 'green' : intent.avgConfidence >= 0.90 ? 'yellow' : 'orange'}
                  >
                    {(intent.avgConfidence * 100).toFixed(0)}%
                  </Badge>
                </Table.Td>
                <Table.Td style={{ textAlign: 'center' }}>
                  <Text
                    size="sm"
                    fw={600}
                    c={trendColor(intent.trend)}
                  >
                    {trendArrow(intent.trend)}
                  </Text>
                </Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      </Paper>

      {/* Knowledge Gaps */}
      <Paper p="lg" radius="md" withBorder>
        <Group justify="space-between" mb="md">
          <div>
            <Text fw={600}>Knowledge Gaps</Text>
            <Text size="xs" c="dimmed">
              Suggested articles to create based on unresolved intents and low confidence areas
            </Text>
          </div>
          <Badge size="sm" variant="light" color="orange">
            {KNOWLEDGE_GAPS.length} suggestions
          </Badge>
        </Group>
        <Stack gap="sm">
          {KNOWLEDGE_GAPS.map((gap) => (
            <Paper
              key={gap.id}
              p="md"
              radius="sm"
              style={{
                border: `1px solid ${cardBorder}`,
              }}
            >
              <Group justify="space-between" mb={4}>
                <Group gap="sm">
                  <Text size="sm" fw={600}>
                    {gap.title}
                  </Text>
                  <Badge
                    size="xs"
                    variant="light"
                    color={priorityColorMap[gap.priority]}
                  >
                    {gap.priority}
                  </Badge>
                </Group>
                <Badge size="xs" variant="outline" color="gray">
                  {gap.intent}
                </Badge>
              </Group>
              <Text size="xs" c="dimmed" mb={4}>
                {gap.reason}
              </Text>
              <Text size="xs" fw={500} c="green">
                Estimated impact: {gap.estimatedImpact}
              </Text>
            </Paper>
          ))}
        </Stack>
      </Paper>
    </Stack>
  );
}
