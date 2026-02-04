/**
 * Shopify Embedded Admin Shell — entry point.
 *
 * This is the main entry for the Shopify embedded admin app. It:
 *   1. Initializes Shopify App Bridge for session auth
 *   2. Provides the ShopifyAppLayout (Polaris + App Bridge chrome)
 *   3. Routes to the 7 admin pages using React Router
 *   4. Injects the authenticated apiFetch into shared components
 *
 * Architecture (Decision UI-7):
 *   Shopify embedded admin uses Polaris + App Bridge for native Shopify UX.
 *   Shared components from admin/shared/ are wrapped in Polaris Page/Card.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppProvider } from '@shopify/polaris';
import '@shopify/polaris/build/esm/styles.css';
import enTranslations from '@shopify/polaris/locales/en.json';

import { ShopifyAppLayout } from './layouts/ShopifyAppLayout';
import { DashboardPage } from './pages/Dashboard';
import { InboxPage } from './pages/Inbox';
import { ConfigurationPage } from './pages/Configuration';
import { KnowledgeBasePage } from './pages/KnowledgeBase';
import { WidgetPage } from './pages/Widget';
import { BillingPage } from './pages/Billing';
import { SettingsPage } from './pages/Settings';

// ---------------------------------------------------------------------------
// App Bridge config (injected by Shopify in the embedded app URL)
// ---------------------------------------------------------------------------

function getShopifyConfig() {
  const params = new URLSearchParams(window.location.search);
  return {
    apiKey: params.get('api_key') || import.meta.env.VITE_SHOPIFY_API_KEY || '',
    host: params.get('host') || '',
    shop: params.get('shop') || '',
  };
}

// ---------------------------------------------------------------------------
// App
// ---------------------------------------------------------------------------

const App: React.FC = () => {
  const config = getShopifyConfig();

  return (
    <AppProvider i18n={enTranslations}>
      <BrowserRouter>
        <ShopifyAppLayout shopifyConfig={config}>
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
        </ShopifyAppLayout>
      </BrowserRouter>
    </AppProvider>
  );
};

// ---------------------------------------------------------------------------
// Mount
// ---------------------------------------------------------------------------

const root = document.getElementById('app');
if (root) {
  createRoot(root).render(<App />);
}
