// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

/**
 * Account and billing page — Standalone admin.
 *
 * Adapted from the prototype BillingPage with API hooks replacing mock data.
 * Uses flat UsageDashboard + DailyVolume API types from shared hooks.
 * Invoice history table replaced with Stripe portal "Manage Billing" button.
 *
 * Four-tier dark mode hierarchy (designer-approved):
 *   chrome #0c0a09 -> page #1c1917 -> surface #292524 -> border #44403c
 */

import React, { useCallback, useState } from 'react';
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
  Alert,
  TextInput,
  Divider,
} from '@mantine/core';

import { useAppContext } from '../layouts/StandaloneLayout';
import { useUsageDashboard } from '../../shared/hooks/index';
import { HelpTooltip } from '../../shared/HelpTooltip';
import { LoadingState } from '../../shared/LoadingState';
import { tokens } from '../../shared/theme/styles';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const BRAND_RED = tokens.brand;

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
        color="action"
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
  const { apiFetch, tenantContext, onNotify, userRole, userEmail } = useAppContext();
  const usage = useUsageDashboard(apiFetch);

  const [purchasingPack, setPurchasingPack] = React.useState<number | null>(null);

  // Contact preferences state (SPEC-1681)
  const [newEmail, setNewEmail] = useState('');
  const [emailChangePending, setEmailChangePending] = useState(false);
  const [recoveryEmail, setRecoveryEmail] = useState('');
  const [phone, setPhone] = useState('');





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

  // --- Email change handler (SPEC-1682) ---

  const handleRequestEmailChange = useCallback(async () => {
    const trimmed = newEmail.trim().toLowerCase();
    if (!trimmed || !trimmed.includes('@')) {
      onNotify('Please enter a valid email address.', 'error');
      return;
    }
    if (trimmed === (userEmail || '').toLowerCase()) {
      onNotify('New email must be different from your current email.', 'warning');
      return;
    }
    setEmailChangePending(true);
    try {
      const resp = await apiFetch('/api/admin/email/request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ new_email: trimmed }),
      });
      const data = await resp.json();
      if (resp.ok && data.ok) {
        onNotify('Confirmation email sent to your new address. Check your inbox.', 'success');
        setNewEmail('');
      } else {
        onNotify(data.message || 'Failed to request email change.', 'error');
      }
    } catch {
      onNotify('Failed to request email change. Please try again.', 'error');
    } finally {
      setEmailChangePending(false);
    }
  }, [newEmail, userEmail, apiFetch, onNotify]);

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
          <Title order={2}>Account and billing</Title>
          <Text c="dimmed" size="sm">Manage your account, contact preferences, and subscription</Text>
        </div>
        <LoadingState text="Loading billing data" />
      </Stack>
    );
  }

  // --- Render ---

  return (
    <Stack gap="lg">
      {/* Page header */}
      <div>
        <Title order={2}>Account and billing</Title>
        <Text c="dimmed" size="sm">
          Manage your account, contact preferences, and subscription
        </Text>
      </div>

      {/* Error alert */}
      {usage.error && (
        <Alert color="red" variant="light" title="Usage data unavailable">
          {usage.error}
        </Alert>
      )}

      {/* Contact and security preferences — superadmin only (SPEC-1681) */}
      {userRole === 'superadmin' && (
        <Paper p="lg" radius="md" withBorder>
          <Text fw={600} mb="md">
            Contact and security preferences
            <HelpTooltip
              text="Manage your account email, recovery options, and security settings. Only visible to superadmins."
              docLink="https://agentredcx.com/docs/admin-guide/account#contact-preferences"
            />
          </Text>

          <SimpleGrid cols={{ base: 1, md: 2 }} spacing="md">
            {/* Current email (read-only) */}
            <TextInput
              label="Account email"
              value={userEmail || ''}
              readOnly
              variant="filled"
              description="Your current login email address"
              styles={{ input: { cursor: 'default' } }}
            />

            {/* Change email (SPEC-1682) */}
            <div>
              <TextInput
                label="New email address"
                placeholder="Enter new email"
                value={newEmail}
                onChange={(e) => setNewEmail(e.currentTarget.value)}
                description="A confirmation link will be sent to the new address"
              />
              <Button
                mt="xs"
                size="xs"
                color="action"
                onClick={handleRequestEmailChange}
                loading={emailChangePending}
                disabled={emailChangePending || !newEmail.trim()}
              >
                Request email change
              </Button>
            </div>

            {/* Recovery email (SPEC-1677) */}
            <TextInput
              label="Recovery email"
              placeholder="backup@example.com"
              value={recoveryEmail}
              onChange={(e) => setRecoveryEmail(e.currentTarget.value)}
              description="Used for account recovery if you lose access"
            />

            {/* Phone number (SPEC-1686) */}
            <TextInput
              label="Phone number"
              placeholder="+1 (555) 123-4567"
              value={phone}
              onChange={(e) => setPhone(e.currentTarget.value)}
              description="For SMS verification and security alerts"
            />
          </SimpleGrid>
        </Paper>
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
            <Button color="action" onClick={handleManageSubscription}>
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
                    color="action"
                    fullWidth
                    onClick={() => onNotify('Add-on checkout coming soon.', 'info')}
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
            <Button color="action" size="md" onClick={handleManageBilling}>
              Manage billing
            </Button>
          </Group>
        </Paper>
      )}
    </Stack>
  );
};
