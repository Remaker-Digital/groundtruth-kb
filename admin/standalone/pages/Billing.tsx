// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

/**
 * Billing & usage page — Standalone admin.
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
import { HelpTooltip } from '../../shared/HelpTooltip';

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

const ADDON_MODULES = [
  { id: 'addon_multi_language', label: 'Multi-Language Pack', description: 'Serve customers in Spanish, French, Portuguese, and more with automatic language detection.', price: 99, availableOn: ['starter', 'professional', 'enterprise'], tierLabel: 'All tiers' },
  { id: 'addon_advanced_analytics', label: 'Advanced Analytics', description: 'Deep conversation analytics, topic clustering, sentiment trends, and exportable reports.', price: 149, availableOn: ['professional', 'enterprise'], tierLabel: 'Professional+' },
  { id: 'addon_mailchimp', label: 'Mailchimp Integration', description: 'Sync customer interactions and segments directly to your Mailchimp audience lists.', price: 49, availableOn: ['professional', 'enterprise'], tierLabel: 'Professional+' },
  { id: 'addon_google_analytics', label: 'Google Analytics', description: 'Send conversation events and widget engagement data to your GA4 property.', price: 49, availableOn: ['professional', 'enterprise'], tierLabel: 'Professional+' },
  { id: 'addon_custom_integration', label: 'Custom Integration', description: 'Connect to your custom systems with a dedicated integration built by our team.', price: 299, availableOn: ['enterprise'], tierLabel: 'Enterprise' },
];

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
  tooltip?: string;
}

function UsageStat({ label, value, subtext, progress, progressColor = BRAND_RED, ring, tooltip }: UsageStatProps) {
  return (
    <Paper p="lg" radius="md" withBorder>
      <Group justify="space-between" align="flex-start" wrap="nowrap">
        <Stack gap={4} style={{ flex: 1 }}>
          <Text size="xs" c="dimmed" fw={600}>
            {label}{tooltip && <HelpTooltip text={tooltip} />}
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
        onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.background = 'rgba(255, 255, 255, 0.06)'; }}
        onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = ''; }}
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

  const handleOpenPortal = useCallback(async () => {
    try {
      const resp = await apiFetch('/api/billing/portal', { method: 'POST' });
      if (!resp.ok) throw new Error('Failed to create portal session');
      const data = await resp.json();
      if (data.portal_url) {
        window.open(data.portal_url, '_blank');
      }
    } catch {
      onNotify('Failed to open billing portal. Please try again.', 'error');
    }
  }, [apiFetch, onNotify]);

  // Alias for backwards-compatible references in the template
  const handleManageSubscription = handleOpenPortal;
  const handleManageBilling = handleOpenPortal;

  const PACK_ID_MAP: Record<number, string> = { 1000: 'pack_1k', 5000: 'pack_5k', 20000: 'pack_20k' };

  const handlePurchasePack = useCallback(
    async (packSize: number) => {
      setPurchasingPack(packSize);
      try {
        const resp = await apiFetch('/api/packs/purchase', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            pack_id: PACK_ID_MAP[packSize],
            tenant_id: tenantContext?.tenantId,
          }),
        });
        if (!resp.ok) throw new Error('Purchase failed');
        const data = await resp.json();
        if (data.checkout_url) {
          window.location.href = data.checkout_url;
        }
      } catch {
        onNotify('Failed to start purchase. Please try again.', 'error');
      } finally {
        setTimeout(() => setPurchasingPack(null), 1000);
      }
    },
    [apiFetch, onNotify, tenantContext],
  );

  // --- Loading state ---

  if (usage.loading && !usage.data) {
    return (
      <Stack gap="lg">
        <div>
          <Title order={2}>Billing & usage</Title>
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
        <Title order={2}>Billing & usage</Title>
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
                Current plan<HelpTooltip text="Your active subscription tier determines your included monthly conversations, overage rate, and available features." docLink="https://agentredcx.com/docs/billing/overview#your-subscription-plan" />
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
                <Text size="xs" c="dimmed">Included conversations</Text>
                <Text size="md" fw={600}>{formatNumber(includedAllowance)}/mo</Text>
              </div>
              <div>
                <Text size="xs" c="dimmed">Used this period</Text>
                <Text size="md" fw={600}>{formatNumber(totalConversations)}</Text>
              </div>
              <div>
                <Text size="xs" c="dimmed">Remaining</Text>
                <Text size="md" fw={600}>{formatNumber(remainingIncluded)}</Text>
              </div>
            </Group>
          </Stack>
          {tenantContext?.hasStripeBilling && (
            <Button color="brand" onClick={handleManageSubscription}>
              Manage subscription
            </Button>
          )}
        </Group>
      </Paper>

      {/* Usage Overview - 4 cards */}
      <SimpleGrid cols={{ base: 1, xs: 2, md: 4 }} spacing="md">
        <UsageStat
          label="Conversations used"
          tooltip="Total conversations this billing period vs. your plan's included monthly allowance."
          value={`${formatNumber(totalConversations)} / ${formatNumber(includedAllowance)}`}
          subtext={`${Math.round(usagePercent)}% of included allowance`}
          progress={usagePercent}
          ring
          progressColor={BRAND_RED}
        />
        <UsageStat
          label="Pack balance"
          tooltip="Remaining conversations from pre-purchased packs. Packs are used after your included allowance is depleted and before overage billing begins."
          value={formatNumber(packBalance)}
          subtext="remaining conversations"
        />
        <UsageStat
          label="Current overage"
          tooltip="Conversations beyond your included allowance and pack balance. Overage is billed at your plan's per-conversation rate."
          value={formatCurrency(estimatedOverageCost)}
          subtext={overageConversations > 0
            ? `${formatNumber(overageConversations)} overage conversations`
            : 'No overage charges'
          }
        />
        <UsageStat
          label="Estimated overage cost"
          tooltip="Projected additional charges for overage conversations this billing period."
          value={formatCurrency(estimatedOverageCost)}
          subtext="Additional charges this period"
        />
      </SimpleGrid>

      {/* Active Alerts */}
      {(usage.data?.activeAlerts ?? []).length > 0 && (
        <Alert color="yellow" variant="light" title="Usage alerts">
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
          Daily usage (30 days)<HelpTooltip text="Number of billable conversations per day over the last 30 days. Helps identify usage trends and peak periods." docLink="https://agentredcx.com/docs/billing/overview#usage-dashboard" />
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
          Conversation packs<HelpTooltip text="Pre-purchase conversation bundles at discounted rates. Pack conversations are consumed after your included allowance and before overage billing. Valid for 90 days, FIFO usage order." docLink="https://agentredcx.com/docs/billing/overview#conversation-packs" />
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

      {/* Add-on Modules */}
      <div>
        <Text size="lg" fw={600} mb={4}>
          Add-on modules<HelpTooltip text="Optional feature modules that extend your plan. Add-on subscriptions are billed monthly alongside your base plan." docLink="https://agentredcx.com/docs/billing/overview#add-on-modules" />
        </Text>
        <Text size="sm" c="dimmed" mb="md">
          Enhance your plan with additional capabilities. Billed monthly.
        </Text>
        <SimpleGrid cols={{ base: 1, xs: 2, md: 3 }} spacing="md">
          {ADDON_MODULES.map((addon) => {
            const tierMet = addon.availableOn.includes(tier);
            return (
              <Paper key={addon.id} p="lg" radius="md" withBorder style={{ opacity: tierMet ? 1 : 0.65 }}>
                <Group justify="space-between" mb={6}>
                  <Text size="md" fw={600}>{addon.label}</Text>
                  <Badge
                    color={addon.tierLabel === 'All tiers' ? 'green' : addon.tierLabel === 'Enterprise' ? 'grape' : 'blue'}
                    variant="light"
                    size="xs"
                  >
                    {addon.tierLabel}
                  </Badge>
                </Group>
                <Text size="xs" c="dimmed" mb="sm" style={{ minHeight: 36 }}>
                  {addon.description}
                </Text>
                <Text size="lg" fw={700} mb="sm">{formatCurrency(addon.price)}<Text span size="xs" c="dimmed">/mo</Text></Text>
                {tierMet ? (
                  <Button
                    variant="outline"
                    color="brand"
                    fullWidth
                    onClick={() => onNotify('Add-on checkout coming soon.', 'info')}
                    onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.background = 'rgba(255, 255, 255, 0.06)'; }}
                    onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = ''; }}
                  >
                    Subscribe
                  </Button>
                ) : (
                  <Button variant="light" color="gray" fullWidth disabled>
                    Requires {addon.tierLabel}
                  </Button>
                )}
              </Paper>
            );
          })}
        </SimpleGrid>
      </div>

      {/* Manage Billing (replaces Invoice History table) — only for Stripe-billed tenants */}
      {tenantContext?.hasStripeBilling && (
        <Paper p="lg" radius="md" withBorder>
          <Group justify="space-between" align="center">
            <div>
              <Text fw={600}>Invoices & payment methods</Text>
              <Text size="sm" c="dimmed">
                View invoice history, update payment methods, and manage your subscription through Stripe.
              </Text>
            </div>
            <Button color="brand" size="md" onClick={handleManageBilling}>
              Manage billing
            </Button>
          </Group>
        </Paper>
      )}
    </Stack>
  );
};
