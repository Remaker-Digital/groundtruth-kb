// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

import React from 'react';
import {
  Paper,
  Group,
  Stack,
  Title,
  Text,
  Badge,
  Button,
  Table,
  Progress,
  RingProgress,
  SimpleGrid,
  Divider,
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
import { USAGE_DASHBOARD, INVOICES } from '../../data/mockData';

const BRAND_RED = '#C41E2A';

const statusColorMap: Record<string, string> = {
  paid: 'green',
  pending: 'yellow',
  failed: 'red',
};

function formatChartDate(dateStr: string): string {
  const d = new Date(dateStr);
  return `${d.getMonth() + 1}/${d.getDate()}`;
}

function formatCurrency(amount: number): string {
  return `$${amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

// --- Stat card for usage overview ---
interface UsageStatProps {
  label: string;
  value: string;
  subtext?: string;
  progress?: number;
  progressColor?: string;
  ring?: boolean;
}

function UsageStat({ label, value, subtext, progress, progressColor = BRAND_RED, ring }: UsageStatProps) {
  return (
    <Paper p="lg" radius="md" withBorder>
      <Group justify="space-between" align="flex-start" wrap="nowrap">
        <Stack gap={4} style={{ flex: 1 }}>
          <Text size="xs" c="dimmed" tt="uppercase" fw={600}>
            {label}
          </Text>
          <Text size="xl" fw={700} lh={1}>
            {value}
          </Text>
          {subtext && (
            <Text size="xs" c="dimmed">
              {subtext}
            </Text>
          )}
          {progress !== undefined && !ring && (
            <Progress
              value={progress}
              color={progress > 90 ? 'red' : progress > 75 ? 'yellow' : progressColor}
              size="sm"
              radius="xl"
              mt={4}
            />
          )}
        </Stack>
        {ring && progress !== undefined && (
          <RingProgress
            size={56}
            thickness={5}
            roundCaps
            sections={[
              {
                value: progress,
                color: progress > 90 ? 'red' : progress > 75 ? 'yellow' : progressColor,
              },
            ]}
            label={
              <Text size="xs" ta="center" fw={600} lh={1}>
                {Math.round(progress)}%
              </Text>
            }
          />
        )}
      </Group>
    </Paper>
  );
}

// --- Pack card ---
interface PackCardProps {
  conversations: number;
  price: number;
  effectiveRate: string;
}

function PackCard({ conversations, price, effectiveRate }: PackCardProps) {
  return (
    <Paper p="lg" radius="md" withBorder style={{ textAlign: 'center' }}>
      <Text size="xl" fw={700} c={BRAND_RED}>
        {conversations.toLocaleString()}
      </Text>
      <Text size="sm" c="dimmed" mb={4}>
        conversations
      </Text>
      <Text size="lg" fw={700} mb={2}>
        {formatCurrency(price)}
      </Text>
      <Text size="xs" c="dimmed" mb="md">
        {effectiveRate}/conversation
      </Text>
      <Button variant="outline" color="brand" fullWidth>
        Purchase
      </Button>
    </Paper>
  );
}

export function BillingPage() {
  const usage = USAGE_DASHBOARD;
  const { currentPeriod, billing, dailyUsage } = usage;
  const computedColorScheme = useComputedColorScheme('dark');
  const isDark = computedColorScheme === 'dark';

  // Dark-mode-aware chart colors — Mazel design revision (2026-02-03 mockup)
  const gridStroke = isDark ? 'rgba(255,255,255,0.06)' : '#e9ecef';
  const axisTickFill = isDark ? '#5C5C5C' : '#868e96';
  const axisLineStroke = isDark ? '#272727' : '#dee2e6';
  const tooltipBg = isDark ? '#1f1f1f' : '#fff';
  const tooltipBorder = isDark ? '#272727' : '#dee2e6';
  const tooltipColor = isDark ? '#E0E0E0' : undefined;

  const estimatedInvoice = billing.monthlyBase + billing.currentOverage;

  return (
    <Stack gap="lg">
      {/* Page header */}
      <div>
        <Title order={2}>Billing & Usage</Title>
        <Text c="dimmed" size="sm">
          Manage your subscription and monitor usage
        </Text>
      </div>

      {/* Plan Card */}
      <Paper p="lg" radius="md" withBorder>
        <Group justify="space-between" align="flex-start" wrap="wrap">
          <Stack gap={6}>
            <Group gap="sm" align="center">
              <Text size="lg" fw={700}>
                Current Plan
              </Text>
              <Badge color="green" variant="filled" size="lg">
                {billing.plan}
              </Badge>
              <Badge color="green" variant="light" size="sm">
                Active
              </Badge>
            </Group>
            <Group gap="lg">
              <div>
                <Text size="xs" c="dimmed">Monthly Base</Text>
                <Text size="md" fw={600}>{formatCurrency(billing.monthlyBase)}/mo</Text>
              </div>
              <div>
                <Text size="xs" c="dimmed">Included Conversations</Text>
                <Text size="md" fw={600}>{currentPeriod.included.toLocaleString()}/mo</Text>
              </div>
              <div>
                <Text size="xs" c="dimmed">Overage Rate</Text>
                <Text size="md" fw={600}>$0.025/conv</Text>
              </div>
              <div>
                <Text size="xs" c="dimmed">Next Invoice</Text>
                <Text size="md" fw={600}>{formatDate(billing.nextInvoice)}</Text>
              </div>
            </Group>
          </Stack>
          <Group gap="sm">
            <Button variant="default">
              Change Plan
            </Button>
            <Button color="brand">
              Manage Subscription
            </Button>
          </Group>
        </Group>
      </Paper>

      {/* Usage Overview - 4 cards */}
      <SimpleGrid cols={{ base: 1, xs: 2, md: 4 }} spacing="md">
        <UsageStat
          label="Conversations Used"
          value={`${currentPeriod.used.toLocaleString()} / ${currentPeriod.included.toLocaleString()}`}
          subtext={`${currentPeriod.percentUsed}% of included allowance`}
          progress={currentPeriod.percentUsed}
          ring
          progressColor={BRAND_RED}
        />
        <UsageStat
          label="Pack Balance"
          value={`${currentPeriod.packBalance.toLocaleString()}`}
          subtext="remaining conversations"
        />
        <UsageStat
          label="Current Overage"
          value={formatCurrency(currentPeriod.overage)}
          subtext="No overage charges"
        />
        <UsageStat
          label="Estimated Invoice"
          value={formatCurrency(estimatedInvoice)}
          subtext={`Base: ${formatCurrency(billing.monthlyBase)} + Overage: ${formatCurrency(billing.currentOverage)}`}
        />
      </SimpleGrid>

      {/* Usage Chart */}
      <Paper p="lg" radius="md" withBorder>
        <Text fw={600} mb="md">
          Daily Usage (30 days)
        </Text>
        <ResponsiveContainer width="100%" height={280}>
          <AreaChart
            data={dailyUsage}
            margin={{ top: 8, right: 8, left: -10, bottom: 0 }}
          >
            <defs>
              <linearGradient id="gradBillingTotal" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={BRAND_RED} stopOpacity={0.15} />
                <stop offset="95%" stopColor={BRAND_RED} stopOpacity={0} />
              </linearGradient>
              <linearGradient id="gradBillingBillable" x1="0" y1="0" x2="0" y2="1">
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
              fill="url(#gradBillingTotal)"
              name="Total"
            />
            <Area
              type="monotone"
              dataKey="billable"
              stroke="#2563EB"
              strokeWidth={1.5}
              fill="url(#gradBillingBillable)"
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
      </Paper>

      {/* Conversation Packs */}
      <div>
        <Text size="lg" fw={600} mb={4}>
          Conversation Packs
        </Text>
        <Text size="sm" c="dimmed" mb="md">
          Pre-purchase conversations at a discounted rate. Packs are valid for 90 days.
        </Text>
        <SimpleGrid cols={{ base: 1, xs: 3 }} spacing="md">
          <PackCard conversations={1000} price={29} effectiveRate="$0.029" />
          <PackCard conversations={5000} price={99} effectiveRate="$0.020" />
          <PackCard conversations={20000} price={249} effectiveRate="$0.012" />
        </SimpleGrid>
      </div>

      {/* Invoice History */}
      <Paper p="lg" radius="md" withBorder>
        <Text fw={600} mb="md">
          Invoice History
        </Text>
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Date</Table.Th>
              <Table.Th>Description</Table.Th>
              <Table.Th style={{ textAlign: 'right' }}>Amount</Table.Th>
              <Table.Th>Status</Table.Th>
              <Table.Th style={{ textAlign: 'right' }}>Invoice</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {INVOICES.map((invoice) => (
              <Table.Tr key={invoice.id}>
                <Table.Td>
                  <Text size="sm">{formatDate(invoice.date)}</Text>
                </Table.Td>
                <Table.Td>
                  <Text size="sm">{invoice.description}</Text>
                </Table.Td>
                <Table.Td style={{ textAlign: 'right' }}>
                  <Text size="sm" fw={500}>
                    {formatCurrency(invoice.amount)}
                  </Text>
                </Table.Td>
                <Table.Td>
                  <Badge
                    size="sm"
                    variant="light"
                    color={statusColorMap[invoice.status] || 'gray'}
                  >
                    {invoice.status}
                  </Badge>
                </Table.Td>
                <Table.Td style={{ textAlign: 'right' }}>
                  <Button
                    variant="subtle"
                    size="xs"
                    color="brand"
                    component="a"
                    href={invoice.pdfUrl}
                  >
                    Download
                  </Button>
                </Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      </Paper>
    </Stack>
  );
}
