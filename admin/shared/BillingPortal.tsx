// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * BillingPortal — Subscription, usage, and billing management component.
 *
 * Displays current subscription status, conversation usage with 3-tier
 * metering breakdown, conversation pack purchasing, tier upgrade options,
 * and a link to the external billing portal (Stripe Customer Portal or
 * Shopify billing page, depending on the tenant's billing channel).
 *
 * Props:
 *   - BaseComponentProps (tenantContext, apiFetch, onNotify, onNavigate)
 *   - onManageBilling: callback invoked when the merchant clicks "Manage Billing"
 *   - onPurchasePack: callback invoked with pack size when the merchant purchases a pack
 *
 * Data hooks:
 *   - useUsageDashboard: real-time usage counters, allowance, overage estimate
 *   - usePackBalance: prepaid pack balance and individual pack details
 *   - useBillingStatus: subscription tier, status, renewal date, billing channel
 *
 * API endpoints consumed:
 *   - GET /api/dashboard/usage
 *   - GET /api/packs/balance/{customerId}
 *   - GET /api/shopify/billing/status | GET /api/billing/portal
 *
 * Architecture references:
 *   - Decision #25: Three-layer usage transparency
 *   - Decision #24: Billable conversation definition
 *   - UI-UX-ARCHITECTURE-DECISIONS.md section 7: BillingPortal spec
 *
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useState, useMemo } from 'react';
import type { BaseComponentProps, TenantTier } from './types';
import { useUsageDashboard, usePackBalance, useBillingStatus } from './hooks';
import { HelpTooltip } from './HelpTooltip';
import { tokens } from './theme/styles';

// ---------------------------------------------------------------------------
// Extended props
// ---------------------------------------------------------------------------

export interface BillingPortalProps extends BaseComponentProps {
  /** Shell handles navigation to Stripe Customer Portal or Shopify billing. */
  onManageBilling: () => void;
  /** Shell handles checkout flow for conversation pack purchases. */
  onPurchasePack: (packSize: 1000 | 5000 | 20000) => void;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const PACK_OPTIONS: Array<{ size: 1000 | 5000 | 20000; price: string; rate: string }> = [
  { size: 1000, price: '$29', rate: '$0.029/conv' },
  { size: 5000, price: '$99', rate: '$0.020/conv' },
  { size: 20000, price: '$249', rate: '$0.012/conv' },
];

const TIER_DISPLAY: Record<string, { label: string; color: string }> = {
  trial: { label: 'Trial', color: '#6B7280' },
  starter: { label: 'Starter', color: tokens.actionHover },
  professional: { label: 'Professional', color: tokens.chartViolet },
  enterprise: { label: 'Enterprise', color: tokens.brand },
};

const TIER_FEATURES: Array<{
  tier: TenantTier;
  price: string;
  annualPrice: string;
  conversations: string;
  overage: string;
  features: string[];
}> = [
  {
    tier: 'starter',
    price: '$149/mo',
    annualPrice: '$124/mo',
    conversations: '1,000',
    overage: '$0.04/conv',
    features: [
      'AI Customer Support (24/7)',
      'Customer Memory (Layer 1-2)',
      '1 Integration (Shopify)',
      'Email support',
    ],
  },
  {
    tier: 'professional',
    price: '$399/mo',
    annualPrice: '$332/mo',
    conversations: '5,000',
    overage: '$0.025/conv',
    features: [
      'Everything in Starter',
      'Cross-Session Learning (Layer 3)',
      'Remove branding',
      '4 Integrations',
      'Advanced Analytics',
      'Priority support',
    ],
  },
  {
    tier: 'enterprise',
    price: '$999/mo',
    annualPrice: '$832/mo',
    conversations: '20,000',
    overage: '$0.015/conv',
    features: [
      'Everything in Professional',
      'Dedicated Model Training',
      'White-Label Package',
      'Custom Integrations',
      'SSO (SAML/OIDC)',
      'Dedicated support',
    ],
  },
];

const STATUS_COLORS: Record<string, string> = {
  active: '#059669',
  suspended: '#D97706',
  cancelled: tokens.danger,
  trial_expired: '#9CA3AF',
};

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------

const styles = {
  container: {
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    maxWidth: 960,
    margin: '0 auto',
  } as React.CSSProperties,

  sectionTitle: {
    fontSize: 18,
    fontWeight: 600,
    color: '#111827',
    margin: '0 0 16px 0',
    padding: '0 0 8px 0',
    borderBottom: '1px solid #E5E7EB',
  } as React.CSSProperties,

  card: {
    background: '#FFFFFF',
    border: '1px solid #E5E7EB',
    borderRadius: 8,
    padding: 24,
    marginBottom: 24,
  } as React.CSSProperties,

  row: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 12,
  } as React.CSSProperties,

