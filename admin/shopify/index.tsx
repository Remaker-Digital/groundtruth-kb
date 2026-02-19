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
import { KnowledgeBasePage } from './pages/KnowledgeBase';
import { ConfigurationPage } from './pages/Configuration';
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
// Error Boundary — catches render crashes in page components
// ---------------------------------------------------------------------------

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

class PageErrorBoundary extends React.Component<
  { children: React.ReactNode; pageName?: string },
  ErrorBoundaryState
> {
  constructor(props: { children: React.ReactNode; pageName?: string }) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error(`[PageErrorBoundary] ${this.props.pageName ?? 'Unknown'} crashed:`, error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          padding: 32,
          fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
          textAlign: 'center',
        }}>
          <h2 style={{ color: '#ff3621', marginBottom: 8 }}>
            Page Error
          </h2>
          <p style={{ color: '#666', fontSize: 14, marginBottom: 16 }}>
            {this.props.pageName ?? 'This page'} encountered an error.
          </p>
          <pre style={{
            textAlign: 'left',
            padding: 12,
            background: '#fafaf9',
            borderRadius: 6,
            fontSize: 12,
            overflow: 'auto',
            maxHeight: 200,
            color: '#ff3621',
          }}>
            {this.state.error?.message}
          </pre>
          <button
            onClick={() => this.setState({ hasError: false, error: null })}
            style={{
              marginTop: 16,
              padding: '8px 20px',
              border: '1px solid #ccc',
              borderRadius: 6,
              background: '#fff',
              cursor: 'pointer',
              fontSize: 13,
            }}
          >
            Try Again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

// ---------------------------------------------------------------------------
// App — full Shopify embedded admin
// ---------------------------------------------------------------------------

const App: React.FC = () => {
  const config = getShopifyConfig();

  return (
    <AppProvider i18n={enTranslations}>
      <BrowserRouter basename="/admin/shopify">
        <ShopifyAppLayout shopifyConfig={config}>
          <Routes>
            <Route path="/" element={<PageErrorBoundary pageName="Dashboard"><DashboardPage /></PageErrorBoundary>} />
            <Route path="/inbox" element={<PageErrorBoundary pageName="Inbox"><InboxPage /></PageErrorBoundary>} />
            <Route path="/knowledge-base" element={<PageErrorBoundary pageName="Knowledge Base"><KnowledgeBasePage /></PageErrorBoundary>} />
            <Route path="/configuration" element={<PageErrorBoundary pageName="Configuration"><ConfigurationPage /></PageErrorBoundary>} />
            <Route path="/widget" element={<PageErrorBoundary pageName="Widget"><WidgetPage /></PageErrorBoundary>} />
            <Route path="/billing" element={<PageErrorBoundary pageName="Billing"><BillingPage /></PageErrorBoundary>} />
            <Route path="/settings" element={<PageErrorBoundary pageName="Settings"><SettingsPage /></PageErrorBoundary>} />
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
