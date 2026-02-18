/**
 * ProviderLayout — Platform operator console shell.
 *
 * Provides:
 *   1. Grouped sidebar navigation (13 pages in 4 groups)
 *   2. Header with platform name, version, and logout
 *   3. Authenticated apiFetch wrapper (SUPERADMIN API key injection)
 *   4. AppContext for child pages
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';
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
import { notifications } from '@mantine/notifications';

// ---------------------------------------------------------------------------
// Context
// ---------------------------------------------------------------------------

interface ProviderContextValue {
  apiFetch: (path: string, init?: RequestInit) => Promise<Response>;
  onNotify: (message: string, type: 'success' | 'error' | 'warning' | 'info') => void;
  productVersion: string | null;
}

const ProviderContext = createContext<ProviderContextValue | null>(null);

export function useProviderContext(): ProviderContextValue {
  const ctx = useContext(ProviderContext);
  if (!ctx) throw new Error('useProviderContext must be used within ProviderLayout');
  return ctx;
}

// ---------------------------------------------------------------------------
// SVG Icons — consistent with Standalone admin; renders identically cross-platform
// ---------------------------------------------------------------------------

const Icons = {
  dashboard: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="7" height="7" /><rect x="14" y="3" width="7" height="7" /><rect x="3" y="14" width="7" height="7" /><rect x="14" y="14" width="7" height="7" />
    </svg>
  ),
  tenants: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M23 21v-2a4 4 0 0 0-3-3.87" /><path d="M16 3.13a4 4 0 0 1 0 7.75" />
    </svg>
  ),
  deployments: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z" /><path d="M12 15l-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z" /><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0" /><path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5" />
    </svg>
  ),
  queue: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="2" y="4" width="20" height="5" rx="1" /><rect x="2" y="13" width="20" height="5" rx="1" /><line x1="6" y1="6.5" x2="6" y2="6.5" /><line x1="6" y1="15.5" x2="6" y2="15.5" />
    </svg>
  ),
  integrations: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" /><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
    </svg>
  ),
  status: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" />
    </svg>
  ),
  alerts: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" /><path d="M13.73 21a2 2 0 0 1-3.46 0" />
    </svg>
  ),
  compliance: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
    </svg>
  ),
  secrets: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4" />
    </svg>
  ),
  billing: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="1" y="4" width="22" height="16" rx="2" ry="2" /><line x1="1" y1="10" x2="23" y2="10" />
    </svg>
  ),
  sla: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="18" y1="20" x2="18" y2="10" /><line x1="12" y1="20" x2="12" y2="4" /><line x1="6" y1="20" x2="6" y2="14" />
    </svg>
  ),
  mfa: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="11" width="18" height="11" rx="2" ry="2" /><path d="M7 11V7a5 5 0 0 1 10 0v4" />
    </svg>
  ),
  docs: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" /><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
    </svg>
  ),
  logout: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" /><polyline points="16 17 21 12 16 7" /><line x1="21" y1="12" x2="9" y2="12" />
    </svg>
  ),
};

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
    ],
  },
  {
    group: 'Compliance & Security',
    items: [
      { label: 'Compliance', path: '/compliance', icon: 'compliance', description: 'PII & DSAR overview' },
      { label: 'Secrets', path: '/secrets', icon: 'secrets', description: 'Secret posture' },
      { label: 'Billing', path: '/billing', icon: 'billing', description: 'Billing health' },
      { label: 'SLA Trends', path: '/sla', icon: 'sla', description: 'Uptime & latency' },
    ],
  },
  {
    group: 'Account',
    items: [
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

  const ctx: ProviderContextValue = { apiFetch, onNotify, productVersion };

  return (
    <ProviderContext.Provider value={ctx}>
      <AppShell
        header={{ height: 56 }}
        navbar={{ width: 260, breakpoint: 'sm', collapsed: { mobile: !opened } }}
        padding="lg"
        styles={{
          main: { backgroundColor: '#141414', minHeight: '100vh' },
          header: { backgroundColor: '#0a0a0a', borderBottom: '1px solid #1E1E1E' },
          navbar: { backgroundColor: '#0a0a0a', borderRight: '1px solid #1E1E1E' },
        }}
      >
        {/* Header */}
        <AppShell.Header>
          <Group h="100%" px="md" justify="space-between">
            <Group gap="sm">
              <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" color="#F5F5F5" />
              <img
                src="/admin/provider/primary-logo-no-wordmark.svg"
                alt="Agent Red"
                style={{ height: '28px' }}
              />
              <Text fw={600} size="sm" c="#F5F5F5">
                Provider Console
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
                  {gi > 0 && <Divider my="xs" color="#1E1E1E" />}
                  <Text
                    size="xs"
                    fw={600}
                    c="#5C5C5C"
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
                        label: { color: '#E0E0E0', fontSize: '14px', fontWeight: 500 },
                        description: { color: '#787878', fontSize: '12px' },
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
