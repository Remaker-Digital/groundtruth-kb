import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
/**
 * IntegrationsManager — Shared component for managing third-party integrations.
 *
 * Displays available integrations (Shopify, Zendesk, Mailchimp, Google Analytics,
 * Stripe MCP) as cards with status badges, activate/deactivate toggles, and
 * disconnect actions. Stripe includes MCP credential management panel.
 * Tier-gated integrations show upgrade prompts for lower-tier tenants.
 *
 * C10 capability dependency for Launch UI Test.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { useCallback, useState } from 'react';
import { useIntegrations, useActivateIntegration, useDeactivateIntegration, useDisconnectIntegration, } from './hooks/index';
import { HelpTooltip } from './HelpTooltip';
import { McpConfigPanel } from './McpConfigPanel';
import { tokens } from './theme/styles';
// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------
/** Map HoverButton variant → CSS utility class */
const VARIANT_CLASS = {
    primary: 'ar-btn-action',
    success: 'ar-btn-activate',
    outline: 'ar-btn-ghost',
    danger: 'ar-btn-danger',
};
const STATUS_COLORS = {
    connected: tokens.success,
    disconnected: tokens.textTertiary,
    error: tokens.danger,
};
const STATUS_LABELS = {
    connected: 'Connected',
    disconnected: 'Not Connected',
    error: 'Error',
};
// Integration logo mapping: type → filename stem (without -dark/-light suffix)
const INTEGRATION_LOGO_MAP = {
    shopify: 'shopify-logo',
    zendesk: 'zendesk-logo',
    mailchimp: 'mailchimp-logo',
    google_analytics: 'google-analytics-logo',
    stripe: 'stripe-logo',
};
const DOCS_BASE = 'https://agentredcx.com/docs/admin-guide';
/** Per-integration tooltip text + doc link. */
const INTEGRATION_TOOLTIPS = {
    shopify: {
        text: 'Core commerce integration. Syncs products, orders, and customer data to power AI responses with real-time store information.',
        docLink: `${DOCS_BASE}/integrations#shopify`,
    },
    zendesk: {
        text: 'Route escalated conversations to Zendesk tickets. Requires Professional tier or above.',
        docLink: `${DOCS_BASE}/integrations#zendesk`,
    },
    mailchimp: {
        text: 'Sync customer emails and conversation insights to Mailchimp audiences for targeted marketing.',
        docLink: `${DOCS_BASE}/integrations#mailchimp`,
    },
    google_analytics: {
        text: 'Send conversation events and conversion data to Google Analytics 4 for unified reporting.',
        docLink: `${DOCS_BASE}/integrations#google-analytics`,
    },
};
// Fallback inline SVG icons (used if logo image fails to load)
const IntegrationIcons = {
    shopify: () => (_jsx("svg", { width: "80", height: "80", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "1.5", children: _jsx("path", { d: "M15.5 2.5L14 10l-3.5-1L7 17.5l-2-1L3 22h18l-2-8-3.5 1L15.5 2.5z" }) })),
    zendesk: () => (_jsxs("svg", { width: "80", height: "80", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "1.5", children: [_jsx("circle", { cx: "12", cy: "12", r: "9" }), _jsx("path", { d: "M8 15l4-6 4 6" })] })),
    mailchimp: () => (_jsxs("svg", { width: "80", height: "80", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "1.5", children: [_jsx("path", { d: "M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" }), _jsx("polyline", { points: "22,6 12,13 2,6" })] })),
    google_analytics: () => (_jsxs("svg", { width: "80", height: "80", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "1.5", children: [_jsx("line", { x1: "18", y1: "20", x2: "18", y2: "10" }), _jsx("line", { x1: "12", y1: "20", x2: "12", y2: "4" }), _jsx("line", { x1: "6", y1: "20", x2: "6", y2: "14" })] })),
    stripe: () => (_jsxs("svg", { width: "80", height: "80", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "1.5", children: [_jsx("rect", { x: "1", y: "4", width: "22", height: "16", rx: "2", ry: "2" }), _jsx("line", { x1: "1", y1: "10", x2: "23", y2: "10" })] })),
};
const cardStyle = {
    background: tokens.surface,
    border: `1px solid ${tokens.border}`,
    borderRadius: 8,
    padding: 16,
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'center',
    gap: 16,
};
const iconContainerStyle = {
    width: 180,
    height: 180,
    borderRadius: 8,
    background: tokens.page,
    border: `1px solid ${tokens.border}`,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: tokens.textMuted,
    flexShrink: 0,
    overflow: 'hidden',
};
const badgeStyle = (color) => ({
    display: 'inline-flex',
    alignItems: 'center',
    gap: 4,
    padding: '2px 8px',
    borderRadius: 10,
    fontSize: 11,
    fontWeight: 600,
    background: `${color}22`,
    color,
    border: `1px solid ${color}44`,
});
const tierBadgeStyle = {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 4,
    padding: '2px 8px',
    borderRadius: 10,
    fontSize: 11,
    fontWeight: 600,
    background: `${tokens.warning}22`,
    color: tokens.warning,
    border: `1px solid ${tokens.warning}44`,
};
const comingSoonBadgeStyle = {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 4,
    padding: '2px 8px',
    borderRadius: 10,
    fontSize: 11,
    fontWeight: 600,
    background: '#6366f122',
    color: '#818cf8',
    border: '1px solid #6366f144',
};
// Button component — uses CSS hover utility classes from tokens.css
const btnBase = {
    padding: '6px 14px',
    borderRadius: 6,
    fontSize: 13,
    fontWeight: 500,
};
const HoverButton = ({ variant, onClick, disabled, children }) => (_jsx("button", { className: VARIANT_CLASS[variant] || 'ar-btn-action', style: btnBase, onClick: onClick, disabled: disabled, children: children }));
const IntegrationCard = ({ integration, onActivate, onDeactivate, onDisconnect, activating, deactivating, isDark = true, basePath = '', apiFetch, tenantId, onNotify, onRefetch, }) => {
    const [showConfirm, setShowConfirm] = useState(false);
    const [logoError, setLogoError] = useState(false);
    const IconComponent = IntegrationIcons[integration.icon] || IntegrationIcons.shopify;
    const statusColor = STATUS_COLORS[integration.status || 'disconnected'] || tokens.textTertiary;
    const statusLabel = STATUS_LABELS[integration.status || 'disconnected'] || 'Not Configured';
    // Resolve logo path: dark variant for dark mode, light for light mode
    const logoStem = INTEGRATION_LOGO_MAP[integration.icon] || INTEGRATION_LOGO_MAP[integration.type];
    const logoSuffix = isDark ? 'dark' : 'light';
    const logoPath = logoStem ? `${basePath}/integration-logos/${logoStem}-${logoSuffix}.svg` : null;
    return (_jsxs("div", { style: cardStyle, children: [_jsx("div", { style: iconContainerStyle, children: logoPath && !logoError ? (_jsx("img", { src: logoPath, alt: `${integration.name} logo`, style: { objectFit: 'contain', display: 'block' }, onError: () => setLogoError(true) })) : (_jsx(IconComponent, {})) }), _jsxs("div", { style: { flex: 1, minWidth: 0 }, children: [_jsxs("div", { style: { display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }, children: [_jsxs("span", { style: { fontSize: 22, fontWeight: 600, color: tokens.textPrimary }, children: [integration.name, INTEGRATION_TOOLTIPS[integration.type] && (_jsx(HelpTooltip, { text: INTEGRATION_TOOLTIPS[integration.type].text, docLink: INTEGRATION_TOOLTIPS[integration.type].docLink }))] }), integration.status && (_jsxs("span", { style: badgeStyle(statusColor), children: [_jsx("span", { style: {
                                            width: 6,
                                            height: 6,
                                            borderRadius: '50%',
                                            background: statusColor,
                                            display: 'inline-block',
                                        } }), statusLabel] })), integration.comingSoon && (_jsx("span", { style: comingSoonBadgeStyle, children: "Coming Soon" })), !integration.comingSoon && !integration.tierMet && integration.tierGate && (_jsxs("span", { style: tierBadgeStyle, children: [String.fromCodePoint(0x2B06), " ", integration.tierGate, " tier"] }))] }), _jsx("p", { style: { margin: '4px 0 8px', fontSize: 13, color: tokens.textTertiary, lineHeight: 1.4 }, children: integration.description }), _jsx("div", { style: { display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }, children: integration.comingSoon ? (_jsx("span", { style: { fontSize: 12, color: '#818cf8' }, children: "This integration is under development and will be available soon." })) : !integration.tierMet ? (_jsxs("span", { style: { fontSize: 12, color: tokens.warning }, children: ["Upgrade to ", integration.tierGate, " to use this integration"] })) : integration.enabled ? (_jsxs(_Fragment, { children: [_jsx(HoverButton, { variant: "danger", onClick: () => onDeactivate(integration.type), disabled: deactivating, children: deactivating ? 'Deactivating...' : 'Deactivate' }), showConfirm ? (_jsxs("div", { style: { display: 'flex', gap: 6, alignItems: 'center' }, children: [_jsx("span", { style: { fontSize: 12, color: tokens.danger }, children: "Disconnect? This removes credentials." }), _jsx(HoverButton, { variant: "danger", onClick: () => { onDisconnect(integration.type); setShowConfirm(false); }, children: "Confirm" }), _jsx(HoverButton, { variant: "outline", onClick: () => setShowConfirm(false), children: "Cancel" })] })) : (_jsx(HoverButton, { variant: "danger", onClick: () => setShowConfirm(true), children: "Disconnect" }))] })) : (_jsx(HoverButton, { variant: "primary", onClick: () => onActivate(integration.type), disabled: activating, children: activating ? 'Activating...' : 'Activate' })) }), integration.type === 'stripe' && integration.enabled && apiFetch && tenantId && onNotify && (_jsx(McpConfigPanel, { tenantId: tenantId, apiFetch: apiFetch, onNotify: onNotify, onStatusChange: onRefetch })), integration.enabled && integration.status === 'connected' && (_jsxs("div", { style: {
                            marginTop: 8,
                            padding: '8px 12px',
                            background: tokens.page,
                            borderRadius: 6,
                            border: `1px solid ${tokens.border}`,
                            fontSize: 12,
                            color: tokens.textTertiary,
                            display: 'flex',
                            gap: 16,
                            alignItems: 'center',
                            flexWrap: 'wrap',
                        }, children: [integration.lastSyncAt && (_jsxs("span", { children: ["Last sync: ", new Date(integration.lastSyncAt).toLocaleString()] })), integration.lastSyncStatus === 'error' && (_jsx("span", { style: { color: tokens.danger }, children: "Sync error" })), typeof integration.ticketCount === 'number' && (_jsxs("span", { children: [integration.ticketCount.toLocaleString(), " tickets"] })), typeof integration.articleCount === 'number' && (_jsxs("span", { children: [integration.articleCount.toLocaleString(), " articles"] })), typeof integration.contactCount === 'number' && (_jsxs("span", { children: [integration.contactCount.toLocaleString(), " contacts"] }))] })), !integration.comingSoon && integration.tierMet && !integration.enabled && integration.authType === 'oauth2' && (_jsx("div", { style: { marginTop: 6 }, children: _jsx("span", { style: { fontSize: 11, color: tokens.textTertiary }, children: "OAuth setup required \u2014 click Activate to begin authorization" }) }))] })] }));
};
const detailPanelStyle = {
    background: tokens.surface,
    border: `1px solid ${tokens.border}`,
    borderRadius: 8,
    padding: 20,
    marginBottom: 16,
};
const tabStyle = (active) => ({
    padding: '6px 14px',
    fontSize: 13,
    fontWeight: active ? 600 : 400,
    color: active ? tokens.brand : tokens.textTertiary,
    background: active ? `${tokens.brand}11` : 'transparent',
    border: `1px solid ${active ? tokens.brand + '44' : 'transparent'}`,
    borderRadius: 6,
    cursor: 'pointer',
});
const IntegrationDetailPanel = ({ integration, apiFetch, onClose, onNotify, onRefetch, }) => {
    const [activeTab, setActiveTab] = useState('config');
    const [syncing, setSyncing] = useState(false);
    const handleSyncNow = useCallback(async () => {
        setSyncing(true);
        try {
            const res = await apiFetch(`/api/admin/integrations/${integration.type}/sync`, {
                method: 'POST',
            });
            if (res.ok) {
                onNotify('Sync started', 'success');
                onRefetch();
            }
            else {
                onNotify('Failed to start sync', 'error');
            }
        }
        catch {
            onNotify('Sync request failed', 'error');
        }
        finally {
            setSyncing(false);
        }
    }, [apiFetch, integration.type, onNotify, onRefetch]);
    return (_jsxs("div", { style: detailPanelStyle, children: [_jsxs("div", { style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }, children: [_jsxs("span", { style: { fontSize: 18, fontWeight: 600, color: tokens.textPrimary }, children: [integration.name, " \u2014 Details"] }), _jsx("button", { className: "ar-btn-ghost", style: { padding: '4px 10px', fontSize: 12 }, onClick: onClose, children: "Close" })] }), _jsx("div", { style: { display: 'flex', gap: 6, marginBottom: 16 }, children: ['config', 'sync', 'actions', 'logs'].map((tab) => (_jsx("button", { style: tabStyle(activeTab === tab), onClick: () => setActiveTab(tab), children: tab.charAt(0).toUpperCase() + tab.slice(1) }, tab))) }), activeTab === 'config' && (_jsxs("div", { style: { fontSize: 13, color: tokens.textSecondary }, children: [_jsxs("div", { style: { marginBottom: 8 }, children: [_jsx("strong", { children: "Category:" }), " ", integration.category || 'N/A'] }), _jsxs("div", { style: { marginBottom: 8 }, children: [_jsx("strong", { children: "Auth Type:" }), " ", integration.authType || 'N/A'] }), _jsxs("div", { style: { marginBottom: 8 }, children: [_jsx("strong", { children: "Capabilities:" }), ' ', integration.capabilities?.join(', ') || 'None listed'] }), _jsxs("div", { style: { marginBottom: 8 }, children: [_jsx("strong", { children: "Tier Gate:" }), " ", integration.tierGate || 'All tiers'] })] })), activeTab === 'sync' && (_jsxs("div", { style: { fontSize: 13, color: tokens.textSecondary }, children: [_jsxs("div", { style: { display: 'flex', gap: 12, alignItems: 'center', marginBottom: 12 }, children: [_jsx(HoverButton, { variant: "primary", onClick: handleSyncNow, disabled: syncing, children: syncing ? 'Syncing...' : 'Sync Now' }), integration.lastSyncAt && (_jsxs("span", { children: ["Last: ", new Date(integration.lastSyncAt).toLocaleString()] }))] }), _jsxs("div", { style: { display: 'flex', gap: 24 }, children: [typeof integration.ticketCount === 'number' && (_jsxs("div", { children: [_jsx("div", { style: { fontSize: 24, fontWeight: 600, color: tokens.textPrimary }, children: integration.ticketCount.toLocaleString() }), _jsx("div", { style: { fontSize: 11, color: tokens.textTertiary }, children: "Tickets" })] })), typeof integration.articleCount === 'number' && (_jsxs("div", { children: [_jsx("div", { style: { fontSize: 24, fontWeight: 600, color: tokens.textPrimary }, children: integration.articleCount.toLocaleString() }), _jsx("div", { style: { fontSize: 11, color: tokens.textTertiary }, children: "Articles" })] })), typeof integration.contactCount === 'number' && (_jsxs("div", { children: [_jsx("div", { style: { fontSize: 24, fontWeight: 600, color: tokens.textPrimary }, children: integration.contactCount.toLocaleString() }), _jsx("div", { style: { fontSize: 11, color: tokens.textTertiary }, children: "Contacts" })] }))] })] })), activeTab === 'actions' && (_jsxs("div", { style: { fontSize: 13, color: tokens.textSecondary }, children: [_jsx("p", { style: { marginBottom: 8 }, children: "Configure HITL (Human-in-the-Loop) policies for each action type." }), _jsx("div", { style: { fontSize: 12, color: tokens.textTertiary }, children: "Action configuration is loaded from the integration's backend settings. Toggle HITL policies to control which actions require human approval." })] })), activeTab === 'logs' && (_jsxs("div", { style: { fontSize: 13, color: tokens.textSecondary }, children: [_jsx("p", { style: { marginBottom: 8 }, children: "Connection logs for this integration." }), _jsxs("div", { style: {
                            fontSize: 12,
                            color: tokens.textTertiary,
                            fontFamily: 'monospace',
                            padding: 12,
                            background: tokens.page,
                            borderRadius: 4,
                            maxHeight: 200,
                            overflow: 'auto',
                        }, children: ["Logs are loaded from the integration events container. Use the API at /api/admin/integrations/", integration.type, "/events for programmatic access."] })] }))] }));
};
// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------
export const IntegrationsManager = ({ tenantContext, apiFetch, onNotify, isDark = true, basePath = '', }) => {
    const { data: integrations, loading, error, refetch } = useIntegrations(apiFetch);
    const { activate, loading: activating } = useActivateIntegration(apiFetch);
    const { deactivate, loading: deactivating } = useDeactivateIntegration(apiFetch);
    const { disconnect } = useDisconnectIntegration(apiFetch);
    const [actionTarget, setActionTarget] = useState(null);
    const [detailType, setDetailType] = useState(null);
    const handleActivate = useCallback(async (type) => {
        setActionTarget(type);
        const result = await activate(type);
        setActionTarget(null);
        if (result?.success) {
            onNotify(`${result.message}`, 'success');
            refetch();
        }
        else {
            onNotify('Failed to activate integration.', 'error');
        }
    }, [activate, onNotify, refetch]);
    const handleDeactivate = useCallback(async (type) => {
        setActionTarget(type);
        const result = await deactivate(type);
        setActionTarget(null);
        if (result?.success) {
            onNotify(`${result.message}`, 'success');
            refetch();
        }
        else {
            onNotify('Failed to deactivate integration.', 'error');
        }
    }, [deactivate, onNotify, refetch]);
    const handleDisconnect = useCallback(async (type) => {
        const result = await disconnect(type);
        if (result?.success) {
            onNotify(`${result.message}`, 'success');
            refetch();
        }
        else {
            onNotify('Failed to disconnect integration.', 'error');
        }
    }, [disconnect, onNotify, refetch]);
    // ----- Loading / Error states -----
    if (loading) {
        return (_jsx("div", { style: { padding: 40, textAlign: 'center', color: tokens.textTertiary }, children: "Loading integrations..." }));
    }
    if (error) {
        return (_jsxs("div", { style: { padding: 40, textAlign: 'center', color: tokens.danger }, children: ["Failed to load integrations: ", error] }));
    }
    const items = integrations ?? [];
    const detailIntegration = detailType
        ? items.find((i) => i.type === detailType) ?? null
        : null;
    return (_jsxs("div", { style: { maxWidth: 800 }, children: [detailIntegration && (_jsx(IntegrationDetailPanel, { integration: detailIntegration, apiFetch: apiFetch, onClose: () => setDetailType(null), onNotify: onNotify, onRefetch: refetch })), _jsx("div", { style: { display: 'flex', flexDirection: 'column', gap: 12 }, children: items.map((integration) => (_jsxs("div", { children: [_jsx(IntegrationCard, { integration: integration, onActivate: handleActivate, onDeactivate: handleDeactivate, onDisconnect: handleDisconnect, activating: activating && actionTarget === integration.type, deactivating: deactivating && actionTarget === integration.type, isDark: isDark, basePath: basePath, apiFetch: apiFetch, tenantId: tenantContext.tenantId, onNotify: onNotify, onRefetch: refetch }), integration.enabled && integration.status === 'connected' && (_jsx("div", { style: { marginTop: 4, textAlign: 'right' }, children: _jsx("button", { className: "ar-btn-ghost", style: { padding: '3px 10px', fontSize: 11 }, onClick: () => setDetailType(detailType === integration.type ? null : integration.type), children: detailType === integration.type ? 'Hide Details' : 'View Details' }) }))] }, integration.type))) }), items.length === 0 && (_jsx("div", { style: {
                    padding: 40,
                    textAlign: 'center',
                    color: tokens.textTertiary,
                    background: tokens.surface,
                    border: `1px solid ${tokens.border}`,
                    borderRadius: 8,
                }, children: "No integrations available." })), _jsxs("div", { style: { marginTop: 16, fontSize: 12, color: tokens.textTertiary }, children: [items.filter((i) => i.enabled).length, " of ", items.length, " integrations active", tenantContext.tier === 'starter' || tenantContext.tier === 'trial' ? (_jsxs("span", { children: [" ", String.fromCodePoint(0x2022), " Some integrations require Professional tier or above"] })) : null] })] }));
};
//# sourceMappingURL=IntegrationsManager.js.map