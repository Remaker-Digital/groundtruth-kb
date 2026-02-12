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
  Skeleton,
  Table,
  Progress,
  SegmentedControl,
  Divider,
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
  useInboxConversations,
  useIntentBreakdown,
  useKnowledgeGaps,
} from '../../shared/hooks/index';
import { HelpTooltip } from '../../shared/HelpTooltip';

const BRAND_RED = '#ff3621';

const statusColorMap: Record<string, string> = {
  active: 'blue',
  idle: 'yellow',
  ended: 'green',
  escalated: 'red',
};

// ---------------------------------------------------------------------------
// StatCard — label + value + optional detail
// ---------------------------------------------------------------------------

interface StatCardProps {
  label: React.ReactNode;
  value: string;
  detail?: string;
  loading?: boolean;
}

function StatCard({ label, value, detail, loading }: StatCardProps) {
  return (
    <Paper p="lg" radius="md" withBorder>
      <Text size="xs" c="dimmed" fw={600} mb={4}>
        {label}
      </Text>
      {loading ? (
        <Skeleton height={28} width="60%" />
      ) : (
        <Text size="xl" fw={700} lh={1}>
          {value}
        </Text>
      )}
      {detail && !loading && (
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

function formatResponseTime(ms: number | null | undefined): string {
  if (ms == null) return '--';
  return `${ms}s`;
}

function formatSatisfaction(val: number | null | undefined): string {
  if (val == null) return '--';
  return `${val}/5`;
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
// DashboardPage — combined overview + analytics
// ---------------------------------------------------------------------------

const DOCS_BASE = 'https://agentredcx.com/docs/admin-guide';

export function DashboardPage() {
  const { apiFetch, tenantContext } = useAppContext();

  // Analytics filters
  const [period, setPeriod] = useState('30d');
  const [modeFilter, setModeFilter] = useState<'all' | 'production' | 'test'>('all');
  const isTestMode = modeFilter === 'test' ? true : modeFilter === 'production' ? false : undefined;

  // Data hooks
  const summary = useAnalyticsSummary(apiFetch, isTestMode);
  const dailyVolume = useDailyVolume(apiFetch);
  const conversations = useInboxConversations(apiFetch);
  const intents = useIntentBreakdown(apiFetch, isTestMode);
  const gaps = useKnowledgeGaps(apiFetch, isTestMode);

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
  const gapList = gaps.data?.gaps ?? [];

  const summaryLoading = summary.loading;
  const s = summary.data;

  return (
    <Stack gap="lg">
      {/* Page header */}
      <Group justify="space-between" align="flex-end">
        <div>
          {tenantContext?.shopDomain && (
            <Text size="lg" fw={700} c="gray.3" mb={2}>
              {tenantContext.shopDomain.replace('.myshopify.com', '')}
            </Text>
          )}
          <Title order={2}>Dashboard</Title>
          <Text c="dimmed" size="sm">
            Overview of your customer experience performance
          </Text>
        </div>
        <Group gap="md">
          <SegmentedControl
            value={modeFilter}
            onChange={(val) => setModeFilter(val as 'all' | 'production' | 'test')}
            data={[
              { label: 'All', value: 'all' },
              { label: 'Production', value: 'production' },
              { label: 'Test', value: 'test' },
            ]}
            size="sm"
          />
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

      {/* Test mode filter indicator */}
      {modeFilter !== 'all' && (
        <Paper p="xs" radius="md" withBorder style={{
          borderColor: modeFilter === 'test' ? 'rgba(255, 152, 0, 0.3)' : undefined,
          background: modeFilter === 'test'
            ? 'linear-gradient(135deg, rgba(255, 152, 0, 0.08) 0%, rgba(255, 87, 34, 0.04) 100%)'
            : undefined,
        }}>
          <Group gap="xs" justify="center">
            <Badge size="sm" variant="light" color={modeFilter === 'test' ? 'orange' : 'blue'}>
              {modeFilter === 'test' ? 'Test mode' : 'Production'}
            </Badge>
            <Text size="xs" c="dimmed">
              {modeFilter === 'test'
                ? 'Showing metrics from test configuration sessions only'
                : 'Showing metrics from production sessions only'}
            </Text>
          </Group>
        </Paper>
      )}

      {/* Stat cards — 5 cards with detail sub-labels + help tooltips (WI #259) */}
      <SimpleGrid cols={{ base: 1, xs: 2, md: 3 }} spacing="md">
        <StatCard
          label={<>Total conversations <HelpTooltip text="All conversations started in the selected period, including billable and non-billable." docLink={`${DOCS_BASE}/analytics`} /></>}
          value={(s?.totalConversations ?? 0).toLocaleString()}
          detail={s ? `Billable: ${(s.billableConversations ?? 0).toLocaleString()}` : undefined}
          loading={summaryLoading}
        />
        <StatCard
          label={<>Avg response time <HelpTooltip text="Average time for the AI to generate a complete response, measured from message received to response delivered." docLink={`${DOCS_BASE}/analytics`} /></>}
          value={formatResponseTime(s?.avgResponseTime)}
          loading={summaryLoading}
        />
        <StatCard
          label={<>Resolution rate <HelpTooltip text="Percentage of conversations resolved by the AI without human escalation." docLink={`${DOCS_BASE}/analytics`} /></>}
          value={s?.resolutionRate != null ? `${(s.resolutionRate * 100).toFixed(1)}%` : '--'}
          detail={
            s != null
              ? `${Math.round(s.totalConversations * (s.resolutionRate ?? 0)).toLocaleString()} resolved`
              : undefined
          }
          loading={summaryLoading}
        />
        <StatCard
          label={<>Customer satisfaction <HelpTooltip text="Average customer rating on a 1-5 scale, collected via post-conversation feedback." docLink={`${DOCS_BASE}/analytics`} /></>}
          value={formatSatisfaction(s?.customerSatisfaction)}
          loading={summaryLoading}
        />
        <StatCard
          label={<>Escalation rate <HelpTooltip text="Percentage of conversations handed off to a human team member." docLink={`${DOCS_BASE}/analytics`} /></>}
          value={s?.escalationRate != null ? `${(s.escalationRate * 100).toFixed(1)}%` : '--'}
          detail={
            s != null
              ? `${(s.escalationCount ?? 0).toLocaleString()} escalated`
              : undefined
          }
          loading={summaryLoading}
        />
      </SimpleGrid>

      {/* Conversation volume chart */}
      <Paper p="lg" radius="md" withBorder>
        <Group justify="space-between" mb="md">
          <Text fw={600}>Conversation volume <HelpTooltip text="Daily breakdown of total and billable conversations over the selected time period." docLink={`${DOCS_BASE}/analytics`} /></Text>
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
        {dailyVolume.loading ? (
          <Skeleton height={320} />
        ) : chartData.length > 0 ? (
          <>
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
          </>
        ) : (
          <Group justify="center" py="xl">
            <Text size="sm" c="dimmed">No volume data available</Text>
          </Group>
        )}
      </Paper>

      {/* Recent Conversations + Top Intents side-by-side */}
      <SimpleGrid cols={{ base: 1, md: 2 }} spacing="md">
        {/* Recent Conversations */}
        <Paper p="lg" radius="md" withBorder>
          <Text fw={600} mb="md">
            Recent conversations <HelpTooltip text="The 5 most recent customer conversations with status and assignment info." docLink={`${DOCS_BASE}/conversations`} />
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

        {/* Top Intents (compact) */}
        <Paper p="lg" radius="md" withBorder>
          <Text fw={600} mb="md">
            Top intents <HelpTooltip text="Most frequently detected customer intents, ranked by conversation count." docLink={`${DOCS_BASE}/analytics`} />
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

      {/* Divider between overview and detailed analytics */}
      <Divider label="Detailed analytics" labelPosition="center" />

      {/* Intent Breakdown Table — full-width, 3 columns */}
      <Paper p="lg" radius="md" withBorder>
        <Text fw={600} mb="md">
          Intent breakdown <HelpTooltip text="Full table of all detected intents with count and distribution percentage." docLink={`${DOCS_BASE}/analytics`} />
        </Text>
        {intentList.length > 0 ? (
          <Table striped highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Intent</Table.Th>
                <Table.Th style={{ width: 80 }}>Count</Table.Th>
                <Table.Th style={{ width: 200 }}>Distribution</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {intentList.map((intent) => (
                <Table.Tr key={intent.agent}>
                  <Table.Td>
                    <Text size="sm" fw={500}>
                      {intent.agent}
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
            {intents.loading ? 'Loading intent data...' : 'No intent data available'}
          </Text>
        )}
      </Paper>

      {/* Knowledge Gaps */}
      <Paper p="lg" radius="md" withBorder>
        <Group justify="space-between" mb="md">
          <div>
            <Text fw={600}>Knowledge gaps <HelpTooltip text="Conversations where the AI lacked sufficient knowledge to fully resolve the query. Add KB entries to address these gaps." docLink={`${DOCS_BASE}/knowledge-base`} /></Text>
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
}
