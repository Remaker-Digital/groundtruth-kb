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
  useMantineColorScheme,
  useComputedColorScheme,
} from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { notifications } from '@mantine/notifications';

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
  tier: string;
  status: string;
  billingChannel: string;
}

interface AppContextValue {
  tenantContext: TenantContext | null;
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
  { path: '/knowledge-base', label: 'Knowledge Base', icon: 'knowledge' },
  { path: '/analytics', label: 'Analytics', icon: 'analytics' },
  { path: '/configuration', label: 'Configuration', icon: 'config' },
  { path: '/widget', label: 'Widget', icon: 'widget' },
  { path: '/team', label: 'Team', icon: 'team' },
  { path: '/billing', label: 'Billing', icon: 'billing' },
  { path: '/onboarding', label: 'Setup Wizard', icon: 'onboarding' },
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
      notifications.show({
        message,
        color: colorMap[type] || 'blue',
        autoClose: 5000,
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
            tier: data.tier,
            status: data.status,
            billingChannel: data.billing_channel || 'stripe',
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

  // ---- Chat widget injection (auto-embed for admin users) ----------------

  useEffect(() => {
    // Only inject widget once tenant context is resolved and no existing widget
    if (!tenantContext || document.getElementById('agent-red-admin-widget')) return;

    // Resolve API base URL — same origin as admin or explicit VITE_API_URL
    const apiUrl = API_BASE_URL || window.location.origin;

    // Fetch the tenant's widget key from the config endpoint
    async function injectWidget() {
      try {
        const resp = await apiFetch('/api/config');
        if (!resp.ok) return;
        const cfg = await resp.json();
        const widgetKey = cfg?.preferences?.widget_key || cfg?.widget_key;
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
          'Hi! I\u2019m your Agent Red AI assistant. Ask me anything about managing your store, configuring the widget, or understanding your analytics.');
        script.setAttribute('data-header-text', 'Agent Red Assistant');
        script.setAttribute('data-agent-name', 'Agent Red AI');
        script.setAttribute('data-sound-enabled', 'false');
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
            <Group gap="xs">
              {tenantContext && (
                <Badge variant="light" color="green" size="sm" tt="capitalize">
                  {tenantContext.tier}
                </Badge>
              )}
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
    </AppContext.Provider>
  );
};