  label: {
    fontSize: 13,
    color: '#6B7280',
    fontWeight: 500,
  } as React.CSSProperties,

  value: {
    fontSize: 14,
    color: '#111827',
    fontWeight: 600,
  } as React.CSSProperties,

  badge: (color: string): React.CSSProperties => ({
    display: 'inline-block',
    padding: '2px 10px',
    borderRadius: 12,
    fontSize: 12,
    fontWeight: 600,
    color: tokens.white,
    background: color,
  }),

  progressBarOuter: {
    width: '100%',
    height: 8,
    background: '#E5E7EB',
    borderRadius: 4,
    overflow: 'hidden' as const,
    marginTop: 4,
    marginBottom: 4,
  } as React.CSSProperties,

  progressBarInner: (percent: number, color: string): React.CSSProperties => ({
    width: `${Math.min(percent, 100)}%`,
    height: '100%',
    background: color,
    borderRadius: 4,
    transition: 'width 0.3s ease',
  }),

  grid: (cols: number): React.CSSProperties => ({
    display: 'grid',
    gridTemplateColumns: `repeat(${cols}, 1fr)`,
    gap: 16,
  }),

  statBox: {
    background: '#F9FAFB',
    border: '1px solid #E5E7EB',
    borderRadius: 6,
    padding: 16,
    textAlign: 'center' as const,
  } as React.CSSProperties,

  statValue: {
    fontSize: 24,
    fontWeight: 700,
    color: '#111827',
    margin: '0 0 4px 0',
  } as React.CSSProperties,

  statLabel: {
    fontSize: 12,
    color: '#6B7280',
    fontWeight: 500,
    margin: 0,
  } as React.CSSProperties,

  button: (variant: 'primary' | 'secondary' | 'outline'): React.CSSProperties => ({
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: variant === 'outline' ? '8px 16px' : '10px 20px',
    borderRadius: 6,
    fontSize: 14,
    fontWeight: 600,
    cursor: 'pointer',
    border: variant === 'outline' ? '1px solid #D1D5DB' : 'none',
    background:
      variant === 'primary'
        ? tokens.action
        : variant === 'secondary'
          ? '#F3F4F6'
          : 'transparent',
    color:
      variant === 'primary'
        ? tokens.white
        : variant === 'secondary'
          ? '#374151'
          : '#374151',
    transition: 'opacity 0.15s ease',
  }),

  buttonDisabled: {
    opacity: 0.5,
    cursor: 'not-allowed',
  } as React.CSSProperties,

  packCard: {
    background: '#FFFFFF',
    border: '1px solid #E5E7EB',
    borderRadius: 8,
    padding: 20,
    textAlign: 'center' as const,
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    gap: 8,
  } as React.CSSProperties,

  packSize: {
    fontSize: 20,
    fontWeight: 700,
    color: '#111827',
    margin: 0,
  } as React.CSSProperties,

  packPrice: {
    fontSize: 28,
    fontWeight: 700,
    color: tokens.brand,
    margin: 0,
  } as React.CSSProperties,

  packRate: {
    fontSize: 12,
    color: '#6B7280',
    margin: 0,
  } as React.CSSProperties,

  packValidity: {
    fontSize: 11,
    color: '#9CA3AF',
    margin: 0,
  } as React.CSSProperties,

  tierCard: (isCurrentTier: boolean): React.CSSProperties => ({
    background: isCurrentTier ? '#FEF2F2' : '#FFFFFF',
    border: isCurrentTier ? `2px solid ${tokens.brand}` : '1px solid #E5E7EB',
    borderRadius: 8,
    padding: 20,
    position: 'relative' as const,
  }),

