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
import { MantineProvider } from '@mantine/core';
import { Notifications } from '@mantine/notifications';

import '@mantine/core/styles.css';
import '@mantine/notifications/styles.css';

import { agentRedTheme } from '../shared/theme/agentRedTheme';
import { StandaloneLayout } from './layouts/StandaloneLayout';
import { ApiKeyLogin } from './login/ApiKeyLogin';
import { DashboardPage } from './pages/Dashboard';
import { InboxPage } from './pages/Inbox';

import { ConfigurationPage } from './pages/Configuration';
import { KnowledgeBasePage } from './pages/KnowledgeBase';
import { WidgetPage } from './pages/Widget';
import { BillingPage } from './pages/Billing';
import { TeamPage } from './pages/Team';
import { IntegrationsPage } from './pages/Integrations';
import { QuickActionsPage } from './pages/QuickActions';
import { MemoryPrivacyPage } from './pages/MemoryPrivacy';

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
