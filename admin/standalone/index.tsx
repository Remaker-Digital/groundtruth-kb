/**
 * Standalone Admin Shell — entry point.
 *
 * This is the main entry for Stripe-direct (non-Shopify) merchants.
 * It provides:
 *   1. API key login page (renders OUTSIDE MantineProvider)
 *   2. MantineProvider with Agent Red brand theme (dark mode default)
 *   3. Mantine AppShell layout with sidebar navigation
 *   4. Routes to 9 admin pages using prototype Mantine components
 *   5. Authenticated apiFetch via API key header
 *
 * Architecture (Decision UI-7):
 *   Standalone admin is required because Stripe-direct merchants
 *   have no Shopify account and cannot access the embedded admin.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { MantineProvider, createTheme } from '@mantine/core';
import { Notifications } from '@mantine/notifications';

import '@mantine/core/styles.css';
import '@mantine/notifications/styles.css';

import { StandaloneLayout } from './layouts/StandaloneLayout';
import { ApiKeyLogin } from './login/ApiKeyLogin';
import { DashboardPage } from './pages/Dashboard';
import { InboxPage } from './pages/Inbox';

import { ConfigurationPage } from './pages/Configuration';
import { KnowledgeBasePage } from './pages/KnowledgeBase';
import { WidgetPage } from './pages/Widget';
import { BillingPage } from './pages/Billing';
import { TeamPage } from './pages/Team';
import { OnboardingPage } from './pages/Onboarding';
import { IntegrationsPage } from './pages/Integrations';
import { QuickActionsPage } from './pages/QuickActions';
import { MemoryPrivacyPage } from './pages/MemoryPrivacy';

// ---------------------------------------------------------------------------
// Agent Red brand theme — copied from prototype/src/main.tsx
// ---------------------------------------------------------------------------

const agentRedTheme = createTheme({
  primaryColor: 'brand',
  colors: {
    // Brand red scale: lightest -> darkest, index 5 = primary #ff3621
    brand: [
      '#FDE8E8', // 0 - error bg tint
      '#F2D4D6', // 1 - Soft Red (Primary Light)
      '#E8A3A7', // 2
      '#DC7278', // 3
      '#D14B52', // 4
      '#ff3621', // 5 - Agent Red (Primary)
      '#B01824', // 6
      '#9B1420', // 7 - Deep Red (Primary Dark, hover)
      '#870E18', // 8
      '#720912', // 9
    ],
    // Neutral grey dark scale — designer-approved (2026-02-03 mockup, revised by Mazel)
    // Depth hierarchy: header/sidebar (#0a0a0a) -> page (#141414) -> cards (#1f1f1f) -> borders (#272727)
    dark: [
      '#F5F5F5', // 0 - Light grey (text on dark bg)
      '#E0E0E0', // 1 - Borders (light)
      '#A0A0A0', // 2 - Muted text
      '#787878', // 3 - Secondary text
      '#5C5C5C', // 4 - Tertiary text
      '#141414', // 5 - Page background
      '#1f1f1f', // 6 - Cards / elevated surfaces
      '#0a0a0a', // 7 - Header, sidebar (deepest chrome)
      '#1f1f1f', // 8 - Card surface (alias)
      '#0a0a0a', // 9 - True dark (alias)
    ],
  },
  fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  fontFamilyMonospace: "'JetBrains Mono', ui-monospace, monospace",
  headings: {
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    fontWeight: '600',
  },
  defaultRadius: 'md',
  cursorType: 'pointer',
  other: {
    colors: {
      primary: '#ff3621',
      primaryDark: '#9B1420',
      primaryLight: '#F2D4D6',
      charcoal: '#0a0a0a',
      slate: '#141414',
      steel: '#5C5C5C',
      silver: '#E0E0E0',
      snow: '#F5F5F5',
      success: '#0D7C3E',
      warning: '#E5A100',
      error: '#D32F2F',
      info: '#1E3A5F',
    },
  },
});

// ---------------------------------------------------------------------------
// Auth state
// ---------------------------------------------------------------------------

function getStoredApiKey(): string | null {
  try {
    return sessionStorage.getItem('agentred_api_key');
  } catch {
    return null;
  }
}

function storeApiKey(key: string): void {
  try {
    sessionStorage.setItem('agentred_api_key', key);
  } catch {
    // sessionStorage unavailable
  }
}

function clearApiKey(): void {
  try {
    sessionStorage.removeItem('agentred_api_key');
  } catch {
    // sessionStorage unavailable
  }
}

// ---------------------------------------------------------------------------
// App
// ---------------------------------------------------------------------------

const App: React.FC = () => {
  const [apiKey, setApiKey] = React.useState<string | null>(getStoredApiKey);

  const handleLogin = React.useCallback((key: string) => {
    storeApiKey(key);
    setApiKey(key);
  }, []);

  const handleLogout = React.useCallback(() => {
    clearApiKey();
    setApiKey(null);
  }, []);

  // ApiKeyLogin renders OUTSIDE MantineProvider — it has its own dark styling
  if (!apiKey) {
    return <ApiKeyLogin onLogin={handleLogin} />;
  }

  return (
    <MantineProvider theme={agentRedTheme} defaultColorScheme="dark">
      <Notifications position="top-right" />
      <BrowserRouter basename="/admin/standalone">
        <StandaloneLayout apiKey={apiKey} onLogout={handleLogout}>
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/inbox" element={<InboxPage />} />
            <Route path="/analytics" element={<Navigate to="/" replace />} />
            <Route path="/configuration" element={<ConfigurationPage />} />
            <Route path="/knowledge-base" element={<KnowledgeBasePage />} />
            <Route path="/widget" element={<WidgetPage />} />
            <Route path="/quick-actions" element={<QuickActionsPage />} />
            <Route path="/billing" element={<BillingPage />} />
            <Route path="/team" element={<TeamPage />} />
            <Route path="/integrations" element={<IntegrationsPage />} />
            <Route path="/memory-privacy" element={<MemoryPrivacyPage />} />
            <Route path="/onboarding" element={<OnboardingPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </StandaloneLayout>
      </BrowserRouter>
    </MantineProvider>
  );
};

// ---------------------------------------------------------------------------
// Mount
// ---------------------------------------------------------------------------

const root = document.getElementById('app');
if (root) {
  createRoot(root).render(<App />);
}
