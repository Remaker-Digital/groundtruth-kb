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
 *   chrome #0a0a0a → page #141414 → surface #1f1f1f → border #272727
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  AppShell,
  NavLink,
  Group,
  Text,
  ThemeIcon,
  Badge,
  Box,
  Burger,
  Tooltip,
  ActionIcon,
  Modal,
  Button,
  Stack,
  useMantineColorScheme,
  useComputedColorScheme,
} from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { notifications } from '@mantine/notifications';

import type { TenantTier, TenantStatus, BillingChannel, TeamRole } from '../../shared/types';
import type { ActivationStatus } from '../../shared/hooks';
import ActivationDialog from '../../shared/ActivationDialog';
import RestoreDialog from '../../shared/RestoreDialog';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface StandaloneLayoutProps {
  apiKey: string;
  onLogout: () => void;
  children: React.ReactNode;
}

interface TenantContext {
  tenantId: string;
  tier: TenantTier;
  status: TenantStatus;
  billingChannel: BillingChannel;
  hasStripeBilling: boolean;
  shopDomain?: string;
}

interface AppContextValue {
  tenantContext: TenantContext | null;
  /** Caller's role from /api/admin/team/whoami. Null until resolved. */
  userRole: TeamRole | null;
  /** Product version from API X-Product-Version header. Null until first API call completes. */
  productVersion: string | null;
  apiFetch: (path: string, init?: RequestInit) => Promise<Response>;
  onNotify: (message: string, type: 'success' | 'error' | 'warning' | 'info') => void;
  loading: boolean;
  /** Trigger an immediate refresh of the sidebar activation status (e.g. after saving a draft). */
  refreshActivationStatus: () => void;
  /** Increments after a discard so child pages can re-fetch their config data. */
  configRefreshKey: number;
}

// ---------------------------------------------------------------------------
// Context
// ---------------------------------------------------------------------------

const AppContext = createContext<AppContextValue | null>(null);

export function useAppContext(): AppContextValue {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useAppContext must be used within StandaloneLayout');
  return ctx;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const API_BASE_URL = import.meta.env?.VITE_API_URL || '';
const DOCS_URL = 'https://agentredcx.com';

/** Tier-dependent badge colors for the header plan indicator. */
const TIER_BADGE_COLORS: Record<string, string> = {
  trial: 'yellow',
  starter: 'blue',
  professional: 'green',
  enterprise: 'grape',
};

/** Tier ordering for comparison. Higher index = higher tier. */
const TIER_ORDER: TenantTier[] = ['trial', 'starter', 'professional', 'enterprise'];

/** Short labels for nav tier badges. */
const TIER_BADGE_LABELS: Record<TenantTier, string> = {
  trial: 'Trial',
  starter: 'Starter',
  professional: 'Professional',
  enterprise: 'Enterprise',
};

/** Returns true if the tenant tier meets or exceeds the required minimum. */
function tierMeetsMin(current: TenantTier, minTier: TenantTier): boolean {
  return TIER_ORDER.indexOf(current) >= TIER_ORDER.indexOf(minTier);
}

// SVG Icons — from prototype StandaloneApp.tsx
const Icons = {
  dashboard: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="7" height="7" /><rect x="14" y="3" width="7" height="7" /><rect x="3" y="14" width="7" height="7" /><rect x="14" y="14" width="7" height="7" />
    </svg>
  ),
  inbox: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
    </svg>
  ),
  knowledge: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" /><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
    </svg>
  ),
  analytics: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="18" y1="20" x2="18" y2="10" /><line x1="12" y1="20" x2="12" y2="4" /><line x1="6" y1="20" x2="6" y2="14" />
    </svg>
  ),
  config: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
    </svg>
  ),
  widget: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="2" y="3" width="20" height="14" rx="2" ry="2" /><line x1="8" y1="21" x2="16" y2="21" /><line x1="12" y1="17" x2="12" y2="21" />
    </svg>
  ),
  billing: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="1" y="4" width="22" height="16" rx="2" ry="2" /><line x1="1" y1="10" x2="23" y2="10" />
    </svg>
  ),
  team: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M23 21v-2a4 4 0 0 0-3-3.87" /><path d="M16 3.13a4 4 0 0 1 0 7.75" />
    </svg>
  ),
  integrations: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" /><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
    </svg>
  ),
  docs: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" /><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
    </svg>
  ),
  externalLink: () => (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" /><polyline points="15 3 21 3 21 9" /><line x1="10" y1="14" x2="21" y2="3" />
    </svg>
  ),
  storefront: () => (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" /><polyline points="9 22 9 12 15 12 15 22" />
    </svg>
  ),
  quickactions: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
    </svg>
  ),
  memory: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 2a4 4 0 0 0-4 4v2H6a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V10a2 2 0 0 0-2-2h-2V6a4 4 0 0 0-4-4z" />
      <circle cx="12" cy="15" r="2" />
      <line x1="12" y1="17" x2="12" y2="19" />
    </svg>
  ),
};

