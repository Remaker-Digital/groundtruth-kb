// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

import React from 'react';
import {
  Paper,
  Group,
  Stack,
  Text,
  Badge,
  SimpleGrid,
  Title,
  Box,
  Skeleton,
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
  useInboxConversations,
  useIntentBreakdown,
} from '../../shared/hooks/index';

const BRAND_RED = '#ff3621';

const statusColorMap: Record<string, string> = {
  active: 'blue',
  idle: 'yellow',
  ended: 'green',
  escalated: 'red',
};

// ---------------------------------------------------------------------------
// StatCard — label + value only (no delta badge)
// ---------------------------------------------------------------------------

interface StatCardProps {
  label: string;
  value: string;
  loading?: boolean;
}

function StatCard({ label, value, loading }: StatCardProps) {
  return (
    <Paper p="lg" radius="md" withBorder>
      <Text size="xs" c="dimmed" tt="uppercase" fw={600} mb={4}>
        {label}
      </Text>
      {loading ? (
        <Skeleton height={28} width="60%" />
      ) : (
        <Text size="xl" fw={700} lh={1}>
          {value}
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

function formatResponseTime(ms: number | null | undefined): string {
  if (ms == null) return '--';
  return `${ms}s`;
}

function formatPercent(val: number | null | undefined): string {
  if (val == null) return '--';
  return `${(val * 100).toFixed(1)}%`;
}

function formatSatisfaction(val: number | null | undefined): string {
  if (val == null) return '--';
  return `${val}/5`;
}

// ---------------------------------------------------------------------------
// DashboardPage
// ---------------------------------------------------------------------------

export function DashboardPage() {
  const { apiFetch } = useAppContext();
  const summary = useAnalyticsSummary(apiFetch);
  const dailyVolume = useDailyVolume(apiFetch);
  const conversations = useInboxConversations(apiFetch);
  const intents = useIntentBreakdown(apiFetch);

  const computedColorScheme = useComputedColorScheme('dark');
  const isDark = computedColorScheme === 'dark';

  // Dark-mode-aware chart colors — Mazel design revision (2026-02-03 mockup)
  const gridStroke = isDark ? 'rgba(255,255,255,0.06)' : '#e9ecef';
  const axisTickFill = isDark ? '#5C5C5C' : '#868e96';
  const axisLineStroke = isDark ? '#272727' : '#dee2e6';
  const tooltipBg = isDark ? '#1f1f1f' : '#fff';
  const tooltipBorder = isDark ? '#272727' : '#dee2e6';
  const tooltipColor = isDark ? '#E0E0E0' : undefined;
  const intentBarBg = isDark ? 'rgba(255,255,255,0.06)' : '#f1f3f5';
  const cardBorder = isDark ? '#272727' : 'var(--mantine-color-gray-2)';

  const recentConversations = (conversations.data?.conversations ?? []).slice(0, 5);
  const intentList = intents.data?.intents ?? [];
  const chartData = dailyVolume.data?.days ?? [];

  const summaryLoading = summary.loading;
  const s = summary.data;

  return (
    <Stack gap="lg">
      {/* Page header */}
      <div>
        <Title order={2}>Dashboard</Title>
        <Text c="dimmed" size="sm">
          Overview of your customer experience performance
        </Text>
      </div>

      {/* Stat cards — 5 cards, 3 columns */}
      <SimpleGrid cols={{ base: 1, xs: 2, md: 3 }} spacing="md">
        <StatCard
          label="Total Conversations"
          value={(s?.totalConversations ?? 0).toLocaleString()}
          loading={summaryLoading}
        />
        <StatCard
          label="Avg Response Time"
          value={formatResponseTime(s?.avgResponseTime)}
          loading={summaryLoading}
        />
        <StatCard
          label="Resolution Rate"
          value={s?.resolutionRate != null ? `${(s.resolutionRate * 100).toFixed(1)}%` : '--'}
          loading={summaryLoading}
        />
        <StatCard
          label="Customer Satisfaction"
          value={formatSatisfaction(s?.customerSatisfaction)}
          loading={summaryLoading}
        />
        <StatCard
          label="Escalation Rate"
          value={s?.escalationRate != null ? `${(s.escalationRate * 100).toFixed(1)}%` : '--'}
          loading={summaryLoading}
        />
      </SimpleGrid>

      {/* Conversation volume chart */}
      <Paper p="lg" radius="md" withBorder>
        <Text fw={600} mb="md">
          Daily Conversation Volume (30 days)
        </Text>
        {dailyVolume.loading ? (
          <Skeleton height={320} />
        ) : (
          <ResponsiveContainer width="100%" height={320}>
            <AreaChart
              data={chartData}
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
            </AreaChart>
          </ResponsiveContainer>
        )}
        {/* Legend */}
        <Group gap="lg" mt="xs" justify="center">
          {[
            { color: BRAND_RED, label: 'Total' },
            { color: '#2563EB', label: 'Billable' },
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
          {conversations.loading ? (
            <Stack gap="xs">
              {[1, 2, 3, 4, 5].map((i) => (
                <Skeleton key={i} height={60} radius="sm" />
              ))}
            </Stack>
          ) : recentConversations.length === 0 ? (
            <Text size="sm" c="dimmed" ta="center" py="xl">
              No conversations yet
            </Text>
          ) : (
            <Stack gap="xs">
              {recentConversations.map((conv) => (
                <Paper
                  key={conv.conversationId}
                  p="sm"
                  radius="sm"
                  style={{
                    border: `1px solid ${cardBorder}`,
                  }}
                >
                  <Group justify="space-between" mb={4}>
                    <Text size="sm" fw={600} lineClamp={1} style={{ flex: 1 }}>
                      {conv.customerName ?? 'Unknown Customer'}
                    </Text>
                    <Badge
                      size="xs"
                      variant="light"
                      color={statusColorMap[conv.status ?? ''] || 'gray'}
                    >
                      {conv.status}
                    </Badge>
                  </Group>
                  <Text size="xs" c="dimmed" lineClamp={1}>
                    {conv.messageCount ?? 0} messages
                  </Text>
                  <Group justify="space-between" mt={4}>
                    <Text size="xs" c="dimmed">
                      {conv.status === 'escalated'
                        ? 'Escalated'
                        : conv.assignedTo
                          ? `Assigned: ${conv.assignedTo}`
                          : 'Unassigned'}
                    </Text>
                    <Text size="xs" c="dimmed">
                      {conv.lastActivityAt != null
                        ? new Date(conv.lastActivityAt).toLocaleTimeString([], {
                            hour: '2-digit',
                            minute: '2-digit',
                          })
                        : '--'}
                    </Text>
                  </Group>
                </Paper>
              ))}
            </Stack>
          )}
        </Paper>

        {/* Top Intents */}
        <Paper p="lg" radius="md" withBorder>
          <Text fw={600} mb="md">
            Top Intents
          </Text>
          {intents.loading ? (
            <Stack gap="xs">
              {[1, 2, 3, 4, 5].map((i) => (
                <Skeleton key={i} height={48} radius="sm" />
              ))}
            </Stack>
          ) : intentList.length === 0 ? (
            <Text size="sm" c="dimmed" ta="center" py="xl">
              No intent data available
            </Text>
          ) : (
            <Stack gap="xs">
              {intentList.map((intent) => (
                <Group
                  key={intent.agent}
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
                        {intent.agent}
                      </Text>
                      <Text size="xs" c="dimmed">
                        {(intent.invocationCount ?? 0).toLocaleString()}
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
                          width: `${intent.percentage ?? 0}%`,
                          borderRadius: 3,
                          backgroundColor: BRAND_RED,
                          opacity: 0.7 + ((intent.percentage ?? 0) / 100) * 0.3,
                        }}
                      />
                    </Box>
                  </div>
                </Group>
              ))}
            </Stack>
          )}
        </Paper>
      </SimpleGrid>
    </Stack>
  );
}
