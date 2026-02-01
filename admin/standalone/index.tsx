/**
 * Standalone Admin Shell — entry point.
 *
 * This is the main entry for Stripe-direct (non-Shopify) merchants.
 * It provides:
 *   1. API key login page
 *   2. Custom sidebar navigation (Agent Red branding)
 *   3. Routes to the same 7 admin pages using shared components
 *   4. Authenticated apiFetch via API key header
 *
 * Architecture (Decision UI-7):
 *   Standalone admin is required because Stripe-direct merchants
 *   have no Shopify account and cannot access the embedded admin.
 *   Shares the same component library as the Shopify shell.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

import { StandaloneLayout } from './layouts/StandaloneLayout';
import { ApiKeyLogin } from './login/ApiKeyLogin';
import { DashboardPage } from './pages/Dashboard';
import { InboxPage } from './pages/Inbox';
import { ConfigurationPage } from './pages/Configuration';
import { KnowledgeBasePage } from './pages/KnowledgeBase';
import { WidgetPage } from './pages/Widget';
import { BillingPage } from './pages/Billing';
import { SettingsPage } from './pages/Settings';

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

  if (!apiKey) {
    return <ApiKeyLogin onLogin={handleLogin} />;
  }

  return (
    <BrowserRouter basename="/admin">
      <StandaloneLayout apiKey={apiKey} onLogout={handleLogout}>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/inbox" element={<InboxPage />} />
          <Route path="/configuration" element={<ConfigurationPage />} />
          <Route path="/knowledge-base" element={<KnowledgeBasePage />} />
          <Route path="/widget" element={<WidgetPage />} />
          <Route path="/billing" element={<BillingPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </StandaloneLayout>
    </BrowserRouter>
  );
};

// ---------------------------------------------------------------------------
// Mount
// ---------------------------------------------------------------------------

const root = document.getElementById('app');
if (root) {
  createRoot(root).render(<App />);
}
