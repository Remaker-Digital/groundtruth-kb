// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

/**
 * Billing & Usage page — Standalone admin.
 *
 * Adapted from the prototype BillingPage with API hooks replacing mock data.
 * Uses flat UsageDashboard + DailyVolume API types from shared hooks.
 * Invoice history table replaced with Stripe portal "Manage Billing" button.
 *
 * Four-tier dark mode hierarchy (designer-approved):
 *   chrome #0a0a0a -> page #141414 -> surface #1f1f1f -> border #272727
 */

import React, { useCallback } from 'react';
import {
  Paper,
  Group,
  Stack,
  Title,
  Text,
  Badge,
  Button,
  Progress,
  RingProgress,
  SimpleGrid,
  Box,
  Loader,
  Alert,
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
import { useUsageDashboard, useDailyVolume } from '../../shared/hooks/index';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const BRAND_RED = '#ff3621';

const TIER_LABELS: Record<string, string> = {
  trial: 'Trial',
  starter: 'Starter',
  professional: 'Professional',
  enterprise: 'Enterprise',
};

const TIER_BADGE_COLORS: Record<string, string> = {
  trial: 'yellow',
  starter: 'blue',
  professional: 'green',
  enterprise: 'grape',
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatChartDate(dateStr: string): string {
  const d = new Date(dateStr);
  return `${d.getMonth() + 1}/${d.getDate()}`;
}

function formatCurrency(amount: number | null | undefined): string {
  if (amount == null) return '$0.00';
  return `$${amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function formatNumber(n: number | null | undefined): string {
  if (n == null) return '0';
  return n.toLocaleString('en-US');
}

// ---------------------------------------------------------------------------
// UsageStat card
// ---------------------------------------------------------------------------

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
              value={Math.min(progress, 100)}
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
                value: Math.min(progress, 100),
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

// ---------------------------------------------------------------------------
// PackCard
// ---------------------------------------------------------------------------

interface PackCardProps {
  conversations: number;
  price: number;
  effectiveRate: string;
  onPurchase: () => void;
  purchasing: boolean;
}

function PackCard({ conversations, price, effectiveRate, onPurchase, purchasing }: PackCardProps) {
  return (
    <Paper p="lg" radius="md" withBorder style={{ textAlign: 'center' }}>
      <Text size="xl" fw={700} c={BRAND_RED}>
        {(conversations ?? 0).toLocaleString()}
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
      <Button
        variant="outline"
        color="brand"
        fullWidth
        onClick={onPurchase}
        loading={purchasing}
        disabled={purchasing}
      >
        Purchase
      </Button>
    </Paper>
  );
}

// ---------------------------------------------------------------------------
// BillingPage
// ---------------------------------------------------------------------------

export const BillingPage: React.FC = () => {
  const { apiFetch, tenantContext, onNotify } = useAppContext();
  const usage = useUsageDashboard(apiFetch);
  const dailyVolume = useDailyVolume(apiFetch);
  const [purchasingPack, setPurchasingPack] = React.useState<number | null>(null);

  const computedColorScheme = useComputedColorScheme('dark');
  const isDark = computedColorScheme === 'dark';

  // Dark-mode-aware chart colors — Mazel design revision (2026-02-03 mockup)
  const gridStroke = isDark ? 'rgba(255,255,255,0.06)' : '#e9ecef';
  const axisTickFill = isDark ? '#5C5C5C' : '#868e96';
  const axisLineStroke = isDark ? '#272727' : '#dee2e6';
  const tooltipBg = isDark ? '#1f1f1f' : '#fff';
  const tooltipBorder = isDark ? '#272727' : '#dee2e6';
  const tooltipColor = isDark ? '#E0E0E0' : undefined;

  // Extract usage fields with null safety
  const totalConversations = usage.data?.totalConversations ?? 0;
  const includedAllowance = usage.data?.includedAllowance ?? 0;
  const remainingIncluded = usage.data?.remainingIncluded ?? 0;
  const packBalance = usage.data?.packBalance ?? 0;
  const overageConversations = usage.data?.overageConversations ?? 0;
  const usagePercent = usage.data?.usagePercent ?? 0;
  const estimatedOverageCost = usage.data?.estimatedOverageCost ?? 0;

  // Tier from tenant context
  const tier = tenantContext?.tier ?? 'starter';
  const tierLabel = TIER_LABELS[tier] || tier;
  const tierBadgeColor = TIER_BADGE_COLORS[tier] || 'gray';

  // Chart data from daily volume hook
  const chartData = dailyVolume.data?.days ?? [];

  // --- Callbacks ---

  const handleManageSubscription = useCallback(async () => {
    try {
      const resp = await apiFetch('/api/billing/portal', { method: 'POST' });
      if (!resp.ok) throw new Error('Failed to create portal session');
      const data = await resp.json();
      if (data.url) {
        window.open(data.url, '_blank');
      }
    } catch {
      onNotify('Failed to open billing portal. Please try again.', 'error');
    }
  }, [apiFetch, onNotify]);

  const handleManageBilling = useCallback(async () => {
    try {
      const resp = await apiFetch('/api/billing/portal', { method: 'POST' });
      if (!resp.ok) throw new Error('Failed to create portal session');
      const data = await resp.json();
      if (data.url) {
        window.open(data.url, '_blank');
      }
    } catch {
      onNotify('Failed to open billing portal. Please try again.', 'error');
    }
  }, [apiFetch, onNotify]);

  const handlePurchasePack = useCallback(
    async (packSize: number) => {
      setPurchasingPack(packSize);
      try {
        const resp = await apiFetch('/api/packs/purchase', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ pack_size: packSize }),
        });
        if (!resp.ok) throw new Error('Purchase failed');
        const data = await resp.json();
        if (data.url) {
          window.location.href = data.url;
        }
      } catch {
        onNotify('Failed to start purchase. Please try again.', 'error');
      } finally {
        setTimeout(() => setPurchasingPack(null), 1000);
      }
    },
    [apiFetch, onNotify],
  );

  // --- Loading state ---

  if (usage.loading && !usage.data) {
    return (
      <Stack gap="lg">
        <div>
          <Title order={2}>Billing & Usage</Title>
          <Text c="dimmed" size="sm">Manage your subscription and monitor usage</Text>
        </div>
        <Group justify="center" py="xl">
          <Loader size="md" />
        </Group>
      </Stack>
    );
  }

  // --- Render ---

  return (
    <Stack gap="lg">
      {/* Page header */}
      <div>
        <Title order={2}>Billing & Usage</Title>
        <Text c="dimmed" size="sm">
          Manage your subscription and monitor usage
        </Text>
      </div>

      {/* Error alert */}
      {usage.error && (
        <Alert color="red" variant="light" title="Usage data unavailable">
          {usage.error}
        </Alert>
      )}

      {/* Plan Card */}
      <Paper p="lg" radius="md" withBorder>
        <Group justify="space-between" align="flex-start" wrap="wrap">
          <Stack gap={6}>
            <Group gap="sm" align="center">
              <Text size="lg" fw={700}>
                Current Plan
              </Text>
              <Badge color={tierBadgeColor} variant="filled" size="lg" tt="capitalize">
                {tierLabel}
              </Badge>
              <Badge color="green" variant="light" size="sm">
                {tenantContext?.status === 'active' ? 'Active' : (tenantContext?.status ?? 'Active')}
              </Badge>
            </Group>
            <Group gap="lg">
              <div>
                <Text size="xs" c="dimmed">Included Conversations</Text>
                <Text size="md" fw={600}>{formatNumber(includedAllowance)}/mo</Text>
              </div>
              <div>
                <Text size="xs" c="dimmed">Used This Period</Text>
                <Text size="md" fw={600}>{formatNumber(totalConversations)}</Text>
              </div>
              <div>
                <Text size="xs" c="dimmed">Remaining</Text>
                <Text size="md" fw={600}>{formatNumber(remainingIncluded)}</Text>
              </div>
            </Group>
          </Stack>
          <Button color="brand" onClick={handleManageSubscription}>
            Manage Subscription
          </Button>
        </Group>
      </Paper>

      {/* Usage Overview - 4 cards */}
      <SimpleGrid cols={{ base: 1, xs: 2, md: 4 }} spacing="md">
        <UsageStat
          label="Conversations Used"
          value={`${formatNumber(totalConversations)} / ${formatNumber(includedAllowance)}`}
          subtext={`${Math.round(usagePercent)}% of included allowance`}
          progress={usagePercent}
          ring
          progressColor={BRAND_RED}
        />
        <UsageStat
          label="Pack Balance"
          value={formatNumber(packBalance)}
          subtext="remaining conversations"
        />
        <UsageStat
          label="Current Overage"
          value={formatCurrency(estimatedOverageCost)}
          subtext={overageConversations > 0
            ? `${formatNumber(overageConversations)} overage conversations`
            : 'No overage charges'
          }
        />
        <UsageStat
          label="Estimated Overage Cost"
          value={formatCurrency(estimatedOverageCost)}
          subtext="Additional charges this period"
        />
      </SimpleGrid>

      {/* Active Alerts */}
      {(usage.data?.activeAlerts ?? []).length > 0 && (
        <Alert color="yellow" variant="light" title="Usage Alerts">
          <Stack gap={4}>
            {(usage.data?.activeAlerts ?? []).map((alert, i) => (
              <Text key={i} size="sm">{alert}</Text>
            ))}
          </Stack>
        </Alert>
      )}

      {/* Usage Chart */}
      <Paper p="lg" radius="md" withBorder>
        <Text fw={600} mb="md">
          Daily Usage (30 days)
        </Text>
        {dailyVolume.loading && !chartData.length ? (
          <Group justify="center" py="xl">
            <Loader size="sm" />
          </Group>
        ) : chartData.length === 0 ? (
          <Text size="sm" c="dimmed" ta="center" py="xl">
            No usage data available yet
          </Text>
        ) : (
          <>
            <ResponsiveContainer width="100%" height={280}>
              <AreaChart
                data={chartData}
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
          </>
        )}
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
          <PackCard
            conversations={1000}
            price={29}
            effectiveRate="$0.029"
            onPurchase={() => handlePurchasePack(1000)}
            purchasing={purchasingPack === 1000}
          />
          <PackCard
            conversations={5000}
            price={99}
            effectiveRate="$0.020"
            onPurchase={() => handlePurchasePack(5000)}
            purchasing={purchasingPack === 5000}
          />
          <PackCard
            conversations={20000}
            price={249}
            effectiveRate="$0.012"
            onPurchase={() => handlePurchasePack(20000)}
            purchasing={purchasingPack === 20000}
          />
        </SimpleGrid>
      </div>

      {/* Manage Billing (replaces Invoice History table) */}
      <Paper p="lg" radius="md" withBorder>
        <Group justify="space-between" align="center">
          <div>
            <Text fw={600}>Invoices & Payment Methods</Text>
            <Text size="sm" c="dimmed">
              View invoice history, update payment methods, and manage your subscription through Stripe.
            </Text>
          </div>
          <Button color="brand" size="md" onClick={handleManageBilling}>
            Manage Billing
          </Button>
        </Group>
      </Paper>
    </Stack>
  );
};
