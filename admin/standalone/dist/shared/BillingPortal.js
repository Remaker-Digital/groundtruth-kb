import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
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
import { useState, useMemo } from 'react';
import { useUsageDashboard, usePackBalance, useBillingStatus } from './hooks';
import { HelpTooltip } from './HelpTooltip';
import { tokens } from './theme/styles';
// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------
const PACK_OPTIONS = [
    { size: 1000, price: '$29', rate: '$0.029/conv' },
    { size: 5000, price: '$99', rate: '$0.020/conv' },
    { size: 20000, price: '$249', rate: '$0.012/conv' },
];
const TIER_DISPLAY = {
    trial: { label: 'Trial', color: '#6B7280' },
    starter: { label: 'Starter', color: tokens.actionHover },
    professional: { label: 'Professional', color: tokens.chartViolet },
    enterprise: { label: 'Enterprise', color: tokens.brand },
};
const TIER_FEATURES = [
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
const STATUS_COLORS = {
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
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: 600,
        color: '#111827',
        margin: '0 0 16px 0',
        padding: '0 0 8px 0',
        borderBottom: '1px solid #E5E7EB',
    },
    card: {
        background: '#FFFFFF',
        border: '1px solid #E5E7EB',
        borderRadius: 8,
        padding: 24,
        marginBottom: 24,
    },
    row: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: 12,
    },
    label: {
        fontSize: 13,
        color: '#6B7280',
        fontWeight: 500,
    },
    value: {
        fontSize: 14,
        color: '#111827',
        fontWeight: 600,
    },
    badge: (color) => ({
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
        overflow: 'hidden',
        marginTop: 4,
        marginBottom: 4,
    },
    progressBarInner: (percent, color) => ({
        width: `${Math.min(percent, 100)}%`,
        height: '100%',
        background: color,
        borderRadius: 4,
        transition: 'width 0.3s ease',
    }),
    grid: (cols) => ({
        display: 'grid',
        gridTemplateColumns: `repeat(${cols}, 1fr)`,
        gap: 16,
    }),
    statBox: {
        background: '#F9FAFB',
        border: '1px solid #E5E7EB',
        borderRadius: 6,
        padding: 16,
        textAlign: 'center',
    },
    statValue: {
        fontSize: 24,
        fontWeight: 700,
        color: '#111827',
        margin: '0 0 4px 0',
    },
    statLabel: {
        fontSize: 12,
        color: '#6B7280',
        fontWeight: 500,
        margin: 0,
    },
    button: (variant) => ({
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: variant === 'outline' ? '8px 16px' : '10px 20px',
        borderRadius: 6,
        fontSize: 14,
        fontWeight: 600,
        cursor: 'pointer',
        border: variant === 'outline' ? '1px solid #D1D5DB' : 'none',
        background: variant === 'primary'
            ? tokens.action
            : variant === 'secondary'
                ? '#F3F4F6'
                : 'transparent',
        color: variant === 'primary'
            ? tokens.white
            : variant === 'secondary'
                ? '#374151'
                : '#374151',
        transition: 'opacity 0.15s ease',
    }),
    buttonDisabled: {
        opacity: 0.5,
        cursor: 'not-allowed',
    },
    packCard: {
        background: '#FFFFFF',
        border: '1px solid #E5E7EB',
        borderRadius: 8,
        padding: 20,
        textAlign: 'center',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: 8,
    },
    packSize: {
        fontSize: 20,
        fontWeight: 700,
        color: '#111827',
        margin: 0,
    },
    packPrice: {
        fontSize: 28,
        fontWeight: 700,
        color: tokens.brand,
        margin: 0,
    },
    packRate: {
        fontSize: 12,
        color: '#6B7280',
        margin: 0,
    },
    packValidity: {
        fontSize: 11,
        color: '#9CA3AF',
        margin: 0,
    },
    tierCard: (isCurrentTier) => ({
        background: isCurrentTier ? '#FEF2F2' : '#FFFFFF',
        border: isCurrentTier ? `2px solid ${tokens.brand}` : '1px solid #E5E7EB',
        borderRadius: 8,
        padding: 20,
        position: 'relative',
    }),
    tierBadge: {
        position: 'absolute',
        top: -10,
        right: 16,
        background: tokens.brand,
        color: tokens.white,
        fontSize: 11,
        fontWeight: 600,
        padding: '2px 10px',
        borderRadius: 10,
    },
    tierName: {
        fontSize: 18,
        fontWeight: 700,
        color: '#111827',
        margin: '0 0 4px 0',
    },
    tierPrice: {
        fontSize: 14,
        color: '#6B7280',
        margin: '0 0 12px 0',
    },
    featureList: {
        listStyle: 'none',
        padding: 0,
        margin: '0 0 16px 0',
    },
    featureItem: {
        fontSize: 13,
        color: '#374151',
        padding: '4px 0',
        display: 'flex',
        alignItems: 'flex-start',
        gap: 6,
    },
    check: {
        color: '#059669',
        fontWeight: 700,
        fontSize: 14,
        lineHeight: '18px',
        flexShrink: 0,
    },
    alertBanner: (type) => ({
        padding: '12px 16px',
        borderRadius: 6,
        fontSize: 13,
        fontWeight: 500,
        marginBottom: 12,
        background: type === 'error' ? '#FEF2F2' : type === 'warning' ? '#FFFBEB' : '#EFF6FF',
        color: type === 'error' ? '#991B1B' : type === 'warning' ? '#92400E' : '#1E40AF',
        border: type === 'error'
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
    },
    errorContainer: {
        padding: 24,
        background: '#FEF2F2',
        border: '1px solid #FECACA',
        borderRadius: 8,
        color: '#991B1B',
        fontSize: 14,
        textAlign: 'center',
    },
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
    },
};
// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function formatNumber(n) {
    if (n == null)
        return '0';
    return n.toLocaleString('en-US');
}
function formatCurrency(amount) {
    if (amount == null)
        return '$0.00';
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    }).format(amount);
}
function formatDate(dateStr) {
    if (!dateStr)
        return '--';
    try {
        return new Date(dateStr).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
        });
    }
    catch {
        return dateStr;
    }
}
function getProgressColor(percent) {
    if (percent >= 100)
        return tokens.danger;
    if (percent >= 80)
        return '#D97706';
    return '#059669';
}
function getTierOrder(tier) {
    const order = { trial: 0, starter: 1, professional: 2, enterprise: 3 };
    return order[tier] ?? 0;
}
// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export const BillingPortal = ({ tenantContext, apiFetch, onNotify, onManageBilling, onPurchasePack, }) => {
    const [purchasingPack, setPurchasingPack] = useState(null);
    // Data hooks
    const usage = useUsageDashboard(apiFetch);
    const packs = usePackBalance(apiFetch, tenantContext.tenantId);
    const billing = useBillingStatus(apiFetch, tenantContext.billingChannel, tenantContext.shopDomain);
    // Derived state
    const tierDisplay = TIER_DISPLAY[tenantContext.tier] || TIER_DISPLAY.starter;
    const statusColor = STATUS_COLORS[tenantContext.status] || '#6B7280';
    const currentTierOrder = getTierOrder(tenantContext.tier);
    const upgradeTiers = useMemo(() => TIER_FEATURES.filter((t) => getTierOrder(t.tier) > currentTierOrder), [currentTierOrder]);
    const usagePercent = usage.data?.usagePercent ?? 0;
    const progressColor = getProgressColor(usagePercent);
    // Active alerts from usage dashboard
    const activeAlerts = usage.data?.activeAlerts ?? [];
    // Pack purchase handler
    const handlePurchasePack = async (size) => {
        setPurchasingPack(size);
        try {
            onPurchasePack(size);
        }
        finally {
            // Shell handles the actual checkout flow; we just reset the UI state.
            // In practice the shell will navigate away or show a modal.
            setTimeout(() => setPurchasingPack(null), 1000);
        }
    };
    // -------------------------------------------------------------------------
    // Loading state
    // -------------------------------------------------------------------------
    if (usage.loading && !usage.data) {
        return (_jsx("div", { style: styles.container, children: _jsx("div", { style: styles.loadingContainer, children: "Loading billing information..." }) }));
    }
    // -------------------------------------------------------------------------
    // Error state
    // -------------------------------------------------------------------------
    if (usage.error && !usage.data) {
        return (_jsx("div", { style: styles.container, children: _jsxs("div", { style: styles.errorContainer, children: [_jsxs("div", { children: ["Failed to load billing data: ", usage.error] }), _jsx("button", { style: styles.retryButton, onClick: usage.refetch, children: "Retry" })] }) }));
    }
    // -------------------------------------------------------------------------
    // Render
    // -------------------------------------------------------------------------
    return (_jsxs("div", { style: styles.container, children: [activeAlerts.length > 0 && (_jsx("div", { style: { marginBottom: 16 }, children: activeAlerts.map((alert, idx) => {
                    const isError = alert.includes('100') || alert.includes('exceeded');
                    const isWarning = alert.includes('80') || alert.includes('low');
                    return (_jsx("div", { style: styles.alertBanner(isError ? 'error' : isWarning ? 'warning' : 'info'), children: alert.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()) }, idx));
                }) })), _jsxs("div", { style: styles.card, children: [_jsx("h3", { style: styles.sectionTitle, children: "Subscription" }), _jsxs("div", { style: styles.row, children: [_jsxs("span", { style: styles.label, children: ["Current plan ", _jsx(HelpTooltip, { text: "Your active subscription tier and billing status.", docLink: "https://agentredcx.com/docs/billing/overview#your-subscription-plan" })] }), _jsx("span", { style: styles.badge(tierDisplay.color), children: tierDisplay.label })] }), _jsxs("div", { style: styles.row, children: [_jsx("span", { style: styles.label, children: "Billing channel" }), _jsx("span", { style: styles.value, children: tenantContext.billingChannel === 'shopify' ? 'Shopify' : 'Stripe' })] }), _jsxs("div", { style: styles.row, children: [_jsx("span", { style: styles.label, children: "Status" }), _jsx("span", { style: styles.badge(statusColor), children: tenantContext.status.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()) })] }), billing.data && billing.data.renewal_date ? (_jsxs("div", { style: styles.row, children: [_jsx("span", { style: styles.label, children: "Next renewal" }), _jsx("span", { style: styles.value, children: formatDate(billing.data.renewal_date) })] })) : null, _jsx("div", { style: { marginTop: 16 }, children: _jsx("button", { className: "ar-btn-action", style: styles.button('primary'), onClick: onManageBilling, children: tenantContext.billingChannel === 'shopify'
                                ? 'Manage Shopify billing'
                                : 'Manage billing in Stripe' }) })] }), _jsxs("div", { style: styles.card, children: [_jsxs("h3", { style: styles.sectionTitle, children: ["Usage this period ", _jsx(HelpTooltip, { text: "Conversation usage for the current monthly billing cycle.", docLink: "https://agentredcx.com/docs/billing/overview#usage-dashboard" })] }), usage.data ? (_jsxs(_Fragment, { children: [_jsxs("div", { style: styles.grid(4), children: [_jsxs("div", { style: styles.statBox, children: [_jsx("p", { style: styles.statValue, children: formatNumber(usage.data.totalConversations) }), _jsxs("p", { style: styles.statLabel, children: ["Total conversations ", _jsx(HelpTooltip, { text: "All conversations this billing period, including those covered by your plan allowance and packs.", docLink: "https://agentredcx.com/docs/billing/overview" })] })] }), _jsxs("div", { style: styles.statBox, children: [_jsx("p", { style: styles.statValue, children: formatNumber(usage.data.remainingIncluded) }), _jsxs("p", { style: styles.statLabel, children: ["Included remaining ", _jsx(HelpTooltip, { text: "Conversations remaining from your plan's monthly included allowance.", docLink: "https://agentredcx.com/docs/billing/overview" })] })] }), _jsxs("div", { style: styles.statBox, children: [_jsx("p", { style: styles.statValue, children: formatNumber(usage.data.packBalance) }), _jsxs("p", { style: styles.statLabel, children: ["Pack balance ", _jsx(HelpTooltip, { text: "Pre-purchased conversation credits. Packs are consumed after your included allowance is used, before overage billing.", docLink: "https://agentredcx.com/docs/billing/overview" })] })] }), _jsxs("div", { style: styles.statBox, children: [_jsx("p", { style: {
                                                    ...styles.statValue,
                                                    color: usage.data.overageConversations > 0 ? tokens.danger : '#111827',
                                                }, children: formatNumber(usage.data.overageConversations) }), _jsxs("p", { style: styles.statLabel, children: ["Overage ", _jsx(HelpTooltip, { text: "Conversations beyond your included allowance and pack balance, billed at your tier's overage rate.", docLink: "https://agentredcx.com/docs/billing/overview" })] })] })] }), _jsxs("div", { style: { marginTop: 20 }, children: [_jsxs("div", { style: styles.row, children: [_jsxs("span", { style: styles.label, children: ["Allowance Used: ", formatNumber(usage.data.totalConversations), " / ", formatNumber(usage.data.includedAllowance)] }), _jsxs("span", { style: {
                                                    ...styles.label,
                                                    fontWeight: 600,
                                                    color: progressColor,
                                                }, children: [Math.round(usagePercent), "%"] })] }), _jsx("div", { style: styles.progressBarOuter, children: _jsx("div", { style: styles.progressBarInner(usagePercent, progressColor) }) })] }), usage.data.estimatedOverageCost > 0 && (_jsxs("div", { style: {
                                    ...styles.row,
                                    marginTop: 16,
                                    padding: '12px 16px',
                                    background: '#FEF2F2',
                                    borderRadius: 6,
                                    border: '1px solid #FECACA',
                                }, children: [_jsxs("span", { style: { ...styles.label, color: '#991B1B' }, children: ["Estimated overage cost ", _jsx(HelpTooltip, { text: "Projected cost based on current overage conversations multiplied by your tier's overage rate.", docLink: "https://agentredcx.com/docs/billing/overview" })] }), _jsx("span", { style: { ...styles.value, color: tokens.danger }, children: formatCurrency(usage.data.estimatedOverageCost) })] }))] })) : (_jsx("div", { style: { padding: 24, textAlign: 'center', color: '#6B7280', fontSize: 14 }, children: "No usage data available for this period." }))] }), _jsxs("div", { style: styles.card, children: [_jsxs("h3", { style: styles.sectionTitle, children: ["Conversation packs ", _jsx(HelpTooltip, { text: "Pre-purchase conversation credits at a discount. Packs are consumed before overage billing and expire after 90 days.", docLink: "https://agentredcx.com/docs/billing/overview#conversation-packs" })] }), _jsx("p", { style: {
                            fontSize: 13,
                            color: '#6B7280',
                            margin: '0 0 16px 0',
                            lineHeight: 1.5,
                        }, children: "Pre-purchase conversations at a discount. Packs are consumed before overage billing (FIFO order, oldest first). Each pack is valid for 90 days from purchase." }), packs.data && packs.data.packs && packs.data.packs.length > 0 && (_jsxs("div", { style: {
                            background: '#F0FDF4',
                            border: '1px solid #BBF7D0',
                            borderRadius: 6,
                            padding: '12px 16px',
                            marginBottom: 16,
                        }, children: [_jsxs("div", { style: styles.row, children: [_jsx("span", { style: { ...styles.label, color: '#166534' }, children: "Active pack balance" }), _jsxs("span", { style: { ...styles.value, color: '#166534' }, children: [formatNumber(packs.data.balance), " conversations"] })] }), packs.data.packs.map((pack, idx) => (_jsxs("div", { style: {
                                    fontSize: 12,
                                    color: '#166534',
                                    opacity: 0.8,
                                    marginTop: 4,
                                }, children: [formatNumber(pack.remaining), " remaining", pack.expires_at ? ` (expires ${formatDate(pack.expires_at)})` : ''] }, idx)))] })), _jsx("div", { style: styles.grid(3), children: PACK_OPTIONS.map((pack) => (_jsxs("div", { style: styles.packCard, children: [_jsx("p", { style: styles.packSize, children: formatNumber(pack.size) }), _jsx("p", { style: { fontSize: 12, color: '#6B7280', margin: 0 }, children: "conversations" }), _jsx("p", { style: styles.packPrice, children: pack.price }), _jsx("p", { style: styles.packRate, children: pack.rate }), _jsx("p", { style: styles.packValidity, children: "Valid for 90 days" }), _jsx("button", { className: "ar-btn-action", style: {
                                        ...styles.button('primary'),
                                        width: '100%',
                                        marginTop: 8,
                                        ...(purchasingPack === pack.size ? styles.buttonDisabled : {}),
                                    }, disabled: purchasingPack === pack.size, onClick: () => handlePurchasePack(pack.size), children: purchasingPack === pack.size ? 'Processing...' : 'Purchase' })] }, pack.size))) })] }), upgradeTiers.length > 0 && (_jsxs("div", { style: styles.card, children: [_jsxs("h3", { style: styles.sectionTitle, children: ["Upgrade plan ", _jsx(HelpTooltip, { text: "Compare features and pricing across all tiers. Annual billing saves 17%.", docLink: "https://agentredcx.com/docs/billing/overview#managing-your-subscription" })] }), _jsx("p", { style: {
                            fontSize: 13,
                            color: '#6B7280',
                            margin: '0 0 16px 0',
                            lineHeight: 1.5,
                        }, children: "Unlock more conversations, advanced AI features, and premium integrations." }), _jsx("div", { style: styles.grid(upgradeTiers.length), children: upgradeTiers.map((tier) => {
                            const display = TIER_DISPLAY[tier.tier];
                            const isCurrent = tier.tier === tenantContext.tier;
                            return (_jsxs("div", { style: styles.tierCard(isCurrent), children: [isCurrent && _jsx("span", { style: styles.tierBadge, children: "Current plan" }), _jsx("p", { style: styles.tierName, children: display.label }), _jsxs("p", { style: styles.tierPrice, children: [tier.price, " ", _jsxs("span", { style: { fontSize: 12, color: '#9CA3AF' }, children: ["or ", tier.annualPrice, " (annual)"] })] }), _jsxs("div", { style: {
                                            display: 'flex',
                                            gap: 16,
                                            marginBottom: 12,
                                            fontSize: 13,
                                        }, children: [_jsxs("div", { children: [_jsxs("span", { style: styles.label, children: ["Included ", _jsx(HelpTooltip, { text: "Conversations included in your plan's monthly fee.", docLink: "https://agentredcx.com/docs/billing/overview#how-conversations-are-billed" })] }), _jsx("div", { style: { ...styles.value, fontSize: 15 }, children: tier.conversations })] }), _jsxs("div", { children: [_jsxs("span", { style: styles.label, children: ["Overage Rate ", _jsx(HelpTooltip, { text: "Per-conversation charge for usage beyond included allowance and pack balance.", docLink: "https://agentredcx.com/docs/billing/overview#how-conversations-are-billed" })] }), _jsx("div", { style: { ...styles.value, fontSize: 15 }, children: tier.overage })] })] }), _jsx("ul", { style: styles.featureList, children: tier.features.map((feature, idx) => (_jsxs("li", { style: styles.featureItem, children: [_jsx("span", { style: styles.check, children: "\u2713" }), _jsx("span", { children: feature })] }, idx))) }), !isCurrent && (_jsxs("button", { className: "ar-btn-action", style: { ...styles.button('primary'), width: '100%' }, onClick: () => {
                                            onNotify(`To upgrade to ${display.label}, please use the Manage Billing portal.`, 'info');
                                            onManageBilling();
                                        }, children: ["Upgrade to ", display.label] }))] }, tier.tier));
                        }) })] }))] }));
};
export default BillingPortal;
//# sourceMappingURL=BillingPortal.js.map