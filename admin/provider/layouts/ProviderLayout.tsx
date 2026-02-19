/**
 * ProviderLayout — Platform operator console shell.
 *
 * Provides:
 *   1. Grouped sidebar navigation (16 pages in 4 groups)
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
import { Icons } from '../../shared/icons';

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
          main: { backgroundColor: '#1c1917', minHeight: '100vh' },
          header: { backgroundColor: '#0c0a09', borderBottom: '1px solid #292524' },
          navbar: { backgroundColor: '#0c0a09', borderRight: '1px solid #292524' },
        }}
      >
        {/* Header */}
        <AppShell.Header>
          <Group h="100%" px="md" justify="space-between">
            <Group gap="sm">
              <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" color="#fafaf9" />
              <img
                src="/admin/provider/primary-logo-no-wordmark.svg"
                alt="Agent Red"
                style={{ height: '28px' }}
              />
              <Text fw={600} size="sm" c="#fafaf9">
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
