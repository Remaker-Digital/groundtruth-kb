/**
 * ProviderLayout — Platform operator console shell.
 *
 * Provides:
 *   1. Grouped sidebar navigation (29 pages in 5 groups)
 *   2. Header with platform name, version, and logout
 *   3. Authenticated apiFetch wrapper (SUPERADMIN API key injection)
 *   4. AppContext for child pages
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { useTenantDirectory, type TenantDisplayInfo } from '../hooks/useTenantDirectory';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  AppShell,
  Box,
  Burger,
  Divider,
  Group,
  NavLink,
  ScrollArea,
  Text,
  ActionIcon,
  Badge,
  Tooltip,
} from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { useMantineColorScheme, useComputedColorScheme } from '@mantine/core';
import { notifications } from '@mantine/notifications';
import { Icons } from '../../shared/icons';
import { tokens } from '../../shared/theme/styles';

// ---------------------------------------------------------------------------
// Context
// ---------------------------------------------------------------------------

interface ProviderContextValue {
  apiFetch: (path: string, init?: RequestInit) => Promise<Response>;
  onNotify: (message: string, type: 'success' | 'error' | 'warning' | 'info') => void;
  productVersion: string | null;
  /** WI-0883: Human-readable tenant lookup (email → domain → UUID) */
  getTenantDisplay: (tenantId: string) => TenantDisplayInfo;
}

const ProviderContext = createContext<ProviderContextValue | null>(null);

export function useProviderContext(): ProviderContextValue {
  const ctx = useContext(ProviderContext);
  if (!ctx) throw new Error('useProviderContext must be used within ProviderLayout');
  return ctx;
}

// ---------------------------------------------------------------------------
// Nav items — grouped navigation
// ---------------------------------------------------------------------------

interface NavItem {
  label: string;
  path: string;
  icon: keyof typeof Icons;
  description: string;
}

interface NavGroup {
  group: string;
  items: NavItem[];
}

const NAV_GROUPS: NavGroup[] = [
  {
    group: 'Overview',
    items: [
      { label: 'Dashboard', path: '/', icon: 'dashboard', description: 'System health overview' },
      { label: 'Tenants', path: '/tenants', icon: 'tenants', description: 'Tenant directory' },
    ],
  },
  {
    group: 'Operations',
    items: [
      { label: 'Deployments', path: '/deployments', icon: 'deployments', description: 'Deploy history' },
      { label: 'Queue Health', path: '/queues', icon: 'queue', description: 'NATS queue depth' },
      { label: 'Integrations', path: '/integrations', icon: 'integrations', description: 'Service reliability' },
      { label: 'Status Page', path: '/status', icon: 'status', description: 'Incident management' },
      { label: 'Alerts', path: '/alerts', icon: 'alerts', description: 'Alert rules & history' },
      { label: 'Diagnostics', path: '/diagnostics', icon: 'diagnostics', description: 'Support diagnostics' },
      { label: 'Co-Pilot Knowledge', path: '/copilot-knowledge', icon: 'knowledge', description: 'Knowledge management' },
      { label: 'Pipeline Observatory', path: '/pipeline', icon: 'queue', description: 'Agent pipeline metrics' },
      { label: 'Contact Messages', path: '/contact-messages', icon: 'contact', description: 'Customer messages' },
      { label: 'Service Messages', path: '/service-messages', icon: 'email', description: 'Bulk tenant notifications' },
    ],
  },
  {
    group: 'Control Plane',
    items: [
      { label: 'Entitlements', path: '/entitlements', icon: 'config', description: 'Tier entitlement config' },
      { label: 'Feature Flags', path: '/feature-flags', icon: 'config', description: 'Feature flag toggles' },
      { label: 'Rate Limits', path: '/rate-limits', icon: 'analytics', description: 'Rate limits & retry' },
      { label: 'Blocklists', path: '/blocklists', icon: 'secrets', description: 'Allow/block lists' },
      { label: 'Alert Thresholds', path: '/alert-thresholds', icon: 'alerts', description: 'Threshold config' },
      { label: 'Notifications', path: '/notification-channels', icon: 'email', description: 'Notification channels' },
      { label: 'Deploy Management', path: '/deploy-management', icon: 'deployments', description: 'Deployment orchestration' },
      { label: 'Test Execution', path: '/test-execution', icon: 'diagnostics', description: 'Test pipeline trigger' },
      { label: 'Maintenance', path: '/maintenance', icon: 'status', description: 'Maintenance mode' },
      { label: 'Experiments', path: '/experiments', icon: 'analytics', description: 'A/B experiment management' },
    ],
  },
  {
    group: 'Compliance & Security',
    items: [
      { label: 'Compliance', path: '/compliance', icon: 'compliance', description: 'PII & DSAR overview' },
      { label: 'Secrets', path: '/secrets', icon: 'secrets', description: 'Secret posture' },
      { label: 'Billing', path: '/billing', icon: 'billing', description: 'Billing health' },
      { label: 'Cost Analytics', path: '/costs', icon: 'cost', description: 'Unit economics' },
      { label: 'SLA Trends', path: '/sla', icon: 'sla', description: 'Uptime & latency' },
      { label: 'Abuse Detection', path: '/abuse', icon: 'abuse', description: 'Usage anomalies' },
    ],
  },
  {
    group: 'Account',
    items: [
      { label: 'User Management', path: '/users', icon: 'team', description: 'SPA admin users' },
      { label: 'MFA Settings', path: '/mfa', icon: 'mfa', description: 'Two-factor auth' },
    ],
  },
];

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

interface ProviderLayoutProps {
  apiKey: string;
  onLogout: () => void;
  children: React.ReactNode;
}