  tierBadge: {
    position: 'absolute' as const,
    top: -10,
    right: 16,
    background: tokens.brand,
    color: tokens.white,
    fontSize: 11,
    fontWeight: 600,
    padding: '2px 10px',
    borderRadius: 10,
  } as React.CSSProperties,

  tierName: {
    fontSize: 18,
    fontWeight: 700,
    color: '#111827',
    margin: '0 0 4px 0',
  } as React.CSSProperties,

  tierPrice: {
    fontSize: 14,
    color: '#6B7280',
    margin: '0 0 12px 0',
  } as React.CSSProperties,

  featureList: {
    listStyle: 'none',
    padding: 0,
    margin: '0 0 16px 0',
  } as React.CSSProperties,

  featureItem: {
    fontSize: 13,
    color: '#374151',
    padding: '4px 0',
    display: 'flex',
    alignItems: 'flex-start',
    gap: 6,
  } as React.CSSProperties,

  check: {
    color: '#059669',
    fontWeight: 700,
    fontSize: 14,
    lineHeight: '18px',
    flexShrink: 0,
  } as React.CSSProperties,

  alertBanner: (type: 'warning' | 'error' | 'info'): React.CSSProperties => ({
    padding: '12px 16px',
    borderRadius: 6,
    fontSize: 13,
    fontWeight: 500,
    marginBottom: 12,
    background:
      type === 'error' ? '#FEF2F2' : type === 'warning' ? '#FFFBEB' : '#EFF6FF',
    color:
      type === 'error' ? '#991B1B' : type === 'warning' ? '#92400E' : '#1E40AF',
    border:
      type === 'error'
        ? '1px solid #FECACA'
        : type === 'warning'
          ? '1px solid #FDE68A'
          : '1px solid #BFDBFE',
  }),

  loadingContainer: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 48,
    color: '#6B7280',
    fontSize: 14,
  } as React.CSSProperties,

  errorContainer: {
    padding: 24,
    background: '#FEF2F2',
    border: '1px solid #FECACA',
    borderRadius: 8,
    color: '#991B1B',
    fontSize: 14,
    textAlign: 'center' as const,
  } as React.CSSProperties,

  retryButton: {
    marginTop: 12,
    padding: '6px 16px',
    background: tokens.danger,
    color: tokens.white,
    border: 'none',
    borderRadius: 4,
    fontSize: 13,
    fontWeight: 600,
    cursor: 'pointer',
  } as React.CSSProperties,
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatNumber(n: number | undefined | null): string {
  if (n == null) return '0';
  return n.toLocaleString('en-US');
}

function formatCurrency(amount: number | undefined | null): string {
  if (amount == null) return '$0.00';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
}

function formatDate(dateStr: string | undefined | null): string {
  if (!dateStr) return '--';
  try {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  } catch {
    return dateStr;
  }
}

function getProgressColor(percent: number): string {
  if (percent >= 100) return tokens.danger;
  if (percent >= 80) return '#D97706';
  return '#059669';
}

