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

import type { TenantTier, TenantStatus, BillingChannel } from '../../shared/types';

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

interface TestModeState {
  enabled: boolean;
  percentage: number;
  overrides: Record<string, unknown>;
  activatedAt: string | null;
  overrideFieldCount: number;
}

interface AppContextValue {
  tenantContext: TenantContext | null;
  testMode: TestModeState | null;
  refetchTestMode: () => void;
  apiFetch: (path: string, init?: RequestInit) => Promise<Response>;
  onNotify: (message: string, type: 'success' | 'error' | 'warning' | 'info') => void;
  loading: boolean;
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
  onboarding: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /><line x1="16" y1="13" x2="8" y2="13" /><line x1="16" y1="17" x2="8" y2="17" /><polyline points="10 9 9 9 8 9" />
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
};

const navItems: NavPage[] = [
  { path: '/', label: 'Dashboard', icon: 'dashboard' },
  { path: '/inbox', label: 'Inbox', icon: 'inbox' },
  { path: '/team', label: 'Team', icon: 'team' },
  { path: '/configuration', label: 'Agent configuration', icon: 'config' },
  { path: '/knowledge-base', label: 'Knowledge base', icon: 'knowledge' },
  { path: '/quick-actions', label: 'Quick actions', icon: 'quickactions' },
  { path: '/widget', label: 'Widget configuration', icon: 'widget' },
  { path: '/integrations', label: 'Integrations', icon: 'integrations' },
  { path: '/memory-privacy', label: 'Memory & privacy', icon: 'memory' },
  { path: '/billing', label: 'Billing', icon: 'billing' },
  { path: '/onboarding', label: 'Setup wizard', icon: 'onboarding' },
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

  // ---- Test Mode status polling (C1) --------------------------------------

  const [testMode, setTestMode] = useState<TestModeState | null>(null);

  const refetchTestMode = useCallback(async () => {
    try {
      const resp = await apiFetch('/api/config/test-mode');
      if (!resp.ok) return;
      const data = await resp.json();
      setTestMode({
        enabled: data.enabled ?? false,
        percentage: data.percentage ?? 10,
        overrides: data.overrides ?? {},
        activatedAt: data.activated_at ?? null,
        overrideFieldCount: data.override_field_count ?? 0,
      });
    } catch {
      // silently ignore — test mode indicator won't show
    }
  }, [apiFetch]);

  useEffect(() => {
    if (!tenantContext) return;
    refetchTestMode();
    // Poll every 30 seconds to keep indicator up to date
    const interval = setInterval(refetchTestMode, 30_000);
    return () => clearInterval(interval);
  }, [tenantContext, refetchTestMode]);

  // ---- Activation status check (WI #291) -----------------------------------

  const [isActivated, setIsActivated] = useState<boolean | null>(null); // null = unknown

  useEffect(() => {
    if (!tenantContext) return;
    apiFetch('/api/config')
      .then(async (resp) => {
        if (!resp.ok) { setIsActivated(false); return; }
        const data = await resp.json();
        setIsActivated(!!data.version && data.version > 0);
      })
      .catch(() => setIsActivated(false));
  }, [tenantContext, apiFetch]);

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

  const goToWizard = useCallback(() => {
    setShowWelcome(false);
    try { localStorage.setItem('agentred-welcome-dismissed', '1'); } catch { /* ignore */ }
    navigate('/onboarding');
  }, [navigate]);

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
    testMode,
    refetchTestMode,
    apiFetch,
    onNotify,
    loading,
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
                <Badge variant="light" color="green" size="sm" tt="capitalize">
                  {tenantContext.tier}
                </Badge>
              )}
              {/* Inactive indicator (WI #291) — shown when system not yet activated */}
              {isActivated === false && !testMode?.enabled && (
                <Tooltip
                  label="Your AI assistant is not yet active. Complete the Setup Wizard to go live."
                  position="bottom"
                  multiline
                  w={240}
                >
                  <Badge
                    variant="light"
                    color="yellow"
                    size="sm"
                    style={{ cursor: 'pointer' }}
                    onClick={() => navigate('/onboarding')}
                  >
                    Inactive
                  </Badge>
                </Tooltip>
              )}
              {/* Test Mode indicator (C1) */}
              {testMode?.enabled && (
                <Tooltip
                  label={`Test Mode active — ${testMode.percentage}% of sessions routed to test config (${testMode.overrideFieldCount} field${testMode.overrideFieldCount !== 1 ? 's' : ''} overridden)`}
                  position="bottom"
                  multiline
                  w={260}
                >
                  <Badge
                    variant="light"
                    color="orange"
                    size="sm"
                    style={{ cursor: 'default' }}
                    leftSection={
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z" />
                      </svg>
                    }
                  >
                    Test Mode {testMode.percentage}%
                  </Badge>
                </Tooltip>
              )}
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
            {navItems.map((item) => {
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
                      <Badge size="xs" variant="filled" color="brand" circle>
                        {item.badge}
                      </Badge>
                    ) : undefined
                  }
                  active={isActive}
                  onClick={() => navigate(item.path)}
                  styles={{
                    label: isActive && isDark ? { color: '#F5F5F5' } : undefined,
                  }}
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
                  src="/admin/standalone/remaker-digital-logo.svg"
                  alt="Remaker Digital"
                  style={{ height: 22, display: 'block' }}
                />
              </Group>
              <Text size="xs" c="dimmed" ta="center" lh={1.3}>
                Agent Red Customer Experience
              </Text>
              <Text size="xs" c="dimmed" ta="center" lh={1.3}>
                v1.0.0
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
          {/* Test Mode sticky banner (C1) — visible on all pages when active */}
          {testMode?.enabled && (
            <Box
              px="md"
              py={8}
              mb="md"
              style={{
                background: 'linear-gradient(135deg, rgba(255, 152, 0, 0.12) 0%, rgba(255, 87, 34, 0.08) 100%)',
                border: '1px solid rgba(255, 152, 0, 0.25)',
                borderRadius: 8,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: 12,
                flexWrap: 'wrap',
              }}
            >
              <Group gap={10} style={{ flex: 1 }}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ff9800" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z" />
                </svg>
                <Text size="sm" fw={500} c="orange.3">
                  Test mode active
                </Text>
                <Text size="xs" c="dimmed">
                  {testMode.percentage}% of customer sessions are receiving your test configuration
                  ({testMode.overrideFieldCount} field{testMode.overrideFieldCount !== 1 ? 's' : ''} overridden)
                </Text>
              </Group>
              <Group gap={8} style={{ flexShrink: 0 }}>
                {location.pathname !== '/configuration' && (
                  <Text
                    size="xs"
                    fw={600}
                    c="orange.4"
                    style={{ cursor: 'pointer', textDecoration: 'underline', textUnderlineOffset: 2 }}
                    onClick={() => navigate('/configuration')}
                  >
                    Manage test
                  </Text>
                )}
                {location.pathname !== '/' && (
                  <Text
                    size="xs"
                    fw={600}
                    c="dimmed"
                    style={{ cursor: 'pointer', textDecoration: 'underline', textUnderlineOffset: 2 }}
                    onClick={() => navigate('/')}
                  >
                    View analytics
                  </Text>
                )}
              </Group>
            </Box>
          )}
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
            Your AI customer service assistant is not yet active. Complete the Setup Wizard to
            configure your agent and go live.
          </Text>
          <Group justify="flex-end">
            <Button variant="default" onClick={dismissWelcome}>
              Dismiss
            </Button>
            <Button color="#ff3621" onClick={goToWizard}>
              Go to Setup Wizard
            </Button>
          </Group>
        </Stack>
      </Modal>
    </AppContext.Provider>
  );
};