type NavPage = {
  path: string;
  label: string;
  icon: keyof typeof Icons;
  badge?: number;
  /** Roles that can see this nav item. Omit = all roles. */
  roles?: TeamRole[];
  /** Minimum tier to use this page (e.g. 'professional'). Shows a small badge in the nav. */
  minTier?: TenantTier;
};

/** Nav items rendered BEFORE the configuration group. */
const navItemsBefore: NavPage[] = [
  { path: '/', label: 'Dashboard', icon: 'dashboard', roles: ['superadmin', 'admin', 'viewer'] },
  { path: '/inbox', label: 'Inbox', icon: 'inbox' },
  { path: '/team', label: 'Team members', icon: 'team', roles: ['superadmin', 'admin'] },
];

/** Pages participating in the Save→Activate lifecycle (grouped in sidebar). */
const configGroupItems: NavPage[] = [
  { path: '/configuration', label: 'Agent configuration', icon: 'config', roles: ['superadmin', 'admin'] },
  { path: '/knowledge-base', label: 'Knowledge base', icon: 'knowledge', roles: ['superadmin', 'admin'] },
  { path: '/quick-actions', label: 'Quick actions', icon: 'quickactions', roles: ['superadmin', 'admin'] },
  { path: '/widget', label: 'Widget configuration', icon: 'widget', roles: ['superadmin', 'admin'] },
];