function getTierOrder(tier: TenantTier): number {
  const order: Record<string, number> = { trial: 0, starter: 1, professional: 2, enterprise: 3 };
  return order[tier] ?? 0;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const BillingPortal: React.FC<BillingPortalProps> = ({
  tenantContext,
  apiFetch,
  onNotify,
  onManageBilling,
  onPurchasePack,
}) => {
  const [purchasingPack, setPurchasingPack] = useState<number | null>(null);

  // Data hooks
  const usage = useUsageDashboard(apiFetch);
  const packs = usePackBalance(apiFetch, tenantContext.tenantId);
  const billing = useBillingStatus(apiFetch, tenantContext.billingChannel, tenantContext.shopDomain);

  // Derived state
  const tierDisplay = TIER_DISPLAY[tenantContext.tier] || TIER_DISPLAY.starter;
  const statusColor = STATUS_COLORS[tenantContext.status] || '#6B7280';
  const currentTierOrder = getTierOrder(tenantContext.tier);

  const upgradeTiers = useMemo(
    () => TIER_FEATURES.filter((t) => getTierOrder(t.tier) > currentTierOrder),
    [currentTierOrder],
  );

  const usagePercent = usage.data?.usagePercent ?? 0;
  const progressColor = getProgressColor(usagePercent);

  // Active alerts from usage dashboard
  const activeAlerts = usage.data?.activeAlerts ?? [];

  // Pack purchase handler
  const handlePurchasePack = async (size: 1000 | 5000 | 20000) => {
    setPurchasingPack(size);
    try {
      onPurchasePack(size);
    } finally {
      // Shell handles the actual checkout flow; we just reset the UI state.
      // In practice the shell will navigate away or show a modal.
      setTimeout(() => setPurchasingPack(null), 1000);
    }
  };

  // -------------------------------------------------------------------------
  // Loading state
  // -------------------------------------------------------------------------

  if (usage.loading && !usage.data) {
    return (
      <div style={styles.container}>
        <div style={styles.loadingContainer}>Loading billing information...</div>
      </div>
    );
  }

  // -------------------------------------------------------------------------
  // Error state
  // -------------------------------------------------------------------------

  if (usage.error && !usage.data) {
    return (
      <div style={styles.container}>
        <div style={styles.errorContainer}>
          <div>Failed to load billing data: {usage.error}</div>
          <button style={styles.retryButton} onClick={usage.refetch}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------

  return (
    <div style={styles.container}>
      {/* Alerts */}
      {activeAlerts.length > 0 && (
        <div style={{ marginBottom: 16 }}>
          {activeAlerts.map((alert, idx) => {
            const isError = alert.includes('100') || alert.includes('exceeded');
            const isWarning = alert.includes('80') || alert.includes('low');
            return (
              <div
                key={idx}
                style={styles.alertBanner(isError ? 'error' : isWarning ? 'warning' : 'info')}
              >
                {alert.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
              </div>
            );
          })}
        </div>
      )}

      {/* Subscription Status Card */}
      <div style={styles.card}>
        <h3 style={styles.sectionTitle}>Subscription</h3>
        <div style={styles.row}>
          <span style={styles.label}>Current plan <HelpTooltip text="Your active subscription tier and billing status." docLink="https://agentredcx.com/docs/billing/overview#your-subscription-plan" /></span>
          <span style={styles.badge(tierDisplay.color)}>{tierDisplay.label}</span>
        </div>
        <div style={styles.row}>
          <span style={styles.label}>Billing channel</span>
          <span style={styles.value}>
            {tenantContext.billingChannel === 'shopify' ? 'Shopify' : 'Stripe'}
          </span>
        </div>
        <div style={styles.row}>
          <span style={styles.label}>Status</span>
          <span style={styles.badge(statusColor)}>
            {tenantContext.status.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
          </span>
        </div>
        {billing.data && (billing.data as Record<string, unknown>).renewal_date ? (
          <div style={styles.row}>
            <span style={styles.label}>Next renewal</span>
            <span style={styles.value}>
              {formatDate((billing.data as Record<string, unknown>).renewal_date as string)}
            </span>
          </div>
        ) : null}
        <div style={{ marginTop: 16 }}>
          <button
            className="ar-btn-action"
            style={styles.button('primary')}
            onClick={onManageBilling}
          >
            {tenantContext.billingChannel === 'shopify'
              ? 'Manage Shopify billing'
              : 'Manage billing in Stripe'}
          </button>
        </div>
      </div>

      {/* Usage Summary Card */}
      <div style={styles.card}>
        <h3 style={styles.sectionTitle}>Usage this period <HelpTooltip text="Conversation usage for the current monthly billing cycle." docLink="https://agentredcx.com/docs/billing/overview#usage-dashboard" /></h3>

        {usage.data ? (
          <>
            {/* Stat boxes */}
            <div style={styles.grid(4)}>
              <div style={styles.statBox}>
                <p style={styles.statValue}>
                  {formatNumber(usage.data.totalConversations)}
                </p>
                <p style={styles.statLabel}>Total conversations <HelpTooltip text="All conversations this billing period, including those covered by your plan allowance and packs." docLink="https://agentredcx.com/docs/billing/overview" /></p>
              </div>
              <div style={styles.statBox}>
                <p style={styles.statValue}>
                  {formatNumber(usage.data.remainingIncluded)}
                </p>
                <p style={styles.statLabel}>Included remaining <HelpTooltip text="Conversations remaining from your plan's monthly included allowance." docLink="https://agentredcx.com/docs/billing/overview" /></p>
              </div>
              <div style={styles.statBox}>
                <p style={styles.statValue}>
                  {formatNumber(usage.data.packBalance)}
                </p>
                <p style={styles.statLabel}>Pack balance <HelpTooltip text="Pre-purchased conversation credits. Packs are consumed after your included allowance is used, before overage billing." docLink="https://agentredcx.com/docs/billing/overview" /></p>
              </div>
              <div style={styles.statBox}>
                <p style={{
                  ...styles.statValue,
                  color: usage.data.overageConversations > 0 ? tokens.danger : '#111827',
                }}>
                  {formatNumber(usage.data.overageConversations)}
                </p>
                <p style={styles.statLabel}>Overage <HelpTooltip text="Conversations beyond your included allowance and pack balance, billed at your tier's overage rate." docLink="https://agentredcx.com/docs/billing/overview" /></p>
              </div>
            </div>

            {/* Progress bar */}
            <div style={{ marginTop: 20 }}>
              <div style={styles.row}>
                <span style={styles.label}>
                  Allowance Used: {formatNumber(usage.data.totalConversations)} / {formatNumber(usage.data.includedAllowance)}
                </span>
                <span style={{
                  ...styles.label,
                  fontWeight: 600,
                  color: progressColor,
                }}>
                  {Math.round(usagePercent)}%
                </span>
              </div>
              <div style={styles.progressBarOuter}>
                <div style={styles.progressBarInner(usagePercent, progressColor)} />
              </div>
            </div>

            {/* Estimated overage cost */}
            {usage.data.estimatedOverageCost > 0 && (
              <div style={{
                ...styles.row,
                marginTop: 16,
                padding: '12px 16px',
                background: '#FEF2F2',
                borderRadius: 6,
                border: '1px solid #FECACA',
              }}>
                <span style={{ ...styles.label, color: '#991B1B' }}>
                  Estimated overage cost <HelpTooltip text="Projected cost based on current overage conversations multiplied by your tier's overage rate." docLink="https://agentredcx.com/docs/billing/overview" />
                </span>
                <span style={{ ...styles.value, color: tokens.danger }}>
                  {formatCurrency(usage.data.estimatedOverageCost)}
                </span>
              </div>
            )}
          </>
        ) : (
          <div style={{ padding: 24, textAlign: 'center', color: '#6B7280', fontSize: 14 }}>
            No usage data available for this period.
          </div>
        )}
      </div>

      {/* Conversation Packs Card */}
      <div style={styles.card}>
        <h3 style={styles.sectionTitle}>Conversation packs <HelpTooltip text="Pre-purchase conversation credits at a discount. Packs are consumed before overage billing and expire after 90 days." docLink="https://agentredcx.com/docs/billing/overview#conversation-packs" /></h3>
        <p style={{
          fontSize: 13,
          color: '#6B7280',
          margin: '0 0 16px 0',
          lineHeight: 1.5,
        }}>
          Pre-purchase conversations at a discount. Packs are consumed before overage billing
          (FIFO order, oldest first). Each pack is valid for 90 days from purchase.
        </p>

        {/* Current pack balance */}
        {packs.data && packs.data.packs && packs.data.packs.length > 0 && (
          <div style={{
            background: '#F0FDF4',
            border: '1px solid #BBF7D0',
            borderRadius: 6,
            padding: '12px 16px',
            marginBottom: 16,
          }}>
            <div style={styles.row}>
              <span style={{ ...styles.label, color: '#166534' }}>Active pack balance</span>
              <span style={{ ...styles.value, color: '#166534' }}>
                {formatNumber(packs.data.balance)} conversations
              </span>
            </div>
            {packs.data.packs.map((pack: Record<string, unknown>, idx: number) => (
              <div key={idx} style={{
                fontSize: 12,
                color: '#166534',
                opacity: 0.8,
                marginTop: 4,
              }}>
                {formatNumber(pack.remaining as number)} remaining
                {pack.expires_at ? ` (expires ${formatDate(pack.expires_at as string)})` : ''}
              </div>
            ))}
          </div>
        )}

        {/* Pack purchase options */}
        <div style={styles.grid(3)}>
          {PACK_OPTIONS.map((pack) => (
            <div key={pack.size} style={styles.packCard}>
              <p style={styles.packSize}>
                {formatNumber(pack.size)}
              </p>
              <p style={{ fontSize: 12, color: '#6B7280', margin: 0 }}>conversations</p>
              <p style={styles.packPrice}>{pack.price}</p>
              <p style={styles.packRate}>{pack.rate}</p>
              <p style={styles.packValidity}>Valid for 90 days</p>
              <button
                className="ar-btn-action"
                style={{
                  ...styles.button('primary'),
                  width: '100%',
                  marginTop: 8,
                  ...(purchasingPack === pack.size ? styles.buttonDisabled : {}),
                }}
                disabled={purchasingPack === pack.size}
                onClick={() => handlePurchasePack(pack.size)}
              >
                {purchasingPack === pack.size ? 'Processing...' : 'Purchase'}
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Upgrade Tier Section */}
      {upgradeTiers.length > 0 && (
        <div style={styles.card}>
          <h3 style={styles.sectionTitle}>Upgrade plan <HelpTooltip text="Compare features and pricing across all tiers. Annual billing saves 17%." docLink="https://agentredcx.com/docs/billing/overview#managing-your-subscription" /></h3>
          <p style={{
            fontSize: 13,
            color: '#6B7280',
            margin: '0 0 16px 0',
            lineHeight: 1.5,
          }}>
            Unlock more conversations, advanced AI features, and premium integrations.
          </p>

          <div style={styles.grid(upgradeTiers.length)}>
            {upgradeTiers.map((tier) => {
              const display = TIER_DISPLAY[tier.tier];
              const isCurrent = tier.tier === tenantContext.tier;

              return (
                <div key={tier.tier} style={styles.tierCard(isCurrent)}>
                  {isCurrent && <span style={styles.tierBadge}>Current plan</span>}
                  <p style={styles.tierName}>{display.label}</p>
                  <p style={styles.tierPrice}>
                    {tier.price} <span style={{ fontSize: 12, color: '#9CA3AF' }}>
                      or {tier.annualPrice} (annual)
                    </span>
                  </p>

                  <div style={{
                    display: 'flex',
                    gap: 16,
                    marginBottom: 12,
                    fontSize: 13,
                  }}>
                    <div>
                      <span style={styles.label}>Included <HelpTooltip text="Conversations included in your plan's monthly fee." docLink="https://agentredcx.com/docs/billing/overview#how-conversations-are-billed" /></span>
                      <div style={{ ...styles.value, fontSize: 15 }}>{tier.conversations}</div>
                    </div>
                    <div>
                      <span style={styles.label}>Overage Rate <HelpTooltip text="Per-conversation charge for usage beyond included allowance and pack balance." docLink="https://agentredcx.com/docs/billing/overview#how-conversations-are-billed" /></span>
                      <div style={{ ...styles.value, fontSize: 15 }}>{tier.overage}</div>
                    </div>
                  </div>

                  <ul style={styles.featureList}>
                    {tier.features.map((feature, idx) => (
                      <li key={idx} style={styles.featureItem}>
                        <span style={styles.check}>&#10003;</span>
                        <span>{feature}</span>
                      </li>
                    ))}
                  </ul>

                  {!isCurrent && (
                    <button
                      className="ar-btn-action"
                      style={{ ...styles.button('primary'), width: '100%' }}
                      onClick={() => {
                        onNotify(
                          `To upgrade to ${display.label}, please use the Manage Billing portal.`,
                          'info',
                        );
                        onManageBilling();
                      }}
                    >
                      Upgrade to {display.label}
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default BillingPortal;
