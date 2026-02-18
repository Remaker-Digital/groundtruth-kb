/**
 * Provider Admin Console — entry point.
 *
 * Platform operator console for managing all tenants, monitoring health,
 * and viewing cross-tenant analytics. Requires SUPERADMIN API key.
 *
 * Architecture:
 *   This is a separate SPA from the standalone admin. The standalone admin
 *   is per-tenant (merchant-facing); this console is platform-wide
 *   (operator-facing) and consumes /api/superadmin/* endpoints.
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

import { ProviderLayout } from './layouts/ProviderLayout';
import { ApiKeyLogin } from './login/ApiKeyLogin';
import { HealthDashboardPage } from './pages/HealthDashboard';
import { TenantDirectoryPage } from './pages/TenantDirectory';
import { DeploymentHistoryPage } from './pages/DeploymentHistory';
import { BillingHealthPage } from './pages/BillingHealth';
import { SLATrendsPage } from './pages/SLATrends';

// ---------------------------------------------------------------------------
// Agent Red brand theme (same as standalone admin)
// ---------------------------------------------------------------------------

const agentRedTheme = createTheme({
  primaryColor: 'brand',
  colors: {
    brand: [
      '#FDE8E8', '#F2D4D6', '#E8A3A7', '#DC7278', '#D14B52',
      '#ff3621', '#B01824', '#9B1420', '#870E18', '#720912',
    ],
    dark: [
      '#F5F5F5', '#E0E0E0', '#A0A0A0', '#787878', '#5C5C5C',
      '#141414', '#1f1f1f', '#0a0a0a', '#1f1f1f', '#0a0a0a',
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
// Auth state (sessionStorage — SUPERADMIN key)
// ---------------------------------------------------------------------------

function getStoredApiKey(): string | null {
  try {
    return sessionStorage.getItem('agentred_provider_key');
  } catch {
    return null;
  }
}

function storeApiKey(key: string): void {
  try {
    sessionStorage.setItem('agentred_provider_key', key);
  } catch {
    // sessionStorage unavailable
  }
}

function clearApiKey(): void {
  try {
    sessionStorage.removeItem('agentred_provider_key');
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

  if (!apiKey) {
    return <ApiKeyLogin onLogin={handleLogin} />;
  }

  return (
    <MantineProvider theme={agentRedTheme} defaultColorScheme="dark">
      <Notifications position="top-right" />
      <BrowserRouter basename="/admin/provider">
        <ProviderLayout apiKey={apiKey} onLogout={handleLogout}>
          <Routes>
            <Route path="/" element={<HealthDashboardPage />} />
            <Route path="/tenants" element={<TenantDirectoryPage />} />
            <Route path="/deployments" element={<DeploymentHistoryPage />} />
            <Route path="/billing" element={<BillingHealthPage />} />
            <Route path="/sla" element={<SLATrendsPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </ProviderLayout>
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
