/**
 * ProviderLayout — Platform operator console shell.
 *
 * Provides:
 *   1. Sidebar navigation (5 pages)
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
  Group,
  NavLink,
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
// Nav items
// ---------------------------------------------------------------------------

interface NavItem {
  label: string;
  path: string;
  icon: string;
  description: string;
}

const NAV_ITEMS: NavItem[] = [
  { label: 'Dashboard', path: '/', icon: '\u{1F4CA}', description: 'System health overview' },
  { label: 'Tenants', path: '/tenants', icon: '\u{1F465}', description: 'Tenant directory' },
  { label: 'Deployments', path: '/deployments', icon: '\u{1F680}', description: 'Deploy history' },
  { label: 'Billing', path: '/billing', icon: '\u{1F4B3}', description: 'Billing health' },
  { label: 'SLA Trends', path: '/sla', icon: '\u{1F4C8}', description: 'Uptime & latency' },
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
        navbar={{ width: 240, breakpoint: 'sm', collapsed: { mobile: !opened } }}
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
                >
                  <Text size="sm">Docs</Text>
                </ActionIcon>
              </Tooltip>
              <Tooltip label="Sign out" position="bottom">
                <ActionIcon variant="subtle" color="gray" onClick={onLogout}>
                  <Text size="lg">{'\u{2BBE}'}</Text>
                </ActionIcon>
              </Tooltip>
            </Group>
          </Group>
        </AppShell.Header>

        {/* Sidebar */}
        <AppShell.Navbar p="sm">
          <Box mt="xs">
            {NAV_ITEMS.map((item) => (
              <NavLink
                key={item.path}
                label={item.label}
                description={item.description}
                leftSection={<Text size="lg">{item.icon}</Text>}
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
            ))}
          </Box>
        </AppShell.Navbar>

        {/* Content */}
        <AppShell.Main>
          {children}
        </AppShell.Main>
      </AppShell>
    </ProviderContext.Provider>
  );
}
