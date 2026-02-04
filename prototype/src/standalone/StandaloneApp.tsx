import React, { useState } from 'react';
import { AppShell, NavLink, Group, Text, ThemeIcon, Badge, Box, Burger, Tooltip, ActionIcon, useMantineTheme, useMantineColorScheme, useComputedColorScheme } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { DashboardPage } from './pages/DashboardPage';
import { InboxPage } from './pages/InboxPage';
import { KnowledgeBasePage } from './pages/KnowledgeBasePage';
import { ConfigurationPage } from './pages/ConfigurationPage';
import { WidgetConfigPage } from './pages/WidgetConfigPage';
import { BillingPage } from './pages/BillingPage';
import { TeamPage } from './pages/TeamPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { OnboardingPage } from './pages/OnboardingPage';

type Page = 'dashboard' | 'inbox' | 'knowledge' | 'config' | 'widget' | 'billing' | 'team' | 'analytics' | 'onboarding';

// Simple SVG icons as inline components
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
  analytics: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="18" y1="20" x2="18" y2="10" /><line x1="12" y1="20" x2="12" y2="4" /><line x1="6" y1="20" x2="6" y2="14" />
    </svg>
  ),
  onboarding: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /><line x1="16" y1="13" x2="8" y2="13" /><line x1="16" y1="17" x2="8" y2="17" /><polyline points="10 9 9 9 8 9" />
    </svg>
  ),
};

const navItems: { page: Page; label: string; icon: keyof typeof Icons; badge?: number | string }[] = [
  { page: 'dashboard', label: 'Dashboard', icon: 'dashboard' },
  { page: 'inbox', label: 'Inbox', icon: 'inbox', badge: 3 },
  { page: 'knowledge', label: 'Knowledge Base', icon: 'knowledge' },
  { page: 'analytics', label: 'Analytics', icon: 'analytics' },
  { page: 'config', label: 'Configuration', icon: 'config' },
  { page: 'widget', label: 'Widget', icon: 'widget' },
  { page: 'team', label: 'Team', icon: 'team' },
  { page: 'billing', label: 'Billing', icon: 'billing' },
  { page: 'onboarding', label: 'Setup Wizard', icon: 'onboarding' },
];

export function StandaloneApp() {
  const [activePage, setActivePage] = useState<Page>('dashboard');
  const [opened, { toggle }] = useDisclosure();
  const theme = useMantineTheme();
  const { setColorScheme } = useMantineColorScheme();
  const computedColorScheme = useComputedColorScheme('dark');
  const isDark = computedColorScheme === 'dark';

  const renderPage = () => {
    switch (activePage) {
      case 'dashboard': return <DashboardPage />;
      case 'inbox': return <InboxPage />;
      case 'knowledge': return <KnowledgeBasePage />;
      case 'config': return <ConfigurationPage />;
      case 'widget': return <WidgetConfigPage />;
      case 'billing': return <BillingPage />;
      case 'team': return <TeamPage />;
      case 'analytics': return <AnalyticsPage />;
      case 'onboarding': return <OnboardingPage />;
      default: return <DashboardPage />;
    }
  };

  return (
    <div id="app-shell-capture-root" style={{ position: 'relative', width: '100%', minHeight: '100vh' }}>
    <AppShell
      header={{ height: 56 }}
      navbar={{ width: 260, breakpoint: 'sm', collapsed: { mobile: !opened } }}
      padding="md"
      styles={{
        header: {
          borderBottom: isDark ? '1px solid rgba(255,255,255,0.06)' : '1px solid #1E1E1E',
          background: '#0a0a0a',
        },
        navbar: {
          borderRight: isDark ? '1px solid rgba(255,255,255,0.06)' : undefined,
          background: isDark ? '#0a0a0a' : undefined,
        },
        main: {
          background: isDark ? '#363636' : undefined,
        },
      }}
    >
      <AppShell.Header>
        <Group h="100%" px="md" justify="space-between">
          <Group>
            <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" />
            <Tooltip label="Agent Red Customer Experience" position="bottom" openDelay={500}>
              <Group gap={10} align="center" style={{ cursor: 'default' }}>
                <img
                  src="/logo/primary-logo-no-wordmark.svg"
                  alt="Agent Red"
                  style={{ height: 30, display: 'block' }}
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
            <Badge variant="light" color="green" size="sm">Professional</Badge>
            {/* Dark mode toggle — always dark styling since header is always dark */}
            <ActionIcon
              variant="subtle"
              size="md"
              onClick={() => setColorScheme(computedColorScheme === 'dark' ? 'light' : 'dark')}
              aria-label="Toggle dark mode"
              style={{
                color: '#A0A0A0',
                border: '1px solid rgba(255, 255, 255, 0.12)',
                background: 'rgba(255, 255, 255, 0.06)',
              }}
            >
              {computedColorScheme === 'dark' ? (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="5" /><line x1="12" y1="1" x2="12" y2="3" /><line x1="12" y1="21" x2="12" y2="23" /><line x1="4.22" y1="4.22" x2="5.64" y2="5.64" /><line x1="18.36" y1="18.36" x2="19.78" y2="19.78" /><line x1="1" y1="12" x2="3" y2="12" /><line x1="21" y1="12" x2="23" y2="12" /><line x1="4.22" y1="19.78" x2="5.64" y2="18.36" /><line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
                </svg>
              ) : (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
                </svg>
              )}
            </ActionIcon>
            <Box
              style={{
                width: 32,
                height: 32,
                borderRadius: '50%',
                background: '#C41E2A',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#fff',
                fontSize: 13,
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              MV
            </Box>
          </Group>
        </Group>
      </AppShell.Header>

      <AppShell.Navbar p="xs">
        <AppShell.Section grow>
          {navItems.map(item => {
            const IconComponent = Icons[item.icon];
            const isActive = activePage === item.page;
            return (
              <NavLink
                key={item.page}
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
                onClick={() => setActivePage(item.page)}
                styles={{
                  label: isActive && isDark ? { color: '#F5F5F5' } : undefined,
                }}
                style={{
                  borderRadius: 8,
                  marginBottom: 2,
                  ...(isActive && isDark ? { background: 'rgba(255, 255, 255, 0.06)' } : {}),
                }}
              />
            );
          })}
        </AppShell.Section>
        <AppShell.Section>
          <Box p="xs" style={{ borderTop: isDark ? '1px solid rgba(255,255,255,0.06)' : '1px solid var(--mantine-color-gray-2)' }}>
            <Text size="xs" c="dimmed" ta="center">
              Agent Red v1.0.0
            </Text>
          </Box>
        </AppShell.Section>
      </AppShell.Navbar>

      <AppShell.Main>
        {renderPage()}
      </AppShell.Main>
    </AppShell>
    </div>
  );
}
