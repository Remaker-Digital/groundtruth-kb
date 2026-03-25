import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * StandaloneLayout — Mantine AppShell with sidebar navigation.
 *
 * Merges prototype StandaloneApp visual layout with production AppContext:
 *   - Mantine AppShell (260px navbar, 56px header)
 *   - 9 SVG nav icons, dark mode toggle, brand logo + wordmark
 *   - Remaker Digital footer with version
 *   - AppContext.Provider with apiFetch (X-API-Key injection)
 *   - Tenant context resolution from API key
 *   - Mantine notifications.show() instead of banner notifications
 *
 * Four-tier dark mode hierarchy (designer-approved):
 *   chrome #0c0a09 → page #1c1917 → surface #292524 → border #44403c
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useQueryPreservingNavigate } from '../hooks/useQueryPreservingNavigate';
import { AppShell, NavLink, Group, Text, ThemeIcon, Badge, Box, Burger, Tooltip, ActionIcon, Modal, Button, Stack, Select, Textarea, TextInput, useMantineColorScheme, useComputedColorScheme, } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { notifications } from '@mantine/notifications';
import { Icons } from '../../shared/icons';
import ActivationDialog from '../../shared/ActivationDialog';
import RestoreDialog from '../../shared/RestoreDialog';
import { OnboardingWizard } from '../../shared/components/OnboardingWizard';
import { tokens } from '../../shared/theme/styles';
// ---------------------------------------------------------------------------
// Context
// ---------------------------------------------------------------------------
const AppContext = createContext(null);
export function useAppContext() {
    const ctx = useContext(AppContext);
    if (!ctx)
        throw new Error('useAppContext must be used within StandaloneLayout');
    return ctx;
}
// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------
const API_BASE_URL = import.meta.env?.VITE_API_URL || '';
const DOCS_URL = 'https://agentredcx.com';
/** Tier-dependent badge colors for the header plan indicator. */
const TIER_BADGE_COLORS = {
    trial: 'yellow',
    starter: 'blue',
    professional: 'green',
    enterprise: 'grape',
};
/** Short labels for nav tier badges (used in top-bar plan display). */
const TIER_BADGE_LABELS = {
    trial: 'Trial',
    starter: 'Starter',
    professional: 'Professional',
    enterprise: 'Enterprise',
};
/** Nav items rendered BEFORE the configuration group. */
const navItemsBefore = [
    { path: '/', label: 'Dashboard', icon: 'dashboard', roles: ['superadmin', 'admin', 'viewer'] },
    { path: '/inbox', label: 'Inbox', icon: 'inbox' },
    { path: '/team', label: 'Team members', icon: 'team', roles: ['superadmin', 'admin'] },
];
/** Pages participating in the Save→Activate lifecycle (grouped in sidebar). */
const configGroupItems = [
    { path: '/configuration', label: 'Agent configuration', icon: 'config', roles: ['superadmin', 'admin'] },
    { path: '/knowledge-base', label: 'Knowledge base', icon: 'knowledge', roles: ['superadmin', 'admin'] },
    { path: '/quick-actions', label: 'Quick actions', icon: 'quickactions', roles: ['superadmin', 'admin'] },
    { path: '/widget', label: 'Widget configuration', icon: 'widget', roles: ['superadmin', 'admin'] },
];
/** Nav items rendered AFTER the configuration group. */
const navItemsAfter = [
    { path: '/integrations', label: 'Integrations', icon: 'integrations', roles: ['superadmin', 'admin'] },
    { path: '/memory-privacy', label: 'Memory & privacy', icon: 'memory', roles: ['superadmin', 'admin'] },
    { path: '/billing', label: 'Account & billing', icon: 'billing', roles: ['superadmin', 'admin'] },
];
// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export const StandaloneLayout = ({ apiKey: legacyApiKey, auth, onLogout, children, }) => {
    // Resolve auth credential — prefer `auth` prop, fall back to legacy `apiKey`
    const resolvedAuth = auth ?? { type: 'api_key', value: legacyApiKey ?? '' };
    const location = useLocation();
    const navigate = useQueryPreservingNavigate();
    const [opened, { toggle }] = useDisclosure();
    const { setColorScheme } = useMantineColorScheme();
    const computedColorScheme = useComputedColorScheme('dark');
    const isDark = computedColorScheme === 'dark';
    const [tenantContext, setTenantContext] = useState(null);
    const [productVersion, setProductVersion] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    // ---- Contact Us modal state --------------------------------------------
    const [contactOpened, contactHandlers] = useDisclosure(false);
    const [contactTopic, setContactTopic] = useState('support');
    const [contactSubject, setContactSubject] = useState('');
    const [contactMessage, setContactMessage] = useState('');
    const [contactSending, setContactSending] = useState(false);
    // ---- Authenticated fetch -----------------------------------------------
    const apiFetch = useCallback(async (path, init) => {
        const headers = new Headers(init?.headers);
        if (resolvedAuth.type === 'session_token') {
            headers.set('X-Session-Token', resolvedAuth.value);
        }
        else {
            headers.set('X-API-Key', resolvedAuth.value);
        }
        const resp = await fetch(`${API_BASE_URL}${path}`, {
            ...init,
            headers,
        });
        // Global auth-failure interceptor: any 401/403 redirects to login
        if (resp.status === 401 || resp.status === 403) {
            onLogout();
        }
        return resp;
    }, [resolvedAuth.type, resolvedAuth.value, onLogout]);
    // ---- Notification handler (Mantine notifications) ----------------------
    const onNotify = useCallback((message, type) => {
        const colorMap = {
            success: 'green',
            error: 'red',
            warning: 'yellow',
            info: 'blue',
        };
        const titleMap = {
            success: 'Success',
            error: 'Error',
            warning: 'Warning',
            info: 'Info',
        };
        notifications.show({
            title: titleMap[type] || 'Notice',
            message,
            color: colorMap[type] || 'blue',
            autoClose: type === 'error' ? 8000 : 5000,
        });
    }, []);
    // ---- Tenant context resolution (SPEC-1644) -----------------------------
    // The ?tenant= URL parameter identifies the tenant.  API keys MUST NOT
    // be used to discover tenants.  We validate the key against the URL
    // tenant via POST /api/tenants/auth/validate-key (partition-scoped).
    useEffect(() => {
        let cancelled = false;
        async function resolveTenant() {
            try {
                // SPEC-1644: tenant comes from the URL, never from the key
                const urlTenant = new URL(window.location.href).searchParams.get('tenant');
                if (!urlTenant) {
                    // No tenant in URL — cannot authenticate.  Redirect to login
                    // so the user can provide their tenant slug + credential.
                    onLogout();
                    return;
                }
                const resp = await apiFetch('/api/tenants/auth/validate-key', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ tenant: urlTenant }),
                });
                if (!resp.ok) {
                    if (resp.status === 400 || resp.status === 401 || resp.status === 403) {
                        // Invalid or revoked credential for this tenant
                        onLogout();
                        return;
                    }
                    throw new Error(`Tenant validation failed: ${resp.status}`);
                }
                const data = await resp.json();
                if (!cancelled) {
                    // Capture product version from response header (set by ApiVersionMiddleware)
                    const pv = resp.headers.get('x-product-version');
                    if (pv)
                        setProductVersion(pv);
                    setTenantContext({
                        tenantId: data.tenant_id,
                        tier: data.tier,
                        status: data.status,
                        billingChannel: (data.billing_channel || 'stripe'),
                        hasStripeBilling: data.has_stripe_billing ?? false,
                        shopDomain: data.shopify_shop_domain || undefined,
                        brandName: data.brand_name || undefined,
                    });
                    // SPEC-1617: Normalize the tenant slug in the URL.
                    // Prefer shop domain (already unique, e.g. "blanco-9939"); fall
                    // back to brand name slugified; last resort use tenant_id.
                    const slug = (data.shopify_shop_domain || '').replace(/\.myshopify\.com$/i, '') ||
                        (data.brand_name || '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') ||
                        data.tenant_id || '';
                    if (slug) {
                        const url = new URL(window.location.href);
                        if (url.searchParams.get('tenant') !== slug) {
                            url.searchParams.set('tenant', slug);
                            window.history.replaceState(null, '', url.toString());
                        }
                    }
                    setLoading(false);
                }
            }
            catch (err) {
                if (!cancelled) {
                    setError(err instanceof Error ? err.message : 'Failed to load');
                    setLoading(false);
                }
            }
        }
        resolveTenant();
        return () => { cancelled = true; };
    }, [apiFetch, onLogout]);
    // ---- Contact Us submit handler ------------------------------------------
    const handleContactSubmit = useCallback(async () => {
        if (!contactTopic || !contactSubject.trim() || !contactMessage.trim())
            return;
        setContactSending(true);
        try {
            const resp = await apiFetch('/api/admin/contact', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    topic: contactTopic,
                    subject: contactSubject.trim(),
                    message: contactMessage.trim(),
                }),
            });
            if (resp.ok) {
                notifications.show({ title: 'Message sent', message: 'We\'ll get back to you shortly.', color: 'green' });
                contactHandlers.close();
                setContactTopic('support');
                setContactSubject('');
                setContactMessage('');
            }
            else {
                const data = await resp.json().catch(() => ({ detail: 'Unexpected error' }));
                notifications.show({ title: 'Failed to send', message: data.detail || 'Please try again.', color: 'red' });
            }
        }
        catch {
            notifications.show({ title: 'Network error', message: 'Please check your connection and try again.', color: 'red' });
        }
        finally {
            setContactSending(false);
        }
    }, [apiFetch, contactTopic, contactSubject, contactMessage, contactHandlers]);
    // ---- Caller role resolution (whoami) ------------------------------------
    const [userRole, setUserRole] = useState(null);
    const [userEmail, setUserEmail] = useState(null);
    useEffect(() => {
        if (!tenantContext)
            return;
        apiFetch('/api/admin/team/whoami')
            .then(async (resp) => {
            if (!resp.ok) {
                // Fallback: treat as admin (legacy tenant API key or endpoint not deployed yet)
                setUserRole('admin');
                return;
            }
            const data = await resp.json();
            setUserRole(data.role || 'admin');
            setUserEmail(data.email || null);
        })
            .catch(() => {
            setUserRole('admin'); // Graceful fallback
        });
    }, [tenantContext, apiFetch]);
    // ---- Activation state (sidebar config group) --------------------------------
    const [showActivationDialog, setShowActivationDialog] = useState(false);
    const [showDeactivateDialog, setShowDeactivateDialog] = useState(false);
    const [showRestoreDialog, setShowRestoreDialog] = useState(false);
    const [deactivating, setDeactivating] = useState(false);
    const [activationRefreshKey, setActivationRefreshKey] = useState(0);
    const [activationStatus, setActivationStatus] = useState(null);
    const [discarding, setDiscarding] = useState(false);
    const [configRefreshKey, setConfigRefreshKey] = useState(0);
    // Poll activation status every 30s (replaces ActivationBanner's internal polling)
    const fetchActivationStatus = useCallback(async () => {
        try {
            const res = await apiFetch('/api/config/activation-status');
            if (res.ok) {
                const data = await res.json();
                setActivationStatus(data);
            }
        }
        catch { /* silent — polling failure is non-fatal */ }
    }, [apiFetch]);
    useEffect(() => {
        if (!tenantContext)
            return;
        fetchActivationStatus();
        const interval = setInterval(fetchActivationStatus, 30000);
        return () => clearInterval(interval);
    }, [tenantContext, fetchActivationStatus, activationRefreshKey]);
    // ---- Activation status check (WI #291) -----------------------------------
    // Derived from activationStatus polling (D34 fix: previously checked version>0
    // which was true even for DRAFT-state tenants that were never activated).
    // Now uses is_configured from the activation-status endpoint, which verifies
    // the active config has all mandatory fields (brand_name, widget_key).
    // D34 re-fix: isActivated = true ONLY when there's an active config
    // that has been activated AND has all mandatory fields. A fresh tenant
    // that has never been activated returns false.
    const isActivated = (activationStatus?.is_configured === true
        && activationStatus?.active_activated_at != null) ? true : (activationStatus != null ? false : null);
    // ---- Onboarding wizard (WI #292 / WI-E4) — first-time merchants --------
    // Uses sessionStorage so the wizard re-appears on each new browser session
    // if the tenant is still unconfigured. Once activated, isActivated === true
    // and the wizard never shows regardless of storage state.
    const [showOnboarding, setShowOnboarding] = useState(false);
    useEffect(() => {
        if (isActivated !== false)
            return; // Only show when explicitly not activated
        try {
            // WI-CP3: When tenant has NEVER been activated (version 0), always show
            // the wizard regardless of sessionStorage state.  This prevents stale
            // dismiss flags from hiding the wizard after tenant re-provisioning
            // or when a new tenant is served to the same browser tab.
            if (activationStatus?.active_version === 0) {
                sessionStorage.removeItem('agentred-onboarding-dismissed');
                setShowOnboarding(true);
                return;
            }
            const dismissed = sessionStorage.getItem('agentred-onboarding-dismissed');
            if (!dismissed)
                setShowOnboarding(true);
        }
        catch { /* ignore */ }
    }, [isActivated, activationStatus?.active_version]);
    const dismissOnboarding = useCallback(() => {
        setShowOnboarding(false);
        try {
            sessionStorage.setItem('agentred-onboarding-dismissed', '1');
        }
        catch { /* ignore */ }
    }, []);
    // Discard all draft changes (confirm → POST → refresh)
    const handleDiscard = useCallback(async () => {
        if (!confirm('Discard all draft changes? This cannot be undone.'))
            return;
        setDiscarding(true);
        try {
            const res = await apiFetch('/api/config/draft/discard', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: '{}',
            });
            if (res.ok) {
                onNotify('Draft changes discarded', 'info');
                setActivationRefreshKey((k) => k + 1);
                setConfigRefreshKey((k) => k + 1);
            }
            else {
                onNotify('Failed to discard draft', 'error');
            }
        }
        catch {
            onNotify('Network error discarding draft', 'error');
        }
        finally {
            setDiscarding(false);
        }
    }, [apiFetch, onNotify]);
    // Config group visible only for superadmin / admin
    const canSeeConfigGroup = !userRole || ['superadmin', 'admin'].includes(userRole);
    // ---- Chat widget injection (auto-embed for admin users) ----------------
    // Widget is shown only when the tenant is Active (is_active === true).
    // Reacts to activation status changes so Activate/Deactivate toggles the
    // widget immediately without requiring a page refresh. (D53 fix)
    useEffect(() => {
        if (!tenantContext)
            return;
        const isActive = activationStatus?.is_active === true;
        // --- Remove widget when not active ---
        if (!isActive) {
            const existing = document.getElementById('agent-red-admin-widget');
            if (existing)
                existing.remove();
            const sdk = window.AgentRed;
            if (sdk?.destroy)
                sdk.destroy();
            return;
        }
        // --- Force re-inject on config changes (e.g. activation) ---
        const existing = document.getElementById('agent-red-admin-widget');
        if (existing) {
            existing.remove();
            const oldSdk = window.AgentRed;
            if (oldSdk?.destroy)
                oldSdk.destroy();
        }
        // Resolve API base URL — same origin as admin or explicit VITE_API_URL
        const apiUrl = API_BASE_URL || window.location.origin;
        // Fetch the tenant's widget key and appearance config from the config endpoint
        async function injectWidget() {
            try {
                const resp = await apiFetch('/api/config?page_type=all');
                if (!resp.ok)
                    return;
                const cfg = await resp.json();
                const config = cfg?.config || {};
                const widgetKey = config.widget_key || cfg?.preferences?.widget_key || cfg?.widget_key;
                if (!widgetKey) {
                    console.warn('[AgentRed Admin] No widget key found in tenant config — chat widget not loaded.');
                    return;
                }
                // Create the widget script tag with admin-specific overrides
                const script = document.createElement('script');
                script.id = 'agent-red-admin-widget';
                // In dev mode, use base-relative URL so Vite serves the local build from public/
                script.src = import.meta.env.DEV ? `${import.meta.env.BASE_URL}widget.js` : `${apiUrl}/widget.js`;
                script.setAttribute('data-widget-key', widgetKey);
                script.setAttribute('data-api-url', apiUrl);
                script.setAttribute('data-auto-open', 'false');
                script.setAttribute('data-auto-open-delay', '0');
                script.setAttribute('data-context', 'admin');
                // SPEC-1562: Co-pilot mode greeting and branding overrides
                const isCoPilot = resolvedAuth.type === 'api_key' && resolvedAuth.value;
                script.setAttribute('data-greeting', isCoPilot
                    ? 'Hi! I\u2019m your Agent Red Co-pilot. I can help you with admin tasks, configuration, analytics, and platform features. What would you like to know?'
                    : (config.greeting_message
                        || 'Hi! I\u2019m your Agent Red AI assistant. Ask me anything about managing your store, configuring the widget, or understanding your analytics.'));
                script.setAttribute('data-header-text', isCoPilot ? 'Agent Red Co-pilot' : (config.widget_header_text || 'Agent Red Assistant'));
                script.setAttribute('data-agent-name', isCoPilot ? 'Co-pilot' : (config.widget_agent_display_name || 'Agent Red AI'));
                script.setAttribute('data-sound-enabled', 'false');
                // SPEC-1562: Pass admin API key for Co-pilot mode. When set, the
                // widget authenticates as a team member, routing messages to the
                // Co-pilot agent instead of the customer-facing pipeline.
                if (resolvedAuth.type === 'api_key' && resolvedAuth.value) {
                    script.setAttribute('data-admin-key', resolvedAuth.value);
                }
                // Pass widget appearance fields so the widget renders with tenant
                // brand colors immediately (without waiting for its own /api/config fetch)
                const appearanceMap = [
                    ['data-color', 'widget_primary_color'],
                    ['data-position', 'widget_position'],
                ];
                for (const [dataAttr, configKey] of appearanceMap) {
                    const val = config[configKey];
                    if (val != null && typeof val === 'string' && val.length > 0) {
                        script.setAttribute(dataAttr, val);
                    }
                }
                document.body.appendChild(script);
            }
            catch (err) {
                console.warn('[AgentRed Admin] Could not load chat widget:', err);
            }
        }
        injectWidget();
        // Cleanup on unmount
        return () => {
            const existing = document.getElementById('agent-red-admin-widget');
            if (existing)
                existing.remove();
            const sdk = window.AgentRed;
            if (sdk?.destroy)
                sdk.destroy();
        };
    }, [tenantContext, apiFetch, activationStatus?.is_active, configRefreshKey]);
    // ---- Draft config preview on Agent Configuration page -------------------
    // When the admin is on /configuration, swap the widget to show draft config
    // so they can preview unsaved changes. Restore active config on navigation
    // away. Re-fetches on configRefreshKey changes (save/discard/activate).
    useEffect(() => {
        if (!tenantContext)
            return;
        const isActive = activationStatus?.is_active === true;
        if (!isActive)
            return; // Widget not loaded — nothing to swap
        const sdk = window.AgentRed;
        if (!sdk?.setConfigPartial)
            return;
        const onConfigPage = location.pathname === '/configuration';
        let cancelled = false;
        async function applyConfig() {
            try {
                // Draft config for the Configuration page; active config for all other pages
                const endpoint = onConfigPage
                    ? '/api/config?state=draft'
                    : '/api/config?page_type=all';
                const resp = await apiFetch(endpoint);
                if (cancelled || !resp.ok)
                    return;
                const data = await resp.json();
                const config = data?.config || {};
                // Extract widget-relevant fields for setConfigPartial
                const overrides = {};
                for (const [key, val] of Object.entries(config)) {
                    if (key.startsWith('widget_') && val != null) {
                        overrides[key] = val;
                    }
                }
                // Map non-prefixed fields the widget recognizes
                if (config.greeting_message != null) {
                    overrides.widget_greeting_message = config.greeting_message;
                }
                if (config.brand_name != null) {
                    overrides.brand_name = config.brand_name;
                }
                if (!cancelled && sdk?.setConfigPartial) {
                    sdk.setConfigPartial(overrides);
                }
            }
            catch {
                // Non-fatal — widget continues with current config
            }
        }
        applyConfig();
        return () => { cancelled = true; };
    }, [tenantContext, apiFetch, activationStatus?.is_active, location.pathname, configRefreshKey]);
    // ---- Context value -----------------------------------------------------
    const contextValue = {
        tenantContext,
        userRole,
        userEmail,
        productVersion,
        apiFetch,
        onNotify,
        loading,
        refreshActivationStatus: fetchActivationStatus,
        configRefreshKey,
        activationStatus,
    };
    // ---- Render ------------------------------------------------------------
    return (_jsxs(AppContext.Provider, { value: contextValue, children: [_jsxs(AppShell, { header: { height: 56 }, navbar: { width: 260, breakpoint: 'sm', collapsed: { mobile: !opened } }, padding: "md", styles: {
                    header: {
                        borderBottom: isDark ? `1px solid ${tokens.border}` : `1px solid ${tokens.surface}`,
                        background: tokens.chrome,
                    },
                    navbar: {
                        borderRight: isDark ? `1px solid ${tokens.border}` : undefined,
                        background: isDark ? tokens.chrome : undefined,
                    },
                    main: {
                        background: isDark ? tokens.page : undefined,
                        paddingBottom: 100, /* clearance for chat widget launcher */
                    },
                }, children: [_jsx(AppShell.Header, { children: _jsxs(Group, { h: "100%", px: "md", justify: "space-between", children: [_jsxs(Group, { children: [_jsx(Burger, { opened: opened, onClick: toggle, hiddenFrom: "sm", size: "sm" }), _jsx(Tooltip, { label: "Agent Red Customer Experience", position: "bottom", openDelay: 500, children: _jsxs(Group, { gap: 10, align: "center", style: { cursor: 'default' }, children: [_jsx("img", { src: "/admin/standalone/primary-logo-no-wordmark.svg", alt: "Agent Red", style: { height: 28, display: 'block' } }), _jsx(Text, { size: "sm", fw: 500, c: "gray.4", style: { letterSpacing: '0.02em', userSelect: 'none' }, children: "Customer Experience" })] }) })] }), _jsxs(Group, { gap: "sm", children: [tenantContext && (tenantContext.shopDomain ? (_jsx(Tooltip, { label: `Open ${tenantContext.shopDomain}`, position: "bottom", children: _jsxs("a", { href: `https://${tenantContext.shopDomain}`, target: "_blank", rel: "noopener noreferrer", className: "ar-link-shop", "data-testid": "navbar-tenant-identity", style: {
                                                    display: 'flex',
                                                    alignItems: 'center',
                                                    gap: 6,
                                                    textDecoration: 'none',
                                                    color: tokens.textMuted,
                                                    padding: '4px 10px',
                                                    borderRadius: 6,
                                                    background: 'var(--ar-storefront-link-bg)',
                                                    fontSize: 13,
                                                }, children: [_jsx(Icons.storefront, {}), _jsx("span", { style: { maxWidth: 180, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }, children: tenantContext.shopDomain.replace('.myshopify.com', '') }), _jsx(Icons.externalLink, {})] }) })) : (_jsxs("span", { className: "ar-link-shop", "data-testid": "navbar-tenant-identity", style: {
                                                display: 'flex',
                                                alignItems: 'center',
                                                gap: 6,
                                                color: tokens.textMuted,
                                                padding: '4px 10px',
                                                borderRadius: 6,
                                                background: 'var(--ar-storefront-link-bg)',
                                                fontSize: 13,
                                            }, children: [_jsx(Icons.storefront, {}), _jsx("span", { style: { maxWidth: 180, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }, children: tenantContext.brandName || tenantContext.tenantId })] }))), tenantContext && (_jsx(Tooltip, { label: `Your current plan: ${tenantContext.tier.charAt(0).toUpperCase() + tenantContext.tier.slice(1)}. Plans available: Starter ($149/mo), Professional ($399/mo), Enterprise ($999/mo).`, position: "bottom", multiline: true, w: 280, openDelay: 300, children: _jsx(Badge, { variant: "light", color: TIER_BADGE_COLORS[tenantContext.tier] ?? 'gray', size: "sm", style: { cursor: 'default' }, children: TIER_BADGE_LABELS[tenantContext.tier] ?? tenantContext.tier }) })), _jsx(Tooltip, { label: "Documentation", position: "bottom", children: _jsx(ActionIcon, { variant: "subtle", size: "md", component: "a", href: DOCS_URL, target: "_blank", rel: "noopener noreferrer", "aria-label": "Open documentation", style: {
                                                    color: tokens.textMuted,
                                                    border: '1px solid var(--ar-icon-btn-border)',
                                                    background: 'var(--ar-icon-btn-bg)',
                                                }, children: _jsx(Icons.docs, {}) }) }), _jsx(Tooltip, { label: "Contact us", position: "bottom", children: _jsx(ActionIcon, { variant: "subtle", size: "md", onClick: contactHandlers.open, "aria-label": "Contact us", style: {
                                                    color: tokens.textMuted,
                                                    border: '1px solid var(--ar-icon-btn-border)',
                                                    background: 'var(--ar-icon-btn-bg)',
                                                }, children: _jsx(Icons.contact, {}) }) }), _jsx(ActionIcon, { variant: "subtle", size: "md", onClick: () => setColorScheme(isDark ? 'light' : 'dark'), "aria-label": "Toggle dark mode", style: {
                                                color: tokens.textMuted,
                                                border: '1px solid var(--ar-icon-btn-border)',
                                                background: 'var(--ar-icon-btn-bg)',
                                            }, children: isDark ? _jsx(Icons.sun, {}) : _jsx(Icons.moon, {}) }), _jsx(ActionIcon, { variant: "subtle", size: "md", onClick: onLogout, "aria-label": "Sign out", style: {
                                                color: tokens.textMuted,
                                                border: '1px solid var(--ar-icon-btn-border)',
                                                background: 'var(--ar-icon-btn-bg)',
                                            }, children: _jsx(Icons.logout, { size: 16 }) })] })] }) }), _jsxs(AppShell.Navbar, { p: "xs", children: [_jsxs(AppShell.Section, { grow: true, children: [navItemsBefore
                                        .filter((item) => !item.roles || !userRole || item.roles.includes(userRole))
                                        .map((item) => {
                                        const IconComponent = Icons[item.icon];
                                        const isActive = location.pathname === item.path
                                            || (item.path !== '/' && location.pathname.startsWith(item.path));
                                        return (_jsx(NavLink, { label: item.label, leftSection: _jsx(ThemeIcon, { variant: isActive ? 'filled' : isDark ? 'default' : 'light', size: "sm", color: isActive ? 'brand.5' : 'gray', style: !isActive && isDark ? { background: 'transparent', border: 'none' } : undefined, children: _jsx(IconComponent, {}) }), rightSection: item.badge ? (_jsx(Badge, { size: "xs", variant: "filled", color: "brand.5", circle: true, children: item.badge })) : undefined, active: isActive, onClick: () => navigate(item.path), styles: { label: isActive && isDark ? { color: tokens.textPrimary } : undefined }, style: {
                                                borderRadius: 8,
                                                marginBottom: 2,
                                                ...(isActive && isDark ? { background: tokens.surface, border: `1px solid ${tokens.border}` } : {}),
                                            } }, item.path));
                                    }), canSeeConfigGroup && (_jsxs(Box, { style: {
                                            border: `1px solid ${isDark ? tokens.border : '#e0e0e0'}`,
                                            borderRadius: 8,
                                            padding: '8px 6px',
                                            margin: '4px 0',
                                            background: isDark ? 'rgba(41, 37, 36, 0.4)' : 'rgba(0, 0, 0, 0.02)',
                                        }, children: [_jsxs(Group, { justify: "space-between", px: 10, py: 4, pb: 6, children: [_jsx(Text, { size: "xs", fw: 600, c: "dimmed", tt: "uppercase", style: { letterSpacing: '0.5px', fontSize: 10 }, children: "AI Configuration" }), activationStatus && (activationStatus.is_active && !activationStatus.has_pending_changes ? (_jsx(Badge, { size: "xs", variant: "dot", color: "green", children: "Active" })) : !activationStatus.is_active
                                                        && activationStatus.is_configured
                                                        && !activationStatus.has_pending_changes
                                                        && activationStatus.active_activated_at != null ? (_jsx(Badge, { size: "xs", variant: "dot", color: "red", children: "Inactive" })) : (_jsx(Badge, { size: "xs", variant: "dot", color: "yellow", children: "Pending" })))] }), configGroupItems.map((item) => {
                                                const IconComponent = Icons[item.icon];
                                                const isActive = location.pathname === item.path
                                                    || (item.path !== '/' && location.pathname.startsWith(item.path));
                                                return (_jsx(NavLink, { label: item.label, leftSection: _jsx(ThemeIcon, { variant: isActive ? 'filled' : isDark ? 'default' : 'light', size: "sm", color: isActive ? 'brand.5' : 'gray', style: !isActive && isDark ? { background: 'transparent', border: 'none' } : undefined, children: _jsx(IconComponent, {}) }), active: isActive, onClick: () => navigate(item.path), styles: { label: isActive && isDark ? { color: tokens.textPrimary } : undefined }, style: {
                                                        borderRadius: 8,
                                                        marginBottom: 2,
                                                        ...(isActive && isDark ? { background: tokens.surface, border: `1px solid ${tokens.border}` } : {}),
                                                    } }, item.path));
                                            }), _jsx(NavLink, { label: "Setup wizard", leftSection: _jsx(ThemeIcon, { variant: isDark ? 'default' : 'light', size: "sm", color: "gray", style: isDark ? { background: 'transparent', border: 'none' } : undefined, children: _jsx("svg", { width: "16", height: "16", viewBox: "0 0 16 16", fill: "none", xmlns: "http://www.w3.org/2000/svg", children: _jsx("path", { d: "M8 0L9.8 6.2L16 8L9.8 9.8L8 16L6.2 9.8L0 8L6.2 6.2L8 0Z", fill: "currentColor" }) }) }), onClick: () => setShowOnboarding(true), style: { borderRadius: 8, marginBottom: 2 } }), _jsxs(Group, { gap: 4, px: 4, pt: 6, pb: 2, wrap: "nowrap", style: {
                                                    borderTop: `1px solid ${isDark ? tokens.border : '#e0e0e0'}`,
                                                    marginTop: 4,
                                                }, children: [_jsx(Button, { size: "compact-xs", variant: "filled", color: 
                                                        /* D44: Three-disposition activation control.
                                                           Red "Deactivate" = active with no pending changes.
                                                           Green "Activate" = ready to activate (can_activate from draft preflight).
                                                           Yellow "Activate" = activation blocked (missing mandatory fields). */
                                                        activationStatus?.is_active && !activationStatus?.has_pending_changes
                                                            ? 'red'
                                                            : activationStatus?.can_activate
                                                                ? 'green'
                                                                : 'yellow', onClick: () => {
                                                            if (activationStatus?.is_active && !activationStatus?.has_pending_changes) {
                                                                setShowDeactivateDialog(true);
                                                            }
                                                            else {
                                                                setShowActivationDialog(true);
                                                            }
                                                        }, style: { flex: 1 }, children: activationStatus?.is_active && !activationStatus?.has_pending_changes
                                                            ? 'Deactivate'
                                                            : 'Activate' }), _jsx(Button, { size: "compact-xs", variant: activationStatus?.has_pending_changes ? 'light' : 'default', color: activationStatus?.has_pending_changes ? 'blue' : undefined, disabled: !activationStatus?.has_pending_changes || discarding, onClick: handleDiscard, children: discarding ? '\u2026' : 'Discard' }), _jsx(Button, { size: "compact-xs", variant: "default", disabled: !activationStatus || activationStatus.active_version < 2, onClick: () => setShowRestoreDialog(true), children: "Roll back" })] })] })), navItemsAfter
                                        .filter((item) => !item.roles || !userRole || item.roles.includes(userRole))
                                        .map((item) => {
                                        const IconComponent = Icons[item.icon];
                                        const isActive = location.pathname === item.path
                                            || (item.path !== '/' && location.pathname.startsWith(item.path));
                                        return (_jsx(NavLink, { label: item.label, leftSection: _jsx(ThemeIcon, { variant: isActive ? 'filled' : isDark ? 'default' : 'light', size: "sm", color: isActive ? 'brand.5' : 'gray', style: !isActive && isDark ? { background: 'transparent', border: 'none' } : undefined, children: _jsx(IconComponent, {}) }), rightSection: item.badge ? (_jsx(Badge, { size: "xs", variant: "filled", color: "brand.5", circle: true, children: item.badge })) : undefined, active: isActive, onClick: () => navigate(item.path), styles: { label: isActive && isDark ? { color: tokens.textPrimary } : undefined }, style: {
                                                borderRadius: 8,
                                                marginBottom: 2,
                                                ...(isActive && isDark ? { background: tokens.surface, border: `1px solid ${tokens.border}` } : {}),
                                            } }, item.path));
                                    })] }), _jsx(AppShell.Section, { children: _jsxs(Box, { p: "xs", style: { borderTop: isDark ? `1px solid ${tokens.border}` : '1px solid var(--mantine-color-gray-2)' }, children: [_jsx(Text, { size: "xs", c: "dimmed", ta: "center", lh: 1.3, children: "Agent Red Customer Experience" }), _jsxs(Text, { size: "xs", c: "dimmed", ta: "center", lh: 1.3, children: ["v", productVersion || '...'] }), _jsxs(Text, { size: "xs", c: "dimmed", ta: "center", lh: 1.4, mt: 4, style: { opacity: 0.7, fontSize: 10 }, children: [String.fromCodePoint(0x00A9), " 2026 Remaker Digital, a DBA of"] }), _jsx(Text, { size: "xs", c: "dimmed", ta: "center", lh: 1.4, style: { opacity: 0.7, fontSize: 10 }, children: "VanDusen & Palmeter, LLC. All rights reserved." })] }) })] }), _jsxs(AppShell.Main, { children: [error && (_jsxs(Box, { p: "md", c: "red", children: ["Failed to load: ", error] })), loading && (_jsx(Box, { p: "xl", ta: "center", c: "dimmed", children: "Loading..." })), !loading && !error && children] })] }), showActivationDialog && (_jsx(ActivationDialog, { apiFetch: apiFetch, onNotify: onNotify, onClose: () => setShowActivationDialog(false), onSuccess: () => {
                    setShowActivationDialog(false);
                    setActivationRefreshKey((k) => k + 1);
                    setConfigRefreshKey((k) => k + 1);
                } })), _jsx(Modal, { opened: showDeactivateDialog, onClose: () => setShowDeactivateDialog(false), title: "Deactivate Configuration", centered: true, size: "sm", children: _jsxs(Stack, { gap: "md", children: [_jsxs(Text, { size: "sm", children: ["Deactivating will ", _jsx("strong", { children: "immediately stop the chat widget" }), " on your storefront. Visitors will no longer see the chat widget or be able to start conversations."] }), _jsx(Text, { size: "sm", c: "dimmed", children: "Your configuration will be preserved. You can re-activate at any time." }), _jsxs(Group, { justify: "flex-end", gap: "sm", children: [_jsx(Button, { variant: "default", size: "sm", onClick: () => setShowDeactivateDialog(false), children: "Cancel" }), _jsx(Button, { color: "red", size: "sm", loading: deactivating, onClick: async () => {
                                        setDeactivating(true);
                                        try {
                                            const res = await apiFetch('/api/config/deactivate', { method: 'POST' });
                                            if (res.ok) {
                                                onNotify('Configuration deactivated. Chat widget is offline.', 'success');
                                                setShowDeactivateDialog(false);
                                                setActivationRefreshKey((k) => k + 1);
                                            }
                                            else {
                                                const err = await res.json().catch(() => ({}));
                                                onNotify(err.detail || 'Deactivation failed.', 'error');
                                            }
                                        }
                                        catch {
                                            onNotify('Deactivation failed — network error.', 'error');
                                        }
                                        finally {
                                            setDeactivating(false);
                                        }
                                    }, children: "Deactivate" })] })] }) }), showRestoreDialog && activationStatus && (_jsx(RestoreDialog, { apiFetch: apiFetch, onNotify: onNotify, onClose: () => setShowRestoreDialog(false), onSuccess: () => {
                    setShowRestoreDialog(false);
                    setActivationRefreshKey((k) => k + 1);
                }, activeVersion: activationStatus.active_version, activeActivatedAt: activationStatus.active_activated_at })), _jsx(Modal, { opened: contactOpened, onClose: contactHandlers.close, title: _jsx(Text, { fw: 600, size: "lg", children: "Contact us" }), centered: true, size: "md", children: _jsxs(Stack, { gap: "md", children: [_jsx(Select, { label: "Topic", placeholder: "Select a topic", value: contactTopic, onChange: setContactTopic, data: [
                                { value: 'support', label: 'Support Request' },
                                { value: 'feature_request', label: 'Feature Request' },
                                { value: 'billing', label: 'Billing Inquiry' },
                                { value: 'bug_report', label: 'Bug Report' },
                                { value: 'general', label: 'General Inquiry' },
                            ] }), _jsx(TextInput, { label: "Subject", placeholder: "Brief summary of your message", value: contactSubject, onChange: (e) => setContactSubject(e.currentTarget.value), maxLength: 200, required: true }), _jsx(Textarea, { label: "Message", placeholder: "Describe your request in detail...", value: contactMessage, onChange: (e) => setContactMessage(e.currentTarget.value), minRows: 4, maxRows: 8, maxLength: 5000, autosize: true, required: true }), _jsxs(Group, { justify: "flex-end", gap: "sm", children: [_jsx(Button, { variant: "default", onClick: contactHandlers.close, disabled: contactSending, children: "Cancel" }), _jsx(Button, { className: "ar-btn-action", onClick: handleContactSubmit, loading: contactSending, disabled: !contactTopic || !contactSubject.trim() || !contactMessage.trim(), children: "Send message" })] })] }) }), _jsx(OnboardingWizard, { opened: showOnboarding, onClose: dismissOnboarding, apiFetch: apiFetch, shopDomain: tenantContext?.shopDomain, onNavigate: (path) => navigate(path) })] }));
};
//# sourceMappingURL=StandaloneLayout.js.map