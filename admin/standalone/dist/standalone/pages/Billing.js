import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
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
import { Paper, Group, Stack, Title, Text, Badge, Button, Progress, RingProgress, SimpleGrid, Alert, TextInput, } from '@mantine/core';
import { useAppContext } from '../layouts/StandaloneLayout';
import { useUsageDashboard } from '../../shared/hooks/index';
import { HelpTooltip } from '../../shared/HelpTooltip';
import { LoadingState } from '../../shared/LoadingState';
import { tokens } from '../../shared/theme/styles';
// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------
const BRAND_RED = tokens.brand;
const TIER_LABELS = {
    trial: 'Trial',
    starter: 'Starter',
    professional: 'Professional',
    enterprise: 'Enterprise',
};
const TIER_BADGE_COLORS = {
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
function formatCurrency(amount) {
    if (amount == null)
        return '$0.00';
    return `$${amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}
function formatNumber(n) {
    if (n == null)
        return '0';
    return n.toLocaleString('en-US');
}
function UsageStat({ label, value, subtext, progress, progressColor = BRAND_RED, ring, tooltip }) {
    return (_jsx(Paper, { p: "lg", radius: "md", withBorder: true, children: _jsxs(Group, { justify: "space-between", align: "flex-start", wrap: "nowrap", children: [_jsxs(Stack, { gap: 4, style: { flex: 1 }, children: [_jsxs(Text, { size: "xs", c: "dimmed", fw: 600, children: [label, tooltip && _jsx(HelpTooltip, { text: tooltip })] }), _jsx(Text, { size: "xl", fw: 700, lh: 1, children: value }), subtext && (_jsx(Text, { size: "xs", c: "dimmed", children: subtext })), progress !== undefined && !ring && (_jsx(Progress, { value: Math.min(progress, 100), color: progress > 90 ? 'red' : progress > 75 ? 'yellow' : progressColor, size: "sm", radius: "xl", mt: 4 }))] }), ring && progress !== undefined && (_jsx(RingProgress, { size: 56, thickness: 5, roundCaps: true, sections: [
                        {
                            value: Math.min(progress, 100),
                            color: progress > 90 ? 'red' : progress > 75 ? 'yellow' : progressColor,
                        },
                    ], label: _jsxs(Text, { size: "xs", ta: "center", fw: 600, lh: 1, children: [Math.round(progress), "%"] }) }))] }) }));
}
function PackCard({ conversations, price, effectiveRate, onPurchase, purchasing }) {
    return (_jsxs(Paper, { p: "lg", radius: "md", withBorder: true, style: { textAlign: 'center' }, children: [_jsx(Text, { size: "xl", fw: 700, c: BRAND_RED, children: (conversations ?? 0).toLocaleString() }), _jsx(Text, { size: "sm", c: "dimmed", mb: 4, children: "conversations" }), _jsx(Text, { size: "lg", fw: 700, mb: 2, children: formatCurrency(price) }), _jsxs(Text, { size: "xs", c: "dimmed", mb: "md", children: [effectiveRate, "/conversation"] }), _jsx(Button, { color: "action", fullWidth: true, onClick: onPurchase, loading: purchasing, disabled: purchasing, children: "Purchase" })] }));
}
// ---------------------------------------------------------------------------
// BillingPage
// ---------------------------------------------------------------------------
export const BillingPage = () => {
    const { apiFetch, tenantContext, onNotify, userRole, userEmail } = useAppContext();
    const usage = useUsageDashboard(apiFetch);
    const [purchasingPack, setPurchasingPack] = React.useState(null);
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
            if (!resp.ok)
                throw new Error('Failed to create portal session');
            const data = await resp.json();
            if (data.portal_url) {
                window.open(data.portal_url, '_blank');
            }
        }
        catch {
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
            }
            else {
                onNotify(data.message || 'Failed to request email change.', 'error');
            }
        }
        catch {
            onNotify('Failed to request email change. Please try again.', 'error');
        }
        finally {
            setEmailChangePending(false);
        }
    }, [newEmail, userEmail, apiFetch, onNotify]);
    const PACK_ID_MAP = { 1000: 'pack_1k', 5000: 'pack_5k', 20000: 'pack_20k' };
    const handlePurchasePack = useCallback(async (packSize) => {
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
            if (!resp.ok)
                throw new Error('Purchase failed');
            const data = await resp.json();
            if (data.checkout_url) {
                window.location.href = data.checkout_url;
            }
        }
        catch {
            onNotify('Failed to start purchase. Please try again.', 'error');
        }
        finally {
            setTimeout(() => setPurchasingPack(null), 1000);
        }
    }, [apiFetch, onNotify, tenantContext]);
    // --- Loading state ---
    if (usage.loading && !usage.data) {
        return (_jsxs(Stack, { gap: "lg", children: [_jsxs("div", { children: [_jsx(Title, { order: 2, children: "Account and billing" }), _jsx(Text, { c: "dimmed", size: "sm", children: "Manage your account, contact preferences, and subscription" })] }), _jsx(LoadingState, { text: "Loading billing data" })] }));
    }
    // --- Render ---
    return (_jsxs(Stack, { gap: "lg", children: [_jsxs("div", { children: [_jsx(Title, { order: 2, children: "Account and billing" }), _jsx(Text, { c: "dimmed", size: "sm", children: "Manage your account, contact preferences, and subscription" })] }), usage.error && (_jsx(Alert, { color: "red", variant: "light", title: "Usage data unavailable", children: usage.error })), userRole === 'superadmin' && (_jsxs(Paper, { p: "lg", radius: "md", withBorder: true, children: [_jsxs(Text, { fw: 600, mb: "md", children: ["Contact and security preferences", _jsx(HelpTooltip, { text: "Manage your account email, recovery options, and security settings. Only visible to superadmins.", docLink: "https://agentredcx.com/docs/admin-guide/account#contact-preferences" })] }), _jsxs(SimpleGrid, { cols: { base: 1, md: 2 }, spacing: "md", children: [_jsx(TextInput, { label: "Account email", value: userEmail || '', readOnly: true, variant: "filled", description: "Your current login email address", styles: { input: { cursor: 'default' } } }), _jsxs("div", { children: [_jsx(TextInput, { label: "New email address", placeholder: "Enter new email", value: newEmail, onChange: (e) => setNewEmail(e.currentTarget.value), description: "A confirmation link will be sent to the new address" }), _jsx(Button, { mt: "xs", size: "xs", color: "action", onClick: handleRequestEmailChange, loading: emailChangePending, disabled: emailChangePending || !newEmail.trim(), children: "Request email change" })] }), _jsx(TextInput, { label: "Recovery email", placeholder: "backup@example.com", value: recoveryEmail, onChange: (e) => setRecoveryEmail(e.currentTarget.value), description: "Used for account recovery if you lose access" }), _jsx(TextInput, { label: "Phone number", placeholder: "+1 (555) 123-4567", value: phone, onChange: (e) => setPhone(e.currentTarget.value), description: "For SMS verification and security alerts" })] })] })), _jsx(Paper, { p: "lg", radius: "md", withBorder: true, children: _jsxs(Group, { justify: "space-between", align: "flex-start", wrap: "wrap", children: [_jsxs(Stack, { gap: 6, children: [_jsxs(Group, { gap: "sm", align: "center", children: [_jsxs(Text, { size: "lg", fw: 700, children: ["Current plan", _jsx(HelpTooltip, { text: "Your active subscription tier determines your included monthly conversations, overage rate, and available features.", docLink: "https://agentredcx.com/docs/billing/overview#your-subscription-plan" })] }), _jsx(Badge, { color: tierBadgeColor, variant: "filled", size: "lg", tt: "capitalize", children: tierLabel }), _jsx(Badge, { color: "green", variant: "light", size: "sm", children: tenantContext?.status === 'active' ? 'Active' : (tenantContext?.status ?? 'Active') })] }), _jsxs(Group, { gap: "lg", children: [_jsxs("div", { children: [_jsx(Text, { size: "xs", c: "dimmed", children: "Included conversations" }), _jsxs(Text, { size: "md", fw: 600, children: [formatNumber(includedAllowance), "/mo"] })] }), _jsxs("div", { children: [_jsx(Text, { size: "xs", c: "dimmed", children: "Used this period" }), _jsx(Text, { size: "md", fw: 600, children: formatNumber(totalConversations) })] }), _jsxs("div", { children: [_jsx(Text, { size: "xs", c: "dimmed", children: "Remaining" }), _jsx(Text, { size: "md", fw: 600, children: formatNumber(remainingIncluded) })] })] })] }), tenantContext?.hasStripeBilling && (_jsx(Button, { color: "action", onClick: handleManageSubscription, children: "Manage subscription" }))] }) }), _jsxs(SimpleGrid, { cols: { base: 1, xs: 2, md: 4 }, spacing: "md", children: [_jsx(UsageStat, { label: "Conversations used", tooltip: "Total conversations this billing period vs. your plan's included monthly allowance.", value: `${formatNumber(totalConversations)} / ${formatNumber(includedAllowance)}`, subtext: `${Math.round(usagePercent)}% of included allowance`, progress: usagePercent, ring: true, progressColor: BRAND_RED }), _jsx(UsageStat, { label: "Pack balance", tooltip: "Remaining conversations from pre-purchased packs. Packs are used after your included allowance is depleted and before overage billing begins.", value: formatNumber(packBalance), subtext: "remaining conversations" }), _jsx(UsageStat, { label: "Current overage", tooltip: "Conversations beyond your included allowance and pack balance. Overage is billed at your plan's per-conversation rate.", value: formatCurrency(estimatedOverageCost), subtext: overageConversations > 0
                            ? `${formatNumber(overageConversations)} overage conversations`
                            : 'No overage charges' }), _jsx(UsageStat, { label: "Estimated overage cost", tooltip: "Projected additional charges for overage conversations this billing period.", value: formatCurrency(estimatedOverageCost), subtext: "Additional charges this period" })] }), (usage.data?.activeAlerts ?? []).length > 0 && (_jsx(Alert, { color: "yellow", variant: "light", title: "Usage alerts", children: _jsx(Stack, { gap: 4, children: (usage.data?.activeAlerts ?? []).map((alert, i) => (_jsx(Text, { size: "sm", children: alert }, i))) }) })), _jsxs("div", { children: [_jsxs(Text, { size: "lg", fw: 600, mb: 4, children: ["Conversation packs", _jsx(HelpTooltip, { text: "Pre-purchase conversation bundles at discounted rates. Pack conversations are consumed after your included allowance and before overage billing. Valid for 90 days, FIFO usage order.", docLink: "https://agentredcx.com/docs/billing/overview#conversation-packs" })] }), _jsx(Text, { size: "sm", c: "dimmed", mb: "md", children: "Pre-purchase conversations at a discounted rate. Packs are valid for 90 days." }), _jsxs(SimpleGrid, { cols: { base: 1, xs: 3 }, spacing: "md", children: [_jsx(PackCard, { conversations: 1000, price: 29, effectiveRate: "$0.029", onPurchase: () => handlePurchasePack(1000), purchasing: purchasingPack === 1000 }), _jsx(PackCard, { conversations: 5000, price: 99, effectiveRate: "$0.020", onPurchase: () => handlePurchasePack(5000), purchasing: purchasingPack === 5000 }), _jsx(PackCard, { conversations: 20000, price: 249, effectiveRate: "$0.012", onPurchase: () => handlePurchasePack(20000), purchasing: purchasingPack === 20000 })] })] }), _jsxs("div", { children: [_jsxs(Text, { size: "lg", fw: 600, mb: 4, children: ["Add-on modules", _jsx(HelpTooltip, { text: "Optional feature modules that extend your plan. Add-on subscriptions are billed monthly alongside your base plan.", docLink: "https://agentredcx.com/docs/billing/overview#add-on-modules" })] }), _jsx(Text, { size: "sm", c: "dimmed", mb: "md", children: "Enhance your plan with additional capabilities. Billed monthly." }), _jsx(SimpleGrid, { cols: { base: 1, xs: 2, md: 3 }, spacing: "md", children: ADDON_MODULES.map((addon) => {
                            const tierMet = addon.availableOn.includes(tier);
                            return (_jsxs(Paper, { p: "lg", radius: "md", withBorder: true, style: { opacity: tierMet ? 1 : 0.65 }, children: [_jsxs(Group, { justify: "space-between", mb: 6, children: [_jsx(Text, { size: "md", fw: 600, children: addon.label }), _jsx(Badge, { color: addon.tierLabel === 'All tiers' ? 'green' : addon.tierLabel === 'Enterprise' ? 'grape' : 'blue', variant: "light", size: "xs", children: addon.tierLabel })] }), _jsx(Text, { size: "xs", c: "dimmed", mb: "sm", style: { minHeight: 36 }, children: addon.description }), _jsxs(Text, { size: "lg", fw: 700, mb: "sm", children: [formatCurrency(addon.price), _jsx(Text, { span: true, size: "xs", c: "dimmed", children: "/mo" })] }), tierMet ? (_jsx(Button, { color: "action", fullWidth: true, onClick: () => onNotify('Add-on checkout coming soon.', 'info'), children: "Subscribe" })) : (_jsxs(Button, { variant: "light", color: "gray", fullWidth: true, disabled: true, children: ["Requires ", addon.tierLabel] }))] }, addon.id));
                        }) })] }), tenantContext?.hasStripeBilling && (_jsx(Paper, { p: "lg", radius: "md", withBorder: true, children: _jsxs(Group, { justify: "space-between", align: "center", children: [_jsxs("div", { children: [_jsx(Text, { fw: 600, children: "Invoices & payment methods" }), _jsx(Text, { size: "sm", c: "dimmed", children: "View invoice history, update payment methods, and manage your subscription through Stripe." })] }), _jsx(Button, { color: "action", size: "md", onClick: handleManageBilling, children: "Manage billing" })] }) }))] }));
};
//# sourceMappingURL=Billing.js.map