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
  Box,
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
  CONVERSATIONS,
  INTENT_BREAKDOWN,
} from '../../data/mockData';

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

const statusColorMap: Record<string, string> = {
  active: 'blue',
  waiting: 'yellow',
  resolved: 'green',
  escalated: 'red',
};

interface StatCardProps {
  label: string;
  value: string;
  delta: number;
  deltaKey: string;
  deltaSuffix?: string;
}

function StatCard({ label, value, delta, deltaKey, deltaSuffix = '%' }: StatCardProps) {
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
    </Paper>
  );
}

function formatChartDate(dateStr: string): string {
  const d = new Date(dateStr);
  return `${d.getMonth() + 1}/${d.getDate()}`;
}

export function DashboardPage() {
  const summary = ANALYTICS_SUMMARY;
  const recentConversations = CONVERSATIONS.slice(0, 5);
  const computedColorScheme = useComputedColorScheme('dark');
  const isDark = computedColorScheme === 'dark';

  // Dark-mode-aware chart colors
  const gridStroke = isDark ? 'rgba(255,255,255,0.06)' : '#e9ecef';
  const axisTickFill = isDark ? '#5C5C5C' : '#868e96';
  const axisLineStroke = isDark ? 'rgba(255,255,255,0.08)' : '#dee2e6';
  const tooltipBg = isDark ? '#2A2A2A' : '#fff';
  const tooltipBorder = isDark ? 'rgba(255,255,255,0.1)' : '#dee2e6';
  const tooltipColor = isDark ? '#E0E0E0' : undefined;
  const intentBarBg = isDark ? 'rgba(255,255,255,0.06)' : '#f1f3f5';
  const cardBorder = isDark ? 'rgba(255,255,255,0.06)' : 'var(--mantine-color-gray-2)';

  return (
    <Stack gap="lg">
      {/* Page header */}
      <div>
        <Title order={2}>Dashboard</Title>
        <Text c="dimmed" size="sm">
          Overview of your customer experience performance
        </Text>
      </div>

      {/* Stat cards - 2 rows of 3 */}
      <SimpleGrid cols={{ base: 1, xs: 2, md: 3 }} spacing="md">
        <StatCard
          label="Total Conversations"
          value={summary.totalConversations.toLocaleString()}
          delta={summary.totalConversationsDelta}
          deltaKey="totalConversations"
        />
        <StatCard
          label="Avg Response Time"
          value={`${summary.avgResponseTime}s`}
          delta={summary.avgResponseTimeDelta}
          deltaKey="avgResponseTime"
        />
        <StatCard
          label="Resolution Rate"
          value={`${summary.resolutionRate}%`}
          delta={summary.resolutionRateDelta}
          deltaKey="resolutionRate"
        />
        <StatCard
          label="Customer Satisfaction"
          value={`${summary.customerSatisfaction}/5`}
          delta={summary.customerSatisfactionDelta}
          deltaKey="customerSatisfaction"
          deltaSuffix=""
        />
        <StatCard
          label="AI Handled"
          value={`${summary.aiHandledRate}%`}
          delta={summary.aiHandledRateDelta}
          deltaKey="aiHandledRate"
        />
        <StatCard
          label="Escalation Rate"
          value={`${summary.escalationRate}%`}
          delta={summary.escalationRateDelta}
          deltaKey="escalationRate"
        />
      </SimpleGrid>

      {/* Conversation volume chart */}
      <Paper p="lg" radius="md" withBorder>
        <Text fw={600} mb="md">
          Daily Conversation Volume (30 days)
        </Text>
        <ResponsiveContainer width="100%" height={320}>
          <AreaChart
            data={DAILY_VOLUMES}
            margin={{ top: 8, right: 8, left: -10, bottom: 0 }}
          >
            <defs>
              <linearGradient id="gradTotal" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={BRAND_RED} stopOpacity={0.15} />
                <stop offset="95%" stopColor={BRAND_RED} stopOpacity={0} />
              </linearGradient>
              <linearGradient id="gradBillable" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#2563EB" stopOpacity={0.12} />
                <stop offset="95%" stopColor="#2563EB" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="gradAI" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#059669" stopOpacity={0.12} />
                <stop offset="95%" stopColor="#059669" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="gradEscalated" x1="0" y1="0" x2="0" y2="1">
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
              fill="url(#gradTotal)"
              name="Total"
            />
            <Area
              type="monotone"
              dataKey="billable"
              stroke="#2563EB"
              strokeWidth={1.5}
              fill="url(#gradBillable)"
              name="Billable"
            />
            <Area
              type="monotone"
              dataKey="aiResolved"
              stroke="#059669"
              strokeWidth={1.5}
              fill="url(#gradAI)"
              name="AI Resolved"
            />
            <Area
              type="monotone"
              dataKey="escalated"
              stroke="#D97706"
              strokeWidth={1.5}
              fill="url(#gradEscalated)"
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

      {/* Bottom section: Recent Conversations + Top Intents */}
      <SimpleGrid cols={{ base: 1, md: 2 }} spacing="md">
        {/* Recent Conversations */}
        <Paper p="lg" radius="md" withBorder>
          <Text fw={600} mb="md">
            Recent Conversations
          </Text>
          <Stack gap="xs">
            {recentConversations.map((conv) => (
              <Paper
                key={conv.id}
                p="sm"
                radius="sm"
                style={{
                  border: `1px solid ${cardBorder}`,
                }}
              >
                <Group justify="space-between" mb={4}>
                  <Text size="sm" fw={600} lineClamp={1} style={{ flex: 1 }}>
                    {conv.customerName}
                  </Text>
                  <Badge
                    size="xs"
                    variant="light"
                    color={statusColorMap[conv.status] || 'gray'}
                  >
                    {conv.status}
                  </Badge>
                </Group>
                <Text size="xs" c="dimmed" lineClamp={1}>
                  {conv.subject}
                </Text>
                <Group justify="space-between" mt={4}>
                  <Text size="xs" c="dimmed">
                    {conv.messageCount} messages
                  </Text>
                  <Text size="xs" c="dimmed">
                    {new Date(conv.updatedAt).toLocaleTimeString([], {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </Text>
                </Group>
              </Paper>
            ))}
          </Stack>
        </Paper>

        {/* Top Intents */}
        <Paper p="lg" radius="md" withBorder>
          <Text fw={600} mb="md">
            Top Intents
          </Text>
          <Stack gap="xs">
            {INTENT_BREAKDOWN.map((intent) => (
              <Group
                key={intent.intent}
                justify="space-between"
                p="sm"
                style={{
                  border: `1px solid ${cardBorder}`,
                  borderRadius: 6,
                }}
              >
                <div style={{ flex: 1, minWidth: 0 }}>
                  <Group justify="space-between" mb={4}>
                    <Text size="sm" fw={500}>
                      {intent.intent}
                    </Text>
                    <Text size="xs" c="dimmed">
                      {intent.count}
                    </Text>
                  </Group>
                  <Box
                    style={{
                      height: 6,
                      borderRadius: 3,
                      backgroundColor: intentBarBg,
                      overflow: 'hidden',
                    }}
                  >
                    <Box
                      style={{
                        height: '100%',
                        width: `${intent.percentage}%`,
                        borderRadius: 3,
                        backgroundColor: BRAND_RED,
                        opacity: 0.7 + (intent.percentage / 100) * 0.3,
                      }}
                    />
                  </Box>
                </div>
                <Text size="xs" c="dimmed" w={32} ta="right">
                  {intent.trend === 'up' ? '\u2191' : intent.trend === 'down' ? '\u2193' : '\u2192'}
                </Text>
              </Group>
            ))}
          </Stack>
        </Paper>
      </SimpleGrid>
    </Stack>
  );
}