/** Nav items rendered AFTER the configuration group. */
const navItemsAfter: NavPage[] = [
  { path: '/integrations', label: 'Integrations', icon: 'integrations', roles: ['superadmin', 'admin'] },
  { path: '/memory-privacy', label: 'Memory & privacy', icon: 'memory', roles: ['superadmin', 'admin'], minTier: 'professional' },
  { path: '/billing', label: 'Billing', icon: 'billing', roles: ['superadmin', 'admin'] },
];

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const StandaloneLayout: React.FC<StandaloneLayoutProps> = ({
  apiKey,
  onLogout,
  children,
}) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [opened, { toggle }] = useDisclosure();
  const { setColorScheme } = useMantineColorScheme();
  const computedColorScheme = useComputedColorScheme('dark');
  const isDark = computedColorScheme === 'dark';

  const [tenantContext, setTenantContext] = useState<TenantContext | null>(null);
  const [productVersion, setProductVersion] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // ---- Authenticated fetch -----------------------------------------------

  const apiFetch = useCallback(
    async (path: string, init?: RequestInit): Promise<Response> => {
      const headers = new Headers(init?.headers);
      headers.set('X-API-Key', apiKey);

      return fetch(`${API_BASE_URL}${path}`, {
        ...init,
        headers,
      });
    },
    [apiKey],
  );

  // ---- Notification handler (Mantine notifications) ----------------------

  const onNotify = useCallback(
    (message: string, type: 'success' | 'error' | 'warning' | 'info') => {
      const colorMap: Record<string, string> = {
        success: 'green',
        error: 'red',
        warning: 'yellow',
        info: 'blue',
      };
      const titleMap: Record<string, string> = {
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
    },
    [],
  );

  // ---- Tenant context resolution -----------------------------------------

  useEffect(() => {
    let cancelled = false;

    async function resolveTenant() {
      try {
        const resp = await apiFetch('/api/tenants/lookup');
        if (!resp.ok) {
          if (resp.status === 401 || resp.status === 403) {
            onLogout();
            return;
          }
          throw new Error(`Tenant lookup failed: ${resp.status}`);
        }
        const data = await resp.json();
        if (!cancelled) {
          // Capture product version from response header (set by ApiVersionMiddleware)
          const pv = resp.headers.get('x-product-version');
          if (pv) setProductVersion(pv);

          setTenantContext({
            tenantId: data.tenant_id,
            tier: data.tier as TenantTier,
            status: data.status as TenantStatus,
            billingChannel: (data.billing_channel || 'stripe') as BillingChannel,
            hasStripeBilling: data.has_stripe_billing ?? false,
            shopDomain: data.shopify_shop_domain || undefined,
          });
          setLoading(false);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load');
          setLoading(false);
        }
      }
    }

    resolveTenant();
    return () => { cancelled = true; };
  }, [apiFetch, onLogout]);

  // ---- Caller role resolution (whoami) ------------------------------------

  const [userRole, setUserRole] = useState<TeamRole | null>(null);

  useEffect(() => {
    if (!tenantContext) return;
    apiFetch('/api/admin/team/whoami')
      .then(async (resp) => {
        if (!resp.ok) {
          // Fallback: treat as admin (legacy tenant API key or endpoint not deployed yet)
          setUserRole('admin');
          return;
        }
        const data = await resp.json();
        setUserRole((data.role as TeamRole) || 'admin');
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
  const [activationStatus, setActivationStatus] = useState<ActivationStatus | null>(null);
  const [discarding, setDiscarding] = useState(false);
  const [configRefreshKey, setConfigRefreshKey] = useState(0);

  // Poll activation status every 30s (replaces ActivationBanner's internal polling)
  const fetchActivationStatus = useCallback(async () => {
    try {
      const res = await apiFetch('/api/config/activation-status');
      if (res.ok) {
        const data: ActivationStatus = await res.json();
        setActivationStatus(data);
      }
    } catch { /* silent — polling failure is non-fatal */ }
  }, [apiFetch]);

  useEffect(() => {
    if (!tenantContext) return;
    fetchActivationStatus();
    const interval = setInterval(fetchActivationStatus, 30_000);
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
  const isActivated = (
    activationStatus?.is_configured === true
    && activationStatus?.active_activated_at != null
  ) ? true : (activationStatus != null ? false : null);

  // ---- Welcome popup (WI #292) — first-time merchants ---------------------

  const [showWelcome, setShowWelcome] = useState(false);

  useEffect(() => {
    if (isActivated !== false) return; // Only show when explicitly not activated
    try {
      const dismissed = localStorage.getItem('agentred-welcome-dismissed');
      if (!dismissed) setShowWelcome(true);
    } catch { /* ignore */ }
  }, [isActivated]);

  const dismissWelcome = useCallback(() => {
    setShowWelcome(false);
    try { localStorage.setItem('agentred-welcome-dismissed', '1'); } catch { /* ignore */ }
  }, []);

  // Discard all draft changes (confirm → POST → refresh)
  const handleDiscard = useCallback(async () => {
    if (!confirm('Discard all draft changes? This cannot be undone.')) return;
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
      } else {
        onNotify('Failed to discard draft', 'error');
      }
    } catch {
      onNotify('Network error discarding draft', 'error');
    } finally {
      setDiscarding(false);
    }
  }, [apiFetch, onNotify]);

  // Config group visible only for superadmin / admin
  const canSeeConfigGroup = !userRole || ['superadmin', 'admin'].includes(userRole);

  // ---- Chat widget injection (auto-embed for admin users) ----------------

  useEffect(() => {
    // Only inject widget once tenant context is resolved and no existing widget
    if (!tenantContext || document.getElementById('agent-red-admin-widget')) return;

    // Resolve API base URL — same origin as admin or explicit VITE_API_URL
    const apiUrl = API_BASE_URL || window.location.origin;

    // Fetch the tenant's widget key and appearance config from the config endpoint
    async function injectWidget() {
      try {
        const resp = await apiFetch('/api/config?page_type=all');
        if (!resp.ok) return;
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
        script.src = `${apiUrl}/widget.js`;
        script.setAttribute('data-widget-key', widgetKey);
        script.setAttribute('data-api-url', apiUrl);
        script.setAttribute('data-auto-open', 'false');
        script.setAttribute('data-auto-open-delay', '0');
        script.setAttribute('data-context', 'admin');
        script.setAttribute('data-greeting',
          config.greeting_message
            || 'Hi! I\u2019m your Agent Red AI assistant. Ask me anything about managing your store, configuring the widget, or understanding your analytics.');
        script.setAttribute('data-header-text', config.widget_header_text || 'Agent Red Assistant');
        script.setAttribute('data-agent-name', config.widget_agent_display_name || 'Agent Red AI');
        script.setAttribute('data-sound-enabled', 'false');

        // Pass widget appearance fields so the widget renders with tenant
        // brand colors immediately (without waiting for its own /api/config fetch)
        const appearanceMap: Array<[string, string]> = [
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
      } catch (err) {
        console.warn('[AgentRed Admin] Could not load chat widget:', err);
      }
    }

    injectWidget();

    // Cleanup on unmount
    return () => {
      // Remove widget if it exists
      const existing = document.getElementById('agent-red-admin-widget');
      if (existing) existing.remove();
      // Destroy SDK if available
      const sdk = (window as unknown as Record<string, unknown>).AgentRed as
        { destroy?: () => void } | undefined;
      if (sdk?.destroy) sdk.destroy();
    };
  }, [tenantContext, apiFetch]);

  // ---- Context value -----------------------------------------------------

  const contextValue: AppContextValue = {
    tenantContext,
    userRole,
    productVersion,
    apiFetch,
    onNotify,
    loading,
    refreshActivationStatus: fetchActivationStatus,
    configRefreshKey,
  };

  // ---- Render ------------------------------------------------------------

  return (
    <AppContext.Provider value={contextValue}>
      <AppShell
        header={{ height: 56 }}
        navbar={{ width: 260, breakpoint: 'sm', collapsed: { mobile: !opened } }}
        padding="md"
        styles={{
          header: {
            borderBottom: isDark ? '1px solid #272727' : '1px solid #1E1E1E',
            background: '#0a0a0a',
          },
          navbar: {
            borderRight: isDark ? '1px solid #272727' : undefined,
            background: isDark ? '#0a0a0a' : undefined,
          },
          main: {
            background: isDark ? '#141414' : undefined,
          },
        }}
      >
        {/* ---- Header ---- */}
        <AppShell.Header>
          <Group h="100%" px="md" justify="space-between">
            <Group>
              <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" />
              <Tooltip label="Agent Red Customer Experience" position="bottom" openDelay={500}>
                <Group gap={10} align="center" style={{ cursor: 'default' }}>
                  <img
                    src="/admin/standalone/primary-logo-no-wordmark.svg"
                    alt="Agent Red"
                    style={{ height: 28, display: 'block' }}
                  />
                  <Text
                    size="sm"
                    fw={500}
                    c="gray.4"
                    style={{ letterSpacing: '0.02em', userSelect: 'none' }}
                  >
                    Customer Experience
                  </Text>
                </Group>
              </Tooltip>
            </Group>
            <Group gap="sm">
              {/* Storefront name + link */}
              {tenantContext?.shopDomain && (
                <Tooltip label={`Open ${tenantContext.shopDomain}`} position="bottom">
                  <a
                    href={`https://${tenantContext.shopDomain}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 6,
                      textDecoration: 'none',
                      color: '#A0A0A0',
                      padding: '4px 10px',
                      borderRadius: 6,
                      border: '1px solid rgba(255, 255, 255, 0.08)',
                      background: 'rgba(255, 255, 255, 0.03)',
                      fontSize: 13,
                      transition: 'border-color 0.15s',
                    }}
                    onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.borderColor = 'rgba(255, 255, 255, 0.2)'; }}
                    onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.borderColor = 'rgba(255, 255, 255, 0.08)'; }}
                  >
                    <Icons.storefront />
                    <span style={{ maxWidth: 180, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {tenantContext.shopDomain.replace('.myshopify.com', '')}
                    </span>
                    <Icons.externalLink />
                  </a>
                </Tooltip>
              )}
              {tenantContext && (
                <Tooltip
                  label={`Your current plan: ${tenantContext.tier.charAt(0).toUpperCase() + tenantContext.tier.slice(1)}. Plans available: Starter ($149/mo), Professional ($399/mo), Enterprise ($999/mo).`}
                  position="bottom"
                  multiline
                  w={280}
                  openDelay={300}
                >
                  <Badge variant="light" color={TIER_BADGE_COLORS[tenantContext.tier] ?? 'gray'} size="sm" style={{ cursor: 'default' }}>
                    {TIER_BADGE_LABELS[tenantContext.tier] ?? tenantContext.tier}
                  </Badge>
                </Tooltip>
              )}
              {/* Inactive badge removed (session 21) — sidebar "Pending" badge already
                 conveys not-yet-activated state; "Inactive" added no distinct meaning. */}
              {/* Documentation link */}
              <Tooltip label="Documentation" position="bottom">
                <ActionIcon
                  variant="subtle"
                  size="md"
                  component="a"
                  href={DOCS_URL}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label="Open documentation"
                  style={{
                    color: '#A0A0A0',
                    border: '1px solid rgba(255, 255, 255, 0.12)',
                    background: 'rgba(255, 255, 255, 0.06)',
                  }}
                >
                  <Icons.docs />
                </ActionIcon>
              </Tooltip>
              {/* Dark mode toggle */}
              <ActionIcon
                variant="subtle"
                size="md"
                onClick={() => setColorScheme(isDark ? 'light' : 'dark')}
                aria-label="Toggle dark mode"
                style={{
                  color: '#A0A0A0',
                  border: '1px solid rgba(255, 255, 255, 0.12)',
                  background: 'rgba(255, 255, 255, 0.06)',
                }}
              >
                {isDark ? (
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="12" cy="12" r="5" /><line x1="12" y1="1" x2="12" y2="3" /><line x1="12" y1="21" x2="12" y2="23" /><line x1="4.22" y1="4.22" x2="5.64" y2="5.64" /><line x1="18.36" y1="18.36" x2="19.78" y2="19.78" /><line x1="1" y1="12" x2="3" y2="12" /><line x1="21" y1="12" x2="23" y2="12" /><line x1="4.22" y1="19.78" x2="5.64" y2="18.36" /><line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
                  </svg>
                ) : (
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
                  </svg>
                )}
              </ActionIcon>
              {/* Sign Out */}
              <ActionIcon
                variant="subtle"
                size="md"
                onClick={onLogout}
                aria-label="Sign out"
                style={{
                  color: '#A0A0A0',
                  border: '1px solid rgba(255, 255, 255, 0.12)',
                  background: 'rgba(255, 255, 255, 0.06)',
                }}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" /><polyline points="16 17 21 12 16 7" /><line x1="21" y1="12" x2="9" y2="12" />
                </svg>
              </ActionIcon>
            </Group>
          </Group>
        </AppShell.Header>

        {/* ---- Navbar ---- */}
        <AppShell.Navbar p="xs">
          <AppShell.Section grow>
            {/* --- Before-group items (Dashboard, Inbox, Team members) --- */}
            {navItemsBefore
              .filter((item) => !item.roles || !userRole || item.roles.includes(userRole))
              .map((item) => {
                const IconComponent = Icons[item.icon];
                const isActive = location.pathname === item.path
                  || (item.path !== '/' && location.pathname.startsWith(item.path));
                return (
                  <NavLink
                    key={item.path}
                    label={item.label}
                    leftSection={
                      <ThemeIcon
                        variant={isActive ? 'filled' : isDark ? 'default' : 'light'}
                        size="sm"
                        color={isActive ? 'brand' : 'gray'}
                        style={!isActive && isDark ? { background: 'transparent', border: 'none' } : undefined}
                      >
                        <IconComponent />
                      </ThemeIcon>
                    }
                    rightSection={
                      item.badge ? (
                        <Badge size="xs" variant="filled" color="brand" circle>{item.badge}</Badge>
                      ) : undefined
                    }
                    active={isActive}
                    onClick={() => navigate(item.path)}
                    styles={{ label: isActive && isDark ? { color: '#F5F5F5' } : undefined }}
                    style={{
                      borderRadius: 8,
                      marginBottom: 2,
                      ...(isActive && isDark ? { background: '#1f1f1f', border: '1px solid #272727' } : {}),
                    }}
                  />
                );
              })}

            {/* --- Configuration group (Save→Activate lifecycle) --- */}
            {canSeeConfigGroup && (
              <Box
                style={{
                  border: `1px solid ${isDark ? '#272727' : '#e0e0e0'}`,
                  borderRadius: 8,
                  padding: '8px 6px',
                  margin: '4px 0',
                  background: isDark ? 'rgba(31, 31, 31, 0.4)' : 'rgba(0, 0, 0, 0.02)',
                }}
              >
                {/* Group header: label + status badge */}
                <Group justify="space-between" px={10} py={4} pb={6}>
                  <Text
                    size="xs"
                    fw={600}
                    c="dimmed"
                    tt="uppercase"
                    style={{ letterSpacing: '0.5px', fontSize: 10 }}
                  >
                    AI Configuration
                  </Text>
                  {/* D44: Three-state badge.
                      Green "Active"  = is_active AND no pending changes.
                      Red "Inactive"  = was active, now deactivated, no pending changes.
                      Yellow "Pending" = everything else (never activated, or has pending changes). */}
                  {activationStatus && (
                    activationStatus.is_active && !activationStatus.has_pending_changes ? (
                      <Badge size="xs" variant="dot" color="green">Active</Badge>
                    ) : !activationStatus.is_active
                        && activationStatus.is_configured
                        && !activationStatus.has_pending_changes
                        && activationStatus.active_activated_at != null ? (
                      <Badge size="xs" variant="dot" color="red">Inactive</Badge>
                    ) : (
                      <Badge size="xs" variant="dot" color="yellow">Pending</Badge>
                    )
                  )}
                </Group>

                {/* Config nav items */}
                {configGroupItems.map((item) => {
                  const IconComponent = Icons[item.icon];
                  const isActive = location.pathname === item.path
                    || (item.path !== '/' && location.pathname.startsWith(item.path));
                  return (
                    <NavLink
                      key={item.path}
                      label={item.label}
                      leftSection={
                        <ThemeIcon
                          variant={isActive ? 'filled' : isDark ? 'default' : 'light'}
                          size="sm"
                          color={isActive ? 'brand' : 'gray'}
                          style={!isActive && isDark ? { background: 'transparent', border: 'none' } : undefined}
                        >
                          <IconComponent />
                        </ThemeIcon>
                      }
                      active={isActive}
                      onClick={() => navigate(item.path)}
                      styles={{ label: isActive && isDark ? { color: '#F5F5F5' } : undefined }}
                      style={{
                        borderRadius: 8,
                        marginBottom: 2,
                        ...(isActive && isDark ? { background: '#1f1f1f', border: '1px solid #272727' } : {}),
                      }}
                    />
                  );
                })}

                {/* Action buttons */}
                <Group
                  gap={4}
                  px={4}
                  pt={6}
                  pb={2}
                  wrap="nowrap"
                  style={{
                    borderTop: `1px solid ${isDark ? '#272727' : '#e0e0e0'}`,
                    marginTop: 4,
                  }}
                >
                  <Button
                    size="compact-xs"
                    variant="filled"
                    color={
                      /* D44: Three-disposition activation control.
                         Red "Deactivate" = active with no pending changes.
                         Green "Activate" = ready to activate (can_activate from draft preflight).
                         Yellow "Activate" = activation blocked (missing mandatory fields). */
                      activationStatus?.is_active && !activationStatus?.has_pending_changes
                        ? 'red'
                        : activationStatus?.can_activate
                          ? 'green'
                          : 'yellow'
                    }
                    onClick={() => {
                      if (activationStatus?.is_active && !activationStatus?.has_pending_changes) {
                        setShowDeactivateDialog(true);
                      } else {
                        setShowActivationDialog(true);
                      }
                    }}
                    style={{ flex: 1 }}
                  >
                    {activationStatus?.is_active && !activationStatus?.has_pending_changes
                      ? 'Deactivate'
                      : 'Activate'}
                  </Button>
                  <Button
                    size="compact-xs"
                    variant={activationStatus?.has_pending_changes ? 'light' : 'default'}
                    color={activationStatus?.has_pending_changes ? 'blue' : undefined}
                    disabled={!activationStatus?.has_pending_changes || discarding}
                    onClick={handleDiscard}
                  >
                    {discarding ? '\u2026' : 'Discard'}
                  </Button>
                  <Button
                    size="compact-xs"
                    variant="default"
                    disabled={!activationStatus || activationStatus.active_version < 2}
                    onClick={() => setShowRestoreDialog(true)}
                  >
                    Roll back
                  </Button>
                </Group>
              </Box>
            )}

            {/* --- After-group items (Integrations, Memory, Billing) --- */}
            {navItemsAfter
              .filter((item) => !item.roles || !userRole || item.roles.includes(userRole))
              .map((item) => {
                const IconComponent = Icons[item.icon];
                const isActive = location.pathname === item.path
                  || (item.path !== '/' && location.pathname.startsWith(item.path));
                const currentTier = tenantContext?.tier ?? 'starter';
                const showTierBadge = item.minTier && !tierMeetsMin(currentTier, item.minTier);
                return (
                  <NavLink
                    key={item.path}
                    label={item.label}
                    leftSection={
                      <ThemeIcon
                        variant={isActive ? 'filled' : isDark ? 'default' : 'light'}
                        size="sm"
                        color={isActive ? 'brand' : 'gray'}
                        style={!isActive && isDark ? { background: 'transparent', border: 'none' } : undefined}
                      >
                        <IconComponent />
                      </ThemeIcon>
                    }
                    rightSection={
                      item.badge ? (
                        <Badge size="xs" variant="filled" color="brand" circle>{item.badge}</Badge>
                      ) : showTierBadge ? (
                        <Badge size="xs" variant="light" color={TIER_BADGE_COLORS[item.minTier!] ?? 'gray'}>
                          {TIER_BADGE_LABELS[item.minTier!]}
                        </Badge>
                      ) : undefined
                    }
                    active={isActive}
                    onClick={() => navigate(item.path)}
                    styles={{ label: isActive && isDark ? { color: '#F5F5F5' } : undefined }}
                    style={{
                      borderRadius: 8,
                      marginBottom: 2,
                      ...(isActive && isDark ? { background: '#1f1f1f', border: '1px solid #272727' } : {}),
                    }}
                  />
                );
              })}

            {/* Documentation — external link */}
            <NavLink
              label="Documentation"
              component="a"
              href={DOCS_URL}
              target="_blank"
              rel="noopener noreferrer"
              leftSection={
                <ThemeIcon
                  variant={isDark ? 'default' : 'light'}
                  size="sm"
                  color="gray"
                  style={isDark ? { background: 'transparent', border: 'none' } : undefined}
                >
                  <Icons.docs />
                </ThemeIcon>
              }
              rightSection={<Icons.externalLink />}
              style={{
                borderRadius: 8,
                marginBottom: 2,
              }}
            />
          </AppShell.Section>

          {/* Footer with Remaker Digital branding */}
          <AppShell.Section>
            <Box p="xs" style={{ borderTop: isDark ? '1px solid #272727' : '1px solid var(--mantine-color-gray-2)' }}>
              <Group gap={8} justify="center" mb={4}>
                <img
                  src={isDark ? '/admin/standalone/remaker-digital-logo-dark.svg' : '/admin/standalone/remaker-digital-logo-light.svg'}
                  alt="Remaker Digital"
                  style={{ height: 22, display: 'block' }}
                />
              </Group>
              <Text size="xs" c="dimmed" ta="center" lh={1.3}>
                Agent Red Customer Experience
              </Text>
              <Text size="xs" c="dimmed" ta="center" lh={1.3}>
                v{productVersion || '...'}
              </Text>
              <Text size="xs" c="dimmed" ta="center" lh={1.4} mt={4} style={{ opacity: 0.7, fontSize: 10 }}>
                Brought to you by remakerdigital.com
              </Text>
              <Text size="xs" c="dimmed" ta="center" lh={1.4} style={{ opacity: 0.7, fontSize: 10 }}>
                {String.fromCodePoint(0x00A9)} 2026 Remaker Digital, a DBA of
              </Text>
              <Text size="xs" c="dimmed" ta="center" lh={1.4} style={{ opacity: 0.7, fontSize: 10 }}>
                VanDusen & Palmeter, LLC. All rights reserved.
              </Text>
            </Box>
          </AppShell.Section>
        </AppShell.Navbar>

        {/* ---- Main content ---- */}
        <AppShell.Main>
          {error && (
            <Box p="md" c="red">
              Failed to load: {error}
            </Box>
          )}
          {loading && (
            <Box p="xl" ta="center" c="dimmed">
              Loading...
            </Box>
          )}
          {!loading && !error && children}
        </AppShell.Main>
      </AppShell>

      {/* Activation dialog (triggered by sidebar Activate button) */}
      {showActivationDialog && (
        <ActivationDialog
          apiFetch={apiFetch}
          onNotify={onNotify}
          onClose={() => setShowActivationDialog(false)}
          onSuccess={() => {
            setShowActivationDialog(false);
            setActivationRefreshKey((k) => k + 1);
          }}
        />
      )}

      {/* Deactivate confirmation dialog (triggered by sidebar Deactivate button) */}
      <Modal
        opened={showDeactivateDialog}
        onClose={() => setShowDeactivateDialog(false)}
        title="Deactivate Configuration"
        centered
        size="sm"
      >
        <Stack gap="md">
          <Text size="sm">
            Deactivating will <strong>immediately stop the chat widget</strong> on your
            storefront. Visitors will no longer see the chat widget or be able to start
            conversations.
          </Text>
          <Text size="sm" c="dimmed">
            Your configuration will be preserved. You can re-activate at any time.
          </Text>
          <Group justify="flex-end" gap="sm">
            <Button
              variant="default"
              size="sm"
              onClick={() => setShowDeactivateDialog(false)}
            >
              Cancel
            </Button>
            <Button
              color="red"
              size="sm"
              loading={deactivating}
              onClick={async () => {
                setDeactivating(true);
                try {
                  const res = await apiFetch('/api/config/deactivate', { method: 'POST' });
                  if (res.ok) {
                    onNotify('Configuration deactivated. Chat widget is offline.', 'success');
                    setShowDeactivateDialog(false);
                    setActivationRefreshKey((k) => k + 1);
                  } else {
                    const err = await res.json().catch(() => ({}));
                    onNotify(err.detail || 'Deactivation failed.', 'error');
                  }
                } catch {
                  onNotify('Deactivation failed — network error.', 'error');
                } finally {
                  setDeactivating(false);
                }
              }}
            >
              Deactivate
            </Button>
          </Group>
        </Stack>
      </Modal>

      {/* Restore dialog (triggered by sidebar Roll back button) */}
      {showRestoreDialog && activationStatus && (
        <RestoreDialog
          apiFetch={apiFetch}
          onNotify={onNotify}
          onClose={() => setShowRestoreDialog(false)}
          onSuccess={() => {
            setShowRestoreDialog(false);
            setActivationRefreshKey((k) => k + 1);
          }}
          activeVersion={activationStatus.active_version}
          activeActivatedAt={activationStatus.active_activated_at}
        />
      )}

      {/* Welcome popup for first-time merchants (WI #292) */}
      <Modal
        opened={showWelcome}
        onClose={dismissWelcome}
        title={
          <Text fw={600} size="lg">
            Welcome to Agent Red!
          </Text>
        }
        centered
        size="sm"
      >
        <Stack gap="md">
          <Text size="sm">
            Your AI customer service assistant is not yet active. Configure your agent on the
            Agent Configuration page, then activate your changes to go live.
          </Text>
          <Group justify="flex-end">
            <Button variant="default" onClick={dismissWelcome}>
              Dismiss
            </Button>
          </Group>
        </Stack>
      </Modal>
    </AppContext.Provider>
  );
};