export function ProviderLayout({ apiKey, onLogout, children }: ProviderLayoutProps) {
  const [opened, { toggle }] = useDisclosure();
  const { setColorScheme } = useMantineColorScheme();
  const computedColorScheme = useComputedColorScheme('dark');
  const isDark = computedColorScheme === 'dark';
  const location = useLocation();
  const navigate = useNavigate();
  const [productVersion, setProductVersion] = useState<string | null>(null);

  // Authenticated fetch wrapper
  const apiFetch = useCallback(
    async (path: string, init?: RequestInit): Promise<Response> => {
      const baseUrl = import.meta.env?.VITE_API_URL || '';
      const headers = new Headers(init?.headers);
      headers.set('X-API-Key', apiKey);
      if (!headers.has('Content-Type') && init?.body) {
        headers.set('Content-Type', 'application/json');
      }
      return fetch(`${baseUrl}${path}`, { ...init, headers });
    },
    [apiKey],
  );

  // Toast helper
  const onNotify = useCallback(
    (message: string, type: 'success' | 'error' | 'warning' | 'info') => {
      const colorMap = { success: 'green', error: 'red', warning: 'yellow', info: 'blue' };
      notifications.show({ message, color: colorMap[type], autoClose: 5000 });
    },
    [],
  );

  // Fetch product version on mount
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await apiFetch('/api/superadmin/dashboard');
        if (res.ok && !cancelled) {
          const data = await res.json();
          setProductVersion(data.system_health?.version?.product ?? null);
        }
      } catch {
        // non-fatal
      }
    })();
    return () => { cancelled = true; };
  }, [apiFetch]);

  // WI-0883: Human-readable tenant directory lookup
  const { getTenantDisplay } = useTenantDirectory(apiFetch);

  const ctx: ProviderContextValue = { apiFetch, onNotify, productVersion, getTenantDisplay };

  return (
    <ProviderContext.Provider value={ctx}>
      <AppShell
        header={{ height: 56 }}
        navbar={{ width: 260, breakpoint: 'sm', collapsed: { mobile: !opened } }}
        padding="lg"
        styles={{
          main: { backgroundColor: tokens.page, minHeight: '100vh' },
          header: { backgroundColor: tokens.chrome, borderBottom: `1px solid ${tokens.surface}` },
          navbar: { backgroundColor: tokens.chrome, borderRight: `1px solid ${tokens.surface}` },
        }}
      >
        {/* Header */}
        <AppShell.Header>
          <Group h="100%" px="md" justify="space-between">
            <Group gap="sm">
              <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" color={tokens.textPrimary} />
              <img
                src="/admin/provider/primary-logo-no-wordmark.svg"
                alt=""
                style={{ height: '28px' }}
              />
              <Text fw={600} size="sm" c={tokens.textPrimary}>
                Service Provider Console
              </Text>
              {productVersion && (
                <Badge variant="outline" color="gray" size="xs" radius="sm">
                  v{productVersion}
                </Badge>
              )}
            </Group>
            <Group gap="sm">
              <Tooltip label="Documentation" position="bottom">
                <ActionIcon
                  variant="subtle"
                  color="gray"
                  component="a"
                  href="https://agentredcx.com"
                  target="_blank"
                  rel="noopener"
                  aria-label="Open documentation"
                >
                  <Icons.docs />
                </ActionIcon>
              </Tooltip>
              <Tooltip label={isDark ? 'Light mode' : 'Dark mode'} position="bottom">
                <ActionIcon
                  variant="subtle"
                  color="gray"
                  onClick={() => setColorScheme(isDark ? 'light' : 'dark')}
                  aria-label="Toggle dark mode"
                >
                  {isDark ? <Icons.sun /> : <Icons.moon />}
                </ActionIcon>
              </Tooltip>
              <Tooltip label="Sign out" position="bottom">
                <ActionIcon variant="subtle" color="gray" onClick={onLogout} aria-label="Sign out">
                  <Icons.logout />
                </ActionIcon>
              </Tooltip>
            </Group>
          </Group>
        </AppShell.Header>

        {/* Sidebar */}
        <AppShell.Navbar p="sm">
          <ScrollArea type="auto" offsetScrollbars>
            <Box mt="xs">
              {NAV_GROUPS.map((group, gi) => (
                <Box key={group.group}>
                  {gi > 0 && <Divider my="xs" color={tokens.page} />}
                  <Text
                    size="xs"
                    fw={600}
                    c={tokens.textTertiary}
                    tt="uppercase"
                    px="sm"
                    mb={4}
                  >
                    {group.group}
                  </Text>
                  {group.items.map((item) => {
                    const IconComponent = Icons[item.icon];
                    return (
                    <NavLink
                      key={item.path}
                      label={item.label}
                      description={item.description}
                      leftSection={<IconComponent />}
                      active={
                        item.path === '/'
                          ? location.pathname === '/'
                          : location.pathname.startsWith(item.path)
                      }
                      onClick={() => { navigate(item.path); toggle(); }}
                      styles={{
                        root: {
                          borderRadius: '8px',
                          marginBottom: '2px',
                          '&[data-active]': {
                            backgroundColor: 'rgba(255, 54, 33, 0.1)',
                          },
                        },
                        label: { color: tokens.textSecondary, fontSize: '14px', fontWeight: 500 },
                        description: { color: tokens.textTertiary, fontSize: '12px' },
                      }}
                    />
                    );
                  })}
                </Box>
              ))}
            </Box>
          </ScrollArea>
        </AppShell.Navbar>

        {/* Content */}
        <AppShell.Main>
          {children}
        </AppShell.Main>
      </AppShell>
    </ProviderContext.Provider>
  );
}
